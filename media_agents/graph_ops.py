import os

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_fireworks import ChatFireworks
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema import HumanMessage, SystemMessage
from media_agents.app_resources import get_resource_content
import json
from functools import cache
import logging
from typing import Dict, Literal
from urllib3.util import parse_url
from datetime import datetime, UTC
import jsonlines
from media_agents.notification_utils import send_email
from media_agents.template_rendering import render_template
from media_agents.subscriptions import get_recipients
from pathlib import Path

import media_agents.config as config

# Initialize logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_client():
    llm_client = os.getenv("LLM_CLIENT", "gpt-4-turbo")
    client = None
    if 'llama' in llm_client:
        client = (ChatFireworks(model=llm_client, temperature=0.7))
        logger.info(f"init ChatGroq:{llm_client}")
    elif 'gpt' in llm_client:
        client = ChatOpenAI(model=llm_client, temperature=0.7)
        logger.info(f"init ChatOpenAI:{llm_client}")
    else: # by default
        client = ChatOpenAI(model=llm_client, temperature=0.7)
        logger.info(f"init ChatOpenAI by default:{llm_client}")

    return client

# Initialize the LLM client

client = create_client()

@cache
def get_content(url: str) -> Dict:
    """
    Fetch content from a URL using a GET request with custom headers.

    :param url: The URL to fetch the content from.
    :return: The JSON content of the response if successful, otherwise None.
    """
    # Define custom headers including a User-Agent
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Send a GET request to the URL with custom headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        return response.json()  # Return the JSON content of the response
    else:
        return None

def compose_sys_content(message: str, schema: str) -> str:
    """
    Compose a system message for the OpenAI API based on user requirements and schema.

    :param message: The user requirement message.
    :param schema: The JSON schema.
    :return: The composed system message.
    """
    return f"""User Requirement:
    {message}
    Schema:
    ```json
    {schema}
    ```"""

def init_agent(state: Dict) -> Dict:
    logger.debug("<-----init_agent state----->")
    filepath = os.getenv("FETCH_STATE_FILE")
    with open(filepath, 'r') as sf:
        state_obj = json.load(sf)
    logger.debug("</-----init_agent state----->")
    return state_obj

# URL for Court Listener API
COURT_LISTENER_URL = 'https://www.courtlistener.com/api/rest/v3/opinions/?'

def fetch_update(state: Dict) -> Dict:
    """
    Fetch the latest court opinions updates from Court Listener.

    :param state: The current state containing the last processed opinion ID.
    :return: A dictionary with fetched opinions to check.
    """
    logger.debug("<-----fetch_update state----->")
    logger.info(f"fetching last updates from {COURT_LISTENER_URL}")
    
    last_id = state["last_processed_id"]
    opinion_objects = []

    for page in range(100, 0, -1):
        url = COURT_LISTENER_URL + f'order_by=-date_created&page={page}'
        json_content = get_content(url)
        if not json_content:
            continue

        for res in reversed(json_content['results']):
            id = int(res['id'])
            if id < last_id:
                continue
            opinion_objects.append(res)
            last_id = int(res['id'])

    logger.info(f"{len(opinion_objects)} court opinions fetched ")
    logger.debug("</-----fetch_update state----->")
    return {"opinions_to_check": opinion_objects}

