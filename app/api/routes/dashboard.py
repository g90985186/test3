from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.cve import CVE
from app.models.analysis import Analysis
from app.core.security import get_auth_dependency
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/metrics")
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get comprehensive dashboard metrics"""
    
    try:
        # Get total counts
        total_count = db.query(CVE).count()
        critical_count = db.query(CVE).filter(CVE.severity_level == "CRITICAL").count()
        high_count = db.query(CVE).filter(CVE.severity_level == "HIGH").count()
        medium_count = db.query(CVE).filter(CVE.severity_level == "MEDIUM").count()
        low_count = db.query(CVE).filter(CVE.severity_level == "LOW").count()
        
        # Get recent CVEs (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_count = db.query(CVE).filter(
            CVE.created_at >= thirty_days_ago
        ).count()
        
        # Get analysis count
        analysis_count = db.query(Analysis).count()
        
        # Get critical CVEs from last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_critical = db.query(CVE).filter(
            and_(
                CVE.severity_level == "CRITICAL",
                CVE.created_at >= seven_days_ago
            )
        ).count()
        
        return {
            "total_count": total_count,
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "recent_count": recent_count,
            "analysis_count": analysis_count,
            "recent_critical": recent_critical,
            "by_severity": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count
            },
            "status": "success",
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return {
            "total_count": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "recent_count": 0,
            "analysis_count": 0,
            "recent_critical": 0,
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "status": "error",
            "error": str(e),
            "last_updated": datetime.utcnow().isoformat()
        }

@router.get("/recent-cves")
async def get_recent_cves(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get recent CVEs for dashboard table"""
    
    try:
        recent_cves = db.query(CVE)\
            .order_by(desc(CVE.published_date))\
            .limit(limit)\
            .all()
        
        results = []
        for cve in recent_cves:
            cve_dict = cve.to_dict()
            # Format date for frontend
            if cve.published_date:
                cve_dict["published_date"] = cve.published_date.strftime("%Y-%m-%d")
            results.append(cve_dict)
        
        return {
            "results": results,
            "total": len(results),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting recent CVEs: {e}")
        return {
            "results": [],
            "total": 0,
            "status": "error",
            "error": str(e)
        }

@router.get("/timeline")
async def get_timeline_data(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get timeline data for charts (CVEs by day)"""
    
    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Query CVEs grouped by date
        timeline_data = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            
            # Get CVEs for this date
            daily_cves = db.query(CVE).filter(
                func.date(CVE.published_date) == current_date
            ).all()
            
            # Count by severity
            critical = sum(1 for cve in daily_cves if cve.severity_level == "CRITICAL")
            high = sum(1 for cve in daily_cves if cve.severity_level == "HIGH")
            medium = sum(1 for cve in daily_cves if cve.severity_level == "MEDIUM")
            low = sum(1 for cve in daily_cves if cve.severity_level == "LOW")
            total = len(daily_cves)
            
            timeline_data.append({
                "date": current_date.isoformat(),
                "count": total,
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low
            })
        
        # Calculate statistics
        total_cves = sum(day["count"] for day in timeline_data)
        avg_per_day = total_cves / days if days > 0 else 0
        peak_day = max(timeline_data, key=lambda x: x["count"]) if timeline_data else None
        
        return {
            "data": timeline_data,
            "statistics": {
                "total_cves": total_cves,
                "average_per_day": round(avg_per_day, 2),
                "peak_day": peak_day,
                "days_covered": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting timeline data: {e}")
        return {
            "data": [],
            "statistics": {
                "total_cves": 0,
                "average_per_day": 0,
                "peak_day": None,
                "days_covered": days,
                "start_date": start_date.isoformat() if 'start_date' in locals() else None,
                "end_date": end_date.isoformat() if 'end_date' in locals() else None
            },
            "status": "error",
            "error": str(e)
        }

@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Get additional dashboard statistics"""
    
    try:
        # Get trending information
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Recent trends
        recent_7d = db.query(CVE).filter(CVE.created_at >= seven_days_ago).count()
        recent_30d = db.query(CVE).filter(CVE.created_at >= thirty_days_ago).count()
        
        # Most common CWEs
        cwe_stats = db.query(CVE).filter(CVE.cwe_ids.isnot(None)).all()
        cwe_counts = {}
        for cve in cwe_stats:
            if cve.cwe_ids:
                for cwe in cve.cwe_ids:
                    cwe_counts[cwe] = cwe_counts.get(cwe, 0) + 1
        
        top_cwes = sorted(cwe_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # CVSS score distribution
        cvss_ranges = {
            "critical": db.query(CVE).filter(CVE.cvss_v3_score >= 9.0).count(),
            "high": db.query(CVE).filter(
                and_(CVE.cvss_v3_score >= 7.0, CVE.cvss_v3_score < 9.0)
            ).count(),
            "medium": db.query(CVE).filter(
                and_(CVE.cvss_v3_score >= 4.0, CVE.cvss_v3_score < 7.0)
            ).count(),
            "low": db.query(CVE).filter(
                and_(CVE.cvss_v3_score >= 0.1, CVE.cvss_v3_score < 4.0)
            ).count()
        }
        
        return {
            "trends": {
                "last_7_days": recent_7d,
                "last_30_days": recent_30d,
                "growth_rate": (recent_7d / recent_30d * 100) if recent_30d > 0 else 0
            },
            "top_cwes": [{"cwe": cwe, "count": count} for cwe, count in top_cwes],
            "cvss_distribution": cvss_ranges,
            "status": "success",
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return {
            "trends": {"last_7_days": 0, "last_30_days": 0, "growth_rate": 0},
            "top_cwes": [],
            "cvss_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "status": "error",
            "error": str(e),
            "generated_at": datetime.utcnow().isoformat()
        }
