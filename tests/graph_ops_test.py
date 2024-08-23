import pytest
from media_agents import graph_ops
from media_agents.graph_description import GraphState
import json
import bleu
import os
import datetime
import logging_init

from langchain.schema import Document
from langgraph.graph import END, StateGraph, START
from typing import Dict
from typing_extensions import TypedDict
from typing import List

# Test data specimen setup
test_data_specimen = {"opinions": [], "opinions_with_keypoints": [],
                      "newsworthy_opinions": [], "article_drafts": [], "articles": [],
                      "news_file": "", "article_drafts_feedback": []}

def setup_module(graph_ops):
    """
    Set up test data by loading various JSON files into the test_data_specimen dictionary.
    This function prepares the test environment with sample data for opinions, newsworthy opinions,
    opinions with keypoints, article drafts, articles, and article draft feedback.
    """
    # Load test data from JSON files
    with open("tests/data/opinion1.json", "r") as fh1:
        opinion1 = json.load(fh1)
        test_data_specimen["opinions"].append(opinion1)
    # ... [similar loading for other JSON files]

    test_data_specimen["attempts"] = 1
    test_data_specimen["news_file"] = "tests/data/legal_news_materials_1.jsonl"
    test_data_specimen["news_num"] = 3

def test_find_news_leads():
    """
    Test the find_news_leads function from graph_ops.
    
    This test checks if the function correctly identifies newsworthy opinions.
    It asserts that the resulting state contains a newsworthy opinion marked as "True"
    with "Global" influence.
    """
    state = {"opinions_to_check": test_data_specimen["opinions"]}
    new_state = graph_ops.find_news_leads(state)
    assert (("newsworthy_opinions" in new_state and len(new_state["newsworthy_opinions"]) == 1
            and new_state["newsworthy_opinions"][0]["newsworthy"] == "True")
            and new_state["newsworthy_opinions"][0]["influence"] == "Global")

def test_extract_keypoints():
    """
    Test the extract_keypoints function from graph_ops.
    
    This test verifies if keypoints are successfully extracted from newsworthy opinions.
    It asserts that the resulting state contains opinions with keypoints.
    """
    state = {"newsworthy_opinions": test_data_specimen["newsworthy_opinions"]}
    new_state = graph_ops.extract_keypoints(state)
    assert ("opinions_with_keypoints" in new_state and len(new_state["opinions_with_keypoints"]) == 1
            and len(new_state["opinions_with_keypoints"][0]["keypoints"]) > 0)

def test_write_articles_draft():
    """
    Test the write_articles_draft function from graph_ops.
    
    This test checks if article drafts are generated from opinions with keypoints.
    It asserts that the resulting state contains article drafts with a "news_article" field.
    """
    state = {"opinions_with_keypoints": test_data_specimen["opinions_with_keypoints"]}
    new_state = graph_ops.write_articles_draft(state)
    assert(("article_drafts" in new_state) and len(new_state["article_drafts"]) == 1 and ("news_article" in new_state["article_drafts"][0]))

def test_editorial_assessment():
    """
    Test the editorial_assessment function from graph_ops.
    
    This test verifies if editorial feedback is added to article drafts.
    It asserts that the resulting state contains article drafts with "editor_feedback".
    """
    state = {"article_drafts": test_data_specimen["article_drafts"], "best_article_drafts": {}}
    new_state = graph_ops.editorial_assessment(state)
    assert(("article_drafts" in new_state) and (len(new_state["article_drafts"]) == 1) and ("editor_feedback" in new_state["article_drafts"][0]))
    article = new_state["article_drafts"][0]
    with open("article_draft_feedback1.json", "w") as ffd:
        json.dump(article, ffd)

def test_should_continue_loop1():
    """
    Test the should_continue function from graph_ops for continuing the loop.
    
    This test checks if the function correctly decides to continue the loop
    (rewrite articles) when attempts are low.
    It asserts that the function returns "rewrite_articles_draft".
    """
    state = {"article_drafts": test_data_specimen["article_drafts_feedback"], "attempts": 1}
    fname = graph_ops.should_continue(state)
    assert(fname == "rewrite_articles_draft")

