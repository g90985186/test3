#!/bin/bash

echo "🚀 CVE Analysis Platform - Complete Setup"
echo "=========================================="

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

# Step 1: Create project structure and files
echo ""
echo "📁 Step 1: Setting up project structure..."

# Run the setup scripts
if [ -f "setup_app.py" ]; then
    python3 setup_app.py
    print_status "Basic application files created"
else
    print_warning "setup_app.py not found - create files manually"
fi

if [ -f "setup_models.py" ]; then
    python3 setup_models.py
    print_status "Models and services created"
else
    print_warning "setup_models.py not found - create files manually"
fi

if [ -f "setup_frontend.py" ]; then
    python3 setup_frontend.py
    print_status "Frontend files created"
else
    print_warning "setup_frontend.py not found - create files manually"
fi

# Step 2: Environment setup
echo ""
echo "⚙️  Step 2: Environment configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status ".env file created from template"
        print_warning "Please edit .env file with your specific settings"
    else
        print_error ".env.example not found"
    fi
else
    print_status ".env file already exists"
fi

# Step 3: Python virtual environment
echo ""
echo "🐍 Step 3: Setting up Python environment..."

if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment and install requirements
source venv/bin/activate
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    print_status "Python dependencies installed"
else
    print_error "requirements.txt not found"
fi

# Step 4: Database setup
echo ""
echo "🗄️  Step 4: Database initialization..."

# Check if PostgreSQL is running
if systemctl is-active --quiet postgresql; then
    print_status "PostgreSQL is running"
    
    # Try to initialize database
    if [ -f "scripts/init_db.py" ]; then
        if python scripts/init_db.py; then
            print_status "Database initialized successfully"
        else
            print_warning "Database initialization had issues - check manually"
        fi
    else
        print_error "scripts/init_db.py not found"
    fi
else
    print_warning "PostgreSQL is not running - start it first"
fi

# Step 5: AI models verification
echo ""
echo "🤖 Step 5: AI models verification..."

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    print_status "Ollama service is running"
    
    if [ -f "scripts/load_models.py" ]; then
        if python scripts/load_models.py; then
            print_status "AI models verified successfully"
        else
            print_warning "AI model verification had issues"
        fi
    else
        print_error "scripts/load_models.py not found"
    fi
else
    print_warning "Ollama service is not running"
    print_info "Start it with: ollama serve"
fi

# Step 6: File permissions
echo ""
echo "🔐 Step 6: Setting file permissions..."

# Make scripts executable
if [ -d "scripts" ]; then
    chmod +
