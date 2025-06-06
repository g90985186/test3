# app/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import logging
from app.database import get_db
from app.dependencies import get_chat_service
from app.ai.services.chat_service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatMessage(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    context_cve_ids: Optional[List[str]] = Field(None, description="CVE IDs for context")
    conversation_type: str = Field("general", description="Type: general, cve_specific, analysis, help")

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime
    context_used: List[str] = []
    suggestions: List[str] = []
    metadata: Dict[str, Any] = {}

@router.post("/", response_model=ChatResponse)
async def send_chat_message(
    message: ChatMessage,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a chat message and get AI response"""
    try:
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        # Get response from chat service
        response_data = await chat_service.get_response(
            user_question=message.message,
            session_id=session_id,
            context_cve_ids=message.context_cve_ids,
            conversation_type=message.conversation_type
        )
        
        # Convert to response model
        response = ChatResponse(
            response=response_data["response"],
            session_id=response_data["session_id"],
            timestamp=datetime.fromisoformat(response_data["timestamp"]),
            context_used=response_data.get("context_used", []),
            suggestions=response_data.get("suggestions", []),
            metadata=response_data.get("metadata", {})
        )
        
        logger.info(f"Chat message processed for session {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        # Return a fallback response instead of raising an exception
        return ChatResponse(
            response="I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
            session_id=message.session_id or str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            context_used=[],
            suggestions=["Try a simpler question", "Check system status", "Refresh the page"],
            metadata={"error": str(e)}
        )

@router.get("/sessions")
async def get_chat_sessions(
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get chat system statistics"""
    try:
        stats = chat_service.get_chat_stats()
        return {
            "sessions": [],  # We don't expose individual sessions for privacy
            "total_sessions": stats["total_sessions"],
            "total_messages": stats["total_messages"],
            "average_messages_per_session": stats["average_messages_per_session"]
        }
    except Exception as e:
        logger.error(f"Error getting chat sessions: {str(e)}")
        return {
            "sessions": [],
            "total_sessions": 0,
            "total_messages": 0,
            "average_messages_per_session": 0,
            "error": str(e)
        }

@router.get("/history")
async def get_chat_history(
    session_id: Optional[str] = None, 
    limit: int = 50,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get chat history for a session"""
    if not session_id:
        return {
            "messages": [],
            "total": 0,
            "session_id": None,
            "note": "Session ID required to retrieve history"
        }
    
    try:
        # Load history for the session
        history = chat_service._load_chat_history(session_id)
        
        # Limit the results
        limited_history = history[-limit:] if len(history) > limit else history
        
        return {
            "messages": limited_history,
            "total": len(limited_history),
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        return {
            "messages": [],
            "total": 0,
            "session_id": session_id,
            "error": str(e)
        }

@router.get("/stats")
async def get_chat_stats(
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get chat system statistics"""
    try:
        return chat_service.get_chat_stats()
    except Exception as e:
        logger.error(f"Error getting chat stats: {str(e)}")
        return {
            "total_sessions": 0,
            "total_messages": 0,
            "average_messages_per_session": 0,
            "error": str(e)
        }

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Delete a chat session and its history"""
    try:
        success = chat_service.clear_history(session_id)
        if success:
            return {"message": "Session deleted successfully"}
        else:
            return {"message": "Session not found or could not be deleted"}
    except Exception as e:
        logger.error(f"Error deleting chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
async def clear_chat_history(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Clear chat history for a specific session"""
    try:
        success = chat_service.clear_history(session_id)
        return {
            "success": success,
            "message": "Chat history cleared" if success else "Could not clear history"
        }
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

# Health check endpoint for chat service
@router.get("/health")
async def chat_health_check(
    chat_service: ChatService = Depends(get_chat_service)
):
    """Check chat service health"""
    try:
        # Test if we can get stats (basic functionality test)
        stats = chat_service.get_chat_stats()
        
        return {
            "status": "healthy",
            "service": "chat",
            "timestamp": datetime.utcnow().isoformat(),
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Chat health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "chat", 
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
