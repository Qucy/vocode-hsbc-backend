from .utils import send_post_request
import datetime
import json
from dataclasses import dataclass


@dataclass
class NewsArticle:
    id: str
    creation_date: datetime.date
    headline: str


def create_rkd_authorisation(username: str, password: str, appid: str) -> str:
    """
    Perform Refinitiv Knowledge Direct (RKD) Authorisation and return token if success.

    :param username: The username for RKD authorisation.
    :param password: The password for RKD authorisation.
    :param appid: The application ID for RKD authorisation.
    :returns: The token if authorisation is successful, otherwise None.
    """
    # create authentication request URL, message and header
    authenMsg = {
        "CreateServiceToken_Request_1": {
            "ApplicationID": appid,
            "Username": username,
            "Password": password,
        }
    }
    authenURL = (
        "https://api.rkd.refinitiv.com/api/"
        + "TokenManagement/TokenManagement.svc/REST/"
        + "Anonymous/TokenManagement_1/CreateServiceToken_1"
    )
    headers = {"content-type": "application/json;charset=utf-8"}

    print("Sending Authentication request message to RKD")
    authenResult = send_post_request(authenURL, authenMsg, headers)

    if authenResult and authenResult.status_code == 200:
        print("Authen success")
        print("response status %s" % (authenResult.status_code))
        token = authenResult.json()["CreateServiceToken_Response_1"]["Token"]
        return token

    print("RKD Authen failed")
    return None


def create_rkd_base_header(username: str, password: str, app_id: str) -> dict[str, str]:
    """Create base header for rkd request which includes token creation/authentication."""

    # Create Authorisation token
    token = create_rkd_authorisation(username, password, app_id)

    # create header for request and send
    headers = {
        "content-type": "application/json;charset=utf-8",
        "X-Trkd-Auth-ApplicationID": app_id,
        "X-Trkd-Auth-Token": token,
    }
    return headers


def retrieve_freetext_query(
    base_header, query, n_weeks_prior: int, query_aspect="headline", lang="EN"
) -> list[dict[str, str]]:
    """Perform free-text query on RKD; get headlines with query.
    Documentation on output fields available:
    https://support-portal.rkd.refinitiv.com/SupportSite/TestApi/Op?svc=News_1&op=RetrieveHeadlineML_1

    :param base_header: Post request header containing auth token
    :param query: Query string
    :param n_weeks_prior: Freshness of news to search in num weeks
    :param query_aspect: Where to search for query string; options: headline, body, both
    :param lang: Language of news to search; options: ZH, EN, None or Others in Refinitiv
    :returns: List of dictionaries containing news objects.
    """

    today = datetime.datetime.now()
    n_weeks_prior = today - datetime.timedelta(weeks=n_weeks_prior)

    freetext_query_url = "http://api.rkd.refinitiv.com/api/News/News.svc/REST/News_1/RetrieveHeadlineML_1"

    freetext_line = {
        "RetrieveHeadlineML_Request_1": {
            "HeadlineMLRequest": {
                "TimeOut": 0,
                "MaxCount": 10,
                "Direction": "Newer",
                "StartTime": n_weeks_prior.strftime("%Y-%m-%dT%H:%M:%S"),
                "EndTime": today.strftime("%Y-%m-%dT%H:%M:%S"),
                "Filter": [
                    {
                        "FreeTextConstraint": {
                            "Value": {"Text": query},
                            "where": query_aspect,  # options: headline, body, body
                        }
                    },
                    {
                        "MetaDataConstraint": {
                            "Value": {"Text": lang},  # ZH, EN, None
                            "class": "Language",
                        }
                    },
                ],
            }
        }
    }
    results_freetext = send_post_request(freetext_query_url, freetext_line, base_header)

    # load result; result is a valid JSON string
    results_freetext = json.loads(
        results_freetext.text, parse_int=str, parse_float=float
    )["RetrieveHeadlineML_Response_1"]["HeadlineMLResponse"]

    # check if there are results
    if results_freetext["HEADLINEML"] is None:
        raise KeyError(f"No freetext results for {query}")
    return results_freetext["HEADLINEML"]["HL"]


def parse_freetext_result(freetext_results: list[dict[str, str]]) -> list[NewsArticle]:
    """Parse freetext results from RKD and return a list of NewsArticle objects.
    Ignore articles that do not have 'Usable' status.
    :param freetext_results: A list of dictionaries containing freetext results from RKD.
    :returns: A list of NewsArticle objects parsed from the freetext results.
    """
    freetext_stories = []
    for ftr in freetext_results:
        # skip if story is not 'usable'
        if ftr["ST"] != "Usable":
            continue
        # parse date
        formatted_date = datetime.datetime.strptime(
            ftr["CT"], "%Y-%m-%dT%H:%M:%S%z"
        ).date()
        freetext_stories.append(
            NewsArticle(
                id=ftr["ID"],
                creation_date=formatted_date,
                headline=ftr["HT"],
            )
        )
    return freetext_stories
