from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from ...ai.services.chat_service import ChatService
from ...dependencies import get_chat_service
import uuid

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    cve_id: Optional[str] = None
    poc_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get AI response for a chat message."""
    try:
        # Generate a session ID if not provided
        session_id = str(uuid.uuid4())
        
        response = await chat_service.get_response(
            user_question=request.question,
            session_id=session_id,
            cve_id=request.cve_id,
            poc_id=request.poc_id
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/{session_id}")
async def clear_chat_history(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Clear chat history for a session."""
    try:
        chat_service.clear_history(session_id)
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 