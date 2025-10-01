#!/usr/bin/env python3
"""
AEGIS-X Intelligence Engine
Web Intelligence Collection and Target Analysis
"""

import os
import json
import logging
import asyncio
import hashlib
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import requests
import httpx
from urllib.parse import urlparse, urljoin
import dns.resolver
import whois
import socket
import ssl
import subprocess

class IntelligenceEngine:
    """
    The Intelligence Engine gathers comprehensive intelligence on targets
    including web intelligence, dark web research, and vulnerability analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.IntelligenceEngine")
        self.intelligence_cache = self._load_intelligence_cache()
        
        # Intelligence gathering modules
        self.modules = {
            "web_intelligence": True,
            "dns_intelligence": True,
            "ssl_intelligence": True,
            "technology_detection": True,
            "vulnerability_research": True,
            "social_intelligence": True,
            "dark_web_research": False,  # Disabled by default for safety
            "threat_intelligence": True
        }
        
        # Known vulnerability databases
        self.vuln_databases = {
            "cve_database": "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=",
            "exploit_db": "https://www.exploit-db.com/search?q=",
            "nvd_database": "https://nvd.nist.gov/vuln/search/results?query="
        }
        
        self.logger.info("🕵️ Intelligence Engine initialized with comprehensive OSINT capabilities")
    
    def _load_intelligence_cache(self) -> Dict[str, Any]:
        """Load intelligence cache to avoid redundant lookups"""
        cache_file = Path("learn/intelligence_cache.json")
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load intelligence cache: {e}")
        
        return {
            "target_profiles": {},
            "technology_fingerprints": {},
            "vulnerability_intel": {},
            "dns_records": {},
            "ssl_certificates": {},
            "last_updated": {}
        }
    
    async def analyze_target(self, target: str) -> Dict[str, Any]:
        """
        Perform comprehensive intelligence analysis on a target
        """
        self.logger.info(f"🔍 Analyzing target intelligence: {target}")
        
        # Check cache first
        cache_key = self._generate_cache_key(target)
        if self._is_cache_valid(cache_key):
            self.logger.debug(f"Using cached intelligence for: {target}")
            return self.intelligence_cache["target_profiles"][cache_key]
        
        intelligence_report = {
            "target": target,
            "target_type": self._classify_target_type(target),
            "analysis_timestamp": datetime.now().isoformat(),
            "intelligence_modules": {},
            "risk_assessment": {},
            "recommendations": [],
            "confidence_score": 0.0
        }
        
        # Execute intelligence gathering modules
        if self.modules["web_intelligence"]:
            web_intel = await self._gather_web_intelligence(target)
            intelligence_report["intelligence_modules"]["web_intelligence"] = web_intel
        
        if self.modules["dns_intelligence"]:
            dns_intel = await self._gather_dns_intelligence(target)
            intelligence_report["intelligence_modules"]["dns_intelligence"] = dns_intel
        
        if self.modules["ssl_intelligence"]:
            ssl_intel = await self._gather_ssl_intelligence(target)
            intelligence_report["intelligence_modules"]["ssl_intelligence"] = ssl_intel
        
        if self.modules["technology_detection"]:
            tech_intel = await self._detect_technologies(target)
            intelligence_report["intelligence_modules"]["technology_detection"] = tech_intel
        
        if self.modules["vulnerability_research"]:
            vuln_intel = await self._research_vulnerabilities(target, intelligence_report)
            intelligence_report["intelligence_modules"]["vulnerability_research"] = vuln_intel
        
        if self.modules["social_intelligence"]:
            social_intel = await self._gather_social_intelligence(target)
            intelligence_report["intelligence_modules"]["social_intelligence"] = social_intel
        
        if self.modules["threat_intelligence"]:
            threat_intel = await self._gather_threat_intelligence(target)
            intelligence_report["intelligence_modules"]["threat_intelligence"] = threat_intel
        
        # Analyze and correlate intelligence
        intelligence_report["risk_assessment"] = self._assess_risk(intelligence_report)
        intelligence_report["recommendations"] = self._generate_recommendations(intelligence_report)
        intelligence_report["confidence_score"] = self._calculate_confidence_score(intelligence_report)
        
        # Cache the results
        self.intelligence_cache["target_profiles"][cache_key] = intelligence_report
        self.intelligence_cache["last_updated"][cache_key] = datetime.now().isoformat()
        
        await self._save_intelligence_cache()
        
        self.logger.info(f"✅ Intelligence analysis completed - Confidence: {intelligence_report['confidence_score']:.2f}")
        return intelligence_report
    
    async def _gather_web_intelligence(self, target: str) -> Dict[str, Any]:
        """Gather web-based intelligence"""
        self.logger.debug(f"🌐 Gathering web intelligence for: {target}")
        
        web_intel = {
            "http_headers": {},
            "robots_txt": "",
            "sitemap_xml": "",
            "security_headers": {},
            "cookies": [],
            "redirects": [],
            "subdomains": [],
            "linked_domains": [],
            "javascript_files": [],
            "api_endpoints": [],
            "forms": [],
            "comments": [],
            "metadata": {}
        }
        
        try:
            # Ensure target has protocol
            if not target.startswith(('http://', 'https://')):
                target_url = f"https://{target}"
            else:
                target_url = target
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # Get main page
                try:
                    response = await client.get(target_url)
                    
                    # Analyze HTTP headers
                    web_intel["http_headers"] = dict(response.headers)
                    web_intel["status_code"] = response.status_code
                    
                    # Analyze security headers
                    web_intel["security_headers"] = self._analyze_security_headers(response.headers)
                    
                    # Analyze cookies
                    web_intel["cookies"] = [
                        {"name": cookie.name, "domain": cookie.domain, "secure": cookie.secure, "httponly": cookie.get("httponly", False)}
                        for cookie in response.cookies
                    ]
                    
                    # Analyze page content
                    if response.text:
                        web_intel["javascript_files"] = self._extract_javascript_files(response.text, target_url)
                        web_intel["api_endpoints"] = self._extract_api_endpoints(response.text)
                        web_intel["forms"] = self._extract_forms(response.text)
                        web_intel["comments"] = self._extract_comments(response.text)
                        web_intel["metadata"] = self._extract_metadata(response.text)
                        web_intel["linked_domains"] = self._extract_linked_domains(response.text, target_url)
                
                except Exception as e:
                    self.logger.debug(f"Failed to analyze main page: {e}")
                
                # Get robots.txt
                try:
                    robots_response = await client.get(f"{target_url}/robots.txt")
                    if robots_response.status_code == 200:
                        web_intel["robots_txt"] = robots_response.text
                except Exception as e:
                    self.logger.debug(f"Failed to get robots.txt: {e}")
                
                # Get sitemap.xml
                try:
                    sitemap_response = await client.get(f"{target_url}/sitemap.xml")
                    if sitemap_response.status_code == 200:
                        web_intel["sitemap_xml"] = sitemap_response.text
                        web_intel["sitemap_urls"] = self._extract_sitemap_urls(sitemap_response.text)
                except Exception as e:
                    self.logger.debug(f"Failed to get sitemap.xml: {e}")
                
                # Subdomain enumeration (basic)
                web_intel["subdomains"] = await self._enumerate_subdomains(target)
        
        except Exception as e:
            self.logger.warning(f"Web intelligence gathering failed: {e}")
            web_intel["error"] = str(e)
        
        return web_intel
    
    async def _gather_dns_intelligence(self, target: str) -> Dict[str, Any]:
        """Gather DNS intelligence"""
        self.logger.debug(f"🌐 Gathering DNS intelligence for: {target}")
        
        dns_intel = {
            "a_records": [],
            "aaaa_records": [],
            "mx_records": [],
            "ns_records": [],
            "txt_records": [],
            "cname_records": [],
            "soa_record": {},
            "reverse_dns": {},
            "dns_security": {}
        }
        
        try:
            # Clean target (remove protocol and path)
            domain = urlparse(f"http://{target}").netloc or target
            domain = domain.split(':')[0]  # Remove port if present
            
            # A records
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                dns_intel["a_records"] = [str(record) for record in a_records]
            except Exception as e:
                self.logger.debug(f"Failed to get A records: {e}")
            
            # AAAA records (IPv6)
            try:
                aaaa_records = dns.resolver.resolve(domain, 'AAAA')
                dns_intel["aaaa_records"] = [str(record) for record in aaaa_records]
            except Exception as e:
                self.logger.debug(f"Failed to get AAAA records: {e}")
            
            # MX records
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                dns_intel["mx_records"] = [{"priority": record.preference, "exchange": str(record.exchange)} for record in mx_records]
            except Exception as e:
                self.logger.debug(f"Failed to get MX records: {e}")
            
            # NS records
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                dns_intel["ns_records"] = [str(record) for record in ns_records]
            except Exception as e:
                self.logger.debug(f"Failed to get NS records: {e}")
            
            # TXT records
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                dns_intel["txt_records"] = [str(record) for record in txt_records]
            except Exception as e:
                self.logger.debug(f"Failed to get TXT records: {e}")
            
            # SOA record
            try:
                soa_record = dns.resolver.resolve(domain, 'SOA')
                for record in soa_record:
                    dns_intel["soa_record"] = {
                        "mname": str(record.mname),
                        "rname": str(record.rname),
                        "serial": record.serial,
                        "refresh": record.refresh,
                        "retry": record.retry,
                        "expire": record.expire,
                        "minimum": record.minimum
                    }
                    break
            except Exception as e:
                self.logger.debug(f"Failed to get SOA record: {e}")
            
            # Reverse DNS lookup
            for ip in dns_intel["a_records"]:
                try:
                    reverse = dns.resolver.resolve_address(ip)
                    dns_intel["reverse_dns"][ip] = str(reverse[0])
                except Exception as e:
                    self.logger.debug(f"Failed reverse DNS for {ip}: {e}")
            
            # DNS security analysis
            dns_intel["dns_security"] = self._analyze_dns_security(dns_intel)
        
        except Exception as e:
            self.logger.warning(f"DNS intelligence gathering failed: {e}")
            dns_intel["error"] = str(e)
        
        return dns_intel
    
    async def _gather_ssl_intelligence(self, target: str) -> Dict[str, Any]:
        """Gather SSL/TLS intelligence"""
        self.logger.debug(f"🔒 Gathering SSL intelligence for: {target}")
        
        ssl_intel = {
            "certificate": {},
            "cipher_suites": [],
            "protocols": [],
            "vulnerabilities": [],
            "configuration_issues": [],
            "trust_chain": []
        }
        
        try:
            # Clean target
            domain = urlparse(f"http://{target}").netloc or target
            domain = domain.split(':')[0]
            port = 443
            
            # Get SSL certificate
            context = ssl.create_default_context()
            
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    ssl_intel["certificate"] = {
                        "subject": dict(x[0] for x in cert.get('subject', [])),
                        "issuer": dict(x[0] for x in cert.get('issuer', [])),
                        "version": cert.get('version'),
                        "serial_number": cert.get('serialNumber'),
                        "not_before": cert.get('notBefore'),
                        "not_after": cert.get('notAfter'),
                        "signature_algorithm": cert.get('signatureAlgorithm'),
                        "san": cert.get('subjectAltName', [])
                    }
                    
                    # Analyze certificate
                    ssl_intel["configuration_issues"] = self._analyze_ssl_certificate(cert)
                    
                    # Get cipher and protocol info
                    ssl_intel["cipher"] = ssock.cipher()
                    ssl_intel["protocol"] = ssock.version()
        
        except Exception as e:
            self.logger.debug(f"SSL intelligence gathering failed: {e}")
            ssl_intel["error"] = str(e)
        
        return ssl_intel
    
    async def _detect_technologies(self, target: str) -> Dict[str, Any]:
        """Detect technologies used by the target"""
        self.logger.debug(f"🔧 Detecting technologies for: {target}")
        
        tech_intel = {
            "web_server": "",
            "programming_languages": [],
            "frameworks": [],
            "cms": "",
            "javascript_libraries": [],
            "analytics": [],
            "cdn": "",
            "cloud_provider": "",
            "database": "",
            "operating_system": ""
        }
        
        try:
            if not target.startswith(('http://', 'https://')):
                target_url = f"https://{target}"
            else:
                target_url = target
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(target_url)
                
                # Analyze headers for technology indicators
                headers = response.headers
                
                # Web server detection
                if 'server' in headers:
                    tech_intel["web_server"] = headers['server']
                
                # X-Powered-By header
                if 'x-powered-by' in headers:
                    powered_by = headers['x-powered-by'].lower()
                    if 'php' in powered_by:
                        tech_intel["programming_languages"].append("PHP")
                    elif 'asp.net' in powered_by:
                        tech_intel["programming_languages"].append("ASP.NET")
                        tech_intel["frameworks"].append("ASP.NET")
                
                # Content analysis
                content = response.text.lower()
                
                # Framework detection
                framework_patterns = {
                    "react": [r"react", r"_react", r"reactdom"],
                    "angular": [r"angular", r"ng-"],
                    "vue": [r"vue\.js", r"vuejs"],
                    "jquery": [r"jquery", r"\$\("],
                    "bootstrap": [r"bootstrap"],
                    "wordpress": [r"wp-content", r"wordpress"],
                    "drupal": [r"drupal", r"sites/default"],
                    "joomla": [r"joomla", r"option=com_"]
                }
                
                for framework, patterns in framework_patterns.items():
                    if any(re.search(pattern, content) for pattern in patterns):
                        if framework in ["wordpress", "drupal", "joomla"]:
                            tech_intel["cms"] = framework
                        elif framework in ["react", "angular", "vue"]:
                            tech_intel["frameworks"].append(framework)
                        else:
                            tech_intel["javascript_libraries"].append(framework)
                
                # Analytics detection
                analytics_patterns = {
                    "google_analytics": [r"google-analytics", r"gtag\(", r"ga\("],
                    "facebook_pixel": [r"fbevents", r"facebook\.com/tr"],
                    "hotjar": [r"hotjar"],
                    "mixpanel": [r"mixpanel"]
                }
                
                for analytics, patterns in analytics_patterns.items():
                    if any(re.search(pattern, content) for pattern in patterns):
                        tech_intel["analytics"].append(analytics)
                
                # CDN detection
                cdn_headers = {
                    "cloudflare": ["cf-ray", "cf-cache-status"],
                    "fastly": ["fastly-debug-digest"],
                    "amazon_cloudfront": ["x-amz-cf-id"],
                    "akamai": ["akamai-origin-hop"]
                }
                
                for cdn, header_indicators in cdn_headers.items():
                    if any(header.lower() in headers for header in header_indicators):
                        tech_intel["cdn"] = cdn
                        break
                
                # Cloud provider detection
                if tech_intel["cdn"] == "amazon_cloudfront":
                    tech_intel["cloud_provider"] = "AWS"
                elif "x-goog" in str(headers):
                    tech_intel["cloud_provider"] = "Google Cloud"
                elif "x-azure" in str(headers):
                    tech_intel["cloud_provider"] = "Microsoft Azure"
        
        except Exception as e:
            self.logger.warning(f"Technology detection failed: {e}")
            tech_intel["error"] = str(e)
        
        return tech_intel
    
    async def _research_vulnerabilities(self, target: str, intelligence_report: Dict[str, Any]) -> Dict[str, Any]:
        """Research known vulnerabilities for detected technologies"""
        self.logger.debug(f"🔍 Researching vulnerabilities for: {target}")
        
        vuln_intel = {
            "known_cves": [],
            "exploit_availability": [],
            "security_advisories": [],
            "patch_status": {},
            "risk_score": 0.0
        }
        
        try:
            # Extract technologies from intelligence report
            tech_data = intelligence_report.get("intelligence_modules", {}).get("technology_detection", {})
            
            technologies = []
            if tech_data.get("web_server"):
                technologies.append(tech_data["web_server"])
            if tech_data.get("cms"):
                technologies.append(tech_data["cms"])
            technologies.extend(tech_data.get("frameworks", []))
            technologies.extend(tech_data.get("programming_languages", []))
            
            # Research each technology
            for tech in technologies:
                if tech:
                    tech_vulns = await self._search_vulnerabilities(tech)
                    if tech_vulns:
                        vuln_intel["known_cves"].extend(tech_vulns.get("cves", []))
                        vuln_intel["exploit_availability"].extend(tech_vulns.get("exploits", []))
            
            # Calculate risk score
            vuln_intel["risk_score"] = self._calculate_vulnerability_risk_score(vuln_intel)
        
        except Exception as e:
            self.logger.warning(f"Vulnerability research failed: {e}")
            vuln_intel["error"] = str(e)
        
        return vuln_intel
    
    async def _gather_social_intelligence(self, target: str) -> Dict[str, Any]:
        """Gather social intelligence (OSINT)"""
        self.logger.debug(f"👥 Gathering social intelligence for: {target}")
        
        social_intel = {
            "whois_data": {},
            "organization_info": {},
            "contact_information": {},
            "social_media_presence": [],
            "employee_information": [],
            "breach_history": [],
            "reputation_score": 0.0
        }
        
        try:
            # WHOIS lookup
            domain = urlparse(f"http://{target}").netloc or target
            domain = domain.split(':')[0]
            
            try:
                whois_data = whois.whois(domain)
                social_intel["whois_data"] = {
                    "registrar": whois_data.registrar,
                    "creation_date": str(whois_data.creation_date) if whois_data.creation_date else None,
                    "expiration_date": str(whois_data.expiration_date) if whois_data.expiration_date else None,
                    "name_servers": whois_data.name_servers,
                    "organization": whois_data.org,
                    "country": whois_data.country
                }
            except Exception as e:
                self.logger.debug(f"WHOIS lookup failed: {e}")
            
            # Organization information extraction
            if social_intel["whois_data"].get("organization"):
                social_intel["organization_info"]["name"] = social_intel["whois_data"]["organization"]
            
            # Basic reputation scoring
            social_intel["reputation_score"] = self._calculate_reputation_score(social_intel)
        
        except Exception as e:
            self.logger.warning(f"Social intelligence gathering failed: {e}")
            social_intel["error"] = str(e)
        
        return social_intel
    
    async def _gather_threat_intelligence(self, target: str) -> Dict[str, Any]:
        """Gather threat intelligence"""
        self.logger.debug(f"⚠️ Gathering threat intelligence for: {target}")
        
        threat_intel = {
            "malware_associations": [],
            "blacklist_status": {},
            "threat_feeds": [],
            "attack_patterns": [],
            "ioc_matches": [],
            "threat_score": 0.0
        }
        
        try:
            # Basic threat analysis
            domain = urlparse(f"http://{target}").netloc or target
            domain = domain.split(':')[0]
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP address instead of domain
                r'[a-z0-9]{20,}',  # Very long random strings
                r'\.tk$|\.ml$|\.ga$|\.cf$',  # Suspicious TLDs
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, domain):
                    threat_intel["attack_patterns"].append(f"Suspicious pattern: {pattern}")
            
            # Calculate threat score
            threat_intel["threat_score"] = len(threat_intel["attack_patterns"]) * 0.3
        
        except Exception as e:
            self.logger.warning(f"Threat intelligence gathering failed: {e}")
            threat_intel["error"] = str(e)
        
        return threat_intel
    
    async def _search_vulnerabilities(self, technology: str) -> Dict[str, Any]:
        """Search for vulnerabilities in a specific technology"""
        vuln_data = {"cves": [], "exploits": []}
        
        try:
            # This would integrate with actual vulnerability databases
            # For now, return mock data based on common vulnerabilities
            
            common_vulns = {
                "wordpress": [
                    {"cve": "CVE-2023-1234", "severity": "High", "description": "WordPress plugin vulnerability"},
                    {"cve": "CVE-2023-5678", "severity": "Medium", "description": "WordPress core vulnerability"}
                ],
                "apache": [
                    {"cve": "CVE-2023-9999", "severity": "Critical", "description": "Apache HTTP Server vulnerability"}
                ],
                "nginx": [
                    {"cve": "CVE-2023-8888", "severity": "Medium", "description": "Nginx vulnerability"}
                ]
            }
            
            tech_lower = technology.lower()
            for tech_name, vulns in common_vulns.items():
                if tech_name in tech_lower:
                    vuln_data["cves"].extend(vulns)
        
        except Exception as e:
            self.logger.debug(f"Vulnerability search failed for {technology}: {e}")
        
        return vuln_data
    
    async def _enumerate_subdomains(self, target: str) -> List[str]:
        """Basic subdomain enumeration"""
        subdomains = []
        
        try:
            domain = urlparse(f"http://{target}").netloc or target
            domain = domain.split(':')[0]
            
            # Common subdomain prefixes
            common_subdomains = [
                "www", "mail", "ftp", "admin", "api", "dev", "test", "staging",
                "blog", "shop", "store", "support", "help", "docs", "cdn",
                "static", "assets", "img", "images", "media", "files"
            ]
            
            for subdomain in common_subdomains:
                try:
                    full_subdomain = f"{subdomain}.{domain}"
                    # Try to resolve the subdomain
                    dns.resolver.resolve(full_subdomain, 'A')
                    subdomains.append(full_subdomain)
                except:
                    continue
        
        except Exception as e:
            self.logger.debug(f"Subdomain enumeration failed: {e}")
        
        return subdomains
    
    # Helper methods for content analysis
    def _analyze_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Analyze security headers"""
        security_analysis = {
            "content_security_policy": headers.get("content-security-policy"),
            "x_frame_options": headers.get("x-frame-options"),
            "x_content_type_options": headers.get("x-content-type-options"),
            "strict_transport_security": headers.get("strict-transport-security"),
            "x_xss_protection": headers.get("x-xss-protection"),
            "referrer_policy": headers.get("referrer-policy"),
            "security_score": 0
        }
        
        # Calculate security score
        security_headers = [
            "content-security-policy", "x-frame-options", "x-content-type-options",
            "strict-transport-security", "x-xss-protection"
        ]
        
        present_headers = sum(1 for header in security_headers if headers.get(header))
        security_analysis["security_score"] = (present_headers / len(security_headers)) * 100
        
        return security_analysis
    
    def _extract_javascript_files(self, content: str, base_url: str) -> List[str]:
        """Extract JavaScript file URLs"""
        js_files = []
        
        # Find script tags with src attributes
        script_pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
        matches = re.findall(script_pattern, content, re.IGNORECASE)
        
        for match in matches:
            if match.startswith('http'):
                js_files.append(match)
            else:
                js_files.append(urljoin(base_url, match))
        
        return js_files
    
    def _extract_api_endpoints(self, content: str) -> List[str]:
        """Extract potential API endpoints from content"""
        endpoints = []
        
        # Common API patterns
        api_patterns = [
            r'["\']([^"\']*/?api/[^"\']*)["\']',
            r'["\']([^"\']*/?v\d+/[^"\']*)["\']',
            r'["\']([^"\']*/?graphql[^"\']*)["\']',
            r'["\']([^"\']*/?rest/[^"\']*)["\']'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            endpoints.extend(matches)
        
        return list(set(endpoints))
    
    def _extract_forms(self, content: str) -> List[Dict[str, Any]]:
        """Extract form information"""
        forms = []
        
        form_pattern = r'<form[^>]*>(.*?)</form>'
        form_matches = re.findall(form_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for form_content in form_matches:
            form_info = {
                "inputs": [],
                "method": "GET",
                "action": ""
            }
            
            # Extract method and action
            method_match = re.search(r'method=["\']([^"\']+)["\']', form_content, re.IGNORECASE)
            if method_match:
                form_info["method"] = method_match.group(1).upper()
            
            action_match = re.search(r'action=["\']([^"\']+)["\']', form_content, re.IGNORECASE)
            if action_match:
                form_info["action"] = action_match.group(1)
            
            # Extract input fields
            input_pattern = r'<input[^>]*>'
            input_matches = re.findall(input_pattern, form_content, re.IGNORECASE)
            
            for input_tag in input_matches:
                input_info = {}
                
                name_match = re.search(r'name=["\']([^"\']+)["\']', input_tag, re.IGNORECASE)
                if name_match:
                    input_info["name"] = name_match.group(1)
                
                type_match = re.search(r'type=["\']([^"\']+)["\']', input_tag, re.IGNORECASE)
                if type_match:
                    input_info["type"] = type_match.group(1)
                
                if input_info:
                    form_info["inputs"].append(input_info)
            
            forms.append(form_info)
        
        return forms
    
    def _extract_comments(self, content: str) -> List[str]:
        """Extract HTML comments"""
        comment_pattern = r'<!--(.*?)-->'
        comments = re.findall(comment_pattern, content, re.DOTALL)
        return [comment.strip() for comment in comments if comment.strip()]
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from HTML"""
        metadata = {}
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            metadata["title"] = title_match.group(1).strip()
        
        # Extract meta tags
        meta_pattern = r'<meta[^>]+>'
        meta_matches = re.findall(meta_pattern, content, re.IGNORECASE)
        
        for meta_tag in meta_matches:
            name_match = re.search(r'name=["\']([^"\']+)["\']', meta_tag, re.IGNORECASE)
            content_match = re.search(r'content=["\']([^"\']+)["\']', meta_tag, re.IGNORECASE)
            
            if name_match and content_match:
                metadata[name_match.group(1)] = content_match.group(1)
        
        return metadata
    
    def _extract_linked_domains(self, content: str, base_url: str) -> List[str]:
        """Extract linked domains"""
        domains = set()
        
        # Extract all URLs
        url_pattern = r'https?://([^/\s"\'<>]+)'
        matches = re.findall(url_pattern, content, re.IGNORECASE)
        
        base_domain = urlparse(base_url).netloc
        
        for domain in matches:
            if domain != base_domain:
                domains.add(domain)
        
        return list(domains)
    
    def _extract_sitemap_urls(self, sitemap_content: str) -> List[str]:
        """Extract URLs from sitemap"""
        urls = []
        
        url_pattern = r'<loc>(.*?)</loc>'
        matches = re.findall(url_pattern, sitemap_content, re.IGNORECASE)
        
        return matches
    
    def _analyze_dns_security(self, dns_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze DNS security configuration"""
        security_analysis = {
            "spf_record": False,
            "dmarc_record": False,
            "dkim_record": False,
            "dnssec": False,
            "security_score": 0
        }
        
        txt_records = dns_data.get("txt_records", [])
        
        for record in txt_records:
            record_lower = record.lower()
            if record_lower.startswith("v=spf1"):
                security_analysis["spf_record"] = True
            elif record_lower.startswith("v=dmarc1"):
                security_analysis["dmarc_record"] = True
            elif "dkim" in record_lower:
                security_analysis["dkim_record"] = True
        
        # Calculate security score
        security_features = ["spf_record", "dmarc_record", "dkim_record", "dnssec"]
        present_features = sum(1 for feature in security_features if security_analysis[feature])
        security_analysis["security_score"] = (present_features / len(security_features)) * 100
        
        return security_analysis
    
    def _analyze_ssl_certificate(self, cert: Dict[str, Any]) -> List[str]:
        """Analyze SSL certificate for issues"""
        issues = []
        
        # Check expiration
        not_after = cert.get("notAfter")
        if not_after:
            try:
                from datetime import datetime
                expiry_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                days_until_expiry = (expiry_date - datetime.now()).days
                
                if days_until_expiry < 30:
                    issues.append(f"Certificate expires in {days_until_expiry} days")
            except:
                pass
        
        # Check for self-signed
        subject = cert.get("subject", {})
        issuer = cert.get("issuer", {})
        
        if subject == issuer:
            issues.append("Self-signed certificate")
        
        return issues
    
    def _calculate_vulnerability_risk_score(self, vuln_data: Dict[str, Any]) -> float:
        """Calculate vulnerability risk score"""
        score = 0.0
        
        cves = vuln_data.get("known_cves", [])
        
        for cve in cves:
            severity = cve.get("severity", "").lower()
            if severity == "critical":
                score += 1.0
            elif severity == "high":
                score += 0.7
            elif severity == "medium":
                score += 0.4
            elif severity == "low":
                score += 0.1
        
        return min(score, 10.0)  # Cap at 10
    
    def _calculate_reputation_score(self, social_data: Dict[str, Any]) -> float:
        """Calculate reputation score"""
        score = 5.0  # Start with neutral score
        
        whois_data = social_data.get("whois_data", {})
        
        # Positive factors
        if whois_data.get("organization"):
            score += 1.0
        
        if whois_data.get("creation_date"):
            # Older domains are generally more trustworthy
            try:
                from datetime import datetime
                creation_date = datetime.strptime(whois_data["creation_date"], "%Y-%m-%d %H:%M:%S")
                years_old = (datetime.now() - creation_date).days / 365
                score += min(years_old * 0.2, 2.0)
            except:
                pass
        
        return min(max(score, 0.0), 10.0)  # Keep between 0-10
    
    def _classify_target_type(self, target: str) -> str:
        """Classify the type of target"""
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', target):
            return "ip_address"
        elif target.startswith(('http://', 'https://')):
            return "web_url"
        elif '.' in target:
            return "domain"
        else:
            return "unknown"
    
    def _assess_risk(self, intelligence_report: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk based on intelligence"""
        risk_factors = []
        risk_score = 0.0
        
        # Analyze each intelligence module
        modules = intelligence_report.get("intelligence_modules", {})
        
        # Web intelligence risks
        web_intel = modules.get("web_intelligence", {})
        if web_intel.get("security_headers", {}).get("security_score", 100) < 50:
            risk_factors.append("Poor security header configuration")
            risk_score += 2.0
        
        # SSL risks
        ssl_intel = modules.get("ssl_intelligence", {})
        if ssl_intel.get("configuration_issues"):
            risk_factors.append("SSL/TLS configuration issues")
            risk_score += 1.5
        
        # Vulnerability risks
        vuln_intel = modules.get("vulnerability_research", {})
        vuln_risk = vuln_intel.get("risk_score", 0.0)
        if vuln_risk > 5.0:
            risk_factors.append("High vulnerability exposure")
            risk_score += vuln_risk
        
        # Threat intelligence risks
        threat_intel = modules.get("threat_intelligence", {})
        threat_score = threat_intel.get("threat_score", 0.0)
        if threat_score > 2.0:
            risk_factors.append("Threat intelligence indicators")
            risk_score += threat_score
        
        return {
            "risk_score": min(risk_score, 10.0),
            "risk_level": self._get_risk_level(risk_score),
            "risk_factors": risk_factors,
            "recommendations": self._get_risk_recommendations(risk_score, risk_factors)
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level from score"""
        if score >= 8.0:
            return "Critical"
        elif score >= 6.0:
            return "High"
        elif score >= 4.0:
            return "Medium"
        elif score >= 2.0:
            return "Low"
        else:
            return "Minimal"
    
    def _get_risk_recommendations(self, score: float, factors: List[str]) -> List[str]:
        """Get risk-based recommendations"""
        recommendations = []
        
        if "Poor security header configuration" in factors:
            recommendations.append("Implement comprehensive security headers (CSP, HSTS, X-Frame-Options)")
        
        if "SSL/TLS configuration issues" in factors:
            recommendations.append("Review and update SSL/TLS configuration")
        
        if "High vulnerability exposure" in factors:
            recommendations.append("Prioritize patching of identified vulnerabilities")
        
        if "Threat intelligence indicators" in factors:
            recommendations.append("Investigate threat intelligence indicators")
        
        if score >= 6.0:
            recommendations.append("Conduct immediate security assessment")
        
        return recommendations
    
    def _generate_recommendations(self, intelligence_report: Dict[str, Any]) -> List[str]:
        """Generate hunting recommendations based on intelligence"""
        recommendations = []
        
        modules = intelligence_report.get("intelligence_modules", {})
        
        # Technology-based recommendations
        tech_intel = modules.get("technology_detection", {})
        if tech_intel.get("cms"):
            recommendations.append(f"Focus on {tech_intel['cms']} specific vulnerabilities")
        
        if tech_intel.get("frameworks"):
            for framework in tech_intel["frameworks"]:
                recommendations.append(f"Test for {framework} framework vulnerabilities")
        
        # Web intelligence recommendations
        web_intel = modules.get("web_intelligence", {})
        if web_intel.get("api_endpoints"):
            recommendations.append("Test discovered API endpoints for vulnerabilities")
        
        if web_intel.get("forms"):
            recommendations.append("Test forms for injection vulnerabilities")
        
        if web_intel.get("subdomains"):
            recommendations.append("Expand testing to discovered subdomains")
        
        # Vulnerability research recommendations
        vuln_intel = modules.get("vulnerability_research", {})
        if vuln_intel.get("known_cves"):
            recommendations.append("Test for known CVEs in detected technologies")
        
        return recommendations
    
    def _calculate_confidence_score(self, intelligence_report: Dict[str, Any]) -> float:
        """Calculate confidence score for intelligence report"""
        modules = intelligence_report.get("intelligence_modules", {})
        
        successful_modules = 0
        total_modules = len(modules)
        
        for module_name, module_data in modules.items():
            if not module_data.get("error"):
                successful_modules += 1
        
        if total_modules == 0:
            return 0.0
        
        base_confidence = successful_modules / total_modules
        
        # Boost confidence based on data richness
        web_intel = modules.get("web_intelligence", {})
        if web_intel.get("subdomains") or web_intel.get("api_endpoints"):
            base_confidence += 0.1
        
        tech_intel = modules.get("technology_detection", {})
        if tech_intel.get("frameworks") or tech_intel.get("cms"):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _generate_cache_key(self, target: str) -> str:
        """Generate cache key for target"""
        return hashlib.md5(target.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str, max_age_hours: int = 24) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.intelligence_cache["target_profiles"]:
            return False
        
        last_updated = self.intelligence_cache["last_updated"].get(cache_key)
        if not last_updated:
            return False
        
        try:
            last_update_time = datetime.fromisoformat(last_updated)
            age = datetime.now() - last_update_time
            return age.total_seconds() < (max_age_hours * 3600)
        except:
            return False
    
    async def _save_intelligence_cache(self):
        """Save intelligence cache to file"""
        cache_file = Path("learn/intelligence_cache.json")
        cache_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.intelligence_cache, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save intelligence cache: {e}")
    
    def get_intelligence_stats(self) -> Dict[str, Any]:
        """Get intelligence gathering statistics"""
        return {
            "cached_targets": len(self.intelligence_cache["target_profiles"]),
            "cache_size_mb": self._calculate_cache_size(),
            "modules_enabled": sum(1 for enabled in self.modules.values() if enabled),
            "total_modules": len(self.modules),
            "last_analysis": max(self.intelligence_cache["last_updated"].values()) if self.intelligence_cache["last_updated"] else None
        }
    
    def _calculate_cache_size(self) -> float:
        """Calculate cache size in MB"""
        try:
            cache_str = json.dumps(self.intelligence_cache)
            return len(cache_str.encode('utf-8')) / (1024 * 1024)
        except:
            return 0.0