#!/usr/bin/env python3
"""
Test the exact same flow that the web interface uses
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_web_flow():
    """Test the exact same code path as the web interface"""
    
    print("🌐 Testing Web Application Flow")
    print("=" * 35)
    
    try:
        # Import exactly what the web route uses
        from app.services.nvd_search_service import NVDSearchService
        from app.api.routes.cve import SearchRequest
        
        # Create the same request object as the web interface
        request = SearchRequest(
            query="apache",
            severity=None,
            search_type="both",
            limit=20
        )
        
        print(f"🔍 Request object:")
        print(f"   Query: {request.query}")
        print(f"   Severity: {request.severity}")
        print(f"   Search Type: {request.search_type}")
        print(f"   Limit: {request.limit}")
        
        # Test the NVD search part specifically
        print(f"\n🧪 Testing NVD search with web parameters...")
        
        nvd_service = NVDSearchService()
        print(f"   API Key: {nvd_service.api_key[:8]}...{nvd_service.api_key[-4:] if nvd_service.api_key else 'None'}")
        
        # Extract the logic from the web route
        cve_id = None
        keyword = None
        
        if request.query and request.query.strip():
            query_clean = request.query.strip()
            if query_clean.upper().startswith("CVE-"):
                cve_id = query_clean
            else:
                keyword = query_clean
        
        print(f"   Parsed CVE ID: {cve_id}")
        print(f"   Parsed Keyword: {keyword}")
        print(f"   Severity: {request.severity}")
        
        # Call the exact same method as the web interface
        nvd_result = await nvd_service.search_live(
            cve_id=cve_id,
            keyword=keyword,
            severity=request.severity,
            limit=request.limit
        )
        
        print(f"\n📊 NVD Result:")
        print(f"   Success: {nvd_result['success']}")
        print(f"   Total Results: {nvd_result.get('total_results', 0)}")
        print(f"   Returned Results: {len(nvd_result.get('results', []))}")
        
        if nvd_result.get('message'):
            print(f"   Message: {nvd_result['message']}")
        
        if not nvd_result['success']:
            print(f"   Error: {nvd_result.get('error', 'Unknown error')}")
            print(f"   Rate Limited: {nvd_result.get('rate_limited', False)}")
        
        # Now test the full hybrid search flow
        print(f"\n🔄 Testing Full Hybrid Search Flow...")
        
        # Simulate what the CVE route does
        results = {
            "local_results": [],  # We'll skip local for this test
            "nvd_results": [],
            "total_local": 0,
            "total_nvd": 0,
            "search_type": request.search_type,
            "query": request.query,
            "severity": request.severity,
            "success": True,
            "errors": [],
            "info_messages": []
        }
        
        if nvd_result["success"]:
            results["nvd_results"] = nvd_result["results"]
            results["total_nvd"] = len(nvd_result["results"])
            print(f"   ✅ NVD search succeeded: {results['total_nvd']} results")
            
            if nvd_result.get("message"):
                results["info_messages"].append(nvd_result["message"])
        else:
            error_msg = f"NVD search error: {nvd_result['error']}"
            print(f"   ❌ NVD search failed: {error_msg}")
            results["errors"].append(error_msg)
            results["nvd_rate_limited"] = nvd_result.get("rate_limited", False)
        
        print(f"\n🎯 Final Results Summary:")
        print(f"   Total Results: {results['total_nvd']}")
        print(f"   Success: {results['success']}")
        print(f"   Errors: {results['errors']}")
        print(f"   Info Messages: {results['info_messages']}")
        
    except Exception as e:
        print(f"❌ Error in web flow test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_web_flow())
