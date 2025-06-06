from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ModelResponse(BaseModel):
    """Standardized model response format."""
    content: str
    confidence: float
    processing_time: float
    model_name: str
    metadata: Dict[str, Any] = {}

class BaseAIModel(ABC):
    """Base interface for all AI models."""
    
    def __init__(self, model_name: str, model_version: str):
        self.model_name = model_name
        self.model_version = model_version
        self.is_loaded = False
    
    @abstractmethod
    async def load(self) -> None:
        """Load the model into memory."""
        pass
    
    @abstractmethod
    async def unload(self) -> None:
        """Unload the model from memory."""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    async def batch_generate(self, prompts: List[str], **kwargs) -> List[ModelResponse]:
        """Generate responses for multiple prompts."""
        pass
    
    @abstractmethod
    async def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for the input text."""
        pass
    
    @property
    @abstractmethod
    def model_info(self) -> Dict[str, Any]:
        """Get model information."""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available."""
        pass 