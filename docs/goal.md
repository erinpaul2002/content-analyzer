# Project Goal

## End goal

Build a production-ready, full-stack RAG chatbot for social media video analysis that takes **two supported social media video URLs** as input, extracts their transcripts and metadata, embeds the transcript content into a vector database, and lets a creator compare both videos through a streaming conversational interface.

## What the project must achieve

The final system should:

1. Accept two real video URLs as input, from YouTube, Instagram Reels, or the same platform for both videos.
2. Retrieve the transcript and metadata for both videos, including:
   - views
   - likes
   - comments
   - creator name
   - follower count
   - hashtags
   - upload date
   - duration
3. Compute engagement rate for each video using:
   - $(likes + comments) / views \times 100$
4. Chunk the transcripts, generate embeddings, and store them in a vector database with every chunk tagged by `video_id` (`A` or `B`).
5. Provide a LangGraph-powered RAG chat experience where users can ask comparative questions such as:
   - why one video performed better than the other
   - engagement rate comparison
   - hook comparison in the first 5 seconds
   - creator and follower-count lookup
   - improvement suggestions for Video B based on Video A
6. Stream answers in real time.
7. Cite the source of every answer with the originating video and chunk reference.
8. Preserve memory across chat turns so the conversation stays context-aware.
9. Display the experience in a fast, side-by-side frontend with:
   - two video cards
   - extracted metadata
   - transcript-backed analysis
   - chat panel

## Success definition

This project is successful when a reviewer can:

- paste in two valid video URLs,
- see both videos analyzed automatically,
- ask comparative questions in chat,
- receive streamed, cited, grounded answers,
- and trust that the app is built with a scalable architecture that can support creators at volume.

## Business target

The demo should prove that this approach is a practical, low-cost, high-quality way to analyze creator content at scale for roughly **1,000 creators per day**. The project should also explain any trade-offs clearly and identify a better alternative if a chosen component is not the most cost-efficient option.

## Non-negotiable constraints

- The output must be dynamic, not hard-coded.
- The system must work end-to-end from URL input to answer generation.
- The solution must use LangChain or LangGraph, embeddings, and a vector database.
- The interface must feel responsive and reliable enough for a live demo.
- The implementation should be understandable, defensible, and easy to expand.

## In one sentence

Create a scalable, streaming RAG chatbot that compares two social media videos using transcripts and metadata, then explains performance differences with cited, memory-aware answers through a clean full-stack app.
