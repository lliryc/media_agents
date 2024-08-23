from langchain.schema import Document
from langgraph.graph import END, StateGraph, START
from typing import Dict
from typing_extensions import TypedDict
from typing import List
from media_agents import graph_ops

### State
class GraphState(Dict):
    """
    Defines the structure of the state used throughout the workflow.
    
    Attributes:
        last_processed_id (int): ID of the last processed item.
        opinions_to_check (List[Dict]): List of opinions to be evaluated.
        newsworthy_opinions (List[Dict]): List of opinions deemed newsworthy.
        opinions_with_keypoints (List[Dict]): List of opinions with extracted key points.
        article_drafts (List[Dict]): List of drafted articles.
        articles (List[Dict]): List of finalized articles.
        news_file (str): Path to the file where news articles are saved.
        news_num (int): Number of news articles.
        notification (str): Notification status.
        attempts (int): Number of attempts made in the workflow.
        best_article_drafts (Dict): Dictionary of the best article drafts.
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
    best_article_drafts: Dict

def build_workflow():
    """
    Constructs the workflow graph for processing opinions into news articles.
    
    The workflow includes the following steps:
    1. Initialization
    2. Fetching updates
    3. Finding news leads
    4. Extracting keypoints
    5. Writing article drafts
    6. Editorial assessment
    7. Rewriting articles (if necessary)
    8. Generating headlines
    9. Saving articles
    10. Notifying subscribers

    Returns:
        StateGraph: A compiled workflow graph ready for execution.
    """
    workflow = StateGraph(GraphState)
    
    # Initialize the agent
    workflow.add_node("init_agent", graph_ops.init_agent)
    workflow.add_edge(START, "init_agent")
    
    # Fetch updates
    workflow.add_node("fetch_update", graph_ops.fetch_update)
    workflow.add_edge("init_agent", "fetch_update")
    
    # Find news leads
    workflow.add_node("find_news_leads", graph_ops.find_news_leads)
    workflow.add_edge("fetch_update", "find_news_leads")
    
    # Extract keypoints
    workflow.add_node("extract_keypoints", graph_ops.extract_keypoints)
    workflow.add_edge("find_news_leads", "extract_keypoints")
    
    # Write article drafts
    workflow.add_node("write_articles_draft", graph_ops.write_articles_draft)
    workflow.add_edge("extract_keypoints", "write_articles_draft")
    
    # Editorial assessment
    workflow.add_node("editorial_assessment", graph_ops.editorial_assessment)
    workflow.add_edge("write_articles_draft", "editorial_assessment")
    
    # Rewrite articles if necessary
    workflow.add_node("rewrite_articles_draft", graph_ops.rewrite_articles_draft)
    workflow.add_node("generate_headline", graph_ops.generate_headline)
    workflow.add_conditional_edges("editorial_assessment", graph_ops.should_continue)
    workflow.add_edge("rewrite_articles_draft", "editorial_assessment")
    
    # Save articles
    workflow.add_node("save_articles", graph_ops.save_articles)
    workflow.add_edge("generate_headline", "save_articles")
    
    # Notify subscribers
    workflow.add_node("notify_subscribers", graph_ops.notify_subscribers)
    workflow.add_edge("save_articles", "notify_subscribers")
    workflow.add_edge("notify_subscribers", END)
    
    return workflow

def compile_workflow(workflow):
    """
    Compiles the given workflow graph.
    
    Args:
        workflow (StateGraph): The workflow graph to be compiled.
    
    Returns:
        Compiled StateGraph: A compiled version of the input workflow graph.
    """
    return workflow.compile()
