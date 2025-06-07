from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc, func
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models.cve import CVE
from app.services.nvd_search_service import NVDSearchService
from app.core.security import get_auth_dependency, get_admin_dependency
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import asyncio
import logging
import hashlib
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory cache for search results (would use Redis in production)
search_cache = {}
CACHE_TTL = 300  # 5 minutes

class SearchRequest(BaseModel):
    query: Optional[str] = None
    severity: Optional[str] = None
    search_type: str = "both"
    limit: int = 20

class ImportRequest(BaseModel):
    cve_id: str
    force: bool = False

class AdvancedSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query (CVE ID, keywords, or description)")
    severity: Optional[List[str]] = Field(None, description="Severity levels to filter by")
    search_type: str = Field("both", description="Search type: local, nvd, or both")
    limit: int = Field(20, ge=1, le=100, description="Number of results to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")
    
    # Advanced filters
    date_from: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    cvss_min: Optional[float] = Field(None, ge=0.0, le=10.0, description="Minimum CVSS score")
    cvss_max: Optional[float] = Field(None, ge=0.0, le=10.0, description="Maximum CVSS score")
    cwe_ids: Optional[List[str]] = Field(None, description="CWE IDs to filter by")
    vendor: Optional[str] = Field(None, description="Vendor name filter")
    product: Optional[str] = Field(None, description="Product name filter")
    
    # Sorting options
    sort_by: str = Field("published_date", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order: asc or desc")
    
    # Search options
    exact_match: bool = Field(False, description="Use exact matching for queries")
    include_descriptions: bool = Field(True, description="Include descriptions in search")
    
    # Response options
    include_details: bool = Field(False, description="Include detailed CVE information")
    include_references: bool = Field(False, description="Include reference links")

class BulkImportRequest(BaseModel):
    cve_ids: List[str] = Field(..., description="List of CVE IDs to import")
    force: bool = Field(False, description="Force import even if CVE exists")
    priority: str = Field("normal", description="Import priority: low, normal, high")

class SearchHistoryItem(BaseModel):
    search_id: str
    query: str
    parameters: Dict[str, Any]
    results_count: int
    executed_at: datetime
    execution_time_ms: int

class SavedSearchRequest(BaseModel):
    name: str = Field(..., description="Name for the saved search")
    description: Optional[str] = Field(None, description="Description of the saved search")
    parameters: AdvancedSearchRequest

# In-memory storage for search history and saved searches
search_history = []
saved_searches = {}

@router.post("/search/advanced")
async def advanced_search_cves(
    request: AdvancedSearchRequest,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Enhanced CVE search with advanced filtering, sorting, and caching"""
    
    start_time = datetime.now()
    
    # Generate cache key
    cache_key = hashlib.md5(
        json.dumps(request.dict(), sort_keys=True, default=str).encode()
    ).hexdigest()
    
    # Check cache first
    if cache_key in search_cache:
        cached_result = search_cache[cache_key]
        if datetime.now() - cached_result["timestamp"] < timedelta(seconds=CACHE_TTL):
            logger.info(f"Returning cached results for search: {cache_key[:8]}")
            cached_result["data"]["cached"] = True
            cached_result["data"]["cache_age_seconds"] = int(
                (datetime.now() - cached_result["timestamp"]).total_seconds()
            )
            return cached_result["data"]
    
    logger.info(f"Advanced search: query='{request.query}', filters={request.dict()}")
    
    results = {
        "local_results": [],
        "nvd_results": [],
        "pagination": {
            "offset": request.offset,
            "limit": request.limit,
            "total_local": 0,
            "total_nvd": 0,
            "has_more_local": False,
            "has_more_nvd": False
        },
        "filters_applied": {
            "search_type": request.search_type,
            "date_range": bool(request.date_from or request.date_to),
            "cvss_range": bool(request.cvss_min is not None or request.cvss_max is not None),
            "severity_filter": bool(request.severity),
            "cwe_filter": bool(request.cwe_ids),
            "vendor_filter": bool(request.vendor),
            "product_filter": bool(request.product)
        },
        "performance": {
            "search_id": cache_key[:8],
            "cached": False
        },
        "success": True,
        "errors": [],
        "warnings": []
    }
    
    # Search local database with advanced filters
    if request.search_type in ["local", "both"]:
        try:
            local_results, total_local = await _search_local_advanced(db, request)
            results["local_results"] = local_results
            results["pagination"]["total_local"] = total_local
            results["pagination"]["has_more_local"] = (
                request.offset + len(local_results) < total_local
            )
            
        except Exception as e:
            error_msg = f"Local search error: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
    
    # Search NVD with advanced parameters
    if request.search_type in ["nvd", "both"]:
        try:
            nvd_service = NVDSearchService()
            nvd_results = await _search_nvd_advanced(nvd_service, request, db)
            results["nvd_results"] = nvd_results.get("results", [])
            results["pagination"]["total_nvd"] = len(nvd_results.get("results", []))
            
            if nvd_results.get("errors"):
                results["errors"].extend(nvd_results["errors"])
            if nvd_results.get("warnings"):
                results["warnings"].extend(nvd_results["warnings"])
                
        except Exception as e:
            error_msg = f"NVD search error: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
    
    # Calculate execution time
    execution_time = (datetime.now() - start_time).total_seconds() * 1000
    results["performance"]["execution_time_ms"] = int(execution_time)
    
    # Cache results
    search_cache[cache_key] = {
        "data": results,
        "timestamp": datetime.now()
    }
    
    # Add to search history
    search_history.append(SearchHistoryItem(
        search_id=cache_key[:8],
        query=request.query or "",
        parameters=request.dict(),
        results_count=len(results["local_results"]) + len(results["nvd_results"]),
        executed_at=start_time,
        execution_time_ms=int(execution_time)
    ))
    
    # Keep only last 100 searches
    if len(search_history) > 100:
        search_history.pop(0)
    
    return results

async def _search_local_advanced(db: Session, request: AdvancedSearchRequest):
    """Advanced local database search with filtering and sorting"""
    
    query = db.query(CVE)
    
    # Text search filters
    if request.query and request.query.strip():
        search_term = request.query.strip()
        
        if request.exact_match:
            # Exact matching
            if search_term.upper().startswith("CVE-"):
                query = query.filter(CVE.cve_id == search_term.upper())
            else:
                query = query.filter(CVE.description == search_term)
        else:
            # Fuzzy matching
            like_term = f"%{search_term}%"
            conditions = [CVE.cve_id.ilike(like_term)]
            
            if request.include_descriptions:
                conditions.extend([
                    CVE.description.ilike(like_term),
                    CVE.cwe_ids.ilike(like_term)
                ])
            
            query = query.filter(or_(*conditions))
    
    # Severity filters
    if request.severity:
        query = query.filter(CVE.severity_level.in_([s.upper() for s in request.severity]))
    
    # Date range filters
    if request.date_from:
        try:
            date_from = datetime.strptime(request.date_from, "%Y-%m-%d")
            query = query.filter(CVE.published_date >= date_from)
        except ValueError:
            logger.warning(f"Invalid date_from format: {request.date_from}")
    
    if request.date_to:
        try:
            date_to = datetime.strptime(request.date_to, "%Y-%m-%d")
            query = query.filter(CVE.published_date <= date_to)
        except ValueError:
            logger.warning(f"Invalid date_to format: {request.date_to}")
    
    # CVSS score filters
    if request.cvss_min is not None:
        query = query.filter(CVE.cvss_v3_score >= request.cvss_min)
    
    if request.cvss_max is not None:
        query = query.filter(CVE.cvss_v3_score <= request.cvss_max)
    
    # CWE filters
    if request.cwe_ids:
        cwe_conditions = []
        for cwe_id in request.cwe_ids:
            cwe_conditions.append(CVE.cwe_ids.ilike(f"%{cwe_id}%"))
        query = query.filter(or_(*cwe_conditions))
    
    # Vendor/Product filters (if we have these fields in the future)
    # These would require additional fields in the CVE model
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply sorting
    sort_column = getattr(CVE, request.sort_by, CVE.published_date)
    if request.sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # Apply pagination
    query = query.offset(request.offset).limit(request.limit)
    
    # Execute query
    cves = query.all()
    
    # Format results
    formatted_results = []
    for cve in cves:
        cve_dict = cve.to_dict()
        cve_dict.update({
            "source": "Local Database",
            "can_import": False,
            "nvd_link": f"https://nvd.nist.gov/vuln/detail/{cve.cve_id}"
        })
        
        # Add detailed information if requested
        if request.include_details:
            cve_dict["detailed_info"] = {
                "attack_vector": getattr(cve, 'attack_vector', None),
                "attack_complexity": getattr(cve, 'attack_complexity', None),
                "privileges_required": getattr(cve, 'privileges_required', None),
                "user_interaction": getattr(cve, 'user_interaction', None),
                "scope": getattr(cve, 'scope', None),
                "confidentiality_impact": getattr(cve, 'confidentiality_impact', None),
                "integrity_impact": getattr(cve, 'integrity_impact', None),
                "availability_impact": getattr(cve, 'availability_impact', None)
            }
        
        formatted_results.append(cve_dict)
    
    return formatted_results, total_count

async def _search_nvd_advanced(nvd_service: NVDSearchService, request: AdvancedSearchRequest, db: Session):
    """Advanced NVD search with enhanced parameters"""
    
    results = {"results": [], "errors": [], "warnings": []}
    
    try:
        # Determine search strategy
        cve_id = None
        keyword = None
        
        if request.query and request.query.strip():
            query_clean = request.query.strip()
            if query_clean.upper().startswith("CVE-"):
                cve_id = query_clean
            else:
                keyword = query_clean
        
        # Map severity list to single value for NVD API
        severity = None
        if request.severity and len(request.severity) == 1:
            severity = request.severity[0]
        elif request.severity and len(request.severity) > 1:
            results["warnings"].append(
                "NVD API supports single severity filter only. Using first value."
            )
            severity = request.severity[0]
        
        # Perform NVD search
        nvd_result = await nvd_service.search_live(
            cve_id=cve_id,
            keyword=keyword,
            severity=severity,
            start_date=request.date_from,
            end_date=request.date_to,
            limit=request.limit
        )
        
        if nvd_result["success"]:
            raw_results = nvd_result["results"]
            
            # Apply additional client-side filters not supported by NVD API
            filtered_results = _apply_client_side_filters(raw_results, request)
            
            # Check import status for each result
            for nvd_cve in filtered_results:
                existing = db.query(CVE).filter(CVE.cve_id == nvd_cve["cve_id"]).first()
                if existing:
                    nvd_cve["can_import"] = False
                    nvd_cve["import_status"] = "Already in local database"
                    nvd_cve["local_last_updated"] = existing.modified_date.isoformat() if existing.modified_date else None
                else:
                    nvd_cve["can_import"] = True
                    nvd_cve["import_status"] = "Available to import"
                
                # Add enhanced metadata if requested
                if request.include_details:
                    nvd_cve["detailed_info"] = _extract_detailed_nvd_info(nvd_cve)
            
            results["results"] = filtered_results
            
            if nvd_result.get("message"):
                results["warnings"].append(nvd_result["message"])
        else:
            results["errors"].append(f"NVD search failed: {nvd_result['error']}")
            
    except Exception as e:
        results["errors"].append(f"NVD search exception: {str(e)}")
    
    return results

def _apply_client_side_filters(nvd_results: List[Dict], request: AdvancedSearchRequest) -> List[Dict]:
    """Apply additional filters that NVD API doesn't support"""
    
    filtered = nvd_results
    
    # CVSS score filtering
    if request.cvss_min is not None or request.cvss_max is not None:
        def cvss_filter(cve):
            score = cve.get("cvss_v3_score")
            if score is None:
                return False
            try:
                score = float(score)
                if request.cvss_min is not None and score < request.cvss_min:
                    return False
                if request.cvss_max is not None and score > request.cvss_max:
                    return False
                return True
            except (ValueError, TypeError):
                return False
        
        filtered = [cve for cve in filtered if cvss_filter(cve)]
    
    # CWE filtering
    if request.cwe_ids:
        def cwe_filter(cve):
            cve_cwes = cve.get("cwe_ids", [])
            if not cve_cwes:
                return False
            return any(cwe_id in cve_cwes for cwe_id in request.cwe_ids)
        
        filtered = [cve for cve in filtered if cwe_filter(cve)]
    
    # Vendor/Product filtering (if available in NVD data)
    if request.vendor:
        vendor_term = request.vendor.lower()
        filtered = [
            cve for cve in filtered
            if vendor_term in cve.get("affected_products", "").lower()
        ]
    
    if request.product:
        product_term = request.product.lower()
        filtered = [
            cve for cve in filtered
            if product_term in cve.get("affected_products", "").lower()
        ]
    
    return filtered

def _extract_detailed_nvd_info(nvd_cve: Dict) -> Dict:
    """Extract detailed information from NVD CVE data"""
    
    return {
        "attack_vector": nvd_cve.get("attack_vector"),
        "attack_complexity": nvd_cve.get("attack_complexity"),
        "privileges_required": nvd_cve.get("privileges_required"),
        "user_interaction": nvd_cve.get("user_interaction"),
        "scope": nvd_cve.get("scope"),
        "confidentiality_impact": nvd_cve.get("confidentiality_impact"),
        "integrity_impact": nvd_cve.get("integrity_impact"),
        "availability_impact": nvd_cve.get("availability_impact"),
        "exploit_code_maturity": nvd_cve.get("exploit_code_maturity"),
        "remediation_level": nvd_cve.get("remediation_level"),
        "report_confidence": nvd_cve.get("report_confidence"),
        "temporal_score": nvd_cve.get("temporal_score"),
        "environmental_score": nvd_cve.get("environmental_score")
    }

@router.post("/bulk-import")
async def bulk_import_cves(
    request: BulkImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    auth: str = Depends(get_admin_dependency())
):
    """Bulk import multiple CVEs from NVD"""
    
    if len(request.cve_ids) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 CVEs can be imported in a single batch"
        )
    
    logger.info(f"Bulk import requested for {len(request.cve_ids)} CVEs")
    
    # Queue the bulk import task
    task_id = hashlib.md5(
        f"{','.join(request.cve_ids)}{datetime.now()}".encode()
    ).hexdigest()[:8]
    
    background_tasks.add_task(
        _process_bulk_import,
        task_id,
        request.cve_ids,
        request.force,
        request.priority
    )
    
    return {
        "success": True,
        "task_id": task_id,
        "message": f"Bulk import queued for {len(request.cve_ids)} CVEs",
        "cve_ids": request.cve_ids,
        "estimated_time_minutes": len(request.cve_ids) * 0.5,
        "status_endpoint": f"/api/v1/cve/bulk-import/{task_id}/status"
    }

async def _process_bulk_import(task_id: str, cve_ids: List[str], force: bool, priority: str):
    """Background task to process bulk import"""
    
    # This would be implemented with proper task queue (Celery/RQ) in production
    logger.info(f"Processing bulk import task {task_id} with {len(cve_ids)} CVEs")
    
    # Simulate processing (in real implementation, would import each CVE)
    import time
    for i, cve_id in enumerate(cve_ids):
        time.sleep(0.1)  # Simulate processing time
        logger.info(f"Task {task_id}: Processing {cve_id} ({i+1}/{len(cve_ids)})")
    
    logger.info(f"Bulk import task {task_id} completed")

@router.get("/search/history")
async def get_search_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    auth: str = Depends(get_auth_dependency())
):
    """Get search history"""
    
    total = len(search_history)
    history_slice = search_history[-(offset + limit):-offset if offset > 0 else None]
    history_slice.reverse()  # Most recent first
    
    return {
        "history": [item.dict() for item in history_slice],
        "pagination": {
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total
        }
    }

