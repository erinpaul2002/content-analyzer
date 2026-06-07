import re
import time
import random
import requests
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig
from config.settings import settings
from adapters.video_source.base import VideoSourceAdapter

class YoutubeVideoSourceAdapter(VideoSourceAdapter):
    def __init__(self):
        self.api_key = settings.youtube_api_key

    def get_video_id(self,url:str)-> str|None:
        sanitized_url = url.strip()
        pattern = r"[a-zA-Z0-9_-]{11}"
        match =re.search(pattern,sanitized_url)
        if match:
            video_id = match.group()
            return video_id
        return None
    
    def get_video_details(self,video_id:str)-> dict|None:
        url="https://www.googleapis.com/youtube/v3/videos"
        params={
            "id":video_id,
            "key":self.api_key,
            "part":"statistics,contentDetails,snippet"
        }
        response = requests.get(url,params=params)
        response.raise_for_status()
        data = response.json()
        channel_id = data['items'][0]['snippet']['channelId']
        channel_details = self.get_channel_details(channel_id)

        stats=data['items'][0]['statistics']
        views=int(stats.get('viewCount',0))
        likes=int(stats.get('likeCount',0))
        comments=int(stats.get('commentCount',0))

        engagement_rate = (likes+comments)/views * 100 if views>0 else 0


        return {"views": views,
                "likes": likes,
                "comments": comments,
                "engagement_rate": round(engagement_rate, 4),
                "duration": data['items'][0]['contentDetails']['duration'],
                "upload_date": data['items'][0]['snippet']['publishedAt'],
                "creator": data['items'][0]['snippet']['channelTitle'],
                "title": data['items'][0]['snippet']['title'],
                "subscribercount": channel_details['subscribers'],
                "profile_url": channel_details['profile_url'],
                "thumbnail_url": data['items'][0]['snippet']['thumbnails']['high']['url'],
                "hashtags": data['items'][0]['snippet']['tags'] if 'tags' in data['items'][0]['snippet'] else "Hashtags not available in this endpoint",  
                }

    def get_channel_details(self, channel_id:str) -> dict|None:
        url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "id": channel_id,
            "key": self.api_key,
            "part": "statistics,snippet"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "subscribers": data['items'][0]['statistics']['subscriberCount'],
            "profile_url": data["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        }

    def _get_proxy_config(self):
        # Connect directly to Tor's SOCKS5 proxy (socks5h = DNS through Tor too)
        proxy_url = "socks5h://127.0.0.1:9050"
        return GenericProxyConfig(http_url=proxy_url, https_url=proxy_url)

    def get_video_transcript(self, video_id: str) -> list | None:
        # Add a random delay to simulate human-like intervals
        time.sleep(random.uniform(2.0, 4.0))

        try:
            proxy_config = self._get_proxy_config()
            
            if proxy_config:
                api = YouTubeTranscriptApi(proxy_config=proxy_config)
                data = api.list(video_id).find_transcript(["en"]).fetch()
            else:
                data = YouTubeTranscriptApi().fetch(video_id)
                
            return [
                {
                    "id": i,
                    "text": snippet.text,
                    "start": snippet.start,
                    "duration": snippet.duration,
                }
                for i, snippet in enumerate(data)
            ]
            
        except Exception as e:
            print(f"Error fetching transcript with youtube_transcript_api: {e}")
            return None