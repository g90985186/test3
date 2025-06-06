import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class LocalAIService:
    """Comprehensive Local AI Service using Ollama models for CVE Analysis Platform"""
    
    def __init__(self):
        self.base_url = 'http://localhost:11434'  # Default Ollama URL
        self.available_models = {}
        self.model_assignments = {
            "chat": "llama3.1:8b",           # General conversation and help
            "cve_analysis": "gemma2:9b",     # Technical CVE analysis
            "code_analysis": "codellama:7b", # Code vulnerability analysis
            "threat_intel": "llama3.1:8b",   # Threat intelligence and OSINT
            "report_generation": "gemma2:9b" # Report writing and summarization
        }
        self.prompt_templates = self._initialize_prompts()
        self.response_cache = {}  # Simple in-memory cache
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the AI service and verify model availability"""
        if self.is_initialized:
            return True
            
        try:
            logger.info("Initializing Local AI Service...")
            
            # Check Ollama service health
            is_healthy = await self.health_check()
            if not is_healthy:
                logger.warning("Ollama service is not available - AI features will use fallback responses")
                self.is_initialized = True  # Still initialize to provide fallback
                return False
            
            # Load available models
            await self._load_available_models()
            logger.info("Local AI Service initialized successfully")
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Local AI Service: {e}")
            self.is_initialized = True  # Still initialize to provide fallback
            return False
    
    async def health_check(self) -> bool:
        """Check if Ollama service is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags", 
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        logger.info(f"Ollama healthy. Available models: {models}")
                        return True
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
        return False
    
    async def _load_available_models(self):
        """Load list of available models from Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        for model in data.get("models", []):
                            self.available_models[model["name"]] = {
                                "size": model.get("size", 0),
                                "modified_at": model.get("modified_at", ""),
                                "digest": model.get("digest", "")
                            }
        except Exception as e:
            logger.error(f"Failed to load available models: {e}")
    
    def _initialize_prompts(self) -> Dict[str, str]:
        """Initialize prompt templates for different AI tasks"""
        return {
            "chat": """You are a cybersecurity expert assistant for the CVE Analysis Platform. 

Context: {context}
Previous conversation: {history}
User: {user_input}

Provide helpful, accurate cybersecurity guidance. Be concise but informative. If discussing CVEs, focus on practical security implications.""",

            "cve_analysis": """Analyze this CVE data and provide a comprehensive security assessment:

CVE Data:
{cve_data}

Provide analysis covering:
1. Vulnerability type and attack vectors
2. Risk severity assessment (1-10 scale)  
3. Potential impact on different systems
4. Remediation priorities
5. Exploitation likelihood

Be technical but clear. Focus on actionable security insights.""",

            "code_analysis": """Analyze this code for security vulnerabilities:

Code:
{code}

Context: {context}

Provide detailed security analysis:
1. Identified vulnerabilities
2. Severity ratings
3. Exploitation methods
4. Secure coding fixes
5. Prevention strategies

