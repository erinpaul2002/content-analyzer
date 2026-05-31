from validators.youtube import get_youtube_video_details, extract_youtube_video_id, get_youtube_transcript
from dotenv import load_dotenv
from utils.pinecone_client import PineconeHandler
from utils.transcripts import save_transcript, load_transcripts, transcript_exists
from config.settings import settings
from adapters.video_source.youtube import YoutubeVideoSourceAdapter
from adapters.storage.json_storage import JsonStorageAdapter



def main():
    src_adapter = YoutubeVideoSourceAdapter()
    storage_adapter = JsonStorageAdapter()
    pinecone_client = PineconeHandler()
    url = settings.youtube_url
    video_id =src_adapter.get_video_id(url)
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {url}")

    if storage_adapter.exists(video_id):
        print(f"Transcript for video ID {video_id} already exists. Loading from file.")
        existing_data = storage_adapter.load(video_id)
        print(existing_data)
        return
    
    video_details = src_adapter.get_video_details(video_id)
    video_transcript = src_adapter.get_video_transcript(video_id)
    if not video_transcript:
        print(f"No transcript available for video ID {video_id}")
        return
    payload = {
        "video_id": video_id,
        "metadata": video_details,
        "transcript": video_transcript
    }

    data_path = storage_adapter.save(video_id, payload)
    print(f"Transcript saved to {data_path}")

    
if __name__ == "__main__":
    main()