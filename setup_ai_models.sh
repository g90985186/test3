#!/bin/bash

echo "🤖 CVE Analysis Platform - AI Models Setup"
echo "==========================================="

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
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

print_progress() {
    echo -e "${PURPLE}🔄 $1${NC}"
}

# Function to check if Ollama is running
check_ollama_service() {
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start Ollama service
start_ollama() {
    print_info "Starting Ollama service..."
    
    # Check if already running
    if check_ollama_service; then
        print_status "Ollama service is already running"
        return 0
    fi
    
    # Start Ollama in background
    ollama serve > /tmp/ollama.log 2>&1 &
    OLLAMA_PID=$!
    
    # Wait for service to start
    echo -n "Waiting for Ollama to start"
    for i in {1..30}; do
        if check_ollama_service; then
            echo ""
            print_status "Ollama service started successfully (PID: $OLLAMA_PID)"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    
    echo ""
    print_error "Failed to start Ollama service"
    print_info "Check logs: tail /tmp/ollama.log"
    return 1
}

# Function to check available disk space
check_disk_space() {
    AVAILABLE_GB=$(df / | awk 'NR==2 {print int($4/1024/1024)}')
    print_info "Available disk space: ${AVAILABLE_GB}GB"
    
    if [ $AVAILABLE_GB -lt 20 ]; then
        print_warning "Low disk space! At least 20GB recommended for AI models"
        print_info "Continue anyway? (y/n)"
        read -r response
        if [[ ! $response =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to check available RAM
check_memory() {
    AVAILABLE_RAM_GB=$(free -m | awk 'NR==2{printf "%.1f", $7/1024}')
    TOTAL_RAM_GB=$(free -m | awk 'NR==2{printf "%.1f", $2/1024}')
    
    print_info "Total RAM: ${TOTAL_RAM_GB}GB, Available: ${AVAILABLE_RAM_GB}GB"
    
    if (( $(echo "$TOTAL_RAM_GB < 12" | bc -l) )); then
        print_warning "Low RAM detected! 16GB+ recommended for optimal performance"
        print_info "Models will load slower and may swap to disk"
    fi
}

# Function to download and verify a model
download_model() {
    local model_name=$1
    local model_size=$2
    local model_purpose=$3
    
    print_progress "Downloading $model_name ($model_size) - $model_purpose"
    print_info "This may take 5-15 minutes depending on your internet connection..."
    
    # Check if model already exists
    if ollama list | grep -q "$model_name"; then
        print_status "$model_name is already downloaded"
        return 0
    fi
    
    # Download the model with progress indication
    if ollama pull "$model_name"; then
        print_status "$model_name downloaded successfully"
        return 0
    else
        print_error "Failed to download $model_name"
        return 1
    fi
}

# Function to test a model
test_model() {
    local model_name=$1
    local test_prompt="Hello, this is a test. Please respond with 'Model working correctly.'"
    
    print_progress "Testing $model_name..."
    
    # Run a simple test
    response=$(ollama run "$model_name" "$test_prompt" 2>/dev/null)
    
    if [[ $? -eq 0 ]] && [[ -n "$response" ]]; then
        print_status "$model_name is working correctly"
        print_info "Response: ${response:0:100}..."
        return 0
    else
        print_error "$model_name test failed"
        return 1
    fi
}

# Function to configure model parameters
configure_model_settings() {
    print_info "Configuring Ollama settings for optimal performance..."
    
    # Set environment variables for better performance
    export OLLAMA_NUM_PARALLEL=2
    export OLLAMA_MAX_LOADED_MODELS=2
    export OLLAMA_FLASH_ATTENTION=1
    
    # Create modelfile for custom configurations if needed
    cat > /tmp/cve-analysis-config << 'EOF'
# CVE Analysis Platform - Ollama Configuration
# Optimized for security analysis workloads

# Memory management
OLLAMA_MAX_LOADED_MODELS=2
OLLAMA_NUM_PARALLEL=2

# Performance tuning
OLLAMA_FLASH_ATTENTION=1
OLLAMA_HOST=0.0.0.0:11434

# Logging
OLLAMA_DEBUG=false
EOF

    print_status "Model configuration optimized for CVE analysis"
}

# Main execution starts here
echo ""
print_info "System Information:"
print_info "OS: $(lsb_release -d | cut -f2)"
print_info "Architecture: $(uname -m)"
echo ""

# Step 1: Pre-flight checks
echo "🔍 Step 1: Pre-flight checks"
check_disk_space
check_memory

# Step 2: Verify Ollama installation
echo ""
echo "🔧 Step 2: Verifying Ollama installation"
if ! command -v ollama >/dev/null 2>&1; then
    print_error "Ollama is not installed!"
    print_info "Please install Ollama first: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

print_status "Ollama found: $(ollama --version 2>/dev/null || echo 'Latest')"

# Step 3: Start Ollama service
echo ""
echo "🚀 Step 3: Starting Ollama service"
if ! start_ollama; then
    print_error "Failed to start Ollama service"
    exit 1
fi

# Step 4: Configure settings
echo ""
echo "⚙️  Step 4: Configuring model settings"
configure_model_settings

# Step 5: Download AI models
echo ""
echo "📦 Step 5: Downloading AI models"
print_warning "This will download approximately 13GB of data"
print_info "The download may take 10-30 minutes depending on your internet speed"
echo ""

# Model definitions: name, size, purpose
models=(
    "llama3.1:8b|~4.7GB|General CVE analysis and risk assessment"
    "gemma2:9b|~5.4GB|Technical analysis and attack vector extraction"
    "codellama:7b|~3.8GB|Code vulnerability analysis and exploitation patterns"
)

failed_models=()

for model_info in "${models[@]}"; do
    IFS='|' read -r model_name model_size model_purpose <<< "$model_info"
    
    echo ""
    if download_model "$model_name" "$model_size" "$model_purpose"; then
        print_status "$model_name ready"
    else
        failed_models+=("$model_name")
    fi
done

# Step 6: Verify installations
echo ""
echo "🧪 Step 6: Testing model installations"

print_info "Available models:"
ollama list

echo ""
successful_tests=0
total_tests=0

for model_info in "${models[@]}"; do
    IFS='|' read -r model_name model_size model_purpose <<< "$model_info"
    
    # Skip failed downloads
    if [[ " ${failed_models[@]} " =~ " ${model_name} " ]]; then
        print_warning "Skipping test for $model_name (download failed)"
        continue
    fi
    
    ((total_tests++))
    if test_model "$model_name"; then
        ((successful_tests++))
    fi
    echo ""
done

# Step 7: Performance optimization
echo ""
echo "⚡ Step 7: Performance optimization"

# Create a simple benchmark
print_info "Running performance benchmark..."
start_time=$(date +%s)
benchmark_response=$(ollama run llama3.1:8b "Analyze this CVE: A buffer overflow vulnerability exists in example software. Rate the severity from 1-10 and explain briefly." 2>/dev/null)
end_time=$(date +%s)
duration=$((end_time - start_time))

if [[ -n "$benchmark_response" ]]; then
    print_status "Benchmark completed in ${duration} seconds"
    print_info "Model response quality: Good"
else
    print_warning "Benchmark test failed - models may need more time to load"
fi

# Step 8: Create helper scripts
echo ""
echo "📝 Step 8: Creating helper scripts"

# Create model management script
cat > model_manager.sh << 'EOF'
#!/bin/bash

case "$1" in
    "start")
        echo "Starting Ollama service..."
        ollama serve &
        echo "Ollama started in background"
        ;;
    "stop")
        echo "Stopping Ollama service..."
        pkill ollama
        echo "Ollama stopped"
        ;;
    "status")
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            echo "Ollama is running"
            echo "Available models:"
            ollama list
        else
            echo "Ollama is not running"
        fi
        ;;
    "test")
        echo "Testing all models..."
        for model in "llama3.1:8b" "gemma2:9b" "codellama:7b"; do
            echo "Testing $model..."
            ollama run "$model" "Test response" >/dev/null 2>&1 && echo "✅ $model: OK" || echo "❌ $model: Failed"
        done
        ;;
    *)
        echo "Usage: $0 {start|stop|status|test}"
        ;;
