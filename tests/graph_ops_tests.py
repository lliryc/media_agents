import pytest
from media_agents import graph_ops
import json
import bleu
import os

test_data_specimen = {"opinions": []}
def setup_module(graph_ops):
    with open("data/opinion1.json") as fh1:
        opinion1 = json.load(fh1)
        test_data_specimen["opinions"].append(opinion1)
def test_find_news_leads():
    state = {"opinions_to_check": test_data_specimen["opinions"]}
    os.chdir("../media_agents")
    new_state = graph_ops.find_news_leads(state)
    assert (("newsworthy_opinions" in new_state and len(new_state["newsworthy_opinions"]) == 1
            and new_state["newsworthy_opinions"][0]["newsworthy"] == "True")
            and new_state["newsworthy_opinions"][0]["influence"] == "Global")

def test_extract_keypoints():
    state = {"newsworthy_opinions": test_data_specimen["opinions"]}
    os.chdir("../media_agents")
    new_state = graph_ops.extract_keypoints(state)
    assert ("opinions_with_keypoints" in new_state and len(new_state["opinions_with_keypoints"]) == 1
            and len(new_state["opinions_with_keypoints"][0]["keypoints"]) > 0)

def write_articles_draft():
    state = {"opinions_with_keypoints": test_data_specimen["opinions"]}
    os.chdir("../media_agents")
    graph_ops.write_articles_draft(state)
    assert True






