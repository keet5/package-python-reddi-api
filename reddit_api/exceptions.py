class RedditException(Exception):
    pass


class RedditRequestError(RedditException):
    def __init__(self, code: int, url: str | None = None):
        self.code = code
        self.url = url


class Reddit403(RedditRequestError):
    pass
