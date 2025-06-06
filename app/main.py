from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
from app.database import engine, Base
from app.api.routes import cve, analysis, dashboard, chat, watchlist, reports, auth, poc, monitoring, notifications
from app.api.routes import settings as settings_router
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting CVE Analysis Platform...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize AI service
    try:
        from app.services.ai_service import ai_service
        logger.info("Initializing Local AI Service...")
        ai_initialized = await ai_service.initialize()
        if ai_initialized:
            logger.info("Local AI Service initialized successfully")
        else:
            logger.warning("Local AI Service initialized in fallback mode")
    except Exception as e:
        logger.error(f"Failed to initialize AI service: {e}")
    
    logger.info("Application started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down CVE Analysis Platform...")

app = FastAPI(
    title="CVE Analysis Platform",
    description="AI-powered CVE Analysis Platform with PoC Generation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers without API key protection for now
app.include_router(
    cve.router,
    prefix="/api/v1/cve",
    tags=["CVE"]
)
app.include_router(
    analysis.router,
    prefix="/api/v1/analysis",
    tags=["Analysis"]
)
app.include_router(
    dashboard.router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)
app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["Chat"]
)
app.include_router(
    watchlist.router,
    prefix="/api/v1/watchlist",
    tags=["Watchlist"]
)
app.include_router(
    reports.router,
    prefix="/api/v1/reports",
    tags=["Reports"]
)
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)
app.include_router(
    poc.router,
    prefix="/api/v1/poc",
    tags=["PoC"]
)
app.include_router(
    monitoring.router,
    prefix="/api/v1/monitoring",
    tags=["Monitoring"]
)
app.include_router(
    settings_router.router,
    prefix="/api/v1/settings",
    tags=["Settings"]
)
app.include_router(
    notifications.router,
    prefix="/api/v1/notifications",
    tags=["Notifications"]
)

# Serve static files for backend
app.mount("/api/static", StaticFiles(directory="app/static"), name="static")

# Serve frontend static files  
app.mount("/static", StaticFiles(directory="app/static/frontend"), name="frontend")

@app.get("/")
async def root():
    """Serve the main frontend application."""
    return FileResponse('app/static/frontend/index.html')

@app.get("/api/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": "CVE Analysis Platform",
        "version": "1.0.0",
        "description": "AI-powered CVE Analysis Platform with PoC Generation",
        "endpoints": {
            "auth": "/api/v1/auth",
            "cve": "/api/v1/cve",
            "analysis": "/api/v1/analysis",
            "chat": "/api/v1/chat",
            "watchlist": "/api/v1/watchlist",
            "reports": "/api/v1/reports",
            "poc": "/api/v1/poc",
            "dashboard": "/api/v1/dashboard",
            "monitoring": "/api/v1/monitoring",
            "settings": "/api/v1/settings",
            "notifications": "/api/v1/notifications"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "CVE Analysis Platform is running"}

# Serve individual frontend assets at root level for HTML compatibility
@app.get("/styles.css")
async def get_styles():
    return FileResponse('app/static/frontend/styles.css')

@app.get("/app.js")
async def get_app_js():
    return FileResponse('app/static/frontend/app.js')

@app.get("/auth.js")
async def get_auth_js():
    return FileResponse('app/static/frontend/auth.js')
