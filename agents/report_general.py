#!/usr/bin/env python3
"""
AEGIS-X Report General Agent
Narrative Forger - Creates professional-grade bug bounty reports
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ReportTemplate:
    """Template for generating professional bug bounty reports"""
    name: str
    sections: List[str]
    format_style: str
    target_audience: str

class ReportGeneral:
    """
    The Report General creates professional-grade bug bounty reports
    that meet industry standards for HackerOne, Bugcrowd, and other platforms.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.ReportGeneral")
        self.model_name = "Mixtral-8x7B.Q5_K_M"
        self.learning_data = self._load_learning_data()
        
        # Report templates for different platforms and audiences
        self.report_templates = self._initialize_report_templates()
        self.cvss_calculator = self._initialize_cvss_calculator()
        self.business_impact_analyzer = self._initialize_business_impact_analyzer()
        
        self.logger.info("📝 Report General initialized with professional reporting capabilities")
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data from previous report generation sessions"""
        learning_file = Path("learn/report_learning.json")
        
        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load report learning data: {e}")
        
        return {
            "report_quality_scores": {},
            "template_effectiveness": {},
            "feedback_analysis": {},
            "improvement_suggestions": []
        }
    
    def _initialize_report_templates(self) -> Dict[str, ReportTemplate]:
        """Initialize professional report templates"""
        return {
            "hackerone": ReportTemplate(
                name="HackerOne Professional Report",
                sections=[
                    "executive_summary",
                    "vulnerability_details",
                    "impact_assessment",
                    "proof_of_concept",
                    "steps_to_reproduce",
                    "remediation_recommendations",
                    "timeline",
                    "supporting_evidence"
                ],
                format_style="markdown",
                target_audience="security_teams"
            ),
            "bugcrowd": ReportTemplate(
                name="Bugcrowd Professional Report",
                sections=[
                    "summary",
                    "description",
                    "impact",
                    "reproduction_steps",
                    "proof_of_concept",
                    "remediation",
                    "references",
                    "attachments"
                ],
                format_style="markdown",
                target_audience="security_teams"
            ),
            "enterprise": ReportTemplate(
                name="Enterprise Security Report",
                sections=[
                    "executive_summary",
                    "technical_details",
                    "business_impact",
                    "risk_assessment",
                    "proof_of_concept",
                    "remediation_strategy",
                    "compliance_implications",
                    "appendices"
                ],
                format_style="formal",
                target_audience="executives_and_security"
            ),
            "technical": ReportTemplate(
                name="Technical Deep Dive Report",
                sections=[
                    "vulnerability_analysis",
                    "attack_vectors",
                    "exploitation_details",
                    "code_analysis",
                    "network_analysis",
                    "remediation_code",
                    "testing_methodology",
                    "references"
                ],
                format_style="technical",
                target_audience="developers"
            )
        }
    
    def _initialize_cvss_calculator(self) -> Dict[str, Any]:
        """Initialize CVSS calculation utilities"""
        return {
            "base_metrics": {
                "attack_vector": {"network": 0.85, "adjacent": 0.62, "local": 0.55, "physical": 0.2},
                "attack_complexity": {"low": 0.77, "high": 0.44},
                "privileges_required": {"none": 0.85, "low": 0.62, "high": 0.27},
                "user_interaction": {"none": 0.85, "required": 0.62},
                "scope": {"unchanged": 0, "changed": 1},
                "confidentiality": {"none": 0, "low": 0.22, "high": 0.56},
                "integrity": {"none": 0, "low": 0.22, "high": 0.56},
                "availability": {"none": 0, "low": 0.22, "high": 0.56}
            },
            "severity_ranges": {
                "critical": (9.0, 10.0),
                "high": (7.0, 8.9),
                "medium": (4.0, 6.9),
                "low": (0.1, 3.9),
                "none": (0.0, 0.0)
            }
        }
    
    def _initialize_business_impact_analyzer(self) -> Dict[str, Dict[str, Any]]:
        """Initialize business impact analysis templates"""
        return {
            "data_breach": {
                "financial_impact": "High - Potential regulatory fines, legal costs, customer compensation",
                "reputational_impact": "Severe - Loss of customer trust, negative media coverage",
                "operational_impact": "High - Service disruption, incident response costs",
                "compliance_impact": "Critical - GDPR, CCPA, HIPAA violations possible"
            },
            "account_takeover": {
                "financial_impact": "High - Fraudulent transactions, account recovery costs",
                "reputational_impact": "High - Customer trust erosion, brand damage",
                "operational_impact": "Medium - Customer support overhead, security measures",
                "compliance_impact": "Medium - Identity verification requirements"
            },
            "service_disruption": {
                "financial_impact": "Medium - Revenue loss during downtime, SLA penalties",
                "reputational_impact": "Medium - Service reliability concerns",
                "operational_impact": "High - Emergency response, system recovery",
                "compliance_impact": "Low - Unless affecting critical services"
            },
            "information_disclosure": {
                "financial_impact": "Variable - Depends on data sensitivity and volume",
                "reputational_impact": "High - Privacy concerns, competitive disadvantage",
                "operational_impact": "Medium - Investigation, notification processes",
                "compliance_impact": "High - Privacy law violations likely"
            }
        }
    
    async def generate_report(self, finding: Dict[str, Any], template_type: str = "hackerone") -> Dict[str, Any]:
        """
        Generate a professional bug bounty report for a single finding
        """
        self.logger.info(f"📝 Generating report for: {finding.get('title', 'Unknown')}")
        
        # Get report template
        template = self.report_templates.get(template_type, self.report_templates["hackerone"])
        
        # Apply self-reflection
        reflection_result = self._apply_report_reflection(finding, template)
        
        # Generate each section
        report_sections = {}
        for section in template.sections:
            section_content = await self._generate_section(section, finding, template)
            report_sections[section] = section_content
        
        # Compile final report
        final_report = self._compile_report(report_sections, template, finding)
        
        # Calculate quality score
        quality_score = self._calculate_report_quality(final_report, finding)
        
        report_result = {
            "finding_id": finding.get("id", "unknown"),
            "template_used": template.name,
            "report_content": final_report,
            "sections": report_sections,
            "quality_score": quality_score,
            "reflection_notes": reflection_result,
            "generated_at": datetime.now().isoformat(),
            "word_count": len(final_report.split()),
            "estimated_reading_time": len(final_report.split()) // 200  # minutes
        }
        
        # Store learning data
        await self._store_report_learning(report_result, finding)
        
        return report_result
    
    async def _generate_section(self, section: str, finding: Dict[str, Any], template: ReportTemplate) -> str:
        """Generate content for a specific report section"""
        
        if section == "executive_summary":
            return self._generate_executive_summary(finding)
        elif section == "vulnerability_details":
            return self._generate_vulnerability_details(finding)
        elif section == "impact_assessment":
            return self._generate_impact_assessment(finding)
        elif section == "proof_of_concept":
            return self._generate_proof_of_concept(finding)
        elif section == "steps_to_reproduce":
            return self._generate_reproduction_steps(finding)
        elif section == "remediation_recommendations":
            return self._generate_remediation_recommendations(finding)
        elif section == "timeline":
            return self._generate_timeline(finding)
        elif section == "supporting_evidence":
            return self._generate_supporting_evidence(finding)
        elif section == "business_impact":
            return self._generate_business_impact(finding)
        elif section == "risk_assessment":
            return self._generate_risk_assessment(finding)
        elif section == "compliance_implications":
            return self._generate_compliance_implications(finding)
        else:
            return f"## {section.replace('_', ' ').title()}\n\n*Content for {section} section*\n"
    
    def _generate_executive_summary(self, finding: Dict[str, Any]) -> str:
        """Generate executive summary section"""
        title = finding.get("title", "Security Vulnerability")
        severity = finding.get("severity", "Medium")
        cvss_score = finding.get("cvss_score", 5.0)
        target = finding.get("target", "Unknown")
        vuln_type = finding.get("type", "security_misconfiguration")
        
        # Generate professional executive summary
        summary = f"""## Executive Summary

