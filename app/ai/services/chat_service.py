from typing import List, Dict, Optional, Any
import json
import logging
from datetime import datetime
from pathlib import Path
from ..models.manager import ModelManager
from ..prompts.manager import PromptManager

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, model_manager: ModelManager, prompt_manager: PromptManager):
        self.model_manager = model_manager
        self.prompt_manager = prompt_manager
        self.chat_history_dir = Path("data/chat_history")
        self.chat_history_dir.mkdir(parents=True, exist_ok=True)
        
    async def get_response(
        self,
        user_question: str,
        session_id: str,
        cve_id: Optional[str] = None,
        poc_id: Optional[str] = None,
        context_cve_ids: Optional[List[str]] = None,
        conversation_type: str = "general"
    ) -> Dict[str, Any]:
        """Get AI response for a user question."""
        try:
            # Load chat history
            chat_history = self._load_chat_history(session_id)
            
            # Get CVE and PoC information if available
            cve_info = self._get_cve_info(cve_id) if cve_id else ""
            poc_info = self._get_poc_info(poc_id) if poc_id else ""
            
            # Add context CVEs if provided
            context_info = ""
            if context_cve_ids:
                context_info = self._get_context_cves_info(context_cve_ids)
            
            # Format chat history
            formatted_history = self._format_chat_history(chat_history)
            
            # Get response from AI
            response = await self._get_ai_response(
                user_question,
                cve_info,
                poc_info,
                context_info,
                formatted_history,
                conversation_type
            )
            
            # Save to chat history
            self._save_to_history(session_id, user_question, response)
            
            return {
                "response": response,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "context_used": context_cve_ids or [],
                "suggestions": self._generate_suggestions(conversation_type),
                "metadata": {
                    "conversation_type": conversation_type,
                    "cve_context": bool(cve_id or context_cve_ids),
                    "poc_context": bool(poc_id)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting chat response: {str(e)}")
            return {
                "response": "I'm sorry, I encountered an error processing your request. Please try again.",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "context_used": [],
                "suggestions": ["Try asking about CVE search", "Ask about the platform features"],
                "metadata": {"error": str(e)}
            }
    
    def _load_chat_history(self, session_id: str) -> List[Dict]:
        """Load chat history for a session."""
        history_file = self.chat_history_dir / f"{session_id}.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading chat history: {e}")
        return []
    
    def _save_to_history(self, session_id: str, question: str, response: str):
        """Save chat interaction to history."""
        try:
            history = self._load_chat_history(session_id)
            history.append({
                "question": question,
                "response": response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep only last 50 messages
            history = history[-50:]
            
            history_file = self.chat_history_dir / f"{session_id}.json"
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
    
    def _format_chat_history(self, history: List[Dict]) -> str:
        """Format chat history for prompt."""
        if not history:
            return ""
        
        formatted = []
        # Only use last 5 messages for context to avoid token limits
        for msg in history[-5:]:
            formatted.append(f"User: {msg['question']}")
            formatted.append(f"Assistant: {msg['response']}")
        return "\n".join(formatted)
    
    def _get_cve_info(self, cve_id: str) -> str:
        """Get CVE information."""
        # This should integrate with your CVE database
        # For now, return basic info
        return f"CVE ID: {cve_id}\nNote: Detailed CVE information would be retrieved from database"
    
    def _get_poc_info(self, poc_id: str) -> str:
        """Get PoC information."""
        # This should integrate with your PoC system
        return f"PoC ID: {poc_id}\nNote: PoC information would be retrieved from system"
    
    def _get_context_cves_info(self, cve_ids: List[str]) -> str:
        """Get information about context CVEs."""
        if not cve_ids:
            return ""
        
        info_parts = []
        for cve_id in cve_ids[:3]:  # Limit to 3 CVEs to avoid overwhelming context
            info_parts.append(f"- {cve_id}: Context CVE for reference")
        
        return f"Context CVEs:\n" + "\n".join(info_parts)
    
    async def _get_ai_response(
        self,
        question: str,
        cve_info: str,
        poc_info: str,
        context_info: str,
        chat_history: str,
        conversation_type: str
    ) -> str:
        """Get response from AI model."""
        try:
            # Build the prompt based on available template
            template = self.prompt_manager.get_template("chat")
            if not template:
                # Fallback template if not found
                template_text = """You are a helpful AI assistant specializing in cybersecurity and CVE analysis.

Context Information:
{context_info}

CVE Information:
{cve_info}

PoC Information:
{poc_info}

Previous Conversation:
{chat_history}

User Question: {user_question}

Please provide a helpful, accurate, and concise response. Focus on cybersecurity topics and be practical in your advice."""
            else:
                template_text = template.template

            # Format the prompt
            formatted_prompt = template_text.format(
                context_info=context_info,
                cve_info=cve_info,
                poc_info=poc_info,
                chat_history=chat_history,
                user_question=question
            )
            
            # Get response from model manager
            response = await self.model_manager.generate_response(
                model_name="llama3.1:8b",  # Default chat model
                prompt=formatted_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return self._get_fallback_response(question, conversation_type)
    
    def _get_fallback_response(self, question: str, conversation_type: str) -> str:
        """Provide fallback response when AI is unavailable."""
        fallback_responses = {
            "general": "I'm here to help with CVE analysis and cybersecurity questions. The AI system is currently initializing - please try again in a moment.",
            "cve_specific": "I can help you analyze CVEs and security vulnerabilities. Please ensure the AI models are running and try your question again.",
            "analysis": "For vulnerability analysis, I need the AI models to be available. Please check the system status and try again.",
            "help": "Here are some things I can help with:\n- CVE search and analysis\n- Security vulnerability assessment\n- Risk evaluation\n- Mitigation strategies\n\nPlease try your question again once the AI system is ready."
        }
        
        return fallback_responses.get(conversation_type, fallback_responses["general"])
    
    def _generate_suggestions(self, conversation_type: str) -> List[str]:
        """Generate contextual suggestions for the user."""
        suggestions_map = {
            "general": [
                "Search for recent CVEs",
                "Analyze a specific vulnerability",
                "Get help with the platform features",
                "View the dashboard"
            ],
            "cve_specific": [
                "Analyze this CVE's impact",
                "Get mitigation recommendations",
                "Compare with similar vulnerabilities",
                "Generate a PoC"
            ],
            "analysis": [
                "Export analysis results",
                "Get remediation steps",
                "Assess business impact",
                "View attack vectors"
            ],
            "help": [
                "Show keyboard shortcuts",
                "Explain platform features",
                "View getting started guide",
                "Contact support"
            ]
        }
        
        return suggestions_map.get(conversation_type, suggestions_map["general"])
    
    def clear_history(self, session_id: str) -> bool:
        """Clear chat history for a session."""
        try:
            history_file = self.chat_history_dir / f"{session_id}.json"
            if history_file.exists():
                history_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Error clearing chat history: {e}")
            return False
    
    def get_chat_stats(self) -> Dict[str, Any]:
        """Get chat system statistics."""
        try:
            history_files = list(self.chat_history_dir.glob("*.json"))
            total_sessions = len(history_files)
            
            total_messages = 0
            for file in history_files:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        history = json.load(f)
                        total_messages += len(history)
                except:
                    continue
            
            return {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "average_messages_per_session": total_messages / max(total_sessions, 1)
            }
        except Exception as e:
            logger.error(f"Error getting chat stats: {e}")
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "average_messages_per_session": 0
            }
