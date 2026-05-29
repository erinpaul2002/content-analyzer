# Tech Stack Decision

This document captures the current stack choice for the Content Analyzer project.

## Finalized decisions

- **Frontend:** Next.js
- **Backend:** FastAPI (Python)
- **Orchestration:** LangGraph
- **Embeddings:** E5
- **Vector DB:** Pinecone

## Still to decide

- **LLM:** not decided yet
- **Transcript source:** not decided yet

## Notes

- Next.js gives us a fast, modern frontend with good streaming support for the chat UI.
- FastAPI keeps the backend Python-based, which is a good fit for AI and transcript-related work.
- LangGraph is the orchestration layer for multi-step RAG flows and memory.
- E5 is the embedding model choice because it is a strong open-source option for retrieval.
- Pinecone is the vector database choice for now, assuming the free tier is sufficient for the demo.

## Open questions

- Which LLM should power the final responses?
- Should transcript extraction use YouTube transcript APIs, `yt-dlp`, Whisper, or a hybrid approach?

## Next step

Once the LLM and transcript source are chosen, this stack can be turned into an implementation plan.
