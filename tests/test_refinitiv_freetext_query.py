from src.refinitiv_query import create_rkd_base_header, freetext_query
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# set global variables
RKD_USERNAME = os.getenv("REFINITIV_USERNAME")
RKD_PASSWORD = os.getenv("REFINITIV_PASSWORD")
RKD_APP_ID = os.getenv("REFINITIV_APP_ID")


def test_retrieving_baseheader():
    """Test retrieving base header for RKD request."""
    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)
    assert isinstance(base_header, dict)
    assert "content-type" in base_header.keys()
    assert "X-Trkd-Auth-ApplicationID" in base_header.keys()
    assert "X-Trkd-Auth-Token" in base_header.keys()


# test freetext query
def test_freetext_query():
    """Test freetext query on RKD."""

    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)

    freetext_results = freetext_query(base_header, "Microsoft", 2, "headline", "EN")
    assert "RetrieveHeadlineML_Response_1" in freetext_results.keys()
    print(freetext_results)
