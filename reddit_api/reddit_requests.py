from requests import get

from .exceptions import RedditRequestError, Reddit403


def request(url, params: dict = dict()):
    res = get(
        url,
        params=params,
        headers={"User-agent": "your bot 0.1"},
    )

    if not res.ok:
        if res.status_code == 403:
            raise Reddit403(res.status_code, url)

        raise RedditRequestError(res.status_code, url)

    return res
