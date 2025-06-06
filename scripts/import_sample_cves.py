#!/usr/bin/env python3
"""
CVE Data Import Script
This script adds sample CVE data to test the platform
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app.database import SessionLocal
from app.models.cve import CVE
import json

def add_sample_cves():
    """Add sample CVE data for testing"""
    
    db = SessionLocal()
    
    try:
        print("🔄 Adding sample CVE data...")
        
        # Sample CVEs for testing
        sample_cves = [
            {
                "cve_id": "CVE-2024-1234",
                "description": "A critical buffer overflow vulnerability in web server software allows remote code execution. An attacker can exploit this vulnerability by sending specially crafted HTTP requests to trigger a buffer overflow condition.",
                "published_date": datetime(2024, 1, 15),
                "modified_date": datetime(2024, 1, 20),
                "cvss_v3_score": 9.8,
                "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "severity_level": "CRITICAL",
                "cwe_ids": ["CWE-119", "CWE-787"],
                "affected_products": [
                    {"cpe": "cpe:2.3:a:example:webserver:*:*:*:*:*:*:*:*", "version_start": "1.0", "version_end": "2.4"}
                ],
                "references": [
                    {"url": "https://example.com/security-advisory", "source": "vendor", "tags": ["vendor-advisory"]}
                ]
            },
            {
                "cve_id": "CVE-2024-5678",
                "description": "SQL injection vulnerability in authentication module allows unauthorized database access. Attackers can bypass authentication and execute arbitrary SQL commands.",
                "published_date": datetime(2024, 2, 10),
                "modified_date": datetime(2024, 2, 15),
                "cvss_v3_score": 8.1,
                "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N",
                "severity_level": "HIGH",
                "cwe_ids": ["CWE-89"],
                "affected_products": [
                    {"cpe": "cpe:2.3:a:example:webapp:*:*:*:*:*:*:*:*", "version_start": "3.0", "version_end": "3.5"}
                ],
                "references": [
                    {"url": "https://nvd.nist.gov/vuln/detail/CVE-2024-5678", "source": "nvd", "tags": ["third-party-advisory"]}
                ]
            },
            {
                "cve_id": "CVE-2024-9999",
                "description": "Cross-site scripting (XSS) vulnerability in user input validation allows execution of malicious scripts in user browsers.",
                "published_date": datetime(2024, 3, 5),
                "modified_date": datetime(2024, 3, 8),
                "cvss_v3_score": 6.1,
                "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
                "severity_level": "MEDIUM",
                "cwe_ids": ["CWE-79"],
                "affected_products": [
                    {"cpe": "cpe:2.3:a:example:cms:*:*:*:*:*:*:*:*", "version_start": "2.0", "version_end": "2.9"}
                ],
                "references": [
                    {"url": "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-9999", "source": "mitre", "tags": ["third-party-advisory"]}
                ]
            },
            {
                "cve_id": "CVE-2023-1111",
                "description": "Privilege escalation vulnerability in system service allows local users to gain administrator privileges through improper permission handling.",
                "published_date": datetime(2023, 12, 1),
                "modified_date": datetime(2023, 12, 5),
                "cvss_v3_score": 7.8,
                "cvss_v3_vector": "CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H",
                "severity_level": "HIGH",
                "cwe_ids": ["CWE-269"],
                "affected_products": [
                    {"cpe": "cpe:2.3:o:example:operating_system:*:*:*:*:*:*:*:*", "version_start": "10.0", "version_end": "10.3"}
                ],
                "references": [
                    {"url": "https://example-os.com/security/advisories/2023-1111", "source": "vendor", "tags": ["vendor-advisory"]}
                ]
            },
            {
                "cve_id": "CVE-2023-2222",
                "description": "Information disclosure vulnerability in logging component exposes sensitive user data in application logs.",
                "published_date": datetime(2023, 11, 15),
                "modified_date": datetime(2023, 11, 20),
                "cvss_v3_score": 5.3,
                "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
                "severity_level": "MEDIUM",
                "cwe_ids": ["CWE-200"],
                "affected_products": [
                    {"cpe": "cpe:2.3:a:example:logger:*:*:*:*:*:*:*:*", "version_start": "1.0", "version_end": "1.8"}
                ],
                "references": [
                    {"url": "https://github.com/example/logger/security/advisories/GHSA-xxxx-yyyy-zzzz", "source": "github", "tags": ["third-party-advisory"]}
                ]
            }
        ]
        
        # Add each CVE to database
        added_count = 0
        for cve_data in sample_cves:
            # Check if CVE already exists
            existing = db.query(CVE).filter(CVE.cve_id == cve_data["cve_id"]).first()
            if existing:
                print(f"  ⚠️  {cve_data['cve_id']} already exists, skipping...")
                continue
            
            # Create new CVE
            new_cve = CVE(**cve_data)
            db.add(new_cve)
            added_count += 1
            print(f"  ✅ Added {cve_data['cve_id']} ({cve_data['severity_level']})")
        
        # Commit changes
        db.commit()
        
        print(f"\n🎉 Successfully added {added_count} CVEs to database!")
        
        # Show summary
        total_cves = db.query(CVE).count()
        critical_count = db.query(CVE).filter(CVE.severity_level == "CRITICAL").count()
        high_count = db.query(CVE).filter(CVE.severity_level == "HIGH").count()
        medium_count = db.query(CVE).filter(CVE.severity_level == "MEDIUM").count()
        
        print(f"\n📊 Database Summary:")
        print(f"  Total CVEs: {total_cves}")
        print(f"  Critical: {critical_count}")
        print(f"  High: {high_count}")
        print(f"  Medium: {medium_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding CVE data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_search():
    """Test CVE search functionality"""
    
    db = SessionLocal()
    
    try:
        print("\n🔍 Testing CVE search...")
        
        # Test basic search
        all_cves = db.query(CVE).all()
        print(f"  Found {len(all_cves)} total CVEs")
        
        # Test severity filter
        critical_cves = db.query(CVE).filter(CVE.severity_level == "CRITICAL").all()
        print(f"  Found {len(critical_cves)} critical CVEs")
        
        # Test specific CVE
        specific_cve = db.query(CVE).filter(CVE.cve_id == "CVE-2024-1234").first()
        if specific_cve:
            print(f"  ✅ Found specific CVE: {specific_cve.cve_id}")
        else:
            print(f"  ❌ Could not find specific CVE")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing search: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 CVE Data Import Tool")
    print("======================")
    
    # Add sample data
    if add_sample_cves():
        # Test search
        if test_search():
            print("\n🎯 Success! Your platform now has CVE data to search.")
            print("\n📋 Next steps:")
            print("1. Go back to the web interface: http://localhost:8000/static/frontend/index.html")
            print("2. Try searching for 'CVE-2024-1234' or use severity filter 'Critical'")
            print("3. Click 'Analyze' on any CVE to test AI analysis")
        else:
            print("\n⚠️  Data added but search test failed")
    else:
        print("\n❌ Failed to add sample data")
        sys.exit(1)
