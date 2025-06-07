import httpx
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import BaseAIModel, ModelResponse

logger = logging.getLogger(__name__)

class OllamaModel(BaseAIModel):
    """Implementation of Ollama models."""
    
    def __init__(
        self,
        model_name: str,
        model_version: str,
        base_url: str = "http://localhost:11434",
        timeout: int = 120  # Increased timeout for code generation
    ):
        super().__init__(model_name, model_version)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout
        )
    
    async def load(self) -> None:
        """Load the model into memory."""
        try:
            response = await self.client.post(
                "/api/pull",
                json={"name": f"{self.model_name}:{self.model_version}"}
            )
            response.raise_for_status()
            self.is_loaded = True
            logger.info(f"Loaded model: {self.model_name} v{self.model_version}")
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
            raise
    
    async def unload(self) -> None:
        """Unload the model from memory."""
        try:
            await self.client.aclose()
            self.is_loaded = False
            logger.info(f"Unloaded model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error unloading model {self.model_name}: {str(e)}")
            raise
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> ModelResponse:
        """Generate a response from the model."""
        if not self.is_loaded:
            await self.load()
        
        try:
            start_time = datetime.now()
            response = await self.client.post(
                "/api/generate",
                json={
                    "model": f"{self.model_name}:{self.model_version}",
                    "prompt": prompt,
                    "stream": False,  # Explicitly disable streaming
                    "temperature": temperature,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    },
                    **kwargs
                }
            )
            response.raise_for_status()
            
            # FIX: Handle potential streaming or malformed JSON response
            try:
            result = response.json()
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON decode error: {json_error}")
                # Try to parse as text and extract JSON
                response_text = response.text
                logger.debug(f"Raw response text: {response_text}")
                
                # If response contains multiple JSON objects, take the last complete one
                lines = response_text.strip().split('\n')
                for line in reversed(lines):
                    if line.strip():
                        try:
                            result = json.loads(line.strip())
                            break
                        except json.JSONDecodeError:
                            continue
                else:
                    # If no valid JSON found, create a fallback response
                    result = {
                        "response": "Error: Could not parse AI response",
                        "done": True
                    }
            
            return ModelResponse(
                content=result.get("response", "No response generated"),
                confidence=result.get("confidence", 1.0),
                processing_time=(datetime.now() - start_time).total_seconds(),
                model_name=self.model_name,
                metadata={
                    "total_tokens": result.get("eval_count", 0),
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "done": result.get("done", False)
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating response with model {self.model_name}:{self.model_version}: {str(e)}")
            logger.error(f"Full model identifier: {self.model_name}:{self.model_version}")
            logger.error(f"Request details - Temperature: {temperature}, Max tokens: {max_tokens}")
            raise
    
    async def batch_generate(
        self,
        prompts: List[str],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> List[ModelResponse]:
        """Generate responses for multiple prompts."""
        if not self.is_loaded:
            await self.load()
        
        try:
            start_time = datetime.now()
            responses = []
            
            for prompt in prompts:
                response = await self.generate(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                responses.append(response)
            
            return responses
            
        except Exception as e:
            logger.error(f"Error batch generating with model {self.model_name}: {str(e)}")
            raise
    
    async def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for the input text."""
        if not self.is_loaded:
            await self.load()
        
        try:
            response = await self.client.post(
                "/api/embeddings",
                json={
                    "model": f"{self.model_name}:{self.model_version}",
                    "prompt": text
                }
            )
            response.raise_for_status()
            result = response.json()
            
            return result["embedding"]
            
        except Exception as e:
            logger.error(f"Error getting embeddings with model {self.model_name}: {str(e)}")
            raise
    
    @property
    def model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "name": self.model_name,
            "version": self.model_version,
            "base_url": self.base_url,
            "is_loaded": self.is_loaded,
            "timeout": self.timeout
        }
    
    @property
    def is_available(self) -> bool:
        """Check if the model is available."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False 