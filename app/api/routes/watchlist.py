from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import logging
from app.database import get_db
from app.core.security import get_auth_dependency

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for watchlists
watchlists = {}
watchlist_alerts = {}

class WatchlistCreate(BaseModel):
    name: str = Field(..., description="Watchlist name")
    description: Optional[str] = Field(None, description="Watchlist description")
    keywords: Optional[List[str]] = Field(None, description="Keywords to monitor")

class WatchlistResponse(BaseModel):
    watchlist_id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    cve_count: int
    alert_count: int
    keywords: Optional[List[str]]

class AddCVERequest(BaseModel):
    cve_ids: List[str] = Field(..., description="CVE IDs to add to watchlist")
    priority: str = Field("medium", description="Priority level")

class WatchlistService:
    def create_watchlist(self, create_data: WatchlistCreate) -> WatchlistResponse:
        """Create a new watchlist"""
        watchlist_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        watchlist = {
            "watchlist_id": watchlist_id,
            "name": create_data.name,
            "description": create_data.description,
            "created_at": now,
            "updated_at": now,
            "is_active": True,
            "cves": {},
            "keywords": create_data.keywords or []
        }
        
        watchlists[watchlist_id] = watchlist
        watchlist_alerts[watchlist_id] = []
        
        logger.info(f"Created watchlist {watchlist_id}: {create_data.name}")
        return self._to_response(watchlist)
    
    def add_cves_to_watchlist(self, watchlist_id: str, request: AddCVERequest) -> Dict[str, Any]:
        """Add CVEs to a watchlist"""
        if watchlist_id not in watchlists:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        watchlist = watchlists[watchlist_id]
        results = {"added": [], "skipped": []}
        
        for cve_id in request.cve_ids:
            if cve_id in watchlist["cves"]:
                results["skipped"].append(cve_id)
                continue
            
            watch_item = {
                "cve_id": cve_id,
                "added_at": datetime.utcnow(),
                "priority": request.priority,
                "status": "active"
            }
            
            watchlist["cves"][cve_id] = watch_item
            results["added"].append(cve_id)
            
            # Create alert
            alert = {
                "alert_id": str(uuid.uuid4()),
                "watchlist_id": watchlist_id,
                "cve_id": cve_id,
                "message": f"CVE {cve_id} added to watchlist",
                "created_at": datetime.utcnow(),
                "read": False
            }
            watchlist_alerts[watchlist_id].append(alert)
        
        watchlist["updated_at"] = datetime.utcnow()
        
        logger.info(f"Added CVEs to watchlist {watchlist_id}: {results}")
        return results
    
    def get_watchlist_statistics(self) -> Dict[str, Any]:
        """Get overall watchlist statistics"""
        total_watchlists = len(watchlists)
        active_watchlists = sum(1 for w in watchlists.values() if w["is_active"])
        total_monitored_cves = sum(len(w["cves"]) for w in watchlists.values())
        total_alerts = sum(len(alerts) for alerts in watchlist_alerts.values())
        unread_alerts = sum(
            len([a for a in alerts if not a.get("read", False)]) 
            for alerts in watchlist_alerts.values()
        )
        
        return {
            "total_watchlists": total_watchlists,
            "active_watchlists": active_watchlists,
            "total_monitored_cves": total_monitored_cves,
            "total_alerts": total_alerts,
            "unread_alerts": unread_alerts
        }
    
    def _to_response(self, watchlist: Dict[str, Any]) -> WatchlistResponse:
        """Convert watchlist dict to response model"""
        return WatchlistResponse(
            watchlist_id=watchlist["watchlist_id"],
            name=watchlist["name"],
            description=watchlist["description"],
            created_at=watchlist["created_at"],
            updated_at=watchlist["updated_at"],
            is_active=watchlist["is_active"],
            cve_count=len(watchlist["cves"]),
            alert_count=len(watchlist_alerts.get(watchlist["watchlist_id"], [])),
            keywords=watchlist["keywords"]
        )

watchlist_service = WatchlistService()

# API Endpoints
@router.post("/", response_model=WatchlistResponse)
async def create_watchlist(
    watchlist_data: WatchlistCreate,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Create a new watchlist"""
    try:
        return watchlist_service.create_watchlist(watchlist_data)
    except Exception as e:
        logger.error(f"Error creating watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create watchlist")

@router.get("/", response_model=List[WatchlistResponse])
async def get_watchlists(
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get all watchlists"""
    try:
        result = []
        for watchlist in watchlists.values():
            if watchlist["is_active"]:
                result.append(watchlist_service._to_response(watchlist))
        
        return sorted(result, key=lambda x: x.updated_at, reverse=True)
    except Exception as e:
        logger.error(f"Error getting watchlists: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get watchlists")

@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: str,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get a specific watchlist"""
    if watchlist_id not in watchlists:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    return watchlist_service._to_response(watchlists[watchlist_id])

@router.delete("/{watchlist_id}")
async def delete_watchlist(
    watchlist_id: str,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Delete a watchlist"""
    if watchlist_id not in watchlists:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    del watchlists[watchlist_id]
    if watchlist_id in watchlist_alerts:
        del watchlist_alerts[watchlist_id]
    
    logger.info(f"Deleted watchlist {watchlist_id}")
    return {"message": "Watchlist deleted successfully"}

@router.post("/{watchlist_id}/cves")
async def add_cves_to_watchlist(
    watchlist_id: str,
    request: AddCVERequest,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Add CVEs to a watchlist"""
    try:
        return watchlist_service.add_cves_to_watchlist(watchlist_id, request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding CVEs to watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add CVEs to watchlist")

@router.get("/{watchlist_id}/cves")
async def get_watchlist_cves(
    watchlist_id: str,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get CVEs in a watchlist"""
    if watchlist_id not in watchlists:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    watchlist = watchlists[watchlist_id]
    cves = watchlist["cves"]
    
    return {"cves": cves, "total": len(cves)}

@router.get("/{watchlist_id}/alerts")
async def get_watchlist_alerts(
    watchlist_id: str,
    limit: int = 50,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get alerts for a watchlist"""
    if watchlist_id not in watchlist_alerts:
        return []
    
    alerts = watchlist_alerts[watchlist_id]
    
    if unread_only:
        alerts = [a for a in alerts if not a.get("read", False)]
    
    # Sort by created_at descending
    alerts = sorted(alerts, key=lambda x: x["created_at"], reverse=True)
    
    return alerts[:limit]

@router.get("/stats/overview")
async def get_watchlist_stats(
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get watchlist statistics"""
    try:
        return watchlist_service.get_watchlist_statistics()
    except Exception as e:
        logger.error(f"Error getting watchlist stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")
