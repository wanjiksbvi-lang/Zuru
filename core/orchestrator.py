#!/usr/bin/env python3
"""
AEGIS-X Main Orchestrator
The central intelligence that coordinates all hunting operations
"""

import os
import sys
import json
import logging
import asyncio
import argparse
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Import all AEGIS-X components
from classifier import TargetClassifier
from intelligence_engine import IntelligenceEngine
from verification_engine import VerificationEngine
from learning_engine import LearningEngine

# Import hunters
from web_hunter import WebHunter
from mobile_hunter import MobileHunter
from file_hunter import FileHunter
from network_hunter import NetworkHunter
from code_hunter import CodeHunter

# Import AI agents
sys.path.append(str(Path(__file__).parent.parent))
from agents.recon_strategist import ReconStrategist
from agents.vuln_tactician import VulnTactician
from agents.poc_engineer import PoCEngineer
from agents.evidence_architect import EvidenceArchitect
from agents.report_general import ReportGeneral

class AegisXOrchestrator:
    """
    The AEGIS-X Orchestrator is the central intelligence that coordinates
    all hunting operations, manages AI agents, and ensures comprehensive
    vulnerability discovery with zero false positives.
    """
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger("AEGIS-X.Orchestrator")
        
        # Initialize core components
        self.classifier = TargetClassifier()
        self.intelligence_engine = IntelligenceEngine()
        self.verification_engine = VerificationEngine()
        self.learning_engine = LearningEngine()
        
        # Initialize hunters
        self.hunters = {
            "web": WebHunter(),
            "mobile": MobileHunter(),
            "file": FileHunter(),
            "network": NetworkHunter(),
            "code": CodeHunter()
        }
        
        # Initialize AI agents
        self.agents = {
            "recon_strategist": ReconStrategist(),
            "vuln_tactician": VulnTactician(),
            "poc_engineer": PoCEngineer(),
            "evidence_architect": EvidenceArchitect(),
            "report_general": ReportGeneral()
        }
        
        # Hunt session state
        self.current_session = None
        self.session_stats = self._load_session_stats()
        
        self.logger.info("🚀 AEGIS-X Orchestrator initialized - Ready for autonomous hunting")
    
    def setup_logging(self):
        """Setup comprehensive logging system"""
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / f"aegis_x_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _load_session_stats(self) -> Dict[str, Any]:
        """Load session statistics"""
        stats_file = Path("learn/session_stats.json")
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load session stats: {e}")
        
        return {
            "total_sessions": 0,
            "total_targets": 0,
            "total_findings": 0,
            "verified_findings": 0,
            "session_history": []
        }
    
    async def hunt(self, targets_file: str) -> Dict[str, Any]:
        """
        Execute comprehensive autonomous hunting on all targets
        """
        self.logger.info("🎯 Starting AEGIS-X autonomous hunting session")
        
        # Initialize hunt session
        session = {
            "session_id": f"hunt_{int(datetime.now().timestamp())}",
            "start_time": datetime.now().isoformat(),
            "targets_file": targets_file,
            "targets": [],
            "findings": [],
            "verified_findings": [],
            "reports": [],
            "statistics": {},
            "learning_insights": {}
        }
        
        self.current_session = session
        
        try:
            # Load and classify targets
            targets = await self._load_targets(targets_file)
            session["targets"] = targets
            
            self.logger.info(f"📋 Loaded {len(targets)} targets for hunting")
            
            # Process each target
            for target_info in targets:
                await self._hunt_target(target_info, session)
            
            # Verify all findings
            await self._verify_all_findings(session)
            
            # Generate reports
            await self._generate_reports(session)
            
            # Learn from session
            await self._learn_from_session(session)
            
        except Exception as e:
            self.logger.error(f"Hunt session failed: {str(e)}")
            session["error"] = str(e)
        
        session["end_time"] = datetime.now().isoformat()
        session["duration"] = self._calculate_duration(session["start_time"], session["end_time"])
        
        # Update statistics
        await self._update_session_stats(session)
        
        # Save session
        await self._save_session(session)
        
        self.logger.info(f"🏆 Hunt session completed - {len(session['verified_findings'])} verified findings")
        return session
    
    async def _load_targets(self, targets_file: str) -> List[Dict[str, Any]]:
        """Load and classify targets from file"""
        targets = []
        
        try:
            with open(targets_file, 'r') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Classify target
                classification = self.classifier.classify(line)
                
                target_info = {
                    "line_number": line_num,
                    "raw_target": line,
                    "classification": classification,
                    "intelligence": None,
                    "findings": []
                }
                
                targets.append(target_info)
                
                self.logger.info(f"🔍 Target {line_num}: {line} -> {classification.target_type.value}")
        
        except Exception as e:
            self.logger.error(f"Failed to load targets: {e}")
            raise
        
        return targets
    
    async def _hunt_target(self, target_info: Dict[str, Any], session: Dict[str, Any]):
        """Hunt a single target comprehensively"""
        target = target_info["raw_target"]
        target_type = target_info["classification"].target_type.value
        
        self.logger.info(f"🎯 Hunting target: {target} (Type: {target_type})")
        
        try:
            # Phase 1: Intelligence Gathering
            self.logger.info("🕵️ Phase 1: Intelligence Gathering")
            intelligence = await self.intelligence_engine.analyze_target(target)
            target_info["intelligence"] = intelligence
            
            # Let Recon Strategist analyze intelligence
            recon_analysis = await self.agents["recon_strategist"].analyze(target, target_type, intelligence)
            
            # Phase 2: Targeted Hunting
            self.logger.info(f"🔍 Phase 2: Targeted Hunting ({target_type})")
            
            if target_type == "web":
                findings = await self.hunters["web"].hunt(target, intelligence)
            elif target_type == "mobile":
                findings = await self.hunters["mobile"].hunt(target, intelligence)
            elif target_type == "file":
                findings = await self.hunters["file"].hunt(target, intelligence)
            elif target_type == "network":
                findings = await self.hunters["network"].hunt(target, intelligence)
            elif target_type == "code":
                findings = await self.hunters["code"].hunt(target, intelligence)
            else:
                self.logger.warning(f"Unknown target type: {target_type}")
                findings = []
            
            target_info["findings"] = findings
            session["findings"].extend(findings)
            
            # Phase 3: Vulnerability Analysis and Chaining
            self.logger.info("🔗 Phase 3: Vulnerability Analysis and Chaining")
            
            if findings:
                # Let Vuln Tactician analyze findings for escalation opportunities
                escalation_analysis = await self.agents["vuln_tactician"].analyze_escalation_chains(findings, intelligence)
                
                # Add escalated findings
                if escalation_analysis.get("escalated_findings"):
                    escalated_findings = escalation_analysis["escalated_findings"]
                    target_info["findings"].extend(escalated_findings)
                    session["findings"].extend(escalated_findings)
                    
                    self.logger.info(f"🚀 Found {len(escalated_findings)} escalated vulnerabilities")
            
            self.logger.info(f"✅ Target hunting completed - Found {len(findings)} potential vulnerabilities")
        
        except Exception as e:
            self.logger.error(f"Target hunting failed for {target}: {e}")
            target_info["error"] = str(e)
    
    async def _verify_all_findings(self, session: Dict[str, Any]):
        """Verify all findings using triple verification protocol"""
        self.logger.info("🔬 Starting comprehensive verification of all findings")
        
        all_findings = session["findings"]
        verified_findings = []
        
        for finding in all_findings:
            try:
                # Triple verification protocol
                verification_result = await self.verification_engine.verify(finding)
                
                if verification_result["verified"]:
                    # Add verification data to finding
                    finding["verification"] = verification_result
                    verified_findings.append(finding)
                    
                    self.logger.info(f"✅ Verified: {finding.get('title', 'Unknown')} (Confidence: {verification_result['confidence_score']:.2f})")
                else:
                    self.logger.info(f"❌ Rejected: {finding.get('title', 'Unknown')} - {verification_result['reason']}")
            
            except Exception as e:
                self.logger.error(f"Verification failed for finding: {e}")
        
        session["verified_findings"] = verified_findings
        
        self.logger.info(f"🎉 Verification completed - {len(verified_findings)}/{len(all_findings)} findings verified")
    
    async def _generate_reports(self, session: Dict[str, Any]):
        """Generate comprehensive reports"""
        self.logger.info("📝 Generating comprehensive reports")
        
        verified_findings = session["verified_findings"]
        
        if not verified_findings:
            self.logger.info("No verified findings to report")
            return
        
        try:
            # Generate PoCs for verified findings
            for finding in verified_findings:
                if finding.get("severity") in ["High", "Critical"]:
                    poc = await self.agents["poc_engineer"].generate_poc(finding)
                    if poc:
                        finding["poc"] = poc
            
            # Collect evidence for all findings
            for finding in verified_findings:
                evidence = await self.agents["evidence_architect"].collect_evidence(finding)
                if evidence:
                    finding["evidence_package"] = evidence
            
            # Generate master report
            master_report = await self.agents["report_general"].generate_master_report(
                session["targets"],
                verified_findings,
                session
            )
            
            session["reports"].append(master_report)
            
            # Save reports to files
            await self._save_reports(session)
            
            self.logger.info(f"📊 Reports generated successfully")
        
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
    
    async def _learn_from_session(self, session: Dict[str, Any]):
        """Learn from the hunting session"""
        self.logger.info("🧠 Learning from hunting session")
        
        try:
            # Analyze session performance
            learning_insights = await self.learning_engine.analyze_session(session)
            session["learning_insights"] = learning_insights
            
            # Update AI agent knowledge
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'learn_from_session'):
                    await agent.learn_from_session(session)
            
            # Update hunter strategies
            for hunter_name, hunter in self.hunters.items():
                if hasattr(hunter, 'learn_from_session'):
                    await hunter.learn_from_session(session)
            
            self.logger.info("🎓 Learning completed - Knowledge base updated")
        
        except Exception as e:
            self.logger.error(f"Learning failed: {e}")
    
    async def _save_reports(self, session: Dict[str, Any]):
        """Save reports to output directory"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        session_id = session["session_id"]
        
        # Save master report
        for report in session["reports"]:
            if report["type"] == "master_report":
                report_file = output_dir / f"{session_id}_master_report.md"
                with open(report_file, 'w') as f:
                    f.write(report["content"])
                
                # Save JSON version for processing
                json_file = output_dir / f"{session_id}_findings.json"
                with open(json_file, 'w') as f:
                    json.dump(session["verified_findings"], f, indent=2, default=str)
        
        # Save individual finding reports
        findings_dir = output_dir / f"{session_id}_findings"
        findings_dir.mkdir(exist_ok=True)
        
        for i, finding in enumerate(session["verified_findings"]):
            finding_file = findings_dir / f"finding_{i+1}_{finding.get('type', 'unknown')}.json"
            with open(finding_file, 'w') as f:
                json.dump(finding, f, indent=2, default=str)
    
    async def _save_session(self, session: Dict[str, Any]):
        """Save complete session data"""
        sessions_dir = Path("learn/sessions")
        sessions_dir.mkdir(parents=True, exist_ok=True)
        
        session_file = sessions_dir / f"{session['session_id']}.json"
        
        # Create a clean copy for saving (remove large objects)
        clean_session = session.copy()
        
        # Remove large intelligence data to save space
        for target in clean_session.get("targets", []):
            if target.get("intelligence"):
                # Keep only summary
                intelligence = target["intelligence"]
                target["intelligence_summary"] = {
                    "confidence_score": intelligence.get("confidence_score", 0),
                    "risk_assessment": intelligence.get("risk_assessment", {}),
                    "recommendations": intelligence.get("recommendations", [])
                }
                del target["intelligence"]
        
        with open(session_file, 'w') as f:
            json.dump(clean_session, f, indent=2, default=str)
    
    async def _update_session_stats(self, session: Dict[str, Any]):
        """Update session statistics"""
        self.session_stats["total_sessions"] += 1
        self.session_stats["total_targets"] += len(session["targets"])
        self.session_stats["total_findings"] += len(session["findings"])
        self.session_stats["verified_findings"] += len(session["verified_findings"])
        
        # Add session summary to history
        session_summary = {
            "session_id": session["session_id"],
            "start_time": session["start_time"],
            "duration": session.get("duration", "unknown"),
            "targets_count": len(session["targets"]),
            "findings_count": len(session["findings"]),
            "verified_count": len(session["verified_findings"]),
            "success_rate": len(session["verified_findings"]) / len(session["findings"]) if session["findings"] else 0
        }
        
        self.session_stats["session_history"].append(session_summary)
        
        # Keep only last 100 sessions
        if len(self.session_stats["session_history"]) > 100:
            self.session_stats["session_history"] = self.session_stats["session_history"][-100:]
        
        # Save statistics
        stats_file = Path("learn/session_stats.json")
        stats_file.parent.mkdir(exist_ok=True)
        
        with open(stats_file, 'w') as f:
            json.dump(self.session_stats, f, indent=2)
    
    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calculate session duration"""
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            duration = end - start
            
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        except:
            return "unknown"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "orchestrator": "operational",
            "components": {},
            "hunters": {},
            "agents": {},
            "statistics": self.session_stats,
            "last_session": self.current_session["session_id"] if self.current_session else None
        }
        
        # Check component status
        components = [
            ("classifier", self.classifier),
            ("intelligence_engine", self.intelligence_engine),
            ("verification_engine", self.verification_engine),
            ("learning_engine", self.learning_engine)
        ]
        
        for name, component in components:
            try:
                if hasattr(component, 'get_status'):
                    status["components"][name] = component.get_status()
                else:
                    status["components"][name] = "operational"
            except:
                status["components"][name] = "unknown"
        
        # Check hunter status
        for name, hunter in self.hunters.items():
            try:
                if hasattr(hunter, 'get_hunting_stats'):
                    status["hunters"][name] = hunter.get_hunting_stats()
                else:
                    status["hunters"][name] = "operational"
            except:
                status["hunters"][name] = "unknown"
        
        # Check agent status
        for name, agent in self.agents.items():
            try:
                if hasattr(agent, 'get_status'):
                    status["agents"][name] = agent.get_status()
                else:
                    status["agents"][name] = "operational"
            except:
                status["agents"][name] = "unknown"
        
        return status
    
    async def cleanup_old_data(self, days_old: int = 30):
        """Cleanup old session data and logs"""
        self.logger.info(f"🧹 Cleaning up data older than {days_old} days")
        
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 3600)
        
        # Cleanup old sessions
        sessions_dir = Path("learn/sessions")
        if sessions_dir.exists():
            for session_file in sessions_dir.glob("*.json"):
                if session_file.stat().st_mtime < cutoff_date:
                    session_file.unlink()
                    self.logger.debug(f"Removed old session: {session_file}")
        
        # Cleanup old logs
        logs_dir = Path("logs")
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    self.logger.debug(f"Removed old log: {log_file}")
        
        # Cleanup old evidence
        evidence_dir = Path("evidence")
        if evidence_dir.exists():
            for evidence_item in evidence_dir.rglob("*"):
                if evidence_item.is_file() and evidence_item.stat().st_mtime < cutoff_date:
                    evidence_item.unlink()
                    self.logger.debug(f"Removed old evidence: {evidence_item}")

