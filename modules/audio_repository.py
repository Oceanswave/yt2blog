import os, uuid
from azure.storage.blob import BlobServiceClient

def store_audio(audio_file_path):
    connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client('deepgram', blob=f'{str(uuid.uuid4())}.mp3')

    print("\nUploading to Azure Storage as blob: " + blob_client.url)

    # Upload the created file
    with open(file=audio_file_path, mode="rb") as data:
        blob_client.upload_blob(data)

    return blob_client.url

# Removes the specified audio file from the audio repository
def remove_audio(blob_url):
    connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get the blob name from the blob URL
    blob_relative_url = blob_url.split("/")[-1]

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client('deepgram', blob=blob_relative_url)

    # Delete the blob if it exists
    print("\nDeleting blob: " + blob_client.url)
    blob_client.delete_blob()
