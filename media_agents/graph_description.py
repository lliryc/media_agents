from langchain.schema import Document
from langgraph.graph import END, StateGraph, START
from typing import Dict
from typing_extensions import TypedDict
from typing import List
from media_agents import graph_ops

### State

class GraphState(Dict):
    """
    Represents the state of our graph.

    Attributes:
        initial_opinion (str): The initial opinion of the court judge.
        news_story_criteria_score (List[int]): Scores indicating the newsworthiness based on various criteria.
        news_story_labels (List[str]): Labels identifying the news story elements present in the opinion.
        news_story_key_facts (List[str]): Key facts extracted from the opinion that are relevant to the news story.
        summary (str): A summary for the article.
    """
    last_processed_id: int
    opinions_to_check: List[Dict]
    newsworthy_opinions: List[Dict]
    opinions_with_keypoints: List[Dict]
    article_drafts: List[Dict]
    articles: List[Dict]
    news_file: str
    news_num: int
    notification: str
    attempts: int

def build_workfrlow():

    workflow = StateGraph(GraphState)

    workflow.add_node("init_agent", graph_ops.init_agent)
    workflow.add_edge(START, "init_agent")

    workflow.add_node("fetch_update", graph_ops.fetch_update)
    workflow.add_edge("init_agent", "fetch_update")

    workflow.add_node("find_news_leads", graph_ops.find_news_leads)
    workflow.add_edge("fetch_update", "find_news_leads")

    workflow.add_node("extract_keypoints", graph_ops.extract_keypoints)
    workflow.add_edge("find_news_leads", "extract_keypoints")

    workflow.add_node("write_articles_draft", graph_ops.write_articles_draft)
    workflow.add_edge("extract_keypoints", "write_articles_draft")

    workflow.add_node("editorial_assessment", graph_ops.editorial_assessment)
    workflow.add_edge("write_articles_draft", "editorial_assessment")

    workflow.add_node("rewrite_articles_draft", graph_ops.rewrite_articles_draft)
    workflow.add_node("generate_headline", graph_ops.generate_headline)
    workflow.add_conditional_edges("editorial_assessment", graph_ops.should_continue)

    workflow.add_node("save_articles", graph_ops.save_articles)
    workflow.add_edge("generate_headline", "save_articles")

    workflow.add_node("notify_subscribers", graph_ops.notify_subscribers)
    workflow.add_edge("save_articles", "notify_subscribers")

    workflow.add_edge(
        "notify_subscribers", END)

    return workflow

def compile_workflow(workflow):
    return  workflow.compile()


