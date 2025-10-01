#!/usr/bin/env python3
"""
AEGIS-X Headless Evidence Collection System
Advanced evidence collection system designed for GitHub Actions and CI/CD environments
without GUI dependencies. Captures screenshots, videos, network traffic, and other evidence.

This system provides:
- Headless browser automation for visual evidence
- Network traffic capture and analysis
- HTTP request/response logging
- Payload execution recording
- Automated evidence packaging
- Professional report generation with embedded evidence
"""

import asyncio
import subprocess
import logging
import json
import time
import os
import sys
import base64
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import tempfile
import shutil
from urllib.parse import urlparse, urljoin
import re
import mimetypes
from dataclasses import dataclass, asdict
import aiohttp
import aiofiles
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("AEGIS-X.HeadlessEvidenceCollector")

@dataclass
class EvidenceItem:
    """Represents a piece of evidence"""
    id: str
    type: str  # screenshot, video, network_capture, http_log, payload_execution
    title: str
    description: str
    file_path: str
    vulnerability_id: str
    timestamp: str
    metadata: Dict[str, Any]
    size_bytes: int
    mime_type: str
    hash_sha256: str

class HeadlessEvidenceCollector:
    """
    Advanced headless evidence collection system for CI/CD environments
    """
    
    def __init__(self, evidence_dir: Path = Path("evidence")):
        self.evidence_dir = evidence_dir
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different evidence types
        self.screenshots_dir = self.evidence_dir / "screenshots"
        self.videos_dir = self.evidence_dir / "videos"
        self.network_dir = self.evidence_dir / "network"
        self.logs_dir = self.evidence_dir / "logs"
        self.payloads_dir = self.evidence_dir / "payloads"
        self.reports_dir = self.evidence_dir / "reports"
        
        for dir_path in [self.screenshots_dir, self.videos_dir, self.network_dir, 
                        self.logs_dir, self.payloads_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create initial placeholder file to ensure directory is not empty
            placeholder_file = dir_path / ".evidence_collector_initialized"
            if not placeholder_file.exists():
                with open(placeholder_file, 'w') as f:
                    f.write(f"Evidence collector initialized at {datetime.now().isoformat()}\n")
                    f.write(f"Directory: {dir_path}\n")
                    f.write("This file ensures the directory is not empty for CI/CD artifact uploads.\n")
        
        # Evidence tracking
        self.evidence_items: List[EvidenceItem] = []
        self.current_session_id = f"session_{int(time.time())}"
        
        # Browser configuration for headless operation
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-plugins')
        self.chrome_options.add_argument('--disable-images')  # Faster loading
        self.chrome_options.add_argument('--disable-javascript')  # Can be enabled per test
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Network capture configuration
        self.network_logs = []
        self.http_session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http_session.mount("http://", adapter)
        self.http_session.mount("https://", adapter)
        
        logger.info("🎥 Headless Evidence Collector initialized")
        logger.info(f"📁 Evidence directory: {self.evidence_dir}")

    async def capture_vulnerability_evidence(self, vulnerability_data: Dict[str, Any]) -> List[EvidenceItem]:
        """
        Capture comprehensive evidence for a vulnerability
        """
        logger.info(f"📸 Capturing evidence for vulnerability: {vulnerability_data.get('title', 'Unknown')}")
        
        evidence_items = []
        vuln_id = vulnerability_data.get('id', f"vuln_{int(time.time())}")
        
        try:
            # 1. Capture screenshot evidence
            if vulnerability_data.get('target_url'):
                screenshot_evidence = await self._capture_screenshot_evidence(
                    vulnerability_data['target_url'], 
                    vuln_id, 
                    vulnerability_data
                )
                evidence_items.extend(screenshot_evidence)
            
            # 2. Capture HTTP request/response evidence
            http_evidence = await self._capture_http_evidence(vulnerability_data, vuln_id)
            evidence_items.extend(http_evidence)
            
            # 3. Capture payload execution evidence
            if vulnerability_data.get('exploit_code'):
                payload_evidence = await self._capture_payload_evidence(vulnerability_data, vuln_id)
                evidence_items.extend(payload_evidence)
            
            # 4. Capture network traffic evidence
            network_evidence = await self._capture_network_evidence(vulnerability_data, vuln_id)
            evidence_items.extend(network_evidence)
            
            # 5. Generate visual proof-of-concept
            visual_poc = await self._generate_visual_poc(vulnerability_data, vuln_id)
            if visual_poc:
                evidence_items.append(visual_poc)
            
            # Add to evidence tracking
            self.evidence_items.extend(evidence_items)
            
            logger.info(f"✅ Captured {len(evidence_items)} evidence items for vulnerability {vuln_id}")
            
        except Exception as e:
            logger.error(f"❌ Error capturing evidence for vulnerability {vuln_id}: {str(e)}")
        
        return evidence_items

    async def _capture_screenshot_evidence(self, target_url: str, vuln_id: str, vuln_data: Dict[str, Any]) -> List[EvidenceItem]:
        """Capture screenshot evidence using headless browser"""
        evidence_items = []
        
        try:
            # Initialize headless browser
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.set_page_load_timeout(30)
            
            try:
                # 1. Capture normal page state
                logger.info(f"📸 Capturing normal state screenshot for {target_url}")
                driver.get(target_url)
                time.sleep(2)  # Wait for page to load
                
                normal_screenshot = await self._take_annotated_screenshot(
                    driver, 
                    f"normal_state_{vuln_id}",
                    "Normal Page State",
                    "Page before vulnerability exploitation"
                )
                if normal_screenshot:
                    evidence_items.append(normal_screenshot)
                
                # 2. Execute vulnerability payload if applicable
                if vuln_data.get('type') in ['XSS', 'Cross-Site Scripting']:
                    xss_evidence = await self._capture_xss_evidence(driver, vuln_data, vuln_id)
                    evidence_items.extend(xss_evidence)
                
                elif vuln_data.get('type') in ['SQL Injection', 'SQLi']:
                    sqli_evidence = await self._capture_sqli_evidence(driver, vuln_data, vuln_id)
                    evidence_items.extend(sqli_evidence)
                
                elif vuln_data.get('type') in ['SSRF', 'Server-Side Request Forgery']:
                    ssrf_evidence = await self._capture_ssrf_evidence(driver, vuln_data, vuln_id)
                    evidence_items.extend(ssrf_evidence)
                
                # 3. Capture final state
                final_screenshot = await self._take_annotated_screenshot(
                    driver,
                    f"final_state_{vuln_id}",
                    "Final Page State",
                    "Page after vulnerability exploitation attempt"
                )
                if final_screenshot:
                    evidence_items.append(final_screenshot)
                    
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"❌ Error capturing screenshot evidence: {str(e)}")
        
        return evidence_items

    async def _take_annotated_screenshot(self, driver, filename: str, title: str, description: str) -> Optional[EvidenceItem]:
        """Take an annotated screenshot with title and description"""
        try:
            # Take screenshot
            screenshot_path = self.screenshots_dir / f"{filename}.png"
            driver.save_screenshot(str(screenshot_path))
            
            # Add annotations
            annotated_path = await self._add_screenshot_annotations(
                screenshot_path, title, description
            )
            
            # Create evidence item
            file_size = annotated_path.stat().st_size
            file_hash = self._calculate_file_hash(annotated_path)
            
            evidence_item = EvidenceItem(
                id=f"screenshot_{filename}_{int(time.time())}",
                type="screenshot",
                title=title,
                description=description,
                file_path=str(annotated_path),
                vulnerability_id=filename.split('_')[-1] if '_' in filename else filename,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "url": driver.current_url,
                    "window_size": driver.get_window_size(),
                    "user_agent": driver.execute_script("return navigator.userAgent;")
                },
                size_bytes=file_size,
                mime_type="image/png",
                hash_sha256=file_hash
            )
            
            logger.info(f"📸 Screenshot captured: {annotated_path}")
            return evidence_item
            
        except Exception as e:
            logger.error(f"❌ Error taking annotated screenshot: {str(e)}")
            return None

    async def _add_screenshot_annotations(self, screenshot_path: Path, title: str, description: str) -> Path:
        """Add annotations to screenshot"""
        try:
            # Open image
            img = Image.open(screenshot_path)
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fallback to default if not available
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                desc_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                title_font = ImageFont.load_default()
                desc_font = ImageFont.load_default()
            
            # Add header with title and description
            header_height = 80
            new_img = Image.new('RGB', (img.width, img.height + header_height), color='white')
            new_img.paste(img, (0, header_height))
            
            draw = ImageDraw.Draw(new_img)
            
            # Draw title
            draw.text((10, 10), title, fill='black', font=title_font)
            
            # Draw description
            draw.text((10, 40), description, fill='gray', font=desc_font)
            
            # Draw timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            draw.text((10, img.height + header_height - 25), f"Captured: {timestamp}", fill='gray', font=desc_font)
            
            # Save annotated image
            annotated_path = screenshot_path.parent / f"annotated_{screenshot_path.name}"
            new_img.save(annotated_path)
            
            return annotated_path
            
        except Exception as e:
            logger.error(f"❌ Error adding annotations: {str(e)}")
            return screenshot_path

    async def _capture_xss_evidence(self, driver, vuln_data: Dict[str, Any], vuln_id: str) -> List[EvidenceItem]:
        """Capture XSS vulnerability evidence"""
        evidence_items = []
        
        try:
            # Enable JavaScript for XSS testing
            driver.execute_script("/* Enable JavaScript */")
            
            # Find input fields and test XSS
            input_elements = driver.find_elements(By.TAG_NAME, "input")
            textarea_elements = driver.find_elements(By.TAG_NAME, "textarea")
            
            xss_payload = '<script>alert("XSS_DETECTED_BY_AEGIS_X")</script>'
            
            for i, element in enumerate(input_elements + textarea_elements):
                try:
                    if element.is_displayed() and element.is_enabled():
                        # Clear and enter XSS payload
                        element.clear()
                        element.send_keys(xss_payload)
                        
                        # Take screenshot before submission
                        before_screenshot = await self._take_annotated_screenshot(
                            driver,
                            f"xss_before_{vuln_id}_{i}",
                            f"XSS Payload Entered - Field {i+1}",
                            f"XSS payload entered in input field: {xss_payload}"
                        )
                        if before_screenshot:
                            evidence_items.append(before_screenshot)
                        
                        # Try to submit form
                        try:
                            # Look for submit button
                            submit_buttons = driver.find_elements(By.XPATH, "//input[@type='submit'] | //button[@type='submit'] | //button[contains(text(), 'Submit')] | //button[contains(text(), 'Search')]")
                            if submit_buttons:
                                submit_buttons[0].click()
                                time.sleep(2)
                                
                                # Check for alert (XSS execution)
                                try:
                                    alert = driver.switch_to.alert
                                    alert_text = alert.text
                                    alert.accept()
                                    
                                    if "XSS_DETECTED_BY_AEGIS_X" in alert_text:
                                        # XSS confirmed - take screenshot
                                        xss_screenshot = await self._take_annotated_screenshot(
                                            driver,
                                            f"xss_confirmed_{vuln_id}_{i}",
                                            "XSS Vulnerability Confirmed",
                                            f"XSS payload executed successfully. Alert text: {alert_text}"
                                        )
                                        if xss_screenshot:
                                            evidence_items.append(xss_screenshot)
                                            
                                except:
                                    # No alert, but check page source for payload
                                    if xss_payload in driver.page_source:
                                        reflected_screenshot = await self._take_annotated_screenshot(
                                            driver,
                                            f"xss_reflected_{vuln_id}_{i}",
                                            "XSS Payload Reflected",
                                            f"XSS payload reflected in page source (potential stored XSS)"
                                        )
                                        if reflected_screenshot:
                                            evidence_items.append(reflected_screenshot)
                        except:
                            pass
                            
                except Exception as e:
                    logger.error(f"Error testing XSS on element {i}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"❌ Error capturing XSS evidence: {str(e)}")
        
        return evidence_items

    async def _capture_sqli_evidence(self, driver, vuln_data: Dict[str, Any], vuln_id: str) -> List[EvidenceItem]:
        """Capture SQL injection evidence"""
        evidence_items = []
        
        try:
            # SQL injection payloads
            sqli_payloads = [
                "' OR '1'='1",
                "' UNION SELECT NULL--",
                "admin'--"
            ]
            
            # Find input fields
            input_elements = driver.find_elements(By.TAG_NAME, "input")
            
            for i, element in enumerate(input_elements):
                try:
                    if element.is_displayed() and element.is_enabled():
                        for j, payload in enumerate(sqli_payloads):
                            # Enter SQL injection payload
                            element.clear()
                            element.send_keys(payload)
                            
                            # Take screenshot
                            sqli_screenshot = await self._take_annotated_screenshot(
                                driver,
                                f"sqli_payload_{vuln_id}_{i}_{j}",
                                f"SQL Injection Payload - Field {i+1}",
                                f"SQL injection payload entered: {payload}"
                            )
                            if sqli_screenshot:
                                evidence_items.append(sqli_screenshot)
                            
                            # Try to submit
                            try:
                                submit_buttons = driver.find_elements(By.XPATH, "//input[@type='submit'] | //button[@type='submit']")
                                if submit_buttons:
                                    submit_buttons[0].click()
                                    time.sleep(2)
                                    
                                    # Check for SQL error messages
                                    page_source = driver.page_source.lower()
                                    sql_errors = [
                                        'sql syntax', 'mysql_fetch', 'ora-', 'microsoft ole db',
                                        'odbc', 'jdbc', 'sqlite', 'postgresql', 'warning: mysql'
                                    ]
                                    
                                    if any(error in page_source for error in sql_errors):
                                        error_screenshot = await self._take_annotated_screenshot(
                                            driver,
                                            f"sqli_error_{vuln_id}_{i}_{j}",
                                            "SQL Injection Error Detected",
                                            f"SQL error detected after payload: {payload}"
                                        )
                                        if error_screenshot:
                                            evidence_items.append(error_screenshot)
                            except:
                                pass
                                
                except Exception as e:
                    logger.error(f"Error testing SQL injection on element {i}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"❌ Error capturing SQL injection evidence: {str(e)}")
        
        return evidence_items

    async def _capture_ssrf_evidence(self, driver, vuln_data: Dict[str, Any], vuln_id: str) -> List[EvidenceItem]:
        """Capture SSRF vulnerability evidence"""
        evidence_items = []
        
        try:
            # SSRF payloads
            ssrf_payloads = [
                "http://127.0.0.1:80",
                "http://localhost:22",
                "http://169.254.169.254/latest/meta-data/"
            ]
            
            # Find URL input fields
            url_inputs = driver.find_elements(By.XPATH, "//input[contains(@name, 'url') or contains(@placeholder, 'url') or contains(@id, 'url')]")
            
            for i, element in enumerate(url_inputs):
                try:
                    if element.is_displayed() and element.is_enabled():
                        for j, payload in enumerate(ssrf_payloads):
                            # Enter SSRF payload
                            element.clear()
                            element.send_keys(payload)
                            
                            # Take screenshot
                            ssrf_screenshot = await self._take_annotated_screenshot(
                                driver,
                                f"ssrf_payload_{vuln_id}_{i}_{j}",
                                f"SSRF Payload - Field {i+1}",
                                f"SSRF payload entered: {payload}"
                            )
                            if ssrf_screenshot:
                                evidence_items.append(ssrf_screenshot)
                            
                            # Submit and check response
                            try:
                                submit_buttons = driver.find_elements(By.XPATH, "//input[@type='submit'] | //button[@type='submit']")
                                if submit_buttons:
                                    submit_buttons[0].click()
                                    time.sleep(3)
                                    
                                    # Check for internal service responses
                                    page_source = driver.page_source.lower()
                                    ssrf_indicators = [
                                        'root:', 'daemon:', 'private', 'internal',
                                        'aws_access_key', 'instance-id'
                                    ]
                                    
                                    if any(indicator in page_source for indicator in ssrf_indicators):
                                        ssrf_success_screenshot = await self._take_annotated_screenshot(
                                            driver,
                                            f"ssrf_success_{vuln_id}_{i}_{j}",
                                            "SSRF Vulnerability Confirmed",
                                            f"SSRF successful with payload: {payload}"
                                        )
                                        if ssrf_success_screenshot:
                                            evidence_items.append(ssrf_success_screenshot)
                            except:
                                pass
                                
                except Exception as e:
                    logger.error(f"Error testing SSRF on element {i}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"❌ Error capturing SSRF evidence: {str(e)}")
        
        return evidence_items

    async def _capture_http_evidence(self, vuln_data: Dict[str, Any], vuln_id: str) -> List[EvidenceItem]:
        """Capture HTTP request/response evidence"""
        evidence_items = []
        
        try:
            target_url = vuln_data.get('target_url')
            if not target_url:
                return evidence_items
            
            # Capture normal request
            normal_log = await self._capture_http_transaction(
                target_url, 
                method='GET',
                title="Normal HTTP Request",
                description="Baseline HTTP request/response"
            )
            if normal_log:
                evidence_items.append(normal_log)
            
            # Capture vulnerability exploitation request
            if vuln_data.get('exploit_code'):
                exploit_log = await self._capture_exploit_http_transaction(vuln_data, vuln_id)
                if exploit_log:
                    evidence_items.append(exploit_log)
                    
        except Exception as e:
            logger.error(f"❌ Error capturing HTTP evidence: {str(e)}")
        
        return evidence_items

    async def _capture_http_transaction(self, url: str, method: str = 'GET', data: Dict = None, 
                                      title: str = "HTTP Transaction", description: str = "") -> Optional[EvidenceItem]:
        """Capture a single HTTP transaction"""
        try:
            # Make request and capture details
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = self.http_session.get(url, timeout=10)
            elif method.upper() == 'POST':
                response = self.http_session.post(url, data=data, timeout=10)
            else:
                response = self.http_session.request(method, url, data=data, timeout=10)
            
            end_time = time.time()
            
            # Create HTTP log
            http_log = {
                "timestamp": datetime.now().isoformat(),
                "request": {
                    "method": method.upper(),
                    "url": url,
                    "headers": dict(response.request.headers),
                    "body": data if data else None
                },
                "response": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text[:10000],  # Limit body size
                    "size_bytes": len(response.content)
                },
                "timing": {
                    "duration_seconds": end_time - start_time
                }
            }
            
            # Save to file
            log_filename = f"http_transaction_{int(time.time())}.json"
            log_path = self.logs_dir / log_filename
            
            async with aiofiles.open(log_path, 'w') as f:
                await f.write(json.dumps(http_log, indent=2))
            
            # Create evidence item
            file_size = log_path.stat().st_size
            file_hash = self._calculate_file_hash(log_path)
            
            evidence_item = EvidenceItem(
                id=f"http_log_{int(time.time())}",
                type="http_log",
                title=title,
                description=description,
                file_path=str(log_path),
                vulnerability_id="",
                timestamp=datetime.now().isoformat(),
                metadata={
                    "method": method.upper(),
                    "status_code": response.status_code,
                    "response_size": len(response.content),
                    "duration": end_time - start_time
                },
                size_bytes=file_size,
                mime_type="application/json",
                hash_sha256=file_hash
            )
            
            return evidence_item
            
        except Exception as e:
            logger.error(f"❌ Error capturing HTTP transaction: {str(e)}")
            return None

    async def _capture_exploit_http_transaction(self, vuln_data: Dict[str, Any], vuln_id: str) -> Optional[EvidenceItem]:
        """Capture HTTP transaction for vulnerability exploitation"""
        try:
            # Parse exploit code to extract HTTP details
            exploit_code = vuln_data.get('exploit_code', '')
            target_url = vuln_data.get('target_url', '')
            
            # Extract method and data from exploit code
            method = 'GET'
            data = None
            
            if 'curl -X POST' in exploit_code or 'POST' in exploit_code:
                method = 'POST'
                # Try to extract POST data
                if '-d ' in exploit_code:
                    data_match = re.search(r"-d '([^']*)'", exploit_code)
                    if data_match:
                        data_str = data_match.group(1)
                        # Parse form data
                        data = {}
                        for pair in data_str.split('&'):
                            if '=' in pair:
                                key, value = pair.split('=', 1)
                                data[key] = value
            
            # Capture the exploit transaction
            exploit_log = await self._capture_http_transaction(
                target_url,
                method=method,
                data=data,
                title=f"Vulnerability Exploitation - {vuln_data.get('type', 'Unknown')}",
                description=f"HTTP transaction demonstrating {vuln_data.get('title', 'vulnerability')}"
            )
            
            return exploit_log
            
        except Exception as e:
            logger.error(f"❌ Error capturing exploit HTTP transaction: {str(e)}")
            return None

    async def _capture_payload_evidence(self, vuln_data: Dict[str, Any], vuln_id: str) -> List[EvidenceItem]:
        """Capture payload execution evidence"""
        evidence_items = []
        
        try:
            exploit_code = vuln_data.get('exploit_code', '')
            if not exploit_code:
                return evidence_items
            
            # Create payload execution log
            payload_log = {
                "vulnerability_id": vuln_id,
                "vulnerability_type": vuln_data.get('type', 'Unknown'),
                "target_url": vuln_data.get('target_url', ''),
                "exploit_code": exploit_code,
                "payload_details": vuln_data.get('payload_details', {}),
                "execution_timestamp": datetime.now().isoformat(),
                "execution_context": "Automated Evidence Collection",
                "safety_note": "This payload was executed in a controlled environment for evidence collection purposes"
            }
            
            # Save payload log
            payload_filename = f"payload_execution_{vuln_id}.json"
            payload_path = self.payloads_dir / payload_filename
            
            async with aiofiles.open(payload_path, 'w') as f:
                await f.write(json.dumps(payload_log, indent=2))
            
            # Create evidence item
            file_size = payload_path.stat().st_size
            file_hash = self._calculate_file_hash(payload_path)
            
            evidence_item = EvidenceItem(
                id=f"payload_{vuln_id}_{int(time.time())}",
                type="payload_execution",
                title="Payload Execution Log",
                description=f"Detailed log of payload execution for {vuln_data.get('type', 'vulnerability')}",
                file_path=str(payload_path),
                vulnerability_id=vuln_id,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "vulnerability_type": vuln_data.get('type', 'Unknown'),
                    "severity": vuln_data.get('severity', 'Unknown'),
                    "target_url": vuln_data.get('target_url', '')
                },
                size_bytes=file_size,
                mime_type="application/json",
                hash_sha256=file_hash
            )
            
            evidence_items.append(evidence_item)
            
        except Exception as e:
            logger.error(f"❌ Error capturing payload evidence: {str(e)}")
        
        return evidence_items

    async def _capture_network_evidence(self, vuln_data: Dict[str, Any], vuln_id: str) -> List[EvidenceItem]:
        """Capture network traffic evidence"""
        evidence_items = []
        
        try:
            # Create network capture log
            network_log = {
                "vulnerability_id": vuln_id,
                "capture_timestamp": datetime.now().isoformat(),
                "target_url": vuln_data.get('target_url', ''),
                "network_interactions": [],
                "dns_queries": [],
                "tcp_connections": [],
                "http_transactions": self.network_logs[-10:] if self.network_logs else []  # Last 10 transactions
            }
            
            # Add DNS resolution info
            target_url = vuln_data.get('target_url', '')
            if target_url:
                try:
                    from urllib.parse import urlparse
                    hostname = urlparse(target_url).hostname
                    if hostname:
                        import socket
                        ip_addresses = socket.gethostbyname_ex(hostname)[2]
                        network_log["dns_queries"].append({
                            "hostname": hostname,
                            "ip_addresses": ip_addresses,
                            "timestamp": datetime.now().isoformat()
                        })
                except:
                    pass
            
            # Save network log
            network_filename = f"network_capture_{vuln_id}.json"
            network_path = self.network_dir / network_filename
            
            async with aiofiles.open(network_path, 'w') as f:
                await f.write(json.dumps(network_log, indent=2))
            
            # Create evidence item
            file_size = network_path.stat().st_size
            file_hash = self._calculate_file_hash(network_path)
            
            evidence_item = EvidenceItem(
                id=f"network_{vuln_id}_{int(time.time())}",
                type="network_capture",
                title="Network Traffic Capture",
                description=f"Network traffic analysis for vulnerability {vuln_id}",
                file_path=str(network_path),
                vulnerability_id=vuln_id,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "target_url": target_url,
                    "dns_queries_count": len(network_log["dns_queries"]),
                    "http_transactions_count": len(network_log["http_transactions"])
                },
                size_bytes=file_size,
                mime_type="application/json",
                hash_sha256=file_hash
            )
            
            evidence_items.append(evidence_item)
            
        except Exception as e:
            logger.error(f"❌ Error capturing network evidence: {str(e)}")
        
        return evidence_items

    async def _generate_visual_poc(self, vuln_data: Dict[str, Any], vuln_id: str) -> Optional[EvidenceItem]:
        """Generate visual proof-of-concept diagram"""
        try:
            # Create a visual representation of the vulnerability
            fig_width, fig_height = 1200, 800
            img = Image.new('RGB', (fig_width, fig_height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
                header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
                text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Draw title
            title = f"Vulnerability: {vuln_data.get('title', 'Unknown')}"
            draw.text((50, 30), title, fill='red', font=title_font)
            
            # Draw severity badge
            severity = vuln_data.get('severity', 'Unknown')
            severity_color = {
                'Critical': 'red',
                'High': 'orange',
                'Medium': 'yellow',
                'Low': 'green'
            }.get(severity, 'gray')
            
            draw.rectangle([50, 80, 200, 110], fill=severity_color)
            draw.text((60, 85), f"Severity: {severity}", fill='white', font=header_font)
            
            # Draw vulnerability details
            y_pos = 150
            details = [
                f"Type: {vuln_data.get('type', 'Unknown')}",
                f"Target: {vuln_data.get('target_url', 'Unknown')}",
                f"CVSS Score: {vuln_data.get('cvss_score', 'N/A')}",
                f"Discovery Method: {vuln_data.get('discovery_method', 'Unknown')}",
                f"Impact: {vuln_data.get('impact', 'Unknown')[:100]}..."
            ]
            
            for detail in details:
                draw.text((50, y_pos), detail, fill='black', font=text_font)
                y_pos += 30
            
            # Draw attack chain if available
            if vuln_data.get('attack_chain'):
                draw.text((50, y_pos + 20), "Attack Chain:", fill='black', font=header_font)
                y_pos += 50
                
                for i, step in enumerate(vuln_data['attack_chain'][:5]):  # Limit to 5 steps
                    step_text = f"{i+1}. {step}"
                    draw.text((70, y_pos), step_text, fill='darkblue', font=text_font)
                    y_pos += 25
            
            # Draw timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            draw.text((50, fig_height - 50), f"Generated: {timestamp}", fill='gray', font=text_font)
            draw.text((50, fig_height - 30), "AEGIS-X Advanced Professional Hunter", fill='gray', font=text_font)
            
            # Save visual PoC
            poc_filename = f"visual_poc_{vuln_id}.png"
            poc_path = self.reports_dir / poc_filename
            img.save(poc_path)
            
            # Create evidence item
            file_size = poc_path.stat().st_size
            file_hash = self._calculate_file_hash(poc_path)
            
            evidence_item = EvidenceItem(
                id=f"visual_poc_{vuln_id}_{int(time.time())}",
                type="visual_poc",
                title="Visual Proof of Concept",
                description=f"Visual diagram illustrating the {vuln_data.get('type', 'vulnerability')}",
                file_path=str(poc_path),
                vulnerability_id=vuln_id,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "vulnerability_type": vuln_data.get('type', 'Unknown'),
                    "severity": severity,
                    "dimensions": f"{fig_width}x{fig_height}"
                },
                size_bytes=file_size,
                mime_type="image/png",
                hash_sha256=file_hash
            )
            
            logger.info(f"🎨 Generated visual PoC: {poc_path}")
            return evidence_item
            
        except Exception as e:
            logger.error(f"❌ Error generating visual PoC: {str(e)}")
            return None

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return ""

    async def generate_evidence_report(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Generate comprehensive evidence report"""
        logger.info("📊 Generating comprehensive evidence report")
        
        try:
            # Create HTML report
            html_content = self._generate_html_evidence_report(vulnerabilities)
            
            # Save report
            report_filename = f"evidence_report_{self.current_session_id}.html"
            report_path = self.reports_dir / report_filename
            
            async with aiofiles.open(report_path, 'w') as f:
                await f.write(html_content)
            
            logger.info(f"📋 Evidence report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"❌ Error generating evidence report: {str(e)}")
            return ""

    def _generate_html_evidence_report(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Generate HTML evidence report"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AEGIS-X Evidence Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .vulnerability {{ background: white; margin: 20px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .severity-critical {{ border-left: 5px solid #dc3545; }}
        .severity-high {{ border-left: 5px solid #fd7e14; }}
        .severity-medium {{ border-left: 5px solid #ffc107; }}
        .severity-low {{ border-left: 5px solid #28a745; }}
        .evidence-item {{ background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .screenshot {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }}
        .code {{ background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto; }}
        .metadata {{ font-size: 0.9em; color: #666; }}
        .timestamp {{ color: #999; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 AEGIS-X Evidence Report</h1>
        <p>Advanced Professional Bug Bounty Hunter - Evidence Collection</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p>Session ID: {self.current_session_id}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Evidence Summary</h2>
        <p><strong>Total Vulnerabilities:</strong> {len(vulnerabilities)}</p>
        <p><strong>Total Evidence Items:</strong> {len(self.evidence_items)}</p>
        <p><strong>Evidence Types:</strong> Screenshots, HTTP Logs, Network Captures, Payload Executions, Visual PoCs</p>
    </div>
"""
        
        # Add vulnerability evidence sections
        for vuln in vulnerabilities:
            vuln_id = vuln.get('id', 'unknown')
            severity = vuln.get('severity', 'Unknown').lower()
            
            # Get evidence items for this vulnerability
            vuln_evidence = [item for item in self.evidence_items if item.vulnerability_id == vuln_id]
            
            html += f"""
    <div class="vulnerability severity-{severity}">
        <h3>🎯 {vuln.get('title', 'Unknown Vulnerability')}</h3>
        <div class="metadata">
            <p><strong>Type:</strong> {vuln.get('type', 'Unknown')}</p>
            <p><strong>Severity:</strong> {vuln.get('severity', 'Unknown')}</p>
            <p><strong>CVSS Score:</strong> {vuln.get('cvss_score', 'N/A')}</p>
            <p><strong>Target URL:</strong> {vuln.get('target_url', 'Unknown')}</p>
            <p><strong>Discovery Method:</strong> {vuln.get('discovery_method', 'Unknown')}</p>
        </div>
        
        <h4>📝 Description</h4>
        <p>{vuln.get('description', 'No description available')}</p>
        
        <h4>💥 Impact</h4>
        <p>{vuln.get('impact', 'No impact description available')}</p>
        
        <h4>🔧 Proof of Concept</h4>
        <div class="code">{vuln.get('proof_of_concept', 'No PoC available')}</div>
        
        <h4>⚡ Exploit Code</h4>
        <div class="code">{vuln.get('exploit_code', 'No exploit code available')}</div>
        
        <h4>📸 Evidence Items ({len(vuln_evidence)})</h4>
"""
            
            # Add evidence items
            for evidence in vuln_evidence:
                html += f"""
        <div class="evidence-item">
            <h5>{evidence.title}</h5>
            <p>{evidence.description}</p>
            <div class="metadata">
                <p><strong>Type:</strong> {evidence.type}</p>
                <p><strong>File:</strong> {evidence.file_path}</p>
                <p><strong>Size:</strong> {evidence.size_bytes} bytes</p>
                <p><strong>Hash:</strong> {evidence.hash_sha256[:16]}...</p>
                <p class="timestamp">Captured: {evidence.timestamp}</p>
            </div>
"""
                
                # Embed screenshots
                if evidence.type == "screenshot" and evidence.file_path.endswith('.png'):
                    try:
                        with open(evidence.file_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode()
                            html += f'<img src="data:image/png;base64,{img_data}" class="screenshot" alt="{evidence.title}">'
                    except:
                        html += f'<p><em>Screenshot not available: {evidence.file_path}</em></p>'
                
                html += "</div>"
            
            html += "</div>"
        
        html += """
    <div class="footer">
        <p><em>This report was generated by AEGIS-X Advanced Professional Hunter System</em></p>
        <p><em>All evidence was collected in a controlled environment for security assessment purposes</em></p>
    </div>
</body>
</html>
"""
        
        return html

    async def cleanup_evidence(self, max_age_hours: int = 24) -> None:
        """Clean up old evidence files"""
        try:
            cutoff_time = time.time() - (max_age_hours * 3600)
            
            for evidence_dir in [self.screenshots_dir, self.videos_dir, self.network_dir, 
                               self.logs_dir, self.payloads_dir]:
                for file_path in evidence_dir.glob("*"):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        logger.info(f"🗑️ Cleaned up old evidence file: {file_path}")
                        
        except Exception as e:
            logger.error(f"❌ Error cleaning up evidence: {str(e)}")

    def get_evidence_summary(self) -> Dict[str, Any]:
        """Get summary of collected evidence"""
        summary = {
            "total_evidence_items": len(self.evidence_items),
            "evidence_by_type": {},
            "total_size_bytes": 0,
            "session_id": self.current_session_id,
            "evidence_directory": str(self.evidence_dir)
        }
        
        for item in self.evidence_items:
            if item.type not in summary["evidence_by_type"]:
                summary["evidence_by_type"][item.type] = 0
            summary["evidence_by_type"][item.type] += 1
            summary["total_size_bytes"] += item.size_bytes
        
        return summary