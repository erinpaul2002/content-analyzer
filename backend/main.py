from validators.youtube import get_youtube_video_details, extract_youtube_video_id, get_youtube_transcript
from dotenv import load_dotenv
from utils.pinecone_client import PineconeHandler
from utils.transcripts import save_transcript, load_transcripts, transcript_exists
import os
load_dotenv()
YOUTUBE_URL = os.getenv("YOUTUBE_URL")


def main():
    pinecone_client = PineconeHandler()
    url = YOUTUBE_URL
    video_id = extract_youtube_video_id(url)
    
    result = get_youtube_video_details(video_id)
    transcript = get_youtube_transcript(video_id)
    if transcript_exists(video_id):
        print(f"Transcript for video ID {video_id} already exists. Loading from file.")
        existing_data = load_transcripts(video_id)
        print(existing_data)
    else:
        data ={
            "video_id": video_id,
            "title": result['title'],
            "creator": result['creator'],
            "upload_date": result['upload_date'],
            "duration": result['duration'],
            "views": result['views'],
            "likes": result['likes'],
            "comments": result['comments'],
            "subscribercount": result['subscribercount'],
            "profile_url": result['profile_url'],
            "thumbnail_url": result['thumbnail_url'],
            "hashtags": result['hashtags'],
            "transcript": transcript
        }

        file_path = save_transcript(data)
        print(f"Transcript saved to {file_path}")




    # print(result)
    # print(transcript)
    # print(pinecone_client.get_client())
    # print(pinecone_client.get_index())
    # print(pinecone_client.get_index().describe_index_stats())

    # dim = 1024  # replace with your actual index dimension
    # dummy_vector = [{
    # "id": "smoke_test_0001",
    # "values": [0.01] * dim,
    # "metadata": {
    #     "source": "smoke-test",
    #     "note": "verify upsert works"
    # }
    # }]
    # upsert_response = pinecone_client.upsert_vectors(dummy_vector, namespace="smoke-test")
    # print("Upsert response:", upsert_response)

    # print(pinecone_client.get_index().fetch(ids=["smoke_test_0001"], namespace="smoke-test"))

if __name__ == "__main__":
    main()