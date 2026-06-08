from sys import prefix
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import ingest,chat,sessions
from config.settings import settings


app=FastAPI(
    title="Video Analyze API",
    description="API for video analysis and comparison"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api",tags=["ingestion"])
app.include_router(chat.router,prefix="/api/chat",tags=["chat"])
app.include_router(sessions.router,prefix="/api/sessions",tags=["sessions"])
@app.get("/health",tags=["system"])
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app",
    host="0.0.0.0",
    port=8000)