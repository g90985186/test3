#!/bin/bash

echo "🚀 Starting CVE Analysis Platform (Production Mode)"
echo "=================================================="

# Set production environment
export DEBUG=False
export LOG_LEVEL=WARNING

# Activate virtual environment
source venv/bin/activate

# Ensure services are running
if ! systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
fi

if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 10
fi

# Start application with multiple workers
echo "Starting FastAPI application with multiple workers..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

