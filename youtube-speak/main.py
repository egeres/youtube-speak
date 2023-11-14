from __future__ import annotations

import glob
import os
import re
from datetime import timedelta
from pathlib import Path

import webvtt
from jsonargparse import CLI
from moviepy.editor import VideoFileClip, concatenate_videoclips

# from moviepy.video.fx.all import resize
from pytube import YouTube
from rich import print
from yt_dlp import YoutubeDL


# TODO: get_youtubechannel_latest_video
def get_youtubechannel_latest_video(url: str) -> str:
    pass


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


def get_video_file_from_youtubevideo(video: YouTube) -> str | None:
    dir_cache = (
        Path(os.path.dirname(os.path.realpath(__file__))).parent.resolve() / ".cache"
    )
    if not dir_cache.exists():
        os.mkdir(dir_cache)

    if (dir_cache / f"{video.video_id}.mp4").exists():
    # if len(glob.glob(f"{dir_cache}/{video.video_id}*.mp4")) > 0:
        return str(dir_cache / f"{video.video_id}.mp4")

    url = video.watch_url
    ydl_opts = {
        # "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        # "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "format": "worstvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": str(dir_cache / "%(id)s.%(ext)s"),
        "ignoreerrors": True,
    }
    # Download video using YoutubeDL
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

        # Getting the video id to form the subtitle file name
        info_dict = ydl.extract_info(url, download=False)
        video_id = info_dict.get("id", None)
        video_file = (
            f".cache/{video_id}.mp4"  # Assuming .vtt format, adjust if necessary
        )
        return video_file if os.path.exists(video_file) else None


def get_words_to_timestamp(vttfile: str | Path) -> dict[str, tuple[float, float]]:
    """Gets words from a VTT file and then returns a dictionary with the words and their
    timestamps."""

    if isinstance(vttfile, str):
        vttfile = Path(vttfile)
    assert vttfile.exists(), f"File {vttfile} does not exist."

    to_return: dict[str, tuple[float, float]] = {}

    unique_words = set()




    def foo(text: str) -> list[tuple[str, float | None]]:
        # Use regular expression to find all matches of the pattern
        pattern = r'<(\d{2}):(\d{2}):(\d{2}\.\d{3})><c>(.*?)<\/c>'
        matches = re.findall(pattern, text)

        result = []
        for match in matches:
            hours, minutes, seconds = match[0:3]
            word = match[3]

            # Convert hours, minutes, and seconds to a timedelta
            time_delta = timedelta(hours=int(hours), minutes=int(minutes), seconds=float(seconds))

            # Convert timedelta to total seconds
            total_seconds = time_delta.total_seconds()

            # Append the tuple to the result list
            result.append((word.strip(), total_seconds))

        # Handle the case for the last word which doesn't have a timestamp
        last_word = text.split('>')[-1]
        result.append((last_word, None))

        return result



    # Parse the VTT file
    captions = webvtt.read(vttfile)

    # # Iterate over the captions and extract words
    # for caption in captions:
    #     words = re.findall(r"\b\w+\b", caption.text.lower())
    #     for w_n, w in enumerate(words):
    #         if w not in unique_words:
    #             unique_words.add(w)
    #             to_return[w] = (caption.start_in_seconds, caption.end_in_seconds)

    v = 0
    for caption in captions:

        if caption.start_in_seconds < 20:
            continue

        # rawr = foo(caption.raw_text.strip())
        # rawr = foo(caption.lines[-1].strip())

        caption_text = caption.lines[-1].strip().lower()
        if caption_text == "":
            continue
        rawr = foo(caption_text)


        aaaa = [
            # (caption.raw_text.strip().split("<00")[0], rawr[0][1])
            (caption_text.strip().split("<00")[0], rawr[0][1])
        ]
        bbb = 0
        for i in rawr[:-1]:
            aaaa.append(i)
        bbb = 0
        for nnn, iii in enumerate(rawr[1:]):
            aaaa[nnn+1] = (aaaa[nnn+1][0], iii[1])
        bbb = 0

        # words = re.findall(r"\b\w+\b", caption_text)

        # 'just<00:00:20.939><c> as</c><00:00:21.060><c> easily</c><00:00:21.359><c> been</c><00:00:21.600><c> entitled</c><00:00:22.080><c> music</c><00:00:22.680><c> is</c>'

        words = [x[0] for x in aaaa]
        current_start = caption.start_in_seconds
        for w_n, w in enumerate(words):

            current_end = aaaa[w_n][1]
            if current_end is None:
                current_end = caption.end_in_seconds
                
            if w not in unique_words:
                unique_words.add(w)
                to_return[w] = (current_start, current_end)

            current_start = current_end
        z = 0

    return to_return


