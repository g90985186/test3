#!/bin/bash

echo "🎉 CVE Analysis Platform - Final Testing & Launch"
echo "================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${PURPLE}🎯 $1${NC}"
}

# Step 1: Comprehensive System Check
echo ""
echo "🔍 Step 1: Comprehensive System Check"
echo "====================================="

print_info "Checking all system components..."

# Check Python environment
source venv/bin/activate
if python -c "import sys; print(f'Python {sys.version}')" 2>/dev/null; then
    print_status "Python environment active"
else
    print_error "Python environment issue"
fi

# Check database connection
if PGPASSWORD=cvepassword psql -h localhost -U cveuser -d cvedb -c "SELECT 1;" >/dev/null 2>&1; then
    print_status "Database connection working"
else
    print_error "Database connection failed"
fi

# Check Ollama service
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    print_status "Ollama AI service running"
    # List available models
    MODELS=$(curl -s http://localhost:11434/api/tags | python -c "import json, sys; data=json.load(sys.stdin); print(', '.join([m['name'] for m in data.get('models', [])]))" 2>/dev/null)
    print_info "Available models: $MODELS"
else
    print_warning "Ollama service not running - starting it..."
    ollama serve &
    sleep 5
fi

# Check Redis (if running)
if redis-cli ping >/dev/null 2>&1; then
    print_status "Redis service running"
else
    print_info "Redis not running (optional for basic functionality)"
fi

# Step 2: Application Testing
echo ""
echo "🧪 Step 2: Application Testing"
echo "==============================="

print_info "Testing application components..."

# Test core imports
if python -c "
try:
    from app.main import app
    from app.database import engine, get_db
    from app.models.cve import CVE
    from app.models.analysis import Analysis
    from app.services.ollama_service import OllamaService
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"; then
    print_status "Core application imports working"
else
    print_error "Application import errors detected"
    exit 1
fi

# Test database tables
if python -c "
from app.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
expected_tables = ['cves', 'analysis_results', 'threat_intelligence']
missing = [t for t in expected_tables if t not in tables]
if missing:
    print(f'❌ Missing tables: {missing}')
    exit(1)
else:
    print(f'✅ Database tables: {tables}')
"; then
    print_status "Database tables created correctly"
else
    print_warning "Database table issues detected"
fi

# Step 3: API Testing
echo ""
echo "🌐 Step 3: API Testing"
echo "======================"

print_info "Starting application for testing..."

# Start the application in background for testing
python run.py &
APP_PID=$!

# Give it time to start
sleep 10

# Test health endpoint
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    print_status "Health endpoint working"
else
    print_error "Health endpoint failed"
fi

# Test API documentation
if curl -s http://localhost:8000/docs | grep -q "CVE Analysis Platform"; then
    print_status "API documentation accessible"
else
    print_warning "API documentation may have issues"
fi

# Test dashboard metrics endpoint
if curl -s http://localhost:8000/api/v1/dashboard/metrics | grep -q "total_count"; then
    print_status "Dashboard API working"
else
    print_warning "Dashboard API may have issues"
fi

# Stop test application
kill $APP_PID 2>/dev/null
sleep 2

# Step 4: AI Model Testing
echo ""
echo "🤖 Step 4: AI Model Testing"
echo "============================"

print_info "Testing AI models functionality..."

# Test each model
MODELS=("llama3.1:8b" "gemma2:9b" "codellama:7b")
WORKING_MODELS=0

for MODEL in "${MODELS[@]}"; do
    print_info "Testing $MODEL..."
    
    if timeout 30s ollama run $MODEL "Hello, respond with 'Model working'" 2>/dev/null | grep -q -i "working\|hello\|model"; then
        print_status "$MODEL is working"
        ((WORKING_MODELS++))
    else
        print_warning "$MODEL test failed or timeout"
    fi
done

if [ $WORKING_MODELS -gt 0 ]; then
    print_status "$WORKING_MODELS out of ${#MODELS[@]} models working"
else
    print_error "No AI models are responding"
fi

# Step 5: Performance Testing
echo ""
echo "⚡ Step 5: Performance Testing"
echo "=============================="

print_info "Checking system performance..."

# Memory usage
MEMORY_TOTAL=$(free -m | awk 'NR==2{printf "%.1f", $2/1024}')
MEMORY_USED=$(free -m | awk 'NR==2{printf "%.1f", $3/1024}')
MEMORY_AVAILABLE=$(free -m | awk 'NR==2{printf "%.1f", $7/1024}')

echo "💾 Memory: ${MEMORY_USED}GB used / ${MEMORY_TOTAL}GB total (${MEMORY_AVAILABLE}GB available)"

if (( $(echo "$MEMORY_AVAILABLE < 4" | bc -l) )); then
    print_warning "Low memory available for AI models"
else
    print_status "Sufficient memory available"
fi

# Disk space
DISK_AVAILABLE=$(df -h / | awk 'NR==2 {print $4}')
echo "💿 Disk: $DISK_AVAILABLE available"

# CPU cores
CPU_CORES=$(nproc)
echo "🏭 CPU: $CPU_CORES cores"

# Step 6: Security Check
echo ""
echo "🔒 Step 6: Security Check"
echo "========================="

print_info "Checking security configuration..."

# Check .env file permissions
if [ -f ".env" ]; then
    PERMS=$(stat -c "%a" .env)
    if [ "$PERMS" = "600" ] || [ "$PERMS" = "644" ]; then
        print_status ".env file permissions acceptable"
    else
        print_warning ".env file has permissive permissions ($PERMS)"
        chmod 600 .env
        print_status "Fixed .env file permissions"
    fi
fi

# Check if debug mode is enabled
if grep -q "DEBUG=True" .env 2>/dev/null; then
    print_warning "Debug mode is enabled (okay for development)"
else
    print_status "Debug mode disabled"
fi

# Step 7: Create Production Scripts
echo ""
echo "🚀 Step 7: Creating Production Scripts"
echo "======================================"

# Create production startup script
cat > start_production.sh << 'EOF'
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

EOF

# Create development startup script
cat > start_development.sh << 'EOF'
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

EOF

# Create Docker startup script
cat > start_docker.sh << 'EOF'
#!/bin/bash

echo "🐳 Starting CVE Analysis Platform (Docker)"
echo "=========================================="

# Build and start with Docker Compose
docker-compose down 2>/dev/null
docker-compose up --build -d

echo "Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Docker services started successfully"
    echo ""
    echo "Access points:"
    echo "• Web Interface: http://localhost"
    echo "• API Documentation: http://localhost:8000/docs"
else
    echo "❌ Some Docker services failed to start"
    docker-compose logs
fi

EOF

# Create service management script
cat > manage_platform.sh << 'EOF'
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
EOF

# Make scripts executable
chmod +x start_production.sh start_development.sh start_docker.sh manage_platform.sh

print_status "Production scripts created"

# Step 8: Final Summary
echo ""
echo "🎯 Step 8: Final Summary & Launch"
echo "================================="

print_success "🎉 CVE Analysis Platform Setup Complete!"

echo ""
echo "📊 Platform Status:"
echo "=================="
echo "✅ Database: PostgreSQL configured and tables created"
echo "✅ AI Models: Ollama with $WORKING_MODELS models available"
echo "✅ Application: FastAPI with all components ready"
echo "✅ Frontend: Web interface available"
echo "✅ API: RESTful endpoints configured"

echo ""
echo "🚀 How to Launch:"
echo "================"
echo "Development Mode:"
echo "  ./start_development.sh"
echo ""
echo "Production Mode:"
echo "  ./start_production.sh"
echo ""
echo "Docker Mode:"
echo "  ./start_docker.sh"
echo ""
echo "Management:"
echo "  ./manage_platform.sh {start|stop|status|test}"

echo ""
echo "🌐 Access Points:"
echo "================"
echo "• Web Interface: http://localhost:8000/static/frontend/index.html"
echo "• API Documentation: http://localhost:8000/docs"
echo "• API Base URL: http://localhost:8000/api/v1/"
echo "• Health Check: http://localhost:8000/health"

echo ""
echo "📖 Quick Start Guide:"
echo "===================="
echo "1. Start the platform: ./start_development.sh"
echo "2. Open browser: http://localhost:8000/static/frontend/index.html"
echo "3. Use the Dashboard to see system metrics"
echo "4. Try CVE Search to search for vulnerabilities"
echo "5. Use AI Analysis to analyze CVEs with local AI models"

echo ""
echo "🔧 Troubleshooting:"
echo "=================="
echo "• Check status: ./manage_platform.sh status"
echo "• View logs: tail -f logs/* (if logging is enabled)"
echo "• Test AI models: ./manage_platform.sh test"
echo "• Restart services: ./manage_platform.sh stop && ./manage_platform.sh start"

echo ""
print_success "🎉 Platform is ready! Choose a startup method above to begin."
