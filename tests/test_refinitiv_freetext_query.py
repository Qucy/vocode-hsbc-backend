from src.refinitiv_query import create_rkd_base_header
import os
from dotenv import load_dotenv
import logging

# load environment variables
load_dotenv()

# set global variables
RKD_USERNAME = os.getenv("REFINITIV_USERNAME")
RKD_PASSWORD = os.getenv("REFINITIV_PASSWORD")
RKD_APP_ID = os.getenv("REFINITIV_APP_ID")

# setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_retrieving_baseheader():
    """Test retrieving base header for RKD request."""

    logger.info("Start testing retrieving base header for RKD request")

    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)
    assert isinstance(base_header, dict)
    assert "content-type" in base_header.keys()
    assert "X-Trkd-Auth-ApplicationID" in base_header.keys()
    assert "X-Trkd-Auth-Token" in base_header.keys()

    logger.info("End testing retrieving base header for RKD request")