Be specific and provide remediation examples."""
        }
    
    async def generate_response(
        self, 
        prompt: str, 
        model: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from specified Ollama model"""
        # Check if AI service is available
        if not await self.health_check():
            return self._fallback_response(prompt, model)
        
        # Check cache first
        cache_key = hashlib.md5(f"{model}:{prompt}".encode()).hexdigest()
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if (datetime.now() - cached["timestamp"]).seconds < 300:  # 5 min cache
                return cached["response"]
        
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
            start_time = datetime.now()
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        # FIX: Handle potential JSON parsing errors from Ollama streaming responses
                        try:
                            result = await response.json()
                        except json.JSONDecodeError as json_error:
                            logger.error(f"JSON decode error in AI service: {json_error}")
                            # Try to parse as text and extract JSON
                            response_text = await response.text()
                            logger.debug(f"Raw AI service response: {response_text}")
                            
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
                                    "response": "Error: Could not parse AI service response",
                                    "done": True
                                }
                        
                        ai_response = {
                            "success": True,
                            "response": result.get("response", "").strip(),
                            "model": model,
                            "processing_time": (datetime.now() - start_time).total_seconds(),
                            "tokens_used": result.get("eval_count", 0),
                            "source": "ollama_local"
                        }
                        
                        # Cache successful responses
                        self.response_cache[cache_key] = {
                            "response": ai_response,
                            "timestamp": datetime.now()
                        }
                        
                        return ai_response
                    else:
                        logger.error(f"Ollama API error {response.status}")
                        return self._fallback_response(prompt, model)
        
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return self._fallback_response(prompt, model)
    
    def _fallback_response(self, prompt: str, model: str) -> Dict[str, Any]:
        """Provide fallback response when AI is unavailable"""
        fallback_responses = {
            "chat": "I'm here to help with CVE analysis and cybersecurity questions. The AI system is currently initializing - please try again in a moment.",
            "cve_analysis": "CVE analysis requires the local AI models to be available. Please ensure Ollama is running with the required models.",
            "code_analysis": "Code vulnerability analysis is temporarily unavailable. Please check that the local AI service is running."
        }
        
        # Determine response type from prompt content
        response_type = "chat"
        if "CVE" in prompt:
            response_type = "cve_analysis"
        elif "code" in prompt.lower():
            response_type = "code_analysis"
        
        return {
            "success": False,
            "response": fallback_responses.get(response_type, "AI service temporarily unavailable."),
            "model": model,
            "processing_time": 0.1,
            "source": "fallback",
            "error": "AI service unavailable"
        }
    
    async def chat_response(
        self, 
        user_input: str, 
        context: str = "", 
        history: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate AI chat response"""
        if not self.is_initialized:
            await self.initialize()
            
        model = self.model_assignments["chat"]
        prompt = self.prompt_templates["chat"].format(
            user_input=user_input,
            context=context,
            history=history
        )
        
        response = await self.generate_response(
            prompt, 
            model, 
            temperature=0.7,
            **kwargs
        )
        
        if response["success"]:
            logger.info(f"Chat response generated using {model}")
        return response
    
    async def analyze_cve(
        self, 
        cve_data: Dict[str, Any], 
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze CVE using local AI"""
        if not self.is_initialized:
            await self.initialize()
            
        model = self.model_assignments["cve_analysis"]
        
        # Format CVE data for analysis
        formatted_cve = self._format_cve_data(cve_data)
        
        prompt = self.prompt_templates["cve_analysis"].format(
            cve_data=formatted_cve
        )
        
        response = await self.generate_response(
            prompt, 
            model, 
            temperature=0.1,  # Lower temperature for technical analysis
            **kwargs
        )
        
        if response["success"]:
            logger.info(f"CVE analysis completed using {model}")
            # Parse and structure the analysis response
            analysis = self._parse_cve_analysis(response["response"])
            response["structured_analysis"] = analysis
        
        return response
    
    async def analyze_code(
        self, 
        code: str, 
        context: str = "", 
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze code for vulnerabilities using local AI"""
        if not self.is_initialized:
            await self.initialize()
            
        model = self.model_assignments["code_analysis"]
        
        prompt = self.prompt_templates["code_analysis"].format(
            code=code,
            context=context
        )
        
        response = await self.generate_response(
            prompt, 
            model, 
            temperature=0.1,
            **kwargs
        )
        
        if response["success"]:
            logger.info(f"Code analysis completed using {model}")
        
        return response
    
    def _format_cve_data(self, cve_data: Dict[str, Any]) -> str:
        """Format CVE data for AI analysis"""
        formatted = []
        
        if "id" in cve_data:
            formatted.append(f"CVE ID: {cve_data['id']}")
        if "description" in cve_data:
            formatted.append(f"Description: {cve_data['description']}")
        if "severity" in cve_data:
            formatted.append(f"CVSS Score: {cve_data['severity']}")
        if "published_date" in cve_data:
            formatted.append(f"Published: {cve_data['published_date']}")
        if "cwe" in cve_data:
            formatted.append(f"CWE: {cve_data['cwe']}")
        
        return "\n".join(formatted) if formatted else "No CVE data available"
    
    def _parse_cve_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse structured analysis from AI response"""
        analysis = {
            "risk_score": self._extract_risk_score(analysis_text),
            "vulnerability_type": "Unknown",
            "impact_assessment": "Analysis pending",
            "remediation_priority": self._extract_priority(analysis_text),
            "exploitation_likelihood": "Medium"
        }
        return analysis
    
    def _extract_risk_score(self, text: str) -> int:
        """Extract risk score from analysis text"""
        import re
        score_match = re.search(r'(\d+)/10|(\d+)\s*(?:out of|/)\s*10', text)
        if score_match:
            return int(score_match.group(1) or score_match.group(2))
        return 5  # Default medium risk
    
    def _extract_priority(self, text: str) -> str:
        """Extract remediation priority"""
        text_lower = text.lower()
        if "critical" in text_lower or "urgent" in text_lower:
            return "Critical"
        elif "high" in text_lower:
            return "High"
        elif "medium" in text_lower:
            return "Medium"
        elif "low" in text_lower:
            return "Low"
        return "Medium"
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get AI service statistics"""
        is_healthy = await self.health_check()
        return {
            "service_status": "active" if is_healthy else "inactive",
            "available_models": list(self.available_models.keys()) if is_healthy else [],
            "model_assignments": self.model_assignments,
            "cache_size": len(self.response_cache),
            "base_url": self.base_url,
            "is_initialized": self.is_initialized
        }

# Global AI service instance
ai_service = LocalAIService()
