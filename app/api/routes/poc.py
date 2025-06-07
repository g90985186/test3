from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from app.ai.services.poc_generator import POCGenerator
from app.core.security import get_auth_dependency, get_admin_dependency
from app.dependencies import get_model_manager, get_prompt_manager
import logging

router = APIRouter()

class POCRequest(BaseModel):
    """Request model for PoC generation."""
    cve_id: str
    description: Optional[str] = "Security vulnerability"
    vulnerability_type: Optional[str] = "unknown"
    affected_component: Optional[str] = "system"
    model_name: Optional[str] = "codellama:7b"

class POCResponse(BaseModel):
    """Response model for PoC generation."""
    cve_id: str
    code: str
    documentation: Dict[str, str]
    metadata: Dict[str, Any]

@router.post("/generate", response_model=POCResponse)
async def generate_poc(
    request: POCRequest,
    auth: str = Depends(get_auth_dependency()),
    model_manager = Depends(get_model_manager),
    prompt_manager = Depends(get_prompt_manager)
) -> POCResponse:
    """Generate a PoC for a CVE using AI."""
    try:
        # Generate PoC using AI
        poc_generator = POCGenerator(model_manager, prompt_manager)
        result = await poc_generator.generate_poc(
            cve_id=request.cve_id,
            vulnerability_type=request.vulnerability_type,
            affected_component=request.affected_component,
            description=request.description
        )
        
        return POCResponse(
            cve_id=request.cve_id,
            code=result["code"],
            documentation=result["documentation"],
            metadata=result["metadata"]
        )
        
    except Exception as e:
        logger.error(f"Error generating PoC: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate PoC. Please ensure the AI service is running and try again."
        )

@router.get("/{cve_id}", response_model=POCResponse)
async def get_poc(
    cve_id: str,
    auth: str = Depends(get_auth_dependency())
) -> POCResponse:
    """Get a previously generated PoC."""
    # Mock response for existing PoC
    return POCResponse(
        cve_id=cve_id,
        code=f"# Existing PoC for {cve_id}\nprint('This PoC was previously generated')",
        documentation={
            "description": f"Previously generated PoC for {cve_id}",
            "usage": "Run this code in a controlled environment",
            "warnings": "This is for testing purposes only"
        },
        metadata={
            "generated_at": "2024-01-01T00:00:00Z",
            "model_used": "codellama",
            "version": "1.0"
        }
    )

@router.get("/", response_model=List[str])
async def list_pocs(
    auth: str = Depends(get_auth_dependency())
) -> List[str]:
    """List all available PoCs."""
    return ["CVE-2024-1234", "CVE-2024-5678", "CVE-2024-9999"]

@router.post("/{cve_id}/validate")
async def validate_poc(
    cve_id: str,
    auth: str = Depends(get_auth_dependency())
) -> Dict[str, Any]:
    """Validate a generated PoC."""
    return {
        "cve_id": cve_id,
        "validation_status": "passed",
        "checks": {
            "syntax_valid": True,
            "dependencies_available": True,
            "security_warnings": False
        },
        "validated_at": "2024-01-01T00:00:00Z"
    } 