def string_to_words(text: str) -> list[str]:
    """Converts a string to a list of words.

    Args:
        text: The text to be converted.

    Returns:
        A list of words.
    """

    # return re.findall(r"\b[\w']+\b", text.lower())
    return text.lower().split(" ")


def main(text: str, url: str, time_wordpadding:float=0.01):
    """Prints the prize won by a person.

    Args:
        text: The text to be generated.
        url: An URL pointing to a YouTube channel, video or playlist.
    """

    # TODO: Add languages support
    # TODO: Option for no video
    # TODO: Statistics to
    # TODO: Sub-word composition!!
    # TODO: Genration gets multiple versions of the same word
    # TODO: Parameter of spacing in between words I guess
    # TODO: [SILENCE 10s] ?
    # TODO: Add whisper for custom videos
    # youtube-dl --list-subs https://www.youtube.com/watch?v=...
    # youtube-dl --write-sub --sub-lang en --skip-download URL
    # --write-subs
    # p = 0

    # v = get_youtube_channel_from_url("https://www.youtube.com/watch?v=gveDhZW-rUk")

    o = get_subtitles_file_from_youtubevideo(
        YouTube("https://www.youtube.com/watch?v=gveDhZW-rUk")
    )
    assert o is not None
    u = get_words_to_timestamp(o)
    z = get_video_file_from_youtubevideo(
        YouTube("https://www.youtube.com/watch?v=gveDhZW-rUk")
    )
    # teeext = "life is a podcast"
    # teeext = "life is"


    # for w in string_to_words(teeext):
    #     if w in u:
    #         print(w, u[w])
    #         start_in_s = u[w][0]
    #         end_in_s = u[w][1]


    # video = VideoFileClip(z)
    # clips = []
    # for word, (start_in_s, end_in_s) in u.items():
    #     clip = video.subclip(start_in_s, end_in_s)
    #     clips.append(clip)
    # final_clip = concatenate_videoclips(clips)
    # final_clip.write_videofile("final_output_video.mp4")


    video = VideoFileClip(z)
    clips = []
    for w in string_to_words(text):
        if w in u:
            start_in_s = u[w][0]
            end_in_s = u[w][1]
            clip = video.subclip(
                start_in_s - time_wordpadding,
                end_in_s   + time_wordpadding,
            )
            clips.append(clip)
            print(f"[green]{w} [/green]", end="")
        else:
            # print(f"Word {w} not found in the video...")
            print(f"[red]{w} [/red]", end="")
    print ("")

    final_clip = concatenate_videoclips(clips)
    # final_clip =  resize(final_clip, newsize=(640, 480)) # TODO
    final_clip.write_videofile(
        "final_output_video.mp4",
        bitrate="100k",
    )

    # 🍑 Just a silly test
    # video = VideoFileClip(z)
    # clips = [video.subclip(0, 5), video.subclip(100, 105)]
    # final_clip = concatenate_videoclips(clips)
    # final_clip.write_videofile(
    #     "final_output_video.mp4",
    #     bitrate="100k",
    # )
    # p = 0

    # fmpeg -i gveDhZW-rUk.webm -c:v libx264 -preset veryfast -c:a aac output.mp4 -threads 0 


if __name__ == "__main__":
    # CLI(main)

    main(
        # "i i i i i i",
        # "don't listen to music every day because it's bad for your brain",
        "your brain is not music",
        "https://www.youtube.com/watch?v=gveDhZW-rUk",
    )

    p = 0
