from typing import List
from domain.models import Segment, Chunk
from processors.tokenizer import count_tokens

TARGET_TOKEN_COUNT = 480
TOKEN_OVERLAP = 50

def chunk_segments(
    video_id: str,
    segments: List[Segment],
    target_token_count: int = TARGET_TOKEN_COUNT,
    token_overlap: int = TOKEN_OVERLAP,
) -> List[Chunk]:
    chunks: List[Chunk] = []
    if not segments:
        return chunks
    
    seg_token_counts = [count_tokens(seg.text) for seg in segments]

    start_idx = 0
    chunk_num = 0
    while start_idx < len(segments):
        end_idx = start_idx
        current_token_count = 0
        
        while end_idx < len(segments) and current_token_count + seg_token_counts[end_idx] <= target_token_count:
            current_token_count += seg_token_counts[end_idx]
            end_idx += 1

        chunk_slice = segments[start_idx:end_idx]
        chunk_text = " ".join(seg.text for seg in chunk_slice)
        
        if not chunk_text.strip():
            start_idx = end_idx
            continue

        chunk_start = chunk_slice[0].start
        chunk_end = chunk_slice[-1].end
        chunk_segment_ids = [seg.id for seg in chunk_slice]  

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

        chunk_num += 1
        if end_idx >= len(segments):
            break
        
        overlap_token_count = 0
        overlap_start_idx = end_idx
        while overlap_start_idx > start_idx and overlap_token_count < token_overlap:
            overlap_start_idx -= 1
            overlap_token_count += seg_token_counts[overlap_start_idx]
        
        start_idx = max(overlap_start_idx, start_idx + 1)
        
    return chunks
