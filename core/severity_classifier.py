#!/usr/bin/env python3
"""
AEGIS-X Professional Vulnerability Severity Classification System
Implements industry-standard CVSS v3.1 scoring with advanced AI-powered
severity confirmation and impact analysis.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import requests
from datetime import datetime
import numpy as np

class SeverityLevel(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class CVSSMetric(Enum):
    """CVSS v3.1 metrics"""
    # Base metrics
    ATTACK_VECTOR = "AV"
    ATTACK_COMPLEXITY = "AC"
    PRIVILEGES_REQUIRED = "PR"
    USER_INTERACTION = "UI"
    SCOPE = "S"
    CONFIDENTIALITY = "C"
    INTEGRITY = "I"
    AVAILABILITY = "A"
    
    # Temporal metrics
    EXPLOIT_CODE_MATURITY = "E"
    REMEDIATION_LEVEL = "RL"
    REPORT_CONFIDENCE = "RC"

@dataclass
class VulnerabilityImpact:
    """Represents the impact of a vulnerability"""
    confidentiality_impact: str
    integrity_impact: str
    availability_impact: str
    business_impact: str
    technical_impact: str
    financial_impact: str
    reputation_impact: str
    compliance_impact: str

@dataclass
class CVSSScore:
    """CVSS v3.1 score breakdown"""
    base_score: float
    temporal_score: float
    environmental_score: float
    overall_score: float
    vector_string: str
    severity_level: SeverityLevel
    metrics: Dict[str, str]

@dataclass
class SeverityAssessment:
    """Complete severity assessment"""
    vulnerability_id: str
    title: str
    cvss_score: CVSSScore
    impact_analysis: VulnerabilityImpact
    severity_justification: str
    confirmation_level: str  # confirmed, likely, possible, false_positive
    verification_methods: List[str]
    risk_factors: List[str]
    mitigation_urgency: str
    created_at: str

class ProfessionalSeverityClassifier:
    """
    Professional-grade vulnerability severity classification system.
    Uses CVSS v3.1 standard with advanced AI-powered analysis to ensure
    accurate severity assessment and confirmation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.SeverityClassifier")
        
        # CVSS v3.1 scoring matrices
        self.cvss_values = {
            "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},  # Attack Vector
            "AC": {"L": 0.77, "H": 0.44},  # Attack Complexity
            "PR": {"N": 0.85, "L": 0.62, "H": 0.27},  # Privileges Required
            "UI": {"N": 0.85, "R": 0.62},  # User Interaction
            "S": {"U": 1.0, "C": 1.0},  # Scope (multiplier handled separately)
            "C": {"H": 0.56, "L": 0.22, "N": 0.0},  # Confidentiality
            "I": {"H": 0.56, "L": 0.22, "N": 0.0},  # Integrity
            "A": {"H": 0.56, "L": 0.22, "N": 0.0}   # Availability
        }
        
        # Vulnerability type to CVSS mapping
        self.vuln_type_cvss_mapping = {
            "rce": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "C",
                "C": "H", "I": "H", "A": "H"
            },
            "sqli": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U",
                "C": "H", "I": "H", "A": "N"
            },
            "xss": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "R", "S": "C",
                "C": "L", "I": "L", "A": "N"
            },
            "lfi": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U",
                "C": "H", "I": "N", "A": "N"
            },
            "ssrf": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "C",
                "C": "H", "I": "L", "A": "L"
            },
            "csrf": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "R", "S": "U",
                "C": "N", "I": "H", "A": "N"
            },
            "xxe": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U",
                "C": "H", "I": "L", "A": "L"
            },
            "deserialization": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "C",
                "C": "H", "I": "H", "A": "H"
            },
            "path_traversal": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U",
                "C": "H", "I": "N", "A": "N"
            },
            "file_upload": {
                "AV": "N", "AC": "L", "PR": "L", "UI": "N", "S": "C",
                "C": "H", "I": "H", "A": "H"
            },
            "authentication_bypass": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "C",
                "C": "H", "I": "H", "A": "N"
            },
            "privilege_escalation": {
                "AV": "L", "AC": "L", "PR": "L", "UI": "N", "S": "C",
                "C": "H", "I": "H", "A": "H"
            },
            "information_disclosure": {
                "AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U",
                "C": "L", "I": "N", "A": "N"
            },
            "weak_crypto": {
                "AV": "N", "AC": "H", "PR": "N", "UI": "N", "S": "U",
                "C": "H", "I": "L", "A": "N"
            },
            "business_logic": {
                "AV": "N", "AC": "L", "PR": "L", "UI": "N", "S": "U",
                "C": "L", "I": "H", "A": "N"
            }
        }
        
        # Critical vulnerability indicators
        self.critical_indicators = [
            "remote code execution",
            "arbitrary file upload",
            "sql injection with admin privileges",
            "authentication bypass",
            "privilege escalation to admin",
            "deserialization rce",
            "command injection",
            "unrestricted file upload",
            "admin panel access",
            "database access",
            "system file access",
            "root access",
            "administrator access"
        ]
        
        # High severity indicators
        self.high_indicators = [
            "sql injection",
            "cross-site scripting",
            "server-side request forgery",
            "local file inclusion",
            "xml external entity",
            "insecure direct object reference",
            "sensitive data exposure",
            "broken access control",
            "security misconfiguration",
            "cross-site request forgery"
        ]
        
        # Business impact factors
        self.business_impact_factors = {
            "financial_data": 3.0,
            "personal_data": 2.5,
            "authentication_system": 2.8,
            "payment_system": 3.0,
            "admin_functionality": 2.7,
            "user_data": 2.0,
            "public_facing": 1.5,
            "internal_system": 1.2,
            "development_environment": 0.8
        }
    
    async def assess_vulnerability_severity(self, vulnerability: Dict[str, Any]) -> SeverityAssessment:
        """
        Perform comprehensive vulnerability severity assessment
        """
        self.logger.info(f"🎯 Assessing severity for vulnerability: {vulnerability.get('id', 'unknown')}")
        
        try:
            # 1. Calculate CVSS score
            cvss_score = await self._calculate_cvss_score(vulnerability)
            
            # 2. Analyze impact
            impact_analysis = await self._analyze_vulnerability_impact(vulnerability)
            
            # 3. Confirm severity level
            confirmation_level = await self._confirm_severity_level(vulnerability, cvss_score)
            
            # 4. Identify risk factors
            risk_factors = await self._identify_risk_factors(vulnerability)
            
            # 5. Determine mitigation urgency
            mitigation_urgency = await self._determine_mitigation_urgency(cvss_score, impact_analysis)
            
            # 6. Generate severity justification
            severity_justification = await self._generate_severity_justification(
                vulnerability, cvss_score, impact_analysis, risk_factors
            )
            
            # 7. Determine verification methods used
            verification_methods = await self._get_verification_methods(vulnerability)
            
            assessment = SeverityAssessment(
                vulnerability_id=vulnerability.get('id', 'unknown'),
                title=vulnerability.get('title', 'Unknown Vulnerability'),
                cvss_score=cvss_score,
                impact_analysis=impact_analysis,
                severity_justification=severity_justification,
                confirmation_level=confirmation_level,
                verification_methods=verification_methods,
                risk_factors=risk_factors,
                mitigation_urgency=mitigation_urgency,
                created_at=datetime.now().isoformat()
            )
            
            self.logger.info(f"✅ Severity assessment completed: {cvss_score.severity_level.value.upper()} ({cvss_score.overall_score})")
            return assessment
            
        except Exception as e:
            self.logger.error(f"❌ Failed to assess vulnerability severity: {e}")
            raise
    
    async def _calculate_cvss_score(self, vulnerability: Dict[str, Any]) -> CVSSScore:
        """Calculate CVSS v3.1 score"""
        vuln_type = vulnerability.get('type', '').lower()
        
        # Get base metrics from vulnerability type mapping
        if vuln_type in self.vuln_type_cvss_mapping:
            base_metrics = self.vuln_type_cvss_mapping[vuln_type].copy()
        else:
            # Default metrics for unknown vulnerability types
            base_metrics = {
                "AV": "N", "AC": "L", "PR": "N", "UI": "N", "S": "U",
                "C": "L", "I": "L", "A": "N"
            }
        
        # Adjust metrics based on vulnerability details
        base_metrics = await self._adjust_cvss_metrics(vulnerability, base_metrics)
        
        # Calculate base score
        base_score = self._calculate_base_score(base_metrics)
        
        # Calculate temporal score (if applicable)
        temporal_metrics = await self._get_temporal_metrics(vulnerability)
        temporal_score = self._calculate_temporal_score(base_score, temporal_metrics)
        
        # Environmental score (use base score for now)
        environmental_score = temporal_score
        
        # Overall score
        overall_score = environmental_score
        
        # Determine severity level
        severity_level = self._score_to_severity(overall_score)
        
        # Generate vector string
        vector_string = self._generate_vector_string(base_metrics, temporal_metrics)
        
        return CVSSScore(
            base_score=base_score,
            temporal_score=temporal_score,
            environmental_score=environmental_score,
            overall_score=overall_score,
            vector_string=vector_string,
            severity_level=severity_level,
            metrics={**base_metrics, **temporal_metrics}
        )
    
    async def _adjust_cvss_metrics(self, vulnerability: Dict[str, Any], base_metrics: Dict[str, str]) -> Dict[str, str]:
        """Adjust CVSS metrics based on vulnerability specifics"""
        
        # Adjust based on authentication requirements
        if vulnerability.get('requires_authentication', False):
            base_metrics["PR"] = "L"  # Low privileges required
        
        # Adjust based on user interaction
        if vulnerability.get('requires_user_interaction', False):
            base_metrics["UI"] = "R"  # Required
        
        # Adjust based on attack complexity
        if vulnerability.get('complex_exploitation', False):
            base_metrics["AC"] = "H"  # High complexity
        
        # Adjust based on network accessibility
        if vulnerability.get('local_access_only', False):
            base_metrics["AV"] = "L"  # Local access
        elif vulnerability.get('adjacent_network_only', False):
            base_metrics["AV"] = "A"  # Adjacent network
        
        # Adjust scope based on impact
        if vulnerability.get('affects_other_components', False):
            base_metrics["S"] = "C"  # Changed scope
        
        # Adjust impact based on data sensitivity
        data_sensitivity = vulnerability.get('data_sensitivity', 'low')
        if data_sensitivity == 'high':
            if base_metrics["C"] == "L":
                base_metrics["C"] = "H"
        elif data_sensitivity == 'critical':
            base_metrics["C"] = "H"
            base_metrics["I"] = "H"
        
        # Adjust based on system criticality
        system_criticality = vulnerability.get('system_criticality', 'medium')
        if system_criticality == 'high':
            if base_metrics["A"] == "N":
                base_metrics["A"] = "L"
        elif system_criticality == 'critical':
            base_metrics["A"] = "H"
        
        return base_metrics
    
    def _calculate_base_score(self, metrics: Dict[str, str]) -> float:
        """Calculate CVSS v3.1 base score"""
        
        # Get metric values
        av = self.cvss_values["AV"][metrics["AV"]]
        ac = self.cvss_values["AC"][metrics["AC"]]
        pr = self.cvss_values["PR"][metrics["PR"]]
        ui = self.cvss_values["UI"][metrics["UI"]]
        c = self.cvss_values["C"][metrics["C"]]
        i = self.cvss_values["I"][metrics["I"]]
        a = self.cvss_values["A"][metrics["A"]]
        
        # Adjust PR based on scope
        if metrics["S"] == "C" and metrics["PR"] != "N":
            pr_adjusted = {"L": 0.68, "H": 0.50}[metrics["PR"]]
        else:
            pr_adjusted = pr
        
        # Calculate exploitability
        exploitability = 8.22 * av * ac * pr_adjusted * ui
        
        # Calculate impact
        impact_base = 1 - ((1 - c) * (1 - i) * (1 - a))
        
        if metrics["S"] == "U":  # Unchanged scope
            impact = 6.42 * impact_base
        else:  # Changed scope
            impact = 7.52 * (impact_base - 0.029) - 3.25 * pow(impact_base - 0.02, 15)
        
        # Calculate base score
        if impact <= 0:
            base_score = 0.0
        elif metrics["S"] == "U":
            base_score = min(10.0, (impact + exploitability))
        else:
            base_score = min(10.0, 1.08 * (impact + exploitability))
        
        # Round up to nearest 0.1
        return round(base_score * 10) / 10
    
    async def _get_temporal_metrics(self, vulnerability: Dict[str, Any]) -> Dict[str, str]:
        """Get temporal metrics for CVSS calculation"""
        temporal_metrics = {}
        
        # Exploit Code Maturity
        if vulnerability.get('public_exploit_available', False):
            temporal_metrics["E"] = "F"  # Functional
        elif vulnerability.get('poc_available', False):
            temporal_metrics["E"] = "P"  # Proof-of-concept
        else:
            temporal_metrics["E"] = "U"  # Unproven
        
        # Remediation Level
        if vulnerability.get('patch_available', False):
            temporal_metrics["RL"] = "O"  # Official fix
        elif vulnerability.get('workaround_available', False):
            temporal_metrics["RL"] = "W"  # Workaround
        else:
            temporal_metrics["RL"] = "U"  # Unavailable
        
        # Report Confidence
        if vulnerability.get('verified', False):
            temporal_metrics["RC"] = "C"  # Confirmed
        else:
            temporal_metrics["RC"] = "R"  # Reasonable
        
        return temporal_metrics
    
    def _calculate_temporal_score(self, base_score: float, temporal_metrics: Dict[str, str]) -> float:
        """Calculate temporal score"""
        if not temporal_metrics:
            return base_score
        
        # Temporal metric values
        temporal_values = {
            "E": {"X": 1.0, "U": 0.91, "P": 0.94, "F": 0.97, "H": 1.0},
            "RL": {"X": 1.0, "O": 0.95, "T": 0.96, "W": 0.97, "U": 1.0},
            "RC": {"X": 1.0, "U": 0.92, "R": 0.96, "C": 1.0}
        }
        
        e = temporal_values["E"].get(temporal_metrics.get("E", "X"), 1.0)
        rl = temporal_values["RL"].get(temporal_metrics.get("RL", "X"), 1.0)
        rc = temporal_values["RC"].get(temporal_metrics.get("RC", "X"), 1.0)
        
        temporal_score = base_score * e * rl * rc
        
        # Round up to nearest 0.1
        return round(temporal_score * 10) / 10
    
    def _score_to_severity(self, score: float) -> SeverityLevel:
        """Convert CVSS score to severity level"""
        if score >= 9.0:
            return SeverityLevel.CRITICAL
        elif score >= 7.0:
            return SeverityLevel.HIGH
        elif score >= 4.0:
            return SeverityLevel.MEDIUM
        elif score >= 0.1:
            return SeverityLevel.LOW
        else:
            return SeverityLevel.INFO
    
    def _generate_vector_string(self, base_metrics: Dict[str, str], temporal_metrics: Dict[str, str]) -> str:
        """Generate CVSS vector string"""
        vector_parts = ["CVSS:3.1"]
        
        # Base metrics
        for metric in ["AV", "AC", "PR", "UI", "S", "C", "I", "A"]:
            vector_parts.append(f"{metric}:{base_metrics[metric]}")
        
        # Temporal metrics (if present)
        for metric in ["E", "RL", "RC"]:
            if metric in temporal_metrics and temporal_metrics[metric] != "X":
                vector_parts.append(f"{metric}:{temporal_metrics[metric]}")
        
        return "/".join(vector_parts)
    
    async def _analyze_vulnerability_impact(self, vulnerability: Dict[str, Any]) -> VulnerabilityImpact:
        """Analyze the impact of the vulnerability"""
        
        vuln_type = vulnerability.get('type', '').lower()
        severity = vulnerability.get('severity', 'medium').lower()
        
        # Confidentiality impact
        if vuln_type in ['sqli', 'lfi', 'xxe', 'information_disclosure', 'path_traversal']:
            confidentiality_impact = "High - Sensitive data can be accessed by unauthorized users"
        elif vuln_type in ['xss', 'csrf', 'ssrf']:
            confidentiality_impact = "Medium - Limited data disclosure possible"
        elif vuln_type in ['rce', 'deserialization', 'file_upload']:
            confidentiality_impact = "High - Complete system access allows data theft"
        else:
            confidentiality_impact = "Low - Minimal data exposure risk"
        
        # Integrity impact
        if vuln_type in ['rce', 'sqli', 'deserialization', 'file_upload']:
            integrity_impact = "High - Data and system files can be modified"
        elif vuln_type in ['xss', 'csrf']:
            integrity_impact = "Medium - User data and actions can be manipulated"
        elif vuln_type in ['lfi', 'xxe', 'information_disclosure']:
            integrity_impact = "Low - Primarily read-only access"
        else:
            integrity_impact = "Low - Limited ability to modify data"
        
        # Availability impact
        if vuln_type in ['rce', 'deserialization']:
            availability_impact = "High - System can be completely compromised or crashed"
        elif vuln_type in ['sqli', 'xxe']:
            availability_impact = "Medium - Database or application may become unavailable"
        elif vuln_type in ['xss', 'csrf', 'lfi', 'ssrf']:
            availability_impact = "Low - Service availability not significantly affected"
        else:
            availability_impact = "Low - Minimal impact on system availability"
        
        # Business impact
        business_impact = await self._assess_business_impact(vulnerability)
        
        # Technical impact
        technical_impact = await self._assess_technical_impact(vulnerability)
        
        # Financial impact
        financial_impact = await self._assess_financial_impact(vulnerability)
        
        # Reputation impact
        reputation_impact = await self._assess_reputation_impact(vulnerability)
        
        # Compliance impact
        compliance_impact = await self._assess_compliance_impact(vulnerability)
        
        return VulnerabilityImpact(
            confidentiality_impact=confidentiality_impact,
            integrity_impact=integrity_impact,
            availability_impact=availability_impact,
            business_impact=business_impact,
            technical_impact=technical_impact,
            financial_impact=financial_impact,
            reputation_impact=reputation_impact,
            compliance_impact=compliance_impact
        )
    
    async def _assess_business_impact(self, vulnerability: Dict[str, Any]) -> str:
        """Assess business impact of the vulnerability"""
        vuln_type = vulnerability.get('type', '').lower()
        severity = vulnerability.get('severity', 'medium').lower()
        
        if vuln_type in ['rce', 'authentication_bypass', 'privilege_escalation']:
            return "Critical - Complete system compromise could lead to business shutdown, data breaches, and significant financial losses"
        elif vuln_type in ['sqli', 'deserialization', 'file_upload']:
            return "High - Data theft and system manipulation could cause significant business disruption and regulatory penalties"
        elif vuln_type in ['xss', 'csrf', 'ssrf']:
            return "Medium - User account compromise and data manipulation could affect customer trust and business operations"
        elif vuln_type in ['lfi', 'xxe', 'information_disclosure']:
            return "Medium - Sensitive information disclosure could lead to competitive disadvantage and privacy violations"
        else:
            return "Low - Limited business impact with proper security controls in place"
    
    async def _assess_technical_impact(self, vulnerability: Dict[str, Any]) -> str:
        """Assess technical impact of the vulnerability"""
        vuln_type = vulnerability.get('type', '').lower()
        
        if vuln_type in ['rce', 'deserialization']:
            return "Critical - Complete server compromise, arbitrary code execution, full system control"
        elif vuln_type in ['sqli', 'authentication_bypass']:
            return "High - Database access, user account compromise, privilege escalation"
        elif vuln_type in ['file_upload', 'xxe']:
            return "High - File system access, internal network scanning, potential RCE"
        elif vuln_type in ['xss', 'csrf']:
            return "Medium - Client-side code execution, session hijacking, user impersonation"
        elif vuln_type in ['lfi', 'ssrf']:
            return "Medium - File system access, internal service enumeration"
        else:
            return "Low - Limited technical exploitation capabilities"
    
    async def _assess_financial_impact(self, vulnerability: Dict[str, Any]) -> str:
        """Assess financial impact of the vulnerability"""
        severity = vulnerability.get('severity', 'medium').lower()
        vuln_type = vulnerability.get('type', '').lower()
        
        if severity == 'critical' or vuln_type in ['rce', 'authentication_bypass']:
            return "High - Potential costs: $100K-$1M+ (incident response, legal fees, regulatory fines, business disruption)"
        elif severity == 'high' or vuln_type in ['sqli', 'deserialization']:
            return "Medium-High - Potential costs: $50K-$500K (data breach response, customer notification, system recovery)"
        elif severity == 'medium':
            return "Medium - Potential costs: $10K-$100K (security remediation, monitoring, reputation management)"
        else:
            return "Low - Potential costs: <$10K (patch deployment, security assessment)"
    
    async def _assess_reputation_impact(self, vulnerability: Dict[str, Any]) -> str:
        """Assess reputation impact of the vulnerability"""
        vuln_type = vulnerability.get('type', '').lower()
        severity = vulnerability.get('severity', 'medium').lower()
        
        if vuln_type in ['rce', 'authentication_bypass', 'sqli'] and severity in ['critical', 'high']:
            return "High - Public disclosure could severely damage brand reputation and customer trust"
        elif severity == 'high':
            return "Medium-High - Security incident could affect customer confidence and market position"
        elif severity == 'medium':
            return "Medium - May cause concern among security-conscious customers"
        else:
            return "Low - Minimal reputation impact with proper communication"
    
    async def _assess_compliance_impact(self, vulnerability: Dict[str, Any]) -> str:
        """Assess compliance impact of the vulnerability"""
        vuln_type = vulnerability.get('type', '').lower()
        data_types = vulnerability.get('affected_data_types', [])
        
        compliance_frameworks = []
        
        if any(data_type in ['pii', 'personal_data', 'customer_data'] for data_type in data_types):
            compliance_frameworks.extend(['GDPR', 'CCPA', 'PIPEDA'])
        
        if any(data_type in ['payment_data', 'credit_card'] for data_type in data_types):
            compliance_frameworks.append('PCI DSS')
        
        if any(data_type in ['health_data', 'medical_records'] for data_type in data_types):
            compliance_frameworks.append('HIPAA')
        
        if any(data_type in ['financial_data'] for data_type in data_types):
            compliance_frameworks.extend(['SOX', 'PCI DSS'])
        
        if compliance_frameworks:
            return f"High - Potential violations of: {', '.join(set(compliance_frameworks))}"
        else:
            return "Low - No specific compliance framework violations identified"
    
    async def _confirm_severity_level(self, vulnerability: Dict[str, Any], cvss_score: CVSSScore) -> str:
        """Confirm the severity level through multiple verification methods"""
        
        confirmation_factors = []
        
        # 1. Check if vulnerability is verified through exploitation
        if vulnerability.get('verified', False):
            confirmation_factors.append("exploitation_verified")
        
        # 2. Check for critical indicators in description
        description = vulnerability.get('description', '').lower()
        title = vulnerability.get('title', '').lower()
        
        for indicator in self.critical_indicators:
            if indicator in description or indicator in title:
                confirmation_factors.append(f"critical_indicator_{indicator.replace(' ', '_')}")
        
        for indicator in self.high_indicators:
            if indicator in description or indicator in title:
                confirmation_factors.append(f"high_indicator_{indicator.replace(' ', '_')}")
        
        # 3. Check for proof-of-concept availability
        if vulnerability.get('poc_available', False):
            confirmation_factors.append("poc_available")
        
        # 4. Check for public exploit availability
        if vulnerability.get('public_exploit_available', False):
            confirmation_factors.append("public_exploit_available")
        
        # 5. Check response patterns
        if vulnerability.get('response_analysis'):
            response_analysis = vulnerability['response_analysis']
            if response_analysis.get('error_messages'):
                confirmation_factors.append("error_messages_detected")
            if response_analysis.get('data_disclosure'):
                confirmation_factors.append("data_disclosure_confirmed")
        
        # Determine confirmation level
        if len(confirmation_factors) >= 3 and "exploitation_verified" in confirmation_factors:
            return "confirmed"
        elif len(confirmation_factors) >= 2:
            return "likely"
        elif len(confirmation_factors) >= 1:
            return "possible"
        else:
            return "needs_verification"
    
    async def _identify_risk_factors(self, vulnerability: Dict[str, Any]) -> List[str]:
        """Identify risk factors that increase vulnerability severity"""
        risk_factors = []
        
        # Network accessibility
        if vulnerability.get('publicly_accessible', True):
            risk_factors.append("Publicly accessible endpoint")
        
        # Authentication requirements
        if not vulnerability.get('requires_authentication', False):
            risk_factors.append("No authentication required")
        
        # Complexity of exploitation
        if not vulnerability.get('complex_exploitation', False):
            risk_factors.append("Simple exploitation process")
        
        # Data sensitivity
        data_sensitivity = vulnerability.get('data_sensitivity', 'low')
        if data_sensitivity in ['high', 'critical']:
            risk_factors.append(f"Affects {data_sensitivity} sensitivity data")
        
        # System criticality
        system_criticality = vulnerability.get('system_criticality', 'medium')
        if system_criticality in ['high', 'critical']:
            risk_factors.append(f"Affects {system_criticality} criticality system")
        
        # Exploit availability
        if vulnerability.get('public_exploit_available', False):
            risk_factors.append("Public exploits available")
        elif vulnerability.get('poc_available', False):
            risk_factors.append("Proof-of-concept code available")
        
        # Patch availability
        if not vulnerability.get('patch_available', False):
            risk_factors.append("No patch currently available")
        
        # Affected user base
        user_impact = vulnerability.get('affected_users', 'some')
        if user_impact == 'all':
            risk_factors.append("Affects all users")
        elif user_impact == 'many':
            risk_factors.append("Affects many users")
        
        return risk_factors
    
    async def _determine_mitigation_urgency(self, cvss_score: CVSSScore, impact_analysis: VulnerabilityImpact) -> str:
        """Determine the urgency of mitigation"""
        
        if cvss_score.severity_level == SeverityLevel.CRITICAL:
            return "Immediate - Fix within 24 hours"
        elif cvss_score.severity_level == SeverityLevel.HIGH:
            return "Urgent - Fix within 72 hours"
        elif cvss_score.severity_level == SeverityLevel.MEDIUM:
            return "High Priority - Fix within 1 week"
        elif cvss_score.severity_level == SeverityLevel.LOW:
            return "Medium Priority - Fix within 1 month"
        else:
            return "Low Priority - Fix during next maintenance window"
    
    async def _generate_severity_justification(self, vulnerability: Dict[str, Any], 
                                             cvss_score: CVSSScore, 
                                             impact_analysis: VulnerabilityImpact,
                                             risk_factors: List[str]) -> str:
        """Generate detailed severity justification"""
        
        justification_parts = []
        
        # CVSS score justification
        justification_parts.append(
            f"CVSS v3.1 Base Score: {cvss_score.base_score}/10.0 ({cvss_score.severity_level.value.upper()})"
        )
        
        # Vector string explanation
        justification_parts.append(f"Vector: {cvss_score.vector_string}")
        
        # Impact justification
        justification_parts.append("Impact Analysis:")
        justification_parts.append(f"• Confidentiality: {impact_analysis.confidentiality_impact}")
        justification_parts.append(f"• Integrity: {impact_analysis.integrity_impact}")
        justification_parts.append(f"• Availability: {impact_analysis.availability_impact}")
        
        # Business impact
        justification_parts.append(f"Business Impact: {impact_analysis.business_impact}")
        
        # Risk factors
        if risk_factors:
            justification_parts.append("Risk Factors:")
            for factor in risk_factors:
                justification_parts.append(f"• {factor}")
        
        # Vulnerability type specific justification
        vuln_type = vulnerability.get('type', '').lower()
        if vuln_type == 'rce':
            justification_parts.append(
                "Remote Code Execution vulnerabilities are classified as CRITICAL due to the "
                "potential for complete system compromise, data theft, and service disruption."
            )
        elif vuln_type == 'sqli':
            justification_parts.append(
                "SQL Injection vulnerabilities are typically HIGH severity due to potential "
                "database access, data theft, and data manipulation capabilities."
            )
        elif vuln_type == 'xss':
            justification_parts.append(
                "Cross-Site Scripting vulnerabilities range from MEDIUM to HIGH severity "
                "depending on context and potential for session hijacking or data theft."
            )
        
        return "\n".join(justification_parts)
    
    async def _get_verification_methods(self, vulnerability: Dict[str, Any]) -> List[str]:
        """Get the verification methods used to confirm the vulnerability"""
        methods = []
        
        if vulnerability.get('automated_verification', False):
            methods.append("Automated vulnerability scanner")
        
        if vulnerability.get('manual_verification', False):
            methods.append("Manual penetration testing")
        
        if vulnerability.get('payload_verification', False):
            methods.append("Payload injection testing")
        
        if vulnerability.get('response_analysis', False):
            methods.append("HTTP response analysis")
        
        if vulnerability.get('browser_verification', False):
            methods.append("Browser-based verification")
        
        if vulnerability.get('exploitation_verified', False):
            methods.append("Successful exploitation")
        
        if not methods:
            methods.append("Basic vulnerability detection")
        
        return methods

# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Example vulnerability for testing
    test_vulnerability = {
        'id': 'test_vuln_001',
        'title': 'SQL Injection in Login Form',
        'type': 'sqli',
        'description': 'SQL injection vulnerability allows database access',
        'url': 'https://example.com/login.php',
        'parameter': 'username',
        'payload': "' OR '1'='1",
        'verified': True,
        'requires_authentication': False,
        'publicly_accessible': True,
        'data_sensitivity': 'high',
        'system_criticality': 'high',
        'poc_available': True,
        'patch_available': False
    }
    
    async def test_severity_assessment():
        classifier = ProfessionalSeverityClassifier()
        assessment = await classifier.assess_vulnerability_severity(test_vulnerability)
        
        print(f"Vulnerability: {assessment.title}")
        print(f"CVSS Score: {assessment.cvss_score.overall_score}")
        print(f"Severity: {assessment.cvss_score.severity_level.value.upper()}")
        print(f"Confirmation: {assessment.confirmation_level}")
        print(f"Urgency: {assessment.mitigation_urgency}")
        print(f"\nJustification:\n{assessment.severity_justification}")
    
    # Run test
    # asyncio.run(test_severity_assessment())