def test_should_continue_stop1():
    """
    Test the should_continue function from graph_ops for stopping the loop (max attempts).
    
    This test verifies if the function correctly decides to stop the loop
    when the maximum attempts are reached.
    It asserts that the function returns "generate_headline".
    """
    state = {"article_drafts": test_data_specimen["article_drafts_feedback"], "attempts": 4}
    fname = graph_ops.should_continue(state)
    assert(fname == "generate_headline")

def test_should_continue_stop2():
    """
    Test the should_continue function from graph_ops for stopping the loop (high quality).
    
    This test checks if the function correctly decides to stop the loop
    when the article quality is high.
    It asserts that the function returns "generate_headline".
    """
    state = {"article_drafts": test_data_specimen["article_drafts_feedback"], "attempts": 1}
    keys_list = list(state["article_drafts"][0]["editor_feedback"].keys())
    for k in keys_list:
        cr = state["article_drafts"][0]["editor_feedback"][k]
        cr["score"] = 9
        state["article_drafts"][0]["editor_feedback"][k] = cr

    fname = graph_ops.should_continue(state)
    assert(fname == "generate_headline")

def test_write_articles_headline():
    """
    Test the generate_headline function from graph_ops.
    
    This test verifies if headlines are generated for article drafts.
    It asserts that the resulting state contains articles with headlines.
    """
    state = {"article_drafts": test_data_specimen["article_drafts"]}
    new_state = graph_ops.generate_headline(state)
    assert(("articles" in new_state) and len(new_state["articles"]) == 1 and ("headline" in new_state["articles"][0]))

def test_save_articles():
    """
    Test the save_articles function from graph_ops.
    
    This test checks if articles are saved to a file.
    It asserts that the file is created and then removes it.
    """
    state = {"articles": test_data_specimen["articles"]}
    new_state = graph_ops.save_articles(state)
    assert "news_file" in new_state
    filepath = new_state["news_file"]
    assert os.path.exists(filepath)
    os.remove(filepath)

def test_notification():
    """
    Test the notify_subscribers function from graph_ops for sending notifications.
    
    This test verifies if notifications are sent when there are news articles.
    It asserts that the notification state is set to "done".
    """
    state = {"news_file": test_data_specimen["news_file"], "news_num": 1}
    new_state = graph_ops.notify_subscribers(state)
    assert "notification" in new_state
    assert new_state["notification"] == "done"

def test_notification_skip():
    """
    Test the notify_subscribers function from graph_ops for skipping notifications.
    
    This test checks if notifications are skipped when there are no news articles.
    It asserts that the notification state is set to "skipped".
    """
    state = {"news_file": test_data_specimen["news_file"], "news_num": 0}
    new_state = graph_ops.notify_subscribers(state)
    assert "notification" in new_state
    assert new_state["notification"] == "skipped"

def test_loop():
    """
    Test the entire workflow graph.
    
    This test verifies if the graph correctly processes article drafts through
    editorial assessment, rewriting, and headline generation.
    It asserts that the final state contains articles with headlines.
    """
    workflow = StateGraph(GraphState)

    workflow.add_node("editorial_assessment", graph_ops.editorial_assessment)
    workflow.add_node("rewrite_articles_draft", graph_ops.rewrite_articles_draft)
    workflow.add_node("generate_headline", graph_ops.generate_headline)
    workflow.add_conditional_edges("editorial_assessment", graph_ops.should_continue)
    workflow.add_edge("rewrite_articles_draft", "editorial_assessment")

    workflow.add_edge(START, "editorial_assessment")
    workflow.add_edge("generate_headline", END)

    graph = workflow.compile()

    new_state = graph.invoke({"article_drafts": test_data_specimen["article_drafts"]})

    assert(("articles" in new_state) and len(new_state["articles"]) == 1 and ("headline" in new_state["articles"][0]))
