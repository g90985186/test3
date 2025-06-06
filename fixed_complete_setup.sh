#!/bin/bash

echo "🚀 CVE Analysis Platform - Fixed Complete Setup"
echo "==============================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Step 1: Fix database permissions
echo ""
echo "🗄️ Step 1: Fixing database permissions..."

if [ -f "fix_database.sh" ]; then
    chmod +x fix_database.sh
    ./fix_database.sh
else
    print_warning "fix_database.sh not found - run database fix manually"
fi

# Step 2: Fix Python dependencies
echo ""
echo "🐍 Step 2: Fixing Python dependencies..."

if [ -f "fix_dependencies.sh" ]; then
    chmod +x fix_dependencies.sh
    ./fix_dependencies.sh
else
    # Inline fix
    print_info "Fixing dependencies inline..."
    source venv/bin/activate 2>/dev/null || python3.11 -m venv venv && source venv/bin/activate
    pip install --upgrade pip
    pip install aiohttp==3.8.6 fastapi==0.104.1 uvicorn==0.24.0 sqlalchemy==2.0.23 psycopg2-binary==2.9.7
    print_status "Core dependencies installed"
fi

# Step 3: Initialize database with proper permissions
echo ""
echo "🗄️ Step 3: Reinitializing database..."

if [ -f "scripts/init_db.py" ]; then
    source venv/bin/activate
    python scripts/init_db.py
    if [ $? -eq 0 ]; then
        print_status "Database initialized successfully"
    else
        print_error "Database initialization failed"
    fi
else
    print_error "scripts/init_db.py not found"
fi

# Step 4: Test AI models
echo ""
echo "🤖 Step 4: Testing AI models..."

if [ -f "scripts/load_models.py" ]; then
    source venv/bin/activate
    python scripts/load_models.py
    if [ $? -eq 0 ]; then
        print_status "AI models verified successfully"
    else
        print_warning "AI model verification had issues"
    fi
else
    print_error "scripts/load_models.py not found"
fi

# Step 5: Test application imports
echo ""
echo "🧪 Step 5: Testing application..."

source venv/bin/activate

print_info "Testing core imports..."
python -c "from app.main import app; print('✅ Main app import successful')" 2>/dev/null && print_status "App imports working" || print_error "App import failed"

python -c "from app.database import engine; print('✅ Database import successful')" 2>/dev/null && print_status "Database imports working" || print_error "Database import failed"

python -c "from app.services.ollama_service import OllamaService; print('✅ Ollama service import successful')" 2>/dev/null && print_status "Ollama service imports working" || print_error "Ollama service import failed"

# Step 6: Create startup script
echo ""
echo "🚀 Step 6: Creating startup script..."

cat > start_platform.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting CVE Analysis Platform"
echo "================================="

# Activate virtual environment
source venv/bin/activate

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Check if PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
fi

# Start the application
echo "Starting FastAPI application..."
python run.py

EOF

chmod +x start_platform.sh
print_status "Startup script created: ./start_platform.sh"

# Step 7: Final verification
echo ""
echo "📊 Final Verification"
echo "===================="

# Check components
check_component() {
    if [ "$2" = "true" ]; then
        echo -e "✅ $1"
        return 0
    else
        echo -e "❌ $1"
        return 1
    fi
}

# Test each component
APP_MAIN_EXISTS="false"
[ -f "app/main.py" ] && APP_MAIN_EXISTS="true"

ENV_EXISTS="false"
[ -f ".env" ] && ENV_EXISTS="true"

VENV_EXISTS="false"
[ -d "venv" ] && VENV_EXISTS="true"

REQUIREMENTS_EXISTS="false"
[ -f "requirements.txt" ] && REQUIREMENTS_EXISTS="true"

DB_RUNNING="false"
systemctl is-active --quiet postgresql && DB_RUNNING="true"

OLLAMA_RUNNING="false"
curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && OLLAMA_RUNNING="true"

# Display results
check_component "Application Files" $APP_MAIN_EXISTS
check_component "Environment Config" $ENV_EXISTS
check_component "Python Virtual Env" $VENV_EXISTS
check_component "Requirements File" $REQUIREMENTS_EXISTS
check_component "PostgreSQL Service" $DB_RUNNING
check_component "Ollama AI Service" $OLLAMA_RUNNING

echo ""
echo "💾 System Resources:"
echo "RAM: $(free -h | awk '/^Mem:/ {print $2 " total, " $7 " available"}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $4 " available"}')"

echo ""
if [ "$APP_MAIN_EXISTS" = "true" ] && [ "$ENV_EXISTS" = "true" ] && [ "$VENV_EXISTS" = "true" ]; then
    print_status "🎉 Platform is ready to start!"
    echo ""
    print_info "Start the platform:"
    echo "  ./start_platform.sh"
    echo ""
    print_info "Or manually:"
    echo "  source venv/bin/activate"
    echo "  python run.py"
    echo ""
    print_info "Access points:"
    echo "  • Web Interface: http://localhost:8000/static/frontend/index.html"
    echo "  • API Documentation: http://localhost:8000/docs"
    echo "  • Health Check: http://localhost:8000/health"
else
    print_warning "Setup issues detected. Please fix the failed components above."
    echo ""
    print_info "Common fixes:"
    echo "• Missing files: Run the setup scripts again"
    echo "• Database issues: ./fix_database.sh"
    echo "• Python issues: ./fix_dependencies.sh"
fi

echo ""
print_info "Setup completed! Check any failed items above and retry if needed."
