import re
import requests
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def extract_youtube_video_id(url: str) -> str|None:
    sanitized_url = url.strip()
    pattern = r"[a-zA-Z0-9_-]{11}"
    match =re.search(pattern,sanitized_url)
    if match:
        video_id = match.group()
        return video_id
    else:
        return None

def get_channel_details(channel_id:str) -> dict|None:
    url="https://www.googleapis.com/youtube/v3/channels"
    params={
        "id":channel_id,
        "key":YOUTUBE_API_KEY,
        "part":"statistics,snippet"
    }
    response = requests.get(url,params=params)
    response.raise_for_status()
    data = response.json()
    return {"subscribers": data['items'][0]['statistics']['subscriberCount'],
            "profile_url": data['items'][0]['snippet']['thumbnails']['high']['url']
            }

def get_youtube_video_details(video_id:str) -> dict|None:
    url="https://www.googleapis.com/youtube/v3/videos"
    params={
        "id":video_id,
        "key":YOUTUBE_API_KEY,
        "part":"statistics,contentDetails,snippet"
    }
    response = requests.get(url,params=params)
    response.raise_for_status()
    data = response.json()
    channel_id = data['items'][0]['snippet']['channelId']
    channel_details = get_channel_details(channel_id)
    return {"views": data['items'][0]['statistics']['viewCount'],
            "likes": data['items'][0]['statistics']['likeCount'],
            "comments": data['items'][0]['statistics']['commentCount'],
            "duration": data['items'][0]['contentDetails']['duration'],
            "upload_date": data['items'][0]['snippet']['publishedAt'],
            "creator": data['items'][0]['snippet']['channelTitle'],
            "subscribercount": channel_details['subscribers'],
            "profile_url": channel_details['profile_url'],
            "thumbnail_url": data['items'][0]['snippet']['thumbnails']['high']['url'],
            "hashtags": data['items'][0]['snippet']['tags'] if 'tags' in data['items'][0]['snippet'] else "Hashtags not available in this endpoint",  
            }

def get_youtube_transcript(video_id:str) -> dict|None:
    try:
        ytt_api = YouTubeTranscriptApi()
        data = ytt_api.fetch(video_id)
        transcript = {
            i: {
                "text": snippet.text,
                "start": snippet.start,
                "duration": snippet.duration,
            }
            for i, snippet in enumerate(data)
        }
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None
    