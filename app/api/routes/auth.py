from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import uuid
import logging
import hashlib
import secrets
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Configuration
SECRET_KEY = "cve-platform-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory storage for users
users_db = {}
user_sessions = {}
api_keys = {}
user_activity = {}

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")
    full_name: Optional[str] = Field(None, description="Full name")
    role: str = Field("user", description="User role: admin, analyst, user")

class UserLogin(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    login_count: int

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class PasswordChange(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class APIKeyCreate(BaseModel):
    name: str = Field(..., description="API key name/description")
    permissions: List[str] = Field(default_factory=list, description="Permissions")

class APIKeyResponse(BaseModel):
    key_id: str
    name: str
    key: str
    permissions: List[str]
    created_at: datetime
    last_used: Optional[datetime]
    is_active: bool

class UserStats(BaseModel):
    total_users: int
    active_users: int
    users_by_role: Dict[str, int]
    recent_logins: int
    api_keys_count: int

class AuthService:
    def __init__(self):
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user if not exists"""
        admin_id = "admin-user-id"
        if admin_id not in users_db:
            admin_user = {
                "user_id": admin_id,
                "username": "admin",
                "email": "admin@cveplatform.com",
                "password_hash": self._hash_password("admin123"),
                "full_name": "System Administrator",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "last_login": None,
                "login_count": 0
            }
            users_db[admin_id] = admin_user
            user_activity[admin_id] = {
                "logins": [],
                "api_calls": 0,
                "reports_generated": 0,
                "last_activity": datetime.utcnow()
            }
            logger.info("Created default admin user: admin/admin123")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def _create_access_token(self, user_id: str, username: str, role: str) -> str:
        """Create simple access token"""
        token_data = f"{user_id}:{username}:{role}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(token_data.encode()).hexdigest()
    
    def _verify_token(self, token: str) -> Optional[str]:
        """Verify token and return user_id"""
        for user_id, session in user_sessions.items():
            if session.get("token") == token:
                # Check if token is still valid (not expired)
                created_at = session.get("created_at")
                if created_at and datetime.utcnow() - created_at < timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES):
                    return user_id
        return None
    
    def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        # Check if username or email already exists
        for user in users_db.values():
            if user["username"] == user_data.username:
                raise HTTPException(
                    status_code=400,
                    detail="Username already registered"
                )
            if user["email"] == user_data.email:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
        
        # Create new user
        user_id = str(uuid.uuid4())
        user = {
            "user_id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": self._hash_password(user_data.password),
            "full_name": user_data.full_name,
            "role": user_data.role,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "login_count": 0
        }
        
        users_db[user_id] = user
        
        # Initialize user activity tracking
        user_activity[user_id] = {
            "logins": [],
            "api_calls": 0,
            "reports_generated": 0,
            "last_activity": datetime.utcnow()
        }
        
        logger.info(f"Registered new user: {user_data.username}")
        return self._to_user_response(user)
    
    def authenticate_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return token"""
        # Find user by username or email
        user = None
        for u in users_db.values():
            if u["username"] == login_data.username or u["email"] == login_data.username:
                user = u
                break
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        if not user["is_active"]:
            raise HTTPException(
                status_code=401,
                detail="Account is inactive"
            )
        
        if not self._verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Update login info
        user["last_login"] = datetime.utcnow()
        user["login_count"] += 1
        
        # Track login activity
        if user["user_id"] in user_activity:
            user_activity[user["user_id"]]["logins"].append(datetime.utcnow())
            user_activity[user["user_id"]]["last_activity"] = datetime.utcnow()
        
        # Create access token
        access_token = self._create_access_token(
            user["user_id"], 
            user["username"], 
            user["role"]
        )
        
        # Store session
        user_sessions[user["user_id"]] = {
            "token": access_token,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        logger.info(f"User authenticated: {user['username']}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=self._to_user_response(user)
        )
    
    def get_current_user(self, token: str) -> UserResponse:
        """Get current user from token"""
        user_id = self._verify_token(token)
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = users_db[user_id]
        if not user["is_active"]:
            raise HTTPException(status_code=401, detail="Account inactive")
        
        return self._to_user_response(user)
    
    def update_user(self, user_id: str, update_data: UserUpdate) -> UserResponse:
        """Update user information"""
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users_db[user_id]
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                user[field] = value
        
        logger.info(f"Updated user: {user['username']}")
        return self._to_user_response(user)
    
    def change_password(self, user_id: str, password_data: PasswordChange) -> Dict[str, str]:
        """Change user password"""
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users_db[user_id]
        
        # Verify current password
        if not self._verify_password(password_data.current_password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        user["password_hash"] = self._hash_password(password_data.new_password)
        
        # Invalidate all sessions
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        logger.info(f"Password changed for user: {user['username']}")
        return {"message": "Password changed successfully"}
    
    def create_api_key(self, user_id: str, key_data: APIKeyCreate) -> APIKeyResponse:
        """Create API key for user"""
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        key_id = str(uuid.uuid4())
        api_key = secrets.token_urlsafe(32)
        
        key_info = {
            "key_id": key_id,
            "user_id": user_id,
            "name": key_data.name,
            "key": api_key,
            "permissions": key_data.permissions,
            "created_at": datetime.utcnow(),
            "last_used": None,
            "is_active": True
        }
        
        api_keys[key_id] = key_info
        
        logger.info(f"Created API key for user {user_id}: {key_data.name}")
        
        return APIKeyResponse(**key_info)
    
    def get_user_stats(self) -> UserStats:
        """Get user statistics"""
        total_users = len(users_db)
        active_users = sum(1 for u in users_db.values() if u["is_active"])
        
        users_by_role = {}
        for user in users_db.values():
            role = user["role"]
            users_by_role[role] = users_by_role.get(role, 0) + 1
        
        # Recent logins (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_logins = sum(
            1 for u in users_db.values() 
            if u["last_login"] and u["last_login"] > yesterday
        )
        
        return UserStats(
            total_users=total_users,
            active_users=active_users,
            users_by_role=users_by_role,
            recent_logins=recent_logins,
            api_keys_count=len(api_keys)
        )
    
    def get_all_users(self, limit: int = 50) -> List[UserResponse]:
        """Get all users"""
        users = list(users_db.values())
        users.sort(key=lambda x: x["created_at"], reverse=True)
        return [self._to_user_response(user) for user in users[:limit]]
    
    def _to_user_response(self, user: Dict[str, Any]) -> UserResponse:
        """Convert user dict to response model"""
        return UserResponse(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            last_login=user["last_login"],
            login_count=user["login_count"]
        )

auth_service = AuthService()

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return auth_service.get_current_user(token)

# Dependency for admin access
async def require_admin(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user

# API Endpoints
@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        return auth_service.register_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    """Authenticate user and get access token"""
    try:
        return auth_service.authenticate_user(login_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update current user information"""
    try:
        return auth_service.update_user(current_user.user_id, update_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Update failed")

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserResponse = Depends(get_current_user)
):
    """Change current user password"""
    try:
        return auth_service.change_password(current_user.user_id, password_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail="Password change failed")

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create API key for current user"""
    try:
        return auth_service.create_api_key(current_user.user_id, key_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        raise HTTPException(status_code=500, detail="API key creation failed")

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    limit: int = 50,
    admin_user: UserResponse = Depends(require_admin)
):
    """Get all users (admin only)"""
    try:
        return auth_service.get_all_users(limit)
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get users")

@router.get("/stats", response_model=UserStats)
async def get_user_stats(admin_user: UserResponse = Depends(require_admin)):
    """Get user statistics (admin only)"""
    try:
        return auth_service.get_user_stats()
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """Logout current user"""
    # Remove session
    if current_user.user_id in user_sessions:
        del user_sessions[current_user.user_id]
    
    logger.info(f"User logged out: {current_user.username}")
    return {"message": "Logged out successfully"}

@router.get("/info")
async def get_auth_info():
    """Get authentication system information"""
    return {
        "authentication": {
            "type": "Bearer Token",
            "token_lifetime": f"{ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
            "supported_roles": ["admin", "analyst", "user"]
        },
        "default_credentials": {
            "username": "admin",
            "password": "admin123",
            "note": "Change default password in production"
        },
        "features": [
            "User Registration",
            "Token-based Authentication", 
            "Role-based Access Control",
            "API Key Management",
            "Password Management",
            "User Activity Tracking"
        ]
    }
