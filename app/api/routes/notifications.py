from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import uuid
import logging
from app.core.security import get_api_key_dependency

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage (in production, use database)
notifications = {}  # user_id -> list of notifications
notification_preferences = {}  # user_id -> preferences
email_queue = []  # Email notifications to be sent

class Notification(BaseModel):
    """Notification model."""
    id: str
    title: str
    message: str
    type: str = Field(..., description="Type: info, warning, error, success, critical")
    read: bool = False
    created_at: datetime
    expires_at: Optional[datetime] = None
    action_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class NotificationCreate(BaseModel):
    """Create notification model."""
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)
    type: str = Field("info", description="Type: info, warning, error, success, critical")
    expires_in_hours: Optional[int] = Field(None, description="Hours until notification expires")
    action_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    target_users: Optional[List[str]] = Field(None, description="Specific users to notify, if None then all users")

class NotificationPreferences(BaseModel):
    """Notification preferences model."""
    email_enabled: bool = False
    email_address: Optional[str] = None
    push_enabled: bool = True
    critical_only: bool = False
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None    # HH:MM format
    categories: Dict[str, bool] = Field(default_factory=lambda: {
        "cve_alerts": True,
        "watchlist_updates": True,
        "analysis_complete": True,
        "system_updates": True,
        "security_alerts": True
    })

class EmailNotification(BaseModel):
    """Email notification model."""
    to_email: str
    subject: str
    body: str
    notification_type: str
    created_at: datetime
    sent: bool = False

@router.get("/")
async def get_notifications(
    user_id: str = "default",
    limit: int = 50,
    unread_only: bool = False,
    type_filter: Optional[str] = None
):
    """Get user notifications."""
    user_notifications = notifications.get(user_id, [])
    
    # Filter by read status
    if unread_only:
        user_notifications = [n for n in user_notifications if not n["read"]]
    
    # Filter by type
    if type_filter:
        user_notifications = [n for n in user_notifications if n["type"] == type_filter]
    
    # Remove expired notifications
    now = datetime.now()
    user_notifications = [
        n for n in user_notifications 
        if not n.get("expires_at") or datetime.fromisoformat(n["expires_at"]) > now
    ]
    
    # Sort by created_at descending
    user_notifications = sorted(
        user_notifications, 
        key=lambda x: x["created_at"], 
        reverse=True
    )
    
    return user_notifications[:limit]

@router.post("/")
async def create_notification(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key_dependency)
):
    """Create a new notification."""
    notification_id = str(uuid.uuid4())
    
    # Calculate expiration
    expires_at = None
    if notification.expires_in_hours:
        expires_at = datetime.now() + timedelta(hours=notification.expires_in_hours)
    
    # Create notification object
    notif_data = {
        "id": notification_id,
        "title": notification.title,
        "message": notification.message,
        "type": notification.type,
        "read": False,
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "action_url": notification.action_url,
        "metadata": notification.metadata or {}
    }
    
    # Determine target users
    target_users = notification.target_users or ["default"]  # Default to all users
    
    # Add notification to each target user
    created_count = 0
    for user_id in target_users:
        if user_id not in notifications:
            notifications[user_id] = []
        
        notifications[user_id].append(notif_data.copy())
        created_count += 1
        
        # Check if user wants email notifications
        user_prefs = notification_preferences.get(user_id, {})
        if (user_prefs.get("email_enabled", False) and 
            user_prefs.get("email_address") and
            _should_send_email(notification.type, user_prefs)):
            
            background_tasks.add_task(
                _queue_email_notification,
                user_prefs["email_address"],
                notification.title,
                notification.message,
                notification.type
            )
    
    logger.info(f"Created notification {notification_id} for {created_count} users")
    
    return {
        "success": True,
        "notification_id": notification_id,
        "created_for_users": created_count,
        "message": "Notification created successfully"
    }

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user_id: str = "default"
):
    """Mark a notification as read."""
    user_notifications = notifications.get(user_id, [])
    
    for notif in user_notifications:
        if notif["id"] == notification_id:
            notif["read"] = True
            return {
                "success": True,
                "message": "Notification marked as read"
            }
    
    raise HTTPException(status_code=404, detail="Notification not found")

@router.put("/mark-all-read")
async def mark_all_notifications_read(user_id: str = "default"):
    """Mark all notifications as read for a user."""
    user_notifications = notifications.get(user_id, [])
    
    read_count = 0
    for notif in user_notifications:
        if not notif["read"]:
            notif["read"] = True
            read_count += 1
    
    return {
        "success": True,
        "marked_read": read_count,
        "message": f"Marked {read_count} notifications as read"
    }

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    user_id: str = "default"
):
    """Delete a specific notification."""
    user_notifications = notifications.get(user_id, [])
    
    for i, notif in enumerate(user_notifications):
        if notif["id"] == notification_id:
            del user_notifications[i]
            return {
                "success": True,
                "message": "Notification deleted"
            }
    
    raise HTTPException(status_code=404, detail="Notification not found")

@router.delete("/clear-all")
async def clear_all_notifications(user_id: str = "default"):
    """Clear all notifications for a user."""
    if user_id in notifications:
        count = len(notifications[user_id])
        notifications[user_id] = []
        return {
            "success": True,
            "cleared_count": count,
            "message": f"Cleared {count} notifications"
        }
    
    return {
        "success": True,
        "cleared_count": 0,
        "message": "No notifications to clear"
    }

