#!/usr/bin/env python3
"""
app/api/routes/analysis.py
Enhanced Analysis Routes with Auto-Import Support
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models.cve import CVE
from app.services.ollama_service import OllamaService
from app.services.nvd_search_service import NVDSearchService
from app.core.security import get_auth_dependency, get_admin_dependency
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import uuid
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for analysis results
analysis_results = {}
analysis_queue = {}

class AnalysisRequest(BaseModel):
    cve_id: str
    analysis_type: str = "comprehensive"
    auto_import: bool = True  # New flag to auto-import from NVD if not found locally

class RiskAssessmentRequest(BaseModel):
    cve_id: str
    environment_context: dict = {}
    asset_criticality: str = "medium"
    auto_import: bool = True

class CVEAnalysisRequest(BaseModel):
    cve_id: str = Field(..., description="CVE identifier")
    cve_data: Optional[Dict[str, Any]] = Field(None, description="CVE data for analysis")
    analysis_type: str = Field("comprehensive", description="Type: comprehensive, risk_only, impact_only")
    include_recommendations: bool = Field(True, description="Include remediation recommendations")

class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Code to analyze for vulnerabilities")
    language: Optional[str] = Field(None, description="Programming language")
    context: Optional[str] = Field(None, description="Additional context")

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    cve_id: Optional[str] = None
    analysis_type: str
    results: Dict[str, Any]
    ai_insights: Dict[str, Any]
    processing_time: float
    created_at: datetime
    model_used: str

class ThreatIntelRequest(BaseModel):
    indicators: List[str] = Field(..., description="IOCs, domains, IPs to analyze")
    context: Optional[str] = Field(None, description="Additional threat context")

@router.post("/analyze")
async def analyze_cve(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """
    Analyze a CVE using AI models
    If CVE not found locally and auto_import=True, will import from NVD first
    """
    
    cve_id = request.cve_id.strip()
    logger.info(f"Analysis request for {cve_id}, auto_import={request.auto_import}")
    
    try:
        # First, check if CVE exists in local database
        cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
        
        if not cve and request.auto_import:
            logger.info(f"CVE {cve_id} not found locally, attempting auto-import from NVD...")
            
            # Try to import from NVD
            import_result = await auto_import_cve_from_nvd(cve_id, db)
            
            if import_result["success"]:
                logger.info(f"Successfully auto-imported {cve_id}")
                # Retrieve the newly imported CVE
                cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
            else:
                logger.warning(f"Auto-import failed for {cve_id}: {import_result['message']}")
                # Continue without CVE for NVD-only analysis
        
        if not cve:
            # If still no CVE, try NVD-only analysis
            logger.info(f"Performing NVD-only analysis for {cve_id}")
            return await analyze_cve_from_nvd_only(cve_id, request.analysis_type)
        
        # Perform standard local analysis
        logger.info(f"Performing local analysis for {cve_id}")
        ollama_service = OllamaService()
        result = await ollama_service.analyze_cve(cve.to_dict())
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {result.get('error')}")
        
        return {
            "success": True,
            "cve_id": cve_id,
            "analysis": result["analysis"],
            "model_used": result["model_used"],
            "source": "Local Database",
            "auto_imported": cve_id != request.cve_id  # True if we had to import
        }
        
    except Exception as e:
        logger.error(f"Analysis error for {cve_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def auto_import_cve_from_nvd(cve_id: str, db: Session) -> dict:
    """Helper function to auto-import CVE from NVD"""
    
    try:
        nvd_service = NVDSearchService()
        nvd_result = await nvd_service.get_cve_details(cve_id)
        
        if not nvd_result["success"]:
            return {
                "success": False,
                "message": f"CVE {cve_id} not found in NVD: {nvd_result.get('error')}"
            }
        
        cve_data = nvd_result["cve"]
        
        # Parse dates
        published_date = None
        if cve_data.get("published_date") and cve_data["published_date"] != "Unknown":
            try:
                if len(cve_data["published_date"]) == 10:
                    published_date = datetime.strptime(cve_data["published_date"], "%Y-%m-%d")
                else:
                    published_date = datetime.fromisoformat(cve_data["published_date"].replace("Z", "+00:00"))
            except:
                published_date = None
        
        modified_date = None
        if cve_data.get("modified_date"):
            try:
                modified_date = datetime.fromisoformat(cve_data["modified_date"].replace("Z", "+00:00"))
            except:
                modified_date = None
        
        # Create new CVE
        new_cve = CVE(
            cve_id=cve_data["cve_id"],
            description=cve_data.get("description"),
            published_date=published_date,
            modified_date=modified_date,
            cvss_v3_score=cve_data.get("cvss_v3_score"),
            cvss_v3_vector=cve_data.get("cvss_v3_vector"),
            severity_level=cve_data.get("severity_level"),
            cwe_ids=cve_data.get("cwe_ids", []),
            affected_products=[],
            references=cve_data.get("references", [])
        )
        
        db.add(new_cve)
        db.commit()
        
        return {
            "success": True,
            "message": f"CVE {cve_id} auto-imported successfully",
            "cve": new_cve.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Auto-import error for {cve_id}: {e}")
        return {
            "success": False,
            "message": f"Auto-import failed: {str(e)}"
        }

async def analyze_cve_from_nvd_only(cve_id: str, analysis_type: str) -> dict:
    """Analyze CVE using only NVD data (without local database)"""
    
    try:
        logger.info(f"Performing NVD-only analysis for {cve_id}")
        
        # Get CVE data from NVD
        nvd_service = NVDSearchService()
        nvd_result = await nvd_service.get_cve_details(cve_id)
        
        if not nvd_result["success"]:
            raise HTTPException(status_code=404, detail=f"CVE {cve_id} not found in NVD")
        
        cve_data = nvd_result["cve"]
        
        # Convert NVD format to analysis format
        analysis_data = {
            "cve_id": cve_data["cve_id"],
            "description": cve_data.get("description", ""),
            "cvss_v3_score": cve_data.get("cvss_v3_score"),
            "cvss_v3_vector": cve_data.get("cvss_v3_vector"),
            "severity_level": cve_data.get("severity_level"),
            "cwe_ids": cve_data.get("cwe_ids", []),
            "references": cve_data.get("references", [])
        }
        
        # Perform AI analysis
        ollama_service = OllamaService()
        result = await ollama_service.analyze_cve(analysis_data)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {result.get('error')}")
        
        return {
            "success": True,
            "cve_id": cve_id,
            "analysis": result["analysis"],
            "model_used": result["model_used"],
            "source": "NVD Live (Not Imported)",
            "auto_imported": False,
            "note": "Analysis performed on live NVD data. CVE was not imported to local database."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"NVD-only analysis error for {cve_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"NVD analysis failed: {str(e)}")

@router.get("/{cve_id}/analysis")
async def get_cve_analysis(
    cve_id: str,
    analysis_type: str = "comprehensive",
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get analysis results for a CVE"""
    
    cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
    if not cve:
        raise HTTPException(status_code=404, detail="CVE not found in local database")
    
    # TODO: Get analysis from analysis results table
    # For now, return basic info
    return {
        "cve_id": cve_id,
        "analysis": None,
        "message": "Analysis results retrieval not yet implemented"
    }

