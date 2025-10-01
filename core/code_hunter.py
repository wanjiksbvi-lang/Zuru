#!/usr/bin/env python3
"""
AEGIS-X Code Hunter
Specialized hunter for source code repositories and static analysis
"""

import os
import json
import logging
import asyncio
import subprocess
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import requests
import re
import git

class CodeHunter:
    """
    The Code Hunter specializes in analyzing source code repositories
    for vulnerabilities, secrets, and security issues.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.CodeHunter")
        self.hunting_stats = self._load_hunting_stats()
        
        # Code analysis patterns
        self.vulnerability_patterns = {
            "sql_injection": [
                r'(SELECT|INSERT|UPDATE|DELETE).*\+.*\$',
                r'query\s*\(\s*["\'].*\$.*["\']',
                r'execute\s*\(\s*["\'].*\$.*["\']'
            ],
            "xss": [
                r'innerHTML\s*=\s*.*\$',
                r'document\.write\s*\(\s*.*\$',
                r'echo\s+.*\$_[GET|POST]'
            ],
            "command_injection": [
                r'exec\s*\(\s*.*\$',
                r'system\s*\(\s*.*\$',
                r'shell_exec\s*\(\s*.*\$',
                r'eval\s*\(\s*.*\$'
            ],
            "path_traversal": [
                r'include\s*\(\s*.*\$',
                r'require\s*\(\s*.*\$',
                r'file_get_contents\s*\(\s*.*\$'
            ],
            "hardcoded_secrets": [
                r'password\s*[:=]\s*["\']([^"\']{8,})["\']',
                r'api[_-]?key\s*[:=]\s*["\']([^"\']{20,})["\']',
                r'secret\s*[:=]\s*["\']([^"\']{20,})["\']',
                r'token\s*[:=]\s*["\']([^"\']{20,})["\']'
            ],
            "weak_crypto": [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'DES\s*\(',
                r'RC4\s*\('
            ]
        }
        
        # File extensions to analyze
        self.code_extensions = {
            '.py', '.php', '.js', '.java', '.cpp', '.c', '.cs', '.rb', '.go',
            '.ts', '.jsx', '.tsx', '.vue', '.swift', '.kt', '.scala', '.rs'
        }
        
        self.config_extensions = {
            '.json', '.xml', '.yaml', '.yml', '.ini', '.conf', '.config',
            '.env', '.properties', '.toml'
        }
        
        self.logger.info("💻 Code Hunter initialized with comprehensive static analysis capabilities")
    
    def _load_hunting_stats(self) -> Dict[str, Any]:
        """Load hunting statistics"""
        stats_file = Path("learn/code_hunting_stats.json")
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load hunting stats: {e}")
        
        return {
            "repositories_analyzed": 0,
            "files_scanned": 0,
            "vulnerabilities_found": 0,
            "secrets_found": 0,
            "hunting_history": []
        }
    
    async def hunt(self, target: str, intelligence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute code hunting on target repository"""
        self.logger.info(f"💻 Starting code hunt on: {target}")
        
        hunt_session = {
            "target": target,
            "start_time": datetime.now().isoformat(),
            "findings": [],
            "repository_info": {},
            "files_analyzed": 0
        }
        
        try:
            # Clone or access repository
            repo_path = await self._prepare_repository(target)
            if not repo_path:
                raise Exception("Failed to prepare repository for analysis")
            
            # Analyze repository structure
            repo_info = await self._analyze_repository_structure(repo_path)
            hunt_session["repository_info"] = repo_info
            
            # Phase 1: Secret Scanning
            secret_findings = await self._scan_for_secrets(repo_path)
            hunt_session["findings"].extend(secret_findings)
            
            # Phase 2: Static Code Analysis
            code_findings = await self._analyze_source_code(repo_path)
            hunt_session["findings"].extend(code_findings)
            
            # Phase 3: Configuration Analysis
            config_findings = await self._analyze_configurations(repo_path)
            hunt_session["findings"].extend(config_findings)
            
            # Phase 4: Dependency Analysis
            dependency_findings = await self._analyze_dependencies(repo_path)
            hunt_session["findings"].extend(dependency_findings)
            
            # Phase 5: Git History Analysis
            git_findings = await self._analyze_git_history(repo_path)
            hunt_session["findings"].extend(git_findings)
            
        except Exception as e:
            self.logger.error(f"Code hunt failed: {str(e)}")
            hunt_session["error"] = str(e)
        
        hunt_session["end_time"] = datetime.now().isoformat()
        hunt_session["total_findings"] = len(hunt_session["findings"])
        
        await self._update_hunting_stats(hunt_session)
        
        self.logger.info(f"🏆 Code hunt completed - Found {hunt_session['total_findings']} potential issues")
        return hunt_session["findings"]
    
    async def _prepare_repository(self, target: str) -> Optional[str]:
        """Prepare repository for analysis"""
        if target.startswith(("http://", "https://", "git@")):
            return await self._clone_repository(target)
        elif os.path.exists(target) and os.path.isdir(target):
            return target
        else:
            # Try to parse as GitHub/GitLab shorthand
            if ":" in target and not target.startswith("http"):
                if target.startswith("github:"):
                    repo_url = f"https://github.com/{target[7:]}.git"
                elif target.startswith("gitlab:"):
                    repo_url = f"https://gitlab.com/{target[7:]}.git"
                else:
                    self.logger.error(f"Unknown repository format: {target}")
                    return None
                
                return await self._clone_repository(repo_url)
            
            self.logger.error(f"Invalid repository target: {target}")
            return None
    
    async def _clone_repository(self, repo_url: str) -> Optional[str]:
        """Clone repository from URL"""
        try:
            # Create temporary directory for cloning
            clone_dir = Path("uploads/repositories") / f"repo_{int(datetime.now().timestamp())}"
            clone_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Cloning repository: {repo_url}")
            
            # Clone repository
            repo = git.Repo.clone_from(repo_url, clone_dir, depth=1)  # Shallow clone
            
            return str(clone_dir)
        
        except Exception as e:
            self.logger.error(f"Failed to clone repository: {e}")
            return None
    
    async def _analyze_repository_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository structure and metadata"""
        repo_info = {
            "path": repo_path,
            "total_files": 0,
            "code_files": 0,
            "config_files": 0,
            "languages": {},
            "frameworks": [],
            "has_git": False
        }
        
        try:
            repo_path_obj = Path(repo_path)
            
            # Check if it's a git repository
            if (repo_path_obj / ".git").exists():
                repo_info["has_git"] = True
            
            # Count files and detect languages
            for file_path in repo_path_obj.rglob("*"):
                if file_path.is_file():
                    repo_info["total_files"] += 1
                    
                    extension = file_path.suffix.lower()
                    
                    if extension in self.code_extensions:
                        repo_info["code_files"] += 1
                        
                        # Count by language
                        language = self._extension_to_language(extension)
                        repo_info["languages"][language] = repo_info["languages"].get(language, 0) + 1
                    
                    elif extension in self.config_extensions:
                        repo_info["config_files"] += 1
            
            # Detect frameworks
            repo_info["frameworks"] = await self._detect_frameworks(repo_path_obj)
        
        except Exception as e:
            self.logger.debug(f"Repository structure analysis failed: {e}")
        
        return repo_info
    
    def _extension_to_language(self, extension: str) -> str:
        """Map file extension to programming language"""
        language_map = {
            '.py': 'Python',
            '.php': 'PHP',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala'
        }
        
        return language_map.get(extension, 'Unknown')
    
    async def _detect_frameworks(self, repo_path: Path) -> List[str]:
        """Detect frameworks used in the repository"""
        frameworks = []
        
        # Check for common framework indicators
        framework_indicators = {
            'Django': ['manage.py', 'settings.py', 'requirements.txt'],
            'Flask': ['app.py', 'requirements.txt'],
            'React': ['package.json', 'src/App.js', 'public/index.html'],
            'Angular': ['angular.json', 'package.json'],
            'Vue.js': ['vue.config.js', 'package.json'],
            'Spring Boot': ['pom.xml', 'application.properties'],
            'Laravel': ['composer.json', 'artisan'],
            'Ruby on Rails': ['Gemfile', 'config/routes.rb'],
            'Express.js': ['package.json', 'app.js'],
            'ASP.NET': ['*.csproj', 'web.config']
        }
        
        for framework, indicators in framework_indicators.items():
            if all(any(repo_path.rglob(indicator)) for indicator in indicators):
                frameworks.append(framework)
        
        return frameworks
    
    async def _scan_for_secrets(self, repo_path: str) -> List[Dict[str, Any]]:
        """Scan repository for hardcoded secrets"""
        findings = []
        
        try:
            repo_path_obj = Path(repo_path)
            
            # Scan all text files
            for file_path in repo_path_obj.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in (self.code_extensions | self.config_extensions):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Search for secrets
                        secrets = self._find_secrets_in_content(content, str(file_path))
                        findings.extend(secrets)
                    
                    except Exception as e:
                        self.logger.debug(f"Failed to scan file {file_path}: {e}")
        
        except Exception as e:
            self.logger.error(f"Secret scanning failed: {e}")
        
        return findings
    
    def _find_secrets_in_content(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Find secrets in file content"""
        findings = []
        
        for secret_type, patterns in self.vulnerability_patterns["hardcoded_secrets"]:
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    # Mask the secret
                    masked_secret = match[:4] + "*" * (len(match) - 8) + match[-4:] if len(match) > 8 else "*" * len(match)
                    
                    findings.append({
                        "type": "hardcoded_secrets",
                        "title": f"Hardcoded Secret in {Path(file_path).name}",
                        "description": f"Found hardcoded secret in source code",
                        "severity": "High",
                        "evidence": {
                            "file": file_path,
                            "secret_type": secret_type,
                            "masked_value": masked_secret,
                            "line_context": self._get_line_context(content, match)
                        },
                        "tool": "code_hunter"
                    })
        
        return findings
    
    def _get_line_context(self, content: str, match: str) -> str:
        """Get line context for a match"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if match in line:
                # Return line with some context
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context_lines = lines[start:end]
                return '\n'.join(f"{start + j + 1}: {line}" for j, line in enumerate(context_lines))
        
        return ""
    
    async def _analyze_source_code(self, repo_path: str) -> List[Dict[str, Any]]:
        """Analyze source code for vulnerabilities"""
        findings = []
        
        try:
            repo_path_obj = Path(repo_path)
            
            # Analyze code files
            for file_path in repo_path_obj.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.code_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Check for various vulnerability patterns
                        for vuln_type, patterns in self.vulnerability_patterns.items():
                            if vuln_type == "hardcoded_secrets":
                                continue  # Already handled in secret scanning
                            
                            for pattern in patterns:
                                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                                
                                if matches:
                                    findings.append({
                                        "type": vuln_type,
                                        "title": f"{vuln_type.replace('_', ' ').title()} in {file_path.name}",
                                        "description": f"Potential {vuln_type.replace('_', ' ')} vulnerability found",
                                        "severity": self._get_vulnerability_severity(vuln_type),
                                        "evidence": {
                                            "file": str(file_path),
                                            "matches": matches[:5],  # Limit to first 5 matches
                                            "pattern": pattern
                                        },
                                        "tool": "code_hunter"
                                    })
                    
                    except Exception as e:
                        self.logger.debug(f"Failed to analyze file {file_path}: {e}")
        
        except Exception as e:
            self.logger.error(f"Source code analysis failed: {e}")
        
        return findings
    
    def _get_vulnerability_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type"""
        severity_map = {
            "sql_injection": "High",
            "xss": "Medium",
            "command_injection": "High",
            "path_traversal": "Medium",
            "weak_crypto": "Medium"
        }
        
        return severity_map.get(vuln_type, "Low")
    
    async def _analyze_configurations(self, repo_path: str) -> List[Dict[str, Any]]:
        """Analyze configuration files"""
        findings = []
        
        try:
            repo_path_obj = Path(repo_path)
            
            # Analyze configuration files
            for file_path in repo_path_obj.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.config_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Check for insecure configurations
                        config_issues = self._analyze_config_content(content, str(file_path))
                        findings.extend(config_issues)
                    
                    except Exception as e:
                        self.logger.debug(f"Failed to analyze config file {file_path}: {e}")
        
        except Exception as e:
            self.logger.error(f"Configuration analysis failed: {e}")
        
        return findings
    
    def _analyze_config_content(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze configuration file content"""
        findings = []
        
        # Check for debug mode enabled
        debug_patterns = [
            r'debug\s*[:=]\s*true',
            r'DEBUG\s*[:=]\s*True',
            r'development\s*[:=]\s*true'
        ]
        
        for pattern in debug_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append({
                    "type": "insecure_configuration",
                    "title": f"Debug Mode Enabled in {Path(file_path).name}",
                    "description": "Debug mode is enabled in configuration",
                    "severity": "Medium",
                    "evidence": {
                        "file": file_path,
                        "issue": "Debug mode enabled"
                    },
                    "tool": "code_hunter"
                })
        
        # Check for insecure database configurations
        db_patterns = [
            r'password\s*[:=]\s*["\']?["\']?',  # Empty password
            r'host\s*[:=]\s*["\']?0\.0\.0\.0["\']?',  # Bind to all interfaces
        ]
        
        for pattern in db_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append({
                    "type": "insecure_configuration",
                    "title": f"Insecure Database Configuration in {Path(file_path).name}",
                    "description": "Insecure database configuration found",
                    "severity": "High",
                    "evidence": {
                        "file": file_path,
                        "issue": "Insecure database configuration"
                    },
                    "tool": "code_hunter"
                })
        
        return findings
    
    async def _analyze_dependencies(self, repo_path: str) -> List[Dict[str, Any]]:
        """Analyze project dependencies for known vulnerabilities"""
        findings = []
        
        try:
            repo_path_obj = Path(repo_path)
            
            # Check different dependency files
            dependency_files = {
                "requirements.txt": "Python",
                "package.json": "Node.js",
                "composer.json": "PHP",
                "Gemfile": "Ruby",
                "pom.xml": "Java",
                "build.gradle": "Java"
            }
            
            for dep_file, language in dependency_files.items():
                dep_path = repo_path_obj / dep_file
                if dep_path.exists():
                    try:
                        with open(dep_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Basic dependency analysis
                        findings.append({
                            "type": "information_disclosure",
                            "title": f"{language} Dependencies Found",
                            "description": f"Found {language} dependency file: {dep_file}",
                            "severity": "Info",
                            "evidence": {
                                "file": str(dep_path),
                                "language": language,
                                "dependency_count": len(content.split('\n'))
                            },
                            "tool": "code_hunter"
                        })
                        
                        # Check for outdated or vulnerable dependencies (simplified)
                        vulnerable_deps = self._check_vulnerable_dependencies(content, language)
                        findings.extend(vulnerable_deps)
                    
                    except Exception as e:
                        self.logger.debug(f"Failed to analyze dependency file {dep_path}: {e}")
        
        except Exception as e:
            self.logger.error(f"Dependency analysis failed: {e}")
        
        return findings
    
    def _check_vulnerable_dependencies(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Check for known vulnerable dependencies"""
        findings = []
        
        # Simplified vulnerability check - in reality, this would use vulnerability databases
        vulnerable_patterns = {
            "Python": [
                r'django\s*[<>=]*\s*[12]\.',  # Old Django versions
                r'flask\s*[<>=]*\s*0\.',      # Very old Flask versions
            ],
            "Node.js": [
                r'"express"\s*:\s*"[0-3]\.',  # Old Express versions
                r'"lodash"\s*:\s*"[0-3]\.',   # Old Lodash versions
            ]
        }
        
        if language in vulnerable_patterns:
            for pattern in vulnerable_patterns[language]:
                if re.search(pattern, content, re.IGNORECASE):
                    findings.append({
                        "type": "vulnerable_dependency",
                        "title": f"Potentially Vulnerable {language} Dependency",
                        "description": f"Found potentially vulnerable dependency in {language} project",
                        "severity": "Medium",
                        "evidence": {
                            "language": language,
                            "pattern_matched": pattern
                        },
                        "tool": "code_hunter"
                    })
        
        return findings
    
    async def _analyze_git_history(self, repo_path: str) -> List[Dict[str, Any]]:
        """Analyze Git history for sensitive information"""
        findings = []
        
        try:
            if not (Path(repo_path) / ".git").exists():
                return findings
            
            # Use git log to check for sensitive commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "50"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commit_messages = result.stdout.strip().split('\n')
                
                # Check for sensitive commit messages
                sensitive_keywords = [
                    "password", "secret", "key", "token", "credential",
                    "fix security", "remove secret", "hide password"
                ]
                
                for commit_line in commit_messages:
                    commit_message = commit_line.lower()
                    
                    for keyword in sensitive_keywords:
                        if keyword in commit_message:
                            findings.append({
                                "type": "information_disclosure",
                                "title": "Sensitive Information in Git History",
                                "description": f"Git commit message contains sensitive keywords",
                                "severity": "Medium",
                                "evidence": {
                                    "commit": commit_line,
                                    "keyword": keyword
                                },
                                "tool": "code_hunter"
                            })
                            break
        
        except Exception as e:
            self.logger.debug(f"Git history analysis failed: {e}")
        
        return findings
    
    async def _update_hunting_stats(self, hunt_session: Dict[str, Any]):
        """Update hunting statistics"""
        self.hunting_stats["repositories_analyzed"] += 1
        self.hunting_stats["files_scanned"] += hunt_session["repository_info"].get("total_files", 0)
        self.hunting_stats["vulnerabilities_found"] += hunt_session["total_findings"]
        
        # Count secrets found
        secrets_count = len([f for f in hunt_session["findings"] if f["type"] == "hardcoded_secrets"])
        self.hunting_stats["secrets_found"] += secrets_count
        
        # Add to hunting history
        self.hunting_stats["hunting_history"].append({
            "target": hunt_session["target"],
            "files_scanned": hunt_session["repository_info"].get("total_files", 0),
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
        stats_file = Path("learn/code_hunting_stats.json")
        stats_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.hunting_stats, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save hunting stats: {e}")
    
    def get_hunting_stats(self) -> Dict[str, Any]:
        """Get hunting statistics"""
        return {
            "repositories_analyzed": self.hunting_stats["repositories_analyzed"],
            "files_scanned": self.hunting_stats["files_scanned"],
            "vulnerabilities_found": self.hunting_stats["vulnerabilities_found"],
            "secrets_found": self.hunting_stats["secrets_found"],
            "recent_hunts": self.hunting_stats["hunting_history"][-10:]  # Last 10 hunts
        }