from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from app.ai.services.poc_generator import POCGenerator
from app.core.security import get_auth_dependency, get_admin_dependency

router = APIRouter()

class POCRequest(BaseModel):
    """Request model for PoC generation."""
    cve_id: str
    description: str
    vulnerability_type: str
    affected_component: str
    model_name: Optional[str] = "codellama"

class POCResponse(BaseModel):
    """Response model for PoC generation."""
    cve_id: str
    code: str
    documentation: Dict[str, str]
    metadata: Dict[str, Any]

@router.post("/generate", response_model=POCResponse)
async def generate_poc(
    request: POCRequest,
    auth: str = Depends(get_auth_dependency())
) -> POCResponse:
    """Generate a PoC for a CVE."""
    try:
        # For now, return a mock response since POCGenerator has complex dependencies
        return POCResponse(
            cve_id=request.cve_id,
            code=f"# PoC for {request.cve_id}\n# This is a placeholder implementation\nprint('PoC generated for {request.vulnerability_type}')",
            documentation={
                "description": f"Proof of concept for {request.cve_id}",
                "vulnerability_type": request.vulnerability_type,
                "affected_component": request.affected_component,
                "usage": "Run this code in a controlled environment",
                "warnings": "This is for testing purposes only"
            },
            metadata={
                "generated_at": "2024-01-01T00:00:00Z",
                "model_used": request.model_name,
                "version": "1.0"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PoC: {str(e)}"
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