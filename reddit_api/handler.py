import re
import os
import io
from operator import itemgetter


from .reddit_requests import request
from .schemas import RedditPost, RedditFile
from .exceptions import Reddit403


def post_handler(post: dict) -> RedditPost:
    title, selftext, post_hint = itemgetter("title", "selftext", "post_hint")(post)
    files = []

    if post_hint == "image":
        url = post["url"]
        image = upload_data(post["url"])
        post_type = "image"
        extension = url.split(".")[-1]
        file = RedditFile(data=image, type="image", extension=extension)
        files.append(file)
    elif post_hint == "hosted:video":
        url = post["secure_media"]["reddit_video"]["fallback_url"]
        video = handler_video(url)
        file = RedditFile(data=video, type="video", extension="mp4")
        files.append(file)
        post_type = "video"
    elif post_hint == "metadata":
        post_type = "metadata"
        for _, item in post["media_metadata"].items():
            if item["e"] == "Image":
                extension = item["m"].split("/")[1]
                id = item["id"]
                url = f"https://i.redd.it/{id}.{extension}"
                image = upload_data(url)
                file = RedditFile(data=image, type="image", extension=extension)
                files.append(file)
            else:
                post_type += f" {item['e']}"
    else:
        post_type = post_hint

    text = ("\n".join([title, selftext])).strip()
    post = RedditPost(text=text, type=post_type, files=files)

    return post


def upload_data(url: str) -> bytes:
    res = request(url)
    return res.content


def handler_video(url: str):
    video_path = "temporary_video.mp4"
    audio_path = "temporary_audio.mp4"
    result_path = "temporary_result.mp4"

    try:
        res = request(url)

        with open(video_path, "wb") as video_file:
            video_file.write(res.content)

        url = re.sub(r"_\d*", "_audio", url)
        res = request(url)

        with open(audio_path, "wb") as audio_file:
            audio_file.write(res.content)

        add_audio(video_path, audio_path, result_path)

        with open(result_path, "rb") as result_file:
            video_result = result_file.read()

    except Reddit403:
        with open(video_path, "rb") as video:
            video_result = video.read()

        return video_result

    finally:
        for file in [video_path, audio_path, result_path]:
            if os.path.isfile(file):
                os.remove(file)

    return video_result


def add_audio(video: str, audio: str, output_video: str):
    os.system(
        f"ffmpeg\
            -y\
            -hide_banner\
            -loglevel error\
            -i {video}\
            -i {audio}\
            -map 0:v\
            -map 1:a\
            -c:v copy\
            -shortest\
            {output_video}"
    )
