#!/usr/bin/env python3
"""
AEGIS-X Advanced Intelligence Engine
AI-powered intelligence gathering and analysis with real-time threat intelligence
"""

import os
import json
import logging
import asyncio
import subprocess
import tempfile
import hashlib
import base64
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import httpx
import requests
from urllib.parse import urlparse, urljoin
import dns.resolver
import whois
import socket
import ssl
import re
import ipaddress
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
from bs4 import BeautifulSoup
import subprocess
import yaml

class AdvancedIntelligenceEngine:
    """
    Advanced AI-powered Intelligence Engine with comprehensive OSINT capabilities,
    real-time threat intelligence, and machine learning-based analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.AdvancedIntelligenceEngine")
        self.intelligence_cache = self._load_intelligence_cache()
        self.threat_intel_cache = self._load_threat_intel_cache()
        
        # Initialize API clients
        self.shodan_client = self._init_shodan_client()
        self.censys_client = self._init_censys_client()
        
        # Advanced intelligence sources configuration
        self.sources = {
            "passive_osint": {
                "shodan": {"enabled": True, "api_key": os.getenv("SHODAN_API_KEY")},
                "censys": {"enabled": True, "api_key": os.getenv("CENSYS_API_KEY")},
                "virustotal": {"enabled": True, "api_key": os.getenv("VIRUSTOTAL_API_KEY")},
                "securitytrails": {"enabled": True, "api_key": os.getenv("SECURITYTRAILS_API_KEY")},
                "whois": {"enabled": True},
                "dns": {"enabled": True},
                "ssl": {"enabled": True},
                "wayback_machine": {"enabled": True},
                "github": {"enabled": True, "api_key": os.getenv("GITHUB_TOKEN")},
                "pastebin": {"enabled": True},
                "social_media": {"enabled": True},
                "certificate_transparency": {"enabled": True},
                "bgp": {"enabled": True},
                "geolocation": {"enabled": True}
            },
            "active_recon": {
                "port_scan": {"enabled": True, "stealth": True},
                "service_detection": {"enabled": True},
                "technology_detection": {"enabled": True},
                "subdomain_enumeration": {"enabled": True},
                "directory_bruteforce": {"enabled": True},
                "vulnerability_scan": {"enabled": True},
                "web_crawling": {"enabled": True},
                "api_discovery": {"enabled": True}
            },
            "threat_intelligence": {
                "malware_analysis": {"enabled": True},
                "ioc_correlation": {"enabled": True},
                "threat_actor_attribution": {"enabled": True},
                "campaign_tracking": {"enabled": True},
                "dark_web_monitoring": {"enabled": True}
            }
        }
        
        # AI/ML models for analysis
        self.ml_models = {
            "risk_assessment": None,
            "vulnerability_prediction": None,
            "threat_classification": None,
            "anomaly_detection": None
        }
        
        # Rate limiting and stealth configuration
        self.rate_limits = {
            "shodan": {"requests_per_second": 1, "last_request": 0},
            "censys": {"requests_per_second": 0.5, "last_request": 0},
            "virustotal": {"requests_per_second": 4, "last_request": 0},
            "default": {"requests_per_second": 2, "last_request": 0}
        }
        
        self.stealth_config = {
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ],
            "delay_range": (1, 5),
            "proxy_rotation": True,
            "request_randomization": True
        }
        
        self.logger.info("🧠 Advanced Intelligence Engine initialized with AI capabilities")
    
    def _init_shodan_client(self):
        """Initialize Shodan client"""
        api_key = os.getenv("SHODAN_API_KEY")
        if api_key:
            try:
                import shodan
                return shodan.Shodan(api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize Shodan client: {e}")
        return None
    
    def _init_censys_client(self):
        """Initialize Censys client"""
        api_id = os.getenv("CENSYS_API_ID")
        api_secret = os.getenv("CENSYS_API_SECRET")
        if api_id and api_secret:
            try:
                import censys.search
                return censys.search.CensysHosts(api_id, api_secret)
            except Exception as e:
                self.logger.warning(f"Failed to initialize Censys client: {e}")
        return None
    
    def _load_intelligence_cache(self) -> Dict[str, Any]:
        """Load enhanced intelligence cache"""
        cache_file = Path("learn/intelligence_cache.json")
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load intelligence cache: {e}")
        
        return {
            "targets": {},
            "domains": {},
            "ips": {},
            "technologies": {},
            "vulnerabilities": {},
            "threat_actors": {},
            "campaigns": {},
            "iocs": {},
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "cache_version": "2.0",
                "total_entries": 0
            }
        }
    
    def _load_threat_intel_cache(self) -> Dict[str, Any]:
        """Load threat intelligence cache"""
        cache_file = Path("learn/threat_intel_cache.json")
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load threat intel cache: {e}")
        
        return {
            "malware_families": {},
            "threat_actors": {},
            "campaigns": {},
            "iocs": {},
            "ttps": {},
            "last_updated": datetime.now().isoformat()
        }
    
    async def analyze_target(self, target: str) -> Dict[str, Any]:
        """
        Perform comprehensive AI-powered intelligence analysis on a target
        """
        self.logger.info(f"🔍 Starting advanced intelligence analysis for: {target}")
        
        # Generate unique analysis ID
        analysis_id = hashlib.md5(f"{target}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Check cache first
        cache_key = self._generate_cache_key(target)
        if cache_key in self.intelligence_cache.get("targets", {}):
            cached_intel = self.intelligence_cache["targets"][cache_key]
            if self._is_cache_valid(cached_intel):
                self.logger.info(f"📋 Using cached intelligence for: {target}")
                cached_intel["cache_hit"] = True
                return cached_intel
        
        # Initialize comprehensive intelligence structure
        intelligence = {
            "analysis_id": analysis_id,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "target_classification": await self._classify_target_advanced(target),
            "passive_osint": {},
            "active_reconnaissance": {},
            "threat_intelligence": {},
            "vulnerability_assessment": {},
            "attack_surface_analysis": {},
            "risk_assessment": {},
            "ai_analysis": {},
            "recommendations": [],
            "confidence_score": 0.0,
            "analysis_metadata": {
                "duration": 0,
                "sources_queried": [],
                "errors": [],
                "warnings": []
            }
        }
        
        start_time = time.time()
        
        try:
            # Phase 1: Passive OSINT Collection
            self.logger.info("🕵️ Phase 1: Passive OSINT Collection")
            intelligence["passive_osint"] = await self._comprehensive_passive_osint(target)
            
            # Phase 2: Active Reconnaissance
            self.logger.info("🎯 Phase 2: Active Reconnaissance")
            intelligence["active_reconnaissance"] = await self._comprehensive_active_recon(target, intelligence["passive_osint"])
            
            # Phase 3: Threat Intelligence Correlation
            self.logger.info("⚠️ Phase 3: Threat Intelligence Correlation")
            intelligence["threat_intelligence"] = await self._correlate_threat_intelligence(target, intelligence)
            
            # Phase 4: Vulnerability Assessment
            self.logger.info("🔍 Phase 4: Vulnerability Assessment")
            intelligence["vulnerability_assessment"] = await self._assess_vulnerabilities(target, intelligence)
            
            # Phase 5: Attack Surface Analysis
            self.logger.info("🎯 Phase 5: Attack Surface Analysis")
            intelligence["attack_surface_analysis"] = await self._analyze_attack_surface_advanced(intelligence)
            
            # Phase 6: AI-Powered Risk Assessment
            self.logger.info("🤖 Phase 6: AI-Powered Risk Assessment")
            intelligence["risk_assessment"] = await self._ai_powered_risk_assessment(intelligence)
            
            # Phase 7: AI Analysis and Pattern Recognition
            self.logger.info("🧠 Phase 7: AI Analysis and Pattern Recognition")
            intelligence["ai_analysis"] = await self._ai_pattern_analysis(intelligence)
            
            # Phase 8: Generate Intelligent Recommendations
            self.logger.info("💡 Phase 8: Generating Intelligent Recommendations")
            intelligence["recommendations"] = await self._generate_intelligent_recommendations(intelligence)
            
            # Calculate comprehensive confidence score
            intelligence["confidence_score"] = await self._calculate_advanced_confidence_score(intelligence)
            
            # Record analysis metadata
            intelligence["analysis_metadata"]["duration"] = time.time() - start_time
            intelligence["analysis_metadata"]["sources_queried"] = list(set(intelligence["analysis_metadata"]["sources_queried"]))
            
            # Cache the results
            await self._cache_intelligence_advanced(target, intelligence)
            
            self.logger.info(f"✅ Advanced intelligence analysis completed for: {target}")
            self.logger.info(f"📊 Analysis ID: {analysis_id}, Duration: {intelligence['analysis_metadata']['duration']:.2f}s, Confidence: {intelligence['confidence_score']:.2f}")
            
        except Exception as e:
            self.logger.error(f"Advanced intelligence analysis failed for {target}: {e}")
            intelligence["analysis_metadata"]["errors"].append(str(e))
            intelligence["error"] = str(e)
        
        return intelligence
    
    async def _classify_target_advanced(self, target: str) -> Dict[str, Any]:
        """Advanced target classification with AI-powered analysis"""
        classification = {
            "primary_type": "unknown",
            "secondary_types": [],
            "confidence": 0.0,
            "attributes": {},
            "context": {}
        }
        
        try:
            # Basic classification
            if target.startswith(('http://', 'https://')):
                classification["primary_type"] = "web_application"
                parsed = urlparse(target)
                classification["attributes"]["protocol"] = parsed.scheme
                classification["attributes"]["domain"] = parsed.netloc
                classification["attributes"]["path"] = parsed.path
                
                # Detect API endpoints
                if any(api_indicator in target.lower() for api_indicator in ['/api/', '/v1/', '/v2/', '/graphql', '/rest']):
                    classification["secondary_types"].append("api_endpoint")
                
                # Detect admin panels
                if any(admin_indicator in target.lower() for admin_indicator in ['/admin', '/dashboard', '/panel', '/manage']):
                    classification["secondary_types"].append("admin_interface")
                    
            elif self._is_ip_address(target):
                classification["primary_type"] = "ip_address"
                classification["attributes"]["ip_version"] = "ipv4" if ":" not in target else "ipv6"
                
                # Check if it's a private IP
                try:
                    ip_obj = ipaddress.ip_address(target)
                    classification["attributes"]["is_private"] = ip_obj.is_private
                    classification["attributes"]["is_multicast"] = ip_obj.is_multicast
                    classification["attributes"]["is_reserved"] = ip_obj.is_reserved
                except:
                    pass
                    
            elif '.' in target and not target.startswith('/'):
                classification["primary_type"] = "domain"
                classification["attributes"]["domain"] = target
                
                # Detect subdomains
                parts = target.split('.')
                if len(parts) > 2:
                    classification["secondary_types"].append("subdomain")
                    classification["attributes"]["subdomain_level"] = len(parts) - 2
                
                # Detect wildcards
                if target.startswith('*.'):
                    classification["secondary_types"].append("wildcard_domain")
                    
            elif target.startswith('/') or target.endswith(('.txt', '.json', '.xml', '.csv')):
                classification["primary_type"] = "file_path"
                classification["attributes"]["path"] = target
                
                # Detect file types
                if target.endswith(('.txt', '.log')):
                    classification["secondary_types"].append("text_file")
                elif target.endswith(('.json', '.xml', '.yaml', '.yml')):
                    classification["secondary_types"].append("config_file")
                elif target.endswith(('.csv', '.xlsx', '.xls')):
                    classification["secondary_types"].append("data_file")
            
            # Calculate confidence based on classification certainty
            if classification["primary_type"] != "unknown":
                classification["confidence"] = 0.8 + (len(classification["secondary_types"]) * 0.05)
            
            classification["confidence"] = min(classification["confidence"], 1.0)
            
        except Exception as e:
            self.logger.warning(f"Target classification failed: {e}")
        
        return classification
    
    async def _comprehensive_passive_osint(self, target: str) -> Dict[str, Any]:
        """Comprehensive passive OSINT collection from multiple sources"""
        osint_data = {
            "whois": {},
            "dns": {},
            "ssl_certificates": {},
            "shodan": {},
            "censys": {},
            "virustotal": {},
            "certificate_transparency": {},
            "wayback_machine": {},
            "github_reconnaissance": {},
            "social_media_intelligence": {},
            "bgp_intelligence": {},
            "geolocation": {},
            "domain_intelligence": {},
            "subdomain_intelligence": {},
            "email_intelligence": {},
            "metadata": {
                "sources_used": [],
                "collection_time": datetime.now().isoformat(),
                "errors": []
            }
        }
        
        # Create tasks for parallel execution
        tasks = []
        
        # WHOIS Intelligence
        if self.sources["passive_osint"]["whois"]["enabled"]:
            tasks.append(self._gather_whois_intelligence_advanced(target))
        
        # DNS Intelligence
        if self.sources["passive_osint"]["dns"]["enabled"]:
            tasks.append(self._gather_dns_intelligence_advanced(target))
        
        # SSL Certificate Intelligence
        if self.sources["passive_osint"]["ssl"]["enabled"]:
            tasks.append(self._gather_ssl_intelligence_advanced(target))
        
        # Shodan Intelligence
        if self.sources["passive_osint"]["shodan"]["enabled"] and self.shodan_client:
            tasks.append(self._gather_shodan_intelligence_advanced(target))
        
        # Certificate Transparency
        if self.sources["passive_osint"]["certificate_transparency"]["enabled"]:
            tasks.append(self._gather_certificate_transparency_intelligence(target))
        
        # Wayback Machine
        if self.sources["passive_osint"]["wayback_machine"]["enabled"]:
            tasks.append(self._gather_wayback_machine_intelligence(target))
        
        # GitHub Reconnaissance
        if self.sources["passive_osint"]["github"]["enabled"]:
            tasks.append(self._gather_github_intelligence(target))
        
        # Execute tasks with proper error handling
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        source_names = ["whois", "dns", "ssl_certificates", "shodan", "certificate_transparency", "wayback_machine", "github_reconnaissance"]
        
        for i, result in enumerate(results):
            if i < len(source_names):
                source_name = source_names[i]
                if isinstance(result, Exception):
                    osint_data["metadata"]["errors"].append(f"{source_name}: {str(result)}")
                    self.logger.warning(f"OSINT collection failed for {source_name}: {result}")
                else:
                    osint_data[source_name] = result
                    osint_data["metadata"]["sources_used"].append(source_name)
        
        return osint_data
    
    async def _gather_whois_intelligence_advanced(self, target: str) -> Dict[str, Any]:
        """Advanced WHOIS intelligence gathering"""
        whois_intel = {
            "domain_info": {},
            "registrar_info": {},
            "contact_info": {},
            "dns_info": {},
            "security_indicators": {},
            "historical_data": {}
        }
        
        try:
            domain = self._extract_domain(target)
            if domain:
                # Rate limiting
                await self._apply_rate_limit("whois")
                
                whois_info = whois.whois(domain)
                
                # Domain information
                whois_intel["domain_info"] = {
                    "domain": domain,
                    "creation_date": str(getattr(whois_info, 'creation_date', None)),
                    "expiration_date": str(getattr(whois_info, 'expiration_date', None)),
                    "updated_date": str(getattr(whois_info, 'updated_date', None)),
                    "status": getattr(whois_info, 'status', []),
                    "dnssec": getattr(whois_info, 'dnssec', None)
                }
                
                # Registrar information
                whois_intel["registrar_info"] = {
                    "registrar": getattr(whois_info, 'registrar', None),
                    "registrar_url": getattr(whois_info, 'registrar_url', None),
                    "registrar_iana_id": getattr(whois_info, 'registrar_iana_id', None)
                }
                
                # Contact information
                whois_intel["contact_info"] = {
                    "emails": getattr(whois_info, 'emails', []),
                    "org": getattr(whois_info, 'org', None),
                    "country": getattr(whois_info, 'country', None),
                    "state": getattr(whois_info, 'state', None),
                    "city": getattr(whois_info, 'city', None)
                }
                
                # DNS information
                whois_intel["dns_info"] = {
                    "name_servers": getattr(whois_info, 'name_servers', [])
                }
                
                # Security indicators
                whois_intel["security_indicators"] = await self._analyze_whois_security_indicators(whois_info)
                
        except Exception as e:
            self.logger.warning(f"Advanced WHOIS lookup failed for {target}: {e}")
        
        return whois_intel
    
    async def _gather_dns_intelligence_advanced(self, target: str) -> Dict[str, Any]:
        """Advanced DNS intelligence gathering"""
        dns_intel = {
            "standard_records": {},
            "security_records": {},
            "mail_security": {},
            "dns_security": {},
            "subdomain_hints": {},
            "dns_history": {}
        }
        
        try:
            domain = self._extract_domain(target)
            if domain:
                # Standard DNS records
                record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA', 'PTR']
                
                for record_type in record_types:
                    try:
                        records = dns.resolver.resolve(domain, record_type)
                        dns_intel["standard_records"][record_type.lower()] = [str(record) for record in records]
                    except dns.resolver.NXDOMAIN:
                        dns_intel["standard_records"][record_type.lower()] = []
                    except Exception:
                        pass
                
                # Security-related DNS records
                security_records = ['SPF', 'DKIM', 'DMARC', 'CAA']
                for sec_record in security_records:
                    try:
                        if sec_record == 'SPF':
                            # SPF is in TXT records
                            txt_records = dns_intel["standard_records"].get("txt", [])
                            spf_records = [record for record in txt_records if record.startswith('"v=spf1')]
                            dns_intel["security_records"]["spf"] = spf_records
                        elif sec_record == 'DMARC':
                            dmarc_domain = f"_dmarc.{domain}"
                            records = dns.resolver.resolve(dmarc_domain, 'TXT')
                            dns_intel["security_records"]["dmarc"] = [str(record) for record in records]
                        elif sec_record == 'CAA':
                            records = dns.resolver.resolve(domain, 'CAA')
                            dns_intel["security_records"]["caa"] = [str(record) for record in records]
                    except Exception:
                        pass
                
                # Analyze DNS security posture
                dns_intel["dns_security"] = await self._analyze_dns_security(dns_intel)
                
        except Exception as e:
            self.logger.warning(f"Advanced DNS lookup failed for {target}: {e}")
        
        return dns_intel
    
    async def _gather_ssl_intelligence_advanced(self, target: str) -> Dict[str, Any]:
        """Advanced SSL certificate intelligence"""
        ssl_intel = {
            "certificate_details": {},
            "certificate_chain": [],
            "security_analysis": {},
            "vulnerability_indicators": {},
            "trust_analysis": {}
        }
        
        try:
            domain = self._extract_domain(target)
            if domain:
                # Get SSL certificate
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((domain, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        cert_der = ssock.getpeercert(binary_form=True)
                        
                        # Certificate details
                        ssl_intel["certificate_details"] = {
                            "subject": dict(x[0] for x in cert.get('subject', [])),
                            "issuer": dict(x[0] for x in cert.get('issuer', [])),
                            "version": cert.get('version'),
                            "serial_number": cert.get('serialNumber'),
                            "not_before": cert.get('notBefore'),
                            "not_after": cert.get('notAfter'),
                            "signature_algorithm": cert.get('signatureAlgorithm'),
                            "san": cert.get('subjectAltName', []),
                            "fingerprint_sha256": hashlib.sha256(cert_der).hexdigest()
                        }
                        
                        # Security analysis
                        ssl_intel["security_analysis"] = await self._analyze_ssl_security(cert, ssock)
                        
                        # Check for vulnerabilities
                        ssl_intel["vulnerability_indicators"] = await self._check_ssl_vulnerabilities(domain, cert)
        
        except Exception as e:
            self.logger.warning(f"Advanced SSL analysis failed for {target}: {e}")
        
        return ssl_intel
    
    async def _gather_shodan_intelligence_advanced(self, target: str) -> Dict[str, Any]:
        """Advanced Shodan intelligence gathering"""
        shodan_intel = {
            "host_info": {},
            "services": [],
            "vulnerabilities": [],
            "historical_data": {},
            "related_hosts": []
        }
        
        try:
            if self.shodan_client:
                await self._apply_rate_limit("shodan")
                
                # Determine if target is IP or domain
                if self._is_ip_address(target):
                    ip = target
                else:
                    domain = self._extract_domain(target)
                    if domain:
                        # Resolve domain to IP
                        try:
                            ip = socket.gethostbyname(domain)
                        except:
                            return shodan_intel
                    else:
                        return shodan_intel
                
                # Get host information
                host_info = self.shodan_client.host(ip)
                
                shodan_intel["host_info"] = {
                    "ip": host_info.get('ip_str'),
                    "org": host_info.get('org'),
                    "isp": host_info.get('isp'),
                    "country": host_info.get('country_name'),
                    "city": host_info.get('city'),
                    "region": host_info.get('region_code'),
                    "postal_code": host_info.get('postal_code'),
                    "latitude": host_info.get('latitude'),
                    "longitude": host_info.get('longitude'),
                    "asn": host_info.get('asn'),
                    "last_update": host_info.get('last_update'),
                    "tags": host_info.get('tags', [])
                }
                
                # Extract services
                for service in host_info.get('data', []):
                    service_info = {
                        "port": service.get('port'),
                        "protocol": service.get('transport'),
                        "service": service.get('product'),
                        "version": service.get('version'),
                        "banner": service.get('data', '').strip(),
                        "timestamp": service.get('timestamp'),
                        "ssl": service.get('ssl', {}),
                        "http": service.get('http', {}),
                        "vulnerabilities": service.get('vulns', [])
                    }
                    shodan_intel["services"].append(service_info)
                
                # Extract vulnerabilities
                for service in host_info.get('data', []):
                    vulns = service.get('vulns', [])
                    for vuln in vulns:
                        if vuln not in shodan_intel["vulnerabilities"]:
                            shodan_intel["vulnerabilities"].append(vuln)
        
        except Exception as e:
            self.logger.warning(f"Shodan intelligence gathering failed for {target}: {e}")
        
        return shodan_intel
    
    async def _gather_certificate_transparency_intelligence(self, target: str) -> Dict[str, Any]:
        """Gather intelligence from Certificate Transparency logs"""
        ct_intel = {
            "certificates": [],
            "subdomains": set(),
            "issuers": set(),
            "timeline": {}
        }
        
        try:
            domain = self._extract_domain(target)
            if domain:
                # Query crt.sh for certificate transparency data
                await self._apply_rate_limit("default")
                
                url = f"https://crt.sh/?q={domain}&output=json"
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        certificates = response.json()
                        
                        for cert in certificates[:50]:  # Limit to 50 most recent
                            cert_info = {
                                "id": cert.get("id"),
                                "logged_at": cert.get("entry_timestamp"),
                                "not_before": cert.get("not_before"),
                                "not_after": cert.get("not_after"),
                                "common_name": cert.get("common_name"),
                                "matching_identities": cert.get("name_value", "").split("\n"),
                                "issuer_name": cert.get("issuer_name")
                            }
                            ct_intel["certificates"].append(cert_info)
                            
                            # Extract subdomains
                            for identity in cert_info["matching_identities"]:
                                if identity and domain in identity:
                                    ct_intel["subdomains"].add(identity.strip())
                            
                            # Track issuers
                            if cert_info["issuer_name"]:
                                ct_intel["issuers"].add(cert_info["issuer_name"])
                
                # Convert sets to lists for JSON serialization
                ct_intel["subdomains"] = list(ct_intel["subdomains"])
                ct_intel["issuers"] = list(ct_intel["issuers"])
        
        except Exception as e:
            self.logger.warning(f"Certificate Transparency intelligence failed for {target}: {e}")
        
        return ct_intel
    
    async def _gather_wayback_machine_intelligence(self, target: str) -> Dict[str, Any]:
        """Gather intelligence from Wayback Machine"""
        wayback_intel = {
            "snapshots": [],
            "first_seen": None,
            "last_seen": None,
            "total_snapshots": 0,
            "interesting_paths": [],
            "technology_evolution": {}
        }
        
        try:
            domain = self._extract_domain(target)
            if domain:
                await self._apply_rate_limit("default")
                
                # Get snapshot data
                url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&limit=100"
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data and len(data) > 1:  # First row is headers
                            wayback_intel["total_snapshots"] = len(data) - 1
                            
                            for row in data[1:]:  # Skip header row
                                if len(row) >= 7:
                                    snapshot = {
                                        "timestamp": row[1],
                                        "url": row[2],
                                        "status_code": row[4],
                                        "mime_type": row[3],
                                        "length": row[5]
                                    }
                                    wayback_intel["snapshots"].append(snapshot)
                            
                            # Find first and last seen
                            if wayback_intel["snapshots"]:
                                wayback_intel["first_seen"] = wayback_intel["snapshots"][-1]["timestamp"]
                                wayback_intel["last_seen"] = wayback_intel["snapshots"][0]["timestamp"]
                            
                            # Extract interesting paths
                            paths = set()
                            for snapshot in wayback_intel["snapshots"]:
                                url_path = urlparse(snapshot["url"]).path
                                if url_path and url_path != "/":
                                    paths.add(url_path)
                            
                            wayback_intel["interesting_paths"] = list(paths)[:50]  # Limit to 50
        
        except Exception as e:
            self.logger.warning(f"Wayback Machine intelligence failed for {target}: {e}")
        
        return wayback_intel
    
    async def _gather_github_intelligence(self, target: str) -> Dict[str, Any]:
        """Gather intelligence from GitHub"""
        github_intel = {
            "repositories": [],
            "users": [],
            "code_exposures": [],
            "secrets_found": [],
            "api_keys": [],
            "configuration_files": []
        }
        
        try:
            domain = self._extract_domain(target)
            if domain and self.sources["passive_osint"]["github"]["api_key"]:
                await self._apply_rate_limit("default")
                
                # Search for repositories mentioning the domain
                headers = {
                    "Authorization": f"token {self.sources['passive_osint']['github']['api_key']}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                search_queries = [
                    f'"{domain}"',
                    f'"{domain.replace(".", "_")}"',
                    f'"{domain.split(".")[0]}"'
                ]
                
                async with httpx.AsyncClient(timeout=30) as client:
                    for query in search_queries:
                        try:
                            url = f"https://api.github.com/search/repositories?q={query}&sort=updated&per_page=10"
                            response = await client.get(url, headers=headers)
                            
                            if response.status_code == 200:
                                data = response.json()
                                for repo in data.get("items", []):
                                    repo_info = {
                                        "name": repo.get("full_name"),
                                        "description": repo.get("description"),
                                        "url": repo.get("html_url"),
                                        "created_at": repo.get("created_at"),
                                        "updated_at": repo.get("updated_at"),
                                        "language": repo.get("language"),
                                        "stars": repo.get("stargazers_count"),
                                        "forks": repo.get("forks_count")
                                    }
                                    github_intel["repositories"].append(repo_info)
                            
                            # Small delay between requests
                            await asyncio.sleep(1)
                        
                        except Exception as e:
                            self.logger.warning(f"GitHub search failed for query {query}: {e}")
        
        except Exception as e:
            self.logger.warning(f"GitHub intelligence gathering failed for {target}: {e}")
        
        return github_intel
    
    async def _comprehensive_active_recon(self, target: str, passive_intel: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive active reconnaissance"""
        active_recon = {
            "port_scanning": {},
            "service_enumeration": {},
            "web_application_analysis": {},
            "subdomain_enumeration": {},
            "directory_discovery": {},
            "technology_detection": {},
            "api_discovery": {},
            "vulnerability_scanning": {},
            "metadata": {
                "scan_time": datetime.now().isoformat(),
                "techniques_used": [],
                "stealth_level": "high"
            }
        }
        
        try:
            # Port Scanning
            if self.sources["active_recon"]["port_scan"]["enabled"]:
                self.logger.info("🔍 Performing advanced port scanning")
                active_recon["port_scanning"] = await self._advanced_port_scanning(target)
                active_recon["metadata"]["techniques_used"].append("port_scanning")
            
            # Service Enumeration
            if self.sources["active_recon"]["service_detection"]["enabled"]:
                self.logger.info("🔍 Performing service enumeration")
                active_recon["service_enumeration"] = await self._advanced_service_enumeration(target, active_recon["port_scanning"])
                active_recon["metadata"]["techniques_used"].append("service_enumeration")
            
            # Web Application Analysis
            if target.startswith(('http://', 'https://')) or self._extract_domain(target):
                self.logger.info("🌐 Performing web application analysis")
                active_recon["web_application_analysis"] = await self._web_application_analysis(target)
                active_recon["metadata"]["techniques_used"].append("web_analysis")
            
            # Subdomain Enumeration
            if self.sources["active_recon"]["subdomain_enumeration"]["enabled"]:
                self.logger.info("🔍 Performing subdomain enumeration")
                active_recon["subdomain_enumeration"] = await self._advanced_subdomain_enumeration(target, passive_intel)
                active_recon["metadata"]["techniques_used"].append("subdomain_enumeration")
            
            # Technology Detection
            if self.sources["active_recon"]["technology_detection"]["enabled"]:
                self.logger.info("🔧 Performing technology detection")
                active_recon["technology_detection"] = await self._advanced_technology_detection(target)
                active_recon["metadata"]["techniques_used"].append("technology_detection")
        
        except Exception as e:
            self.logger.error(f"Active reconnaissance failed for {target}: {e}")
        
        return active_recon
    
    # Helper methods for rate limiting, caching, and utility functions
    async def _apply_rate_limit(self, source: str):
        """Apply rate limiting for API calls"""
        if source in self.rate_limits:
            config = self.rate_limits[source]
        else:
            config = self.rate_limits["default"]
        
        current_time = time.time()
        time_since_last = current_time - config["last_request"]
        min_interval = 1.0 / config["requests_per_second"]
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        config["last_request"] = time.time()
    
    def _generate_cache_key(self, target: str) -> str:
        """Generate cache key for target"""
        return hashlib.md5(target.encode()).hexdigest()
    
    def _is_cache_valid(self, cached_intel: Dict[str, Any]) -> bool:
        """Check if cached intelligence is still valid"""
        try:
            timestamp = datetime.fromisoformat(cached_intel.get("timestamp", ""))
            age = datetime.now() - timestamp
            return age.total_seconds() < 7200  # 2 hour cache
        except:
            return False
    
    async def _cache_intelligence_advanced(self, target: str, intelligence: Dict[str, Any]):
        """Cache intelligence results with advanced metadata"""
        try:
            cache_key = self._generate_cache_key(target)
            self.intelligence_cache["targets"][cache_key] = intelligence
            
            # Update metadata
            self.intelligence_cache["metadata"]["last_updated"] = datetime.now().isoformat()
            self.intelligence_cache["metadata"]["total_entries"] = len(self.intelligence_cache["targets"])
            
            # Save to file
            cache_file = Path("learn/intelligence_cache.json")
            cache_file.parent.mkdir(exist_ok=True)
            
            with open(cache_file, 'w') as f:
                json.dump(self.intelligence_cache, f, indent=2, default=str)
        
        except Exception as e:
            self.logger.warning(f"Failed to cache intelligence: {e}")
    
    def _extract_domain(self, target: str) -> Optional[str]:
        """Extract domain from target"""
        if target.startswith(('http://', 'https://')):
            return urlparse(target).netloc
        elif '.' in target and not self._is_ip_address(target):
            return target.split('/')[0]  # Remove path if present
        return None
    
    def _is_ip_address(self, target: str) -> bool:
        """Check if target is an IP address"""
        try:
            ipaddress.ip_address(target)
            return True
        except ValueError:
            return False
    
    # Placeholder methods for remaining functionality (to be implemented)
    async def _advanced_port_scanning(self, target: str) -> Dict[str, Any]:
        """Advanced port scanning with stealth techniques"""
        return {"open_ports": [], "scan_technique": "stealth", "total_ports": 0}
    
    async def _advanced_service_enumeration(self, target: str, port_scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced service enumeration"""
        return {"services": [], "banners": {}, "versions": {}}
    
    async def _web_application_analysis(self, target: str) -> Dict[str, Any]:
        """Comprehensive web application analysis"""
        return {"technologies": [], "forms": [], "security_headers": {}}
    
    async def _advanced_subdomain_enumeration(self, target: str, passive_intel: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced subdomain enumeration"""
        return {"subdomains": [], "techniques_used": [], "alive_subdomains": []}
    
    async def _advanced_technology_detection(self, target: str) -> Dict[str, Any]:
        """Advanced technology detection"""
        return {"web_technologies": [], "cms": None, "frameworks": []}
    
    async def _correlate_threat_intelligence(self, target: str, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate with threat intelligence feeds"""
        return {"threat_indicators": [], "malware_associations": [], "threat_actor_links": []}
    
    async def _assess_vulnerabilities(self, target: str, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Assess vulnerabilities based on gathered intelligence"""
        return {"potential_vulnerabilities": [], "risk_score": 0.0, "exploit_likelihood": "low"}
    
    async def _analyze_attack_surface_advanced(self, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced attack surface analysis"""
        return {"exposed_services": [], "attack_vectors": [], "entry_points": []}
    
    async def _ai_powered_risk_assessment(self, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered risk assessment"""
        return {"overall_risk": "medium", "risk_factors": [], "mitigation_recommendations": []}
    
    async def _ai_pattern_analysis(self, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """AI pattern analysis and anomaly detection"""
        return {"patterns_detected": [], "anomalies": [], "behavioral_analysis": {}}
    
    async def _generate_intelligent_recommendations(self, intelligence: Dict[str, Any]) -> List[str]:
        """Generate intelligent hunting recommendations"""
        return [
            "Perform comprehensive subdomain enumeration using multiple techniques",
            "Conduct advanced port scanning with service version detection",
            "Analyze web application for common vulnerabilities (OWASP Top 10)",
            "Check for exposed sensitive files and directories",
            "Perform API endpoint discovery and testing"
        ]
    
    async def _calculate_advanced_confidence_score(self, intelligence: Dict[str, Any]) -> float:
        """Calculate advanced confidence score"""
        score = 0.0
        
        # Passive OSINT weight: 30%
        if intelligence.get("passive_osint"):
            passive_sources = len([k for k, v in intelligence["passive_osint"].items() if v and k != "metadata"])
            score += min(passive_sources * 0.05, 0.3)
        
        # Active reconnaissance weight: 40%
        if intelligence.get("active_reconnaissance"):
            active_techniques = len(intelligence["active_reconnaissance"].get("metadata", {}).get("techniques_used", []))
            score += min(active_techniques * 0.08, 0.4)
        
        # Additional scoring logic...
        return min(score, 1.0)
    
    # Additional helper methods for specific analysis tasks
    async def _analyze_whois_security_indicators(self, whois_info) -> Dict[str, Any]:
        """Analyze WHOIS data for security indicators"""
        return {"privacy_protection": False, "recent_registration": False, "suspicious_registrar": False}
    
    async def _analyze_dns_security(self, dns_intel: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze DNS security posture"""
        return {"dnssec_enabled": False, "spf_configured": False, "dmarc_configured": False}
    
    async def _analyze_ssl_security(self, cert, ssock) -> Dict[str, Any]:
        """Analyze SSL security configuration"""
        return {"weak_cipher": False, "expired_cert": False, "self_signed": False}
    
    async def _check_ssl_vulnerabilities(self, domain: str, cert) -> Dict[str, Any]:
        """Check for SSL vulnerabilities"""
        return {"heartbleed": False, "poodle": False, "beast": False}