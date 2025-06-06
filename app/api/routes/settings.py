from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import os
from datetime import datetime
from app.core.security import get_api_key_dependency
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Settings storage (in production, use database)
user_settings = {}
system_settings = {
    "default_search_source": "both",
    "default_results_per_page": 25,
    "max_results_per_page": 100,
    "auto_refresh_interval": 30,
    "rate_limit_per_minute": 100,
    "session_timeout_minutes": 60,
    "max_search_history": 50,
    "enable_notifications": True,
    "enable_email_notifications": False,
    "default_export_format": "pdf",
    "ollama_endpoint": "http://localhost:11434",
    "nvd_api_key": "",
    "maintenance_mode": False
}

class UserSettings(BaseModel):
    """User settings model."""
    general: Optional[Dict[str, Any]] = Field(default_factory=dict)
    notifications: Optional[Dict[str, Any]] = Field(default_factory=dict) 
    export: Optional[Dict[str, Any]] = Field(default_factory=dict)
    advanced: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SystemSettings(BaseModel):
    """System settings model."""
    api: Optional[Dict[str, Any]] = Field(default_factory=dict)
    security: Optional[Dict[str, Any]] = Field(default_factory=dict)
    external_services: Optional[Dict[str, Any]] = Field(default_factory=dict)
    performance: Optional[Dict[str, Any]] = Field(default_factory=dict)

class NotificationPreferences(BaseModel):
    """Notification preferences model."""
    email_enabled: bool = False
    email_address: Optional[str] = None
    critical_cves: bool = True
    watchlist_updates: bool = True
    analysis_complete: bool = False
    daily_summary: bool = False
    
class ExportPreferences(BaseModel):
    """Export preferences model."""
    default_format: str = "pdf"
    template: str = "executive"
    include_charts: bool = True
    include_recommendations: bool = True
    auto_save: bool = False

@router.get("/user", response_model=UserSettings)
async def get_user_settings(user_id: str = "default"):
    """Get user settings."""
    if user_id not in user_settings:
        # Return default settings
        return UserSettings(
            general={
                "auto_refresh": False,
                "show_tooltips": True,
                "default_search_source": "both",
                "default_results_per_page": 25,
                "dark_mode": False
            },
            notifications={
                "email_enabled": False,
                "critical_cves": True,
                "watchlist_updates": True,
                "analysis_complete": False
            },
            export={
                "default_format": "pdf",
                "template": "executive",
                "include_charts": True,
                "include_recommendations": True
            },
            advanced={
                "enable_shortcuts": True,
                "cache_results": True,
                "debug_mode": False
            }
        )
    
    return UserSettings(**user_settings[user_id])

@router.put("/user")
async def update_user_settings(
    settings: UserSettings,
    user_id: str = "default"
):
    """Update user settings."""
    user_settings[user_id] = settings.dict()
    
    # In production, save to database
    logger.info(f"Updated user settings for {user_id}")
    
    return {
        "success": True,
        "message": "User settings updated successfully",
        "updated_at": datetime.now().isoformat()
    }

@router.get("/notifications", response_model=NotificationPreferences)
async def get_notification_preferences(user_id: str = "default"):
    """Get notification preferences."""
    settings = user_settings.get(user_id, {})
    notif_settings = settings.get("notifications", {})
    
    return NotificationPreferences(
        email_enabled=notif_settings.get("email_enabled", False),
        email_address=notif_settings.get("email_address"),
        critical_cves=notif_settings.get("critical_cves", True),
        watchlist_updates=notif_settings.get("watchlist_updates", True),
        analysis_complete=notif_settings.get("analysis_complete", False),
        daily_summary=notif_settings.get("daily_summary", False)
    )

@router.put("/notifications")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    user_id: str = "default"
):
    """Update notification preferences."""
    if user_id not in user_settings:
        user_settings[user_id] = {}
    
    user_settings[user_id]["notifications"] = preferences.dict()
    
    return {
        "success": True,
        "message": "Notification preferences updated successfully"
    }

@router.get("/export", response_model=ExportPreferences)
async def get_export_preferences(user_id: str = "default"):
    """Get export preferences."""
    settings = user_settings.get(user_id, {})
    export_settings = settings.get("export", {})
    
    return ExportPreferences(
        default_format=export_settings.get("default_format", "pdf"),
        template=export_settings.get("template", "executive"),
        include_charts=export_settings.get("include_charts", True),
        include_recommendations=export_settings.get("include_recommendations", True),
        auto_save=export_settings.get("auto_save", False)
    )