@router.post("/search/save")
async def save_search(
    request: SavedSearchRequest,
    auth: str = Depends(get_auth_dependency())
):
    """Save a search for later reuse"""
    
    search_id = hashlib.md5(
        f"{request.name}{datetime.now()}".encode()
    ).hexdigest()[:8]
    
    saved_searches[search_id] = {
        "id": search_id,
        "name": request.name,
        "description": request.description,
        "parameters": request.parameters.dict(),
        "created_at": datetime.now().isoformat(),
        "last_used": None,
        "usage_count": 0
    }
    
    return {
        "success": True,
        "search_id": search_id,
        "message": f"Search '{request.name}' saved successfully"
    }

@router.get("/search/saved")
async def get_saved_searches(auth: str = Depends(get_auth_dependency())):
    """Get all saved searches"""
    
    return {
        "saved_searches": list(saved_searches.values()),
        "total": len(saved_searches)
    }

@router.post("/search/saved/{search_id}/execute")
async def execute_saved_search(
    search_id: str,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Execute a saved search"""
    
    if search_id not in saved_searches:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    saved_search = saved_searches[search_id]
    
    # Update usage statistics
    saved_search["last_used"] = datetime.now().isoformat()
    saved_search["usage_count"] += 1
    
    # Execute the search
    search_params = AdvancedSearchRequest(**saved_search["parameters"])
    result = await advanced_search_cves(search_params, db)
    
    # Add metadata about the saved search
    result["saved_search_info"] = {
        "id": search_id,
        "name": saved_search["name"],
        "description": saved_search["description"]
    }
    
    return result

@router.delete("/search/saved/{search_id}")
async def delete_saved_search(
    search_id: str,
    auth: str = Depends(get_auth_dependency())
):
    """Delete a saved search"""
    
    if search_id not in saved_searches:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    deleted_search = saved_searches.pop(search_id)
    
    return {
        "success": True,
        "message": f"Saved search '{deleted_search['name']}' deleted successfully"
    }

# Legacy simple search endpoint (for backward compatibility)
@router.post("/search")
async def search_cves_hybrid(
    request: SearchRequest,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Legacy hybrid CVE search - redirects to advanced search"""
    
    # Convert legacy request to advanced request
    advanced_request = AdvancedSearchRequest(
        query=request.query,
        severity=[request.severity] if request.severity else None,
        search_type=request.search_type,
        limit=request.limit
    )
    
    # Call advanced search
    result = await advanced_search_cves(advanced_request, db)
    
    # Convert back to legacy format for compatibility
    legacy_result = {
        "local_results": result["local_results"],
        "nvd_results": result["nvd_results"],
        "total_local": result["pagination"]["total_local"],
        "total_nvd": result["pagination"]["total_nvd"],
        "search_type": request.search_type,
        "query": request.query,
        "severity": request.severity,
        "success": result["success"],
        "errors": result["errors"],
        "total_results": len(result["local_results"]) + len(result["nvd_results"])
    }
    
    if result["errors"]:
        legacy_result["message"] = "; ".join(result["errors"])
    elif len(legacy_result["local_results"]) + len(legacy_result["nvd_results"]) == 0:
        legacy_result["message"] = "No CVEs found matching your criteria"
    
    return legacy_result

@router.post("/import-from-nvd")
async def import_cve_from_nvd(
    request: ImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
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
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
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
async def get_cve(
    cve_id: str, 
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
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

@router.get("/{cve_id}/details")
async def get_cve_details_hybrid(
    cve_id: str, 
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get CVE details from local database or NVD (hybrid approach)"""
    try:
        # Try local database first
        cve = db.query(CVE).filter(CVE.cve_id == cve_id).first()
        if cve:
            result = cve.to_dict()
            result.update({
                "source": "Local Database",
                "can_import": False,
                "nvd_link": f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            })
            return result
        
        # If not found locally, try NVD
        logger.info(f"CVE {cve_id} not found locally, searching NVD...")
        nvd_service = NVDSearchService()
        nvd_result = await nvd_service.get_cve_details(cve_id)
        
        if nvd_result.get("success") and nvd_result.get("cve"):
            cve_data = nvd_result["cve"]
            cve_data.update({
                "can_import": True,
                "import_status": "Available to import"
            })
            return cve_data
        
        # If not found anywhere, raise 404
        raise HTTPException(status_code=404, detail=f"CVE {cve_id} not found in local database or NVD")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching CVE details for {cve_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching CVE details: {str(e)}")

@router.get("/stats/summary")
async def get_cve_stats(
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
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
