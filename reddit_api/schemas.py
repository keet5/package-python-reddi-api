from pydantic import BaseModel


class RedditFile(BaseModel):
    type: str
    data: bytes
    extension: str


class RedditPost(BaseModel):
    text: str
    type: str
    files: list[RedditFile]


post = RedditPost(text="test", type="dic", files=[])
