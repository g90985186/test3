from fastapi import HTTPException, Security, Depends, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request
from starlette.responses import Response
from typing import Optional, Union
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute
MAX_REQUESTS_PER_WINDOW = 100

# In-memory rate limiting storage (replace with Redis in production)
request_counts = defaultdict(list)

# Authentication configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify the API key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required"
        )
    
    # In production, validate against a database or environment variable
    if api_key != "your-secure-api-key":  # Replace with actual validation
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return api_key

async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> str:
    """Verify JWT token using the auth service."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required"
        )
    
    # Import here to avoid circular imports
    from app.api.routes.auth import auth_service
    
    user_id = auth_service._verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user_id

async def verify_auth(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> str:
    """Verify authentication using either API key or JWT token."""
    
    # Try API key first
    if api_key:
        try:
            return await verify_api_key(api_key)
        except HTTPException:
            pass  # Fall through to token auth
    
    # Try JWT token
    if credentials:
        try:
            return await verify_jwt_token(credentials)
        except HTTPException:
            pass  # Fall through to error
    
    # No valid authentication found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide either X-API-Key header or Bearer token.",
        headers={"WWW-Authenticate": "Bearer"}
    )

async def verify_admin_auth(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> str:
    """Verify authentication and ensure admin role."""
    
    # Verify basic authentication first
    auth_result = await verify_auth(api_key, credentials)
    
    # For API key, assume admin (in production, check permissions)
    if api_key:
        return auth_result
    
    # For JWT token, check user role
    if credentials:
        from app.api.routes.auth import auth_service, users_db
        user_id = auth_service._verify_token(credentials.credentials)
        if user_id and users_db.get(user_id, {}).get("role") == "admin":
            return user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check rate limit
    if len(request_counts[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return Response(
            content="Rate limit exceeded",
            status_code=429
        )
    
    # Add current request
    request_counts[client_ip].append(current_time)
    
    # Process request
    response = await call_next(request)
    return response

# Dependency functions
def get_api_key_dependency():
    """Get API key only dependency for routes."""
    return Depends(verify_api_key)

def get_auth_dependency():
    """Get flexible authentication dependency (API key or JWT)."""
    return verify_auth

def get_admin_dependency():
    """Get admin authentication dependency."""
    return verify_admin_auth 