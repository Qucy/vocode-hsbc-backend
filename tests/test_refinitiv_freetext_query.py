import datetime
import os

from dotenv import load_dotenv

from src.newsearch.refinitiv_query import (
    NewsArticle,
    create_rkd_base_header,
    parse_freetext_headlines,
    parse_news_stories_texts,
    retrieve_freetext_headlines,
    retrieve_news_stories,
)

# load environment variables
load_dotenv()

# set global variables
RKD_USERNAME = os.getenv("REFINITIV_USERNAME")
RKD_PASSWORD = os.getenv("REFINITIV_PASSWORD")
RKD_APP_ID = os.getenv("REFINITIV_APP_ID")

"""
Note we assume that the tests run sequentially so that later tests build on 
functions that have been tested previously.
"""


def test_retrieving_baseheader():
    """Test retrieving base header for RKD request."""
    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)
    assert isinstance(base_header, dict)
    assert "content-type" in base_header.keys()
    assert "X-Trkd-Auth-ApplicationID" in base_header.keys()
    assert "X-Trkd-Auth-Token" in base_header.keys()


def test_freetext_headline():
    """Test freetext query on RKD. Set a very generic query to ensure
    that there are results."""

    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)

    freetext_results = retrieve_freetext_headlines(
        base_header, "America", 4, "both", "EN"
    )
    assert freetext_results is not None
    assert isinstance(freetext_results[0], dict)


def test_parse_freetext_headline():
    """Test freetext query on RKD and the parser for it.
    Set a very generic query to ensure that there are results."""

    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)

    freetext_results = retrieve_freetext_headlines(
        base_header, "America", 4, "both", "EN"
    )

    freetext_news_articles = parse_freetext_headlines(freetext_results)
    assert isinstance(freetext_news_articles, list)
    assert len(freetext_news_articles) > 0

    first_article = freetext_news_articles[0]
    assert isinstance(first_article, NewsArticle)
    assert isinstance(first_article.id, str)
    assert isinstance(first_article.creation_date, datetime.date)
    assert isinstance(first_article.headline, str)


def test_retrieve_news_stories():
    """Test freetext query on RKD and the parser for it.
    Then retrieve the top news stories."""

    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)

    freetext_results = retrieve_freetext_headlines(
        base_header, "America", 4, "both", "EN"
    )

    freetext_news_articles = parse_freetext_headlines(freetext_results)
    news_stories = retrieve_news_stories(
        base_header, [article.id for article in freetext_news_articles]
    )
    assert isinstance(news_stories, list)
    assert len(news_stories) > 0
    assert isinstance(news_stories[0], dict)


def test_parse_news_stories():
    """Test freetext query on RKD and the parser for it; as well as the story retrieval
    and parser for that also."""

    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)

    freetext_results = retrieve_freetext_headlines(
        base_header, "America", 4, "both", "EN"
    )

    freetext_news_articles = parse_freetext_headlines(freetext_results)
    news_stories = retrieve_news_stories(
        base_header, [article.id for article in freetext_news_articles]
    )
    news_stories_texts = parse_news_stories_texts(news_stories)

    # assign news story texts to Article object
    for idx, nst in enumerate(news_stories_texts):
        freetext_news_articles[idx].story = nst

    assert isinstance(news_stories_texts, list)
    assert len(news_stories_texts) > 0
    assert isinstance(news_stories_texts[0], str)
    assert isinstance(freetext_news_articles[0].story, str)
