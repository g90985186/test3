#!/usr/bin/env python3
"""
Test script to check API health
"""
import requests

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing API Health...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health Response: {response.json()}")
        
        # Test API info
        response = requests.get("http://localhost:8000/api/info", timeout=5)
        print(f"API Info Status: {response.status_code}")
        if response.status_code == 200:
            print(f"API Info: {response.json()}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_health() 