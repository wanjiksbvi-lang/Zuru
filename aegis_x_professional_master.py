#!/usr/bin/env python3
"""
AEGIS-X Professional Master System
The ultimate professional bug bounty hunting platform with industry-grade capabilities
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
import time

# Add core modules to path
sys.path.append(str(Path(__file__).parent / "core"))

# Import professional components
from professional_vulnerability_engine import ProfessionalVulnerabilityEngine
from professional_evidence_collector import ProfessionalEvidenceCollector
from professional_report_engine import ProfessionalReportEngine
from advanced_verification_system import AdvancedVerificationSystem

# Import existing components
from classifier import TargetClassifier
from intelligence_engine import IntelligenceEngine
from learning_engine import LearningEngine

class AegisXProfessionalMaster:
    """
    AEGIS-X Professional Master System
    
    The ultimate autonomous bug bounty hunting platform that delivers
    professional-grade security assessments with comprehensive evidence
    collection and industry-standard reporting.
    """
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger("AEGIS-X.ProfessionalMaster")
        
        # Initialize professional components
        self.vulnerability_engine = ProfessionalVulnerabilityEngine()
        self.evidence_collector = ProfessionalEvidenceCollector()
        self.report_engine = ProfessionalReportEngine()
        self.verification_system = AdvancedVerificationSystem()
        
        # Initialize supporting components
        self.classifier = TargetClassifier()
        self.intelligence_engine = IntelligenceEngine()
        self.learning_engine = LearningEngine()
        
        # Professional configuration
        self.config = {
            "max_concurrent_targets": 5,
            "verification_enabled": True,
            "evidence_collection_enabled": True,
            "professional_reporting": True,
            "quality_threshold": 0.8,
            "false_positive_filtering": True,
            "vulnerability_chaining": True,
            "advanced_exploitation": True
        }
        
        # Session tracking
        self.session_id = f"professional_hunt_{int(time.time())}"
        self.session_stats = {
            "start_time": datetime.now().isoformat(),
            "targets_processed": 0,
            "vulnerabilities_found": 0,
            "vulnerabilities_verified": 0,
            "evidence_packages_created": 0,
            "reports_generated": 0,
            "quality_score": 0.0
        }
        
        self.logger.info("🚀 AEGIS-X Professional Master System initialized")
        self.logger.info("🎯 Ready for professional-grade security assessments")
    
    def setup_logging(self):
        """Setup comprehensive logging system"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure logging with professional format
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / f"aegis_x_professional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    async def execute_professional_hunt(self, targets_file: str, report_type: str = "hackerone_professional") -> Dict[str, Any]:
        """
        Execute comprehensive professional security assessment
        """
        self.logger.info("🔥 Starting AEGIS-X Professional Security Assessment")
        self.logger.info(f"📋 Session ID: {self.session_id}")
        
        hunt_results = {
            "session_id": self.session_id,
            "start_time": self.session_stats["start_time"],
            "targets_file": targets_file,
            "report_type": report_type,
            "targets": [],
            "findings": [],
            "verified_findings": [],
            "evidence_packages": [],
            "reports": [],
            "statistics": {},
            "quality_metrics": {}
        }
        
        try:
            # Phase 1: Target Classification and Intelligence Gathering
            self.logger.info("🎯 Phase 1: Target Classification and Intelligence Gathering")
            targets = await self._load_and_classify_targets(targets_file)
            hunt_results["targets"] = targets
            self.session_stats["targets_processed"] = len(targets)
            
            # Phase 2: Professional Vulnerability Discovery
            self.logger.info("🔍 Phase 2: Professional Vulnerability Discovery")
            all_findings = []
            
            for target_info in targets:
                target_findings = await self._execute_professional_vulnerability_discovery(target_info)
                all_findings.extend(target_findings)
                
                self.logger.info(f"✅ Target {target_info['raw_target']} completed - {len(target_findings)} findings")
            
            hunt_results["findings"] = all_findings
            self.session_stats["vulnerabilities_found"] = len(all_findings)
            
            # Phase 3: Advanced Verification
            self.logger.info("🔬 Phase 3: Advanced Verification System")
            verified_findings = []
            
            if self.config["verification_enabled"]:
                for finding in all_findings:
                    verification_result = await self.verification_system.verify_finding(
                        finding, finding.get("target", "")
                    )
                    
                    if verification_result.get("verified", False):
                        finding["verification"] = verification_result
                        verified_findings.append(finding)
                        
                        self.logger.info(f"✅ Verified: {finding.get('title', 'Unknown')} "
                                       f"(Confidence: {verification_result.get('confidence_score', 0):.2f})")
                    else:
                        self.logger.info(f"❌ Rejected: {finding.get('title', 'Unknown')} - "
                                       f"{verification_result.get('reason', 'Unknown reason')}")
            else:
                verified_findings = all_findings
            
            hunt_results["verified_findings"] = verified_findings
            self.session_stats["vulnerabilities_verified"] = len(verified_findings)
            
            # Phase 4: Professional Evidence Collection
            self.logger.info("📸 Phase 4: Professional Evidence Collection")
            evidence_packages = []
            
            if self.config["evidence_collection_enabled"] and verified_findings:
                for finding in verified_findings:
                    target = finding.get("target", "")
                    evidence_package = await self.evidence_collector.collect_comprehensive_evidence(
                        finding, target
                    )
                    evidence_packages.append(evidence_package)
                    
                    self.logger.info(f"📦 Evidence collected for: {finding.get('title', 'Unknown')}")
            
            hunt_results["evidence_packages"] = evidence_packages
            self.session_stats["evidence_packages_created"] = len(evidence_packages)
            
            # Phase 5: Professional Report Generation
            self.logger.info("📝 Phase 5: Professional Report Generation")
            reports = []
            
            if self.config["professional_reporting"] and verified_findings:
                # Generate main assessment report
                main_report = await self.report_engine.generate_professional_report(
                    verified_findings, evidence_packages, targets_file, report_type
                )
                reports.append(main_report)
                
                # Generate individual finding reports for high/critical findings
                critical_high_findings = [
                    f for f in verified_findings 
                    if f.get("severity", "").lower() in ["critical", "high"]
                ]
                
                for finding in critical_high_findings:
                    finding_evidence = [
                        ep for ep in evidence_packages 
                        if ep.get("finding_id") == finding.get("id")
                    ]
                    
                    individual_report = await self.report_engine.generate_professional_report(
                        [finding], finding_evidence, finding.get("target", ""), 
                        f"individual_{report_type}"
                    )
                    reports.append(individual_report)
            
            hunt_results["reports"] = reports
            self.session_stats["reports_generated"] = len(reports)
            
            # Phase 6: Quality Assessment and Learning
            self.logger.info("📊 Phase 6: Quality Assessment and Learning")
            quality_metrics = await self._assess_hunt_quality(hunt_results)
            hunt_results["quality_metrics"] = quality_metrics
            self.session_stats["quality_score"] = quality_metrics.get("overall_quality_score", 0.0)
            
            # Update learning system
            await self.learning_engine.learn_from_session({
                "session_id": self.session_id,
                "findings": verified_findings,
                "evidence_packages": evidence_packages,
                "quality_metrics": quality_metrics
            })
            
            # Finalize session
            hunt_results["end_time"] = datetime.now().isoformat()
            hunt_results["duration"] = self._calculate_session_duration()
            hunt_results["statistics"] = self.session_stats
            
            # Save session results
            await self._save_session_results(hunt_results)
            
            # Display professional summary
            self._display_professional_summary(hunt_results)
            
            return hunt_results
            
        except Exception as e:
            self.logger.error(f"Professional hunt failed: {str(e)}")
            hunt_results["error"] = str(e)
            hunt_results["end_time"] = datetime.now().isoformat()
            return hunt_results
    
    async def _load_and_classify_targets(self, targets_file: str) -> List[Dict[str, Any]]:
        """Load and classify targets with intelligence gathering"""
        targets = []
        
        try:
            with open(targets_file, 'r') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                self.logger.info(f"🎯 Processing target {line_num}: {line}")
                
                # Classify target
                classification = self.classifier.classify(line)
                
                # Gather intelligence
                intelligence = await self.intelligence_engine.analyze_target(line)
                
                target_info = {
                    "line_number": line_num,
                    "raw_target": line,
                    "classification": classification,
                    "intelligence": intelligence,
                    "processed_timestamp": datetime.now().isoformat()
                }
                
                targets.append(target_info)
                
                self.logger.info(f"✅ Target classified: {line} -> {classification.target_type.value}")
        
        except Exception as e:
            self.logger.error(f"Failed to load targets: {e}")
            raise
        
        return targets
    
    async def _execute_professional_vulnerability_discovery(self, target_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute professional vulnerability discovery for a target"""
        target = target_info["raw_target"]
        target_type = target_info["classification"].target_type.value
        intelligence = target_info["intelligence"]
        
        self.logger.info(f"🔍 Professional vulnerability discovery: {target} ({target_type})")
        
        try:
            # Execute comprehensive vulnerability scanning
            findings = await self.vulnerability_engine.comprehensive_scan(
                target, target_type, intelligence
            )
            
            # Enrich findings with target information
            for finding in findings:
                finding["target"] = target
                finding["target_type"] = target_type
                finding["target_intelligence"] = intelligence
                finding["discovery_session"] = self.session_id
                finding["discovery_timestamp"] = datetime.now().isoformat()
            
            return findings
            
        except Exception as e:
            self.logger.error(f"Vulnerability discovery failed for {target}: {e}")
            return []
    
    async def _assess_hunt_quality(self, hunt_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall quality of the security assessment"""
        quality_metrics = {
            "overall_quality_score": 0.0,
            "verification_rate": 0.0,
            "evidence_quality": 0.0,
            "report_quality": 0.0,
            "false_positive_rate": 0.0,
            "coverage_score": 0.0,
            "professional_standards_compliance": 0.0
        }
        
        try:
            total_findings = len(hunt_results.get("findings", []))
            verified_findings = len(hunt_results.get("verified_findings", []))
            evidence_packages = hunt_results.get("evidence_packages", [])
            reports = hunt_results.get("reports", [])
            
            # Calculate verification rate
            if total_findings > 0:
                quality_metrics["verification_rate"] = verified_findings / total_findings
            
            # Calculate evidence quality
            if evidence_packages:
                evidence_scores = [
                    ep.get("metadata", {}).get("evidence_quality_score", 0.0)
                    for ep in evidence_packages
                ]
                quality_metrics["evidence_quality"] = sum(evidence_scores) / len(evidence_scores)
            
            # Calculate report quality
            if reports:
                report_scores = [r.get("quality_score", 0.0) for r in reports]
                quality_metrics["report_quality"] = sum(report_scores) / len(report_scores)
            
            # Calculate false positive rate (inverse of verification rate)
            quality_metrics["false_positive_rate"] = 1.0 - quality_metrics["verification_rate"]
            
            # Calculate coverage score (based on techniques used)
            quality_metrics["coverage_score"] = self._calculate_coverage_score(hunt_results)
            
            # Calculate professional standards compliance
            quality_metrics["professional_standards_compliance"] = self._calculate_compliance_score(hunt_results)
            
            # Calculate overall quality score
            weights = {
                "verification_rate": 0.25,
                "evidence_quality": 0.25,
                "report_quality": 0.20,
                "coverage_score": 0.15,
                "professional_standards_compliance": 0.15
            }
            
            overall_score = sum(
                quality_metrics[metric] * weight
                for metric, weight in weights.items()
            )
            
            quality_metrics["overall_quality_score"] = min(1.0, overall_score)
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            return quality_metrics
    
    def _calculate_coverage_score(self, hunt_results: Dict[str, Any]) -> float:
        """Calculate coverage score based on techniques and tools used"""
        # This would analyze the breadth and depth of testing performed
        # For now, return a baseline score
        return 0.8
    
    def _calculate_compliance_score(self, hunt_results: Dict[str, Any]) -> float:
        """Calculate professional standards compliance score"""
        compliance_score = 0.0
        
        # Check for required elements
        has_verified_findings = len(hunt_results.get("verified_findings", [])) > 0
        has_evidence_packages = len(hunt_results.get("evidence_packages", [])) > 0
        has_professional_reports = len(hunt_results.get("reports", [])) > 0
        
        if has_verified_findings:
            compliance_score += 0.4
        if has_evidence_packages:
            compliance_score += 0.3
        if has_professional_reports:
            compliance_score += 0.3
        
        return compliance_score
    
    def _calculate_session_duration(self) -> str:
        """Calculate session duration"""
        start_time = datetime.fromisoformat(self.session_stats["start_time"])
        end_time = datetime.now()
        duration = end_time - start_time
        
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    async def _save_session_results(self, hunt_results: Dict[str, Any]):
        """Save comprehensive session results"""
        results_dir = Path("temp/sessions")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        session_file = results_dir / f"professional_session_{self.session_id}.json"
        
        # Prepare serializable results
        serializable_results = self._prepare_serializable_results(hunt_results)
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        self.logger.info(f"💾 Session results saved: {session_file}")
    
    def _prepare_serializable_results(self, hunt_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare results for JSON serialization"""
        # Remove non-serializable objects and large data
        serializable = {}
        
        for key, value in hunt_results.items():
            if key in ["targets", "findings", "verified_findings", "statistics", "quality_metrics"]:
                serializable[key] = value
            elif key == "evidence_packages":
                # Include only metadata for evidence packages
                serializable[key] = [
                    {
                        "finding_id": ep.get("finding_id"),
                        "collection_timestamp": ep.get("collection_timestamp"),
                        "evidence_types": ep.get("evidence_types", []),
                        "metadata": ep.get("metadata", {})
                    }
                    for ep in value
                ]
            elif key == "reports":
                # Include only metadata for reports
                serializable[key] = [
                    {
                        "report_id": r.get("report_id"),
                        "report_type": r.get("report_type"),
                        "generation_timestamp": r.get("generation_timestamp"),
                        "quality_score": r.get("quality_score"),
                        "files_count": len(r.get("files", []))
                    }
                    for r in value
                ]
            else:
                serializable[key] = value
        
        return serializable
    
    def _display_professional_summary(self, hunt_results: Dict[str, Any]):
        """Display professional assessment summary"""
        print("\n" + "="*80)
        print("🔍 AEGIS-X PROFESSIONAL SECURITY ASSESSMENT SUMMARY")
        print("="*80)
        
        # Session information
        print(f"📋 Session ID: {self.session_id}")
        print(f"⏱️  Duration: {hunt_results.get('duration', 'Unknown')}")
        print(f"🎯 Targets Processed: {self.session_stats['targets_processed']}")
        
        # Findings summary
        print(f"\n📊 FINDINGS SUMMARY:")
        print(f"   Total Vulnerabilities Found: {self.session_stats['vulnerabilities_found']}")
        print(f"   Verified Vulnerabilities: {self.session_stats['vulnerabilities_verified']}")
        
        # Severity breakdown
        verified_findings = hunt_results.get("verified_findings", [])
        severity_counts = {
            "Critical": len([f for f in verified_findings if f.get("severity", "").lower() == "critical"]),
            "High": len([f for f in verified_findings if f.get("severity", "").lower() == "high"]),
            "Medium": len([f for f in verified_findings if f.get("severity", "").lower() == "medium"]),
            "Low": len([f for f in verified_findings if f.get("severity", "").lower() == "low"]),
            "Info": len([f for f in verified_findings if f.get("severity", "").lower() == "info"])
        }
        
        print(f"\n🎯 SEVERITY BREAKDOWN:")
        for severity, count in severity_counts.items():
            if count > 0:
                print(f"   {severity}: {count}")
        
        # Quality metrics
        quality_metrics = hunt_results.get("quality_metrics", {})
        print(f"\n📈 QUALITY METRICS:")
        print(f"   Overall Quality Score: {quality_metrics.get('overall_quality_score', 0):.2f}/1.00")
        print(f"   Verification Rate: {quality_metrics.get('verification_rate', 0):.2f}")
        print(f"   Evidence Quality: {quality_metrics.get('evidence_quality', 0):.2f}")
        print(f"   Report Quality: {quality_metrics.get('report_quality', 0):.2f}")
        print(f"   False Positive Rate: {quality_metrics.get('false_positive_rate', 0):.2f}")
        
        # Evidence and reports
        print(f"\n📦 DELIVERABLES:")
        print(f"   Evidence Packages: {self.session_stats['evidence_packages_created']}")
        print(f"   Professional Reports: {self.session_stats['reports_generated']}")
        
        # Professional recommendations
        print(f"\n💡 PROFESSIONAL RECOMMENDATIONS:")
        if severity_counts["Critical"] > 0:
            print("   🚨 IMMEDIATE ACTION REQUIRED: Critical vulnerabilities detected")
        if severity_counts["High"] > 0:
            print("   ⚠️  HIGH PRIORITY: Address high-severity vulnerabilities within 30 days")
        if quality_metrics.get("overall_quality_score", 0) >= 0.9:
            print("   ✅ EXCELLENT: Assessment meets professional standards")
        elif quality_metrics.get("overall_quality_score", 0) >= 0.7:
            print("   👍 GOOD: Assessment quality is acceptable")
        else:
            print("   ⚠️  REVIEW NEEDED: Assessment quality below professional standards")
        
        print("\n" + "="*80)
        print("🎉 PROFESSIONAL SECURITY ASSESSMENT COMPLETED")
        print("="*80 + "\n")


async def main():
    """Main entry point for AEGIS-X Professional Master"""
    parser = argparse.ArgumentParser(
        description="AEGIS-X Professional Master - Ultimate Bug Bounty Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python aegis_x_professional_master.py --targets targets.txt
  python aegis_x_professional_master.py --targets targets.txt --report-type bugcrowd_professional
  python aegis_x_professional_master.py --targets targets.txt --report-type enterprise_security
        """
    )
    
    parser.add_argument(
        "--targets", "-t",
        required=True,
        help="Path to targets file"
    )
    
    parser.add_argument(
        "--report-type", "-r",
        default="hackerone_professional",
        choices=["hackerone_professional", "bugcrowd_professional", "enterprise_security", "penetration_test"],
        help="Type of professional report to generate"
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file (optional)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run professional master
    master = AegisXProfessionalMaster()
    
    try:
        results = await master.execute_professional_hunt(args.targets, args.report_type)
        
        if results.get("error"):
            print(f"❌ Assessment failed: {results['error']}")
            sys.exit(1)
        else:
            print("✅ Professional security assessment completed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Assessment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())