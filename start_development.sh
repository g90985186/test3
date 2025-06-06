#!/bin/bash

echo "🧪 Starting CVE Analysis Platform (Development Mode)"
echo "==================================================="

# Set development environment
export DEBUG=True
export LOG_LEVEL=INFO

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

# Start application with auto-reload
echo "Starting FastAPI application with auto-reload..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

