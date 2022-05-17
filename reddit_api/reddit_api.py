from typing import Generator, Iterable
from .reddit_requests import request
from .handler import post_handler
from .schemas import RedditPost


class RedditAPI:
    def __init__(
        self,
        subreddit: str,
        after: str | None = None,
        limit: int = 10,
    ):
        self.after = after
        self.subreddit = subreddit
        self.limit = limit
        self.posts: list[dict] = []

    def get_posts(self) -> Generator[RedditPost, None, None]:
        if len(self.posts) == 0:
            self.load_posts()
        for post in self.posts:
            yield post_handler(post)

    def load_posts(self):
        url = f"https://reddit.com/r/{self.subreddit}/new.json"
        params = {
            "limit": self.limit,
            "after": self.after,
        }
        res = request(url, params)
        data = res.json()["data"]
        self.after = data["after"]
        posts = map(post_dict_handler, data["children"])
        self.posts += list(posts)


def post_dict_handler(post):
    post = post["data"]

    if "post_hint" in post:
        pass
    elif not "post_hint" in post and "media_metadata" in post:
        post["post_hint"] = "metadata"
    else:
        post["post_hint"] = f" What the Hell Are You? {post['id']}"

    return post
