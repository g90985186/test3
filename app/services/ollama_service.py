import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.base_url = settings.ollama_url
        self.models = {
            "general": "llama3.1:8b",
            "technical": "gemma2:9b", 
            "code": "codellama:7b"
        }
    
    async def health_check(self) -> bool:
        """Check if Ollama service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        available_models = [model["name"] for model in data.get("models", [])]
                        logger.info(f"Ollama service healthy. Available models: {available_models}")
                        return True
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
        return False
    
    async def generate_response(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Generate response from Ollama model"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.1),
                "top_p": kwargs.get("top_p", 0.9),
                "num_ctx": kwargs.get("num_ctx", 4096),
                "num_predict": kwargs.get("num_predict", 2048)
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        # FIX: Handle potential JSON parsing errors from Ollama streaming responses
                        try:
                        result = await response.json()
                        except json.JSONDecodeError as json_error:
                            logger.error(f"JSON decode error in Ollama service: {json_error}")
                            # Try to parse as text and extract JSON
                            response_text = await response.text()
                            logger.debug(f"Raw Ollama response: {response_text}")
                            
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
                                    "response": "Error: Could not parse Ollama response",
                                    "done": True
                                }
                        
                        return {
                            "success": True,
                            "response": result.get("response", ""),
                            "model": model,
                            "total_duration": result.get("total_duration", 0),
                            "load_duration": result.get("load_duration", 0)
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama API error {response.status}: {error_text}")
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        
        except asyncio.TimeoutError:
            logger.error("Ollama request timeout")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_cve(self, cve_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CVE using appropriate model"""
        from app.ai.prompts.cve_analysis import CVE_ANALYSIS_PROMPT
        
        prompt = CVE_ANALYSIS_PROMPT.format(
            cve_id=cve_data.get("cve_id", "Unknown"),
            description=cve_data.get("description", "No description available"),
            cvss_score=cve_data.get("cvss_v3_score", "Unknown"),
            cvss_vector=cve_data.get("cvss_v3_vector", "Unknown"),
            cwe_ids=cve_data.get("cwe_ids", [])
        )
        
        response = await self.generate_response(prompt, self.models["general"])
        
        if response["success"]:
            try:
                # Try to parse JSON response
                analysis_result = json.loads(response["response"])
                return {
                    "success": True,
                    "analysis": analysis_result,
                    "model_used": response["model"],
                    "duration": response["total_duration"]
                }
            except json.JSONDecodeError:
                # If not JSON, return raw response
                return {
                    "success": True,
                    "analysis": {"raw_response": response["response"]},
                    "model_used": response["model"],
                    "duration": response["total_duration"]
                }
        
        return response
