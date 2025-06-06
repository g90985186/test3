#!/usr/bin/env python3
"""
Test NVD API Key directly
Run this to verify if your API key is working
"""

import aiohttp
import asyncio
import os
from dotenv import load_dotenv

async def test_api_key():
    """Test NVD API key directly"""
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('NVD_API_KEY')
    
    print("🔑 NVD API Key Test")
    print("=" * 30)
    
    if not api_key:
        print("❌ No API key found in environment")
        return
    
    # Mask the API key for security (show first 8 and last 4 chars)
    if len(api_key) > 12:
        masked_key = api_key[:8] + "..." + api_key[-4:]
    else:
        masked_key = api_key[:4] + "..."
    
    print(f"🔍 Testing API key: {masked_key}")
    print(f"📏 Key length: {len(api_key)} characters")
    
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    # Test cases with API key
    test_cases = [
        {
            "name": "1. Simple request with API key",
            "params": {"resultsPerPage": 5}
        },
        {
            "name": "2. Specific CVE with API key",
            "params": {"cveId": "CVE-2021-44228"}
        },
        {
            "name": "3. No parameters with API key",
            "params": {}
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test in test_cases:
            print(f"\n🧪 {test['name']}")
            print(f"Parameters: {test['params']}")
            
            headers = {
                "Accept": "application/json",
                "User-Agent": "CVE-Analysis-Platform-Test/1.0",
                "apiKey": api_key
            }
            
            try:
                async with session.get(
                    base_url,
                    params=test['params'],
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    print(f"📊 Status: {response.status}")
                    
                    # Print response headers for debugging
                    important_headers = ['message', 'x-ratelimit-remaining', 'x-ratelimit-limit']
                    for header in important_headers:
                        if header in response.headers:
                            print(f"📋 {header}: {response.headers[header]}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            total_results = data.get("totalResults", 0)
                            vulnerabilities = data.get("vulnerabilities", [])
                            
                            print(f"✅ SUCCESS!")
                            print(f"   Total Results: {total_results}")
                            print(f"   Returned: {len(vulnerabilities)} vulnerabilities")
                            
                        except Exception as e:
                            print(f"❌ JSON Parse Error: {e}")
                    
                    elif response.status == 404:
                        error_msg = response.headers.get('message', 'Unknown error')
                        print(f"❌ 404 Error: {error_msg}")
                        
                    elif response.status == 403:
                        error_msg = response.headers.get('message', 'Forbidden')
                        print(f"❌ 403 Forbidden: {error_msg}")
                        
                    else:
                        error_text = await response.text()
                        print(f"❌ Error {response.status}: {error_text}")
                    
            except Exception as e:
                print(f"❌ Request failed: {e}")
            
            # Small delay between requests
            await asyncio.sleep(1)
    
    print("\n" + "=" * 50)
    print("🎯 API KEY DIAGNOSIS:")
    
    print("\nIf you see 'Invalid apiKey' errors:")
    print("1. Check that your API key is correctly formatted")
    print("2. Verify the key is active in your NVD account")
    print("3. Make sure there are no extra spaces or characters")
    
    print("\nIf all tests succeed:")
    print("The API key is working - the issue is in our application code")
    
    print("\nIf you see 403 errors:")
    print("The API key might not be activated yet (can take a few minutes)")

if __name__ == "__main__":
    asyncio.run(test_api_key())
