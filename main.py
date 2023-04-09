import os
import argparse
import yaml
import json
from dotenv import load_dotenv
import modules.audio_download_service as audio_download_service
import modules.audio_repository as audio_repository
import modules.transcription_service as transcription_service
import modules.blogification_service as blogification_service

def process_blog_post(blog_post, output_directory="output"):
    target_file_path = os.path.join(output_directory, blog_post["slug"])
    print(f"Downloading videos into '{target_file_path}'...")

    video_urls = blog_post["video_urls"]
    print(video_urls)
    for url in video_urls:
        audio_download_service.download_audio(url, target_file_path)

    for file_name in os.listdir(target_file_path):
        if file_name.endswith(".mp3"):
            # If there isn't a corresponding .json file, transcribe the audio
            json_file_path = os.path.splitext(file_name)[0] + ".json"
            if os.path.exists(os.path.join(target_file_path, json_file_path)):
                print(
                    f"Skipping transcription of '{file_name}' because '{json_file_path}' already exists."
                )
            else:
                audio_file_path = os.path.join(target_file_path, file_name)
                print(f"Storing '{audio_file_path}'...")
                audio_file_url = audio_repository.store_audio(audio_file_path)
                print(f"Transcribing audio at '{audio_file_url}'...")
                transcription = transcription_service.transcribe_audio(audio_file_url)
                if transcription:
                    print(f"Writing transcription to '{json_file_path}'...")
                    with open(os.path.join(target_file_path, json_file_path), "w") as f:
                        json.dump(transcription, f, indent=4)
                # Remove the audio file from the audio repository
                audio_repository.remove_audio(audio_file_url)

            # if there isn't a corresponding .txt file, run the transcription through the summarizer
            txt_file_path = os.path.splitext(file_name)[0] + ".txt"
            if os.path.exists(os.path.join(target_file_path, txt_file_path)):
                print(
                    f"Skipping summarization of '{file_name}' because '{txt_file_path}' already exists."
                )
            else:
                # Open the json file and extract the transcription - specifically, we want the paragraphs
                json_file_path = os.path.splitext(file_name)[0] + ".json"
                with open(os.path.join(target_file_path, json_file_path), "r") as f:
                    transcription = json.load(f)
                paragraphs = transcription["results"]["channels"][0]["alternatives"][0]["paragraphs"]

                raw_text = ""
                current_speaker = -1
                for paragraph in paragraphs["paragraphs"]:
                    if (paragraph["speaker"] != current_speaker):
                        current_speaker = paragraph["speaker"]
                        raw_text += f"Speaker {current_speaker}: \r\n"
                    for sentence in paragraph["sentences"]:
                        sentenceText = sentence["text"]
                        raw_text += f"\t{sentenceText}\r\n"

                with open(
                    os.path.join(
                        target_file_path, os.path.splitext(file_name)[0] + "-paragraphs.txt"
                    ),
                    "w",
                ) as f:
                    f.write(raw_text)
                blog = blogification_service.blogify(paragraphs["paragraphs"])

                # Write the blog to a file
                print(f"Writing blog to '{txt_file_path}'...")
                finalContent = []
                for index, response in enumerate(blog):
                    finalContent.append(response["choices"][0]["message"]["content"])
                    with open(
                        os.path.join(
                            target_file_path,
                            os.path.splitext(file_name)[0] + f"-summary-{index}.json",
                        ),
                        "w",
                    ) as f:
                        f.write(json.dumps(response, indent=4))
                blog_body = "\r\n".join(finalContent)
                with open(os.path.join(target_file_path, txt_file_path), "w") as f:
                    f.write(blog_body)

def main():
    load_dotenv()  # Load environment variables from the .env file

    parser = argparse.ArgumentParser(
        description="Download and transcribe YouTube videos."
    )
    parser.add_argument("file", help="A file containing a list of video URLs.")
    parser.add_argument(
        "--output",
        help="The subdirectory to place the downloaded audio in.",
        default="output",
    )
    args = parser.parse_args()

    blog_posts = []
    with open(args.file, "r") as f:
        blog_posts = yaml.safe_load(f)

    print(blog_posts)
    for blog_post in blog_posts:
        print(blog_post)
        process_blog_post(blog_post, args.output)

if __name__ == "__main__":
    main()
