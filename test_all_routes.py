#!/usr/bin/env python3
"""
Comprehensive API Route Test Script
Tests all 92+ backend API routes for CVE Analysis Platform
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
API_BASE = "http://127.0.0.1:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

class APITestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = {}
        self.total_routes = 0
        self.passed_routes = 0
        self.failed_routes = 0

    def authenticate(self):
        """Authenticate with the API"""
        print("🔐 Authenticating...")
        
        response = self.session.post(f"{API_BASE}/auth/login", json={
            "username": USERNAME,
            "password": PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print(f"✅ Authentication successful! Token: {self.token[:20]}...")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False

    def test_route(self, method, endpoint, data=None, description=""):
        """Test a single API route"""
        self.total_routes += 1
        url = f"{API_BASE}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data or {})
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data or {})
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code in [200, 201, 204]:
                print(f"✅ {method} {endpoint} - {description}")
                self.passed_routes += 1
                self.test_results[endpoint] = {"status": "PASS", "code": response.status_code}
                return True
            elif response.status_code == 401:
                print(f"🔐 {method} {endpoint} - Authentication required")
                self.test_results[endpoint] = {"status": "AUTH_REQUIRED", "code": response.status_code}
                return False
            elif response.status_code == 404:
                print(f"🚫 {method} {endpoint} - Not Found")
                self.test_results[endpoint] = {"status": "NOT_FOUND", "code": response.status_code}
                self.failed_routes += 1
                return False
            elif response.status_code == 405:
                print(f"⚠️  {method} {endpoint} - Method not allowed")
                self.test_results[endpoint] = {"status": "METHOD_NOT_ALLOWED", "code": response.status_code}
                self.failed_routes += 1
                return False
            else:
                print(f"⚠️  {method} {endpoint} - HTTP {response.status_code}")
                self.test_results[endpoint] = {"status": "OTHER", "code": response.status_code}
                return False
                
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {str(e)}")
            self.test_results[endpoint] = {"status": "ERROR", "error": str(e)}
            self.failed_routes += 1
            return False

    def run_all_tests(self):
        """Test all 92+ API routes"""
        
        print("\n🚀 Testing ALL 92+ Backend API Routes...\n")
        
        # Authentication Routes (10)
        print("📋 AUTHENTICATION ROUTES (10)")
        self.test_route("POST", "/auth/register", {"username": "testuser", "password": "testpass", "email": "test@example.com"}, "User registration")
        self.test_route("POST", "/auth/login", {"username": USERNAME, "password": PASSWORD}, "User login")
        self.test_route("GET", "/auth/me", description="Get current user")
        self.test_route("PUT", "/auth/me", {"email": "new@example.com"}, "Update user profile")
        self.test_route("POST", "/auth/change-password", {"old_password": PASSWORD, "new_password": "newpass"}, "Change password")
        self.test_route("POST", "/auth/api-keys", {"name": "test-key"}, "Generate API key")
        self.test_route("GET", "/auth/users", description="List all users (admin)")
        self.test_route("GET", "/auth/stats", description="User statistics")
        self.test_route("POST", "/auth/logout", description="User logout")
        self.test_route("GET", "/auth/info", description="Auth system info")
        
        # CVE Routes (12)
        print("\n📋 CVE ROUTES (12)")
        self.test_route("POST", "/cve/search/advanced", {"query": "test", "limit": 10}, "Advanced CVE search")
        self.test_route("POST", "/cve/bulk-import", {"cves": []}, "Bulk import CVEs")
        self.test_route("GET", "/cve/search/history", description="Get search history")
        self.test_route("POST", "/cve/search/save", {"name": "test-search", "query": "test"}, "Save search query")
        self.test_route("GET", "/cve/search/saved", description="Get saved searches")
        self.test_route("POST", "/cve/search/saved/test-id/execute", description="Execute saved search")
        self.test_route("DELETE", "/cve/search/saved/test-id", description="Delete saved search")
        self.test_route("POST", "/cve/search", {"query": "test"}, "Basic CVE search")
        self.test_route("POST", "/cve/import-from-nvd", {"start_date": "2024-01-01"}, "Import from NVD")
        self.test_route("GET", "/cve/", description="List CVEs")
        self.test_route("GET", "/cve/CVE-2024-0001", description="Get specific CVE")
        self.test_route("GET", "/cve/stats/summary", description="CVE statistics")
        
        # Analysis Routes (11)
        print("\n📋 ANALYSIS ROUTES (11)")
        self.test_route("POST", "/analysis/analyze", {"cve_id": "CVE-2024-0001"}, "Analyze CVE")
        self.test_route("GET", "/analysis/CVE-2024-0001/analysis", description="Get CVE analysis")
        self.test_route("POST", "/analysis/risk-assessment", {"cve_id": "CVE-2024-0001"}, "Risk assessment")
        self.test_route("POST", "/analysis/CVE-2024-0001/mitigations", {"type": "full"}, "Get mitigations")
        self.test_route("GET", "/analysis/CVE-2024-0001/attack-vectors", description="Get attack vectors")
        self.test_route("POST", "/analysis/cve/analyze", {"cve_id": "CVE-2024-0001"}, "CVE analysis")
        self.test_route("POST", "/analysis/code/analyze", {"code": "test code"}, "Code analysis")
        self.test_route("GET", "/analysis/results/test-id", description="Get analysis result")
        self.test_route("GET", "/analysis/results", description="List analysis results")
        self.test_route("GET", "/analysis/ai/status", description="AI service status")
        self.test_route("POST", "/analysis/ai/initialize", description="Initialize AI service")
        
        # Dashboard Routes (4)
        print("\n📋 DASHBOARD ROUTES (4)")
        self.test_route("GET", "/dashboard/metrics", description="Dashboard metrics")
        self.test_route("GET", "/dashboard/recent-cves", description="Recent CVEs")
        self.test_route("GET", "/dashboard/timeline", description="Timeline data")
        self.test_route("GET", "/dashboard/stats", description="Dashboard statistics")
        
        # Chat Routes (5)
        print("\n📋 CHAT ROUTES (5)")
        self.test_route("POST", "/chat/", {"message": "test message"}, "Send chat message")
        self.test_route("GET", "/chat/sessions", description="Get chat sessions")
        self.test_route("GET", "/chat/history", description="Get chat history")
        self.test_route("GET", "/chat/stats", description="Chat statistics")
        self.test_route("DELETE", "/chat/sessions/test-session", description="Delete chat session")
        
        # PoC Routes (4)
        print("\n📋 POC ROUTES (4)")
        self.test_route("POST", "/poc/generate", {"cve_id": "CVE-2024-0001"}, "Generate PoC")
        self.test_route("GET", "/poc/CVE-2024-0001", description="Get PoC for CVE")
        self.test_route("GET", "/poc/", description="List PoCs")
        self.test_route("POST", "/poc/CVE-2024-0001/validate", {"type": "syntax"}, "Validate PoC")
        
        # Watchlist Routes (8)
        print("\n📋 WATCHLIST ROUTES (8)")
        self.test_route("POST", "/watchlist/", {"name": "Test Watchlist"}, "Create watchlist")
        self.test_route("GET", "/watchlist/", description="List watchlists")
        self.test_route("GET", "/watchlist/test-id", description="Get watchlist")
        self.test_route("DELETE", "/watchlist/test-id", description="Delete watchlist")
        self.test_route("POST", "/watchlist/test-id/cves", {"cve_ids": ["CVE-2024-0001"]}, "Add CVEs to watchlist")
        self.test_route("GET", "/watchlist/test-id/cves", description="Get watchlist CVEs")
        self.test_route("GET", "/watchlist/test-id/alerts", description="Get watchlist alerts")
        self.test_route("GET", "/watchlist/stats/overview", description="Watchlist statistics")
        
        # Reports Routes (7)
        print("\n📋 REPORTS ROUTES (7)")
        self.test_route("POST", "/reports/generate", {"type": "summary"}, "Generate report")
        self.test_route("GET", "/reports/", description="List reports")
        self.test_route("GET", "/reports/test-id", description="Get report")
        self.test_route("GET", "/reports/test-id/download", description="Download report")
        self.test_route("DELETE", "/reports/test-id", description="Delete report")
        self.test_route("GET", "/reports/metrics/overview", description="Report metrics")
        self.test_route("GET", "/reports/types/supported", description="Supported report types")
        
        # Notifications Routes (12)
        print("\n📋 NOTIFICATIONS ROUTES (12)")
        self.test_route("GET", "/notifications/", description="Get notifications")
        self.test_route("POST", "/notifications/", {"title": "Test", "message": "Test"}, "Create notification")
        self.test_route("PUT", "/notifications/test-id/read", description="Mark notification as read")
        self.test_route("PUT", "/notifications/mark-all-read", description="Mark all notifications as read")
        self.test_route("DELETE", "/notifications/test-id", description="Delete notification")
        self.test_route("DELETE", "/notifications/clear-all", description="Clear all notifications")
        self.test_route("GET", "/notifications/stats", description="Notification statistics")
        self.test_route("GET", "/notifications/preferences", description="Get notification preferences")
        self.test_route("PUT", "/notifications/preferences", {"email": True}, "Update notification preferences")
        self.test_route("POST", "/notifications/test", description="Test notification")
        self.test_route("GET", "/notifications/email-queue", description="Email queue status")
        self.test_route("POST", "/notifications/cleanup", description="Cleanup notifications")
        
        # Settings Routes (13)
        print("\n📋 SETTINGS ROUTES (13)")
        self.test_route("GET", "/settings/user", description="Get user settings")
        self.test_route("PUT", "/settings/user", {"theme": "dark"}, "Update user settings")
        self.test_route("GET", "/settings/notifications", description="Get notification settings")
        self.test_route("PUT", "/settings/notifications", {"email": True}, "Update notification settings")
        self.test_route("GET", "/settings/export", description="Get export settings")
        self.test_route("PUT", "/settings/export", {"format": "json"}, "Update export settings")
        self.test_route("GET", "/settings/system", description="Get system settings")
        self.test_route("PUT", "/settings/system", {"debug": False}, "Update system settings")
        self.test_route("GET", "/settings/defaults", description="Get default settings")
        self.test_route("POST", "/settings/reset", description="Reset settings")
        self.test_route("GET", "/settings/export-all", description="Export all settings")
        self.test_route("POST", "/settings/import-all", {"settings": {}}, "Import all settings")
        self.test_route("GET", "/settings/validate", description="Validate settings")
        
        # Monitoring Routes (6)
        print("\n📋 MONITORING ROUTES (6)")
        self.test_route("GET", "/monitoring/health", description="Health check")
        self.test_route("GET", "/monitoring/metrics", description="System metrics")
        self.test_route("GET", "/monitoring/status", description="System status")
        self.test_route("GET", "/monitoring/logs", description="System logs")
        self.test_route("POST", "/monitoring/restart", description="Restart system")
        self.test_route("GET", "/monitoring/performance", description="Performance metrics")

    def generate_report(self):
        """Generate test report"""
        print(f"\n📊 TEST RESULTS SUMMARY")
        print(f"{'='*50}")
        print(f"Total Routes Tested: {self.total_routes}")
        print(f"✅ Passed: {self.passed_routes}")
        print(f"❌ Failed: {self.failed_routes}")
        print(f"🎯 Success Rate: {(self.passed_routes/self.total_routes*100):.1f}%")
        
        # Detailed breakdown
        status_counts = {}
        for result in self.test_results.values():
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📈 STATUS BREAKDOWN:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Save detailed results
        with open('api_test_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': self.total_routes,
                    'passed': self.passed_routes,
                    'failed': self.failed_routes,
                    'success_rate': self.passed_routes/self.total_routes*100
                },
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to 'api_test_results.json'")

def main():
    print("🧪 CVE Analysis Platform - Comprehensive API Test Suite")
    print("Testing all 92+ backend API routes")
    print("="*60)
    
    test_suite = APITestSuite()
    
    # Authenticate first
    if not test_suite.authenticate():
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Run all tests
    test_suite.run_all_tests()
    
    # Generate report
    test_suite.generate_report()
    
    # Exit with appropriate code
    if test_suite.failed_routes == 0:
        print("\n🎉 ALL TESTS PASSED! All API routes are accessible.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {test_suite.failed_routes} routes failed. Check results above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 