@router.get("/stats")
async def get_notification_stats(user_id: str = "default"):
    """Get notification statistics for a user."""
    user_notifications = notifications.get(user_id, [])
    
    total = len(user_notifications)
    unread = len([n for n in user_notifications if not n["read"]])
    
    # Count by type
    type_counts = {}
    for notif in user_notifications:
        notif_type = notif["type"]
        type_counts[notif_type] = type_counts.get(notif_type, 0) + 1
    
    # Recent notifications (last 24 hours)
    recent_cutoff = datetime.now() - timedelta(hours=24)
    recent = len([
        n for n in user_notifications 
        if datetime.fromisoformat(n["created_at"]) > recent_cutoff
    ])
    
    return {
        "total_notifications": total,
        "unread_notifications": unread,
        "recent_notifications": recent,
        "notifications_by_type": type_counts,
        "last_notification": user_notifications[0]["created_at"] if user_notifications else None
    }

@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(user_id: str = "default"):
    """Get notification preferences for a user."""
    prefs = notification_preferences.get(user_id, {})
    
    return NotificationPreferences(
        email_enabled=prefs.get("email_enabled", False),
        email_address=prefs.get("email_address"),
        push_enabled=prefs.get("push_enabled", True),
        critical_only=prefs.get("critical_only", False),
        quiet_hours_start=prefs.get("quiet_hours_start"),
        quiet_hours_end=prefs.get("quiet_hours_end"),
        categories=prefs.get("categories", {
            "cve_alerts": True,
            "watchlist_updates": True,
            "analysis_complete": True,
            "system_updates": True,
            "security_alerts": True
        })
    )

@router.put("/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    user_id: str = "default"
):
    """Update notification preferences for a user."""
    notification_preferences[user_id] = preferences.dict()
    
    logger.info(f"Updated notification preferences for user {user_id}")
    
    return {
        "success": True,
        "message": "Notification preferences updated successfully"
    }

@router.post("/test")
async def send_test_notification(
    user_id: str = "default",
    notification_type: str = "info"
):
    """Send a test notification to verify settings."""
    test_notif = {
        "id": str(uuid.uuid4()),
        "title": "Test Notification",
        "message": f"This is a test {notification_type} notification to verify your settings.",
        "type": notification_type,
        "read": False,
        "created_at": datetime.now().isoformat(),
        "expires_at": None,
        "action_url": None,
        "metadata": {"test": True}
    }
    
    if user_id not in notifications:
        notifications[user_id] = []
    
    notifications[user_id].append(test_notif)
    
    return {
        "success": True,
        "message": "Test notification sent",
        "notification_id": test_notif["id"]
    }

@router.get("/email-queue")
async def get_email_queue(api_key: str = Depends(get_api_key_dependency)):
    """Get pending email notifications (admin only)."""
    return {
        "pending_emails": len([e for e in email_queue if not e["sent"]]),
        "total_emails": len(email_queue),
        "queue": email_queue[-10:]  # Last 10 emails
    }

@router.post("/cleanup")
async def cleanup_notifications(
    days_old: int = 30,
    api_key: str = Depends(get_api_key_dependency)
):
    """Clean up old notifications (admin only)."""
    cutoff_date = datetime.now() - timedelta(days=days_old)
    cleaned_count = 0
    
    for user_id in notifications:
        original_count = len(notifications[user_id])
        notifications[user_id] = [
            n for n in notifications[user_id]
            if datetime.fromisoformat(n["created_at"]) > cutoff_date
        ]
        cleaned_count += original_count - len(notifications[user_id])
    
    return {
        "success": True,
        "cleaned_notifications": cleaned_count,
        "cutoff_date": cutoff_date.isoformat()
    }

# Helper functions
def _should_send_email(notification_type: str, user_prefs: dict) -> bool:
    """Determine if an email should be sent based on user preferences."""
    if not user_prefs.get("email_enabled", False):
        return False
    
    if user_prefs.get("critical_only", False) and notification_type != "critical":
        return False
    
    # Check quiet hours
    now = datetime.now().time()
    quiet_start = user_prefs.get("quiet_hours_start")
    quiet_end = user_prefs.get("quiet_hours_end")
    
    if quiet_start and quiet_end:
        try:
            start_time = datetime.strptime(quiet_start, "%H:%M").time()
            end_time = datetime.strptime(quiet_end, "%H:%M").time()
            
            if start_time <= end_time:
                # Same day quiet hours
                if start_time <= now <= end_time:
                    return False
            else:
                # Overnight quiet hours
                if now >= start_time or now <= end_time:
                    return False
        except ValueError:
            pass  # Invalid time format, ignore quiet hours
    
    return True

async def _queue_email_notification(email: str, subject: str, body: str, notif_type: str):
    """Queue an email notification for sending."""
    email_notif = {
        "to_email": email,
        "subject": f"[CVE Platform] {subject}",
        "body": body,
        "notification_type": notif_type,
        "created_at": datetime.now().isoformat(),
        "sent": False
    }
    
    email_queue.append(email_notif)
    logger.info(f"Queued email notification to {email}")
    
    # In production, integrate with email service (SendGrid, SES, etc.)
    # For now, just mark as sent after a delay
    import asyncio
    await asyncio.sleep(1)
    email_notif["sent"] = True 