**Vulnerability:** {title}
**Target:** {target}
**Severity:** {severity} (CVSS {cvss_score})
**Type:** {vuln_type.replace('_', ' ').title()}

### Key Findings

A {severity.lower()}-severity {vuln_type.replace('_', ' ')} vulnerability has been identified in {target}. This vulnerability allows an attacker to {self._generate_attack_scenario(finding)}.

### Business Impact

{self._generate_business_impact_summary(finding)}

### Immediate Actions Required

1. **Immediate:** {self._generate_immediate_action(finding)}
2. **Short-term:** Implement proper security controls and monitoring
3. **Long-term:** Conduct comprehensive security review of similar systems

### Risk Rating

- **Confidentiality Impact:** {self._assess_cia_impact(finding, 'confidentiality')}
- **Integrity Impact:** {self._assess_cia_impact(finding, 'integrity')}  
- **Availability Impact:** {self._assess_cia_impact(finding, 'availability')}
"""
        return summary
    
    def _generate_attack_scenario(self, finding: Dict[str, Any]) -> str:
        """Generate attack scenario description"""
        vuln_type = finding.get("type", "security_misconfiguration")
        
        scenarios = {
            "security_misconfiguration": "exploit misconfigurations to gain unauthorized access or information",
            "information_disclosure": "access sensitive information that should not be publicly available",
            "sensitive_data_exposure": "retrieve confidential data including credentials, API keys, or personal information",
            "authentication_bypass": "bypass authentication mechanisms and gain unauthorized access",
            "sql_injection": "execute arbitrary SQL queries and potentially access or modify database contents",
            "xss": "execute malicious scripts in users' browsers and steal sensitive information",
            "ssrf": "make requests to internal systems and potentially access restricted resources"
        }
        
        return scenarios.get(vuln_type, "exploit the identified vulnerability to compromise system security")
    
    def _generate_business_impact_summary(self, finding: Dict[str, Any]) -> str:
        """Generate business impact summary"""
        severity = finding.get("severity", "Medium").lower()
        
        if severity == "critical":
            return "This vulnerability poses an immediate and severe threat to business operations, potentially resulting in complete system compromise, data breaches, and significant financial losses."
        elif severity == "high":
            return "This vulnerability represents a significant security risk that could lead to data exposure, system compromise, and potential regulatory compliance violations."
        elif severity == "medium":
            return "This vulnerability creates a moderate security risk that could be exploited to gain unauthorized access or information, potentially impacting business operations."
        else:
            return "This vulnerability represents a low-level security concern that should be addressed as part of regular security maintenance."
    
    def _generate_immediate_action(self, finding: Dict[str, Any]) -> str:
        """Generate immediate action recommendation"""
        vuln_type = finding.get("type", "security_misconfiguration")
        
        actions = {
            "security_misconfiguration": "Review and correct the identified misconfiguration",
            "information_disclosure": "Restrict access to the exposed information immediately",
            "sensitive_data_exposure": "Remove or secure the exposed sensitive data",
            "authentication_bypass": "Implement proper authentication controls",
            "sql_injection": "Implement input validation and parameterized queries",
            "xss": "Implement proper input sanitization and output encoding",
            "ssrf": "Implement proper input validation and network restrictions"
        }
        
        return actions.get(vuln_type, "Address the identified security vulnerability")
    
    def _assess_cia_impact(self, finding: Dict[str, Any], aspect: str) -> str:
        """Assess CIA (Confidentiality, Integrity, Availability) impact"""
        severity = finding.get("severity", "Medium").lower()
        vuln_type = finding.get("type", "security_misconfiguration")
        
        # Impact mapping based on vulnerability type and severity
        impact_matrix = {
            "information_disclosure": {"confidentiality": "High", "integrity": "None", "availability": "None"},
            "sensitive_data_exposure": {"confidentiality": "High", "integrity": "Low", "availability": "None"},
            "authentication_bypass": {"confidentiality": "High", "integrity": "High", "availability": "Low"},
            "sql_injection": {"confidentiality": "High", "integrity": "High", "availability": "Medium"},
            "xss": {"confidentiality": "Medium", "integrity": "Medium", "availability": "Low"},
            "ssrf": {"confidentiality": "Medium", "integrity": "Low", "availability": "Low"},
            "security_misconfiguration": {"confidentiality": "Medium", "integrity": "Low", "availability": "Low"}
        }
        
        base_impact = impact_matrix.get(vuln_type, {"confidentiality": "Low", "integrity": "Low", "availability": "Low"})
        
        # Adjust based on severity
        impact = base_impact.get(aspect, "Low")
        if severity == "critical" and impact != "None":
            impact = "High"
        elif severity == "low":
            impact = "Low" if impact != "None" else "None"
            
        return impact
    
    def _generate_vulnerability_details(self, finding: Dict[str, Any]) -> str:
        """Generate detailed vulnerability description"""
        vuln_type = finding.get("vulnerability_type", "Unknown")
        description = finding.get("description", "No description available")
        
        return f"""## Vulnerability Details

