import os
import subprocess
import json

def truncate_title(title, max_length=50):
    if len(title) <= max_length:
        return title

    truncated_title = title[:max_length].strip()
    last_space = truncated_title.rfind(" ")

    if last_space != -1:
        truncated_title = truncated_title[:last_space]

    return truncated_title


def download_audio(video_url, output_directory="output"):
    # Extract video information
    extract_info_command = [
        "yt-dlp",
        "--quiet",
        "--no-warnings",
        "--skip-download",
        "-J",
        video_url,
    ]
    video_info_json = subprocess.check_output(extract_info_command).decode("utf-8")
    video_info = json.loads(video_info_json)

    video_id = video_info["id"]
    video_title = truncate_title(video_info["title"])
    file_path = f"{output_directory}/{video_id} - {video_title}.mp3"

    # Download the video if the output file doesn't already exist
    if not os.path.exists(file_path):
        print(f"Downloading '{video_title}' to '{file_path}'...")
        download_command = [
            "yt-dlp",
            "-x",
            "--audio-format=mp3",
            "--output",
            f"{file_path}",
            video_url,
        ]
        (f"Invoking yt-dlp: {download_command}")
        subprocess.run(download_command)
        print("Download complete.")
    else:
        print(f"'{file_path}' already exists. Skipping download.")
