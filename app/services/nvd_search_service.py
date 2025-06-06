#!/usr/bin/env python3
"""
app/services/nvd_search_service.py
Enhanced NVD Search Service - Prioritizes Recent CVEs for Keywords
"""

import aiohttp
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class NVDSearchService:
    """Service for searching CVEs directly from NVD API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        
        # Try multiple ways to get the API key
        self.api_key = self._get_api_key(api_key)
        
        # Set rate limiting based on API key availability
        if self.api_key:
            self.rate_limit_delay = 0.6
            logger.info(f"Using API key for faster rate limiting")
        else:
            self.rate_limit_delay = 6
            logger.info("No API key - using public rate limiting (6 seconds)")
    
    def _get_api_key(self, provided_key: Optional[str] = None) -> Optional[str]:
        """Get API key from multiple sources and validate it"""
        
        # Try provided key first
        if provided_key and provided_key.strip():
            return provided_key.strip()
        
        # Try settings
        try:
            settings_key = getattr(settings, 'nvd_api_key', None)
            if settings_key and settings_key.strip():
                return settings_key.strip()
        except Exception as e:
            logger.warning(f"Could not read API key from settings: {e}")
        
        # Try environment variable directly
        try:
            env_key = os.getenv('NVD_API_KEY')
            if env_key and env_key.strip():
                return env_key.strip()
        except Exception as e:
            logger.warning(f"Could not read API key from environment: {e}")
        
        return None
        
    async def search_live(self, 
                         cve_id: Optional[str] = None,
                         keyword: Optional[str] = None,
                         severity: Optional[str] = None,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         limit: int = 20) -> Dict[str, Any]:
        """Enhanced search that prioritizes recent CVEs"""
        
        try:
            logger.info(f"NVD Search: cve_id={cve_id}, keyword={keyword}, severity={severity}")
            
            # Strategy 1: Specific CVE ID (most reliable)
            if cve_id and cve_id.strip():
                return await self._search_specific_cve(cve_id.strip())
            
            # Strategy 2: Recent-first keyword search
            if keyword and keyword.strip():
                return await self._recent_keyword_search(keyword.strip(), severity, limit)
            
            # Strategy 3: Recent CVEs by severity
            return await self._search_recent_cves(severity, limit)
            
        except Exception as e:
            logger.error(f"NVD search error: {e}")
            return {
                "success": False,
                "error": f"NVD search failed: {str(e)}",
                "source": "NVD Live",
                "rate_limited": False
            }
    
    async def _search_specific_cve(self, cve_id: str) -> Dict[str, Any]:
        """Search for a specific CVE ID"""
        
        params = {"cveId": cve_id}
        return await self._make_nvd_request(params, f"specific CVE {cve_id}")
    
    async def _recent_keyword_search(self, keyword: str, severity: Optional[str], limit: int) -> Dict[str, Any]:
        """Search for keyword in recent CVEs first, then expand if needed"""
        
        logger.info(f"Recent-first keyword search for: {keyword}")
        all_results = []
        
        # Strategy 1: Search recent CVEs (last 2 years) in reverse chronological order
        recent_results = await self._search_recent_time_periods(keyword, severity, limit)
        all_results.extend(recent_results)
        
        # If we don't have enough recent results, try broader search
        if len(all_results) < limit:
            logger.info(f"Found {len(all_results)} recent results, searching broader...")
            broader_results = await self._search_broader_for_keyword(keyword, severity, limit - len(all_results))
            all_results.extend(broader_results)
        
        # Sort all results by date (most recent first)
        all_results.sort(key=lambda x: x.get('published_date', '1999-01-01'), reverse=True)
        
        return {
            "success": True,
            "source": "NVD Live",
            "total_results": len(all_results),
            "results": all_results[:limit],
            "rate_limited": False,
            "message": f"Found {len(all_results)} CVEs matching '{keyword}' (prioritizing recent vulnerabilities)"
        }
    
    async def _search_recent_time_periods(self, keyword: str, severity: Optional[str], limit: int) -> List[Dict]:
        """Search recent time periods for keyword matches"""
        
        all_results = []
        
        # Define recent time periods (within 120-day NVD limit)
        time_periods = [
            ("last 30 days", 0, 30),
            ("30-60 days ago", 30, 60),
            ("60-90 days ago", 60, 90),
            ("90-120 days ago", 90, 120)
        ]
        
        for period_name, start_days, end_days in time_periods:
            try:
                end_date = datetime.now() - timedelta(days=start_days)
                start_date = datetime.now() - timedelta(days=end_days)
                
                params = {
                    "resultsPerPage": 100,  # Get more results to filter
                    "startIndex": 0,
                    "pubStartDate": start_date.strftime("%Y-%m-%dT00:00:00.000"),
                    "pubEndDate": end_date.strftime("%Y-%m-%dT23:59:59.999")
                }
                
                if severity and severity.upper() in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    params["cvssV3Severity"] = severity.upper()
                
                logger.info(f"Searching {period_name} for '{keyword}'...")
                period_result = await self._make_nvd_request(params, f"{period_name} search")
                
                if period_result["success"] and period_result.get("results"):
                    # Filter for keyword matches
                    filtered_period = self._filter_results_by_keyword_detailed(
                        period_result["results"], keyword
                    )
                    all_results.extend(filtered_period)
                    
                    logger.info(f"{period_name}: {len(filtered_period)} matches found")
                    
                    # If we have enough results, prioritize recent ones
                    if len(all_results) >= limit:
                        break
                        
            except Exception as e:
                logger.warning(f"Time-based search for {period_name} failed: {e}")
                continue
        
        return all_results
    
    async def _search_broader_for_keyword(self, keyword: str, severity: Optional[str], needed: int) -> List[Dict]:
        """Search broader time ranges if recent search didn't find enough"""
        
        logger.info(f"Searching broader time ranges for '{keyword}'...")
        all_results = []
        
        # Try different years (going backwards from recent)
        current_year = datetime.now().year
        years_to_search = [current_year - 1, current_year - 2, current_year - 3]
        
        for year in years_to_search:
            try:
                # Search by year in chunks to avoid 120-day limit
                year_results = await self._search_year_in_chunks(year, keyword, severity, needed)
                all_results.extend(year_results)
                
                if len(all_results) >= needed:
                    break
                    
            except Exception as e:
                logger.warning(f"Year {year} search failed: {e}")
                continue
        
        return all_results[:needed]
    
    async def _search_year_in_chunks(self, year: int, keyword: str, severity: Optional[str], needed: int) -> List[Dict]:
        """Search a specific year in 3-month chunks"""
        
        year_results = []
        
        # Divide year into quarters
        quarters = [
            (f"{year} Q4", f"{year}-10-01", f"{year}-12-31"),
            (f"{year} Q3", f"{year}-07-01", f"{year}-09-30"),
            (f"{year} Q2", f"{year}-04-01", f"{year}-06-30"),
            (f"{year} Q1", f"{year}-01-01", f"{year}-03-31")
        ]
        
        for quarter_name, start_date_str, end_date_str in quarters:
            try:
                params = {
                    "resultsPerPage": 100,
                    "startIndex": 0,
                    "pubStartDate": f"{start_date_str}T00:00:00.000",
                    "pubEndDate": f"{end_date_str}T23:59:59.999"
                }
                
                if severity and severity.upper() in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    params["cvssV3Severity"] = severity.upper()
                
                logger.info(f"Searching {quarter_name}...")
                quarter_result = await self._make_nvd_request(params, f"{quarter_name} search")
                
                if quarter_result["success"] and quarter_result.get("results"):
                    filtered_quarter = self._filter_results_by_keyword_detailed(
                        quarter_result["results"], keyword
                    )
                    year_results.extend(filtered_quarter)
                    
                    logger.info(f"{quarter_name}: {len(filtered_quarter)} matches found")
                    
                    if len(year_results) >= needed:
                        break
                        
            except Exception as e:
                logger.warning(f"Quarter {quarter_name} search failed: {e}")
                continue
        
        return year_results
    
    async def _search_recent_cves(self, severity: Optional[str], limit: int) -> Dict[str, Any]:
        """Search for recent CVEs without keyword filtering"""
        
        # Get recent CVEs (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        params = {
            "resultsPerPage": min(limit, 100),
            "startIndex": 0,
            "pubStartDate": start_date.strftime("%Y-%m-%dT00:00:00.000"),
            "pubEndDate": end_date.strftime("%Y-%m-%dT23:59:59.999")
        }
        
        if severity and severity.upper() in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            params["cvssV3Severity"] = severity.upper()
        
        result = await self._make_nvd_request(params, "recent CVEs")
        
        if result["success"]:
            # Sort by date (most recent first)
            if result.get("results"):
                result["results"].sort(key=lambda x: x.get('published_date', '1999-01-01'), reverse=True)
                result["message"] = f"Showing recent {severity or 'all'} severity CVEs from last 30 days"
        
        return result
    
    def _filter_results_by_keyword_detailed(self, results: List[Dict], keyword: str) -> List[Dict]:
        """Enhanced keyword filtering with better matching"""
        
        if not results or not keyword:
            return results
        
        keyword_lower = keyword.lower()
        keyword_words = keyword_lower.split()
        filtered_results = []
        
        for cve in results:
            description = (cve.get("description") or "").lower()
            cve_id = (cve.get("cve_id") or "").lower()
            
            # Check for exact keyword match first (highest priority)
            if keyword_lower in description or keyword_lower in cve_id:
                filtered_results.append(cve)
                continue
            
            # Check for partial word matches (for compound words)
            match_found = False
            for word in keyword_words:
                if len(word) >= 3:
                    # Look for word boundaries to avoid false matches
                    if (f" {word} " in f" {description} " or 
                        f" {word} " in f" {cve_id} " or
                        description.startswith(word + " ") or
                        description.endswith(" " + word) or
                        word in description.split("-") or
                        word in description.split("_") or
                        word in description.split(".")):
                        match_found = True
                        break
            
            if match_found:
                filtered_results.append(cve)
        
        return filtered_results
    
    async def _make_nvd_request(self, params: Dict[str, Any], search_description: str) -> Dict[str, Any]:
        """Make request with comprehensive error handling"""
        
        headers = {
            "Accept": "application/json",
            "User-Agent": "CVE-Analysis-Platform/1.0"
        }
        
        if self.api_key:
            headers["apiKey"] = self.api_key
        
        await asyncio.sleep(self.rate_limit_delay)
        
        logger.info(f"NVD API request for {search_description}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    logger.info(f"NVD API response status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            formatted_results = self._format_nvd_results(data)
                            
                            return {
                                "success": True,
                                "source": "NVD Live",
                                "total_results": data.get("totalResults", 0),
                                "results": formatted_results,
                                "search_params": params,
                                "rate_limited": False
                            }
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON response: {e}")
                            return {
                                "success": False,
                                "error": "Invalid JSON response from NVD API",
                                "source": "NVD Live",
                                "rate_limited": False
                            }
                    
                    elif response.status == 404:
                        error_msg = response.headers.get('message', 'No results found')
                        logger.warning(f"NVD API 404 for {search_description}: {error_msg}")
                        
                        return {
                            "success": True,
                            "source": "NVD Live",
                            "total_results": 0,
                            "results": [],
                            "search_params": params,
                            "rate_limited": False,
                            "message": f"No results found"
                        }
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"NVD API error {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"API error {response.status}",
                            "source": "NVD Live",
                            "rate_limited": False
                        }
                        
        except Exception as e:
            logger.error(f"Request error: {e}")
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "source": "NVD Live",
                "rate_limited": False
            }
    
    def _format_nvd_results(self, nvd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format NVD API response to match our CVE format"""
        
        formatted_cves = []
        
        vulnerabilities = nvd_data.get("vulnerabilities", [])
        logger.info(f"Processing {len(vulnerabilities)} vulnerabilities from NVD")
        
        for vuln in vulnerabilities:
            cve_data = vuln.get("cve", {})
            
            try:
                cve_id = cve_data.get("id", "Unknown")
                
                # Extract description
                descriptions = cve_data.get("descriptions", [])
                description = "No description available"
                for desc in descriptions:
                    if desc.get("lang") == "en":
                        description = desc.get("value", "")
                        break
                
                # Extract dates
                published_date = cve_data.get("published", "")
                modified_date = cve_data.get("lastModified", "")
                
                # Extract CVSS information
                cvss_v3_score = None
                cvss_v3_vector = None
                severity_level = "UNKNOWN"
                
                metrics = cve_data.get("metrics", {})
                cvss_v3_data = metrics.get("cvssMetricV31", []) or metrics.get("cvssMetricV30", [])
                
                if cvss_v3_data:
                    cvss_info = cvss_v3_data[0].get("cvssData", {})
                    cvss_v3_score = cvss_info.get("baseScore")
                    cvss_v3_vector = cvss_info.get("vectorString")
                    severity_level = cvss_info.get("baseSeverity", "UNKNOWN")
                
                # Extract CWE information
                cwe_ids = []
                weaknesses = cve_data.get("weaknesses", [])
                for weakness in weaknesses:
                    for desc in weakness.get("description", []):
                        if desc.get("lang") == "en":
                            cwe_value = desc.get("value", "")
                            if cwe_value and cwe_value not in cwe_ids:
                                cwe_ids.append(cwe_value)
                
                # Extract references
                references = []
                ref_data = cve_data.get("references", [])
                for ref in ref_data[:3]:
                    references.append({
                        "url": ref.get("url", ""),
                        "source": ref.get("source", ""),
                        "tags": ref.get("tags", [])
                    })
                
                # Format dates
                try:
                    if published_date:
                        pub_date_formatted = datetime.fromisoformat(
                            published_date.replace("Z", "+00:00")
                        ).strftime("%Y-%m-%d")
                    else:
                        pub_date_formatted = "Unknown"
                except:
                    pub_date_formatted = published_date[:10] if published_date and len(published_date) >= 10 else "Unknown"
                
                formatted_cve = {
                    "id": f"nvd-{cve_id}",
                    "cve_id": cve_id,
                    "description": description[:300] + "..." if len(description) > 300 else description,
                    "published_date": pub_date_formatted,
                    "modified_date": modified_date,
                    "cvss_v3_score": cvss_v3_score,
                    "cvss_v3_vector": cvss_v3_vector,
                    "severity_level": severity_level,
                    "cwe_ids": cwe_ids,
                    "references": references,
                    "source": "NVD Live",
                    "can_import": True,
                    "nvd_link": f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                }
                
                formatted_cves.append(formatted_cve)
                
            except Exception as e:
                logger.error(f"Error formatting CVE {cve_data.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully formatted {len(formatted_cves)} CVEs")
        return formatted_cves
    
    async def get_cve_details(self, cve_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific CVE"""
        
        result = await self.search_live(cve_id=cve_id, limit=1)
        
        if result["success"] and result["results"]:
            return {
                "success": True,
                "cve": result["results"][0]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "CVE not found")
            }
