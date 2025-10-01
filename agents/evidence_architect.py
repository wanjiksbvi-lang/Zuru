#!/usr/bin/env python3
"""
AEGIS-X Evidence Architect Agent
Proof Creator - Captures comprehensive evidence for vulnerabilities
"""

import os
import json
import logging
import asyncio
import base64
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class EvidenceArchitect:
    """
    The Evidence Architect captures comprehensive evidence for vulnerabilities
    including screenshots, videos, network traffic, and detailed documentation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.EvidenceArchitect")
        self.model_name = "Phi-3-mini"
        self.learning_data = self._load_learning_data()
        
        # Evidence collection strategies
        self.evidence_strategies = self._initialize_evidence_strategies()
        self.annotation_templates = self._initialize_annotation_templates()
        
        self.logger.info("📸 Evidence Architect initialized with comprehensive capture capabilities")
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data from previous evidence collection sessions"""
        learning_file = Path("learn/evidence_learning.json")
        
        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load evidence learning data: {e}")
        
        return {
            "evidence_quality_scores": {},
            "capture_success_rates": {},
            "annotation_effectiveness": {},
            "improvement_suggestions": []
        }
    
    def _initialize_evidence_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize evidence collection strategies by vulnerability type"""
        return {
            "web": {
                "required_evidence": [
                    "screenshot_before",
                    "screenshot_after",
                    "video_demonstration",
                    "network_traffic",
                    "curl_command",
                    "response_headers"
                ],
                "optional_evidence": [
                    "source_code_snippet",
                    "browser_console_logs",
                    "performance_metrics"
                ],
                "capture_methods": {
                    "screenshot": "playwright_screenshot",
                    "video": "playwright_video",
                    "network": "har_capture",
                    "console": "browser_console"
                }
            },
            "mobile": {
                "required_evidence": [
                    "app_screenshot",
                    "network_traffic",
                    "decompiled_code",
                    "manifest_analysis"
                ],
                "optional_evidence": [
                    "dynamic_analysis_logs",
                    "frida_traces",
                    "api_calls"
                ],
                "capture_methods": {
                    "screenshot": "mobile_screenshot",
                    "network": "mitmproxy_capture",
                    "code": "static_analysis"
                }
            },
            "api": {
                "required_evidence": [
                    "request_response_pair",
                    "curl_command",
                    "postman_collection",
                    "api_documentation"
                ],
                "optional_evidence": [
                    "rate_limiting_test",
                    "authentication_bypass",
                    "parameter_fuzzing_results"
                ],
                "capture_methods": {
                    "request": "http_capture",
                    "documentation": "api_analysis"
                }
            }
        }
    
    def _initialize_annotation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize annotation templates for different evidence types"""
        return {
            "screenshot": {
                "elements": [
                    {"type": "arrow", "color": "red", "width": 3},
                    {"type": "rectangle", "color": "red", "width": 2},
                    {"type": "text", "color": "red", "font_size": 16},
                    {"type": "highlight", "color": "yellow", "opacity": 0.3}
                ],
                "annotations": [
                    "vulnerability_location",
                    "payload_injection_point",
                    "response_indication",
                    "error_message_highlight"
                ]
            },
            "video": {
                "elements": [
                    {"type": "overlay_text", "position": "top_left"},
                    {"type": "timestamp", "position": "bottom_right"},
                    {"type": "step_counter", "position": "top_right"},
                    {"type": "highlight_cursor", "color": "red"}
                ],
                "annotations": [
                    "step_descriptions",
                    "vulnerability_demonstration",
                    "impact_visualization"
                ]
            },
            "network_traffic": {
                "elements": [
                    {"type": "request_highlight", "color": "blue"},
                    {"type": "response_highlight", "color": "green"},
                    {"type": "vulnerability_marker", "color": "red"}
                ],
                "annotations": [
                    "malicious_payload",
                    "vulnerable_parameter",
                    "server_response",
                    "security_headers"
                ]
            }
        }
    
    async def capture_evidence(self, vulnerability: Dict[str, Any], poc_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture comprehensive evidence for a vulnerability
        """
        self.logger.info(f"📸 Capturing evidence for: {vulnerability.get('title', 'Unknown')}")
        
        # Determine evidence strategy
        target_type = vulnerability.get("target_type", "web")
        strategy = self.evidence_strategies.get(target_type, self.evidence_strategies["web"])
        
        # Create evidence directory
        evidence_dir = self._create_evidence_directory(vulnerability)
        
        # Capture required evidence
        evidence_collection = {}
        
        for evidence_type in strategy["required_evidence"]:
            try:
                evidence_data = await self._capture_evidence_type(
                    evidence_type, vulnerability, poc_result, evidence_dir
                )
                evidence_collection[evidence_type] = evidence_data
                self.logger.info(f"✅ Captured {evidence_type}")
            except Exception as e:
                self.logger.error(f"❌ Failed to capture {evidence_type}: {str(e)}")
                evidence_collection[evidence_type] = {"error": str(e)}
        
        # Capture optional evidence
        for evidence_type in strategy.get("optional_evidence", []):
            try:
                evidence_data = await self._capture_evidence_type(
                    evidence_type, vulnerability, poc_result, evidence_dir
                )
                evidence_collection[evidence_type] = evidence_data
                self.logger.debug(f"📎 Captured optional {evidence_type}")
            except Exception as e:
                self.logger.debug(f"⚠️ Optional evidence {evidence_type} failed: {str(e)}")
        
        # Apply self-reflection
        reflection_result = self._apply_evidence_reflection(evidence_collection, vulnerability)
        
        # Generate evidence summary
        evidence_summary = self._generate_evidence_summary(evidence_collection, evidence_dir)
        
        final_result = {
            "vulnerability_id": vulnerability.get("id", "unknown"),
            "evidence_directory": str(evidence_dir),
            "evidence_collection": evidence_collection,
            "evidence_summary": evidence_summary,
            "quality_score": self._calculate_evidence_quality(evidence_collection),
            "reflection_notes": reflection_result,
            "captured_at": datetime.now().isoformat()
        }
        
        # Store learning data
        await self._store_evidence_learning(final_result, vulnerability)
        
        return final_result
    
    def _create_evidence_directory(self, vulnerability: Dict[str, Any]) -> Path:
        """Create organized evidence directory"""
        # Create unique directory name
        vuln_id = vulnerability.get("id", hashlib.md5(str(vulnerability).encode()).hexdigest()[:8])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        evidence_dir = Path("evidence") / f"{vuln_id}_{timestamp}"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (evidence_dir / "screenshots").mkdir(exist_ok=True)
        (evidence_dir / "videos").mkdir(exist_ok=True)
        (evidence_dir / "network").mkdir(exist_ok=True)
        (evidence_dir / "code").mkdir(exist_ok=True)
        (evidence_dir / "logs").mkdir(exist_ok=True)
        
        return evidence_dir
    
    async def _capture_evidence_type(self, evidence_type: str, vulnerability: Dict[str, Any], 
                                   poc_result: Dict[str, Any], evidence_dir: Path) -> Dict[str, Any]:
        """Capture specific type of evidence"""
        
        if evidence_type == "screenshot_before":
            return await self._capture_screenshot_before(vulnerability, evidence_dir)
        elif evidence_type == "screenshot_after":
            return await self._capture_screenshot_after(vulnerability, poc_result, evidence_dir)
        elif evidence_type == "video_demonstration":
            return await self._capture_video_demonstration(vulnerability, poc_result, evidence_dir)
        elif evidence_type == "network_traffic":
            return await self._capture_network_traffic(vulnerability, poc_result, evidence_dir)
        elif evidence_type == "curl_command":
            return self._generate_curl_command(vulnerability, poc_result, evidence_dir)
        elif evidence_type == "response_headers":
            return await self._capture_response_headers(vulnerability, evidence_dir)
        elif evidence_type == "source_code_snippet":
            return self._capture_source_code(vulnerability, evidence_dir)
        elif evidence_type == "browser_console_logs":
            return await self._capture_console_logs(vulnerability, evidence_dir)
        else:
            return {"error": f"Unknown evidence type: {evidence_type}"}
    
    async def _capture_screenshot_before(self, vulnerability: Dict[str, Any], evidence_dir: Path) -> Dict[str, Any]:
        """Capture screenshot before vulnerability exploitation"""
        target_url = vulnerability.get("target", "")
        
        if not target_url.startswith("http"):
            target_url = f"http://{target_url}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            
            page = await context.new_page()
            
            try:
                await page.goto(target_url, timeout=30000)
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                screenshot_path = evidence_dir / "screenshots" / "before_exploitation.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                
                # Add annotations
                annotated_path = await self._annotate_screenshot(
                    screenshot_path, 
                    "Normal state before vulnerability exploitation",
                    []
                )
                
                return {
                    "success": True,
                    "file_path": str(screenshot_path),
                    "annotated_path": str(annotated_path),
                    "url": target_url,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {"error": str(e), "url": target_url}
            finally:
                await browser.close()
    
    async def _capture_screenshot_after(self, vulnerability: Dict[str, Any], poc_result: Dict[str, Any], evidence_dir: Path) -> Dict[str, Any]:
        """Capture screenshot after vulnerability exploitation"""
        target_url = vulnerability.get("target", "")
        
        if not target_url.startswith("http"):
            target_url = f"http://{target_url}"
        
        # Extract payload from PoC result
        payload = self._extract_payload_from_poc(poc_result)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            page = await context.new_page()
            
            try:
                # Navigate and execute payload
                if vulnerability.get("method", "GET").upper() == "POST":
                    await page.goto(target_url)
                    # Execute POST request with payload
                    await page.evaluate(f"""
                        fetch('{target_url}', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                            body: '{payload}'
                        }});
                    """)
                else:
                    # GET request with payload in URL
                    exploit_url = f"{target_url}?{payload}"
                    await page.goto(exploit_url, timeout=30000)
                
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                screenshot_path = evidence_dir / "screenshots" / "after_exploitation.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                
                # Add annotations highlighting the vulnerability
                annotations = [
                    {"type": "highlight", "text": "Vulnerability demonstrated here", "color": "red"}
                ]
                
                annotated_path = await self._annotate_screenshot(
                    screenshot_path,
                    f"Vulnerability exploitation result: {vulnerability.get('title', 'Unknown')}",
                    annotations
                )
                
                return {
                    "success": True,
                    "file_path": str(screenshot_path),
                    "annotated_path": str(annotated_path),
                    "exploit_url": exploit_url if 'exploit_url' in locals() else target_url,
                    "payload": payload,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {"error": str(e), "url": target_url, "payload": payload}
            finally:
                await browser.close()
    
    async def _capture_video_demonstration(self, vulnerability: Dict[str, Any], poc_result: Dict[str, Any], evidence_dir: Path) -> Dict[str, Any]:
        """Capture video demonstration of vulnerability exploitation"""
        target_url = vulnerability.get("target", "")
        
        if not target_url.startswith("http"):
            target_url = f"http://{target_url}"
        
        video_path = evidence_dir / "videos" / "vulnerability_demonstration.webm"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_video_dir=str(evidence_dir / "videos"),
                record_video_size={"width": 1920, "height": 1080}
            )
            
            page = await context.new_page()
            
            try:
                # Step 1: Navigate to target
                await page.goto(target_url, timeout=30000)
                await page.wait_for_load_state("networkidle", timeout=10000)
                await asyncio.sleep(2)  # Pause for video clarity
                
                # Step 2: Execute vulnerability
                payload = self._extract_payload_from_poc(poc_result)
                
                if vulnerability.get("method", "GET").upper() == "POST":
                    # Demonstrate POST exploitation
                    await page.evaluate(f"""
                        console.log('Executing vulnerability payload...');
                        fetch('{target_url}', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                            body: '{payload}'
                        }}).then(response => response.text()).then(data => console.log('Response:', data));
                    """)
                else:
                    # Demonstrate GET exploitation
                    exploit_url = f"{target_url}?{payload}"
                    await page.goto(exploit_url)
                
                await page.wait_for_load_state("networkidle", timeout=10000)
                await asyncio.sleep(3)  # Show result
                
                # Step 3: Highlight vulnerability impact
                await page.evaluate("""
                    console.log('Vulnerability successfully demonstrated');
                """)
                
                await asyncio.sleep(2)
                
                return {
                    "success": True,
                    "file_path": str(video_path),
                    "duration_seconds": 7,
                    "steps_demonstrated": [
                        "Navigate to target URL",
                        "Execute vulnerability payload",
                        "Show vulnerability impact"
                    ],
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {"error": str(e), "url": target_url}
            finally:
                await context.close()
                await browser.close()
    
    async def _capture_network_traffic(self, vulnerability: Dict[str, Any], poc_result: Dict[str, Any], evidence_dir: Path) -> Dict[str, Any]:
        """Capture network traffic during vulnerability exploitation"""
        target_url = vulnerability.get("target", "")
        
        if not target_url.startswith("http"):
            target_url = f"http://{target_url}"
        
        har_path = evidence_dir / "network" / "traffic_capture.har"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            page = await context.new_page()
            
            # Start HAR recording
            await context.tracing.start(screenshots=True, snapshots=True)
            
            try:
                # Execute vulnerability with network capture
                payload = self._extract_payload_from_poc(poc_result)
                
                if vulnerability.get("method", "GET").upper() == "POST":
                    await page.goto(target_url)
                    response = await page.evaluate(f"""
                        fetch('{target_url}', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                            body: '{payload}'
                        }}).then(response => response.text())
                    """)
                else:
                    exploit_url = f"{target_url}?{payload}"
                    await page.goto(exploit_url)
                
                # Stop tracing and save HAR
                await context.tracing.stop(path=har_path)
                
                # Analyze captured traffic
                traffic_analysis = self._analyze_network_traffic(har_path, payload)
                
                return {
                    "success": True,
                    "har_file": str(har_path),
                    "payload": payload,
                    "traffic_analysis": traffic_analysis,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {"error": str(e), "url": target_url}
            finally:
                await browser.close()
    
    def _generate_curl_command(self, vulnerability: Dict[str, Any], poc_result: Dict[str, Any], evidence_dir: Path) -> Dict[str, Any]:
        """Generate curl command for vulnerability reproduction"""
        target_url = vulnerability.get("target", "")
        
        if not target_url.startswith("http"):
            target_url = f"http://{target_url}"
        
        payload = self._extract_payload_from_poc(poc_result)
        method = vulnerability.get("method", "GET").upper()
        
        # Generate curl command
        if method == "POST":
            curl_command = f"""curl -X POST '{target_url}' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \\
  -d '{payload}' \\
  --max-time 30 \\
  --silent \\
  --show-error"""
        else:
            curl_command = f"""curl -X GET '{target_url}?{payload}' \\
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \\
  --max-time 30 \\
  --silent \\
  --show-error"""
        
        # Save curl command to file
        curl_file = evidence_dir / "curl_command.txt"
        with open(curl_file, 'w') as f:
            f.write(f"# Vulnerability: {vulnerability.get('title', 'Unknown')}\n")
            f.write(f"# Target: {target_url}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
            f.write(curl_command)
            f.write("\n\n# Expected indicators:\n")
            f.write("# - Check response for vulnerability indicators\n")
            f.write("# - Look for error messages, unexpected behavior\n")
            f.write("# - Verify payload execution or reflection\n")
        
        return {
            "success": True,
            "curl_command": curl_command,
            "file_path": str(curl_file),
            "method": method,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _capture_response_headers(self, vulnerability: Dict[str, Any], evidence_dir: Path) -> Dict[str, Any]:
        """Capture HTTP response headers"""
        target_url = vulnerability.get("target", "")
        
        if not target_url.startswith("http"):
            target_url = f"http://{target_url}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            headers_data = []
            
            # Capture response headers
            page.on("response", lambda response: headers_data.append({
                "url": response.url,
                "status": response.status,
                "headers": response.headers,
                "timestamp": datetime.now().isoformat()
            }))
            
            try:
                await page.goto(target_url, timeout=30000)
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                # Save headers to file
                headers_file = evidence_dir / "response_headers.json"
                with open(headers_file, 'w') as f:
                    json.dump(headers_data, f, indent=2)
                
                # Analyze security headers
                security_analysis = self._analyze_security_headers(headers_data)
                
                return {
                    "success": True,
                    "headers_file": str(headers_file),
                    "headers_captured": len(headers_data),
                    "security_analysis": security_analysis,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {"error": str(e), "url": target_url}
            finally:
                await browser.close()
    
    def _capture_source_code(self, vulnerability: Dict[str, Any], evidence_dir: Path) -> Dict[str, Any]:
        """Capture relevant source code snippets"""
        # This would extract relevant code from the vulnerability context
        code_snippet = vulnerability.get("code_snippet", "")
        
        if not code_snippet:
            return {"error": "No source code available"}
        
        code_file = evidence_dir / "code" / "vulnerable_code.txt"
        with open(code_file, 'w') as f:
            f.write(f"# Vulnerable Code Snippet\n")
            f.write(f"# Vulnerability: {vulnerability.get('title', 'Unknown')}\n")
            f.write(f"# File: {vulnerability.get('file_path', 'Unknown')}\n")
            f.write(f"# Line: {vulnerability.get('line_number', 'Unknown')}\n\n")
            f.write(code_snippet)
        
        return {
            "success": True,
            "code_file": str(code_file),
            "lines_captured": len(code_snippet.split('\n')),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _capture_console_logs(self, vulnerability: Dict[str, Any], evidence_dir: Path) -> Dict[str, Any]:
        """Capture browser console logs during exploitation"""
        target_url = vulnerability.get("target", "")
        
        if not target_url.startswith("http"):
            target_url = f"http://{target_url}"
        
        console_logs = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Capture console messages
            page.on("console", lambda msg: console_logs.append({
                "type": msg.type,
                "text": msg.text,
                "timestamp": datetime.now().isoformat()
            }))
            
            try:
                await page.goto(target_url, timeout=30000)
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                # Save console logs
                logs_file = evidence_dir / "logs" / "console_logs.json"
                with open(logs_file, 'w') as f:
                    json.dump(console_logs, f, indent=2)
                
                return {
                    "success": True,
                    "logs_file": str(logs_file),
                    "logs_captured": len(console_logs),
                    "error_count": len([log for log in console_logs if log["type"] == "error"]),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {"error": str(e), "url": target_url}
            finally:
                await browser.close()
    
    async def _annotate_screenshot(self, screenshot_path: Path, title: str, annotations: List[Dict[str, Any]]) -> Path:
        """Add annotations to screenshot"""
        try:
            # Load image
            image = Image.open(screenshot_path)
            draw = ImageDraw.Draw(image)
            
            # Try to load a font, fallback to default if not available
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Add title
            draw.text((10, 10), title, fill="red", font=font)
            
            # Add annotations
            for i, annotation in enumerate(annotations):
                y_pos = 40 + (i * 25)
                draw.text((10, y_pos), annotation.get("text", ""), fill=annotation.get("color", "red"), font=font)
            
            # Save annotated image
            annotated_path = screenshot_path.parent / f"annotated_{screenshot_path.name}"
            image.save(annotated_path)
            
            return annotated_path
            
        except Exception as e:
            self.logger.warning(f"Failed to annotate screenshot: {e}")
            return screenshot_path
    
    def _extract_payload_from_poc(self, poc_result: Dict[str, Any]) -> str:
        """Extract payload from PoC result"""
        # This would parse the PoC code to extract the actual payload
        poc_code = poc_result.get("poc_code", "")
        
        # Simple extraction - in reality this would be more sophisticated
        if "payload" in poc_code:
            # Extract payload from code
            lines = poc_code.split('\n')
            for line in lines:
                if 'payload' in line and '=' in line:
                    return line.split('=')[1].strip().strip('"\'')
        
        return "test_payload"
    
    def _analyze_network_traffic(self, har_path: Path, payload: str) -> Dict[str, Any]:
        """Analyze captured network traffic"""
        try:
            with open(har_path, 'r') as f:
                har_data = json.load(f)
            
            analysis = {
                "requests_captured": len(har_data.get("log", {}).get("entries", [])),
                "payload_found": False,
                "suspicious_responses": [],
                "security_headers_missing": []
            }
            
            # Analyze entries
            for entry in har_data.get("log", {}).get("entries", []):
                request = entry.get("request", {})
                response = entry.get("response", {})
                
                # Check if payload is in request
                if payload in str(request):
                    analysis["payload_found"] = True
                
                # Check response for suspicious content
                if response.get("status", 0) >= 400:
                    analysis["suspicious_responses"].append({
                        "status": response.get("status"),
                        "url": request.get("url")
                    })
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_security_headers(self, headers_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze security headers"""
        security_headers = [
            "content-security-policy",
            "x-frame-options",
            "x-content-type-options",
            "strict-transport-security",
            "x-xss-protection"
        ]
        
        analysis = {
            "missing_headers": [],
            "present_headers": [],
            "security_score": 0
        }
        
        if headers_data:
            headers = headers_data[0].get("headers", {})
            
            for header in security_headers:
                if header.lower() in [h.lower() for h in headers.keys()]:
                    analysis["present_headers"].append(header)
                    analysis["security_score"] += 20
                else:
                    analysis["missing_headers"].append(header)
        
        return analysis
    
    def _apply_evidence_reflection(self, evidence_collection: Dict[str, Any], vulnerability: Dict[str, Any]) -> List[str]:
        """Apply self-reflection to evidence collection"""
        reflection_questions = [
            "Does this video clearly show the vulnerability?",
            "Are screenshots annotated properly?",
            "Is the HAR log useful for reproduction?",
            "How can I improve evidence quality?"
        ]
        
        reflection_notes = []
        
        # Check evidence completeness
        successful_captures = len([e for e in evidence_collection.values() if e.get("success")])
        total_attempts = len(evidence_collection)
        
        if successful_captures < total_attempts * 0.8:
            reflection_notes.append("Evidence capture success rate is low - investigate failures")
        
        # Check for video evidence
        if "video_demonstration" not in evidence_collection or not evidence_collection["video_demonstration"].get("success"):
            reflection_notes.append("Video demonstration missing - critical for professional reports")
        
        # Check for network evidence
        if "network_traffic" not in evidence_collection or not evidence_collection["network_traffic"].get("success"):
            reflection_notes.append("Network traffic capture missing - important for technical analysis")
        
        return reflection_notes
    
    def _generate_evidence_summary(self, evidence_collection: Dict[str, Any], evidence_dir: Path) -> Dict[str, Any]:
        """Generate summary of collected evidence"""
        summary = {
            "total_evidence_types": len(evidence_collection),
            "successful_captures": len([e for e in evidence_collection.values() if e.get("success")]),
            "failed_captures": len([e for e in evidence_collection.values() if e.get("error")]),
            "evidence_directory": str(evidence_dir),
            "file_inventory": []
        }
        
        # Inventory all files
        for root, dirs, files in os.walk(evidence_dir):
            for file in files:
                file_path = Path(root) / file
                summary["file_inventory"].append({
                    "file": str(file_path.relative_to(evidence_dir)),
                    "size_bytes": file_path.stat().st_size,
                    "type": file_path.suffix
                })
        
        return summary
    
    def _calculate_evidence_quality(self, evidence_collection: Dict[str, Any]) -> float:
        """Calculate evidence quality score"""
        quality_weights = {
            "screenshot_before": 0.1,
            "screenshot_after": 0.2,
            "video_demonstration": 0.3,
            "network_traffic": 0.2,
            "curl_command": 0.1,
            "response_headers": 0.1
        }
        
        total_score = 0
        total_weight = 0
        
        for evidence_type, weight in quality_weights.items():
            if evidence_type in evidence_collection:
                if evidence_collection[evidence_type].get("success"):
                    total_score += weight
                total_weight += weight
        
        return round(total_score / total_weight if total_weight > 0 else 0, 2)
    
    async def _store_evidence_learning(self, evidence_result: Dict[str, Any], vulnerability: Dict[str, Any]):
        """Store evidence collection learning data"""
        learning_entry = {
            "vulnerability_type": vulnerability.get("type"),
            "evidence_quality_score": evidence_result["quality_score"],
            "successful_captures": evidence_result["evidence_summary"]["successful_captures"],
            "total_attempts": evidence_result["evidence_summary"]["total_evidence_types"],
            "reflection_notes": evidence_result["reflection_notes"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.learning_data.setdefault("evidence_sessions", []).append(learning_entry)
        
        # Save learning data
        learning_file = Path("learn/evidence_learning.json")
        learning_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save evidence learning data: {e}")