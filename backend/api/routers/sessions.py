import json
import os
from pathlib import Path
from fastapi import APIRouter,HTTPException
#from adapters.storage.json_storage import JsonStorageAdapter
from adapters.storage.convex_storage import ConvexStorageAdapter
from adapters.vector_db.pinecone_adapter import PineconeVectorDBAdapter
from pydantic import BaseModel

router=APIRouter()
#storage_adapter=JsonStorageAdapter()
storage_adapter=ConvexStorageAdapter()

@router.get("")
def list_sessions():
    """
    sessions_dir=Path("data/sessions")
    logs_dir=Path("data/logs")
    if not sessions_dir.exists():
        return []
    
    sessions_list=[]
    for file_path in sessions_dir.glob("session_*.json"):
        try:
            with open(file_path,"r",encoding="utf-8") as f:
                manifest=json.load(f)
            session_id=manifest.get("session_id")
            if not session_id:
                continue
            log_path=logs_dir / f"session_{session_id}.json"
            title="New Comparison"
            date="Unknown"
            if log_path.exists():
                with open(log_path,"r",encoding="utf-8") as f:
                    log_data=json.load(f)
                    turns=log_data.get("turns",[])
                    if turns:
                        title=turns[0].get("question","New Comparison")
                        timestamp=turns[0].get("timestamp","")
                        if timestamp:
                            date=timestamp.split("T")[0]
            sessions_list.append({
                "id":session_id,
                "title":title,
                "date":date,
                "timestamp":os.path.getmtime(file_path)
            })
        except Exception as e:
            print(f"Error loading session {file_path}:{e}")
    sessions_list.sort(key=lambda x: x["timestamp"],reverse=True)
    return sessions_list
    """
    sessions_list = storage_adapter.client.query("actions:listSessions")
    if not sessions_list:
        return []
        
    formatted_sessions = []
    for s in sessions_list:
        session_id = s.get("session_id")
        if not session_id:
            continue
            
        # Fetch log to infer title from the first question (just like the old JSON logic)
        log_data = storage_adapter.client.query("actions:getLog", {"session_id": session_id})
        title = "New Comparison"
        date = "Unknown"
        
        if log_data and log_data.get("turns"):
            first_turn = log_data["turns"][0]
            title = first_turn.get("question", "New Comparison")
            timestamp_str = first_turn.get("timestamp", "")
            if timestamp_str:
                date = timestamp_str.split("T")[0]
                
        formatted_sessions.append({
            "id": session_id,
            "title": title,
            "date": date,
            "timestamp": s.get("timestamp", 0)
        })
        
    # Sort descending by timestamp
    formatted_sessions.sort(key=lambda x: x["timestamp"], reverse=True)
    return formatted_sessions


                

@router.get("/{session_id}")
def get_session(session_id:str):
    """
    session_path=Path("data/sessions")/f"session_{session_id}.json"
    if not session_path.exists():
        raise HTTPException(status_code=404,detail="Session not found")
    
    with open(session_path,"r",encoding="utf-8") as f:
        manifest=json.load(f)
    videos={}
    labels=manifest.get("labels",{})
    for video_id,label in labels.items():
        videos[label]=storage_adapter.load(video_id)
    log_path=Path("data/logs")/f"session_{session_id}.json"
    history=[]
    if log_path.exists():
        with open(log_path,"r",encoding="utf-8") as f:
            log_data=json.load(f)
            history=log_data.get("turns",[])
    return {
        "session_id":session_id,
        "videos":videos,
        "history":history
    }
    """
    session = storage_adapter.client.query("actions:getSession", {"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    videos = {}
    labels = session.get("labels", {})
    for video_id, label in labels.items():
        videos[label] = storage_adapter.load(video_id)
        
    history = []
    log_data = storage_adapter.client.query("actions:getLog", {"session_id": session_id})
    if log_data and log_data.get("turns"):
        history = log_data["turns"]
        
    return {
        "session_id": session_id,
        "videos": videos,
        "history": history
    }

@router.delete("/{session_id}")
def delete_session(session_id: str):
    session = storage_adapter.client.query("actions:getSession", {"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        pinecone_adapter = PineconeVectorDBAdapter()
        pinecone_adapter.delete_namespace(session_id)
    except Exception as e:
        print(f"Failed to delete Pinecone namespace for session {session_id}: {e}")
        # Proceed to delete from Convex even if Pinecone fails
        
    try:
        storage_adapter.client.mutation("actions:deleteSession", {"session_id": session_id})
    except Exception as e:
        print(f"Failed to delete session {session_id} from Convex: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session from Convex database")

    return {"status": "success", "message": f"Session {session_id} deleted."}
        