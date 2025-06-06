#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ollama_service import OllamaService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_models():
    """Load and verify AI models in Ollama"""
    
    try:
        logger.info("Connecting to Ollama service...")
        
        ollama_service = OllamaService()
        
        # Check health
        is_healthy = await ollama_service.health_check()
        if not is_healthy:
            logger.error("Ollama service is not available")
            return False
        
        logger.info("Ollama service is healthy!")
        
        # Test each model
        models_to_test = [
            ("llama3.1:8b", "general"),
            ("gemma2:9b", "technical"),
            ("codellama:7b", "code")
        ]
        
        for model, purpose in models_to_test:
            logger.info(f"Testing {model} ({purpose} analysis)...")
            
            test_prompt = "Test prompt for model verification"
            
            try:
                response = await ollama_service.generate_response(test_prompt, model)
                
                if response["success"]:
                    logger.info(f"✓ {model} is working correctly")
                else:
                    logger.error(f"✗ {model} failed: {response.get('error')}")
                    
            except Exception as e:
                logger.error(f"✗ Error testing {model}: {e}")
        
        logger.info("Model verification completed!")
        return True
        
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(load_models())
    sys.exit(0 if success else 1)
