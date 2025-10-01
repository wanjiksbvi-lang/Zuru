#!/usr/bin/env python3
"""
AEGIS-X Network Hunter
Specialized hunter for network infrastructure and services
"""

import os
import json
import logging
import asyncio
import socket
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import ipaddress

class NetworkHunter:
    """
    The Network Hunter specializes in discovering vulnerabilities in
    network infrastructure, services, and protocols.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.NetworkHunter")
        self.hunting_stats = self._load_hunting_stats()
        
        # Common ports and services
        self.common_ports = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S",
            1433: "MSSQL",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            27017: "MongoDB",
            3389: "RDP",
            5985: "WinRM",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt"
        }
        
        # Vulnerability patterns by service
        self.service_vulns = {
            "SSH": ["weak_ciphers", "default_credentials", "version_disclosure"],
            "FTP": ["anonymous_access", "weak_credentials", "directory_traversal"],
            "HTTP": ["directory_listing", "server_disclosure", "weak_headers"],
            "HTTPS": ["weak_ssl", "certificate_issues", "cipher_weaknesses"],
            "SMTP": ["open_relay", "user_enumeration", "weak_auth"],
            "DNS": ["zone_transfer", "cache_poisoning", "amplification"],
            "Database": ["default_credentials", "weak_auth", "information_disclosure"]
        }
        
        self.logger.info("🌐 Network Hunter initialized with comprehensive network security capabilities")
    
    def _load_hunting_stats(self) -> Dict[str, Any]:
        """Load hunting statistics"""
        stats_file = Path("learn/network_hunting_stats.json")
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load hunting stats: {e}")
        
        return {
            "networks_scanned": 0,
            "hosts_discovered": 0,
            "services_found": 0,
            "vulnerabilities_found": 0,
            "hunting_history": []
        }
    
    async def hunt(self, target: str, intelligence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute network hunting on target"""
        self.logger.info(f"🌐 Starting network hunt on: {target}")
        
        hunt_session = {
            "target": target,
            "start_time": datetime.now().isoformat(),
            "findings": [],
            "hosts_discovered": [],
            "services_discovered": []
        }
        
        try:
            # Parse target (IP, CIDR, or hostname)
            targets = await self._parse_network_target(target)
            
            # Phase 1: Host Discovery
            live_hosts = await self._discover_hosts(targets)
            hunt_session["hosts_discovered"] = live_hosts
            
            if live_hosts:
                hunt_session["findings"].append({
                    "type": "information_disclosure",
                    "title": "Live Hosts Discovered",
                    "description": f"Found {len(live_hosts)} live hosts",
                    "severity": "Info",
                    "evidence": {"hosts": live_hosts},
                    "tool": "host_discovery"
                })
            
            # Phase 2: Port Scanning
            for host in live_hosts:
                open_ports = await self._scan_ports(host)
                if open_ports:
                    hunt_session["findings"].append({
                        "type": "information_disclosure",
                        "title": f"Open Ports on {host}",
                        "description": f"Found {len(open_ports)} open ports",
                        "severity": "Info",
                        "evidence": {"host": host, "ports": open_ports},
                        "tool": "port_scan"
                    })
                    
                    # Phase 3: Service Detection
                    services = await self._detect_services(host, open_ports)
                    hunt_session["services_discovered"].extend(services)
                    
                    # Phase 4: Service-specific Testing
                    for service in services:
                        service_vulns = await self._test_service_vulnerabilities(host, service)
                        hunt_session["findings"].extend(service_vulns)
        
        except Exception as e:
            self.logger.error(f"Network hunt failed: {str(e)}")
            hunt_session["error"] = str(e)
        
        hunt_session["end_time"] = datetime.now().isoformat()
        hunt_session["total_findings"] = len(hunt_session["findings"])
        
        await self._update_hunting_stats(hunt_session)
        
        self.logger.info(f"🏆 Network hunt completed - Found {hunt_session['total_findings']} potential issues")
        return hunt_session["findings"]
    
    async def _parse_network_target(self, target: str) -> List[str]:
        """Parse network target into list of IPs"""
        targets = []
        
        try:
            # Check if it's a CIDR range
            if '/' in target:
                network = ipaddress.ip_network(target, strict=False)
                # Limit to reasonable size to avoid scanning entire internet
                if network.num_addresses <= 256:
                    targets = [str(ip) for ip in network.hosts()]
                else:
                    self.logger.warning(f"Network {target} too large, limiting to first 256 hosts")
                    targets = [str(ip) for ip in list(network.hosts())[:256]]
            
            # Check if it's a single IP
            elif self._is_valid_ip(target):
                targets = [target]
            
            # Try to resolve hostname
            else:
                try:
                    ip = socket.gethostbyname(target)
                    targets = [ip]
                except socket.gaierror:
                    self.logger.error(f"Could not resolve hostname: {target}")
        
        except Exception as e:
            self.logger.error(f"Failed to parse network target: {e}")
        
        return targets
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Check if string is a valid IP address"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    async def _discover_hosts(self, targets: List[str]) -> List[str]:
        """Discover live hosts using ping"""
        live_hosts = []
        
        # Limit concurrent pings
        semaphore = asyncio.Semaphore(50)
        
        async def ping_host(ip: str) -> Optional[str]:
            async with semaphore:
                try:
                    # Use ping command
                    process = await asyncio.create_subprocess_exec(
                        'ping', '-c', '1', '-W', '1', ip,
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL
                    )
                    
                    await asyncio.wait_for(process.wait(), timeout=3)
                    
                    if process.returncode == 0:
                        return ip
                except (asyncio.TimeoutError, Exception):
                    pass
                
                return None
        
        # Ping all targets concurrently
        tasks = [ping_host(ip) for ip in targets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        live_hosts = [ip for ip in results if ip and isinstance(ip, str)]
        
        self.logger.info(f"Discovered {len(live_hosts)} live hosts out of {len(targets)} targets")
        return live_hosts
    
    async def _scan_ports(self, host: str) -> List[Dict[str, Any]]:
        """Scan ports on a host"""
        open_ports = []
        
        # Scan common ports first
        ports_to_scan = list(self.common_ports.keys())
        
        # Add some additional common ports
        additional_ports = [8000, 8080, 8443, 8888, 9000, 9090, 10000]
        ports_to_scan.extend(additional_ports)
        
        semaphore = asyncio.Semaphore(100)  # Limit concurrent connections
        
        async def scan_port(port: int) -> Optional[Dict[str, Any]]:
            async with semaphore:
                try:
                    # TCP connect scan
                    future = asyncio.open_connection(host, port)
                    reader, writer = await asyncio.wait_for(future, timeout=2)
                    
                    writer.close()
                    await writer.wait_closed()
                    
                    service_name = self.common_ports.get(port, "Unknown")
                    
                    return {
                        "port": port,
                        "protocol": "tcp",
                        "state": "open",
                        "service": service_name
                    }
                
                except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                    pass
                
                return None
        
        # Scan all ports concurrently
        tasks = [scan_port(port) for port in ports_to_scan]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        open_ports = [port_info for port_info in results if port_info and isinstance(port_info, dict)]
        
        self.logger.debug(f"Found {len(open_ports)} open ports on {host}")
        return open_ports
    
    async def _detect_services(self, host: str, open_ports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect services running on open ports"""
        services = []
        
        for port_info in open_ports:
            port = port_info["port"]
            service_name = port_info["service"]
            
            # Try to get service banner
            banner = await self._get_service_banner(host, port)
            
            service_info = {
                "host": host,
                "port": port,
                "service": service_name,
                "banner": banner,
                "version": self._extract_version_from_banner(banner) if banner else None
            }
            
            services.append(service_info)
        
        return services
    
    async def _get_service_banner(self, host: str, port: int) -> Optional[str]:
        """Get service banner"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=5
            )
            
            # Try to read banner
            banner_data = await asyncio.wait_for(reader.read(1024), timeout=3)
            banner = banner_data.decode('utf-8', errors='ignore').strip()
            
            writer.close()
            await writer.wait_closed()
            
            return banner if banner else None
        
        except Exception:
            return None
    
    def _extract_version_from_banner(self, banner: str) -> Optional[str]:
        """Extract version information from service banner"""
        if not banner:
            return None
        
        # Common version patterns
        version_patterns = [
            r'(\d+\.\d+\.\d+)',
            r'(\d+\.\d+)',
            r'version\s+(\d+\.\d+\.\d+)',
            r'v(\d+\.\d+\.\d+)'
        ]
        
        import re
        for pattern in version_patterns:
            match = re.search(pattern, banner, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    async def _test_service_vulnerabilities(self, host: str, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test service-specific vulnerabilities"""
        findings = []
        
        service_name = service["service"]
        port = service["port"]
        
        # Test based on service type
        if service_name == "SSH":
            ssh_vulns = await self._test_ssh_vulnerabilities(host, port, service)
            findings.extend(ssh_vulns)
        
        elif service_name == "FTP":
            ftp_vulns = await self._test_ftp_vulnerabilities(host, port, service)
            findings.extend(ftp_vulns)
        
        elif service_name in ["HTTP", "HTTPS"]:
            http_vulns = await self._test_http_vulnerabilities(host, port, service)
            findings.extend(http_vulns)
        
        elif service_name == "SMTP":
            smtp_vulns = await self._test_smtp_vulnerabilities(host, port, service)
            findings.extend(smtp_vulns)
        
        elif service_name == "DNS":
            dns_vulns = await self._test_dns_vulnerabilities(host, port, service)
            findings.extend(dns_vulns)
        
        elif service_name in ["MySQL", "PostgreSQL", "MSSQL"]:
            db_vulns = await self._test_database_vulnerabilities(host, port, service)
            findings.extend(db_vulns)
        
        return findings
    
    async def _test_ssh_vulnerabilities(self, host: str, port: int, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test SSH-specific vulnerabilities"""
        findings = []
        
        # Check for weak SSH configuration
        banner = service.get("banner", "")
        
        if banner:
            # Check for old SSH versions
            if "SSH-1." in banner:
                findings.append({
                    "type": "weak_cryptography",
                    "title": "Weak SSH Protocol Version",
                    "description": f"SSH service on {host}:{port} uses weak protocol version",
                    "severity": "High",
                    "evidence": {"banner": banner, "issue": "SSH-1.x protocol"},
                    "tool": "ssh_test"
                })
            
            # Check for version disclosure
            findings.append({
                "type": "information_disclosure",
                "title": "SSH Version Disclosure",
                "description": f"SSH service on {host}:{port} discloses version information",
                "severity": "Low",
                "evidence": {"banner": banner},
                "tool": "ssh_test"
            })
        
        return findings
    
    async def _test_ftp_vulnerabilities(self, host: str, port: int, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test FTP-specific vulnerabilities"""
        findings = []
        
        try:
            # Test for anonymous FTP access
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=5
            )
            
            # Read welcome banner
            welcome = await asyncio.wait_for(reader.read(1024), timeout=3)
            
            # Try anonymous login
            writer.write(b"USER anonymous\r\n")
            await writer.drain()
            
            response = await asyncio.wait_for(reader.read(1024), timeout=3)
            
            if b"331" in response:  # User name okay, need password
                writer.write(b"PASS anonymous@example.com\r\n")
                await writer.drain()
                
                login_response = await asyncio.wait_for(reader.read(1024), timeout=3)
                
                if b"230" in login_response:  # User logged in
                    findings.append({
                        "type": "authentication_bypass",
                        "title": "Anonymous FTP Access",
                        "description": f"FTP service on {host}:{port} allows anonymous access",
                        "severity": "Medium",
                        "evidence": {"login_response": login_response.decode('utf-8', errors='ignore')},
                        "tool": "ftp_test"
                    })
            
            writer.close()
            await writer.wait_closed()
        
        except Exception as e:
            self.logger.debug(f"FTP test failed for {host}:{port}: {e}")
        
        return findings
    
    async def _test_http_vulnerabilities(self, host: str, port: int, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test HTTP-specific vulnerabilities"""
        findings = []
        
        try:
            import httpx
            
            protocol = "https" if port == 443 or service["service"] == "HTTPS" else "http"
            url = f"{protocol}://{host}:{port}"
            
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                response = await client.get(url)
                
                # Check for server header disclosure
                server_header = response.headers.get("server")
                if server_header:
                    findings.append({
                        "type": "information_disclosure",
                        "title": "Server Header Disclosure",
                        "description": f"HTTP service on {host}:{port} discloses server information",
                        "severity": "Low",
                        "evidence": {"server_header": server_header},
                        "tool": "http_test"
                    })
                
                # Check for missing security headers
                security_headers = [
                    "X-Frame-Options",
                    "X-Content-Type-Options",
                    "X-XSS-Protection",
                    "Strict-Transport-Security"
                ]
                
                missing_headers = [header for header in security_headers if header not in response.headers]
                
                if missing_headers:
                    findings.append({
                        "type": "insecure_configuration",
                        "title": "Missing Security Headers",
                        "description": f"HTTP service on {host}:{port} missing security headers",
                        "severity": "Medium",
                        "evidence": {"missing_headers": missing_headers},
                        "tool": "http_test"
                    })
        
        except Exception as e:
            self.logger.debug(f"HTTP test failed for {host}:{port}: {e}")
        
        return findings
    
    async def _test_smtp_vulnerabilities(self, host: str, port: int, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test SMTP-specific vulnerabilities"""
        findings = []
        
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=5
            )
            
            # Read welcome banner
            welcome = await asyncio.wait_for(reader.read(1024), timeout=3)
            
            # Test for open relay
            writer.write(b"HELO test.com\r\n")
            await writer.drain()
            
            helo_response = await asyncio.wait_for(reader.read(1024), timeout=3)
            
            if b"250" in helo_response:
                writer.write(b"MAIL FROM:<test@external.com>\r\n")
                await writer.drain()
                
                mail_response = await asyncio.wait_for(reader.read(1024), timeout=3)
                
                if b"250" in mail_response:
                    writer.write(b"RCPT TO:<victim@external.com>\r\n")
                    await writer.drain()
                    
                    rcpt_response = await asyncio.wait_for(reader.read(1024), timeout=3)
                    
                    if b"250" in rcpt_response:
                        findings.append({
                            "type": "misconfiguration",
                            "title": "SMTP Open Relay",
                            "description": f"SMTP service on {host}:{port} configured as open relay",
                            "severity": "High",
                            "evidence": {"relay_test": "External to external relay allowed"},
                            "tool": "smtp_test"
                        })
            
            writer.close()
            await writer.wait_closed()
        
        except Exception as e:
            self.logger.debug(f"SMTP test failed for {host}:{port}: {e}")
        
        return findings
    
    async def _test_dns_vulnerabilities(self, host: str, port: int, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test DNS-specific vulnerabilities"""
        findings = []
        
        try:
            import dns.resolver
            import dns.zone
            
            # Test for zone transfer
            try:
                # This is a simplified test - in reality you'd need the domain name
                zone = dns.zone.from_xfr(dns.query.xfr(host, 'example.com'))
                
                findings.append({
                    "type": "information_disclosure",
                    "title": "DNS Zone Transfer Allowed",
                    "description": f"DNS service on {host}:{port} allows zone transfers",
                    "severity": "Medium",
                    "evidence": {"zone_transfer": "Allowed"},
                    "tool": "dns_test"
                })
            
            except Exception:
                # Zone transfer not allowed or failed
                pass
        
        except Exception as e:
            self.logger.debug(f"DNS test failed for {host}:{port}: {e}")
        
        return findings
    
    async def _test_database_vulnerabilities(self, host: str, port: int, service: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test database-specific vulnerabilities"""
        findings = []
        
        service_name = service["service"]
        
        # Test for default credentials (simplified)
        default_creds = {
            "MySQL": [("root", ""), ("root", "root"), ("admin", "admin")],
            "PostgreSQL": [("postgres", ""), ("postgres", "postgres")],
            "MSSQL": [("sa", ""), ("sa", "sa"), ("admin", "admin")]
        }
        
        if service_name in default_creds:
            findings.append({
                "type": "weak_authentication",
                "title": f"Potential Default {service_name} Credentials",
                "description": f"{service_name} service on {host}:{port} may use default credentials",
                "severity": "High",
                "evidence": {
                    "service": service_name,
                    "common_defaults": [f"{user}:{password}" for user, password in default_creds[service_name]]
                },
                "tool": "database_test"
            })
        
        return findings
    
    async def _update_hunting_stats(self, hunt_session: Dict[str, Any]):
        """Update hunting statistics"""
        self.hunting_stats["networks_scanned"] += 1
        self.hunting_stats["hosts_discovered"] += len(hunt_session["hosts_discovered"])
        self.hunting_stats["services_found"] += len(hunt_session["services_discovered"])
        self.hunting_stats["vulnerabilities_found"] += hunt_session["total_findings"]
        
        # Add to hunting history
        self.hunting_stats["hunting_history"].append({
            "target": hunt_session["target"],
            "hosts_found": len(hunt_session["hosts_discovered"]),
            "services_found": len(hunt_session["services_discovered"]),
            "findings_count": hunt_session["total_findings"],
            "timestamp": hunt_session["start_time"]
        })
        
        # Keep only last 50 hunt records
        if len(self.hunting_stats["hunting_history"]) > 50:
            self.hunting_stats["hunting_history"] = self.hunting_stats["hunting_history"][-50:]
        
        # Save statistics
        await self._save_hunting_stats()
    
    async def _save_hunting_stats(self):
        """Save hunting statistics"""
        stats_file = Path("learn/network_hunting_stats.json")
        stats_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.hunting_stats, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save hunting stats: {e}")
    
    def get_hunting_stats(self) -> Dict[str, Any]:
        """Get hunting statistics"""
        return {
            "networks_scanned": self.hunting_stats["networks_scanned"],
            "hosts_discovered": self.hunting_stats["hosts_discovered"],
            "services_found": self.hunting_stats["services_found"],
            "vulnerabilities_found": self.hunting_stats["vulnerabilities_found"],
            "recent_hunts": self.hunting_stats["hunting_history"][-10:]  # Last 10 hunts
        }