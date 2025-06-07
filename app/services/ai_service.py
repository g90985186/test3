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

            "cve_analysis": """You are an elite cybersecurity expert and penetration tester. Provide a sophisticated, comprehensive technical analysis of this CVE with detailed exploitation scenarios and attack methodologies.

CVE Data:
{cve_data}

Provide detailed analysis covering:

1. **VULNERABILITY CLASSIFICATION & ROOT CAUSE ANALYSIS**
   - Detailed vulnerability type and CWE pattern analysis
   - Root cause analysis and code-level understanding
   - Attack surface mapping and entry points

2. **ADVANCED EXPLOITATION ANALYSIS**
   - Step-by-step attack scenarios with technical details
   - Exploitation difficulty and skill requirements
   - Required tools, frameworks, and techniques
   - Payload development and delivery methods
   - Bypass techniques for security controls

3. **TECHNICAL EXPLOITATION DETAILS**
   - Memory corruption exploitation techniques (if applicable)
   - Code injection vectors and methods (if applicable)
   - Privilege escalation pathways and techniques
   - Persistence mechanisms and backdoor methods

4. **ATTACK CHAIN & SCENARIO MODELING**
   - Complete attack flow from reconnaissance to post-exploitation
   - Lateral movement and network propagation possibilities
   - Data exfiltration and impact scenarios
   - APT-style attack integration possibilities

5. **DEFENSIVE COUNTERMEASURES**
   - Detection signatures and behavioral indicators
   - Prevention controls and hardening measures
   - Monitoring recommendations and forensic artifacts
   - Incident response procedures

6. **THREAT INTELLIGENCE ASSESSMENT**
   - Exploitation likelihood and timeline
   - Threat actor interest and weaponization potential
   - Market value and underground activity
   - Real-world exploitation evidence

Provide technical depth suitable for penetration testers, red teams, and advanced security professionals. Focus on actionable intelligence and practical exploitation knowledge.""",

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
            raise Exception("AI service is currently unavailable. Please ensure Ollama is running with the required models.")
        
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
        """Comprehensive CVE analysis using local AI with detailed insights"""
        if not self.is_initialized:
            await self.initialize()
            
        model = self.model_assignments["cve_analysis"]
        
        # Enhanced CVE data formatting for comprehensive analysis
        formatted_data = self._format_comprehensive_cve_data(cve_data)
        
        # Format the CVE data as a string for the template
        cve_data_str = f"""CVE ID: {formatted_data.get("cve_id", "Unknown")}
Description: {formatted_data.get("description", "No description available")}
CVSS Score: {formatted_data.get("cvss_score", "Not available")}
Severity Level: {formatted_data.get("severity_level", "Unknown")}
CWE IDs: {formatted_data.get("cwe_ids", "Not specified")}
Published Date: {formatted_data.get("published_date", "Unknown")}
Affected Products: {formatted_data.get("affected_products", "Not specified")}
References: {formatted_data.get("references", "No references available")}"""
        
        prompt = self.prompt_templates["cve_analysis"].format(
            cve_data=cve_data_str
        )
        
        response = await self.generate_response(
            prompt, 
            model, 
            temperature=0.2,  # Low temperature for consistent technical analysis
            num_predict=4096,  # More tokens for comprehensive analysis
            **kwargs
        )
        
        if response["success"]:
            logger.info(f"CVE analysis completed using {model}")
            # Parse and structure the comprehensive analysis response
            structured_analysis = self._parse_comprehensive_cve_analysis(response["response"], cve_data)
            response["structured_analysis"] = structured_analysis
            response["detailed_insights"] = self._extract_detailed_insights(response["response"])
        
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
    
    def _format_comprehensive_cve_data(self, cve_data: Dict[str, Any]) -> Dict[str, str]:
        """Format CVE data comprehensively for detailed AI analysis"""
        
        # Handle different possible field names and formats
        cve_id = (cve_data.get("cve_id") or 
                 cve_data.get("id") or 
                 cve_data.get("CVE_ID") or 
                 "Unknown CVE")
        
        description = (cve_data.get("description") or 
                      cve_data.get("summary") or 
                      "No description available")
        
        cvss_score = (cve_data.get("cvss_v3_score") or 
                     cve_data.get("cvss_score") or 
                     cve_data.get("severity") or 
                     "Not available")
        
        severity_level = (cve_data.get("severity_level") or 
                         cve_data.get("severity") or 
                         self._determine_severity_from_score(cvss_score))
        
        # Format CWE IDs
        cwe_ids = cve_data.get("cwe_ids", [])
        if isinstance(cwe_ids, list):
            cwe_formatted = ", ".join(cwe_ids) if cwe_ids else "Not specified"
        else:
            cwe_formatted = str(cwe_ids) if cwe_ids else "Not specified"
        
        # Format published date
        published_date = (cve_data.get("published_date") or 
                         cve_data.get("published") or 
                         "Unknown")
        
        # Format affected products
        affected_products = cve_data.get("affected_products", [])
        if isinstance(affected_products, list):
            products_formatted = ", ".join(affected_products) if affected_products else "Not specified"
        else:
            products_formatted = str(affected_products) if affected_products else "Not specified"
        
        # Format references
        references = cve_data.get("references", [])
        if isinstance(references, list):
            refs_formatted = "\n".join([f"- {ref}" for ref in references[:5]]) if references else "No references available"
        else:
            refs_formatted = str(references) if references else "No references available"
        
        return {
            "cve_id": cve_id,
            "description": description,
            "cvss_score": str(cvss_score),
            "severity_level": severity_level,
            "cwe_ids": cwe_formatted,
            "published_date": str(published_date),
            "affected_products": products_formatted,
            "references": refs_formatted
        }
    
    def _determine_severity_from_score(self, score) -> str:
        """Determine severity level from CVSS score"""
        try:
            score_float = float(score)
            if score_float >= 9.0:
                return "CRITICAL"
            elif score_float >= 7.0:
                return "HIGH"
            elif score_float >= 4.0:
                return "MEDIUM"
            else:
                return "LOW"
        except (ValueError, TypeError):
            return "Unknown"
    
    def _parse_comprehensive_cve_analysis(self, analysis_text: str, cve_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse comprehensive structured analysis from AI response"""
        
        analysis = {
            # Basic assessment
            "risk_score": self._extract_risk_score(analysis_text),
            "vulnerability_type": self._extract_vulnerability_type(analysis_text),
            "remediation_priority": self._extract_priority(analysis_text),
            "exploitation_likelihood": self._extract_exploitation_likelihood(analysis_text),
            
            # Technical details
            "attack_vectors": self._extract_attack_vectors(analysis_text),
            "technical_complexity": self._extract_complexity(analysis_text),
            "prerequisites": self._extract_prerequisites(analysis_text),
            
            # Impact analysis
            "confidentiality_impact": self._extract_impact_type(analysis_text, "confidentiality"),
            "integrity_impact": self._extract_impact_type(analysis_text, "integrity"),
            "availability_impact": self._extract_impact_type(analysis_text, "availability"),
            "business_impact": self._extract_business_impact(analysis_text),
            
            # Mitigation and recommendations
            "immediate_actions": self._extract_immediate_actions(analysis_text),
            "patch_availability": self._extract_patch_info(analysis_text),
            "workarounds": self._extract_workarounds(analysis_text),
            "monitoring_recommendations": self._extract_monitoring_recommendations(analysis_text),
            
            # Metadata
            "analysis_confidence": self._calculate_analysis_confidence(analysis_text, cve_data),
            "last_updated": datetime.now().isoformat()
        }
        
        return analysis
    
    def _extract_detailed_insights(self, analysis_text: str) -> Dict[str, Any]:
        """Extract detailed insights from the AI analysis"""
        
        insights = {
            "key_findings": self._extract_key_findings(analysis_text),
            "security_implications": self._extract_security_implications(analysis_text),
            "threat_landscape": self._extract_threat_landscape(analysis_text),
            "compliance_considerations": self._extract_compliance_considerations(analysis_text),
            "detection_strategies": self._extract_detection_strategies(analysis_text)
        }
        
        return insights
    
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
    
    def _extract_vulnerability_type(self, text: str) -> str:
        """Extract vulnerability type from analysis"""
        text_lower = text.lower()
        
        # Common vulnerability types
        vuln_types = {
            "injection": ["sql injection", "code injection", "command injection", "ldap injection"],
            "xss": ["cross-site scripting", "xss", "reflected xss", "stored xss"],
            "authentication": ["authentication bypass", "weak authentication", "broken authentication"],
            "authorization": ["privilege escalation", "access control", "authorization bypass"],
            "cryptographic": ["weak encryption", "cryptographic", "weak hash", "broken crypto"],
            "buffer_overflow": ["buffer overflow", "stack overflow", "heap overflow"],
            "deserialization": ["deserialization", "unsafe deserialization"],
            "path_traversal": ["path traversal", "directory traversal", "file inclusion"],
            "ssrf": ["server-side request forgery", "ssrf"],
            "csrf": ["cross-site request forgery", "csrf"],
            "dos": ["denial of service", "dos", "ddos"],
            "information_disclosure": ["information disclosure", "data exposure", "sensitive data"]
        }
        
        for vuln_type, keywords in vuln_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return vuln_type.replace("_", " ").title()
        
        return "Unknown"
    
    def _extract_exploitation_likelihood(self, text: str) -> str:
        """Extract exploitation likelihood"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["very high", "extremely likely", "trivial", "easy"]):
            return "Very High"
        elif any(word in text_lower for word in ["high", "likely", "probable"]):
            return "High"
        elif any(word in text_lower for word in ["medium", "moderate", "possible"]):
            return "Medium"
        elif any(word in text_lower for word in ["low", "unlikely", "difficult"]):
            return "Low"
        elif any(word in text_lower for word in ["very low", "extremely unlikely", "nearly impossible"]):
            return "Very Low"
        
        return "Medium"
    
    def _extract_attack_vectors(self, text: str) -> List[str]:
        """Extract attack vectors from analysis"""
        vectors = []
        text_lower = text.lower()
        
        vector_keywords = {
            "Network": ["network", "remote", "internet", "web"],
            "Local": ["local", "physical access", "local access"],
            "Adjacent Network": ["adjacent", "local network", "lan"],
            "Physical": ["physical", "physical access", "usb", "hardware"]
        }
        
        for vector, keywords in vector_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                vectors.append(vector)
        
        return vectors if vectors else ["Unknown"]
    
    def _extract_complexity(self, text: str) -> str:
        """Extract technical complexity"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["very complex", "extremely difficult", "advanced"]):
            return "Very High"
        elif any(word in text_lower for word in ["complex", "difficult", "sophisticated"]):
            return "High"
        elif any(word in text_lower for word in ["moderate", "medium complexity"]):
            return "Medium"
        elif any(word in text_lower for word in ["simple", "easy", "straightforward", "low complexity"]):
            return "Low"
        
        return "Medium"
    
    def _extract_prerequisites(self, text: str) -> List[str]:
        """Extract prerequisites for exploitation"""
        prerequisites = []
        text_lower = text.lower()
        
        prereq_patterns = [
            ("Authentication Required", ["authentication", "login", "credentials"]),
            ("Administrative Access", ["admin", "administrator", "root", "elevated"]),
            ("User Interaction", ["user interaction", "social engineering", "click"]),
            ("Network Access", ["network access", "network connectivity"]),
            ("Local Access", ["local access", "physical access"]),
            ("Specific Configuration", ["configuration", "misconfiguration", "settings"])
        ]
        
        for prereq, keywords in prereq_patterns:
            if any(keyword in text_lower for keyword in keywords):
                prerequisites.append(prereq)
        
        return prerequisites if prerequisites else ["Standard system access"]
    
    def _extract_impact_type(self, text: str, impact_type: str) -> str:
        """Extract specific impact type (confidentiality, integrity, availability)"""
        text_lower = text.lower()
        impact_section = ""
        
        # Try to find the specific impact section
        if f"{impact_type} impact" in text_lower:
            start = text_lower.find(f"{impact_type} impact")
            end = text_lower.find("\n\n", start)
            if end == -1:
                end = start + 200
            impact_section = text_lower[start:end]
        else:
            impact_section = text_lower
        
        if any(word in impact_section for word in ["complete", "total", "full", "high"]):
            return "High"
        elif any(word in impact_section for word in ["partial", "limited", "some"]):
            return "Partial"
        elif any(word in impact_section for word in ["none", "no impact", "minimal"]):
            return "None"
        
        return "Unknown"
    
    def _extract_business_impact(self, text: str) -> List[str]:
        """Extract business impact considerations"""
        impacts = []
        text_lower = text.lower()
        
        business_impacts = [
            ("Data Breach", ["data breach", "data exposure", "sensitive data"]),
            ("Service Disruption", ["service disruption", "downtime", "availability"]),
            ("Financial Loss", ["financial", "revenue", "cost"]),
            ("Reputation Damage", ["reputation", "brand", "trust"]),
            ("Compliance Violation", ["compliance", "regulatory", "gdpr", "hipaa"]),
            ("Intellectual Property Theft", ["intellectual property", "trade secrets", "proprietary"])
        ]
        
        for impact, keywords in business_impacts:
            if any(keyword in text_lower for keyword in keywords):
                impacts.append(impact)
        
        return impacts if impacts else ["Potential security compromise"]
    
    def _extract_immediate_actions(self, text: str) -> List[str]:
        """Extract immediate action items"""
        actions = []
        text_lower = text.lower()
        
        # Look for action-oriented phrases
        action_patterns = [
            "apply patch",
            "update software",
            "disable service",
            "implement workaround",
            "monitor systems",
            "review logs",
            "restrict access",
            "backup data"
        ]
        
        for pattern in action_patterns:
            if pattern in text_lower:
                actions.append(pattern.title())
        
        # If no specific actions found, provide generic ones
        if not actions:
            actions = ["Review security patches", "Monitor system logs", "Assess exposure"]
        
        return actions
    
    def _extract_patch_info(self, text: str) -> str:
        """Extract patch availability information"""
        text_lower = text.lower()
        
        if "patch available" in text_lower or "update available" in text_lower:
            return "Available"
        elif "patch pending" in text_lower or "fix in development" in text_lower:
            return "Pending"
        elif "no patch" in text_lower or "no fix" in text_lower:
            return "Not Available"
        
        return "Unknown"
    
    def _extract_workarounds(self, text: str) -> List[str]:
        """Extract workaround suggestions"""
        workarounds = []
        text_lower = text.lower()
        
        workaround_patterns = [
            "disable feature",
            "restrict access",
            "implement firewall rules",
            "use alternative software",
            "apply configuration changes",
            "enable additional logging"
        ]
        
        for pattern in workaround_patterns:
            if pattern in text_lower:
                workarounds.append(pattern.title())
        
        return workarounds if workarounds else ["Consult vendor documentation"]
    
    def _extract_monitoring_recommendations(self, text: str) -> List[str]:
        """Extract monitoring and detection recommendations"""
        recommendations = []
        text_lower = text.lower()
        
        monitoring_patterns = [
            "monitor network traffic",
            "review access logs",
            "implement intrusion detection",
            "enable security logging",
            "monitor file integrity",
            "track user activities"
        ]
        
        for pattern in monitoring_patterns:
            if pattern in text_lower:
                recommendations.append(pattern.title())
        
        return recommendations if recommendations else ["Enable comprehensive logging", "Monitor for suspicious activities"]
    
    def _calculate_analysis_confidence(self, analysis_text: str, cve_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on available data
        if cve_data.get("cvss_v3_score"):
            confidence += 0.1
        if cve_data.get("description") and len(cve_data["description"]) > 50:
            confidence += 0.1
        if cve_data.get("cwe_ids"):
            confidence += 0.1
        if cve_data.get("references"):
            confidence += 0.1
        
        # Increase confidence based on analysis depth
        if len(analysis_text) > 1000:
            confidence += 0.1
        if "technical details" in analysis_text.lower():
            confidence += 0.05
        if "mitigation" in analysis_text.lower():
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _extract_key_findings(self, text: str) -> List[str]:
        """Extract key findings from analysis"""
        findings = []
        
        # Look for bullet points or numbered items
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or any(line.startswith(f"{i}.") for i in range(1, 10)):
                finding = line.lstrip('-•0123456789. ').strip()
                if len(finding) > 10:  # Filter out very short items
                    findings.append(finding)
        
        return findings[:5] if findings else ["Comprehensive security analysis completed"]
    
    def _extract_security_implications(self, text: str) -> List[str]:
        """Extract security implications"""
        implications = []
        text_lower = text.lower()
        
        implication_keywords = [
            "security risk",
            "vulnerability allows",
            "attacker can",
            "potential for",
            "risk of",
            "could lead to"
        ]
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if any(keyword in sentence_lower for keyword in implication_keywords):
                implications.append(sentence.strip())
        
        return implications[:3] if implications else ["Standard security considerations apply"]
    
    def _extract_threat_landscape(self, text: str) -> str:
        """Extract threat landscape assessment"""
        text_lower = text.lower()
        
        if "active exploitation" in text_lower or "in the wild" in text_lower:
            return "Active threats detected"
        elif "proof of concept" in text_lower or "poc available" in text_lower:
            return "PoC exploits available"
        elif "theoretical" in text_lower:
            return "Theoretical risk"
        
        return "Standard threat landscape"
    
    def _extract_compliance_considerations(self, text: str) -> List[str]:
        """Extract compliance considerations"""
        considerations = []
        text_lower = text.lower()
        
        compliance_frameworks = [
            "PCI DSS", "HIPAA", "GDPR", "SOX", "ISO 27001", "NIST", "CIS"
        ]
        
        for framework in compliance_frameworks:
            if framework.lower() in text_lower:
                considerations.append(f"{framework} compliance impact")
        
        return considerations if considerations else ["Review applicable compliance requirements"]
    
    def _extract_detection_strategies(self, text: str) -> List[str]:
        """Extract detection strategies"""
        strategies = []
        text_lower = text.lower()
        
        detection_methods = [
            "signature-based detection",
            "behavioral analysis",
            "anomaly detection",
            "log analysis",
            "network monitoring",
            "endpoint detection"
        ]
        
        for method in detection_methods:
            if method in text_lower:
                strategies.append(method.title())
        
        return strategies if strategies else ["Implement comprehensive monitoring", "Review security logs regularly"]
    
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
