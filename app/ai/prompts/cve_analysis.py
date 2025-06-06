CVE_ANALYSIS_PROMPT = '''
You are a cybersecurity expert analyzing CVE vulnerabilities. Provide a comprehensive technical analysis of the following CVE.

CVE Information:
- CVE ID: {cve_id}
- Description: {description}
- CVSS v3 Score: {cvss_score}
- CVSS v3 Vector: {cvss_vector}
- CWE IDs: {cwe_ids}

Please analyze this vulnerability and provide a structured JSON response with the following fields:

{{
  "vulnerability_type": "Brief classification of the vulnerability",
  "attack_complexity": "Low|Medium|High",
  "attack_vectors": [
    {{
      "vector": "Vector name (e.g., Network, Local, Physical)",
      "description": "How this attack vector can be exploited",
      "requirements": ["List of requirements for this vector"]
    }}
  ],
  "impact_assessment": {{
    "confidentiality": "None|Low|High",
    "integrity": "None|Low|High", 
    "availability": "None|Low|High",
    "scope": "Unchanged|Changed",
    "description": "Detailed impact description"
  }},
  "exploitability": {{
    "ease_of_exploitation": "Low|Medium|High",
    "exploit_availability": "Unknown|Theoretical|Proof of Concept|Functional|High",
    "prerequisites": ["List of prerequisites for exploitation"],
    "technical_requirements": ["Technical skills/tools needed"]
  }},
  "business_impact": {{
    "severity": "Critical|High|Medium|Low",
    "potential_damage": ["List of potential business impacts"],
    "affected_assets": ["Types of assets at risk"]
  }},
  "confidence_score": 85,
  "additional_notes": "Any additional technical insights or concerns"
}}

Provide only the JSON response, no additional text.
'''
