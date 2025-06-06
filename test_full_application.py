#!/usr/bin/env python3
"""
Comprehensive test suite for CVE Analysis Platform
Tests all major backend functionality and API endpoints
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
DEFAULT_HEADERS = {"Content-Type": "application/json"}

class CVEPlatformTester:
    def __init__(self):
        self.token = None
        self.headers = DEFAULT_HEADERS.copy()
        
    def authenticate(self):
        """Authenticate and get access token"""
        print("🔐 Authenticating...")
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
                "username": "admin",
                "password": "admin123"
            })
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"  ✅ Authentication successful")
                return True
            else:
                print(f"  ❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Authentication error: {e}")
            return False

    def test_health_endpoints(self):
        """Test system health endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        endpoints = [
            ("/health", "System Health"),
            ("/api/v1/monitoring/status", "Monitoring Status")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=self.headers)
                if response.status_code == 200:
                    print(f"  ✅ {name}: OK")
                else:
                    print(f"  ⚠️  {name}: Status {response.status_code}")
            except Exception as e:
                print(f"  ❌ {name}: Error - {e}")

    def test_cve_endpoints(self):
        """Test CVE-related endpoints"""
        print("\n🔍 Testing CVE Endpoints...")
        
        # Test CVE listing
        try:
            response = requests.get(f"{BASE_URL}/api/v1/cve/?limit=5", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ CVE List: Retrieved {len(data.get('results', []))} CVEs")
            else:
                print(f"  ⚠️  CVE List: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ CVE List: Error - {e}")
            
        # Test CVE search
        try:
            search_data = {"query": "apache", "limit": 3}
            response = requests.post(f"{BASE_URL}/api/v1/cve/search", 
                                   json=search_data, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ CVE Search: Found results")
            else:
                print(f"  ⚠️  CVE Search: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ CVE Search: Error - {e}")

    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        print("\n📊 Testing Dashboard Endpoints...")
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/dashboard/metrics", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Dashboard Metrics: Retrieved metrics")
            else:
                print(f"  ⚠️  Dashboard Metrics: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Dashboard Metrics: Error - {e}")

    def test_poc_endpoints(self):
        """Test Proof of Concept endpoints"""
        print("\n💻 Testing PoC Endpoints...")
        
        # Test PoC listing
        try:
            response = requests.get(f"{BASE_URL}/api/v1/poc/", headers=self.headers)
            if response.status_code == 200:
                print(f"  ✅ PoC List: OK")
            else:
                print(f"  ⚠️  PoC List: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ PoC List: Error - {e}")
            
        # Test PoC generation
        try:
            poc_data = {
                "cve_id": "CVE-2024-TEST",
                "vulnerability_type": "XSS",
                "target_system": "Web Application"
            }
            response = requests.post(f"{BASE_URL}/api/v1/poc/generate", 
                                   json=poc_data, headers=self.headers)
            if response.status_code == 200:
                print(f"  ✅ PoC Generation: Successfully generated")
            else:
                print(f"  ⚠️  PoC Generation: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ PoC Generation: Error - {e}")

    def test_settings_endpoints(self):
        """Test settings endpoints"""
        print("\n⚙️ Testing Settings Endpoints...")
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/settings/user", headers=self.headers)
            if response.status_code == 200:
                print(f"  ✅ User Settings: Retrieved")
            else:
                print(f"  ⚠️  User Settings: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ User Settings: Error - {e}")

    def test_notifications_endpoints(self):
        """Test notifications endpoints"""
        print("\n🔔 Testing Notifications Endpoints...")
        
        # Get notifications
        try:
            response = requests.get(f"{BASE_URL}/api/v1/notifications/", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Notifications List: Retrieved {len(data.get('notifications', []))} notifications")
            else:
                print(f"  ⚠️  Notifications List: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Notifications List: Error - {e}")
            
        # Create test notification
        try:
            notification_data = {
                "title": "Test Notification",
                "message": "This is a test notification from the test suite",
                "type": "info"
            }
            response = requests.post(f"{BASE_URL}/api/v1/notifications/", 
                                   json=notification_data, headers=self.headers)
            if response.status_code == 200:
                print(f"  ✅ Create Notification: Successfully created")
            else:
                print(f"  ⚠️  Create Notification: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Create Notification: Error - {e}")

    def test_watchlist_endpoints(self):
        """Test watchlist endpoints"""
        print("\n⭐ Testing Watchlist Endpoints...")
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/watchlist/", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Watchlist: Retrieved {len(data.get('items', []))} items")
            else:
                print(f"  ⚠️  Watchlist: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Watchlist: Error - {e}")

    def test_reports_endpoints(self):
        """Test reports endpoints"""
        print("\n📋 Testing Reports Endpoints...")
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/reports/", headers=self.headers)
            if response.status_code == 200:
                print(f"  ✅ Reports List: OK")
            else:
                print(f"  ⚠️  Reports List: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Reports List: Error - {e}")

    def test_chat_endpoints(self):
        """Test chat endpoints"""
        print("\n💬 Testing Chat Endpoints...")
        
        try:
            chat_data = {"message": "What is CVE-2024-TEST?"}
            response = requests.post(f"{BASE_URL}/api/v1/chat", 
                                   json=chat_data, headers=self.headers)
            if response.status_code == 200:
                print(f"  ✅ Chat: Response received")
            else:
                print(f"  ⚠️  Chat: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Chat: Error - {e}")

    def run_full_test_suite(self):
        """Run the complete test suite"""
        print("🚀 CVE Analysis Platform - Full Application Test Suite")
        print("=" * 70)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Authenticate first
        if not self.authenticate():
            print("\n❌ Cannot proceed without authentication")
            return False
            
        # Run all tests
        self.test_health_endpoints()
        self.test_cve_endpoints()
        self.test_dashboard_endpoints()
        self.test_poc_endpoints()
        self.test_settings_endpoints()
        self.test_notifications_endpoints()
        self.test_watchlist_endpoints()
        self.test_reports_endpoints()
        self.test_chat_endpoints()
        
        print("\n" + "=" * 70)
        print("✅ Full Application Test Suite Complete!")
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True

def main():
    """Main test runner"""
    tester = CVEPlatformTester()
    tester.run_full_test_suite()

if __name__ == "__main__":
    main() 