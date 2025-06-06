#!/usr/bin/env python3
"""
Test our NVD service directly
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_our_nvd_service():
    """Test our NVD service directly"""
    
    print("🧪 Testing Our NVD Service")
    print("=" * 30)
    
    try:
        from app.services.nvd_search_service import NVDSearchService
        
        # Create service
        service = NVDSearchService()
        
        print(f"API Key: {service.api_key[:8] + '...' + service.api_key[-4:] if service.api_key else 'None'}")
        print(f"Rate Limit: {service.rate_limit_delay} seconds")
        print(f"Base URL: {service.base_url}")
        
        # Test 1: Simple search
        print("\n🔍 Test 1: Simple search (no parameters)")
        result = await service.search_live(limit=5)
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Results: {result['total_results']}")
        else:
            print(f"Error: {result['error']}")
        
        # Test 2: Specific CVE
        print("\n🔍 Test 2: Specific CVE search")
        result = await service.search_live(cve_id="CVE-2021-44228", limit=1)
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Results: {result['total_results']}")
        else:
            print(f"Error: {result['error']}")
        
        # Test 3: Keyword search
        print("\n🔍 Test 3: Keyword search")
        result = await service.search_live(keyword="apache", limit=5)
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Results: {result['total_results']}")
            if result.get('message'):
                print(f"Message: {result['message']}")
        else:
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_our_nvd_service())
