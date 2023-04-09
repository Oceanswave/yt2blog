import os
import openai
import tiktoken
import regex as re


def create_chunks(tt_encoding, text, chunkSize):
    # Split the text into sentences
    sentences = re.split("(?<=[.!?])+", text)
    print(sentences)
    # Group the sentences into chunks
    max_chunk_size = chunkSize  # Taking consideration of the extra tokens of prompts
    chunks = []
    current_chunk = ""
    current_chunk_tokens = 0

    for i, sentence in enumerate(sentences):
        sentence_tokens = len(tt_encoding.encode(sentence))
        if current_chunk_tokens + sentence_tokens > max_chunk_size:
            # Add the current chunk to the list of chunks
            chunks.append((current_chunk_tokens, current_chunk))
            # Start a new chunk with the last sentence of the previous chunk
            current_chunk = sentences[i - 1] + sentence
            current_chunk_tokens = len(tt_encoding.encode(current_chunk))
        else:
            # Add the sentence to the current chunk, with overlap if not first chunk
            if current_chunk:
                current_chunk += " " + sentence
                current_chunk_tokens += sentence_tokens
            else:
                current_chunk = sentence
                current_chunk_tokens = sentence_tokens

    # Add the last chunk to the list of chunks
    chunks.append((current_chunk_tokens, current_chunk))
    return chunks


def blogify(paragraphs):
    opanai_api_key = os.environ.get("OPENAI_API_KEY")
    if opanai_api_key == None:
        print("OPENAI_API_KEY is not set")
        exit(1)

    openai.api_key = opanai_api_key

    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo-0301")

    # for now, just join all the sentences in each together
    raw_text = ""
    current_speaker = -1
    for paragraph in paragraphs:
        if paragraph["speaker"] != current_speaker:
            current_speaker = paragraph["speaker"]
            raw_text += f"Speaker {current_speaker}: \r\n"
        for sentence in paragraph["sentences"]:
            sentenceText = sentence["text"]
            raw_text += f"\t{sentenceText}\r\n"

    tt_encoding = tiktoken.encoding_for_model(model)
    chunks = create_chunks(tt_encoding, raw_text, 2049) # gpt-3.5-turbo-0301 has a max of 4096 tokens

    final_response = []
    for i, (tokens, chunk) in enumerate(chunks):
        print(f'Chunk [{i}]: {chunk}\nTokens: {tokens}\n')
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Ignore all previous instructions.  You are a Principal Software Architect for a famous online tech website. Your task is to write engaging and helpful blob posts from the given context.",
                },
                {
                    "role": "user",
                    "content": f"Ignore all previous instructions. Here is your new role and persona: You are a Principal Software Architect for a famous online tech website. Your task is to write engaging and helpful blob posts from the given context:\n {chunk}",
                },
            ],
        )

        final_response.append(response)

    return final_response
