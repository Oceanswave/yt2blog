import os
from deepgram import Deepgram


def transcribe_audio(audio_file_url):
    deepgram_api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not deepgram_api_key:
        print("Please set the DEEPGRAM_API_KEY environment variable")
        return

    dg = Deepgram(deepgram_api_key)
    source = {"url": audio_file_url}
    options = {
        "punctuate": True,
        "smart_format": True,
        "diarize": True,
        "paragraphs": True,
        "summarize": True,
        "model": "general",
        "language": "en-US",
        "tier": "enhanced",
    }

    try:
        response = dg.transcription.sync_prerecorded(source, options)
    except Exception as e:
        print(f"Error while transcribing: {e}")
        return

    return response