def find_news_leads(state: Dict) -> Dict:
    """
    Identify newsworthy court opinions from the fetched updates.

    :param state: The current state containing opinions to check.
    :return: A dictionary with newsworthy opinions.
    """
    logger.debug("<-----find_news_leads state----->")
    opinions_to_check = state["opinions_to_check"]
    newsworthy_opinions = []
    parser = JsonOutputParser()
    sys_intro = get_resource_content('prompts/newsworthiness_prompt.txt')
    sys_schema = get_resource_content('schemas/newsworthiness_output.json')
    sys_message = compose_sys_content(sys_intro, sys_schema)

    for opinion in opinions_to_check:
        id = opinion["id"]
        user_content = f"Here is a court opinion id#{id}:\n" + opinion["plain_text"]
        if 'supreme court' not in str.lower(user_content):
            continue

        try:
            pipeline = client | parser
            json_obj = pipeline.invoke([
                    SystemMessage(content=sys_message),
                    HumanMessage(content=user_content)
                ]
            )

            if 'properties' not in json_obj:
                if json_obj["newsworthy"] == "True" and json_obj["influence"] == "Global":
                    json_obj["id"] = opinion["id"]
                    json_obj["resource_uri"] = opinion["resource_uri"]
                    json_obj["absolute_url"] = opinion["absolute_url"]
                    json_obj["plain_text"] = opinion["plain_text"]
                    json_obj["download_url"] = opinion["download_url"]
                    json_obj["local_path"] = opinion["local_path"]
                    json_obj["date_created"] = opinion["date_created"]
                    json_obj["date_modified"] = opinion["date_modified"]
                    json_obj["opinions_cited"] = json_obj.get("opinions_cited", [])
                    newsworthy_opinions.append(json_obj)
        except Exception as e:
            logger.error(f"Error: processing opinion {opinion['resource_uri']}")
            logger.error(e)
    logger.info(f"{len(newsworthy_opinions)} court opinions detected as newsworthy")
    logger.debug("</-----find_news_leads state----->")
    return {"newsworthy_opinions": newsworthy_opinions}

def extract_keypoints(state: Dict) -> Dict:
    """
    Extract key points from the newsworthy opinions.

    :param state: The current state containing newsworthy opinions.
    :return: A dictionary with opinions and their key points.
    """
    logger.debug("<-----extract_keypoints state----->")
    opinions = state["newsworthy_opinions"]
    logger.info(f"extract keypoints: {len(opinions)} opinions")
    res_opinions = []
    parser = JsonOutputParser()
    sys_intro = get_resource_content('prompts/keypoints_prompt.txt')
    sys_schema = get_resource_content('schemas/keypoints_output.json')
    sys_message = compose_sys_content(sys_intro, sys_schema)

    for opinion in opinions:
        id = opinion["id"]
        user_content = f"Here is a court opinion id#{id}:\n" + opinion["plain_text"]
        try:
            pipeline = client | parser
            json_obj = pipeline.invoke([
                    SystemMessage(content=sys_message),
                    HumanMessage(content=user_content)
                ]
            )

            if 'properties' not in json_obj:
                opinion["keypoints"] = json_obj
                res_opinions.append(opinion)
        except Exception as e:
            logger.error(f"Error: processing opinion {opinion['resource_uri']}")
            logger.error(e)
    logger.debug("</-----extract_keypoints state----->")
    return {"opinions_with_keypoints": res_opinions}

def write_articles_draft(state: Dict) -> Dict:
    """
    Write draft articles based on the opinions with key points.

    :param state: The current state containing opinions with key points.
    :return: A dictionary with article drafts.
    """
    logger.debug("<-----write_articles_draft state----->")
    opinions = state["opinions_with_keypoints"]
    logger.info(f"write articles: {len(opinions)} court opinions")
    res_article_drafts = []
    parser = JsonOutputParser()
    sys_intro = get_resource_content('prompts/draft_prompt.txt')
    sys_schema = get_resource_content('schemas/draft_output.json')
    sys_message = compose_sys_content(sys_intro, sys_schema)

    for opinion in opinions:
        id = opinion["id"]
        user_content = f"Here is a court opinion id#{id}:\n" + json.dumps(opinion)
        try:
            pipeline = client | parser
            json_obj = pipeline.invoke([
                    SystemMessage(content=sys_message),
                    HumanMessage(content=user_content)
                ]
            )

            if 'properties' not in json_obj:
                opinion["news_article"] = json_obj["news_article"]
                opinion["keywords"] = json_obj["keywords"]
                res_article_drafts.append(opinion)
            else:
                raise Exception("Illegal format of the json output")
        except Exception as e:
            logger.error(f"Error: processing opinion {opinion['resource_uri']}")
            logger.error(e)
    logger.debug("</-----write_articles_draft state----->")
    return {"article_drafts": res_article_drafts}

