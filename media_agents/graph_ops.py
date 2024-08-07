import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema import HumanMessage, SystemMessage
from media_agents.app_resources import get_resource_content
from functools import cache
import logging
from typing import Dict
import media_agents.config

# Initialize logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)

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

# URL for Court Listener API
COURT_LISTENER_URL = 'https://www.courtlistener.com/api/rest/v3/opinions/?'

def fetch_update(state: Dict) -> Dict:
    """
    Fetch the latest court opinions updates from Court Listener.

    :param state: The current state containing the last processed opinion ID.
    :return: A dictionary with fetched opinions to check.
    """
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
    return {"opinions_to_check": opinion_objects}

def find_news_leads(state: Dict) -> Dict:
    """
    Identify newsworthy court opinions from the fetched updates.

    :param state: The current state containing opinions to check.
    :return: A dictionary with newsworthy opinions.
    """
    opinions_to_check = state["opinions_to_check"]
    newsworthy_opinions = []
    parser = JsonOutputParser()
    sys_intro = get_resource_content('prompts/newsworthiness_prompt.txt')
    sys_schema = get_resource_content('schemas/newsworthiness_output.json')
    sys_message = compose_sys_content(sys_intro, sys_schema)

    for opinion in opinions_to_check:
        id = opinion["id"]
        user_content = f"Here is a court opinion id#{id}:\n" + opinion["plain_text"]
        if 'SUPREME COURT' not in user_content:
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

    return {"newsworthy_opinions": newsworthy_opinions}

def extract_keypoints(state: Dict) -> Dict:
    """
    Extract key points from the newsworthy opinions.

    :param state: The current state containing newsworthy opinions.
    :return: A dictionary with opinions and their key points.
    """
    opinions = state["newsworthy_opinions"]
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
    return {"opinions_with_keypoints": res_opinions}

def write_articles_draft(state: Dict) -> Dict:
    """
    Write draft articles based on the opinions with key points.

    :param state: The current state containing opinions with key points.
    :return: A dictionary with article drafts.
    """
    opinions = state["opinions_with_keypoints"]
    return {"article_drafts": opinions}
