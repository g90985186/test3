#!/usr/bin/env python3
"""
CVE Analysis Platform - Application Code Setup
This script creates all the necessary files from the main artifact.
"""

import os
import sys
from pathlib import Path

def create_file(filepath, content):
    """Create a file with the given content"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created: {filepath}")

def setup_application_files():
    """Create all application files"""
    
    print("🚀 Setting up CVE Analysis Platform Application Code")
    print("=" * 55)
    
    # Root configuration files
    files = {
        
        # Requirements
        "requirements.txt": """# Web Framework
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.7
redis==5.0.1

# AI & ML
requests==2.31.0
httpx==0.25.2
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0

# Security & Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Utilities
pydantic==2.4.2
pydantic-settings==2.0.3
python-dateutil==2.8.2
schedule==1.2.0
aiofiles==23.2.1

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.9.1
flake8==6.1.0
""",

        # Docker Compose
        "docker-compose.yml": """version: '3.8'

services:
  # Ollama AI Service
  ollama:
    image: ollama/ollama:latest
    container_name: cve-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    command: >
      sh -c "
        ollama serve &
        sleep 10 &&
        ollama pull llama3.1:8b &&
        ollama pull gemma2:9b &&
        ollama pull codellama:7b &&
        wait
      "

  # PostgreSQL Database
  postgres:
    image: postgres:15
    container_name: cve-postgres
    environment:
      POSTGRES_DB: cvedb
      POSTGRES_USER: cveuser
      POSTGRES_PASSWORD: cvepassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: cve-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # FastAPI Application
  app:
    build: .
    container_name: cve-app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://cveuser:cvepassword@postgres:5432/cvedb
      - REDIS_URL=redis://redis:6379
      - OLLAMA_URL=http://ollama:11434
    depends_on:
      - postgres
      - redis
      - ollama
    volumes:
      - .:/app
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: cve-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  ollama_data:
""",

        # Dockerfile
        "Dockerfile": """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
""",

        # Environment example
        ".env.example": """# Database
DATABASE_URL=postgresql://cveuser:cvepassword@localhost:5432/cvedb

# Redis
REDIS_URL=redis://localhost:6379

# Ollama
OLLAMA_URL=http://localhost:11434

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
NVD_API_KEY=your-nvd-api-key

# Application
DEBUG=True
LOG_LEVEL=INFO
""",

        # Run script
        "run.py": """#!/usr/bin/env python3

import uvicorn
import argparse
import logging
from config.settings import settings

def main():
    parser = argparse.ArgumentParser(description='CVE Analysis Platform')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--workers', type=int, default=1, help='Number of workers')
    parser.add_argument('--log-level', default='info', help='Log level')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()
""",

        # Config settings
        "config/settings.py": """from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://cveuser:cvepassword@localhost:5432/cvedb"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Ollama
    ollama_url: str = "http://localhost:11434"
    
    # Security
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External APIs
    nvd_api_key: Optional[str] = None
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
""",

        # Main app
        "app/main.py": """from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from app.database import engine, Base
from app.api.routes import cve, analysis, dashboard
from app.services.ollama_service import OllamaService
from config.settings import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting CVE Analysis Platform...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize Ollama service
    ollama_service = OllamaService()
    await ollama_service.health_check()
    
    logger.info("Application started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down CVE Analysis Platform...")

app = FastAPI(
    title="CVE Analysis Platform",
    description="AI-powered CVE analysis and vulnerability assessment platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cve.router, prefix="/api/v1/cve", tags=["CVE"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"message": "CVE Analysis Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "CVE Analysis Platform is running"}
""",

        # Database configuration
        "app/database.py": """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
    }
    
    # Create all files
    for filepath, content in files.items():
        create_file(filepath, content)
    
    # Create __init__.py files
    init_files = [
        "config/__init__.py",
        "app/__init__.py", 
        "app/api/__init__.py",
        "app/api/routes/__init__.py",
        "app/models/__init__.py",
        "app/services/__init__.py",
        "app/ai/__init__.py",
        "app/ai/prompts/__init__.py",
        "app/ai/models/__init__.py",
        "app/ai/utils/__init__.py",
        "app/core/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        create_file(init_file, "")
    
    print(f"\n✅ Created {len(files) + len(init_files)} files")
    print("📁 Basic application structure is ready!")

if __name__ == "__main__":
    setup_application_files()
