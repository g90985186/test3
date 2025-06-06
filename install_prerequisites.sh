#!/bin/bash

echo "🐧 CVE Analysis Platform - Ubuntu Prerequisites Setup"
echo "===================================================="

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🔍 Checking current system..."
print_info "OS: $(lsb_release -d | cut -f2)"
print_info "Kernel: $(uname -r)"
print_info "Architecture: $(uname -m)"

# Step 1: Update system
echo ""
echo "📦 Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_status "System updated"

# Step 2: Install basic development tools
echo ""
echo "🔧 Step 2: Installing development tools..."
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    tree \
    htop \
    vim \
    unzip
print_status "Development tools installed"

# Step 3: Install Python 3.11
echo ""
echo "🐍 Step 3: Installing Python 3.11..."
if command_exists python3.11; then
    print_status "Python 3.11 already installed: $(python3.11 --version)"
else
    # Add deadsnakes PPA for Python 3.11
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
    
    # Set Python 3.11 as default python3 (optional)
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    
    print_status "Python 3.11 installed: $(python3.11 --version)"
fi

# Install pip for Python 3.11
if ! python3.11 -m pip --version >/dev/null 2>&1; then
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
    print_status "pip installed for Python 3.11"
fi

# Step 4: Install PostgreSQL
echo ""
echo "🐘 Step 4: Installing PostgreSQL..."
if command_exists psql; then
    print_status "PostgreSQL already installed: $(psql --version)"
else
    sudo apt install -y postgresql postgresql-contrib postgresql-client
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    print_status "PostgreSQL installed and started"
fi

# Step 5: Install Redis
echo ""
echo "🔴 Step 5: Installing Redis..."
if command_exists redis-server; then
    print_status "Redis already installed: $(redis-server --version)"
else
    sudo apt install -y redis-server
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    print_status "Redis installed and started"
fi

# Step 6: Install Docker
echo ""
echo "🐳 Step 6: Installing Docker..."
if command_exists docker; then
    print_status "Docker already installed: $(docker --version)"
else
    # Remove old versions
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    print_status "Docker installed: $(sudo docker --version)"
    print_warning "You need to log out and back in for Docker group membership to take effect"
fi

# Step 7: Install Docker Compose
echo ""
echo "🐙 Step 7: Installing Docker Compose..."
if command_exists docker-compose; then
    print_status "Docker Compose already installed: $(docker-compose --version)"
else
    # Get latest version
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_status "Docker Compose installed: $(docker-compose --version)"
fi

# Step 8: Install Ollama
echo ""
echo "🤖 Step 8: Installing Ollama..."
if command_exists ollama; then
    print_status "Ollama already installed"
else
    curl -fsSL https://ollama.ai/install.sh | sh
    print_status "Ollama installed"
fi

# Step 9: System configuration
echo ""
echo "⚙️  Step 9: System configuration..."

# Increase file descriptor limits for better performance
if ! grep -q "* soft nofile 65536" /etc/security/limits.conf; then
    echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
    echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
    print_status "File descriptor limits increased"
fi

# Configure PostgreSQL
echo ""
echo "🛠️  Configuring PostgreSQL..."
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';" 2>/dev/null || true

# Create CVE database and user
sudo -u postgres createdb cvedb 2>/dev/null || print_warning "Database 'cvedb' might already exist"
sudo -u postgres psql -c "CREATE USER cveuser WITH PASSWORD 'cvepassword';" 2>/dev/null || print_warning "User 'cveuser' might already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cvedb TO cveuser;" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER cveuser CREATEDB;" 2>/dev/null || true

print_status "PostgreSQL configured"

# Test Redis
echo ""
echo "🧪 Testing Redis connection..."
if redis-cli ping | grep -q PONG; then
    print_status "Redis is working correctly"
else
    print_error "Redis connection failed"
fi

# Step 10: Summary and next steps
echo ""
echo "🎉 Installation Summary"
echo "======================"
print_info "Python: $(python3.11 --version 2>/dev/null || echo 'Not found')"
print_info "PostgreSQL: $(psql --version 2>/dev/null || echo 'Not found')"
print_info "Redis: $(redis-server --version 2>/dev/null || echo 'Not found')"
print_info "Docker: $(sudo docker --version 2>/dev/null || echo 'Not found')"
print_info "Docker Compose: $(docker-compose --version 2>/dev/null || echo 'Not found')"
print_info "Ollama: $(ollama --version 2>/dev/null || echo 'Installed')"

echo ""
echo "📋 Next Steps:"
echo "1. Log out and log back in (or run: newgrp docker)"
echo "2. Test Docker: docker run hello-world"
echo "3. Start Ollama: ollama serve"
echo "4. Download AI models (we'll do this in Step 3)"
echo "5. Create the project files"

echo ""
echo "⚠️  IMPORTANT: You may need to restart your terminal or run 'newgrp docker' for Docker permissions to work"

# Check available memory
echo ""
echo "💾 System Resources:"
echo "RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $4 " available"}')"

echo ""
print_status "Prerequisites installation complete!"
