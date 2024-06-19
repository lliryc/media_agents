from langchain.schema import Document
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from typing import List

### State

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        initial_opinion: court judge opinion
        news_story_score: score in terms of newsworthiness
        news_story_labels: what news story elements presented in the opinion
        summary: summary for the article
    """
    initial_opinion : str
    news_story_score : int
    news_story_labels : List[str]
    news_story_key_facts: List[str]
    summary: str
    
