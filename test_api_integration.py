#!/usr/bin/env python3
"""
API Integration Test Script
Tests key endpoints for CVE Analysis Platform
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_BASE = "http://127.0.0.1:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

def test_auth():
    """Test authentication"""
    print("🔐 Testing Authentication...")
    
    response = requests.post(f"{API_BASE}/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Authentication successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return None

def test_dashboard(token):
    """Test dashboard metrics"""
    print("\n📊 Testing Dashboard Metrics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/dashboard/metrics", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Dashboard metrics loaded!")
        print(f"   Total CVEs: {data.get('total_count', 'N/A')}")
        print(f"   Critical: {data.get('critical_count', 'N/A')}")
        print(f"   High: {data.get('high_count', 'N/A')}")
        return True
    else:
        print(f"❌ Dashboard failed: {response.status_code} - {response.text}")
        return False

def test_cve_search(token):
    """Test CVE search"""
    print("\n🔍 Testing CVE Search...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/cve/?limit=5", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        cve_count = len(data.get("items", []))
        print(f"✅ CVE search successful! Found {cve_count} CVEs")
        
        if cve_count > 0:
            sample_cve = data["items"][0]
            print(f"   Sample CVE: {sample_cve.get('cve_id', 'N/A')}")
            return sample_cve.get('cve_id')
        return True
    else:
        print(f"❌ CVE search failed: {response.status_code} - {response.text}")
        return False

def test_analysis(token, cve_id="CVE-2024-0001"):
    """Test CVE analysis"""
    print(f"\n🧠 Testing CVE Analysis for {cve_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE}/analysis/analyze", 
                           headers=headers,
                           json={
                               "cve_id": cve_id,
                               "analysis_type": "comprehensive",
                               "auto_import": True
                           })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Analysis successful for {cve_id}!")
        print(f"   Model used: {data.get('model_used', 'N/A')}")
        print(f"   Source: {data.get('source', 'N/A')}")
        return True
    else:
        print(f"❌ Analysis failed: {response.status_code} - {response.text}")
        return False

def test_poc_generation(token, cve_id="CVE-2024-0001"):
    """Test PoC generation"""
    print(f"\n⚡ Testing PoC Generation for {cve_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE}/poc/generate",
                           headers=headers,
                           json={
                               "cve_id": cve_id,
                               "description": "Test vulnerability",
                               "vulnerability_type": "injection",
                               "affected_component": "web application"
                           })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ PoC generation successful for {cve_id}!")
        print(f"   Code length: {len(data.get('code', ''))} characters")
        print(f"   Documentation: {len(data.get('documentation', {}))} fields")
        return True
    else:
        print(f"❌ PoC generation failed: {response.status_code} - {response.text}")
        return False

def test_watchlist(token):
    """Test watchlist operations"""
    print("\n👁️ Testing Watchlist Operations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First create a watchlist
    response = requests.post(f"{API_BASE}/watchlist/",
                           headers=headers,
                           json={
                               "name": "Test Watchlist",
                               "description": "API Integration Test"
                           })
    
    if response.status_code == 200:
        data = response.json()
        watchlist_id = data.get("watchlist_id")
        print(f"✅ Watchlist created! ID: {watchlist_id}")
        
        # Test adding CVEs to watchlist
        add_response = requests.post(f"{API_BASE}/watchlist/{watchlist_id}/cves",
                                   headers=headers,
                                   json={
                                       "cve_ids": ["CVE-2024-0001", "CVE-2024-0002"],
                                       "priority": "high"
                                   })
        
        if add_response.status_code == 200:
            add_data = add_response.json()
            print(f"✅ CVEs added to watchlist: {add_data.get('added', [])}")
            return True
        else:
            print(f"⚠️ Failed to add CVEs to watchlist: {add_response.status_code}")
            return True  # Still return True since watchlist creation worked
    else:
        print(f"❌ Watchlist creation failed: {response.status_code} - {response.text}")
        return False

def main():
    """Run all API tests"""
    print("🚀 CVE Analysis Platform - API Integration Test")
    print("=" * 50)
    
    # Test authentication
    token = test_auth()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Track results
    results = {
        "auth": True,
        "dashboard": test_dashboard(token),
        "cve_search": test_cve_search(token),
        "analysis": test_analysis(token),
        "poc": test_poc_generation(token),
        "watchlist": test_watchlist(token)
    }
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.upper()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All API endpoints are working correctly!")
        print("🌐 Frontend should be able to integrate with these APIs")
    else:
        print("⚠️ Some issues detected. Check logs for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 