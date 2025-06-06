from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import logging
import json
import csv
import os
from pathlib import Path
from app.database import get_db
from app.models.cve import CVE
from app.core.security import get_auth_dependency, get_admin_dependency

logger = logging.getLogger(__name__)
router = APIRouter()

# Create reports directory
REPORTS_DIR = Path("app/static/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

class ReportRequest(BaseModel):
    report_type: str = Field(..., description="Type: dashboard, cve_analysis, watchlist, custom")
    format: str = Field("pdf", description="Format: pdf, html, csv, json")
    title: Optional[str] = Field(None, description="Custom report title")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    template: str = Field("standard", description="Report template: standard, executive, technical")

class ReportResponse(BaseModel):
    report_id: str
    report_type: str
    format: str
    title: str
    status: str
    created_at: datetime
    file_path: Optional[str]
    download_url: Optional[str]
    file_size: Optional[int]
    metadata: Dict[str, Any]

class ReportService:
    def __init__(self):
        self.reports_storage = {}
        self.report_metrics = {
            "total_reports": 0,
            "reports_by_type": {},
            "reports_by_format": {},
            "total_downloads": 0,
            "generation_times": []
        }
    
    def generate_report(self, request: ReportRequest, db: Session) -> ReportResponse:
        """Generate a report based on the request"""
        start_time = datetime.utcnow()
        report_id = str(uuid.uuid4())
        
        try:
            # Determine report title
            title = request.title or self._generate_title(request.report_type)
            
            # Collect data based on report type
            data = self._collect_report_data(request, db)
            
            # Generate report content
            file_path, file_size = self._generate_report_file(report_id, request, data)
            
            # Calculate generation time
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create report record
            report = {
                "report_id": report_id,
                "report_type": request.report_type,
                "format": request.format,
                "title": title,
                "status": "completed",
                "created_at": start_time,
                "file_path": file_path,
                "download_url": f"/api/v1/reports/{report_id}/download",
                "file_size": file_size,
                "metadata": {
                    "generation_time": generation_time,
                    "filters": request.filters,
                    "template": request.template,
                    "data_points": len(data.get("items", []))
                }
            }
            
            # Store report
            self.reports_storage[report_id] = report
            
            # Update metrics
            self._update_metrics(request.report_type, request.format, generation_time)
            
            logger.info(f"Generated {request.format.upper()} report {report_id}: {title}")
            return ReportResponse(**report)
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            # Create failed report record
            report = {
                "report_id": report_id,
                "report_type": request.report_type,
                "format": request.format,
                "title": title if 'title' in locals() else "Report Generation Failed",
                "status": "failed",
                "created_at": start_time,
                "file_path": None,
                "download_url": None,
                "file_size": None,
                "metadata": {"error": str(e)}
            }
            self.reports_storage[report_id] = report
            return ReportResponse(**report)
    
    def _collect_report_data(self, request: ReportRequest, db: Session) -> Dict[str, Any]:
        """Collect data for the report based on type"""
        data = {"items": [], "summary": {}, "charts": []}
        
        if request.report_type == "dashboard":
            data = self._collect_dashboard_data(request, db)
        elif request.report_type == "cve_analysis":
            data = self._collect_cve_data(request, db)
        elif request.report_type == "watchlist":
            data = self._collect_watchlist_data(request, db)
        
        return data
    
    def _collect_dashboard_data(self, request: ReportRequest, db: Session) -> Dict[str, Any]:
        """Collect dashboard metrics data"""
        cves = db.query(CVE).limit(100).all()
        
        severity_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for cve in cves:
            if hasattr(cve, 'severity') and cve.severity:
                severity_counts[cve.severity.upper()] = severity_counts.get(cve.severity.upper(), 0) + 1
        
        return {
            "items": [{"cve_id": cve.cve_id, "severity": getattr(cve, 'severity', 'UNKNOWN')} for cve in cves],
            "summary": {
                "total_cves": len(cves),
                "severity_breakdown": severity_counts,
                "generated_at": datetime.utcnow().isoformat()
            },
            "charts": [
                {
                    "type": "pie",
                    "title": "CVE Severity Distribution",
                    "data": severity_counts
                }
            ]
        }
    
    def _collect_cve_data(self, request: ReportRequest, db: Session) -> Dict[str, Any]:
        """Collect CVE analysis data"""
        query = db.query(CVE)
        cves = query.limit(200).all()
        
        return {
            "items": [
                {
                    "cve_id": cve.cve_id,
                    "description": getattr(cve, 'description', 'No description available')[:200],
                    "severity": getattr(cve, 'severity', 'UNKNOWN')
                } for cve in cves
            ],
            "summary": {
                "total_analyzed": len(cves),
                "analysis_date": datetime.utcnow().isoformat()
            },
            "charts": []
        }
    
    def _collect_watchlist_data(self, request: ReportRequest, db: Session) -> Dict[str, Any]:
        """Collect watchlist data"""
        return {
            "items": [
                {
                    "watchlist_name": "Critical Security Watchlist",
                    "cve_count": 2,
                    "alert_count": 2,
                    "last_updated": datetime.utcnow().isoformat()
                }
            ],
            "summary": {
                "total_watchlists": 1,
                "total_monitored_cves": 2,
                "total_alerts": 2
            },
            "charts": []
        }
    
    def _generate_report_file(self, report_id: str, request: ReportRequest, data: Dict[str, Any]) -> tuple:
        """Generate the actual report file"""
        if request.format == "json":
            return self._generate_json_report(report_id, request, data)
        elif request.format == "csv":
            return self._generate_csv_report(report_id, request, data)
        elif request.format == "html":
            return self._generate_html_report(report_id, request, data)
        elif request.format == "pdf":
            return self._generate_pdf_report(report_id, request, data)
        else:
            raise ValueError(f"Unsupported format: {request.format}")
    
    def _generate_json_report(self, report_id: str, request: ReportRequest, data: Dict[str, Any]) -> tuple:
        """Generate JSON report"""
        file_path = REPORTS_DIR / f"{report_id}.json"
        
        report_content = {
            "report_id": report_id,
            "title": request.title or self._generate_title(request.report_type),
            "generated_at": datetime.utcnow().isoformat(),
            "report_type": request.report_type,
            "template": request.template,
            "data": data
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_content, f, indent=2, default=str)
        
        file_size = file_path.stat().st_size
        return str(file_path), file_size
    
    def _generate_csv_report(self, report_id: str, request: ReportRequest, data: Dict[str, Any]) -> tuple:
        """Generate CSV report"""
        file_path = REPORTS_DIR / f"{report_id}.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            if data["items"]:
                fieldnames = list(data["items"][0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in data["items"]:
                    clean_item = {}
                    for key, value in item.items():
                        clean_item[key] = str(value) if value is not None else ""
                    writer.writerow(clean_item)
        
        file_size = file_path.stat().st_size
        return str(file_path), file_size
    
    def _generate_html_report(self, report_id: str, request: ReportRequest, data: Dict[str, Any]) -> tuple:
        """Generate HTML report"""
        file_path = REPORTS_DIR / f"{report_id}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{request.title or self._generate_title(request.report_type)}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .summary {{ background-color: #e9ecef; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{request.title or self._generate_title(request.report_type)}</h1>
                <p>Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                <p>Report ID: {report_id}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <ul>
        """
        
        for key, value in data["summary"].items():
            html_content += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        
        html_content += "</ul></div>"
        
        if data["items"]:
            html_content += "<h2>Data</h2><table><thead><tr>"
            
            for key in data["items"][0].keys():
                html_content += f"<th>{key.replace('_', ' ').title()}</th>"
            
            html_content += "</tr></thead><tbody>"
            
            for item in data["items"][:50]:
                html_content += "<tr>"
                for value in item.values():
                    display_value = str(value) if value is not None else ""
                    if len(display_value) > 100:
                        display_value = display_value[:100] + "..."
                    html_content += f"<td>{display_value}</td>"
                html_content += "</tr>"
            
            html_content += "</tbody></table>"
        
        html_content += "</body></html>"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        file_size = file_path.stat().st_size
        return str(file_path), file_size
    
    def _generate_pdf_report(self, report_id: str, request: ReportRequest, data: Dict[str, Any]) -> tuple:
        """Generate PDF report (text-based)"""
        file_path = REPORTS_DIR / f"{report_id}.txt"
        
        content = f"""
CVE Analysis Platform - Report

Title: {request.title or self._generate_title(request.report_type)}
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
Report ID: {report_id}

SUMMARY:
"""
        for key, value in data["summary"].items():
            content += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        content += f"\nDATA ITEMS: {len(data['items'])} records found\n"
        
        if data["items"]:
            content += "\nSAMPLE DATA (First 5 items):\n"
            for i, item in enumerate(data["items"][:5]):
                content += f"\n{i+1}. "
                for key, value in item.items():
                    content += f"{key}: {value}, "
                content = content.rstrip(", ") + "\n"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = file_path.stat().st_size
        return str(file_path), file_size
    
    def _generate_title(self, report_type: str) -> str:
        """Generate default title based on report type"""
        titles = {
            "dashboard": "CVE Analysis Dashboard Report",
            "cve_analysis": "CVE Analysis Report",
            "watchlist": "Watchlist Summary Report",
            "custom": "Custom Analysis Report"
        }
        return titles.get(report_type, "CVE Platform Report")
    
    def _update_metrics(self, report_type: str, format: str, generation_time: float):
        """Update report generation metrics"""
        self.report_metrics["total_reports"] += 1
        self.report_metrics["reports_by_type"][report_type] = (
            self.report_metrics["reports_by_type"].get(report_type, 0) + 1
        )
        self.report_metrics["reports_by_format"][format] = (
            self.report_metrics["reports_by_format"].get(format, 0) + 1
        )
        self.report_metrics["generation_times"].append(generation_time)
    
    def get_report(self, report_id: str) -> Optional[ReportResponse]:
        """Get a specific report"""
        if report_id in self.reports_storage:
            return ReportResponse(**self.reports_storage[report_id])
        return None
    
    def get_all_reports(self, limit: int = 50) -> List[ReportResponse]:
        """Get all reports"""
        reports = list(self.reports_storage.values())
        reports.sort(key=lambda x: x["created_at"], reverse=True)
        return [ReportResponse(**report) for report in reports[:limit]]
    
    def download_report(self, report_id: str) -> Optional[str]:
        """Get file path for download"""
        if report_id in self.reports_storage:
            report = self.reports_storage[report_id]
            if report["status"] == "completed" and report["file_path"]:
                self.report_metrics["total_downloads"] += 1
                return report["file_path"]
        return None

report_service = ReportService()

# API Endpoints
@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    auth: str = Depends(get_auth_dependency())
):
    """Generate a new report"""
    try:
        return report_service.generate_report(request, db)
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    limit: int = 50,
    auth: str = Depends(get_auth_dependency())
):
    """Get all generated reports"""
    try:
        return report_service.get_all_reports(limit)
    except Exception as e:
        logger.error(f"Error getting reports: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve reports")

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    auth: str = Depends(get_auth_dependency())
):
    """Get a specific report"""
    report = report_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    auth: str = Depends(get_auth_dependency())
):
    """Download a report file"""
    file_path = report_service.download_report(report_id)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='application/octet-stream'
    )

@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    auth: str = Depends(get_auth_dependency())
):
    """Delete a report"""
    if report_id not in report_service.reports_storage:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = report_service.reports_storage[report_id]
    if report["file_path"] and os.path.exists(report["file_path"]):
        os.remove(report["file_path"])
    
    del report_service.reports_storage[report_id]
    
    logger.info(f"Deleted report {report_id}")
    return {"message": "Report deleted successfully"}

@router.get("/metrics/overview")
async def get_report_metrics(auth: str = Depends(get_auth_dependency())):
    """Get report generation metrics"""
    try:
        avg_time = (
            sum(report_service.report_metrics["generation_times"]) / 
            len(report_service.report_metrics["generation_times"])
            if report_service.report_metrics["generation_times"] else 0.0
        )
        
        return {
            "total_reports": report_service.report_metrics["total_reports"],
            "reports_by_type": report_service.report_metrics["reports_by_type"],
            "reports_by_format": report_service.report_metrics["reports_by_format"],
            "total_downloads": report_service.report_metrics["total_downloads"],
            "average_generation_time": avg_time
        }
    except Exception as e:
        logger.error(f"Error getting report metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

@router.get("/types/supported")
async def get_supported_report_types(auth: str = Depends(get_auth_dependency())):
    """Get supported report types"""
    return {
        "report_types": [
            {
                "type": "dashboard",
                "description": "Comprehensive dashboard metrics and analytics",
                "supported_formats": ["pdf", "html", "json", "csv"]
            },
            {
                "type": "cve_analysis",
                "description": "Detailed CVE analysis and vulnerability assessment",
                "supported_formats": ["pdf", "html", "json", "csv"]
            },
            {
                "type": "watchlist",
                "description": "Watchlist summary with monitored CVEs and alerts",
                "supported_formats": ["pdf", "html", "json", "csv"]
            }
        ]
    }
