from sys import prefix
import uvicorn
from fastapi import FastAPI
from api.routers import ingest,chat
from config.settings import settings


app=FastAPI(
    title="Video Analyze API",
    description="API for video analysis and comparison"
)

app.include_router(ingest.router, prefix="/api",tags=["ingestion"])
app.include_router(chat.router,prefix="/api/chat",tags=["chat"])

@app.get("/health",tags=["system"])
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app",
    host="0.0.0.0",
    port=8000,
    reload=True)