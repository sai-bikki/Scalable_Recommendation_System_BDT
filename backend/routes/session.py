from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.user import User
import logging

router = APIRouter(prefix="/session", tags=["session"])
logger = logging.getLogger(__name__)

class SessionStartRequest(BaseModel):
    user_id: str
    session_id: str

@router.post("/start")
async def start_session(req: SessionStartRequest):
    """Create or update user session in MongoDB"""
    if not req.user_id or not req.session_id:
        raise HTTPException(status_code=400, detail="user_id and session_id are required")
    
    try:
        user = User.find_one_and_update(req.user_id)
        visit_count = user.get('visit_count', 1)
        
        logger.info(f"[session/start] user={req.user_id} session={req.session_id} visits={visit_count}")
        return {
            "status": "ok",
            "user_id": req.user_id,
            "session_id": req.session_id,
            "visit_count": visit_count
        }
    except Exception as e:
        logger.error(f"[session/start] error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start session")