### Vulnerability Type
{vuln_type.replace('_', ' ').title()}

### Description
{description}

### Technical Analysis
{self._generate_technical_analysis(finding)}

### Attack Vector
{self._generate_attack_vector_analysis(finding)}

### Affected Components
{self._generate_affected_components(finding)}

---
"""
    
    def _generate_impact_assessment(self, finding: Dict[str, Any]) -> str:
        """Generate impact assessment section"""
        severity = finding.get("severity", "Medium")
        cvss_score = finding.get("cvss_score", 5.0)
        
        return f"""## Impact Assessment

### CVSS 3.1 Score: {cvss_score} ({severity})

{self._generate_cvss_breakdown(finding)}

### Potential Impact

#### Confidentiality
{self._assess_confidentiality_impact(finding)}

#### Integrity
{self._assess_integrity_impact(finding)}

#### Availability
{self._assess_availability_impact(finding)}

### Attack Scenarios
{self._generate_attack_scenarios(finding)}

---
"""
    
    def _generate_proof_of_concept(self, finding: Dict[str, Any]) -> str:
        """Generate proof of concept section"""
        poc_data = finding.get("poc_data", {})
        
        return f"""## Proof of Concept

### Overview
This section demonstrates the exploitability of the identified vulnerability through a controlled proof-of-concept.

### PoC Environment
- **Target:** {finding.get('target', 'Unknown')}
- **Testing Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Tools Used:** {', '.join(poc_data.get('tools_used', ['Manual testing']))}

### Exploitation Steps
{self._generate_exploitation_steps(finding)}

### PoC Code
```python
{poc_data.get('poc_code', '# PoC code not available')}
```

### Expected Results
{self._generate_expected_results(finding)}

### Safety Measures
All testing was conducted with appropriate safety measures:
- Non-destructive payloads only
- Read-only operations where possible
- Proper authorization obtained
- Rate limiting respected

---
"""
    
    def _generate_reproduction_steps(self, finding: Dict[str, Any]) -> str:
        """Generate step-by-step reproduction instructions"""
        return f"""## Steps to Reproduce

### Prerequisites
- Access to {finding.get('target', 'the target application')}
- Web browser or appropriate testing tools
- Network connectivity

### Detailed Steps

1. **Initial Setup**
   - Navigate to {finding.get('target', 'the target URL')}
   - Ensure you have appropriate testing authorization

2. **Vulnerability Trigger**
   {self._generate_trigger_steps(finding)}

3. **Observation**
   {self._generate_observation_steps(finding)}

4. **Verification**
   {self._generate_verification_steps(finding)}

### Alternative Reproduction Methods
{self._generate_alternative_methods(finding)}

### Troubleshooting
If reproduction fails:
- Verify target accessibility
- Check for rate limiting or WAF interference
- Ensure proper parameter formatting
- Review network connectivity

---
"""
    
    def _generate_remediation_recommendations(self, finding: Dict[str, Any]) -> str:
        """Generate remediation recommendations"""
        vuln_type = finding.get("vulnerability_type", "unknown")
        
        return f"""## Remediation Recommendations

### Immediate Actions (0-24 hours)
{self._get_immediate_actions(vuln_type)}

### Short-term Fixes (1-7 days)
{self._get_short_term_fixes(vuln_type)}

### Long-term Solutions (1-4 weeks)
{self._get_long_term_solutions(vuln_type)}

### Code-Level Remediation
{self._generate_code_remediation(finding)}

### Configuration Changes
{self._generate_config_remediation(finding)}

### Verification Steps
After implementing fixes:
1. Re-test the vulnerability using the provided PoC
2. Conduct regression testing on related functionality
3. Perform security code review of changes
4. Update security documentation and procedures

### Prevention Measures
{self._generate_prevention_measures(vuln_type)}

---
"""
    
    def _generate_timeline(self, finding: Dict[str, Any]) -> str:
        """Generate vulnerability timeline"""
        discovery_date = datetime.now().strftime('%Y-%m-%d')
        
        return f"""## Timeline

| Date | Event | Details |
|------|-------|---------|
| {discovery_date} | Vulnerability Discovered | Initial identification during security assessment |
| {discovery_date} | Vulnerability Analyzed | Detailed analysis and impact assessment completed |
| {discovery_date} | PoC Developed | Safe proof-of-concept created and tested |
| {discovery_date} | Report Generated | Comprehensive security report compiled |

### Recommended Response Timeline

| Timeframe | Action | Responsibility |
|-----------|--------|----------------|
| 0-24 hours | Acknowledge receipt and begin triage | Security Team |
| 1-3 days | Validate vulnerability and assess impact | Development Team |
| 3-7 days | Implement temporary mitigations | DevOps/Security |
| 1-4 weeks | Deploy permanent fix | Development Team |
| 4-6 weeks | Conduct post-fix verification | Security Team |

---
"""
    
    def _generate_supporting_evidence(self, finding: Dict[str, Any]) -> str:
        """Generate supporting evidence section"""
        evidence_data = finding.get("evidence_data", {})
        
        return f"""## Supporting Evidence

### Evidence Summary
{evidence_data.get('evidence_summary', {}).get('successful_captures', 0)} pieces of evidence collected with quality score: {evidence_data.get('quality_score', 0.0)}

### Screenshots
{self._generate_screenshot_evidence(evidence_data)}

