from __future__ import annotations

import os
import re
from pathlib import Path

from jsonargparse import CLI
from pytube import YouTube
import webvtt
from yt_dlp import YoutubeDL


def get_youtube_channel_from_url(url: str) -> str:
    """Given a URL to a channel, video or playlist returns the channel name.

    Args:
        url (str): The YouTube URL.

    Returns:
        str: The channel name.

    Raises:
        ValueError: If the URL is not a YouTube URL.
    """
    # Check if the URL is a valid YouTube URL
    youtube_regex = (
        r"(https?://)?(www\.)?"
        r"(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
    )
    youtube_match = re.match(youtube_regex, url)
    if not youtube_match:
        raise ValueError("Invalid YouTube URL")

    # Extract the video ID and get the YouTube object
    video_id = youtube_match.group(6)
    video = YouTube(f"https://www.youtube.com/watch?v={video_id}")

    # Extract the channel name
    return video.channel_url


def get_youtubechannel_latest_video(url: str) -> str:
    pass


def get_subtitles_file_from_youtubevideo(
    video: YouTube, language: str = "en"
) -> str | None:
    """Download the subtitles file from a YouTube video to .cache folder."""

    dir_cache = (
        Path(os.path.dirname(os.path.realpath(__file__))).parent.resolve() / ".cache"
    )
    if not dir_cache.exists():
        os.mkdir(dir_cache)

    if (dir_cache / f"{video.video_id}.{language}.vtt").exists():
        return str(dir_cache / f"{video.video_id}.{language}.vtt")

    url = video.watch_url
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,  # Also download automatic subtitles if available
        "subtitleslangs": [language],
        "subtitlesformat": "vtt",  # Specify the desired subtitles format
        "outtmpl": str(dir_cache / "%(id)s.%(ext)s"),
        "ignoreerrors": True,
    }
    # Download subtitles using YoutubeDL
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

        # Getting the video id to form the subtitle file name
        info_dict = ydl.extract_info(url, download=False)
        video_id = info_dict.get("id", None)
        subtitle_file = (
            f".cache/{video_id}.en.vtt"  # Assuming .vtt format, adjust if necessary
        )
        return subtitle_file if os.path.exists(subtitle_file) else None


def get_uniquewords_from_vttfile(vttfile: str | Path) -> set[str]:
    """Get the unique words from a .vtt file."""

    if isinstance(vttfile, str):
        vttfile = Path(vttfile)
    assert vttfile.exists(), f"File {vttfile} does not exist."

    unique_words = set()

    # Parse the VTT file
    captions = webvtt.read(vttfile)

    # Iterate over the captions and extract words
    for caption in captions:
        # Remove non-alphabetic characters and split by whitespace
        words = re.findall(r"\b\w+\b", caption.text.lower())
        unique_words.update(words)

    return unique_words


def string_to_words(text: str) -> list[str]:
    """Converts a string to a list of words.

    Args:
        text: The text to be converted.

    Returns:
        A list of words.
    """

    return re.findall(r"\b\w+\b", text.lower())


def main(text: str, url: str):
    """Prints the prize won by a person.

    Args:
        text: The text to be generated.
        url: An URL pointing to a YouTube channel, video or playlist.
    """

    # TODO: Add languages support
    # TODO: Option for no video

    # youtube-dl --list-subs https://www.youtube.com/watch?v=...
    # youtube-dl --write-sub --sub-lang en --skip-download URL

    # --write-subs
    # p = 0


if __name__ == "__main__":
    # CLI(main)

    # main(
    #     "Hello, I'm bob",
    #     "https://www.youtube.com/watch?v=gveDhZW-rUk",
    # )

    # v = get_youtube_channel_from_url("https://www.youtube.com/watch?v=gveDhZW-rUk")

    o = get_subtitles_file_from_youtubevideo(
        YouTube("https://www.youtube.com/watch?v=gveDhZW-rUk")
    )
    u = get_uniquewords_from_vttfile(o)

    p = 0
