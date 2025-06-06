#!/bin/bash

echo "🚀 Setting up Hybrid CVE Search Enhancement"
echo "==========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Step 1: Create NVD Search Service
print_info "Creating NVD Search Service..."

cat > app/services/nvd_search_service.py << 'EOF'
#!/usr/bin/env python3
"""
app/services/nvd_search_service.py
Complete NVD Live Search Service
"""

import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class NVDSearchService:
    """Service for searching CVEs directly from NVD API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.api_key = api_key or getattr(settings, 'nvd_api_key', None)
        self.rate_limit_delay = 6 if not self.api_key else 0.6
    
    async def search_live(self, 
                         cve_id: Optional[str] = None,
                         keyword: Optional[str] = None,
                         severity: Optional[str] = None,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         limit: int = 20) -> Dict[str, Any]:
        """Search CVEs directly from NVD API"""
        
        try:
            logger.info(f"Searching NVD for: cve_id={cve_id}, keyword={keyword}, severity={severity}")
            
            # Build search parameters
            params = {
                "resultsPerPage": min(limit, 100),
                "startIndex": 0
            }
            
            if cve_id and cve_id.strip():
                params["cveId"] = cve_id.strip()
            
            if keyword and keyword.strip():
                params["keywordSearch"] = keyword.strip()
            
            if start_date:
                params["pubStartDate"] = start_date
            if end_date:
                params["pubEndDate"] = end_date
            
            if severity and severity.upper() in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                params["cvssV3Severity"] = severity.upper()
            
            headers = {
                "Accept": "application/json",
                "User-Agent": "CVE-Analysis-Platform/1.0"
            }
            if self.api_key:
                headers["apiKey"] = self.api_key
            
            await asyncio.sleep(self.rate_limit_delay)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    logger.info(f"NVD API response status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        formatted_results = self._format_nvd_results(data)
                        
                        return {
                            "success": True,
                            "source": "NVD Live",
                            "total_results": data.get("totalResults", 0),
                            "results": formatted_results,
                            "search_params": params,
                            "rate_limited": False
                        }
                    
                    elif response.status == 403:
                        return {
                            "success": False,
                            "error": "NVD API access forbidden. Consider getting a free API key from https://nvd.nist.gov/developers/request-an-api-key",
                            "source": "NVD Live",
                            "rate_limited": True
                        }
                    
                    elif response.status == 429:
                        return {
                            "success": False,
                            "error": "NVD API rate limited. Please wait and try again.",
                            "source": "NVD Live",
                            "rate_limited": True
                        }
                    
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"NVD API error {response.status}: {error_text}",
                            "source": "NVD Live",
                            "rate_limited": False
                        }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "NVD API request timeout",
                "source": "NVD Live",
                "rate_limited": False
            }
        except Exception as e:
            logger.error(f"NVD search error: {e}")
            return {
                "success": False,
                "error": f"NVD search failed: {str(e)}",
                "source": "NVD Live",
                "rate_limited": False
            }
    
    def _format_nvd_results(self, nvd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format NVD API response to match our CVE format"""
        
        formatted_cves = []
        
        for vuln in nvd_data.get("vulnerabilities", []):
            cve_data = vuln.get("cve", {})
            
            try:
                cve_id = cve_data.get("id", "Unknown")
                
                descriptions = cve_data.get("descriptions", [])
                description = "No description available"
                for desc in descriptions:
                    if desc.get("lang") == "en":
                        description = desc.get("value", "")
                        break
                
                published_date = cve_data.get("published", "")
                modified_date = cve_data.get("lastModified", "")
                
                cvss_v3_score = None
                cvss_v3_vector = None
                severity_level = "UNKNOWN"
                
                metrics = cve_data.get("metrics", {})
                cvss_v3_data = metrics.get("cvssMetricV31", []) or metrics.get("cvssMetricV30", [])
                
                if cvss_v3_data:
                    cvss_info = cvss_v3_data[0].get("cvssData", {})
                    cvss_v3_score = cvss_info.get("baseScore")
                    cvss_v3_vector = cvss_info.get("vectorString")
                    severity_level = cvss_info.get("baseSeverity", "UNKNOWN")
                
                cwe_ids = []
                weaknesses = cve_data.get("weaknesses", [])
                for weakness in weaknesses:
                    for desc in weakness.get("description", []):
                        if desc.get("lang") == "en":
                            cwe_value = desc.get("value", "")
                            if cwe_value and cwe_value not in cwe_ids:
                                cwe_ids.append(cwe_value)
                
                references = []
                ref_data = cve_data.get("references", [])
                for ref in ref_data[:3]:
                    references.append({
                        "url": ref.get("url", ""),
                        "source": ref.get("source", ""),
                        "tags": ref.get("tags", [])
                    })
                
                try:
                    pub_date_formatted = datetime.fromisoformat(published_date.replace("Z", "+00:00")).strftime("%Y-%m-%d") if published_date else "Unknown"
                except:
                    pub_date_formatted = published_date[:10] if len(published_date) >= 10 else "Unknown"
                
                formatted_cve = {
                    "id": f"nvd-{cve_id}",
                    "cve_id": cve_id,
                    "description": description[:300] + "..." if len(description) > 300 else description,
                    "published_date": pub_date_formatted,
                    "modified_date": modified_date,
                    "cvss_v3_score": cvss_v3_score,
                    "cvss_v3_vector": cvss_v3_vector,
                    "severity_level": severity_level,
                    "cwe_ids": cwe_ids,
                    "references": references,
                    "source": "NVD Live",
                    "can_import": True,
                    "nvd_link": f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                }
                
                formatted_cves.append(formatted_cve)
                
            except Exception as e:
                logger.error(f"Error formatting CVE {cve_data.get('id', 'unknown')}: {e}")
                continue
        
        return formatted_cves
    
    async def get_cve_details(self, cve_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific CVE"""
        
        result = await self.search_live(cve_id=cve_id, limit=1)
        
        if result["success"] and result["results"]:
            return {
                "success": True,
                "cve": result["results"][0]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "CVE not found")
            }
EOF

print_status "NVD Search Service created"

# Step 2: Update CVE Routes
print_info "Updating CVE Routes..."

cat > app/api/routes/cve.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.models.cve import CVE
from app.services.nvd_search_service import NVDSearchService
from pydantic import BaseModel
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchRequest(BaseModel):
    query: Optional[str] = None
    severity: Optional[str] = None
    search_type: str = "both"
    limit: int = 20

class ImportRequest(BaseModel):
    cve_id: str
    force: bool = False

@router.post("/search")
async def search_cves_hybrid(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Hybrid CVE search supporting both local database and live NVD"""
    
    logger.info(f"Hybrid search: query='{request.query}', type='{request.search_type}', severity='{request.severity}'")
    
    results = {
        "local_results": [],
        "nvd_results": [],
        "total_local": 0,
        "total_nvd": 0,
        "search_type": request.search_type,
        "query": request.query,
        "severity": request.severity,
        "success": True,
        "errors": []
    }
    
    # Search local database
    if request.search_type in ["local", "both"]:
        try:
            logger.info("Searching local database...")
            query = db.query(CVE)
            
            if request.query and request.query.strip():
                search_term = f"%{request.query.strip()}%"
                query = query.filter(
                    or_(
                        CVE.cve_id.ilike(search_term),
                        CVE.description.ilike(search_term)
                    )
                )
            
            if request.severity and request.severity.upper() in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                query = query.filter(CVE.severity_level == request.severity.upper())
            
            local_cves = query.order_by(CVE.published_date.desc()).limit(request.limit).all()
            
            for cve in local_cves:
                cve_dict = cve.to_dict()
                cve_dict.update({
                    "source": "Local Database",
                    "can_import": False,
                    "nvd_link": f"https://nvd.nist.gov/vuln/detail/{cve.cve_id}"
                })
                results["local_results"].append(cve_dict)
            
            results["total_local"] = len(results["local_results"])
            logger.info(f"Found {results['total_local']} local results")
            
        except Exception as e:
            error_msg = f"Local search error: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
    
    # Search NVD live
    if request.search_type in ["nvd", "both"]:
        try:
            logger.info("Searching NVD live...")
            nvd_service = NVDSearchService()
            
            cve_id = None
            keyword = None
            
            if request.query and request.query.strip():
                query_clean = request.query.strip()
                if query_clean.upper().startswith("CVE-"):
                    cve_id = query_clean
                else:
                    keyword = query_clean
            
            nvd_result = await nvd_service.search_live(
                cve_id=cve_id,
                keyword=keyword,
                severity=request.severity,
                limit=request.limit
            )
            
            if nvd_result["success"]:
                results["nvd_results"] = nvd_result["results"]
                results["total_nvd"] = len(nvd_result["results"])
                logger.info(f"Found {results['total_nvd']} NVD results")
                
                for nvd_cve in results["nvd_results"]:
                    existing = db.query(CVE).filter(CVE.cve_id == nvd_cve["cve_id"]).first()
                    if existing:
                        nvd_cve["can_import"] = False
                        nvd_cve["import_status"] = "Already in local database"
                    else:
                        nvd_cve["can_import"] = True
                        nvd_cve["import_status"] = "Available to import"
            else:
                error_msg = f"NVD search error: {nvd_result['error']}"
                logger.warning(error_msg)
                results["errors"].append(error_msg)
                results["nvd_rate_limited"] = nvd_result.get("rate_limited", False)
                
        except Exception as e:
            error_msg = f"NVD search error: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
    
    total_results = results["total_local"] + results["total_nvd"]
    results["total_results"] = total_results
    
    if total_results == 0 and not results["errors"]:
        results["message"] = "No CVEs found matching your criteria"
    elif results["errors"]:
        results["success"] = False
    
    return results

@router.post("/import-from-nvd")
async def import_cve_from_nvd(
    request: ImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Import a specific CVE from NVD into local database"""
    
    try:
        cve_id = request.cve_id.strip()
        logger.info(f"Importing CVE {cve_id} from NVD")
        
        existing = db.query(CVE).filter(CVE.cve_id == cve_id).first()
        if existing and not request.force:
            return {
                "success": False,
                "message": f"{cve_id} already exists in local database",
                "cve_id": cve_id
            }
        
        nvd_service = NVDSearchService()
        nvd_result = await nvd_service.get_cve_details(cve_id)
        
        if not nvd_result["success"]:
            return {
                "success": False,
                "message": f"CVE {cve_id} not found in NVD: {nvd_result.get('error')}",
                "cve_id": cve_id
            }
        
        cve_data = nvd_result["cve"]
        
        try:
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
            
            if existing and request.force:
                existing.description = cve_data.get("description")
                existing.published_date = published_date
                existing.modified_date = modified_date
                existing.cvss_v3_score = cve_data.get("cvss_v3_score")
                existing.cvss_v3_vector = cve_data.get("cvss_v3_vector")
                existing.severity_level = cve_data.get("severity_level")
                existing.cwe_ids = cve_data.get("cwe_ids", [])
                existing.references = cve_data.get("references", [])
                existing.updated_at = datetime.utcnow()
                
                db.commit()
                
                return {
                    "success": True,
                    "message": f"CVE {cve_id} updated successfully",
                    "cve": existing.to_dict(),
                    "action": "updated"
                }
            else:
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
                    "message": f"CVE {cve_id} imported successfully",
                    "cve": new_cve.to_dict(),
                    "action": "imported"
                }
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating CVE object: {e}")
            return {
                "success": False,
                "message": f"Failed to create CVE record: {str(e)}",
                "cve_id": cve_id
            }
        
    except Exception as e:
        logger.error(f"Import error: {e}")
        return {
            "success": False,
            "message": f"Import failed: {str(e)}",
            "cve_id": request.cve_id
        }

@router.get("/")
async def get_cves(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get CVEs from local database"""
    
    query = db.query(CVE)
    
    if severity and severity.upper() in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        query = query.filter(CVE.severity_level == severity.upper())
    
    total = query.count()
    cves = query.order_by(CVE.published_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "results": [
            {
                **cve.to_dict(),
                "source": "Local Database",
                "can_import": False,
                "nvd_link": f"https://nvd.nist.gov/vuln/detail/{cve.cve_id}"
            } for cve in cves
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
        "source": "Local Database"
    }

@router.get("/{cve_id}")
async def get_cve(cve_id: str, db: Session = Depends(get_db)):
    """Get specific CVE by ID from local database"""
    cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
    if not cve:
        raise HTTPException(status_code=404, detail="CVE not found in local database")
    
    result = cve.to_dict()
    result.update({
        "source": "Local Database",
        "nvd_link": f"https://nvd.nist.gov/vuln/detail/{cve_id}"
    })
    
    return result

@router.get("/stats/summary")
async def get_cve_stats(db: Session = Depends(get_db)):
    """Get CVE statistics from local database"""
    
    total = db.query(CVE).count()
    critical = db.query(CVE).filter(CVE.severity_level == "CRITICAL").count()
    high = db.query(CVE).filter(CVE.severity_level == "HIGH").count()
    medium = db.query(CVE).filter(CVE.severity_level == "MEDIUM").count()
    low = db.query(CVE).filter(CVE.severity_level == "LOW").count()
    
    return {
        "total_cves": total,
        "by_severity": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        },
        "source": "Local Database"
    }
EOF

print_status "CVE Routes updated"

# Step 3: Test the setup
print_info "Testing imports..."

cd "$(dirname "$0")"
source venv/bin/activate

python -c "
try:
    from app.services.nvd_search_service import NVDSearchService
    print('✅ NVD Search Service imports successfully')
except Exception as e:
    print(f'❌ NVD Search Service import error: {e}')

try:
    from app.api.routes.cve import router
    print('✅ Enhanced CVE Routes import successfully')
except Exception as e:
    print(f'❌ CVE Routes import error: {e}')
"

print_status "Hybrid search backend is ready!"

echo ""
echo "🎯 Next Steps:"
echo "1. Update your frontend HTML to include the new search interface"
echo "2. Update your JavaScript file with enhanced search functions"
echo "3. Restart your application: python run.py"
echo "4. Test the hybrid search functionality"

echo ""
echo "📝 Manual frontend updates needed:"
echo "- Update app/static/frontend/index.html with enhanced search section"
echo "- Update app/static/frontend/app.js with hybrid search JavaScript"
echo ""
echo "🔧 Quick test command:"
echo "python -c \"import asyncio; from app.services.nvd_search_service import NVDSearchService; print('NVD Service ready!')\""
EOF

chmod +x hybrid_setup.sh

print_status "Hybrid setup script created"

print_info "Run: ./hybrid_setup.sh"
