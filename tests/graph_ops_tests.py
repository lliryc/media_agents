import pytest
from media_agents import graph_ops
import json
import bleu
import os

test_data_specimen = {"opinions": [], "opinions_with_keypoints": [], "article_drafts": []}
def setup_module(graph_ops):
    with open("data/opinion1.json", "r") as fh1:
        opinion1 = json.load(fh1)
        test_data_specimen["opinions"].append(opinion1)
    with open("data/opinion_with_keypoints2.json", "r") as fh2:
        opinion2 = json.load(fh2)
        test_data_specimen["opinions_with_keypoints"].append(opinion2)
    with open("data/article_draft1.json", "r") as fd1:
        article_draft1 = json.load(fd1)
        test_data_specimen["article_drafts"].append(article_draft1)

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
#    with open("opinion_with_keypoints2.json", "w") as fo:
#        json.dump(new_state["opinions_with_keypoints"][0], fo)
    assert ("opinions_with_keypoints" in new_state and len(new_state["opinions_with_keypoints"]) == 1
            and len(new_state["opinions_with_keypoints"][0]["keypoints"]) > 0)

def test_write_articles_draft():
    state = {"opinions_with_keypoints": test_data_specimen["opinions_with_keypoints"]}
    os.chdir("../media_agents")
    new_state = graph_ops.write_articles_draft(state)
    with open("article_draft1.json", "w") as fo:
        json.dump(new_state["article_drafts"][0], fo)
    assert(("article_drafts" in new_state) and len(new_state["article_drafts"]) == 1 and ("news_article" in new_state["article_drafts"][0]))

def test_write_articles_headline():
    state = {"article_drafts": test_data_specimen["article_drafts"]}
    os.chdir("../media_agents")
    new_state = graph_ops.generate_headline(state)
    assert(("articles" in new_state) and len(new_state["articles"]) == 1 and ("headline" in new_state["articles"][0]))