@router.post("/risk-assessment")
async def assess_risk(
    request: RiskAssessmentRequest,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Perform risk assessment for a CVE with auto-import support"""
    
    cve_id = request.cve_id.strip()
    
    # Check if CVE exists locally
    cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
    
    if not cve and request.auto_import:
        # Try auto-import
        import_result = await auto_import_cve_from_nvd(cve_id, db)
        if import_result["success"]:
            cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
    
    if not cve:
        raise HTTPException(status_code=404, detail="CVE not found and could not be imported")
    
    ollama_service = OllamaService()
    
    # Prepare context for risk assessment
    context = {
        "asset_criticality": request.asset_criticality,
        "environment": request.environment_context
    }
    
    # Perform risk assessment
    risk_result = await ollama_service.assess_risk(cve.to_dict(), context)
    
    if not risk_result["success"]:
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {risk_result.get('error')}")
    
    return {
        "cve_id": cve_id,
        "risk_assessment": risk_result["risk_assessment"],
        "model_used": risk_result["model_used"],
        "context": context
    }

@router.post("/{cve_id}/mitigations")
async def generate_mitigations(
    cve_id: str,
    auto_import: bool = True,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Generate mitigation strategies for a CVE with auto-import support"""
    
    # Check if CVE exists locally
    cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
    
    if not cve and auto_import:
        # Try auto-import
        import_result = await auto_import_cve_from_nvd(cve_id, db)
        if import_result["success"]:
            cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
    
    if not cve:
        raise HTTPException(status_code=404, detail="CVE not found and could not be imported")
    
    ollama_service = OllamaService()
    
    # For now, use CVE data directly for mitigation generation
    # TODO: Get existing analysis from analysis results table
    analysis_data = cve.to_dict()
    
    # Generate mitigations
    mitigation_result = await ollama_service.generate_mitigations(analysis_data)
    
    if not mitigation_result["success"]:
        raise HTTPException(status_code=500, detail=f"Mitigation generation failed: {mitigation_result.get('error')}")
    
    return {
        "cve_id": cve_id,
        "mitigations": mitigation_result["mitigations"],
        "model_used": mitigation_result["model_used"],
        "based_on": "CVE data"
    }

@router.get("/{cve_id}/attack-vectors")
async def get_attack_vectors(
    cve_id: str,
    auto_import: bool = True,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get detailed attack vector analysis for a CVE with auto-import support"""
    
    # Check if CVE exists locally
    cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
    
    if not cve and auto_import:
        # Try auto-import
        import_result = await auto_import_cve_from_nvd(cve_id, db)
        if import_result["success"]:
            cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
    
    if not cve:
        raise HTTPException(status_code=404, detail="CVE not found and could not be imported")
    
    # TODO: Get analysis from analysis results table
    # For now, return basic CVSS vector info
    return {
        "cve_id": cve_id,
        "attack_vectors": [],
        "cvss_vector": cve.cvss_v3_vector,
        "severity": cve.severity_level,
        "message": "Detailed attack vector analysis requires full AI analysis first"
    }

@router.post("/cve/analyze", response_model=AnalysisResponse)
async def analyze_cve_with_ai(
    request: CVEAnalysisRequest,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Analyze CVE using local AI models"""
    cve_data = None
    try:
        analysis_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Starting AI-powered CVE analysis for {request.cve_id}")
        
        # If CVE data not provided, fetch from our database or external API
        if request.cve_data:
            cve_data = request.cve_data
        else:
            cve_data = await _fetch_cve_data(request.cve_id)
        
        if not cve_data:
            raise ValueError(f"Could not fetch CVE data for {request.cve_id}")
        
        # Perform AI analysis
        ai_analysis = await ai_service.analyze_cve(cve_data)
        
        # Structure the analysis results
        results = {
            "vulnerability_summary": cve_data.get("description", "No description available") if cve_data else "No CVE data available",
            "severity_assessment": {
                "cvss_score": cve_data.get("severity", "Unknown") if cve_data else "Unknown",
                "ai_risk_score": ai_analysis.get("structured_analysis", {}).get("risk_score", 5),
                "severity_justification": "AI-generated risk assessment based on vulnerability characteristics"
            },
            "attack_vectors": _extract_attack_vectors(ai_analysis.get("response", "")),
            "affected_systems": cve_data.get("affected_products", []) if cve_data else [],
            "exploitation_analysis": {
                "likelihood": ai_analysis.get("structured_analysis", {}).get("exploitation_likelihood", "Medium"),
                "complexity": "Analysis pending",
                "prerequisites": "Standard system access"
            }
        }
        
        if request.include_recommendations:
            results["remediation"] = {
                "priority": ai_analysis.get("structured_analysis", {}).get("remediation_priority", "Medium"),
                "immediate_actions": ["Apply security patches", "Review system configurations"],
                "long_term_strategies": ["Implement defense in depth", "Regular security assessments"]
            }
        
        # Store analysis result
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        analysis_result = AnalysisResponse(
            analysis_id=analysis_id,
            status="completed" if ai_analysis["success"] else "completed_with_warnings",
            cve_id=request.cve_id,
            analysis_type=request.analysis_type,
            results=results,
            ai_insights={
                "model_confidence": 0.85 if ai_analysis["success"] else 0.5,
                "analysis_method": "Local LLM Analysis",
                "key_findings": _extract_key_findings(ai_analysis.get("response", "")),
                "ai_model": ai_analysis.get("model", "unknown"),
                "processing_time": ai_analysis.get("processing_time", 0)
            },
            processing_time=processing_time,
            created_at=start_time,
            model_used=ai_analysis.get("model", "fallback")
        )
        
        analysis_results[analysis_id] = analysis_result
        
        logger.info(f"CVE analysis completed: {analysis_id} in {processing_time:.2f}s")
        return analysis_result
        
    except ValueError as e:
        logger.error(f"CVE data error for {request.cve_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"CVE data not found: {str(e)}")
    except Exception as e:
        logger.error(f"Error in CVE analysis for {request.cve_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"CVE analysis failed: {str(e)}")

@router.post("/code/analyze", response_model=AnalysisResponse)
async def analyze_code_with_ai(
    request: CodeAnalysisRequest,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Analyze code for vulnerabilities using local AI"""
    try:
        analysis_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Starting AI-powered code analysis for {len(request.code)} characters")
        
        # Prepare context for analysis
        context = f"Programming Language: {request.language or 'Unknown'}"
        if request.context:
            context += f"\nAdditional Context: {request.context}"
        
        # Perform AI code analysis
        ai_analysis = await ai_service.analyze_code(
            code=request.code,
            context=context
        )
        
        # Structure the analysis results
        results = {
            "code_summary": {
                "lines_analyzed": len(request.code.split('\n')),
                "language": request.language or "Unknown",
                "analysis_scope": "Full code security review"
            },
            "vulnerabilities_found": _parse_vulnerabilities(ai_analysis.get("response", "")),
            "security_score": _calculate_security_score(ai_analysis.get("response", "")),
            "recommendations": _extract_recommendations(ai_analysis.get("response", ""))
        }
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        analysis_result = AnalysisResponse(
            analysis_id=analysis_id,
            status="completed" if ai_analysis["success"] else "completed_with_warnings",
            cve_id=None,
            analysis_type="code_vulnerability",
            results=results,
            ai_insights={
                "model_confidence": 0.8 if ai_analysis["success"] else 0.4,
                "analysis_method": "Local LLM Code Analysis",
                "ai_model": ai_analysis.get("model", "unknown"),
                "processing_time": ai_analysis.get("processing_time", 0)
            },
            processing_time=processing_time,
            created_at=start_time,
            model_used=ai_analysis.get("model", "fallback")
        )
        
        analysis_results[analysis_id] = analysis_result
        
        logger.info(f"Code analysis completed: {analysis_id} in {processing_time:.2f}s")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in code analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Code analysis failed")

@router.get("/results/{analysis_id}")
async def get_analysis_result(
    analysis_id: str,
    auth: str = Depends(get_auth_dependency())
):
    """Get analysis result by ID"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_results[analysis_id]

@router.get("/results")
async def list_analysis_results(
    limit: int = 50,
    auth: str = Depends(get_auth_dependency())
):
    """List all analysis results"""
    results = list(analysis_results.values())
    results.sort(key=lambda x: x.created_at, reverse=True)
    return {"results": results[:limit], "total": len(results)}

@router.get("/ai/status")
async def get_ai_service_status(auth: str = Depends(get_auth_dependency())):
    """Get AI service status and capabilities"""
    stats = await ai_service.get_service_stats()
    return {
        "ai_service": stats,
        "supported_analysis_types": [
            "cve_analysis",
            "code_vulnerability",
            "threat_intelligence"
        ],
        "features": [
            "Local LLM Processing",
            "Multi-model Support", 
            "Caching for Performance",
            "Fallback Responses"
        ]
    }

@router.post("/ai/initialize")
async def initialize_ai_service(auth: str = Depends(get_admin_dependency())):
    """Initialize or reinitialize the AI service"""
    try:
        success = await ai_service.initialize()
        return {
            "success": success,
            "message": "AI service initialized successfully" if success else "AI service initialized with fallback mode",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error initializing AI service: {str(e)}")
        raise HTTPException(status_code=500, detail="AI service initialization failed")

# Helper functions
async def _fetch_cve_data(cve_id: str) -> Dict[str, Any]:
    """Fetch CVE data from database or external API"""
    try:
        # Try to get from database first
        from app.database import get_db
        from app.models.cve import CVE
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
            if cve:
                return cve.to_dict()
        finally:
            db.close()
        
        # If not found in database, try NVD
        from app.services.nvd_search_service import NVDSearchService
        nvd_service = NVDSearchService()
        nvd_result = await nvd_service.get_cve_details(cve_id)
        
        if nvd_result.get("success") and nvd_result.get("cve"):
            return nvd_result["cve"]
        
        # Fallback to mock data if nothing found
        logger.warning(f"CVE {cve_id} not found in database or NVD, using fallback data")
    return {
            "cve_id": cve_id,
        "description": f"Security vulnerability {cve_id} - detailed analysis required",
            "severity": "Unknown",
            "cvss_v3_score": None,
            "published_date": "Unknown",
            "cwe_ids": [],
            "affected_products": []
        }
        
    except Exception as e:
        logger.error(f"Error fetching CVE data for {cve_id}: {str(e)}")
        # Return minimal fallback data
        return {
            "cve_id": cve_id,
            "description": f"CVE {cve_id} - data fetch failed",
            "severity": "Unknown",
            "cvss_v3_score": None,
            "published_date": "Unknown",
            "cwe_ids": [],
            "affected_products": []
    }

def _extract_attack_vectors(ai_response: str) -> List[str]:
    """Extract attack vectors from AI response"""
    vectors = []
    response_lower = ai_response.lower()
    
    if "remote" in response_lower:
        vectors.append("Remote exploitation")
    if "local" in response_lower:
        vectors.append("Local privilege escalation")
    if "web" in response_lower or "http" in response_lower:
        vectors.append("Web application attack")
    if "injection" in response_lower:
        vectors.append("Code injection")
    
    return vectors if vectors else ["General attack vector"]

def _extract_key_findings(ai_response: str) -> List[str]:
    """Extract key findings from AI analysis"""
    findings = []
    if "critical" in ai_response.lower():
        findings.append("Critical vulnerability identified")
    if "exploit" in ai_response.lower():
        findings.append("Exploitation potential detected")
    if "patch" in ai_response.lower():
        findings.append("Patch availability noted")
    
    return findings if findings else ["Analysis completed"]

def _parse_vulnerabilities(ai_response: str) -> List[Dict[str, Any]]:
    """Parse vulnerabilities from code analysis response"""
    vulnerabilities = []
    
    # Simple parsing - in production this would be more sophisticated
    if "sql injection" in ai_response.lower():
        vulnerabilities.append({
            "type": "SQL Injection",
            "severity": "High",
            "description": "Potential SQL injection vulnerability detected",
            "line_number": "Unknown"
        })
    
    if "xss" in ai_response.lower() or "cross-site" in ai_response.lower():
        vulnerabilities.append({
            "type": "Cross-Site Scripting (XSS)",
            "severity": "Medium", 
            "description": "Potential XSS vulnerability detected",
            "line_number": "Unknown"
        })
    
    if "buffer overflow" in ai_response.lower():
        vulnerabilities.append({
            "type": "Buffer Overflow",
            "severity": "High",
            "description": "Potential buffer overflow vulnerability detected",
            "line_number": "Unknown"
        })
    
    return vulnerabilities

def _calculate_security_score(ai_response: str) -> int:
    """Calculate security score based on AI analysis"""
    score = 100  # Start with perfect score
    
    response_lower = ai_response.lower()
    if "critical" in response_lower:
        score -= 40
    elif "high" in response_lower:
        score -= 25
    elif "medium" in response_lower:
        score -= 15
    elif "low" in response_lower:
        score -= 5
    
    return max(score, 0)

def _extract_recommendations(ai_response: str) -> List[str]:
    """Extract security recommendations from AI response"""
    recommendations = []
    
    response_lower = ai_response.lower()
    if "sanitize" in response_lower or "validate" in response_lower:
        recommendations.append("Implement input validation and sanitization")
    if "encode" in response_lower:
        recommendations.append("Use proper output encoding")
    if "parameterized" in response_lower or "prepared" in response_lower:
        recommendations.append("Use parameterized queries")
    if "authentication" in response_lower:
        recommendations.append("Strengthen authentication mechanisms")
    
    return recommendations if recommendations else ["Follow secure coding best practices"]
