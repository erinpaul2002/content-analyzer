# Content Analyzer

Content Analyzer: RAG based video transcript analysis tool that lets you compare two videos, chat with the content, and pull exact citations. 

## Tech Stack

**Frontend**
- Next.js 16 (React 19)
- Tailwind CSS v4
- Convex (real-time state & serverless database)

**Backend API & AI Pipeline**
- Python / FastAPI
- LangGraph (Agent/RAG orchestration)
- Pinecone (Vector Database)
- Pinecone Serverless Inference (`multilingual-e5-large` 1024-dim embeddings)
- Groq / Google GenAI / OpenRouter (for LLM reasoning)
- Cloudflare Workers (Custom transcript proxy)

## Engineering Trade-offs

### Why Pinecone & E5?
Honestly, I went with Pinecone because out of all the options, I had already done a project with it earlier and it has a really good free tier. For embeddings, I chose Pinecone-hosted `multilingual-e5-large` because E5 is just solid for conversational transcripts, which are usually a grammatically incorrect mess. More importantly, using Pinecone to run the inference means I don't have to stuff a giant transformer model into the FastAPI container or spin up a separate microservice. Pinecone handles storage and embeddings in one shot. It keeps the backend super light, and if I ever outgrow it, the adapter pattern lets me rip it out easily.

### The Transcript API Nightmare
Getting transcripts reliably was brutal. The YouTube API doesn't give you transcripts out of the box, and scraping them directly from my backend host (Render) led to immediate IP bans and connection timeouts. I spent a lot of time doing trial and error with Tor routing (`socks5h`) and random proxies, but it was incredibly flaky. 
The fix? I wrote a custom Cloudflare Worker that sits at the edge. This was actually my first time using Cloudflare Workers, and I learned it specifically to solve this problem for the project. It fetches the public watch page, extracts the `ytInitialPlayerResponse` payload, parses the caption tracks, and returns clean JSON. Bypassing residential proxies entirely and offloading it to Cloudflare's massive IP pool stabilized the whole ingestion pipeline.

### Why 480 Tokens for chunk size?
Chunking is set to 480 tokens with a 50-token overlap. Spoken video transcripts don't have clean sentence boundaries, so 480 tokens (around 350-400 words) felt like the right balance. It's big enough to grab a full thought, but small enough that the vector doesn't get muddied by three different topics at once. It also means I can stuff 5-10 good chunks into the LLM prompt without hitting context limits or tanking generation speed. The 50-token overlap is just there so I don't accidentally slice a crucial sentence in half.

### What breaks at 10,000 users?
If this gets hit with 10k users tomorrow, it will still fall over here:
- **Pinecone Namespaces:** The current setup creates a new Pinecone namespace for every single comparison session to keep data isolated. At 10k concurrent sessions, spinning up and tearing down that many namespaces will definitely hit Pinecone's control-plane limits. I'd need to switch to a single namespace and just filter by `session_id`.
- **Cloudflare Worker / Ingestion limits:** Even though the Cloudflare Worker fixed my IP bans, synchronously hitting it 10,000 times at once will blow past the free tier and probably trigger YouTube's rate limits on Cloudflare's IPs anyway. I'd have to decouple ingestion into an async queue (like Convex actions or Redis) to throttle the requests.