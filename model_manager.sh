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
