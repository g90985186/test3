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