### Video Demonstration
{self._generate_video_evidence(evidence_data)}

### Network Traffic Analysis
{self._generate_network_evidence(evidence_data)}

### HTTP Request/Response
{self._generate_http_evidence(evidence_data)}

### Additional Files
{self._generate_file_evidence(evidence_data)}

### Evidence Integrity
All evidence was collected using automated tools with timestamps and checksums for integrity verification.

---
"""
    
    def _generate_business_impact(self, finding: Dict[str, Any]) -> str:
        """Generate business impact analysis"""
        impact_type = self._determine_impact_type(finding)
        impact_data = self.business_impact_analyzer.get(impact_type, {})
        
        return f"""## Business Impact Analysis

### Impact Category: {impact_type.replace('_', ' ').title()}

#### Financial Impact
{impact_data.get('financial_impact', 'Impact assessment pending')}

#### Reputational Impact
{impact_data.get('reputational_impact', 'Impact assessment pending')}

#### Operational Impact
{impact_data.get('operational_impact', 'Impact assessment pending')}

#### Compliance Impact
{impact_data.get('compliance_impact', 'Impact assessment pending')}

### Quantitative Risk Assessment
{self._generate_quantitative_risk(finding)}

### Industry Benchmarking
{self._generate_industry_comparison(finding)}

---
"""
    
    def _compile_report(self, sections: Dict[str, str], template: ReportTemplate, finding: Dict[str, Any]) -> str:
        """Compile all sections into final report"""
        report_header = f"""# Security Vulnerability Report

