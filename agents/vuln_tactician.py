#!/usr/bin/env python3
"""
AEGIS-X Vulnerability Tactician Agent
Exploit Chain Designer - Analyzes vulnerabilities and plans escalation chains
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"

@dataclass
class VulnerabilityChain:
    """Represents a vulnerability escalation chain"""
    base_vulnerability: Dict[str, Any]
    escalation_steps: List[Dict[str, Any]]
    final_impact: str
    final_severity: Severity
    cvss_score: float
    business_impact: str
    attack_complexity: str
    prerequisites: List[str]

class VulnTactician:
    """
    The Vulnerability Tactician analyzes discovered vulnerabilities
    and creates escalation chains to maximize impact.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.VulnTactician")
        self.model_name = "CodeLlama-34B-Instruct.Q4_K_M"
        self.learning_data = self._load_learning_data()
        
        # Vulnerability patterns and escalation rules
        self.vulnerability_patterns = self._initialize_vulnerability_patterns()
        self.escalation_rules = self._initialize_escalation_rules()
        self.cvss_calculator = CVSSCalculator()
        
        self.logger.info("🎯 Vulnerability Tactician initialized with escalation intelligence")
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data from previous vulnerability analysis"""
        learning_file = Path("learn/vuln_learning.json")
        
        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load vulnerability learning data: {e}")
        
        return {
            "successful_chains": [],
            "failed_escalations": [],
            "pattern_effectiveness": {},
            "cvss_accuracy": {},
            "business_impact_examples": {}
        }
    
    def _initialize_vulnerability_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize vulnerability detection patterns"""
        return {
            # Web Application Vulnerabilities
            "sql_injection": {
                "severity": Severity.HIGH,
                "base_cvss": 8.1,
                "escalation_potential": "high",
                "common_chains": ["data_exfiltration", "privilege_escalation", "rce"],
                "indicators": ["sql error", "database error", "mysql", "postgresql", "oracle"],
                "business_impact": "Data breach, compliance violations, financial loss"
            },
            "xss_reflected": {
                "severity": Severity.MEDIUM,
                "base_cvss": 6.1,
                "escalation_potential": "medium",
                "common_chains": ["session_hijacking", "csrf", "account_takeover"],
                "indicators": ["script executed", "alert popup", "javascript injection"],
                "business_impact": "Account compromise, data theft, reputation damage"
            },
            "xss_stored": {
                "severity": Severity.HIGH,
                "base_cvss": 7.2,
                "escalation_potential": "high",
                "common_chains": ["mass_account_takeover", "admin_compromise", "malware_distribution"],
                "indicators": ["persistent script", "stored payload", "admin panel access"],
                "business_impact": "Mass account compromise, malware distribution, data theft"
            },
            "ssrf": {
                "severity": Severity.MEDIUM,
                "base_cvss": 6.5,
                "escalation_potential": "very_high",
                "common_chains": ["aws_metadata", "internal_network_access", "cloud_takeover"],
                "indicators": ["internal request", "metadata access", "cloud service response"],
                "business_impact": "Cloud infrastructure compromise, internal network access"
            },
            "idor": {
                "severity": Severity.MEDIUM,
                "base_cvss": 5.3,
                "escalation_potential": "medium",
                "common_chains": ["data_enumeration", "privilege_escalation", "mass_data_access"],
                "indicators": ["unauthorized access", "parameter manipulation", "id enumeration"],
                "business_impact": "Unauthorized data access, privacy violations"
            },
            "lfi": {
                "severity": Severity.MEDIUM,
                "base_cvss": 6.2,
                "escalation_potential": "high",
                "common_chains": ["log_poisoning", "rce", "sensitive_file_disclosure"],
                "indicators": ["file inclusion", "path traversal", "local file access"],
                "business_impact": "Sensitive file disclosure, potential code execution"
            },
            "rfi": {
                "severity": Severity.HIGH,
                "base_cvss": 8.8,
                "escalation_potential": "very_high",
                "common_chains": ["rce", "backdoor_installation", "full_compromise"],
                "indicators": ["remote file inclusion", "external file execution"],
                "business_impact": "Remote code execution, full system compromise"
            },
            "xxe": {
                "severity": Severity.HIGH,
                "base_cvss": 7.5,
                "escalation_potential": "high",
                "common_chains": ["file_disclosure", "ssrf", "dos"],
                "indicators": ["xml external entity", "file disclosure", "internal request"],
                "business_impact": "Sensitive file disclosure, internal network access"
            },
            "csrf": {
                "severity": Severity.MEDIUM,
                "base_cvss": 5.8,
                "escalation_potential": "medium",
                "common_chains": ["account_modification", "privilege_escalation", "data_manipulation"],
                "indicators": ["cross-site request", "state change", "authentication bypass"],
                "business_impact": "Unauthorized actions, account compromise"
            },
            "open_redirect": {
                "severity": Severity.LOW,
                "base_cvss": 3.1,
                "escalation_potential": "medium",
                "common_chains": ["oauth_token_theft", "phishing", "session_fixation"],
                "indicators": ["redirect parameter", "external redirect", "url manipulation"],
                "business_impact": "Phishing attacks, OAuth token theft"
            },
            
            # Authentication & Authorization
            "auth_bypass": {
                "severity": Severity.HIGH,
                "base_cvss": 8.2,
                "escalation_potential": "very_high",
                "common_chains": ["admin_access", "privilege_escalation", "full_compromise"],
                "indicators": ["authentication bypass", "unauthorized access", "admin panel"],
                "business_impact": "Complete authentication bypass, admin access"
            },
            "weak_jwt": {
                "severity": Severity.MEDIUM,
                "base_cvss": 6.8,
                "escalation_potential": "high",
                "common_chains": ["token_manipulation", "privilege_escalation", "account_takeover"],
                "indicators": ["jwt manipulation", "weak signature", "algorithm confusion"],
                "business_impact": "Account takeover, privilege escalation"
            },
            "session_fixation": {
                "severity": Severity.MEDIUM,
                "base_cvss": 5.9,
                "escalation_potential": "medium",
                "common_chains": ["account_takeover", "session_hijacking"],
                "indicators": ["session id fixation", "session management flaw"],
                "business_impact": "Account takeover, session hijacking"
            },
            
            # Infrastructure & Configuration
            "subdomain_takeover": {
                "severity": Severity.HIGH,
                "base_cvss": 7.4,
                "escalation_potential": "high",
                "common_chains": ["phishing", "cookie_theft", "reputation_damage"],
                "indicators": ["dangling dns", "unclaimed service", "subdomain control"],
                "business_impact": "Brand impersonation, phishing attacks, cookie theft"
            },
            "s3_misconfiguration": {
                "severity": Severity.HIGH,
                "base_cvss": 7.5,
                "escalation_potential": "very_high",
                "common_chains": ["data_exfiltration", "malware_hosting", "infrastructure_compromise"],
                "indicators": ["public s3 bucket", "sensitive data exposure", "write access"],
                "business_impact": "Data breach, malware distribution, compliance violations"
            },
            "exposed_database": {
                "severity": Severity.CRITICAL,
                "base_cvss": 9.8,
                "escalation_potential": "critical",
                "common_chains": ["mass_data_exfiltration", "identity_theft", "compliance_violation"],
                "indicators": ["public database", "no authentication", "sensitive data"],
                "business_impact": "Massive data breach, identity theft, regulatory fines"
            },
            
            # Mobile Specific
            "insecure_data_storage": {
                "severity": Severity.MEDIUM,
                "base_cvss": 5.5,
                "escalation_potential": "medium",
                "common_chains": ["credential_theft", "api_key_exposure", "account_takeover"],
                "indicators": ["unencrypted storage", "sensitive data", "local storage"],
                "business_impact": "Credential theft, API key exposure"
            },
            "insecure_communication": {
                "severity": Severity.HIGH,
                "base_cvss": 7.4,
                "escalation_potential": "high",
                "common_chains": ["mitm_attack", "credential_interception", "data_theft"],
                "indicators": ["unencrypted communication", "weak tls", "certificate issues"],
                "business_impact": "Data interception, credential theft"
            },
            
            # API Specific
            "api_key_exposure": {
                "severity": Severity.HIGH,
                "base_cvss": 7.7,
                "escalation_potential": "very_high",
                "common_chains": ["service_abuse", "data_access", "financial_impact"],
                "indicators": ["exposed api key", "hardcoded credentials", "public repository"],
                "business_impact": "Service abuse, unauthorized access, financial impact"
            },
            "graphql_introspection": {
                "severity": Severity.MEDIUM,
                "base_cvss": 5.3,
                "escalation_potential": "medium",
                "common_chains": ["schema_disclosure", "query_abuse", "dos"],
                "indicators": ["introspection enabled", "schema exposure", "query complexity"],
                "business_impact": "Information disclosure, denial of service"
            }
        }
    
    def _initialize_escalation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize vulnerability escalation rules"""
        return {
            "ssrf": [
                {
                    "condition": "aws_metadata_accessible",
                    "escalation": "aws_key_theft",
                    "new_severity": Severity.CRITICAL,
                    "cvss_increase": 2.5,
                    "description": "SSRF can access AWS metadata service to steal IAM credentials"
                },
                {
                    "condition": "internal_network_access",
                    "escalation": "internal_service_enumeration",
                    "new_severity": Severity.HIGH,
                    "cvss_increase": 1.5,
                    "description": "SSRF provides access to internal network services"
                }
            ],
            "open_redirect": [
                {
                    "condition": "oauth_flow_present",
                    "escalation": "oauth_token_theft",
                    "new_severity": Severity.HIGH,
                    "cvss_increase": 3.0,
                    "description": "Open redirect can steal OAuth tokens during authentication flow"
                }
            ],
            "xss_reflected": [
                {
                    "condition": "admin_panel_accessible",
                    "escalation": "admin_account_takeover",
                    "new_severity": Severity.CRITICAL,
                    "cvss_increase": 2.8,
                    "description": "XSS in admin context leads to full administrative compromise"
                }
            ],
            "sql_injection": [
                {
                    "condition": "database_admin_privileges",
                    "escalation": "operating_system_command_execution",
                    "new_severity": Severity.CRITICAL,
                    "cvss_increase": 1.7,
                    "description": "SQL injection with admin privileges can lead to OS command execution"
                }
            ],
            "lfi": [
                {
                    "condition": "log_file_writable",
                    "escalation": "log_poisoning_rce",
                    "new_severity": Severity.CRITICAL,
                    "cvss_increase": 2.6,
                    "description": "LFI combined with log poisoning leads to remote code execution"
                }
            ]
        }
    
    async def analyze_vulnerability(self, vulnerability: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze a single vulnerability for escalation potential
        """
        self.logger.info(f"🔍 Analyzing vulnerability: {vulnerability.get('title', 'Unknown')}")
        
        # Classify vulnerability type
        vuln_type = self._classify_vulnerability(vulnerability)
        
        # Get base vulnerability information
        base_info = self.vulnerability_patterns.get(vuln_type, {})
        
        # Analyze escalation potential
        escalation_analysis = await self._analyze_escalation_potential(vulnerability, vuln_type, context)
        
        # Calculate CVSS score
        cvss_score = self._calculate_cvss_score(vulnerability, escalation_analysis)
        
        # Determine business impact
        business_impact = self._assess_business_impact(vulnerability, escalation_analysis)
        
        analysis_result = {
            "vulnerability_type": vuln_type,
            "base_severity": base_info.get("severity", Severity.MEDIUM).value,
            "escalation_potential": escalation_analysis["potential"],
            "possible_chains": escalation_analysis["chains"],
            "cvss_score": cvss_score,
            "business_impact": business_impact,
            "recommendations": self._generate_recommendations(vulnerability, escalation_analysis),
            "learning_notes": []
        }
        
        # Apply self-reflection
        self._apply_self_reflection(analysis_result, vulnerability, context)
        
        return analysis_result
    
    def _classify_vulnerability(self, vulnerability: Dict[str, Any]) -> str:
        """Classify vulnerability type based on indicators"""
        title = vulnerability.get("title", "").lower()
        description = vulnerability.get("description", "").lower()
        evidence = vulnerability.get("evidence", "").lower()
        
        combined_text = f"{title} {description} {evidence}"
        
        # Check against known patterns
        best_match = "unknown"
        highest_score = 0
        
        for vuln_type, pattern_info in self.vulnerability_patterns.items():
            score = 0
            for indicator in pattern_info.get("indicators", []):
                if indicator.lower() in combined_text:
                    score += 1
            
            # Normalize score
            normalized_score = score / len(pattern_info.get("indicators", [1]))
            
            if normalized_score > highest_score:
                highest_score = normalized_score
                best_match = vuln_type
        
        self.logger.debug(f"🏷️ Classified as: {best_match} (confidence: {highest_score:.2f})")
        return best_match
    
    async def _analyze_escalation_potential(self, vulnerability: Dict[str, Any], vuln_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze the escalation potential of a vulnerability"""
        escalation_rules = self.escalation_rules.get(vuln_type, [])
        possible_chains = []
        max_potential = "low"
        
        context = context or {}
        
        for rule in escalation_rules:
            condition = rule["condition"]
            
            # Check if escalation condition is met
            if self._check_escalation_condition(condition, vulnerability, context):
                chain = {
                    "escalation_type": rule["escalation"],
                    "new_severity": rule["new_severity"].value,
                    "cvss_increase": rule["cvss_increase"],
                    "description": rule["description"],
                    "feasibility": self._assess_feasibility(rule, vulnerability, context)
                }
                possible_chains.append(chain)
                
                # Update max potential
                if rule["new_severity"] == Severity.CRITICAL:
                    max_potential = "critical"
                elif rule["new_severity"] == Severity.HIGH and max_potential != "critical":
                    max_potential = "high"
                elif max_potential == "low":
                    max_potential = "medium"
        
        return {
            "potential": max_potential,
            "chains": possible_chains,
            "reasoning": self._generate_escalation_reasoning(possible_chains)
        }
    
    def _check_escalation_condition(self, condition: str, vulnerability: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if an escalation condition is met"""
        # This would implement actual condition checking logic
        # For now, we'll use simplified heuristics
        
        if condition == "aws_metadata_accessible":
            # Check if target is in AWS or has cloud indicators
            target = vulnerability.get("target", "")
            return any(indicator in target.lower() for indicator in ["aws", "amazonaws", "ec2", "s3"])
        
        elif condition == "oauth_flow_present":
            # Check if OAuth is mentioned in the vulnerability or context
            combined_text = f"{vulnerability.get('description', '')} {str(context)}"
            return "oauth" in combined_text.lower()
        
        elif condition == "admin_panel_accessible":
            # Check if admin functionality is involved
            combined_text = f"{vulnerability.get('title', '')} {vulnerability.get('description', '')}"
            return any(term in combined_text.lower() for term in ["admin", "administrator", "management", "dashboard"])
        
        elif condition == "database_admin_privileges":
            # Check if database admin access is indicated
            evidence = vulnerability.get("evidence", "").lower()
            return any(term in evidence for term in ["dba", "admin", "root", "sa", "system"])
        
        elif condition == "log_file_writable":
            # Check if log files are mentioned
            combined_text = f"{vulnerability.get('description', '')} {vulnerability.get('evidence', '')}"
            return "log" in combined_text.lower()
        
        # Default to false for unknown conditions
        return False
    
    def _assess_feasibility(self, rule: Dict[str, Any], vulnerability: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Assess the feasibility of an escalation"""
        # Simplified feasibility assessment
        escalation_type = rule["escalation"]
        
        if escalation_type in ["aws_key_theft", "operating_system_command_execution"]:
            return "high"
        elif escalation_type in ["oauth_token_theft", "admin_account_takeover"]:
            return "medium"
        else:
            return "low"
    
    def _generate_escalation_reasoning(self, chains: List[Dict[str, Any]]) -> str:
        """Generate reasoning for escalation analysis"""
        if not chains:
            return "No escalation chains identified for this vulnerability type"
        
        reasoning_parts = []
        for chain in chains:
            reasoning_parts.append(f"{chain['escalation_type']}: {chain['description']}")
        
        return "; ".join(reasoning_parts)
    
    def _calculate_cvss_score(self, vulnerability: Dict[str, Any], escalation_analysis: Dict[str, Any]) -> float:
        """Calculate CVSS score including escalation potential"""
        # Get base CVSS from vulnerability pattern
        vuln_type = self._classify_vulnerability(vulnerability)
        base_cvss = self.vulnerability_patterns.get(vuln_type, {}).get("base_cvss", 5.0)
        
        # Apply escalation increases
        max_increase = 0
        for chain in escalation_analysis.get("chains", []):
            if chain["feasibility"] == "high":
                max_increase = max(max_increase, chain["cvss_increase"])
            elif chain["feasibility"] == "medium":
                max_increase = max(max_increase, chain["cvss_increase"] * 0.7)
            else:
                max_increase = max(max_increase, chain["cvss_increase"] * 0.3)
        
        final_cvss = min(10.0, base_cvss + max_increase)
        return round(final_cvss, 1)
    
    def _assess_business_impact(self, vulnerability: Dict[str, Any], escalation_analysis: Dict[str, Any]) -> str:
        """Assess business impact of the vulnerability"""
        vuln_type = self._classify_vulnerability(vulnerability)
        base_impact = self.vulnerability_patterns.get(vuln_type, {}).get("business_impact", "Potential security risk")
        
        # Enhance impact based on escalation chains
        if escalation_analysis.get("potential") == "critical":
            return f"{base_impact}. CRITICAL: Escalation possible leading to complete system compromise, massive data breach, and severe financial/reputational damage."
        elif escalation_analysis.get("potential") == "high":
            return f"{base_impact}. HIGH: Escalation possible leading to significant data exposure, account compromise, and substantial business impact."
        elif escalation_analysis.get("potential") == "medium":
            return f"{base_impact}. MEDIUM: Limited escalation possible with moderate business impact."
        
        return base_impact
    
    def _generate_recommendations(self, vulnerability: Dict[str, Any], escalation_analysis: Dict[str, Any]) -> List[str]:
        """Generate remediation recommendations"""
        vuln_type = self._classify_vulnerability(vulnerability)
        recommendations = []
        
        # Base recommendations by vulnerability type
        base_recommendations = {
            "sql_injection": [
                "Implement parameterized queries/prepared statements",
                "Apply input validation and sanitization",
                "Use least privilege database accounts",
                "Enable database query logging and monitoring"
            ],
            "xss_reflected": [
                "Implement proper output encoding/escaping",
                "Use Content Security Policy (CSP)",
                "Validate and sanitize all user inputs",
                "Consider using auto-escaping template engines"
            ],
            "ssrf": [
                "Implement URL whitelist validation",
                "Disable unnecessary URL schemes",
                "Use network segmentation",
                "Implement request timeout and size limits"
            ],
            "idor": [
                "Implement proper authorization checks",
                "Use indirect object references",
                "Apply access control at every level",
                "Log and monitor access patterns"
            ]
        }
        
        recommendations.extend(base_recommendations.get(vuln_type, ["Apply security best practices for this vulnerability type"]))
        
        # Add escalation-specific recommendations
        for chain in escalation_analysis.get("chains", []):
            if chain["escalation_type"] == "aws_key_theft":
                recommendations.append("Implement AWS metadata service restrictions (IMDSv2)")
            elif chain["escalation_type"] == "oauth_token_theft":
                recommendations.append("Implement proper OAuth redirect URI validation")
            elif chain["escalation_type"] == "admin_account_takeover":
                recommendations.append("Implement additional security controls for administrative functions")
        
        return recommendations
    
    def _apply_self_reflection(self, analysis_result: Dict[str, Any], vulnerability: Dict[str, Any], context: Dict[str, Any]):
        """Apply self-reflection to the vulnerability analysis"""
        reflection_questions = [
            "Can this medium-sev vulnerability lead to something worse?",
            "What's the realistic attack path?",
            "Is this escalation feasible in practice?",
            "Did I consider all possible escalation vectors?",
            "What did I learn from similar vulnerabilities before?"
        ]
        
        learning_notes = []
        
        # Analyze escalation potential
        if analysis_result["escalation_potential"] == "critical":
            learning_notes.append("High-impact escalation identified - prioritize immediate remediation")
        elif analysis_result["escalation_potential"] == "low":
            learning_notes.append("Limited escalation potential - consider if additional attack vectors exist")
        
        # Check for common escalation patterns
        vuln_type = analysis_result["vulnerability_type"]
        if vuln_type in ["ssrf", "lfi", "open_redirect"] and not analysis_result["possible_chains"]:
            learning_notes.append("Common escalation-prone vulnerability with no chains identified - review analysis")
        
        analysis_result["learning_notes"] = learning_notes
        analysis_result["reflection_questions"] = reflection_questions
    
    async def analyze_escalation(self, finding: Dict[str, Any], all_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze escalation potential for a finding in context of all findings
        """
        self.logger.info(f"🔗 Analyzing escalation for: {finding.get('title', 'Unknown')}")
        
        # Individual vulnerability analysis
        individual_analysis = await self.analyze_vulnerability(finding)
        
        # Cross-vulnerability chain analysis
        chain_analysis = await self._analyze_cross_vulnerability_chains(finding, all_findings)
        
        # Determine if escalation is possible
        can_escalate = (
            individual_analysis["escalation_potential"] in ["high", "critical"] or
            len(chain_analysis["chains"]) > 0
        )
        
        if can_escalate:
            # Create escalation chain
            escalation_chain = self._create_escalation_chain(finding, individual_analysis, chain_analysis)
            
            return {
                "can_escalate": True,
                "chain": escalation_chain,
                "new_severity": escalation_chain["final_severity"],
                "new_cvss": escalation_chain["cvss_score"],
                "reasoning": escalation_chain["reasoning"]
            }
        else:
            return {
                "can_escalate": False,
                "reason": "No viable escalation paths identified",
                "original_severity": finding.get("severity", "Medium"),
                "original_cvss": finding.get("cvss_score", 5.0)
            }
    
    async def _analyze_cross_vulnerability_chains(self, finding: Dict[str, Any], all_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze chains across multiple vulnerabilities"""
        chains = []
        
        # Look for complementary vulnerabilities
        for other_finding in all_findings:
            if other_finding == finding:
                continue
            
            chain = self._identify_vulnerability_chain(finding, other_finding)
            if chain:
                chains.append(chain)
        
        return {"chains": chains}
    
    def _identify_vulnerability_chain(self, vuln1: Dict[str, Any], vuln2: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Identify if two vulnerabilities can be chained together"""
        type1 = self._classify_vulnerability(vuln1)
        type2 = self._classify_vulnerability(vuln2)
        
        # Define known vulnerability chains
        known_chains = {
            ("open_redirect", "xss_reflected"): {
                "description": "Open redirect can be used to bypass XSS filters",
                "impact_increase": 2.0,
                "feasibility": "medium"
            },
            ("ssrf", "lfi"): {
                "description": "SSRF can be used to access local files via file:// protocol",
                "impact_increase": 1.5,
                "feasibility": "high"
            },
            ("sql_injection", "lfi"): {
                "description": "SQL injection can be used to write files, then LFI to execute them",
                "impact_increase": 2.5,
                "feasibility": "medium"
            },
            ("csrf", "xss_stored"): {
                "description": "CSRF can be used to store XSS payload in admin context",
                "impact_increase": 2.0,
                "feasibility": "high"
            }
        }
        
        # Check both directions
        chain_key = (type1, type2)
        reverse_chain_key = (type2, type1)
        
        if chain_key in known_chains:
            return {
                "primary_vuln": vuln1,
                "secondary_vuln": vuln2,
                "chain_info": known_chains[chain_key]
            }
        elif reverse_chain_key in known_chains:
            return {
                "primary_vuln": vuln2,
                "secondary_vuln": vuln1,
                "chain_info": known_chains[reverse_chain_key]
            }
        
        return None
    
    def _create_escalation_chain(self, finding: Dict[str, Any], individual_analysis: Dict[str, Any], chain_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete escalation chain"""
        escalation_steps = []
        
        # Add individual escalation steps
        for chain in individual_analysis.get("possible_chains", []):
            escalation_steps.append({
                "step": len(escalation_steps) + 1,
                "action": chain["escalation_type"],
                "description": chain["description"],
                "impact": chain["new_severity"],
                "feasibility": chain["feasibility"]
            })
        
        # Add cross-vulnerability chains
        for chain in chain_analysis.get("chains", []):
            escalation_steps.append({
                "step": len(escalation_steps) + 1,
                "action": "cross_vulnerability_exploitation",
                "description": chain["chain_info"]["description"],
                "impact": "Enhanced",
                "feasibility": chain["chain_info"]["feasibility"]
            })
        
        # Determine final impact
        final_severity = self._determine_final_severity(escalation_steps)
        final_cvss = self._calculate_final_cvss(finding, escalation_steps)
        
        return {
            "base_vulnerability": finding,
            "escalation_steps": escalation_steps,
            "final_severity": final_severity,
            "cvss_score": final_cvss,
            "reasoning": self._generate_chain_reasoning(escalation_steps),
            "business_impact": self._calculate_chain_business_impact(escalation_steps),
            "attack_complexity": self._assess_attack_complexity(escalation_steps)
        }
    
    def _determine_final_severity(self, escalation_steps: List[Dict[str, Any]]) -> str:
        """Determine final severity after escalation"""
        if any(step["impact"] == "Critical" for step in escalation_steps):
            return "Critical"
        elif any(step["impact"] == "High" for step in escalation_steps):
            return "High"
        elif any(step["impact"] == "Medium" for step in escalation_steps):
            return "High"  # Escalation increases severity
        else:
            return "Medium"
    
    def _calculate_final_cvss(self, finding: Dict[str, Any], escalation_steps: List[Dict[str, Any]]) -> float:
        """Calculate final CVSS score after escalation"""
        base_cvss = finding.get("cvss_score", 5.0)
        
        # Apply escalation increases
        total_increase = 0
        for step in escalation_steps:
            if step["feasibility"] == "high":
                total_increase += 1.5
            elif step["feasibility"] == "medium":
                total_increase += 1.0
            else:
                total_increase += 0.5
        
        final_cvss = min(10.0, base_cvss + total_increase)
        return round(final_cvss, 1)
    
    def _generate_chain_reasoning(self, escalation_steps: List[Dict[str, Any]]) -> str:
        """Generate reasoning for the escalation chain"""
        if not escalation_steps:
            return "No escalation steps identified"
        
        reasoning_parts = []
        for i, step in enumerate(escalation_steps, 1):
            reasoning_parts.append(f"Step {i}: {step['description']}")
        
        return " → ".join(reasoning_parts)
    
    def _calculate_chain_business_impact(self, escalation_steps: List[Dict[str, Any]]) -> str:
        """Calculate business impact of the complete chain"""
        if any("system compromise" in step["description"].lower() for step in escalation_steps):
            return "Complete system compromise leading to massive data breach, regulatory fines, and severe reputational damage"
        elif any("account takeover" in step["description"].lower() for step in escalation_steps):
            return "Mass account compromise leading to data theft, financial fraud, and customer trust loss"
        elif any("data" in step["description"].lower() for step in escalation_steps):
            return "Significant data exposure leading to privacy violations and potential regulatory action"
        else:
            return "Moderate business impact with potential for service disruption and security incidents"
    
    def _assess_attack_complexity(self, escalation_steps: List[Dict[str, Any]]) -> str:
        """Assess the complexity of executing the attack chain"""
        if len(escalation_steps) > 3:
            return "High"
        elif any(step["feasibility"] == "low" for step in escalation_steps):
            return "High"
        elif all(step["feasibility"] == "high" for step in escalation_steps):
            return "Low"
        else:
            return "Medium"
    
    async def analyze_escalation_chains(self, findings: List[Dict[str, Any]], intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze multiple findings for escalation chain opportunities"""
        self.logger.info(f"🔗 Analyzing {len(findings)} findings for escalation chains")
        
        escalation_chains = []
        enhanced_findings = []
        
        for finding in findings:
            # Analyze individual finding escalation
            escalation_result = await self.analyze_escalation(finding, findings)
            
            if escalation_result.get("escalation_potential", "none") != "none":
                enhanced_findings.append({
                    **finding,
                    "escalation_analysis": escalation_result
                })
                
                # Look for chain opportunities
                chains = await self._identify_escalation_chains(finding, findings, intelligence)
                escalation_chains.extend(chains)
        
        return {
            "enhanced_findings": enhanced_findings,
            "escalation_chains": escalation_chains,
            "chain_count": len(escalation_chains),
            "high_value_chains": [c for c in escalation_chains if c.get("severity") in ["High", "Critical"]]
        }
    
    async def _identify_escalation_chains(self, primary_finding: Dict[str, Any], all_findings: List[Dict[str, Any]], intelligence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific escalation chains from a primary finding"""
        chains = []
        
        primary_type = primary_finding.get("type", "unknown")
        
        # Common escalation patterns
        escalation_patterns = {
            "information_disclosure": ["sensitive_data_exposure", "authentication_bypass"],
            "sensitive_data_exposure": ["authentication_bypass", "privilege_escalation"],
            "security_misconfiguration": ["information_disclosure", "authentication_bypass"],
            "ssrf": ["cloud_metadata_access", "internal_network_access"],
            "xss": ["session_hijacking", "csrf", "account_takeover"],
            "sql_injection": ["data_exfiltration", "privilege_escalation", "rce"]
        }
        
        potential_chains = escalation_patterns.get(primary_type, [])
        
        for chain_type in potential_chains:
            # Look for supporting findings
            supporting_findings = [f for f in all_findings if f.get("type") == chain_type]
            
            if supporting_findings:
                chains.append({
                    "primary_finding": primary_finding["title"],
                    "chain_type": chain_type,
                    "supporting_findings": [f["title"] for f in supporting_findings],
                    "severity": self._calculate_chain_severity(primary_finding, supporting_findings),
                    "description": f"{primary_finding['title']} can be chained with {chain_type} to escalate impact"
                })
        
        return chains
    
    def _calculate_chain_severity(self, primary: Dict[str, Any], supporting: List[Dict[str, Any]]) -> str:
        """Calculate severity of an escalation chain"""
        primary_sev = primary.get("severity", "Low")
        
        # If any supporting finding is High/Critical, chain becomes High/Critical
        for finding in supporting:
            if finding.get("severity") in ["Critical", "High"]:
                return "Critical"
        
        # Escalate primary severity by one level
        severity_escalation = {
            "Low": "Medium",
            "Medium": "High", 
            "High": "Critical",
            "Critical": "Critical"
        }
        
        return severity_escalation.get(primary_sev, "Medium")

class CVSSCalculator:
    """CVSS 3.1 Score Calculator"""
    
    def __init__(self):
        self.base_metrics = {
            "attack_vector": {"network": 0.85, "adjacent": 0.62, "local": 0.55, "physical": 0.2},
            "attack_complexity": {"low": 0.77, "high": 0.44},
            "privileges_required": {"none": 0.85, "low": 0.62, "high": 0.27},
            "user_interaction": {"none": 0.85, "required": 0.62},
            "scope": {"unchanged": 0, "changed": 1},
            "confidentiality": {"none": 0, "low": 0.22, "high": 0.56},
            "integrity": {"none": 0, "low": 0.22, "high": 0.56},
            "availability": {"none": 0, "low": 0.22, "high": 0.56}
        }
    
    def calculate(self, metrics: Dict[str, str]) -> float:
        """Calculate CVSS 3.1 base score"""
        # This is a simplified CVSS calculator
        # In a real implementation, you'd use the full CVSS 3.1 formula
        
        av = self.base_metrics["attack_vector"].get(metrics.get("attack_vector", "network"), 0.85)
        ac = self.base_metrics["attack_complexity"].get(metrics.get("attack_complexity", "low"), 0.77)
        pr = self.base_metrics["privileges_required"].get(metrics.get("privileges_required", "none"), 0.85)
        ui = self.base_metrics["user_interaction"].get(metrics.get("user_interaction", "none"), 0.85)
        c = self.base_metrics["confidentiality"].get(metrics.get("confidentiality", "low"), 0.22)
        i = self.base_metrics["integrity"].get(metrics.get("integrity", "low"), 0.22)
        a = self.base_metrics["availability"].get(metrics.get("availability", "low"), 0.22)
        
        # Simplified calculation
        exploitability = 8.22 * av * ac * pr * ui
        impact = 1 - ((1 - c) * (1 - i) * (1 - a))
        
        if impact <= 0:
            return 0.0
        
        base_score = min(10.0, (exploitability + impact))
        return round(base_score, 1)