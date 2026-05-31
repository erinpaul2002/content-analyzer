from typing import List
from functools import lru_cache
from transformers import AutoTokenizer
from utils.text_utils import clean_text
from config.settings import settings
from domain.models import Segment,Chunk

TARGET_TOKEN_COUNT=480
TOKEN_OVERLAP=50

MODEL_NAME=settings.tokenizer_model

@lru_cache(maxsize=1)
def get_tokenizer():
    return AutoTokenizer.from_pretrained(MODEL_NAME)

def count_tokens(text:str)->int:
    cleaned_text=text.strip()
    tokenizer=get_tokenizer()
    tokens=tokenizer.encode(cleaned_text, add_special_tokens=False)
    return len(tokens)

def normalize_segments(raw_transcript: dict) ->List[Segment]:

    segments: List[Segment] = []
    
    for key in sorted(raw_transcript.keys(), key=lambda x: int(x)):
        item = raw_transcript[key]
        text = str(clean_text(item.get("text", "")))
        if not text:
            continue
        start = float(item.get("start", 0))
        duration = float(item.get("duration", 0))
        end = start + duration

        segments.append(Segment(
            id=int(key),
            text=text,
            start=start,
            duration=duration,
            end=end
        ))

    return segments

def chunk_segments(
    video_id:str,
    segments:List[Segment],
    target_token_count:int=TARGET_TOKEN_COUNT,
    token_overlap:int=TOKEN_OVERLAP,
) -> List[Chunk]:

    chunks:List[Chunk] = []
    if not segments:
        return chunks
    
    seg_token_counts = [count_tokens(seg.text) for seg in segments]

    start_idx=0
    chunk_num=0
    while start_idx < len(segments):
        end_idx = start_idx
        current_token_count = 0
        while end_idx < len(segments) and current_token_count + seg_token_counts[end_idx] <= target_token_count:
            current_token_count += seg_token_counts[end_idx]
            end_idx += 1

        chunk_slice = segments[start_idx:end_idx]
        chunk_text=" ".join(seg.text for seg in chunk_slice)
        if not chunk_text.strip():
            start_idx = end_idx
            continue

        chunk_start=chunk_slice[0].start
        chunk_end=chunk_slice[-1].end
        chunk_segment_ids=[seg.id for seg in chunk_slice]  

        embed_text = f"passage: {chunk_text}"
        chunk_token_count = count_tokens(embed_text)

        chunks.append(Chunk(
            chunk_id=f"{video_id}_chunk_{chunk_num}",
            video_id=video_id,
            text=chunk_text,
            start=chunk_start,
            end=chunk_end,
            segment_ids=chunk_segment_ids,
            token_count=chunk_token_count
        ))

        chunk_num+=1
        if end_idx >= len(segments):
            break
        
        overlap_token_count=0
        overlap_start_idx=end_idx
        while overlap_start_idx > start_idx and overlap_token_count < token_overlap:
            overlap_start_idx -= 1
            overlap_token_count += seg_token_counts[overlap_start_idx]
        
        start_idx = max(overlap_start_idx, start_idx + 1)
    return chunks

def build_chunks_from_transcript(video_id: str, raw_transcript: dict) -> list[Chunk]:
    segments = normalize_segments(raw_transcript)
    return chunk_segments(video_id=video_id, segments=segments)