#!/usr/bin/env python3
"""
AEGIS-X File Hunter
Specialized hunter for file analysis and secret extraction
"""

import os
import json
import logging
import asyncio
import hashlib
import mimetypes
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import requests
import re
import zipfile
import tarfile

class FileHunter:
    """
    The File Hunter specializes in analyzing files for secrets,
    vulnerabilities, and sensitive information.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.FileHunter")
        self.hunting_stats = self._load_hunting_stats()
        
        # File analysis patterns
        self.secret_patterns = {
            "api_keys": [
                r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
                r'secret[_-]?key["\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
                r'access[_-]?token["\']?\s*[:=]\s*["\']([^"\']{20,})["\']'
            ],
            "passwords": [
                r'password["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
                r'passwd["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
                r'pwd["\']?\s*[:=]\s*["\']([^"\']{8,})["\']'
            ],
            "database_urls": [
                r'(mongodb://[^\s"\'<>]+)',
                r'(mysql://[^\s"\'<>]+)',
                r'(postgresql://[^\s"\'<>]+)',
                r'(redis://[^\s"\'<>]+)'
            ],
            "cloud_keys": [
                r'(AKIA[0-9A-Z]{16})',  # AWS Access Key
                r'(sk_live_[0-9a-zA-Z]{24})',  # Stripe Live Key
                r'(sk_test_[0-9a-zA-Z]{24})',  # Stripe Test Key
                r'(AIza[0-9A-Za-z\\-_]{35})'   # Google API Key
            ]
        }
        
        self.logger.info("📄 File Hunter initialized with comprehensive file analysis capabilities")
    
    def _load_hunting_stats(self) -> Dict[str, Any]:
        """Load hunting statistics"""
        stats_file = Path("learn/file_hunting_stats.json")
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load hunting stats: {e}")
        
        return {
            "files_analyzed": 0,
            "secrets_found": 0,
            "hunting_history": []
        }
    
    async def hunt(self, target: str, intelligence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute file hunting on target"""
        self.logger.info(f"📄 Starting file hunt on: {target}")
        
        hunt_session = {
            "target": target,
            "start_time": datetime.now().isoformat(),
            "findings": [],
            "file_info": {}
        }
        
        try:
            # Download or access file
            file_path = await self._prepare_file(target)
            if not file_path:
                raise Exception("Failed to prepare file for analysis")
            
            # Analyze file
            file_info = await self._analyze_file_info(file_path)
            hunt_session["file_info"] = file_info
            
            # Extract and analyze content
            content = await self._extract_content(file_path, file_info)
            if content:
                # Search for secrets
                secrets = await self._search_secrets(content, file_path)
                hunt_session["findings"].extend(secrets)
                
                # Search for URLs and endpoints
                urls = await self._search_urls(content, file_path)
                hunt_session["findings"].extend(urls)
                
                # Search for sensitive patterns
                sensitive = await self._search_sensitive_patterns(content, file_path)
                hunt_session["findings"].extend(sensitive)
        
        except Exception as e:
            self.logger.error(f"File hunt failed: {str(e)}")
            hunt_session["error"] = str(e)
        
        hunt_session["end_time"] = datetime.now().isoformat()
        hunt_session["total_findings"] = len(hunt_session["findings"])
        
        await self._update_hunting_stats(hunt_session)
        
        self.logger.info(f"🏆 File hunt completed - Found {hunt_session['total_findings']} potential issues")
        return hunt_session["findings"]
    
    async def _prepare_file(self, target: str) -> Optional[str]:
        """Prepare file for analysis"""
        if target.startswith("http"):
            return await self._download_file(target)
        elif os.path.exists(target):
            return target
        else:
            self.logger.error(f"Invalid file target: {target}")
            return None
    
    async def _download_file(self, url: str) -> Optional[str]:
        """Download file from URL"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Determine filename
            filename = url.split('/')[-1] or 'downloaded_file'
            
            # Create uploads directory
            uploads_dir = Path("uploads/files")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = uploads_dir / filename
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(file_path)
        
        except Exception as e:
            self.logger.error(f"Failed to download file: {e}")
            return None
    
    async def _analyze_file_info(self, file_path: str) -> Dict[str, Any]:
        """Analyze basic file information"""
        file_info = {}
        
        try:
            file_path_obj = Path(file_path)
            
            file_info = {
                "filename": file_path_obj.name,
                "size_bytes": file_path_obj.stat().st_size,
                "extension": file_path_obj.suffix,
                "mime_type": mimetypes.guess_type(file_path)[0],
                "hash_md5": self._calculate_file_hash(file_path, "md5"),
                "hash_sha256": self._calculate_file_hash(file_path, "sha256")
            }
        
        except Exception as e:
            self.logger.debug(f"File info analysis failed: {e}")
        
        return file_info
    
    def _calculate_file_hash(self, file_path: str, algorithm: str) -> str:
        """Calculate file hash"""
        try:
            if algorithm == "md5":
                hash_obj = hashlib.md5()
            elif algorithm == "sha256":
                hash_obj = hashlib.sha256()
            else:
                return ""
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        
        except Exception as e:
            self.logger.debug(f"Hash calculation failed: {e}")
            return ""
    
    async def _extract_content(self, file_path: str, file_info: Dict[str, Any]) -> Optional[str]:
        """Extract content from file based on type"""
        try:
            mime_type = file_info.get("mime_type", "")
            extension = file_info.get("extension", "").lower()
            
            # Text files
            if mime_type and mime_type.startswith("text/"):
                return self._read_text_file(file_path)
            
            # Archive files
            elif extension in [".zip", ".jar", ".war", ".ear"]:
                return await self._extract_archive_content(file_path)
            
            # Configuration files
            elif extension in [".json", ".xml", ".yaml", ".yml", ".ini", ".conf", ".config"]:
                return self._read_text_file(file_path)
            
            # Source code files
            elif extension in [".js", ".php", ".py", ".java", ".cpp", ".c", ".h", ".cs", ".rb", ".go"]:
                return self._read_text_file(file_path)
            
            # Try to read as text anyway
            else:
                return self._read_text_file(file_path)
        
        except Exception as e:
            self.logger.debug(f"Content extraction failed: {e}")
            return None
    
    def _read_text_file(self, file_path: str) -> str:
        """Read text file content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            self.logger.debug(f"Text file reading failed: {e}")
            return ""
    
    async def _extract_archive_content(self, file_path: str) -> str:
        """Extract content from archive files"""
        content = ""
        
        try:
            if file_path.endswith('.zip') or file_path.endswith('.jar') or file_path.endswith('.war'):
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    for file_info in zip_file.filelist:
                        if not file_info.is_dir() and file_info.file_size < 1024 * 1024:  # Max 1MB per file
                            try:
                                file_content = zip_file.read(file_info.filename).decode('utf-8', errors='ignore')
                                content += f"\n--- {file_info.filename} ---\n{file_content}\n"
                            except:
                                continue
            
            elif file_path.endswith('.tar') or file_path.endswith('.tar.gz'):
                with tarfile.open(file_path, 'r') as tar_file:
                    for member in tar_file.getmembers():
                        if member.isfile() and member.size < 1024 * 1024:  # Max 1MB per file
                            try:
                                file_obj = tar_file.extractfile(member)
                                if file_obj:
                                    file_content = file_obj.read().decode('utf-8', errors='ignore')
                                    content += f"\n--- {member.name} ---\n{file_content}\n"
                            except:
                                continue
        
        except Exception as e:
            self.logger.debug(f"Archive extraction failed: {e}")
        
        return content
    
    async def _search_secrets(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Search for secrets in content"""
        findings = []
        
        for secret_type, patterns in self.secret_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    # Mask the secret for logging
                    masked_secret = match[:4] + "*" * (len(match) - 8) + match[-4:] if len(match) > 8 else "*" * len(match)
                    
                    findings.append({
                        "type": "hardcoded_secrets",
                        "title": f"{secret_type.replace('_', ' ').title()} Found",
                        "description": f"Found {secret_type.replace('_', ' ')} in file",
                        "severity": "High",
                        "evidence": {
                            "file": file_path,
                            "secret_type": secret_type,
                            "masked_value": masked_secret,
                            "pattern_matched": pattern
                        },
                        "tool": "file_hunter"
                    })
        
        return findings
    
    async def _search_urls(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Search for URLs and endpoints in content"""
        findings = []
        
        # URL patterns
        url_patterns = [
            r'https?://[^\s"\'<>]+',
            r'ftp://[^\s"\'<>]+',
            r'["\']([^"\']*/?api/[^"\']*)["\']',
            r'["\']([^"\']*/?v\d+/[^"\']*)["\']'
        ]
        
        urls = set()
        for pattern in url_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            urls.update(matches)
        
        if urls:
            # Check for insecure URLs
            insecure_urls = [url for url in urls if url.startswith('http://')]
            
            if insecure_urls:
                findings.append({
                    "type": "insecure_communication",
                    "title": "Insecure HTTP URLs Found",
                    "description": f"Found {len(insecure_urls)} insecure HTTP URLs",
                    "severity": "Medium",
                    "evidence": {
                        "file": file_path,
                        "insecure_urls": list(insecure_urls)[:10]  # Limit to 10
                    },
                    "tool": "file_hunter"
                })
            
            # Check for API endpoints
            api_urls = [url for url in urls if '/api/' in url or '/v1/' in url or '/v2/' in url]
            
            if api_urls:
                findings.append({
                    "type": "information_disclosure",
                    "title": "API Endpoints Found",
                    "description": f"Found {len(api_urls)} potential API endpoints",
                    "severity": "Info",
                    "evidence": {
                        "file": file_path,
                        "api_endpoints": list(api_urls)[:10]  # Limit to 10
                    },
                    "tool": "file_hunter"
                })
        
        return findings
    
    async def _search_sensitive_patterns(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Search for sensitive patterns in content"""
        findings = []
        
        # Sensitive patterns
        sensitive_patterns = {
            "private_keys": [
                r'-----BEGIN PRIVATE KEY-----',
                r'-----BEGIN RSA PRIVATE KEY-----',
                r'-----BEGIN OPENSSH PRIVATE KEY-----'
            ],
            "certificates": [
                r'-----BEGIN CERTIFICATE-----'
            ],
            "database_info": [
                r'(host|server|hostname)\s*[:=]\s*["\']?([^"\';\s]+)["\']?',
                r'(database|db|schema)\s*[:=]\s*["\']?([^"\';\s]+)["\']?',
                r'(username|user|uid)\s*[:=]\s*["\']?([^"\';\s]+)["\']?'
            ],
            "email_addresses": [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            "ip_addresses": [
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ]
        }
        
        for pattern_type, patterns in sensitive_patterns.items():
            matches = set()
            
            for pattern in patterns:
                pattern_matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                if isinstance(pattern_matches[0], tuple) if pattern_matches else False:
                    # Extract the captured group
                    matches.update([match[1] if len(match) > 1 else match[0] for match in pattern_matches])
                else:
                    matches.update(pattern_matches)
            
            if matches:
                findings.append({
                    "type": "information_disclosure",
                    "title": f"{pattern_type.replace('_', ' ').title()} Found",
                    "description": f"Found {len(matches)} {pattern_type.replace('_', ' ')}",
                    "severity": "Medium" if pattern_type in ["private_keys", "database_info"] else "Low",
                    "evidence": {
                        "file": file_path,
                        "pattern_type": pattern_type,
                        "matches": list(matches)[:10]  # Limit to 10
                    },
                    "tool": "file_hunter"
                })
        
        return findings
    
    async def _update_hunting_stats(self, hunt_session: Dict[str, Any]):
        """Update hunting statistics"""
        self.hunting_stats["files_analyzed"] += 1
        
        # Count secrets found
        secrets_count = len([f for f in hunt_session["findings"] if f["type"] == "hardcoded_secrets"])
        self.hunting_stats["secrets_found"] += secrets_count
        
        # Add to hunting history
        self.hunting_stats["hunting_history"].append({
            "target": hunt_session["target"],
            "findings_count": hunt_session["total_findings"],
            "secrets_count": secrets_count,
            "timestamp": hunt_session["start_time"]
        })
        
        # Keep only last 50 hunt records
        if len(self.hunting_stats["hunting_history"]) > 50:
            self.hunting_stats["hunting_history"] = self.hunting_stats["hunting_history"][-50:]
        
        # Save statistics
        await self._save_hunting_stats()
    
    async def _save_hunting_stats(self):
        """Save hunting statistics"""
        stats_file = Path("learn/file_hunting_stats.json")
        stats_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.hunting_stats, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save hunting stats: {e}")
    
    def get_hunting_stats(self) -> Dict[str, Any]:
        """Get hunting statistics"""
        return {
            "files_analyzed": self.hunting_stats["files_analyzed"],
            "secrets_found": self.hunting_stats["secrets_found"],
            "recent_hunts": self.hunting_stats["hunting_history"][-10:]  # Last 10 hunts
        }