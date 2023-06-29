import requests
import json


def send_post_request(
    url: str,
    requestMsg: dict[str, dict[str, str]],
    headers: dict[str, str],
    has_timeout_already: bool = False,
) -> requests.models.Response:
    """Send a post request to url with data in request_msg and header also."""
    result = None
    try:
        result = requests.post(url, data=json.dumps(requestMsg), headers=headers)
        if result.status_code != 200:
            result.raise_for_status()
        return result

    except requests.exceptions.Timeout:
        if has_timeout_already:
            print(f"Timeout error. Tried again with {url} but still failed.")
            raise SystemExit("Timeout error. Tried again but still failed.")
        else:
            print(f"Timeout error. Trying again with {url}")
            return send_post_request(url, requestMsg, headers, True)

    except requests.exceptions.TooManyRedirects:
        print(f"The URL {url} is bad. Try a different one.")
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)