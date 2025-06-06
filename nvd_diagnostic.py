#!/usr/bin/env python3
"""
NVD API Diagnostic Script
Run this to identify the exact issue with the NVD API
"""

import aiohttp
import asyncio
import json
from datetime import datetime

async def diagnose_nvd_api():
    """Comprehensive NVD API diagnosis"""
    
    print("🔍 NVD API Diagnostic Tool")
    print("=" * 50)
    
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    # Test cases in order of complexity
    test_cases = [
        {
            "name": "1. Basic connectivity test",
            "url": base_url,
            "params": {},
            "expected": "Should return some response"
        },
        {
            "name": "2. Minimal valid request",
            "url": base_url,
            "params": {"resultsPerPage": 5},
            "expected": "Should return recent CVEs"
        },
        {
            "name": "3. Specific CVE test",
            "url": base_url,
            "params": {"cveId": "CVE-2021-44228"},  # Log4j vulnerability
            "expected": "Should return Log4j CVE"
        },
        {
            "name": "4. Date range test",
            "url": base_url,
            "params": {
                "resultsPerPage": 5,
                "pubStartDate": "2024-01-01T00:00:00.000",
                "pubEndDate": "2024-12-31T23:59:59.999"
            },
            "expected": "Should return 2024 CVEs"
        },
        {
            "name": "5. Severity filter test",
            "url": base_url,
            "params": {
                "resultsPerPage": 5,
                "cvssV3Severity": "CRITICAL"
            },
            "expected": "Should return critical CVEs"
        }
    ]
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "CVE-Analysis-Platform-Diagnostic/1.0"
    }
    
    async with aiohttp.ClientSession() as session:
        for i, test in enumerate(test_cases, 1):
            print(f"\n🧪 {test['name']}")
            print(f"Expected: {test['expected']}")
            print(f"URL: {test['url']}")
            print(f"Params: {test['params']}")
            
            try:
                # Add delay between requests
                if i > 1:
                    print("⏳ Waiting 6 seconds (rate limiting)...")
                    await asyncio.sleep(6)
                
                async with session.get(
                    test['url'],
                    params=test['params'],
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    print(f"📊 Status Code: {response.status}")
                    print(f"📋 Headers: {dict(response.headers)}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            total_results = data.get("totalResults", 0)
                            vulnerabilities = data.get("vulnerabilities", [])
                            
                            print(f"✅ SUCCESS!")
                            print(f"   Total Results: {total_results}")
                            print(f"   Returned: {len(vulnerabilities)} vulnerabilities")
                            
                            if vulnerabilities:
                                first_cve = vulnerabilities[0].get("cve", {})
                                cve_id = first_cve.get("id", "Unknown")
                                print(f"   First CVE: {cve_id}")
                            
                            # Check response structure
                            print(f"   Response keys: {list(data.keys())}")
                            
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON Parse Error: {e}")
                            response_text = await response.text()
                            print(f"   Raw response: {response_text[:200]}...")
                    
                    elif response.status == 404:
                        print(f"❌ NOT FOUND (404)")
                        response_text = await response.text()
                        print(f"   Response: {response_text}")
                        
                    elif response.status == 403:
                        print(f"❌ FORBIDDEN (403)")
                        response_text = await response.text()
                        print(f"   Response: {response_text}")
                        print("   💡 You might need an API key")
                        
                    elif response.status == 429:
                        print(f"❌ RATE LIMITED (429)")
                        response_text = await response.text()
                        print(f"   Response: {response_text}")
                        
                    else:
                        print(f"❌ ERROR ({response.status})")
                        response_text = await response.text()
                        print(f"   Response: {response_text}")
                        
            except aiohttp.ClientError as e:
                print(f"❌ CLIENT ERROR: {e}")
            except asyncio.TimeoutError:
                print(f"❌ TIMEOUT ERROR")
            except Exception as e:
                print(f"❌ UNEXPECTED ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS SUMMARY:")
    print("1. If ALL tests fail with 404: NVD API endpoint might have changed")
    print("2. If tests 1-2 work but others fail: Parameter formatting issue")
    print("3. If you get 403: You need an API key")
    print("4. If you get timeouts: Network/firewall issue")
    print("5. If basic connectivity fails: Check internet connection")
    
    print("\n🔧 RECOMMENDED ACTIONS:")
    print("- Check NVD API documentation: https://nvd.nist.gov/developers/vulnerabilities")
    print("- Get free API key: https://nvd.nist.gov/developers/request-an-api-key")
    print("- Check firewall/proxy settings")

if __name__ == "__main__":
    asyncio.run(diagnose_nvd_api())
