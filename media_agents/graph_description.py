from langchain.schema import Document
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from typing import List

### State

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        initial_opinion (str): The initial opinion of the court judge.
        news_story_criteria_score (List[int]): Scores indicating the newsworthiness based on various criteria.
        news_story_labels (List[str]): Labels identifying the news story elements present in the opinion.
        news_story_key_facts (List[str]): Key facts extracted from the opinion that are relevant to the news story.
        summary (str): A summary for the article.
    """
    initial_opinion: str
    news_story_criteria_score: List[int]
    news_story_labels: List[str]
    news_story_key_facts: List[str]
    summary: str