#!/usr/bin/env python3
"""
CVE Analysis Platform - Models and Services Setup
This script creates the database models, services, and API routes.
"""

import os
from pathlib import Path

def create_file(filepath, content):
    """Create a file with the given content"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created: {filepath}")

def setup_models_and_services():
    """Create models, services, and API routes"""
    
    print("🔧 Setting up Models, Services, and API Routes")
    print("=" * 50)
    
    files = {
        
        # CVE Model
        "app/models/cve.py": """from sqlalchemy import Column, String, DateTime, Float, JSON, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from datetime import datetime

class CVE(Base):
    __tablename__ = "cves"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cve_id = Column(String(20), unique=True, nullable=False, index=True)
    published_date = Column(DateTime)
    modified_date = Column(DateTime)
    description = Column(Text)
    cvss_v3_score = Column(Float)
    cvss_v3_vector = Column(String(100))
    severity_level = Column(String(10))
    cwe_ids = Column(JSON)
    affected_products = Column(JSON)
    references = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "cve_id": self.cve_id,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "modified_date": self.modified_date.isoformat() if self.modified_date else None,
            "description": self.description,
            "cvss_v3_score": self.cvss_v3_score,
            "cvss_v3_vector": self.cvss_v3_vector,
            "severity_level": self.severity_level,
            "cwe_ids": self.cwe_ids,
            "affected_products": self.affected_products,
            "references": self.references,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
""",

        # Analysis Model
        "app/models/analysis.py": """from sqlalchemy import Column, String, DateTime, Integer, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

class Analysis(Base):
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cve_id = Column(UUID(as_uuid=True), ForeignKey("cves.id"), nullable=False)
    attack_vectors = Column(JSON)
    exploitation_complexity = Column(String(10))
    privilege_required = Column(String(10))
    user_interaction = Column(String(10))
    impact_analysis = Column(JSON)
    mitigation_strategies = Column(JSON)
    risk_score = Column(Integer)
    confidence_score = Column(Integer)
    ai_model_used = Column(String(50))
    analysis_type = Column(String(20))
    raw_analysis = Column(Text)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    cve = relationship("CVE", backref="analyses")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "cve_id": str(self.cve_id),
            "attack_vectors": self.attack_vectors,
            "exploitation_complexity": self.exploitation_complexity,
            "privilege_required": self.privilege_required,
            "user_interaction": self.user_interaction,
            "impact_analysis": self.impact_analysis,
            "mitigation_strategies": self.mitigation_strategies,
            "risk_score": self.risk_score,
            "confidence_score": self.confidence_score,
            "ai_model_used": self.ai_model_used,
            "analysis_type": self.analysis_type,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None
        }

class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cve_id = Column(UUID(as_uuid=True), ForeignKey("cves.id"), nullable=False)
    exploit_available = Column(JSON)
    exploit_maturity = Column(String(20))
    attack_patterns = Column(JSON)
    iocs = Column(JSON)
    threat_actors = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    cve = relationship("CVE", backref="threat_intel")
""",

        # Ollama Service
        "app/services/ollama_service.py": """import aiohttp
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
        \"\"\"Check if Ollama service is available\"\"\"
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
        \"\"\"Generate response from Ollama model\"\"\"
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
                        result = await response.json()
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
        \"\"\"Analyze CVE using appropriate model\"\"\"
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
""",

        # CVE Analysis Prompts
        "app/ai/prompts/cve_analysis.py": """CVE_ANALYSIS_PROMPT = '''
You are a cybersecurity expert analyzing CVE vulnerabilities. Provide a comprehensive technical analysis of the following CVE.

CVE Information:
- CVE ID: {cve_id}
- Description: {description}
- CVSS v3 Score: {cvss_score}
- CVSS v3 Vector: {cvss_vector}
- CWE IDs: {cwe_ids}

Please analyze this vulnerability and provide a structured JSON response with the following fields:

{{
  "vulnerability_type": "Brief classification of the vulnerability",
  "attack_complexity": "Low|Medium|High",
  "attack_vectors": [
    {{
      "vector": "Vector name (e.g., Network, Local, Physical)",
      "description": "How this attack vector can be exploited",
      "requirements": ["List of requirements for this vector"]
    }}
  ],
  "impact_assessment": {{
    "confidentiality": "None|Low|High",
    "integrity": "None|Low|High", 
    "availability": "None|Low|High",
    "scope": "Unchanged|Changed",
    "description": "Detailed impact description"
  }},
  "exploitability": {{
    "ease_of_exploitation": "Low|Medium|High",
    "exploit_availability": "Unknown|Theoretical|Proof of Concept|Functional|High",
    "prerequisites": ["List of prerequisites for exploitation"],
    "technical_requirements": ["Technical skills/tools needed"]
  }},
  "business_impact": {{
    "severity": "Critical|High|Medium|Low",
    "potential_damage": ["List of potential business impacts"],
    "affected_assets": ["Types of assets at risk"]
  }},
  "confidence_score": 85,
  "additional_notes": "Any additional technical insights or concerns"
}}

Provide only the JSON response, no additional text.
'''
""",

        # Simple CVE Routes for now
        "app/api/routes/cve.py": """from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.cve import CVE
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class CVEResponse(BaseModel):
    id: str
    cve_id: str
    description: Optional[str]
    cvss_v3_score: Optional[float]
    severity_level: Optional[str]
    published_date: Optional[datetime]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[CVEResponse])
