from requests import session
from config.settings import settings
from domain.pipelines import process_youtube_video
from adapters.vector_db.pinecone_adapter import PineconeVectorDBAdapter

def main():
    url = settings.youtube_url
    session_id="test-session-001"
    records=process_youtube_video(url,session_id)
    db_adapter=PineconeVectorDBAdapter()
    response=db_adapter.upsert(records=records,namespace=session_id)
    print(f"Records Upserted for Session ID: {session_id}")
    print(response)
    
if __name__ == "__main__":
    main()