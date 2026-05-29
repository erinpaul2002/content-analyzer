from validators.youtube import get_youtube_video_details, extract_youtube_video_id, get_youtube_transcript
from dotenv import load_dotenv
import os
load_dotenv()
YOUTUBE_URL = os.getenv("YOUTUBE_URL")

def main():
    url = YOUTUBE_URL
    video_id = extract_youtube_video_id(url)
    result = get_youtube_video_details(video_id)
    transcript = get_youtube_transcript(video_id)
    print(result)
    print(transcript)

if __name__ == "__main__":
    main()