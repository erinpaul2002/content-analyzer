import re
from typing import List
from domain.models import Segment

def clean_text(text:str) -> str:
    text=re.sub(r"^\s*(>>|--)+\s*","",text)
    return re.sub(r"\s+"," ",text).strip()

def normalize_segments(raw_transcript_list:list)->List[Segment]:
    segments : List[Segment] = []
    for item in raw_transcript_list:
        text=clean_text(item.get("text"," "))
        if not text:
            continue
        start=float(item.get("start",0))
        duration=float(item.get("duration",0))
        segments.append(
            Segment(
                id=int(item.get("id",0)),
                text=text,
                start=start,
                duration=duration,
                end=start+duration
            )
        )
    return segments