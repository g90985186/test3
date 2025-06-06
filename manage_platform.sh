#!/bin/bash

case "$1" in
    "start")
        echo "Starting CVE Analysis Platform..."
        ./start_development.sh
        ;;
    "start-prod")
        echo "Starting in production mode..."
        ./start_production.sh
        ;;
    "start-docker")
        echo "Starting with Docker..."
        ./start_docker.sh
        ;;
    "stop")
        echo "Stopping CVE Analysis Platform..."
        pkill -f "uvicorn app.main:app" 2>/dev/null
        pkill -f "python run.py" 2>/dev/null
        docker-compose down 2>/dev/null
        echo "Platform stopped"
        ;;
    "status")
        echo "CVE Analysis Platform Status:"
        echo "=============================="
        
        # Check if application is running
        if pgrep -f "uvicorn app.main:app" >/dev/null; then
            echo "✅ Application: Running"
        else
            echo "❌ Application: Not running"
        fi
        
        # Check PostgreSQL
        if systemctl is-active --quiet postgresql; then
            echo "✅ PostgreSQL: Running"
        else
            echo "❌ PostgreSQL: Not running"
        fi
        
        # Check Ollama
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            echo "✅ Ollama: Running"
        else
            echo "❌ Ollama: Not running"
        fi
        
        # Check web access
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo "✅ Web API: Accessible"
        else
            echo "❌ Web API: Not accessible"
        fi
        ;;
    "test")
        echo "Running platform tests..."
        source venv/bin/activate
        python scripts/load_models.py
        ;;
    *)
        echo "Usage: $0 {start|start-prod|start-docker|stop|status|test}"
        echo ""
        echo "Commands:"
        echo "  start        - Start in development mode"
        echo "  start-prod   - Start in production mode"
        echo "  start-docker - Start with Docker Compose"
        echo "  stop         - Stop all services"
        echo "  status       - Check service status"
        echo "  test         - Test AI models"
        ;;
esac
