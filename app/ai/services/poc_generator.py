from typing import Dict, Optional, List, Any
import logging
from pathlib import Path
import json
import re
from datetime import datetime
from ..models.manager import ModelManager
from ..prompts.manager import PromptManager

logger = logging.getLogger(__name__)

class POCGenerator:
    """Service for generating Proof of Concept code for CVEs."""
    
    def __init__(
        self,
        model_manager: ModelManager,
        prompt_manager: PromptManager,
        output_dir: str = "app/ai/pocs"
    ):
        self.model_manager = model_manager
        self.prompt_manager = prompt_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_poc(
        self,
        cve_id: str,
        description: str,
        vulnerability_type: str,
        affected_component: str,
        model_name: str = "codellama:7b",
        **kwargs
    ) -> Dict[str, str]:
        """Generate a PoC code for a CVE."""
        try:
            # Format the prompt
            prompt = self.prompt_manager.format_prompt(
                "poc_generation",
                cve_id=cve_id,
                description=description,
                vulnerability_type=vulnerability_type,
                affected_component=affected_component
            )
            
            # Generate the code
            model = await self.model_manager.get_model(model_name)
            if not model:
                raise ValueError(f"Model {model_name} not found")
            
            response = await model.generate(
                prompt,
                temperature=0.3,
                max_tokens=4096,
                **kwargs
            )
            
            # Extract code and documentation
            code, documentation = self._parse_response(response.content)
            
            # Save the PoC
            poc_info = {
                "cve_id": cve_id,
                "generated_at": datetime.now().isoformat(),
                "model_used": model_name,
                "code": code,
                "documentation": documentation,
                "metadata": {
                    "vulnerability_type": vulnerability_type,
                    "affected_component": affected_component,
                    "model_confidence": response.confidence
                }
            }
            
            self._save_poc(cve_id, poc_info)
            
            return poc_info
            
        except Exception as e:
            logger.error(f"Error generating PoC for {cve_id}: {str(e)}")
            raise
    
    def _parse_response(self, response: str) -> tuple[str, Dict[str, str]]:
        """Parse the model response into code and documentation."""
        # Extract code blocks
        code_blocks = re.findall(r"```python\n(.*?)\n```", response, re.DOTALL)
        if not code_blocks:
            raise ValueError("No Python code found in the response")
        
        code = code_blocks[0].strip()
        
        # Extract documentation sections
        documentation = {
            "dependencies": self._extract_section(response, "dependencies"),
            "setup": self._extract_section(response, "setup"),
            "usage": self._extract_section(response, "usage"),
            "warnings": self._extract_section(response, "warnings"),
            "explanation": self._extract_section(response, "explanation")
        }
        
        return code, documentation
    
    def _extract_section(self, text: str, section: str) -> str:
        """Extract a specific section from the response."""
        pattern = f"{section.title()}.*?:(.*?)(?=\n\n|\\Z)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _save_poc(self, cve_id: str, poc_info: Dict[str, Any]) -> None:
        """Save the PoC code and information."""
        try:
            # Create CVE-specific directory
            cve_dir = self.output_dir / cve_id
            cve_dir.mkdir(exist_ok=True)
            
            # Save code
            code_file = cve_dir / "poc.py"
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(poc_info["code"])
            
            # Save documentation
            doc_file = cve_dir / "documentation.json"
            with open(doc_file, "w", encoding="utf-8") as f:
                json.dump(poc_info["documentation"], f, indent=2)
            
            # Save metadata
            meta_file = cve_dir / "metadata.json"
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(poc_info["metadata"], f, indent=2)
            
            logger.info(f"Saved PoC for {cve_id}")
            
        except Exception as e:
            logger.error(f"Error saving PoC for {cve_id}: {str(e)}")
            raise
    
    async def get_poc(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """Get a previously generated PoC."""
        try:
            cve_dir = self.output_dir / cve_id
            if not cve_dir.exists():
                return None
            
            # Load code
            code_file = cve_dir / "poc.py"
            with open(code_file, "r", encoding="utf-8") as f:
                code = f.read()
            
            # Load documentation
            doc_file = cve_dir / "documentation.json"
            with open(doc_file, "r", encoding="utf-8") as f:
                documentation = json.load(f)
            
            # Load metadata
            meta_file = cve_dir / "metadata.json"
            with open(meta_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            return {
                "cve_id": cve_id,
                "code": code,
                "documentation": documentation,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error loading PoC for {cve_id}: {str(e)}")
            return None
    
    def list_pocs(self) -> List[str]:
        """List all available PoCs."""
        try:
            return [d.name for d in self.output_dir.iterdir() if d.is_dir()]
        except Exception as e:
            logger.error(f"Error listing PoCs: {str(e)}")
            return []
    
    async def validate_poc(self, cve_id: str) -> Dict[str, Any]:
        """Validate a generated PoC."""
        try:
            poc = await self.get_poc(cve_id)
            if not poc:
                raise ValueError(f"PoC for {cve_id} not found")
            
            validation_results = {
                "cve_id": cve_id,
                "validation_time": datetime.now().isoformat(),
                "checks": {
                    "code_syntax": self._check_code_syntax(poc["code"]),
                    "dependencies": self._check_dependencies(poc["documentation"]),
                    "documentation": self._check_documentation(poc["documentation"]),
                    "safety_warnings": self._check_safety_warnings(poc["documentation"])
                }
            }
            
            # Save validation results
            cve_dir = self.output_dir / cve_id
            validation_file = cve_dir / "validation.json"
            with open(validation_file, "w", encoding="utf-8") as f:
                json.dump(validation_results, f, indent=2)
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating PoC for {cve_id}: {str(e)}")
            raise
    
    def _check_code_syntax(self, code: str) -> Dict[str, Any]:
        """Check Python code syntax."""
        try:
            compile(code, "<string>", "exec")
            return {"status": "valid", "errors": []}
        except SyntaxError as e:
            return {
                "status": "invalid",
                "errors": [{"line": e.lineno, "message": str(e)}]
            }
    
    def _check_dependencies(self, documentation: Dict[str, str]) -> Dict[str, Any]:
        """Check if dependencies are properly documented."""
        deps = documentation.get("dependencies", "")
        return {
            "status": "valid" if deps else "missing",
            "dependencies": deps.split("\n") if deps else []
        }
    
    def _check_documentation(self, documentation: Dict[str, str]) -> Dict[str, Any]:
        """Check if documentation is complete."""
        required_sections = ["setup", "usage", "explanation"]
        missing_sections = [
            section for section in required_sections
            if not documentation.get(section)
        ]
        
        return {
            "status": "valid" if not missing_sections else "incomplete",
            "missing_sections": missing_sections
        }
    
    def _check_safety_warnings(self, documentation: Dict[str, str]) -> Dict[str, Any]:
        """Check if safety warnings are present."""
        warnings = documentation.get("warnings", "")
        return {
            "status": "valid" if warnings else "missing",
            "has_warnings": bool(warnings)
        } 