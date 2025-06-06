#!/usr/bin/env python3
"""
Simple test script to verify authentication integration
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_public_endpoints():
    """Test public endpoints that should work without authentication"""
    print("🔓 Testing public endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"  ✅ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Health endpoint failed: {e}")
    
    # Test home page
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"  ✅ Home page: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Home page failed: {e}")

def test_protected_endpoints_without_auth():
    """Test protected endpoints without authentication"""
    print("\n🔒 Testing protected endpoints without authentication...")
    
    protected_endpoints = [
        "/api/v1/cve/",
        "/api/v1/dashboard/metrics", 
        "/api/v1/analysis/",
        "/api/v1/poc/",
    ]
    
    for endpoint in protected_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"  ✅ {endpoint}: Properly protected (401)")
            else:
                print(f"  ⚠️  {endpoint}: Unexpected status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint}: Error - {e}")

def test_authentication():
    """Test authentication flow"""
    print("\n🔐 Testing authentication...")
    
    # Test login
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"  ✅ Login successful, got token: {token[:20]}...")
            return token
        else:
            print(f"  ❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Login error: {e}")
        return None

def test_authenticated_endpoints(token):
    """Test protected endpoints with valid token"""
    if not token:
        print("\n❌ Cannot test authenticated endpoints - no token")
        return
        
    print("\n🔓 Testing protected endpoints with authentication...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    protected_endpoints = [
        "/api/v1/cve/",
        "/api/v1/dashboard/metrics",
        "/api/v1/poc/",
    ]
    
    for endpoint in protected_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                print(f"  ✅ {endpoint}: Access granted (200)")
            else:
                print(f"  ⚠️  {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint}: Error - {e}")

def main():
    print("🚀 CVE Analysis Platform Authentication Integration Test")
    print("=" * 60)
    
    # Test public endpoints
    test_public_endpoints()
    
    # Test protected endpoints without auth
    test_protected_endpoints_without_auth()
    
    # Test authentication
    token = test_authentication()
    
    # Test authenticated endpoints
    test_authenticated_endpoints(token)
    
    print("\n" + "=" * 60)
    print("✅ Authentication integration test complete!")

if __name__ == "__main__":
    main() 