def editorial_assessment(state: Dict) -> Dict:
    article_drafts = state["article_drafts"]
    best_article_drafts = state["best_article_drafts"]
    if best_article_drafts is None:
        best_article_drafts = {}
    logger.info(f"editorial assessment: {len(article_drafts)} drafts")
    attempts = state.get("attempts")
    if attempts is None:
        attempts = 1
    res_article_drafts = []
    parser = JsonOutputParser()
    sys_intro = get_resource_content('prompts/article_assessment_prompt.txt')
    sys_schema = get_resource_content('schemas/article_assessment.json')
    sys_message = compose_sys_content(sys_intro, sys_schema)
    for article_draft in article_drafts:
        user_content = f"News article draft:\n\n" + article_draft["news_article"]
        try:
            pipeline = client | parser
            json_obj = pipeline.invoke([
                    SystemMessage(content=sys_message),
                    HumanMessage(content=user_content)
                ]
            )

            if 'properties' not in json_obj:
                article_draft["editor_feedback"] = json_obj
                res_article_drafts.append(article_draft)
                # best article estimation
                score_avg = sum([float(article_draft["editor_feedback"][crit]["score"]) for crit in article_draft["editor_feedback"]]) / len(article_draft["editor_feedback"])
                id = article_draft['id']
                if id not in best_article_drafts:
                    best_article_drafts[id] = {'news_article': article_draft['news_article'], 'keywords':  article_draft['keywords'], 'score': score_avg}
                elif best_article_drafts[id]['score'] < score_avg:
                    logger.info(f'Article draft {str(id)} was improved after revise')
                    best_article_drafts[id]['news_article'] = article_draft['news_article']
                    best_article_drafts[id]['keywords'] = article_draft['keywords']
                    best_article_drafts[id]['score'] = score_avg
            else:
                raise Exception("Illegal format of json output")
        except Exception as e:
            logger.error(f"Error: processing opinion {article_draft['resource_uri']}")
            logger.error(e)
    return {"article_drafts": res_article_drafts, "best_article_drafts": best_article_drafts, "attempts": attempts}

# Define the function that determines whether to continue or not
def should_continue(state: Dict) -> Literal["generate_headline", "rewrite_articles_draft"]:
    articles = state["article_drafts"]
    attempts = state["attempts"]
    logger.info(f"should continue? {attempts} attempts, {len(articles)} articles")
    if attempts < config.MAX_ATTEMPTS:
        for article in articles:
            assessment = article['editor_feedback']
            for k in assessment:
                criteria = assessment[k]
                if int(criteria["score"]) <= 8:
                    return "rewrite_articles_draft"
    return "generate_headline"

def rewrite_articles_draft(state: Dict) -> Dict:
    """
    Write draft articles based on the opinions with key points.

    :param state: The current state containing opinions with key points.
    :return: A dictionary with article drafts.
    """
    logger.info(f"re-write article")
    logger.debug("<-----re-write_articles_draft state----->")
    opinions = state["article_drafts"]
    attempts = state.get("attempts", 1)
    res_article_drafts = []
    parser = JsonOutputParser()
    sys_intro = get_resource_content('prompts/rewrite_draft_prompt.txt')
    sys_schema = get_resource_content('schemas/rewritten_draft_output.json')
    sys_message = compose_sys_content(sys_intro, sys_schema)

    for opinion in opinions:
        id = opinion["id"]
        user_content = f"Here is a court opinion id#{id}:\n" + json.dumps(opinion)
        try:
            pipeline = client | parser
            json_obj = pipeline.invoke([
                    SystemMessage(content=sys_message),
                    HumanMessage(content=user_content)
                ]
            )

            if 'properties' not in json_obj:
                opinion["news_article"] = json_obj["rewritten_news_article"]
                opinion["keywords"] = json_obj["keywords"]
                res_article_drafts.append(opinion)
            else:
                raise Exception("Illegal format of the json output")
        except Exception as e:
            logger.error(f"Error: processing opinion {opinion['resource_uri']}")
            logger.error(e)
    logger.debug("</-----re-write_articles_draft state----->")
    attempts += 1
    return {"article_drafts": res_article_drafts, "attempts": attempts, "best_article_drafts": state["best_article_drafts"]}


