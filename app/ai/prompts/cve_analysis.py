CVE_ANALYSIS_PROMPT = '''
You are an elite cybersecurity expert and penetration tester analyzing CVE vulnerabilities. Provide a comprehensive, sophisticated technical analysis of the following CVE with detailed exploitation scenarios.

CVE Information:
- CVE ID: {cve_id}
- Description: {description}
- CVSS v3 Score: {cvss_score}
- CVSS v3 Vector: {cvss_vector}
- CWE IDs: {cwe_ids}

Provide a detailed JSON analysis covering advanced exploitation techniques, attack chains, and technical implementation details:

{{
  "vulnerability_classification": {{
    "primary_type": "Detailed vulnerability classification",
    "cwe_analysis": "Analysis of CWE patterns and root causes",
    "attack_surface": "Description of exposed attack surface",
    "vulnerability_chain": "How this vulnerability fits into attack chains"
  }},
  "exploitation_analysis": {{
    "attack_complexity": "Low|Medium|High",
    "exploitation_difficulty": "Trivial|Easy|Moderate|Hard|Expert",
    "time_to_exploit": "Minutes|Hours|Days|Weeks",
    "skill_level_required": "Script Kiddie|Intermediate|Advanced|Expert",
    "tools_required": ["List of tools/frameworks needed"],
    "exploit_reliability": "Very High|High|Medium|Low|Very Low"
  }},
  "attack_scenarios": [
    {{
      "scenario_name": "Primary attack scenario name",
      "attack_vector": "Network|Local|Physical|Adjacent",
      "attack_flow": [
        "Step 1: Initial reconnaissance and target identification",
        "Step 2: Vulnerability discovery and validation", 
        "Step 3: Exploit development and payload crafting",
        "Step 4: Exploitation and initial access",
        "Step 5: Post-exploitation and persistence"
      ],
      "technical_details": {{
        "entry_point": "Specific entry point for exploitation",
        "payload_type": "Type of payload used",
        "exploitation_technique": "Detailed technique description",
        "bypass_methods": ["Methods to bypass security controls"],
        "persistence_methods": ["Ways to maintain access"]
      }},
      "prerequisites": ["Detailed prerequisites for this scenario"],
      "success_indicators": ["How to know if exploitation succeeded"],
      "detection_evasion": ["Techniques to avoid detection"]
    }}
  ],
  "technical_exploitation_details": {{
    "memory_corruption": {{
      "applicable": true/false,
      "corruption_type": "Buffer overflow|Use-after-free|Double-free|etc",
      "memory_layout": "Description of memory layout exploitation",
      "rop_gadgets": "ROP/JOP gadget requirements",
      "aslr_bypass": "ASLR bypass techniques",
      "dep_bypass": "DEP/NX bypass methods"
    }},
    "code_injection": {{
      "applicable": true/false,
      "injection_type": "SQL|Command|Code|Script|etc",
      "injection_points": ["Specific injection vectors"],
      "payload_encoding": "Required payload encoding/obfuscation",
      "filter_bypass": ["Methods to bypass input filters"],
      "execution_context": "Context where code executes"
    }},
    "privilege_escalation": {{
      "applicable": true/false,
      "escalation_type": "Horizontal|Vertical|Both",
      "target_privileges": "Target privilege level",
      "escalation_method": "Specific escalation technique",
      "persistence_mechanism": "How to maintain elevated access"
    }}
  }},
  "impact_analysis": {{
    "immediate_impact": {{
      "confidentiality": "None|Low|High",
      "integrity": "None|Low|High",
      "availability": "None|Low|High",
      "scope": "Unchanged|Changed",
      "data_exposure": "Types of data that could be exposed",
      "system_compromise": "Level of system compromise possible"
    }},
    "cascading_effects": [
      "Secondary vulnerabilities that could be triggered",
      "Lateral movement possibilities",
      "Network propagation potential",
      "Data exfiltration scenarios"
    ],
    "business_consequences": {{
      "financial_impact": "Potential financial losses",
      "operational_disruption": "Business operation impacts",
      "reputation_damage": "Brand and reputation risks",
      "compliance_violations": "Regulatory compliance issues",
      "recovery_time": "Estimated recovery timeframe"
    }}
  }},
  "advanced_exploitation_techniques": {{
    "chaining_opportunities": ["How to chain with other vulnerabilities"],
    "zero_day_potential": "Likelihood of zero-day exploitation",
    "apt_relevance": "Relevance to APT attack patterns",
    "automation_potential": "Can this be automated/weaponized",
    "mass_exploitation": "Potential for mass exploitation campaigns"
  }},
  "defensive_analysis": {{
    "detection_methods": [
      "Network-based detection signatures",
      "Host-based detection indicators", 
      "Behavioral analysis patterns",
      "Log analysis techniques"
    ],
    "prevention_controls": [
      "Technical controls to prevent exploitation",
      "Configuration hardening measures",
      "Network segmentation strategies",
      "Access control improvements"
    ],
    "monitoring_recommendations": [
      "Specific monitoring points to implement",
      "Alert thresholds and triggers",
      "Forensic artifacts to collect"
    ]
  }},
  "threat_intelligence": {{
    "exploit_in_wild": "Known exploitation in the wild",
    "threat_actor_interest": "APT/criminal group interest level",
    "exploit_market_value": "Estimated value in exploit markets",
    "weaponization_timeline": "Expected weaponization timeframe"
  }},
  "remediation_strategy": {{
    "immediate_actions": [
      "Emergency response steps",
      "Temporary mitigations",
      "Incident response procedures"
    ],
    "short_term_fixes": [
      "Quick fixes and workarounds",
      "Configuration changes",
      "Access restrictions"
    ],
    "long_term_solutions": [
      "Permanent fixes and patches",
      "Architecture improvements",
      "Security program enhancements"
    ],
    "validation_steps": [
      "How to verify fixes are effective",
      "Testing procedures",
      "Monitoring for regression"
    ]
  }},
  "confidence_assessment": {{
    "overall_confidence": 85,
    "analysis_limitations": ["Factors limiting analysis confidence"],
    "additional_research_needed": ["Areas requiring further investigation"],
    "expert_consultation": "Recommendation for expert review"
  }}
}}

Provide only the JSON response with sophisticated technical analysis. Focus on actionable intelligence for security professionals and penetration testers.
'''
