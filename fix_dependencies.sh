#!/bin/bash

echo "🐍 Fixing Python Dependencies"
echo "============================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_status "Virtual environment found"
    source venv/bin/activate
else
    print_warning "Virtual environment not found, creating new one..."
    python3.11 -m venv venv
    source venv/bin/activate
fi

echo "📦 Installing/updating Python dependencies..."

# Upgrade pip first
pip install --upgrade pip

# Install core dependencies
echo "Installing core web framework dependencies..."
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install python-multipart==0.0.6

echo "Installing database dependencies..."
pip install sqlalchemy==2.0.23
pip install alembic==1.12.1
pip install psycopg2-binary==2.9.7
pip install redis==5.0.1

echo "Installing AI and HTTP dependencies..."
pip install aiohttp==3.8.6
pip install httpx==0.25.2
pip install requests==2.31.0

echo "Installing data processing dependencies..."
pip install numpy==1.24.3
pip install pandas==2.0.3

echo "Installing security dependencies..."
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
pip install python-dotenv==1.0.0

echo "Installing utility dependencies..."
pip install pydantic==2.4.2
pip install pydantic-settings==2.0.3
pip install python-dateutil==2.8.2
pip install aiofiles==23.2.1

echo "Installing development dependencies..."
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1

# Create updated requirements.txt
echo "📝 Creating updated requirements.txt..."
cat > requirements.txt << 'EOF'
# Web Framework
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.7
redis==5.0.1

# AI & HTTP
aiohttp==3.8.6
httpx==0.25.2
requests==2.31.0

# Data Processing
numpy==1.24.3
pandas==2.0.3

# Security & Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Utilities
pydantic==2.4.2
pydantic-settings==2.0.3
python-dateutil==2.8.2
aiofiles==23.2.1

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
EOF

print_status "Dependencies installed successfully"

# Test imports
echo ""
echo "🧪 Testing critical imports..."

python -c "import aiohttp; print('✅ aiohttp imported successfully')" 2>/dev/null && print_status "aiohttp working" || print_error "aiohttp import failed"

python -c "import fastapi; print('✅ FastAPI imported successfully')" 2>/dev/null && print_status "FastAPI working" || print_error "FastAPI import failed"

python -c "import sqlalchemy; print('✅ SQLAlchemy imported successfully')" 2>/dev/null && print_status "SQLAlchemy working" || print_error "SQLAlchemy import failed"

python -c "import psycopg2; print('✅ psycopg2 imported successfully')" 2>/dev/null && print_status "PostgreSQL driver working" || print_error "psycopg2 import failed"

echo ""
print_status "Python dependencies fix completed!"
echo "Virtual environment is active. To reactivate later, run: source venv/bin/activate"