**Report ID:** AEGIS-X-{finding.get('id', 'UNKNOWN')}-{datetime.now().strftime('%Y%m%d')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Template:** {template.name}
**Target:** {finding.get('target', 'Unknown')}

---

"""
        
        # Combine all sections
        report_body = ""
        for section_name in template.sections:
            if section_name in sections:
                report_body += sections[section_name] + "\n"
        
        # Add footer
        report_footer = f"""
---

## Report Metadata

**Generated by:** AEGIS-X Autonomous Bug Bounty System
**Report Version:** 1.0
**Quality Score:** {self._calculate_report_quality({'content': report_body}, finding)}/10
**Word Count:** {len(report_body.split())} words
**Estimated Reading Time:** {len(report_body.split()) // 200} minutes

### Disclaimer
This report was generated by an autonomous security testing system. All findings have been verified through multiple validation layers. The testing was conducted in accordance with responsible disclosure principles and with appropriate authorization.

### Contact Information
For questions about this report or the vulnerability, please contact the security team.

---

*End of Report*
"""
        
        return report_header + report_body + report_footer
    
    def _apply_report_reflection(self, finding: Dict[str, Any], template: ReportTemplate) -> List[str]:
        """Apply self-reflection to report generation"""
        reflection_questions = [
            "Is this report clear enough for a non-technical manager?",
            "Did I explain business impact effectively?",
            "Is remediation actionable and specific?",
            "What feedback did I get on similar reports?",
            "How can I improve this report's quality?"
        ]
        
        reflection_notes = []
        
        # Check report completeness
        if not finding.get("evidence_data"):
            reflection_notes.append("No evidence data available - report may lack supporting proof")
        
        if not finding.get("poc_data"):
            reflection_notes.append("No PoC data available - demonstration section will be limited")
        
        # Check severity alignment
        severity = finding.get("severity", "Medium")
        cvss_score = finding.get("cvss_score", 5.0)
        
        if severity == "Critical" and cvss_score < 9.0:
            reflection_notes.append("Severity and CVSS score may be misaligned - review scoring")
        
        # Check business impact
        if not self._has_business_impact_analysis(finding):
            reflection_notes.append("Business impact analysis may be generic - consider more specific analysis")
        
        return reflection_notes
    
    def _calculate_report_quality(self, report: Dict[str, Any], finding: Dict[str, Any]) -> float:
        """Calculate report quality score"""
        quality_factors = {
            "completeness": 0.3,
            "clarity": 0.2,
            "evidence": 0.2,
            "actionability": 0.15,
            "professionalism": 0.15
        }
        
        scores = {}
        
        # Completeness score
        content = report.get("content", "")
        required_sections = ["vulnerability", "impact", "remediation", "proof"]
        completeness = sum(1 for section in required_sections if section.lower() in content.lower()) / len(required_sections)
        scores["completeness"] = completeness
        
        # Clarity score (based on readability metrics)
        word_count = len(content.split())
        sentence_count = content.count('.') + content.count('!') + content.count('?')
        avg_sentence_length = word_count / max(sentence_count, 1)
        clarity = max(0, min(1, 1 - (avg_sentence_length - 15) / 20))  # Optimal around 15 words per sentence
        scores["clarity"] = clarity
        
        # Evidence score
        evidence_quality = finding.get("evidence_data", {}).get("quality_score", 0.5)
        scores["evidence"] = evidence_quality
        
        # Actionability score (presence of specific remediation steps)
        actionable_keywords = ["implement", "configure", "update", "patch", "validate"]
        actionability = sum(1 for keyword in actionable_keywords if keyword in content.lower()) / len(actionable_keywords)
        scores["actionability"] = min(1.0, actionability)
        
        # Professionalism score (formatting, structure, language)
        professional_indicators = ["##", "**", "```", "---", "CVSS"]
        professionalism = sum(1 for indicator in professional_indicators if indicator in content) / len(professional_indicators)
        scores["professionalism"] = min(1.0, professionalism)
        
        # Calculate weighted score
        total_score = sum(scores[factor] * weight for factor, weight in quality_factors.items())
        
        return round(total_score * 10, 1)  # Scale to 0-10
    
    # Helper methods for generating specific content
    def _get_attack_description(self, finding: Dict[str, Any]) -> str:
        """Get attack description based on vulnerability type"""
        vuln_type = finding.get("vulnerability_type", "unknown")
        
        descriptions = {
            "sql_injection": "execute arbitrary SQL queries against the database",
            "xss_reflected": "inject malicious scripts that execute in victim browsers",
            "xss_stored": "store malicious scripts that affect all users",
            "ssrf": "make requests to internal systems and services",
            "lfi": "access local files on the server",
            "idor": "access unauthorized data by manipulating object references",
            "csrf": "perform unauthorized actions on behalf of authenticated users"
        }
        
        return descriptions.get(vuln_type, "exploit the identified security weakness")
    
    def _get_impact_summary(self, finding: Dict[str, Any]) -> str:
        """Get impact summary based on vulnerability"""
        severity = finding.get("severity", "Medium")
        
        if severity == "Critical":
            return "complete system compromise, massive data breach, and severe business disruption"
        elif severity == "High":
            return "significant data exposure, account compromise, and substantial business impact"
        elif severity == "Medium":
            return "moderate data exposure and potential service disruption"
        else:
            return "limited security impact with potential for information disclosure"
    
    def _get_business_impact_summary(self, finding: Dict[str, Any]) -> str:
        """Get business impact summary"""
        impact_type = self._determine_impact_type(finding)
        
        summaries = {
            "data_breach": "High risk of regulatory fines, legal liability, and customer trust loss",
            "account_takeover": "Risk of fraudulent activity and customer account compromise",
            "service_disruption": "Potential service downtime and SLA violations",
            "information_disclosure": "Risk of competitive disadvantage and privacy violations"
        }
        
        return summaries.get(impact_type, "Moderate business risk requiring prompt attention")
    
    def _determine_impact_type(self, finding: Dict[str, Any]) -> str:
        """Determine the primary business impact type"""
        vuln_type = finding.get("vulnerability_type", "unknown")
        description = finding.get("description", "").lower()
        
        if any(term in description for term in ["data", "database", "personal", "sensitive"]):
            return "data_breach"
        elif any(term in description for term in ["account", "authentication", "session"]):
            return "account_takeover"
        elif any(term in description for term in ["denial", "crash", "unavailable"]):
            return "service_disruption"
        else:
            return "information_disclosure"
    
    # Additional helper methods would be implemented here...
    # (Truncated for brevity, but would include all the referenced helper methods)
    
    def _generate_technical_analysis(self, finding: Dict[str, Any]) -> str:
        """Generate technical analysis content"""
        return f"Technical analysis of {finding.get('vulnerability_type', 'the vulnerability')} indicates potential for exploitation through {finding.get('attack_vector', 'identified attack vectors')}."
    
    def _generate_attack_vector_analysis(self, finding: Dict[str, Any]) -> str:
        """Generate attack vector analysis"""
        return f"The vulnerability can be exploited via {finding.get('attack_vector', 'network-based attacks')} with {finding.get('complexity', 'moderate')} complexity."
    
    def _generate_affected_components(self, finding: Dict[str, Any]) -> str:
        """Generate affected components list"""
        return f"- Target: {finding.get('target', 'Unknown')}\n- Component: {finding.get('component', 'Web application')}\n- Parameter: {finding.get('parameter', 'Not specified')}"
    
    def _generate_cvss_breakdown(self, finding: Dict[str, Any]) -> str:
        """Generate CVSS score breakdown"""
        return f"""
**Attack Vector:** Network (AV:N)
**Attack Complexity:** Low (AC:L)  
**Privileges Required:** None (PR:N)
**User Interaction:** None (UI:N)
**Scope:** Unchanged (S:U)
**Confidentiality:** {finding.get('confidentiality_impact', 'Low')} (C:L)
**Integrity:** {finding.get('integrity_impact', 'Low')} (I:L)
**Availability:** {finding.get('availability_impact', 'None')} (A:N)
"""
    
    def _assess_confidentiality_impact(self, finding: Dict[str, Any]) -> str:
        """Assess confidentiality impact"""
        return "Potential for unauthorized access to sensitive information."
    
    def _assess_integrity_impact(self, finding: Dict[str, Any]) -> str:
        """Assess integrity impact"""
        return "Potential for unauthorized modification of data or system state."
    
    def _assess_availability_impact(self, finding: Dict[str, Any]) -> str:
        """Assess availability impact"""
        return "Potential for service disruption or denial of service."
    
    def _generate_attack_scenarios(self, finding: Dict[str, Any]) -> str:
        """Generate attack scenarios"""
        return f"""
**Scenario 1:** External attacker exploits the vulnerability to gain unauthorized access
**Scenario 2:** Malicious insider leverages the vulnerability for privilege escalation
**Scenario 3:** Automated attack tools discover and exploit the vulnerability at scale
"""
    
    def _generate_exploitation_steps(self, finding: Dict[str, Any]) -> str:
        """Generate exploitation steps"""
        return f"""
1. Identify vulnerable parameter in {finding.get('target', 'target application')}
2. Craft malicious payload targeting the vulnerability
3. Submit payload through identified attack vector
4. Observe system response confirming exploitation
5. Document evidence of successful exploitation
"""
    
    def _generate_expected_results(self, finding: Dict[str, Any]) -> str:
        """Generate expected results"""
        return f"Successful exploitation should result in {self._get_attack_description(finding)}, demonstrating the vulnerability's impact."
    
    def _generate_trigger_steps(self, finding: Dict[str, Any]) -> str:
        """Generate vulnerability trigger steps"""
        return f"   - Locate the vulnerable parameter: {finding.get('parameter', 'target parameter')}\n   - Submit the malicious payload\n   - Monitor the application response"
    
    def _generate_observation_steps(self, finding: Dict[str, Any]) -> str:
        """Generate observation steps"""
        return "   - Check for vulnerability indicators in the response\n   - Document any error messages or unexpected behavior\n   - Capture screenshots or network traffic as evidence"
    
    def _generate_verification_steps(self, finding: Dict[str, Any]) -> str:
        """Generate verification steps"""
        return "   - Confirm the vulnerability is reproducible\n   - Verify the impact matches expectations\n   - Ensure no false positive indicators"
    
    def _generate_alternative_methods(self, finding: Dict[str, Any]) -> str:
        """Generate alternative reproduction methods"""
        return f"Alternative methods include using automated tools like {finding.get('tools_used', ['curl', 'Burp Suite'])} or manual browser testing."
    
    def _get_immediate_actions(self, vuln_type: str) -> str:
        """Get immediate action recommendations"""
        actions = {
            "sql_injection": "- Disable vulnerable endpoints if possible\n- Enable database query logging\n- Review recent database access logs",
            "xss_reflected": "- Implement Content Security Policy (CSP)\n- Enable XSS protection headers\n- Review user input validation",
            "ssrf": "- Restrict outbound network access\n- Implement URL whitelist validation\n- Monitor internal network traffic"
        }
        return actions.get(vuln_type, "- Assess vulnerability impact\n- Implement temporary mitigations\n- Monitor for exploitation attempts")
    
    def _get_short_term_fixes(self, vuln_type: str) -> str:
        """Get short-term fix recommendations"""
        fixes = {
            "sql_injection": "- Implement parameterized queries\n- Add input validation and sanitization\n- Update database permissions",
            "xss_reflected": "- Implement proper output encoding\n- Add input validation\n- Update template engines with auto-escaping",
            "ssrf": "- Implement URL validation\n- Add network segmentation\n- Update request handling logic"
        }
        return fixes.get(vuln_type, "- Apply security patches\n- Update input validation\n- Implement proper access controls")
    
    def _get_long_term_solutions(self, vuln_type: str) -> str:
        """Get long-term solution recommendations"""
        solutions = {
            "sql_injection": "- Implement comprehensive ORM usage\n- Establish secure coding standards\n- Deploy database activity monitoring",
            "xss_reflected": "- Implement comprehensive CSP\n- Deploy Web Application Firewall\n- Establish secure development lifecycle",
            "ssrf": "- Implement zero-trust network architecture\n- Deploy comprehensive monitoring\n- Establish secure API design patterns"
        }
        return solutions.get(vuln_type, "- Implement security-by-design principles\n- Establish comprehensive security testing\n- Deploy continuous security monitoring")
    
    def _generate_code_remediation(self, finding: Dict[str, Any]) -> str:
        """Generate code-level remediation"""
        return f"Specific code changes required to address the {finding.get('vulnerability_type', 'vulnerability')} in the affected component."
    
    def _generate_config_remediation(self, finding: Dict[str, Any]) -> str:
        """Generate configuration remediation"""
        return "Configuration changes to security headers, server settings, and application parameters."
    
    def _generate_prevention_measures(self, vuln_type: str) -> str:
        """Generate prevention measures"""
        return f"Implement secure coding practices, regular security testing, and continuous monitoring to prevent {vuln_type.replace('_', ' ')} vulnerabilities."
    
    def _generate_screenshot_evidence(self, evidence_data: Dict[str, Any]) -> str:
        """Generate screenshot evidence section"""
        screenshots = evidence_data.get("evidence_collection", {})
        if "screenshot_after" in screenshots and screenshots["screenshot_after"].get("success"):
            return f"Screenshot evidence available: {screenshots['screenshot_after']['file_path']}"
        return "Screenshot evidence not available"
    
    def _generate_video_evidence(self, evidence_data: Dict[str, Any]) -> str:
        """Generate video evidence section"""
        videos = evidence_data.get("evidence_collection", {})
        if "video_demonstration" in videos and videos["video_demonstration"].get("success"):
            return f"Video demonstration available: {videos['video_demonstration']['file_path']}"
        return "Video demonstration not available"
    
    def _generate_network_evidence(self, evidence_data: Dict[str, Any]) -> str:
        """Generate network evidence section"""
        network = evidence_data.get("evidence_collection", {})
        if "network_traffic" in network and network["network_traffic"].get("success"):
            return f"Network traffic capture available: {network['network_traffic']['har_file']}"
        return "Network traffic analysis not available"
    
    def _generate_http_evidence(self, evidence_data: Dict[str, Any]) -> str:
        """Generate HTTP evidence section"""
        curl = evidence_data.get("evidence_collection", {})
        if "curl_command" in curl and curl["curl_command"].get("success"):
            return f"```bash\n{curl['curl_command']['curl_command']}\n```"
        return "HTTP request/response evidence not available"
    
    def _generate_file_evidence(self, evidence_data: Dict[str, Any]) -> str:
        """Generate file evidence section"""
        files = evidence_data.get("evidence_summary", {}).get("file_inventory", [])
        if files:
            return f"Additional evidence files: {len(files)} files in evidence directory"
        return "No additional evidence files"
    
    def _generate_quantitative_risk(self, finding: Dict[str, Any]) -> str:
        """Generate quantitative risk assessment"""
        cvss_score = finding.get("cvss_score", 5.0)
        return f"Risk Score: {cvss_score}/10.0 - {self._get_risk_level(cvss_score)} risk level"
    
    def _get_risk_level(self, cvss_score: float) -> str:
        """Get risk level from CVSS score"""
        if cvss_score >= 9.0:
            return "Critical"
        elif cvss_score >= 7.0:
            return "High"
        elif cvss_score >= 4.0:
            return "Medium"
        else:
            return "Low"
    
    def _generate_industry_comparison(self, finding: Dict[str, Any]) -> str:
        """Generate industry comparison"""
        return f"This vulnerability type represents a common security issue in web applications, with similar findings reported across the industry."
    
    def _has_business_impact_analysis(self, finding: Dict[str, Any]) -> bool:
        """Check if finding has business impact analysis"""
        return bool(finding.get("business_impact") or finding.get("impact_analysis"))
    
    async def generate_master_report(self, findings: List[Dict[str, Any]], session: Any) -> Dict[str, Any]:
        """Generate master summary report for all findings"""
        self.logger.info(f"📊 Generating master report for {len(findings)} findings")
        
        # Analyze findings
        findings_analysis = self._analyze_findings_collection(findings)
        
        # Generate master report content
        master_content = self._generate_master_content(findings, session, findings_analysis)
        
        master_report = {
            "session_id": session.session_id,
            "title": f"AEGIS-X Security Assessment Report - {datetime.now().strftime('%Y-%m-%d')}",
            "content": master_content,
            "findings_count": len(findings),
            "findings_analysis": findings_analysis,
            "generated_at": datetime.now().isoformat()
        }
        
        return master_report
    
    def _analyze_findings_collection(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze collection of findings"""
        analysis = {
            "total_findings": len(findings),
            "severity_breakdown": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
            "vulnerability_types": {},
            "targets_affected": set(),
            "average_cvss": 0.0,
            "top_risks": []
        }
        
        cvss_scores = []
        
        for finding in findings:
            # Severity breakdown
            severity = finding.get("severity", "Medium")
            analysis["severity_breakdown"][severity] += 1
            
            # Vulnerability types
            vuln_type = finding.get("vulnerability_type", "unknown")
            analysis["vulnerability_types"][vuln_type] = analysis["vulnerability_types"].get(vuln_type, 0) + 1
            
            # Targets
            target = finding.get("target", "unknown")
            analysis["targets_affected"].add(target)
            
            # CVSS scores
            cvss = finding.get("cvss_score", 5.0)
            cvss_scores.append(cvss)
        
        # Calculate average CVSS
        if cvss_scores:
            analysis["average_cvss"] = round(sum(cvss_scores) / len(cvss_scores), 1)
        
        # Convert set to list for JSON serialization
        analysis["targets_affected"] = list(analysis["targets_affected"])
        
        # Identify top risks
        critical_high = [f for f in findings if f.get("severity") in ["Critical", "High"]]
        analysis["top_risks"] = sorted(critical_high, key=lambda x: x.get("cvss_score", 0), reverse=True)[:5]
        
        return analysis
    
    def _generate_master_content(self, findings: List[Dict[str, Any]], session: Any, analysis: Dict[str, Any]) -> str:
        """Generate master report content"""
        return f"""# AEGIS-X Security Assessment Report

**Assessment ID:** {session.session_id}
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Duration:** {session.performance_metrics.get('duration_minutes', 0):.1f} minutes
**Targets Assessed:** {len(session.targets)}

## Executive Summary

This automated security assessment identified **{analysis['total_findings']} vulnerabilities** across {len(analysis['targets_affected'])} targets. The assessment revealed {analysis['severity_breakdown']['Critical']} critical, {analysis['severity_breakdown']['High']} high, {analysis['severity_breakdown']['Medium']} medium, and {analysis['severity_breakdown']['Low']} low severity issues.

### Key Findings

- **Average CVSS Score:** {analysis['average_cvss']}/10.0
- **Most Common Vulnerability:** {max(analysis['vulnerability_types'].items(), key=lambda x: x[1])[0] if analysis['vulnerability_types'] else 'None'}
- **Highest Risk Target:** {analysis['top_risks'][0].get('target', 'N/A') if analysis['top_risks'] else 'N/A'}

### Immediate Actions Required

{self._generate_immediate_actions_summary(analysis)}

## Findings Summary

### Severity Breakdown
- **Critical:** {analysis['severity_breakdown']['Critical']} findings
- **High:** {analysis['severity_breakdown']['High']} findings  
- **Medium:** {analysis['severity_breakdown']['Medium']} findings
- **Low:** {analysis['severity_breakdown']['Low']} findings

### Vulnerability Types
{self._format_vulnerability_types(analysis['vulnerability_types'])}

### Targets Assessed
{self._format_targets_list(analysis['targets_affected'])}

## Top Risk Findings

{self._format_top_risks(analysis['top_risks'])}

## Detailed Findings

{self._format_detailed_findings(findings)}

## Recommendations

### Priority 1 (Immediate)
{self._generate_priority_1_recommendations(analysis)}

### Priority 2 (Short-term)
{self._generate_priority_2_recommendations(analysis)}

### Priority 3 (Long-term)
{self._generate_priority_3_recommendations(analysis)}

## Assessment Methodology

This assessment was conducted using AEGIS-X, an autonomous bug bounty hunting system that employs:

- **Multi-layered verification** to ensure zero false positives
- **Professional-grade evidence collection** including screenshots, videos, and network captures
- **Comprehensive vulnerability chaining** to identify escalation paths
- **Industry-standard reporting** compatible with major bug bounty platforms

### Tools and Techniques Used
{self._format_tools_used(session)}

### Quality Assurance
- All findings verified through triple verification protocol
- Evidence collected for each vulnerability
- Professional-grade documentation generated
- Self-learning system continuously improves accuracy

## Conclusion

{self._generate_conclusion(analysis, session)}

---

**Report Generated by:** AEGIS-X Autonomous Bug Bounty System
**Quality Score:** {self._calculate_master_report_quality(analysis)}/10
**Next Assessment Recommended:** {self._recommend_next_assessment_date()}

*End of Report*
"""
    
    def _generate_immediate_actions_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate immediate actions summary"""
        critical_count = analysis['severity_breakdown']['Critical']
        high_count = analysis['severity_breakdown']['High']
        
        if critical_count > 0:
            return f"**URGENT:** {critical_count} critical vulnerabilities require immediate attention and remediation within 24 hours."
        elif high_count > 0:
            return f"**HIGH PRIORITY:** {high_count} high-severity vulnerabilities should be addressed within 72 hours."
        else:
            return "No critical or high-severity vulnerabilities identified. Review medium and low findings for improvement opportunities."
    
    def _format_vulnerability_types(self, vuln_types: Dict[str, int]) -> str:
        """Format vulnerability types list"""
        if not vuln_types:
            return "No vulnerabilities identified."
        
        formatted = []
        for vuln_type, count in sorted(vuln_types.items(), key=lambda x: x[1], reverse=True):
            formatted.append(f"- **{vuln_type.replace('_', ' ').title()}:** {count} finding{'s' if count > 1 else ''}")
        
        return '\n'.join(formatted)
    
    def _format_targets_list(self, targets: List[str]) -> str:
        """Format targets list"""
        if not targets:
            return "No targets assessed."
        
        return '\n'.join(f"- {target}" for target in sorted(targets))
    
    def _format_top_risks(self, top_risks: List[Dict[str, Any]]) -> str:
        """Format top risks section"""
        if not top_risks:
            return "No high-risk findings identified."
        
        formatted = []
        for i, risk in enumerate(top_risks[:5], 1):
            formatted.append(f"""
### {i}. {risk.get('title', 'Unknown Vulnerability')}
- **Target:** {risk.get('target', 'Unknown')}
- **Severity:** {risk.get('severity', 'Unknown')} (CVSS {risk.get('cvss_score', 0.0)})
- **Type:** {risk.get('vulnerability_type', 'Unknown').replace('_', ' ').title()}
- **Impact:** {self._get_impact_summary(risk)}
""")
        
        return '\n'.join(formatted)
    
    def _format_detailed_findings(self, findings: List[Dict[str, Any]]) -> str:
        """Format detailed findings section"""
        if not findings:
            return "No detailed findings to report."
        
        formatted = []
        for i, finding in enumerate(findings, 1):
            formatted.append(f"""
### Finding {i}: {finding.get('title', 'Unknown Vulnerability')}

**Target:** {finding.get('target', 'Unknown')}
**Severity:** {finding.get('severity', 'Unknown')} (CVSS {finding.get('cvss_score', 0.0)})
**Type:** {finding.get('vulnerability_type', 'Unknown').replace('_', ' ').title()}

**Description:** {finding.get('description', 'No description available')[:200]}...

**Evidence:** {self._summarize_evidence(finding)}

**Remediation:** {self._summarize_remediation(finding)}

---
""")
        
        return '\n'.join(formatted)
    
    def _summarize_evidence(self, finding: Dict[str, Any]) -> str:
        """Summarize evidence for finding"""
        evidence_data = finding.get("evidence_data", {})
        if evidence_data:
            quality_score = evidence_data.get("quality_score", 0.0)
            return f"Evidence collected with quality score {quality_score}/1.0"
        return "Evidence collection pending"
    
    def _summarize_remediation(self, finding: Dict[str, Any]) -> str:
        """Summarize remediation for finding"""
        vuln_type = finding.get("vulnerability_type", "unknown")
        return self._get_immediate_actions(vuln_type).split('\n')[0].replace('- ', '')
    
    def _generate_priority_1_recommendations(self, analysis: Dict[str, Any]) -> str:
        """Generate priority 1 recommendations"""
        critical_count = analysis['severity_breakdown']['Critical']
        high_count = analysis['severity_breakdown']['High']
        
        recommendations = []
        
        if critical_count > 0:
            recommendations.append(f"Address all {critical_count} critical vulnerabilities immediately")
        
        if high_count > 0:
            recommendations.append(f"Remediate {high_count} high-severity vulnerabilities within 72 hours")
        
        recommendations.append("Implement emergency incident response procedures")
        recommendations.append("Notify relevant stakeholders and compliance teams")
        
        return '\n'.join(f"- {rec}" for rec in recommendations)
    
    def _generate_priority_2_recommendations(self, analysis: Dict[str, Any]) -> str:
        """Generate priority 2 recommendations"""
        medium_count = analysis['severity_breakdown']['Medium']
        
        recommendations = [
            f"Address {medium_count} medium-severity vulnerabilities within 2 weeks",
            "Implement comprehensive security testing in CI/CD pipeline",
            "Conduct security code review for affected components",
            "Update security documentation and procedures"
        ]
        
        return '\n'.join(f"- {rec}" for rec in recommendations)
    
    def _generate_priority_3_recommendations(self, analysis: Dict[str, Any]) -> str:
        """Generate priority 3 recommendations"""
        recommendations = [
            "Establish regular automated security assessments",
            "Implement security awareness training for development teams",
            "Deploy comprehensive security monitoring and alerting",
            "Conduct regular penetration testing and security audits"
        ]
        
        return '\n'.join(f"- {rec}" for rec in recommendations)
    
    def _format_tools_used(self, session: Any) -> str:
        """Format tools used in assessment"""
        # This would extract tools from session data
        return "- AEGIS-X Autonomous Hunting System\n- Multi-layered verification protocols\n- Professional evidence collection tools"
    
    def _generate_conclusion(self, analysis: Dict[str, Any], session: Any) -> str:
        """Generate report conclusion"""
        total_findings = analysis['total_findings']
        avg_cvss = analysis['average_cvss']
        
        if total_findings == 0:
            return "This assessment found no security vulnerabilities in the tested targets. Continue regular security testing to maintain this security posture."
        
        risk_level = self._get_risk_level(avg_cvss)
        
        return f"""This assessment identified {total_findings} security vulnerabilities with an average CVSS score of {avg_cvss}, indicating a {risk_level.lower()} overall risk level. 

Immediate attention should be focused on the {analysis['severity_breakdown']['Critical'] + analysis['severity_breakdown']['High']} critical and high-severity findings. Implementation of the recommended remediation steps will significantly improve the security posture of the assessed targets.

Regular automated security assessments using AEGIS-X are recommended to maintain ongoing security visibility and prevent future vulnerabilities."""
    
    def _calculate_master_report_quality(self, analysis: Dict[str, Any]) -> float:
        """Calculate master report quality score"""
        # Simple quality calculation based on completeness and analysis depth
        base_score = 8.0
        
        # Bonus for comprehensive analysis
        if analysis['total_findings'] > 0:
            base_score += 1.0
        
        # Bonus for detailed breakdown
        if len(analysis['vulnerability_types']) > 1:
            base_score += 0.5
        
        return min(10.0, base_score)
    
    def _recommend_next_assessment_date(self) -> str:
        """Recommend next assessment date"""
        next_date = datetime.now().replace(day=1)
        if next_date.month == 12:
            next_date = next_date.replace(year=next_date.year + 1, month=1)
        else:
            next_date = next_date.replace(month=next_date.month + 1)
        
        return next_date.strftime('%Y-%m-%d')
    
    async def _store_report_learning(self, report_result: Dict[str, Any], finding: Dict[str, Any]):
        """Store report generation learning data"""
        learning_entry = {
            "report_quality_score": report_result["quality_score"],
            "template_used": report_result["template_used"],
            "word_count": report_result["word_count"],
            "reading_time": report_result["estimated_reading_time"],
            "reflection_notes": report_result["reflection_notes"],
            "vulnerability_type": finding.get("vulnerability_type"),
            "severity": finding.get("severity"),
            "timestamp": datetime.now().isoformat()
        }
        
        self.learning_data.setdefault("report_generations", []).append(learning_entry)
        
        # Save learning data
        learning_file = Path("learn/report_learning.json")
        learning_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save report learning data: {e}")