async def get_cves(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    \"\"\"Get list of CVEs with optional filtering\"\"\"
    query = db.query(CVE)
    
    if severity:
        query = query.filter(CVE.severity_level == severity.upper())
    
    cves = query.offset(skip).limit(limit).all()
    return [CVEResponse.from_orm(cve) for cve in cves]

@router.get("/{cve_id}")
async def get_cve(cve_id: str, db: Session = Depends(get_db)):
    \"\"\"Get specific CVE by ID\"\"\"
    cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
    if not cve:
        raise HTTPException(status_code=404, detail="CVE not found")
    
    return cve.to_dict()
""",

        # Simple Analysis Routes
        "app/api/routes/analysis.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cve import CVE
from app.services.ollama_service import OllamaService
from pydantic import BaseModel

router = APIRouter()

class AnalysisRequest(BaseModel):
    cve_id: str
    analysis_type: str = "comprehensive"

@router.post("/analyze")
async def analyze_cve(request: AnalysisRequest, db: Session = Depends(get_db)):
    \"\"\"Analyze a CVE using AI models\"\"\"
    
    # Check if CVE exists
    cve = db.query(CVE).filter(CVE.cve_id == request.cve_id).first()
    if not cve:
        raise HTTPException(status_code=404, detail="CVE not found")
    
    # Perform AI analysis
    ollama_service = OllamaService()
    result = await ollama_service.analyze_cve(cve.to_dict())
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {result.get('error')}")
    
    return {
        "cve_id": request.cve_id,
        "analysis": result["analysis"],
        "model_used": result["model_used"]
    }
""",

        # Simple Dashboard Routes
        "app/api/routes/dashboard.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cve import CVE

router = APIRouter()

@router.get("/metrics")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    \"\"\"Get high-level dashboard metrics\"\"\"
    
    total_count = db.query(CVE).count()
    critical_count = db.query(CVE).filter(CVE.severity_level == "CRITICAL").count()
    
    return {
        "total_count": total_count,
        "critical_count": critical_count,
        "high_count": db.query(CVE).filter(CVE.severity_level == "HIGH").count(),
        "medium_count": db.query(CVE).filter(CVE.severity_level == "MEDIUM").count(),
        "low_count": db.query(CVE).filter(CVE.severity_level == "LOW").count(),
        "recent_count": 0,  # TODO: Implement recent count
        "analysis_count": 0  # TODO: Implement analysis count
    }
""",

        # Database initialization script
        "scripts/init_db.py": """#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models.cve import CVE
from app.models.analysis import Analysis, ThreatIntelligence
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    \"\"\"Initialize the database with all tables\"\"\"
    
    try:
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully!")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Created tables: {', '.join(tables)}")
        
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
""",

        # Model loading script
        "scripts/load_models.py": """#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ollama_service import OllamaService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_models():
    \"\"\"Load and verify AI models in Ollama\"\"\"
    
    try:
        logger.info("Connecting to Ollama service...")
        
        ollama_service = OllamaService()
        
        # Check health
        is_healthy = await ollama_service.health_check()
        if not is_healthy:
            logger.error("Ollama service is not available")
            return False
        
        logger.info("Ollama service is healthy!")
        
        # Test each model
        models_to_test = [
            ("llama3.1:8b", "general"),
            ("gemma2:9b", "technical"),
            ("codellama:7b", "code")
        ]
        
        for model, purpose in models_to_test:
            logger.info(f"Testing {model} ({purpose} analysis)...")
            
            test_prompt = "Test prompt for model verification"
            
            try:
                response = await ollama_service.generate_response(test_prompt, model)
                
                if response["success"]:
                    logger.info(f"✓ {model} is working correctly")
                else:
                    logger.error(f"✗ {model} failed: {response.get('error')}")
                    
            except Exception as e:
                logger.error(f"✗ Error testing {model}: {e}")
        
        logger.info("Model verification completed!")
        return True
        
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(load_models())
    sys.exit(0 if success else 1)
""",
    }
    
    # Create all files
    for filepath, content in files.items():
        create_file(filepath, content)
    
    print(f"\n✅ Created {len(files)} model and service files")
    print("🔧 Core application logic is ready!")

if __name__ == "__main__":
    setup_models_and_services()
