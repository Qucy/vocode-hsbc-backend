from src.refinitiv_query import (
    create_rkd_base_header,
    retrieve_freetext_query,
    parse_freetext_result,
    NewsArticle,
)
import os
import datetime
from dotenv import load_dotenv

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


def test_freetext_query():
    """Test freetext query on RKD. Set a very generic query to ensure
    that there are results."""

    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)

    freetext_results = retrieve_freetext_query(base_header, "America", 4, "both", "EN")
    assert freetext_results is not None
    assert isinstance(freetext_results[0], dict)


def test_parse_freetext_query():
    """Test freetext query on RKD and the parser for it.
    Set a very generic query to ensure that there are results."""

    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)

    freetext_results = retrieve_freetext_query(base_header, "America", 4, "both", "EN")

    freetext_news_articles = parse_freetext_result(freetext_results)
    assert isinstance(freetext_news_articles, list)
    assert len(freetext_news_articles) > 0

    first_article = freetext_news_articles[0]
    assert isinstance(first_article, NewsArticle)
    assert isinstance(first_article.id, str)
    assert isinstance(first_article.creation_date, datetime.date)
    assert isinstance(first_article.headline, str)
