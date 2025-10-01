#!/usr/bin/env python3
"""
AEGIS-X Recon Strategist Agent
Intelligence Architect - Plans and executes reconnaissance strategies
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

class ReconStrategist:
    """
    The Recon Strategist is responsible for planning and executing
    comprehensive reconnaissance strategies for each target.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.ReconStrategist")
        self.model_name = "Phi-3-mini-128k-instruct.Q5_K_M"
        self.learning_data = self._load_learning_data()
        
        # Reconnaissance strategies by target type
        self.recon_strategies = {
            "web": self._get_web_recon_strategy(),
            "mobile": self._get_mobile_recon_strategy(),
            "file": self._get_file_recon_strategy(),
            "network": self._get_network_recon_strategy(),
            "code": self._get_code_recon_strategy()
        }
        
        self.logger.info("🧠 Recon Strategist initialized with self-learning capabilities")
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data from previous reconnaissance sessions"""
        learning_file = Path("learn/recon_learning.json")
        
        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load recon learning data: {e}")
        
        return {
            "successful_strategies": {},
            "failed_strategies": {},
            "tool_effectiveness": {},
            "target_insights": {},
            "improvement_notes": []
        }
    
    def _get_web_recon_strategy(self) -> Dict[str, Any]:
        """Get comprehensive web reconnaissance strategy"""
        return {
            "phases": [
                {
                    "name": "Domain Intelligence",
                    "tools": ["amass", "subfinder", "assetfinder", "findomain"],
                    "objectives": [
                        "Discover all subdomains",
                        "Find related domains",
                        "Identify cloud assets",
                        "Map DNS records"
                    ],
                    "self_reflection": "What hidden assets might exist based on this domain structure? Why is this subdomain important? Am I missing anything?"
                },
                {
                    "name": "Web Technology Analysis",
                    "tools": ["httpx", "whatweb", "wappalyzer", "builtwith"],
                    "objectives": [
                        "Identify web technologies",
                        "Detect frameworks and versions",
                        "Find server information",
                        "Analyze security headers"
                    ],
                    "self_reflection": "What vulnerabilities are common in these technologies? Are there known CVEs for these versions?"
                },
                {
                    "name": "Content Discovery",
                    "tools": ["gobuster", "ffuf", "dirsearch", "feroxbuster"],
                    "objectives": [
                        "Discover hidden directories",
                        "Find backup files",
                        "Locate admin panels",
                        "Identify API endpoints"
                    ],
                    "self_reflection": "What sensitive files might exist? Are there common patterns for this technology stack?"
                },
                {
                    "name": "JavaScript Analysis",
                    "tools": ["jsluice", "linkfinder", "secretfinder", "jsbeautifier"],
                    "objectives": [
                        "Extract API endpoints from JS",
                        "Find hardcoded secrets",
                        "Analyze client-side logic",
                        "Discover hidden functionality"
                    ],
                    "self_reflection": "What secrets might be exposed in client-side code? Are there API keys or tokens?"
                },
                {
                    "name": "Cloud Asset Discovery",
                    "tools": ["cloudlist", "cloud_enum", "s3scanner", "gcp-scanner"],
                    "objectives": [
                        "Find cloud storage buckets",
                        "Discover cloud services",
                        "Identify misconfigured resources",
                        "Map cloud infrastructure"
                    ],
                    "self_reflection": "What cloud services might this organization use? Are there naming patterns I can exploit?"
                }
            ],
            "learning_prompts": [
                "What worked best for similar targets?",
                "Should I add dark web reconnaissance?",
                "Are there organization-specific patterns I should look for?",
                "What tools failed last time and why?"
            ]
        }
    
    def _get_mobile_recon_strategy(self) -> Dict[str, Any]:
        """Get mobile application reconnaissance strategy"""
        return {
            "phases": [
                {
                    "name": "App Store Intelligence",
                    "tools": ["gplaycli", "app-store-scraper", "mobile-security-framework"],
                    "objectives": [
                        "Download APK/IPA files",
                        "Analyze app metadata",
                        "Check permissions",
                        "Review app description and updates"
                    ],
                    "self_reflection": "What permissions seem excessive? Are there recent security updates?"
                },
                {
                    "name": "Static Analysis Preparation",
                    "tools": ["apktool", "jadx", "dex2jar", "androguard"],
                    "objectives": [
                        "Decompile application",
                        "Extract resources",
                        "Analyze manifest file",
                        "Prepare for code analysis"
                    ],
                    "self_reflection": "Did I miss any obfuscation techniques? Should I use multiple decompilers?"
                },
                {
                    "name": "Network Endpoint Discovery",
                    "tools": ["mitmproxy", "burp-suite", "charles-proxy"],
                    "objectives": [
                        "Intercept network traffic",
                        "Discover API endpoints",
                        "Analyze authentication mechanisms",
                        "Map data flows"
                    ],
                    "self_reflection": "Are there hidden API endpoints? What authentication methods are used?"
                }
            ],
            "learning_prompts": [
                "What obfuscation techniques did I encounter?",
                "Should I use Frida for dynamic analysis?",
                "What improved from the last mobile hunt?"
            ]
        }
    
    def _get_file_recon_strategy(self) -> Dict[str, Any]:
        """Get file analysis reconnaissance strategy"""
        return {
            "phases": [
                {
                    "name": "File Type Analysis",
                    "tools": ["file", "binwalk", "exiftool", "strings"],
                    "objectives": [
                        "Identify file type and format",
                        "Extract metadata",
                        "Find embedded files",
                        "Analyze file structure"
                    ],
                    "self_reflection": "Is this file what it appears to be? Are there hidden components?"
                },
                {
                    "name": "Content Extraction",
                    "tools": ["shhgit", "trufflehog", "linkfinder", "secretfinder"],
                    "objectives": [
                        "Extract secrets and credentials",
                        "Find URLs and endpoints",
                        "Analyze configuration data",
                        "Discover sensitive information"
                    ],
                    "self_reflection": "Is this file encrypted? Should I try different extraction methods?"
                }
            ],
            "learning_prompts": [
                "What tools failed last time?",
                "Are there file-specific patterns I should look for?"
            ]
        }
    
    def _get_network_recon_strategy(self) -> Dict[str, Any]:
        """Get network reconnaissance strategy"""
        return {
            "phases": [
                {
                    "name": "Network Discovery",
                    "tools": ["nmap", "masscan", "zmap", "naabu"],
                    "objectives": [
                        "Discover live hosts",
                        "Scan for open ports",
                        "Identify services",
                        "Map network topology"
                    ],
                    "self_reflection": "Is this scan too aggressive? Should I use stealth techniques?"
                },
                {
                    "name": "Service Enumeration",
                    "tools": ["nmap -sV", "banner-grabbing", "service-detection"],
                    "objectives": [
                        "Identify service versions",
                        "Grab service banners",
                        "Detect operating systems",
                        "Find service-specific information"
                    ],
                    "self_reflection": "What evasion techniques should I use? Are there IDS/IPS systems?"
                }
            ],
            "learning_prompts": [
                "What evasion techniques worked?",
                "Should I adjust timing and stealth settings?"
            ]
        }
    
    def _get_code_recon_strategy(self) -> Dict[str, Any]:
        """Get code repository reconnaissance strategy"""
        return {
            "phases": [
                {
                    "name": "Repository Analysis",
                    "tools": ["git", "gitleaks", "trufflehog", "repo-supervisor"],
                    "objectives": [
                        "Clone repository",
                        "Analyze commit history",
                        "Find secrets in code",
                        "Map project structure"
                    ],
                    "self_reflection": "Did I check all branches? Should I analyze CI/CD configurations?"
                },
                {
                    "name": "Dependency Analysis",
                    "tools": ["dependency-check", "safety", "audit-tools"],
                    "objectives": [
                        "Identify vulnerable dependencies",
                        "Check for outdated packages",
                        "Analyze security advisories",
                        "Map dependency tree"
                    ],
                    "self_reflection": "What new patterns can I add? Are there supply chain risks?"
                }
            ],
            "learning_prompts": [
                "Did I check for CI/CD secrets?",
                "Should I scan more branches?",
                "What new vulnerability patterns emerged?"
            ]
        }
    
    async def analyze(self, target: str, target_type: str, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze target and generate comprehensive reconnaissance strategy"""
        self.logger.info(f"🧠 Analyzing target for reconnaissance: {target}")
        
        # Generate reconnaissance plan
        recon_plan = await self.plan_reconnaissance(target, target_type, intelligence)
        
        # Execute reconnaissance
        recon_results = await self.execute_reconnaissance(recon_plan)
        
        # Generate analysis summary
        analysis = {
            "target": target,
            "target_type": target_type,
            "recon_plan": recon_plan,
            "recon_results": recon_results,
            "analysis_summary": {
                "total_phases": len(recon_plan.get("phases", [])),
                "completed_phases": len([p for p in recon_results.get("phase_results", []) if p.get("status") == "completed"]),
                "total_findings": sum(len(p.get("findings", [])) for p in recon_results.get("phase_results", [])),
                "high_value_findings": [f for p in recon_results.get("phase_results", []) for f in p.get("findings", []) if f.get("severity", "").lower() in ["high", "critical"]],
                "recommendations": recon_results.get("recommendations", [])
            },
            "self_reflection": {
                "effectiveness": recon_results.get("effectiveness_score", 0.0),
                "improvements": recon_results.get("improvement_suggestions", []),
                "learning_notes": recon_results.get("learning_notes", [])
            }
        }
        
        self.logger.info(f"✅ Reconnaissance analysis completed - {analysis['analysis_summary']['total_findings']} findings")
        return analysis

    async def plan_reconnaissance(self, target: str, target_type: str, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan comprehensive reconnaissance strategy for a target
        """
        self.logger.info(f"🎯 Planning reconnaissance for {target_type} target: {target}")
        
        # Get base strategy for target type
        base_strategy = self.recon_strategies.get(target_type, {})
        
        # Apply intelligence-based customizations
        customized_strategy = await self._customize_strategy(target, target_type, base_strategy, intelligence)
        
        # Apply learning-based improvements
        improved_strategy = self._apply_learning_improvements(target, target_type, customized_strategy)
        
        # Generate self-reflection questions
        reflection_questions = self._generate_reflection_questions(target, target_type, intelligence)
        
        recon_plan = {
            "target": target,
            "target_type": target_type,
            "strategy": improved_strategy,
            "intelligence_context": intelligence,
            "reflection_questions": reflection_questions,
            "estimated_duration": self._estimate_duration(improved_strategy),
            "learning_notes": []
        }
        
        # Log the plan with self-reflection
        self._log_recon_plan_with_reflection(recon_plan)
        
        return recon_plan
    
    async def _customize_strategy(self, target: str, target_type: str, base_strategy: Dict[str, Any], intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Customize reconnaissance strategy based on target intelligence"""
        customized = base_strategy.copy()
        
        if target_type == "web":
            # Customize based on technology stack
            if intelligence.get("technologies"):
                tech_stack = intelligence["technologies"]
                
                # Add framework-specific tools
                if "wordpress" in str(tech_stack).lower():
                    customized["phases"].append({
                        "name": "WordPress Specific",
                        "tools": ["wpscan", "wp-cli", "wordpress-exploit-framework"],
                        "objectives": ["Enumerate WordPress vulnerabilities", "Check plugin security", "Analyze theme vulnerabilities"]
                    })
                
                if "drupal" in str(tech_stack).lower():
                    customized["phases"].append({
                        "name": "Drupal Specific",
                        "tools": ["droopescan", "drupal-exploit"],
                        "objectives": ["Enumerate Drupal vulnerabilities", "Check module security"]
                    })
            
            # Add cloud-specific reconnaissance if cloud services detected
            if intelligence.get("cloud_services"):
                customized["phases"].append({
                    "name": "Cloud Infrastructure Deep Dive",
                    "tools": ["cloud_enum", "s3scanner", "gcp-scanner", "azure-scanner"],
                    "objectives": ["Deep cloud asset discovery", "Check for misconfigurations", "Analyze IAM policies"]
                })
        
        return customized
    
    def _apply_learning_improvements(self, target: str, target_type: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learning-based improvements to the strategy"""
        improved = strategy.copy()
        
        # Check tool effectiveness from past hunts
        for phase in improved.get("phases", []):
            effective_tools = []
            ineffective_tools = []
            
            for tool in phase.get("tools", []):
                effectiveness = self.learning_data.get("tool_effectiveness", {}).get(tool, 0.5)
                
                if effectiveness > 0.7:
                    effective_tools.append(tool)
                elif effectiveness < 0.3:
                    ineffective_tools.append(tool)
            
            # Prioritize effective tools
            if effective_tools:
                phase["priority_tools"] = effective_tools
            
            # Add learning notes about ineffective tools
            if ineffective_tools:
                phase["learning_notes"] = [f"Tools with low effectiveness: {', '.join(ineffective_tools)}"]
        
        return improved
    
    def _generate_reflection_questions(self, target: str, target_type: str, intelligence: Dict[str, Any]) -> List[str]:
        """Generate self-reflection questions for the reconnaissance"""
        base_questions = [
            "What hidden assets might exist based on this target?",
            "Why is this reconnaissance approach important?",
            "Am I missing anything obvious?",
            "What did I learn from similar targets before?",
            "How can I improve this reconnaissance strategy?"
        ]
        
        # Add target-specific questions
        if target_type == "web":
            base_questions.extend([
                "Are there organization-specific naming patterns I should exploit?",
                "What cloud services might this organization use?",
                "Should I add dark web reconnaissance?"
            ])
        elif target_type == "mobile":
            base_questions.extend([
                "What obfuscation techniques might be used?",
                "Should I use dynamic analysis with Frida?",
                "Are there platform-specific vulnerabilities to consider?"
            ])
        
        return base_questions
    
    def _estimate_duration(self, strategy: Dict[str, Any]) -> int:
        """Estimate reconnaissance duration in minutes"""
        base_duration = 0
        
        for phase in strategy.get("phases", []):
            tool_count = len(phase.get("tools", []))
            objective_count = len(phase.get("objectives", []))
            
            # Estimate 2-5 minutes per tool depending on complexity
            phase_duration = tool_count * 3 + objective_count * 2
            base_duration += phase_duration
        
        return min(base_duration, 45)  # Cap at 45 minutes per target
    
    def _log_recon_plan_with_reflection(self, recon_plan: Dict[str, Any]):
        """Log reconnaissance plan with self-reflection"""
        self.logger.info(f"📋 Reconnaissance plan created for: {recon_plan['target']}")
        self.logger.info(f"⏱️ Estimated duration: {recon_plan['estimated_duration']} minutes")
        self.logger.info(f"🔍 Phases: {len(recon_plan['strategy'].get('phases', []))}")
        
        # Log self-reflection questions
        for question in recon_plan['reflection_questions']:
            self.logger.debug(f"🤔 Self-reflection: {question}")
    
    async def execute_reconnaissance(self, recon_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the reconnaissance plan and collect intelligence
        """
        self.logger.info(f"🚀 Executing reconnaissance for: {recon_plan['target']}")
        
        results = {
            "target": recon_plan["target"],
            "target_type": recon_plan["target_type"],
            "start_time": datetime.now().isoformat(),
            "phases_completed": [],
            "intelligence_gathered": {},
            "tools_used": [],
            "learning_data": []
        }
        
        # Execute each phase
        for phase in recon_plan["strategy"].get("phases", []):
            phase_result = await self._execute_phase(phase, recon_plan["target"])
            results["phases_completed"].append(phase_result)
            results["tools_used"].extend(phase.get("tools", []))
        
        results["end_time"] = datetime.now().isoformat()
        results["duration_minutes"] = self._calculate_duration(results["start_time"], results["end_time"])
        
        # Store learning data
        await self._store_recon_learning(recon_plan, results)
        
        self.logger.info(f"✅ Reconnaissance completed in {results['duration_minutes']:.2f} minutes")
        return results
    
    async def _execute_phase(self, phase: Dict[str, Any], target: str) -> Dict[str, Any]:
        """Execute a single reconnaissance phase"""
        self.logger.info(f"🔍 Executing phase: {phase['name']}")
        
        phase_result = {
            "name": phase["name"],
            "tools_executed": [],
            "objectives_met": [],
            "intelligence_gathered": {},
            "errors": []
        }
        
        # Execute tools in the phase
        for tool in phase.get("tools", []):
            try:
                tool_result = await self._execute_tool(tool, target, phase["objectives"])
                phase_result["tools_executed"].append({
                    "tool": tool,
                    "success": tool_result["success"],
                    "data": tool_result.get("data", {}),
                    "duration": tool_result.get("duration", 0)
                })
                
                if tool_result["success"]:
                    phase_result["intelligence_gathered"].update(tool_result.get("data", {}))
                
            except Exception as e:
                self.logger.error(f"❌ Tool {tool} failed: {str(e)}")
                phase_result["errors"].append(f"{tool}: {str(e)}")
        
        return phase_result
    
    async def _execute_tool(self, tool: str, target: str, objectives: List[str]) -> Dict[str, Any]:
        """Execute a specific reconnaissance tool"""
        # This is a placeholder for actual tool execution
        # In a real implementation, this would call the actual tools
        
        self.logger.debug(f"🛠️ Executing tool: {tool} on {target}")
        
        # Simulate tool execution
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "success": True,
            "data": {
                f"{tool}_results": f"Mock results for {tool} on {target}"
            },
            "duration": 0.1
        }
    
    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """Calculate duration between two ISO timestamps"""
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        return (end - start).total_seconds() / 60
    
    async def _store_recon_learning(self, recon_plan: Dict[str, Any], results: Dict[str, Any]):
        """Store reconnaissance learning data for future improvement"""
        learning_entry = {
            "target": recon_plan["target"],
            "target_type": recon_plan["target_type"],
            "strategy_used": recon_plan["strategy"]["phases"],
            "tools_used": results["tools_used"],
            "duration": results["duration_minutes"],
            "success_rate": len(results["phases_completed"]) / len(recon_plan["strategy"].get("phases", [])),
            "timestamp": datetime.now().isoformat(),
            "learning_notes": []
        }
        
        # Update tool effectiveness
        for phase in results["phases_completed"]:
            for tool_result in phase["tools_executed"]:
                tool = tool_result["tool"]
                success = tool_result["success"]
                
                current_effectiveness = self.learning_data.get("tool_effectiveness", {}).get(tool, 0.5)
                learning_rate = 0.1
                
                if success:
                    new_effectiveness = current_effectiveness + (1.0 - current_effectiveness) * learning_rate
                else:
                    new_effectiveness = current_effectiveness - current_effectiveness * learning_rate
                
                self.learning_data.setdefault("tool_effectiveness", {})[tool] = new_effectiveness
        
        # Store learning data
        self.learning_data.setdefault("recon_sessions", []).append(learning_entry)
        
        # Save to file
        learning_file = Path("learn/recon_learning.json")
        learning_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save recon learning data: {e}")
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from reconnaissance learning data"""
        if not self.learning_data.get("recon_sessions"):
            return {"message": "No learning data available yet"}
        
        sessions = self.learning_data["recon_sessions"]
        tool_effectiveness = self.learning_data.get("tool_effectiveness", {})
        
        # Calculate statistics
        avg_duration = sum(s["duration"] for s in sessions) / len(sessions)
        avg_success_rate = sum(s["success_rate"] for s in sessions) / len(sessions)
        
        # Find most effective tools
        most_effective_tools = sorted(tool_effectiveness.items(), key=lambda x: x[1], reverse=True)[:5]
        least_effective_tools = sorted(tool_effectiveness.items(), key=lambda x: x[1])[:5]
        
        return {
            "total_sessions": len(sessions),
            "average_duration_minutes": avg_duration,
            "average_success_rate": avg_success_rate,
            "most_effective_tools": most_effective_tools,
            "least_effective_tools": least_effective_tools,
            "improvement_suggestions": self._generate_improvement_suggestions(sessions, tool_effectiveness)
        }
    
    def _generate_improvement_suggestions(self, sessions: List[Dict[str, Any]], tool_effectiveness: Dict[str, float]) -> List[str]:
        """Generate improvement suggestions based on learning data"""
        suggestions = []
        
        # Suggest removing ineffective tools
        ineffective_tools = [tool for tool, eff in tool_effectiveness.items() if eff < 0.3]
        if ineffective_tools:
            suggestions.append(f"Consider removing or replacing ineffective tools: {', '.join(ineffective_tools)}")
        
        # Suggest optimizing duration
        long_sessions = [s for s in sessions if s["duration"] > 30]
        if len(long_sessions) > len(sessions) * 0.3:
            suggestions.append("Consider optimizing reconnaissance phases to reduce duration")
        
        # Suggest adding new tools for low success rates
        low_success_sessions = [s for s in sessions if s["success_rate"] < 0.7]
        if len(low_success_sessions) > len(sessions) * 0.3:
            suggestions.append("Consider adding more tools or improving existing tool configurations")
        
        return suggestions