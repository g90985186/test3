# app/dependencies.py
from functools import lru_cache
from app.ai.models.manager import ModelManager
from app.ai.prompts.manager import PromptManager
from app.ai.services.chat_service import ChatService
from app.ai.models.ollama_model import OllamaModel
import logging

logger = logging.getLogger(__name__)

# Global instances
_model_manager = None
_prompt_manager = None
_chat_service = None

@lru_cache()
def get_model_manager() -> ModelManager:
    """Get or create model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
        
        # Register default models
        try:
            # Register Ollama models
            ollama_chat = OllamaModel("llama3.1", "8b")
            ollama_analysis = OllamaModel("gemma2", "9b")
            ollama_code = OllamaModel("codellama", "7b")
            
            # Note: In production, you'd want to handle these async operations properly
            # For now, we'll register them and they'll be loaded on first use
            _model_manager.models["llama3.1:8b"] = ollama_chat
            _model_manager.models["gemma2:9b"] = ollama_analysis
            _model_manager.models["codellama:7b"] = ollama_code
            
            logger.info("Model manager initialized with default models")
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
    
    return _model_manager

@lru_cache()
def get_prompt_manager() -> PromptManager:
    """Get or create prompt manager instance."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
        logger.info("Prompt manager initialized")
    return _prompt_manager

@lru_cache()
def get_chat_service() -> ChatService:
    """Get or create chat service instance."""
    global _chat_service
    if _chat_service is None:
        model_manager = get_model_manager()
        prompt_manager = get_prompt_manager()
        _chat_service = ChatService(model_manager, prompt_manager)
        logger.info("Chat service initialized")
    return _chat_service

# Health check function
def check_ai_services() -> dict:
    """Check the health of AI services."""
    try:
        model_manager = get_model_manager()
        prompt_manager = get_prompt_manager()
        chat_service = get_chat_service()
        
        return {
            "model_manager": "healthy" if model_manager else "unavailable",
            "prompt_manager": "healthy" if prompt_manager else "unavailable", 
            "chat_service": "healthy" if chat_service else "unavailable",
            "models_registered": len(model_manager.models) if model_manager else 0
        }
    except Exception as e:
        logger.error(f"Error checking AI services: {e}")
        return {
            "model_manager": "error",
            "prompt_manager": "error",
            "chat_service": "error",
            "error": str(e)
        }