async def main():
    """Main entry point for AEGIS-X"""
    parser = argparse.ArgumentParser(description="AEGIS-X Autonomous Bug Bounty System")
    parser.add_argument("--targets", required=True, help="Path to targets file")
    parser.add_argument("--cleanup", type=int, help="Cleanup data older than N days")
    parser.add_argument("--status", action="store_true", help="Show system status")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = AegisXOrchestrator()
    
    if args.status:
        # Show system status
        status = orchestrator.get_system_status()
        print(json.dumps(status, indent=2, default=str))
        return
    
    if args.cleanup:
        # Cleanup old data
        await orchestrator.cleanup_old_data(args.cleanup)
        return
    
    # Execute hunt
    try:
        session = await orchestrator.hunt(args.targets)
        
        print("\n" + "="*80)
        print("🎉 AEGIS-X HUNT COMPLETED")
        print("="*80)
        print(f"Session ID: {session['session_id']}")
        print(f"Duration: {session.get('duration', 'unknown')}")
        print(f"Targets Processed: {len(session['targets'])}")
        print(f"Total Findings: {len(session['findings'])}")
        print(f"Verified Findings: {len(session['verified_findings'])}")
        print(f"Success Rate: {len(session['verified_findings'])/len(session['findings'])*100:.1f}%" if session['findings'] else "N/A")
        print("="*80)
        
        # Show critical/high findings
        critical_high = [f for f in session['verified_findings'] if f.get('severity') in ['Critical', 'High']]
        if critical_high:
            print(f"\n🚨 {len(critical_high)} CRITICAL/HIGH SEVERITY FINDINGS:")
            for finding in critical_high:
                print(f"  • {finding.get('title', 'Unknown')} ({finding.get('severity', 'Unknown')})")
        
        print(f"\n📊 Reports saved to: output/{session['session_id']}_*")
        print("="*80)
    
    except KeyboardInterrupt:
        print("\n🛑 Hunt interrupted by user")
    except Exception as e:
        print(f"\n❌ Hunt failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())