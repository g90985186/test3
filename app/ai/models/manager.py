from typing import Dict, List, Optional, Type, Any
import asyncio
import logging
from datetime import datetime
from .base import BaseAIModel, ModelResponse

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages multiple AI models and their lifecycle."""
    
    def __init__(self):
        self.models: Dict[str, BaseAIModel] = {}
        self.model_usage: Dict[str, Dict[str, int]] = {}
        self.model_errors: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()
    
    async def register_model(self, model: BaseAIModel) -> None:
        """Register a new model."""
        async with self._lock:
            if model.model_name in self.models:
                raise ValueError(f"Model {model.model_name} already registered")
            
            self.models[model.model_name] = model
            self.model_usage[model.model_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "last_used": None
            }
            self.model_errors[model.model_name] = []
            
            logger.info(f"Registered model: {model.model_name} v{model.model_version}")
    
    async def unregister_model(self, model_name: str) -> None:
        """Unregister a model."""
        async with self._lock:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[model_name]
            await model.unload()
            del self.models[model_name]
            del self.model_usage[model_name]
            del self.model_errors[model_name]
            
            logger.info(f"Unregistered model: {model_name}")
    
    async def get_model(self, model_name: str) -> Optional[BaseAIModel]:
        """Get a model by name."""
        return self.models.get(model_name)
    
    async def generate_response(
        self,
        model_name: str,
        prompt: str,
        **kwargs
    ) -> ModelResponse:
        """Generate a response using the specified model."""
        model = await self.get_model(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not found")
        
        try:
            start_time = datetime.now()
            response = await model.generate(prompt, **kwargs)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update usage statistics
            self.model_usage[model_name]["total_requests"] += 1
            self.model_usage[model_name]["successful_requests"] += 1
            self.model_usage[model_name]["last_used"] = datetime.now()
            
            # Add processing time to response
            response.processing_time = processing_time
            
            return response
            
        except Exception as e:
            # Update error statistics
            self.model_usage[model_name]["total_requests"] += 1
            self.model_usage[model_name]["failed_requests"] += 1
            self.model_errors[model_name].append({
                "timestamp": datetime.now(),
                "error": str(e),
                "prompt": prompt
            })
            
            logger.error(f"Error generating response with model {model_name}: {str(e)}")
            raise
    
    async def batch_generate(
        self,
        model_name: str,
        prompts: List[str],
        **kwargs
    ) -> List[ModelResponse]:
        """Generate responses for multiple prompts."""
        model = await self.get_model(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not found")
        
        try:
            start_time = datetime.now()
            responses = await model.batch_generate(prompts, **kwargs)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update usage statistics
            self.model_usage[model_name]["total_requests"] += len(prompts)
            self.model_usage[model_name]["successful_requests"] += len(prompts)
            self.model_usage[model_name]["last_used"] = datetime.now()
            
            # Add processing time to responses
            for response in responses:
                response.processing_time = processing_time / len(prompts)
            
            return responses
            
        except Exception as e:
            # Update error statistics
            self.model_usage[model_name]["total_requests"] += len(prompts)
            self.model_usage[model_name]["failed_requests"] += len(prompts)
            self.model_errors[model_name].append({
                "timestamp": datetime.now(),
                "error": str(e),
                "prompts": prompts
            })
            
            logger.error(f"Error batch generating with model {model_name}: {str(e)}")
            raise
    
    def get_model_stats(self, model_name: str) -> Dict[str, Any]:
        """Get statistics for a specific model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        usage = self.model_usage[model_name]
        model = self.models[model_name]
        
        return {
            "model_name": model_name,
            "model_version": model.model_version,
            "is_loaded": model.is_loaded,
            "total_requests": usage["total_requests"],
            "successful_requests": usage["successful_requests"],
            "failed_requests": usage["failed_requests"],
            "success_rate": (
                usage["successful_requests"] / usage["total_requests"]
                if usage["total_requests"] > 0 else 0
            ),
            "last_used": usage["last_used"],
            "recent_errors": self.model_errors[model_name][-5:]  # Last 5 errors
        }
    
    def get_all_model_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all models."""
        return {
            model_name: self.get_model_stats(model_name)
            for model_name in self.models
        } 