@router.put("/export")
async def update_export_preferences(
    preferences: ExportPreferences,
    user_id: str = "default"
):
    """Update export preferences."""
    if user_id not in user_settings:
        user_settings[user_id] = {}
    
    user_settings[user_id]["export"] = preferences.dict()
    
    return {
        "success": True,
        "message": "Export preferences updated successfully"
    }

@router.get("/system", response_model=SystemSettings)
async def get_system_settings(api_key: str = Depends(get_api_key_dependency)):
    """Get system settings (admin only)."""
    return SystemSettings(
        api={
            "rate_limit_per_minute": system_settings["rate_limit_per_minute"],
            "max_results_per_page": system_settings["max_results_per_page"],
            "session_timeout_minutes": system_settings["session_timeout_minutes"]
        },
        security={
            "maintenance_mode": system_settings["maintenance_mode"],
            "enable_api_logging": True
        },
        external_services={
            "ollama_endpoint": system_settings["ollama_endpoint"],
            "nvd_api_enabled": bool(system_settings["nvd_api_key"])
        },
        performance={
            "auto_refresh_interval": system_settings["auto_refresh_interval"],
            "max_search_history": system_settings["max_search_history"]
        }
    )

@router.put("/system")
async def update_system_settings(
    settings: SystemSettings,
    api_key: str = Depends(get_api_key_dependency)
):
    """Update system settings (admin only)."""
    # Update system settings
    if settings.api:
        system_settings.update(settings.api)
    if settings.security:
        system_settings.update(settings.security)
    if settings.external_services:
        system_settings.update(settings.external_services)
    if settings.performance:
        system_settings.update(settings.performance)
    
    logger.info("System settings updated by admin")
    
    return {
        "success": True,
        "message": "System settings updated successfully",
        "updated_at": datetime.now().isoformat()
    }

@router.get("/defaults")
async def get_default_settings():
    """Get default settings for all categories."""
    return {
        "user_defaults": {
            "general": {
                "auto_refresh": False,
                "show_tooltips": True,
                "default_search_source": "both",
                "default_results_per_page": 25,
                "dark_mode": False
            },
            "notifications": {
                "email_enabled": False,
                "critical_cves": True,
                "watchlist_updates": True,
                "analysis_complete": False
            },
            "export": {
                "default_format": "pdf",
                "template": "executive",
                "include_charts": True,
                "include_recommendations": True
            }
        },
        "system_defaults": system_settings
    }

@router.post("/reset")
async def reset_user_settings(user_id: str = "default"):
    """Reset user settings to defaults."""
    if user_id in user_settings:
        del user_settings[user_id]
    
    return {
        "success": True,
        "message": "User settings reset to defaults"
    }

@router.get("/export-all")
async def export_all_settings(api_key: str = Depends(get_api_key_dependency)):
    """Export all settings for backup (admin only)."""
    return {
        "timestamp": datetime.now().isoformat(),
        "user_settings": user_settings,
        "system_settings": system_settings,
        "version": "1.0.0"
    }

@router.post("/import-all")
async def import_all_settings(
    settings_data: Dict[str, Any],
    api_key: str = Depends(get_api_key_dependency)
):
    """Import settings from backup (admin only)."""
    try:
        if "user_settings" in settings_data:
            user_settings.update(settings_data["user_settings"])
        
        if "system_settings" in settings_data:
            system_settings.update(settings_data["system_settings"])
        
        return {
            "success": True,
            "message": "Settings imported successfully",
            "imported_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

@router.get("/validate")
async def validate_settings(user_id: str = "default"):
    """Validate current settings and return any issues."""
    issues = []
    settings = user_settings.get(user_id, {})
    
    # Validate notification settings
    notif = settings.get("notifications", {})
    if notif.get("email_enabled") and not notif.get("email_address"):
        issues.append("Email notifications enabled but no email address provided")
    
    # Validate export settings
    export = settings.get("export", {})
    if export.get("default_format") not in ["pdf", "json", "csv", "html"]:
        issues.append("Invalid default export format")
    
    # Validate general settings
    general = settings.get("general", {})
    if general.get("default_results_per_page", 0) > system_settings["max_results_per_page"]:
        issues.append(f"Results per page exceeds maximum ({system_settings['max_results_per_page']})")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "validated_at": datetime.now().isoformat()
    } 