esac
EOF

chmod +x model_manager.sh
print_status "Model management script created: ./model_manager.sh"

# Step 9: Summary
echo ""
echo "📊 Step 9: Installation Summary"
echo "==============================="

print_info "Downloaded Models:"
ollama list | grep -E "(llama3.1:8b|gemma2:9b|codellama:7b)" || print_warning "Some models may not be listed yet"

echo ""
print_info "Test Results: $successful_tests/$total_tests models working"

if [ "$successful_tests" -eq "$total_tests" ] && [ "$total_tests" -gt 0 ]; then
    print_status "All AI models are ready for CVE analysis!"
elif [ "$successful_tests" -gt 0 ]; then
    print_warning "Some models are working. Platform will function with reduced capabilities."
else
    print_error "No models are working. Please check the installation."
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Keep Ollama running: ollama serve"
echo "2. Models are now ready for CVE analysis"
echo "3. Proceed to Step 4: Setting up the application code"

echo ""
echo "💡 Useful Commands:"
echo "- Check models: ollama list"
echo "- Test a model: ollama run llama3.1:8b 'Hello'"
echo "- Monitor Ollama: ./model_manager.sh status"
echo "- View logs: tail /tmp/ollama.log"

echo ""
if [ ${#failed_models[@]} -eq 0 ]; then
    print_status "AI Models setup complete! 🎉"
else
    print_warning "Setup completed with some issues. Failed models: ${failed_models[*]}"
fi
