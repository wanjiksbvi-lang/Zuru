#!/usr/bin/env python3
"""
AEGIS-X Learning Engine
Self-Learning and Evolution System
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import statistics

@dataclass
class LearningMetric:
    """Represents a learning metric"""
    name: str
    value: float
    timestamp: datetime
    context: Dict[str, Any]

@dataclass
class ImprovementSuggestion:
    """Represents an improvement suggestion"""
    category: str
    suggestion: str
    priority: str
    estimated_impact: float
    implementation_effort: str

class LearningEngine:
    """
    The Learning Engine continuously learns from each hunt,
    adapts strategies, and evolves the system's intelligence.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AEGIS-X.LearningEngine")
        self.learning_data = self._load_learning_data()
        self.metrics_history = self._load_metrics_history()
        self.improvement_tracker = self._load_improvement_tracker()
        
        # Learning parameters
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.7
        self.evolution_cycles = 0
        
        self.logger.info("🧠 Learning Engine initialized with adaptive intelligence")
    
    async def learn_from_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from a completed hunting session"""
        self.logger.info(f"🧠 Learning from session: {session_data.get('session_id', 'unknown')}")
        
        learning_results = {
            "session_id": session_data.get("session_id"),
            "learning_timestamp": datetime.now().isoformat(),
            "insights_gained": [],
            "adaptations_made": [],
            "performance_improvements": {}
        }
        
        try:
            # Analyze findings patterns
            findings = session_data.get("findings", [])
            if findings:
                pattern_insights = self._analyze_findings_patterns(findings)
                learning_results["insights_gained"].extend(pattern_insights)
            
            # Analyze evidence quality
            evidence_packages = session_data.get("evidence_packages", [])
            if evidence_packages:
                evidence_insights = self._analyze_evidence_quality(evidence_packages)
                learning_results["insights_gained"].extend(evidence_insights)
            
            # Analyze quality metrics
            quality_metrics = session_data.get("quality_metrics", {})
            if quality_metrics:
                quality_insights = self._analyze_quality_metrics(quality_metrics)
                learning_results["insights_gained"].extend(quality_insights)
            
            # Update learning data
            self._update_learning_data(session_data)
            
            # Save learning results
            await self._save_learning_results(learning_results)
            
            self.logger.info(f"✅ Learning completed - {len(learning_results['insights_gained'])} insights gained")
            
            return learning_results
            
        except Exception as e:
            self.logger.error(f"Learning from session failed: {str(e)}")
            learning_results["error"] = str(e)
            return learning_results
    
    def _analyze_findings_patterns(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Analyze patterns in findings"""
        insights = []
        
        # Analyze severity distribution
        severity_counts = {}
        for finding in findings:
            severity = finding.get("severity", "unknown").lower()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        if severity_counts:
            most_common = max(severity_counts, key=severity_counts.get)
            insights.append(f"Most common vulnerability severity: {most_common}")
        
        # Analyze vulnerability types
        vuln_types = {}
        for finding in findings:
            title = finding.get("title", "").lower()
            if "xss" in title:
                vuln_types["xss"] = vuln_types.get("xss", 0) + 1
            elif "sql" in title:
                vuln_types["sqli"] = vuln_types.get("sqli", 0) + 1
            elif "ssrf" in title:
                vuln_types["ssrf"] = vuln_types.get("ssrf", 0) + 1
        
        if vuln_types:
            most_common_type = max(vuln_types, key=vuln_types.get)
            insights.append(f"Most common vulnerability type: {most_common_type}")
        
        return insights
    
    def _analyze_evidence_quality(self, evidence_packages: List[Dict[str, Any]]) -> List[str]:
        """Analyze evidence quality patterns"""
        insights = []
        
        if evidence_packages:
            quality_scores = [
                ep.get("metadata", {}).get("evidence_quality_score", 0.0)
                for ep in evidence_packages
            ]
            
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                insights.append(f"Average evidence quality score: {avg_quality:.2f}")
                
                if avg_quality < 0.7:
                    insights.append("Evidence quality below threshold - need improvement")
                elif avg_quality > 0.9:
                    insights.append("Excellent evidence quality maintained")
        
        return insights
    
    def _analyze_quality_metrics(self, quality_metrics: Dict[str, Any]) -> List[str]:
        """Analyze overall quality metrics"""
        insights = []
        
        overall_score = quality_metrics.get("overall_quality_score", 0.0)
        verification_rate = quality_metrics.get("verification_rate", 0.0)
        
        insights.append(f"Overall quality score: {overall_score:.2f}")
        insights.append(f"Verification rate: {verification_rate:.2f}")
        
        if verification_rate < 0.5:
            insights.append("Low verification rate - need better vulnerability detection")
        elif verification_rate > 0.8:
            insights.append("High verification rate - excellent detection accuracy")
        
        return insights
    
    def _update_learning_data(self, session_data: Dict[str, Any]):
        """Update learning data with session results"""
        # Update session count
        self.learning_data["total_sessions"] = self.learning_data.get("total_sessions", 0) + 1
        
        # Update findings count
        findings_count = len(session_data.get("findings", []))
        self.learning_data["total_findings"] = self.learning_data.get("total_findings", 0) + findings_count
        
        # Update quality metrics history
        quality_metrics = session_data.get("quality_metrics", {})
        if quality_metrics:
            if "quality_history" not in self.learning_data:
                self.learning_data["quality_history"] = []
            
            self.learning_data["quality_history"].append({
                "timestamp": datetime.now().isoformat(),
                "metrics": quality_metrics
            })
    
    async def _save_learning_results(self, learning_results: Dict[str, Any]):
        """Save learning results to file"""
        learning_dir = Path("learn")
        learning_dir.mkdir(exist_ok=True)
        
        results_file = learning_dir / f"learning_results_{int(datetime.now().timestamp())}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(learning_results, f, indent=2, default=str)
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load comprehensive learning data"""
        learning_file = Path("learn/master_learning.json")
        
        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load learning data: {e}")
        
        return {
            "hunt_sessions": [],
            "tool_effectiveness": {},
            "vulnerability_patterns": {},
            "target_insights": {},
            "strategy_success_rates": {},
            "performance_trends": {},
            "adaptation_history": [],
            "evolution_milestones": []
        }
    
    def _load_metrics_history(self) -> List[LearningMetric]:
        """Load metrics history"""
        metrics_file = Path("learn/metrics_history.json")
        
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    return [
                        LearningMetric(
                            name=m["name"],
                            value=m["value"],
                            timestamp=datetime.fromisoformat(m["timestamp"]),
                            context=m["context"]
                        ) for m in data
                    ]
            except Exception as e:
                self.logger.warning(f"Failed to load metrics history: {e}")
        
        return []
    
    def _load_improvement_tracker(self) -> Dict[str, Any]:
        """Load improvement tracking data"""
        tracker_file = Path("learn/improvement_tracker.json")
        
        if tracker_file.exists():
            try:
                with open(tracker_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load improvement tracker: {e}")
        
        return {
            "suggestions_generated": [],
            "suggestions_implemented": [],
            "impact_measurements": {},
            "success_stories": []
        }
    
    async def analyze_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a completed hunt session and extract learning insights"""
        self.logger.info(f"🧠 Analyzing session for learning: {session_data.get('session_id')}")
        
        # Extract key metrics from session
        session_metrics = {
            "session_id": session_data.get("session_id"),
            "duration": session_data.get("duration", "00:00:00"),
            "targets_processed": len(session_data.get("targets", [])),
            "total_findings": len(session_data.get("findings", [])),
            "verified_findings": len(session_data.get("verified_findings", [])),
            "success_rate": len(session_data.get("verified_findings", [])) / max(len(session_data.get("findings", [])), 1),
            "target_types": list(set([self._extract_target_type(t) for t in session_data.get("targets", [])]))
        }
        
        # Analyze tool effectiveness
        tool_analysis = await self._analyze_session_tools(session_data)
        
        # Analyze vulnerability patterns
        vuln_analysis = await self._analyze_session_vulnerabilities(session_data)
        
        # Generate learning insights
        learning_insights = {
            "session_metrics": session_metrics,
            "tool_effectiveness": tool_analysis,
            "vulnerability_patterns": vuln_analysis,
            "performance_assessment": self._assess_session_performance(session_data),
            "improvement_opportunities": self._identify_improvement_opportunities(session_data),
            "learning_notes": self._generate_session_learning_notes(session_data)
        }
        
        # Update learning system
        await self.update(session_data)
        
        self.logger.info(f"✅ Session analysis completed - {len(learning_insights['improvement_opportunities'])} improvements identified")
        return learning_insights
    
    async def _analyze_session_tools(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze tool effectiveness in the session"""
        tools_used = []
        for target in session_data.get("targets", []):
            for finding in target.get("findings", []):
                tools_used.extend(finding.get("tools_used", []))
        
        return {
            "tools_used": list(set(tools_used)),
            "tool_count": len(set(tools_used)),
            "effectiveness_score": len(session_data.get("verified_findings", [])) / max(len(tools_used), 1)
        }
    
    async def _analyze_session_vulnerabilities(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze vulnerability patterns found in the session"""
        vulnerabilities = []
        for finding in session_data.get("verified_findings", []):
            vulnerabilities.append({
                "type": finding.get("vulnerability_type", "unknown"),
                "severity": finding.get("severity", "unknown"),
                "target_type": finding.get("target_type", "unknown")
            })
        
        return {
            "vulnerability_types": list(set([v["type"] for v in vulnerabilities])),
            "severity_distribution": {
                "critical": len([v for v in vulnerabilities if v["severity"].lower() == "critical"]),
                "high": len([v for v in vulnerabilities if v["severity"].lower() == "high"]),
                "medium": len([v for v in vulnerabilities if v["severity"].lower() == "medium"]),
                "low": len([v for v in vulnerabilities if v["severity"].lower() == "low"])
            },
            "patterns": vulnerabilities
        }
    
    def _assess_session_performance(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall session performance"""
        total_findings = len(session_data.get("findings", []))
        verified_findings = len(session_data.get("verified_findings", []))
        targets_processed = len(session_data.get("targets", []))
        
        performance_score = 0.0
        if total_findings > 0:
            performance_score = (verified_findings / total_findings) * 100
        
        return {
            "performance_score": performance_score,
            "verification_rate": verified_findings / max(total_findings, 1),
            "findings_per_target": total_findings / max(targets_processed, 1),
            "assessment": "Excellent" if performance_score >= 80 else "Good" if performance_score >= 60 else "Needs Improvement"
        }
    
    def _identify_improvement_opportunities(self, session_data: Dict[str, Any]) -> List[str]:
        """Identify opportunities for improvement based on session data"""
        opportunities = []
        
        if len(session_data.get("verified_findings", [])) == 0:
            opportunities.append("No verified findings - consider expanding tool arsenal or improving verification protocols")
        
        if len(session_data.get("findings", [])) == 0:
            opportunities.append("No findings detected - consider adding more vulnerability scanning techniques")
        
        for target in session_data.get("targets", []):
            if target.get("error"):
                opportunities.append(f"Target processing failed: {target['error']} - investigate and fix")
        
        return opportunities
    
    def _generate_session_learning_notes(self, session_data: Dict[str, Any]) -> List[str]:
        """Generate learning notes from the session"""
        notes = []
        
        # Note successful patterns
        if session_data.get("verified_findings"):
            notes.append("Successfully verified findings - continue using current verification protocols")
        
        # Note target type patterns
        target_types = set([self._extract_target_type(t) for t in session_data.get("targets", [])])
        notes.append(f"Processed target types: {', '.join(target_types)}")
        
        # Note duration insights
        duration = session_data.get("duration", "00:00:00")
        notes.append(f"Session completed in {duration} - monitor for optimization opportunities")
        
        return notes
    
    def _extract_target_type(self, target_data: Dict[str, Any]) -> str:
        """Extract target type from target data, handling both dict and ClassificationResult"""
        classification = target_data.get("classification")
        if classification:
            if hasattr(classification, 'target_type'):
                # ClassificationResult object
                return classification.target_type.value if hasattr(classification.target_type, 'value') else str(classification.target_type)
            elif isinstance(classification, dict):
                # Dictionary
                return classification.get("target_type", "unknown")
        return "unknown"

    async def update(self, learning_data: Dict[str, Any]):
        """Update the learning system with new data from a hunt session"""
        self.logger.info(f"🔄 Updating learning system with session: {learning_data.get('session_id')}")
        
        # Store session data
        session_entry = {
            **learning_data,
            "processed_at": datetime.now().isoformat()
        }
        self.learning_data["hunt_sessions"].append(session_entry)
        
        # Update tool effectiveness
        await self._update_tool_effectiveness(learning_data)
        
        # Update vulnerability patterns
        await self._update_vulnerability_patterns(learning_data)
        
        # Update target insights
        await self._update_target_insights(learning_data)
        
        # Update strategy success rates
        await self._update_strategy_success_rates(learning_data)
        
        # Analyze performance trends
        await self._analyze_performance_trends()
        
        # Generate improvement suggestions
        suggestions = await self._generate_improvement_suggestions()
        
        # Check for adaptation triggers
        await self._check_adaptation_triggers()
        
        # Save all learning data
        await self._save_learning_data()
        
        self.logger.info("✅ Learning system updated successfully")
    
    async def _update_tool_effectiveness(self, session_data: Dict[str, Any]):
        """Update tool effectiveness metrics"""
        tools_used = session_data.get("tools_used", [])
        success_rate = session_data.get("success_rate", 0.0)
        findings_count = session_data.get("findings_count", 0)
        
        for tool in tools_used:
            if tool not in self.learning_data["tool_effectiveness"]:
                self.learning_data["tool_effectiveness"][tool] = {
                    "usage_count": 0,
                    "success_rate": 0.5,
                    "findings_generated": 0,
                    "avg_execution_time": 0.0,
                    "reliability_score": 0.5,
                    "last_updated": datetime.now().isoformat()
                }
            
            tool_data = self.learning_data["tool_effectiveness"][tool]
            
            # Update metrics using exponential moving average
            tool_data["usage_count"] += 1
            tool_data["success_rate"] = self._update_moving_average(
                tool_data["success_rate"], success_rate, self.learning_rate
            )
            tool_data["findings_generated"] += findings_count
            tool_data["last_updated"] = datetime.now().isoformat()
            
            # Calculate reliability score
            tool_data["reliability_score"] = min(1.0, 
                (tool_data["success_rate"] * 0.7) + 
                (min(1.0, tool_data["usage_count"] / 10) * 0.3)
            )
        
        self.logger.debug(f"Updated effectiveness for {len(tools_used)} tools")
    
    async def _update_vulnerability_patterns(self, session_data: Dict[str, Any]):
        """Update vulnerability pattern recognition"""
        target_types = session_data.get("target_types", [])
        findings_count = session_data.get("findings_count", 0)
        
        for target_type in target_types:
            if target_type not in self.learning_data["vulnerability_patterns"]:
                self.learning_data["vulnerability_patterns"][target_type] = {
                    "common_vulnerabilities": {},
                    "success_indicators": [],
                    "failure_patterns": [],
                    "optimal_strategies": [],
                    "discovery_rate": 0.0
                }
            
            pattern_data = self.learning_data["vulnerability_patterns"][target_type]
            
            # Update discovery rate
            pattern_data["discovery_rate"] = self._update_moving_average(
                pattern_data["discovery_rate"], 
                findings_count / max(1, len(session_data.get("targets", []))),
                self.learning_rate
            )
        
        self.logger.debug(f"Updated vulnerability patterns for {len(target_types)} target types")
    
    async def _update_target_insights(self, session_data: Dict[str, Any]):
        """Update target-specific insights"""
        session_id = session_data.get("session_id")
        targets = session_data.get("targets", [])
        
        for target in targets:
            target_key = self._normalize_target(target)
            
            if target_key not in self.learning_data["target_insights"]:
                self.learning_data["target_insights"][target_key] = {
                    "assessment_count": 0,
                    "avg_findings": 0.0,
                    "common_vulnerabilities": {},
                    "best_tools": [],
                    "response_patterns": {},
                    "security_posture_trend": []
                }
            
            insight_data = self.learning_data["target_insights"][target_key]
            insight_data["assessment_count"] += 1
            
            # Update average findings
            current_findings = session_data.get("findings_count", 0)
            insight_data["avg_findings"] = self._update_moving_average(
                insight_data["avg_findings"], current_findings, self.learning_rate
            )
            
            # Track security posture trend
            insight_data["security_posture_trend"].append({
                "session_id": session_id,
                "findings_count": current_findings,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 10 assessments for trend analysis
            if len(insight_data["security_posture_trend"]) > 10:
                insight_data["security_posture_trend"] = insight_data["security_posture_trend"][-10:]
        
        self.logger.debug(f"Updated insights for {len(targets)} targets")
    
    async def _update_strategy_success_rates(self, session_data: Dict[str, Any]):
        """Update strategy success rates"""
        # This would track which hunting strategies work best
        strategy_used = session_data.get("strategy_used", "default")
        success_rate = session_data.get("success_rate", 0.0)
        
        if strategy_used not in self.learning_data["strategy_success_rates"]:
            self.learning_data["strategy_success_rates"][strategy_used] = {
                "usage_count": 0,
                "success_rate": 0.5,
                "avg_duration": 0.0,
                "findings_per_target": 0.0
            }
        
        strategy_data = self.learning_data["strategy_success_rates"][strategy_used]
        strategy_data["usage_count"] += 1
        strategy_data["success_rate"] = self._update_moving_average(
            strategy_data["success_rate"], success_rate, self.learning_rate
        )
        
        self.logger.debug(f"Updated strategy success rate for: {strategy_used}")
    
    async def _analyze_performance_trends(self):
        """Analyze performance trends over time"""
        recent_sessions = self._get_recent_sessions(days=30)
        
        if len(recent_sessions) < 2:
            return
        
        # Calculate trend metrics
        trends = {
            "findings_per_session": [],
            "success_rates": [],
            "duration_efficiency": [],
            "tool_reliability": []
        }
        
        for session in recent_sessions:
            trends["findings_per_session"].append(session.get("findings_count", 0))
            trends["success_rates"].append(session.get("success_rate", 0.0))
            
            # Calculate duration efficiency (findings per minute)
            duration = session.get("duration_minutes", 1)
            findings = session.get("findings_count", 0)
            trends["duration_efficiency"].append(findings / duration)
        
        # Store trend analysis
        self.learning_data["performance_trends"] = {
            "analysis_date": datetime.now().isoformat(),
            "session_count": len(recent_sessions),
            "avg_findings_per_session": statistics.mean(trends["findings_per_session"]),
            "avg_success_rate": statistics.mean(trends["success_rates"]),
            "avg_efficiency": statistics.mean(trends["duration_efficiency"]),
            "trends": {
                "findings_trend": self._calculate_trend(trends["findings_per_session"]),
                "success_trend": self._calculate_trend(trends["success_rates"]),
                "efficiency_trend": self._calculate_trend(trends["duration_efficiency"])
            }
        }
        
        self.logger.debug("Performance trends analyzed")
    
    async def _generate_improvement_suggestions(self) -> List[ImprovementSuggestion]:
        """Generate improvement suggestions based on learning data"""
        suggestions = []
        
        # Analyze tool effectiveness
        tool_suggestions = self._analyze_tool_effectiveness()
        suggestions.extend(tool_suggestions)
        
        # Analyze vulnerability patterns
        pattern_suggestions = self._analyze_vulnerability_patterns()
        suggestions.extend(pattern_suggestions)
        
        # Analyze performance trends
        performance_suggestions = self._analyze_performance_for_improvements()
        suggestions.extend(performance_suggestions)
        
        # Store suggestions
        for suggestion in suggestions:
            self.improvement_tracker["suggestions_generated"].append({
                **asdict(suggestion),
                "generated_at": datetime.now().isoformat(),
                "status": "pending"
            })
        
        self.logger.info(f"Generated {len(suggestions)} improvement suggestions")
        return suggestions
    
    def _analyze_tool_effectiveness(self) -> List[ImprovementSuggestion]:
        """Analyze tool effectiveness and suggest improvements"""
        suggestions = []
        
        for tool, data in self.learning_data["tool_effectiveness"].items():
            reliability = data["reliability_score"]
            usage_count = data["usage_count"]
            
            if reliability < 0.3 and usage_count > 5:
                suggestions.append(ImprovementSuggestion(
                    category="tool_optimization",
                    suggestion=f"Consider replacing or improving {tool} - low reliability score: {reliability:.2f}",
                    priority="medium",
                    estimated_impact=0.6,
                    implementation_effort="medium"
                ))
            
            elif reliability > 0.8 and usage_count > 10:
                suggestions.append(ImprovementSuggestion(
                    category="tool_optimization",
                    suggestion=f"Increase usage of {tool} - high reliability score: {reliability:.2f}",
                    priority="low",
                    estimated_impact=0.4,
                    implementation_effort="low"
                ))
        
        return suggestions
    
    def _analyze_vulnerability_patterns(self) -> List[ImprovementSuggestion]:
        """Analyze vulnerability patterns and suggest improvements"""
        suggestions = []
        
        for target_type, pattern_data in self.learning_data["vulnerability_patterns"].items():
            discovery_rate = pattern_data["discovery_rate"]
            
            if discovery_rate < 0.2:
                suggestions.append(ImprovementSuggestion(
                    category="strategy_improvement",
                    suggestion=f"Improve hunting strategy for {target_type} - low discovery rate: {discovery_rate:.2f}",
                    priority="high",
                    estimated_impact=0.8,
                    implementation_effort="high"
                ))
        
        return suggestions
    
    def _analyze_performance_for_improvements(self) -> List[ImprovementSuggestion]:
        """Analyze performance trends for improvement opportunities"""
        suggestions = []
        
        trends = self.learning_data.get("performance_trends", {}).get("trends", {})
        
        if trends.get("efficiency_trend", 0) < -0.1:
            suggestions.append(ImprovementSuggestion(
                category="performance_optimization",
                suggestion="Efficiency is declining - optimize tool selection and parallel processing",
                priority="high",
                estimated_impact=0.7,
                implementation_effort="medium"
            ))
        
        if trends.get("success_trend", 0) < -0.05:
            suggestions.append(ImprovementSuggestion(
                category="accuracy_improvement",
                suggestion="Success rate is declining - review verification protocols and tool configurations",
                priority="high",
                estimated_impact=0.9,
                implementation_effort="high"
            ))
        
        return suggestions
    
    async def _check_adaptation_triggers(self):
        """Check if adaptation should be triggered"""
        recent_performance = self._get_recent_performance_metrics()
        
        adaptation_needed = False
        adaptation_reasons = []
        
        # Check success rate threshold
        if recent_performance.get("avg_success_rate", 1.0) < self.adaptation_threshold:
            adaptation_needed = True
            adaptation_reasons.append("Low success rate")
        
        # Check tool reliability
        unreliable_tools = [
            tool for tool, data in self.learning_data["tool_effectiveness"].items()
            if data["reliability_score"] < 0.4 and data["usage_count"] > 5
        ]
        
        if len(unreliable_tools) > 3:
            adaptation_needed = True
            adaptation_reasons.append(f"Multiple unreliable tools: {unreliable_tools}")
        
        # Check performance trends
        trends = self.learning_data.get("performance_trends", {}).get("trends", {})
        if trends.get("efficiency_trend", 0) < -0.2:
            adaptation_needed = True
            adaptation_reasons.append("Declining efficiency trend")
        
        if adaptation_needed:
            await self._trigger_adaptation(adaptation_reasons)
    
    async def _trigger_adaptation(self, reasons: List[str]):
        """Trigger system adaptation"""
        self.logger.info(f"🔄 Triggering adaptation due to: {', '.join(reasons)}")
        
        adaptation_entry = {
            "adaptation_id": f"adapt_{int(datetime.now().timestamp())}",
            "triggered_at": datetime.now().isoformat(),
            "reasons": reasons,
            "changes_made": [],
            "expected_improvements": []
        }
        
        # Implement adaptation strategies
        changes_made = []
        
        # Strategy 1: Update tool selection priorities
        if "Low success rate" in reasons:
            changes_made.append("Updated tool selection to prioritize high-reliability tools")
            await self._adapt_tool_selection()
        
        # Strategy 2: Adjust hunting strategies
        if "Declining efficiency trend" in reasons:
            changes_made.append("Optimized hunting strategies for better efficiency")
            await self._adapt_hunting_strategies()
        
        # Strategy 3: Update verification protocols
        if any("unreliable" in reason for reason in reasons):
            changes_made.append("Enhanced verification protocols")
            await self._adapt_verification_protocols()
        
        adaptation_entry["changes_made"] = changes_made
        self.learning_data["adaptation_history"].append(adaptation_entry)
        
        self.evolution_cycles += 1
        self.logger.info(f"✅ Adaptation completed - Evolution cycle: {self.evolution_cycles}")
    
    async def _adapt_tool_selection(self):
        """Adapt tool selection based on effectiveness data"""
        # Prioritize high-reliability tools
        reliable_tools = [
            tool for tool, data in self.learning_data["tool_effectiveness"].items()
            if data["reliability_score"] > 0.7
        ]
        
        # Update tool selection preferences
        self.learning_data["tool_preferences"] = {
            "high_priority": reliable_tools,
            "low_priority": [
                tool for tool, data in self.learning_data["tool_effectiveness"].items()
                if data["reliability_score"] < 0.4
            ],
            "updated_at": datetime.now().isoformat()
        }
    
    async def _adapt_hunting_strategies(self):
        """Adapt hunting strategies based on success patterns"""
        # Identify most successful strategies
        successful_strategies = [
            strategy for strategy, data in self.learning_data["strategy_success_rates"].items()
            if data["success_rate"] > 0.7
        ]
        
        # Update strategy preferences
        self.learning_data["strategy_preferences"] = {
            "preferred_strategies": successful_strategies,
            "strategy_weights": {
                strategy: data["success_rate"] 
                for strategy, data in self.learning_data["strategy_success_rates"].items()
            },
            "updated_at": datetime.now().isoformat()
        }
    
    async def _adapt_verification_protocols(self):
        """Adapt verification protocols to improve reliability"""
        # Increase verification strictness
        self.learning_data["verification_config"] = {
            "strictness_level": "high",
            "additional_checks": True,
            "cross_validation": True,
            "updated_at": datetime.now().isoformat()
        }
    
    def _get_recent_sessions(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent hunt sessions"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_sessions = []
        for session in self.learning_data["hunt_sessions"]:
            session_date = datetime.fromisoformat(session.get("processed_at", "1970-01-01"))
            if session_date > cutoff_date:
                recent_sessions.append(session)
        
        return recent_sessions
    
    def _get_recent_performance_metrics(self) -> Dict[str, float]:
        """Get recent performance metrics"""
        recent_sessions = self._get_recent_sessions(days=7)
        
        if not recent_sessions:
            return {}
        
        success_rates = [s.get("success_rate", 0.0) for s in recent_sessions]
        findings_counts = [s.get("findings_count", 0) for s in recent_sessions]
        
        return {
            "avg_success_rate": statistics.mean(success_rates),
            "avg_findings": statistics.mean(findings_counts),
            "session_count": len(recent_sessions)
        }
    
    def _update_moving_average(self, current_avg: float, new_value: float, learning_rate: float) -> float:
        """Update moving average with new value"""
        return current_avg * (1 - learning_rate) + new_value * learning_rate
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction (-1 to 1)"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        if n * x2_sum - x_sum * x_sum == 0:
            return 0.0
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        
        # Normalize slope to -1 to 1 range
        return max(-1.0, min(1.0, slope))
    
    def _normalize_target(self, target: str) -> str:
        """Normalize target for consistent tracking"""
        # Remove protocol and www
        normalized = target.lower()
        normalized = normalized.replace("https://", "").replace("http://", "")
        normalized = normalized.replace("www.", "")
        
        # Remove trailing slash
        if normalized.endswith("/"):
            normalized = normalized[:-1]
        
        return normalized
    
    async def _save_learning_data(self):
        """Save all learning data to files"""
        # Save main learning data
        learning_file = Path("learn/master_learning.json")
        learning_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save learning data: {e}")
        
        # Save metrics history
        metrics_file = Path("learn/metrics_history.json")
        try:
            metrics_data = [
                {
                    "name": m.name,
                    "value": m.value,
                    "timestamp": m.timestamp.isoformat(),
                    "context": m.context
                } for m in self.metrics_history
            ]
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save metrics history: {e}")
        
        # Save improvement tracker
        tracker_file = Path("learn/improvement_tracker.json")
        try:
            with open(tracker_file, 'w') as f:
                json.dump(self.improvement_tracker, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save improvement tracker: {e}")
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get comprehensive learning insights"""
        recent_sessions = self._get_recent_sessions(days=30)
        
        insights = {
            "evolution_cycles": self.evolution_cycles,
            "total_sessions": len(self.learning_data["hunt_sessions"]),
            "recent_sessions": len(recent_sessions),
            "tool_count": len(self.learning_data["tool_effectiveness"]),
            "target_insights_count": len(self.learning_data["target_insights"]),
            "adaptation_count": len(self.learning_data["adaptation_history"]),
            "performance_trends": self.learning_data.get("performance_trends", {}),
            "top_tools": self._get_top_tools(),
            "improvement_suggestions": len(self.improvement_tracker["suggestions_generated"]),
            "learning_health": self._assess_learning_health()
        }
        
        return insights
    
    def _get_top_tools(self) -> List[Dict[str, Any]]:
        """Get top performing tools"""
        tools = []
        
        for tool, data in self.learning_data["tool_effectiveness"].items():
            tools.append({
                "tool": tool,
                "reliability_score": data["reliability_score"],
                "usage_count": data["usage_count"],
                "success_rate": data["success_rate"]
            })
        
        # Sort by reliability score
        tools.sort(key=lambda x: x["reliability_score"], reverse=True)
        
        return tools[:10]
    
    def _assess_learning_health(self) -> Dict[str, Any]:
        """Assess the health of the learning system"""
        recent_sessions = self._get_recent_sessions(days=7)
        
        health_score = 0.0
        health_factors = []
        
        # Factor 1: Recent activity
        if len(recent_sessions) > 0:
            health_score += 0.3
            health_factors.append("Active learning from recent sessions")
        
        # Factor 2: Tool diversity
        reliable_tools = len([
            tool for tool, data in self.learning_data["tool_effectiveness"].items()
            if data["reliability_score"] > 0.6
        ])
        
        if reliable_tools > 5:
            health_score += 0.3
            health_factors.append(f"{reliable_tools} reliable tools available")
        
        # Factor 3: Adaptation capability
        if len(self.learning_data["adaptation_history"]) > 0:
            health_score += 0.2
            health_factors.append("System has adapted to improve performance")
        
        # Factor 4: Trend analysis
        trends = self.learning_data.get("performance_trends", {}).get("trends", {})
        if trends.get("success_trend", 0) > 0:
            health_score += 0.2
            health_factors.append("Positive performance trends detected")
        
        return {
            "health_score": round(health_score, 2),
            "health_level": self._get_health_level(health_score),
            "contributing_factors": health_factors,
            "recommendations": self._get_health_recommendations(health_score)
        }
    
    def _get_health_level(self, score: float) -> str:
        """Get health level description"""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _get_health_recommendations(self, score: float) -> List[str]:
        """Get health improvement recommendations"""
        recommendations = []
        
        if score < 0.4:
            recommendations.append("Increase hunting frequency to improve learning")
            recommendations.append("Review and update tool configurations")
            recommendations.append("Analyze recent failures for improvement opportunities")
        elif score < 0.6:
            recommendations.append("Continue regular hunting to maintain learning momentum")
            recommendations.append("Monitor tool effectiveness and replace underperforming tools")
        elif score < 0.8:
            recommendations.append("Excellent progress - consider expanding target diversity")
            recommendations.append("Share successful strategies across different target types")
        else:
            recommendations.append("Outstanding learning health - system is self-optimizing effectively")
        
        return recommendations