def generate_headline(state: Dict) -> Dict:
    """
    Write news headline based on the news content.

    :param state: The current state containing news articles content.
    :return: A dictionary with news articles with headlines.
    """
    logger.debug("<-----generate_headline state----->")
    article_drafts = state["article_drafts"]
    logger.info(f"generate headlines: {article_drafts} drafts")
    res_articles = []
    parser = JsonOutputParser()
    sys_intro = get_resource_content('prompts/headline_prompt.txt')
    sys_schema = get_resource_content('schemas/headline_output.json')
    sys_message = compose_sys_content(sys_intro, sys_schema)

    for article_draft in article_drafts:
        user_content = f"Keywords:\n" + ",".join([kw["keyword"] for kw in article_draft["keywords"]]) + \
                       f"\n\nNews article:\n:" + json.dumps(article_draft["news_article"])
        try:
            pipeline = client | parser
            json_obj = pipeline.invoke([
                    SystemMessage(content=sys_message),
                    HumanMessage(content=user_content)
                ]
            )

            if 'properties' not in json_obj:
                article  = {"source_date_created": article_draft["date_created"], "source_date_modified": article_draft["date_modified"],
                            "keypoints": article_draft["keypoints"], "headline": json_obj["headline"], "news_article": article_draft["news_article"]}
                article["keywords"] = [kw["keyword"] for kw in article_draft["keywords"]]
                article["date_created"] = datetime.now(UTC).isoformat()
                parsed = parse_url(article_draft["resource_uri"])
                source_url = parsed.scheme + "://" + parsed.host + article_draft["absolute_url"]
                article["source_url"] = source_url
                article["why_newsworthy"] = article_draft["reason"]
                if "people" in article_draft:
                    article["people"] = article_draft["people"]
                if "events" in article_draft:
                    article["events"] = article_draft["events"]
                if "organizations" in article_draft:
                    article["organizations"] = article_draft["organizations"]
                if "labels" in article_draft:
                    article["categories"] = article_draft["labels"]
                res_articles.append(article)
            else:
                raise Exception("Illegal format of json output")
        except Exception as e:
            logger.error(f"Error: processing opinion {article_draft['resource_uri']}")
            logger.error(e)
    logger.debug("</-----generate_headline state----->")
    return {"articles": res_articles}

def save_articles(state: Dict) -> Dict:
    """
    Store generated news articles in the output folder

    :param state: The current state containing news articles.
    :return: empty dictionary.
    """
    logger.debug("<-----save_articles state----->")
    article_drafts = state["articles"]
    logger.info(f"saving {len(article_drafts)} articles")
    dtstamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    filename = f"legal_news_materials_{dtstamp}.jsonl"
    output_dir = os.getenv('OUTPUT_DIR', 'output')
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with jsonlines.open(filepath, mode='w') as writer:
        writer.write_all(article_drafts)
    logger.debug("</-----save_articles state----->")
    return {"news_file": filepath, "news_num": len(article_drafts)}

def notify_subscribers(state: Dict) -> Dict:
    news_num = state["news_num"]
    if news_num == 0:
        return {"notification": "skipped"}
    news_file = state["news_file"]
    recipients = get_recipients()
    logger.info(f"news letter for {len(recipients)} subscribers")
    current_date = datetime.now(UTC).strftime('%B %d, %Y')
    subject = f'AI Assistant - Legal News Update - {current_date}'
    html_body = render_template('templates/email_html.jinja', news_file)
    txt_body = render_template('templates/email_txt.jinja', news_file)
    send_email(subject, html_body, txt_body, recipients)
    return {"notification": "done"}
