from typing import Dict, List, Optional, Any
import json
import logging
from pathlib import Path
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class PromptTemplate(BaseModel):
    """Prompt template with variables."""
    name: str
    description: str
    template: str
    variables: List[str]
    metadata: Dict[str, str] = {}

class PromptManager:
    """Manages prompt templates and their optimization."""
    
    def __init__(self, templates_dir: str = "app/ai/prompts/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, PromptTemplate] = {}
        self.template_usage: Dict[str, int] = {}
        self.template_success: Dict[str, int] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load prompt templates from the templates directory."""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    template = PromptTemplate(**data)
                    self.templates[template.name] = template
                    self.template_usage[template.name] = 0
                    self.template_success[template.name] = 0
                    logger.info(f"Loaded prompt template: {template.name}")
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {str(e)}")
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name."""
        return self.templates.get(name)
    
    def format_prompt(
        self,
        template_name: str,
        **variables
    ) -> str:
        """Format a prompt template with variables."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        # Check if all required variables are provided
        missing_vars = set(template.variables) - set(variables.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        # Format the template
        try:
            prompt = template.template.format(**variables)
            self.template_usage[template_name] += 1
            return prompt
        except KeyError as e:
            logger.error(f"Error formatting template {template_name}: {str(e)}")
            raise
    
    def record_success(self, template_name: str) -> None:
        """Record a successful prompt usage."""
        if template_name in self.template_success:
            self.template_success[template_name] += 1
    
    def get_template_stats(self, template_name: str) -> Dict[str, Any]:
        """Get statistics for a specific template."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        total_usage = self.template_usage[template_name]
        success_count = self.template_success[template_name]
        
        return {
            "name": template_name,
            "description": template.description,
            "total_usage": total_usage,
            "success_count": success_count,
            "success_rate": (
                success_count / total_usage
                if total_usage > 0 else 0
            ),
            "variables": template.variables,
            "metadata": template.metadata
        }
    
    def get_all_template_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all templates."""
        return {
            name: self.get_template_stats(name)
            for name in self.templates
        }
    
    def save_template(self, template: PromptTemplate) -> None:
        """Save a new prompt template."""
        template_file = self.templates_dir / f"{template.name}.json"
        
        try:
            with open(template_file, "w", encoding="utf-8") as f:
                json.dump(template.dict(), f, indent=2)
            
            self.templates[template.name] = template
            self.template_usage[template.name] = 0
            self.template_success[template.name] = 0
            
            logger.info(f"Saved prompt template: {template.name}")
        except Exception as e:
            logger.error(f"Error saving template {template.name}: {str(e)}")
            raise 