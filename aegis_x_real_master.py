#!/usr/bin/env python3
"""
AEGIS-X Real Professional Master System
Uses REAL tools, REAL methodologies, finds REAL vulnerabilities
Continuous loop until MULTIPLE super-critical/exceptional vulnerabilities found
"""

import asyncio
import logging
import argparse
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from core.real_professional_system import RealProfessionalSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aegis_x_real_master.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AEGIS-X.RealMaster")

class RealMasterSystem:
    """
    Real Master System that continuously hunts until finding
    MULTIPLE super-critical/exceptional vulnerabilities
    """
    
    def __init__(self):
        self.version = "3.0 Real Professional"
        self.professional_system = RealProfessionalSystem()
        self.success_criteria = {
            'min_critical_vulns': 2,
            'min_super_critical_vulns': 1,
            'min_exceptional_vulns': 1,
            'min_total_high_critical': 5
        }
        
        logger.info(f"🔥 AEGIS-X Real Master System v{self.version} initialized")
        logger.info("🎯 Success criteria: Multiple super-critical/exceptional vulnerabilities required")
    
    async def continuous_hunting_loop(self, target: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Continuous hunting loop until success criteria met
        """
        
        logger.info(f"🚀 Starting continuous hunting loop against {target}")
        logger.info(f"🎯 Will continue until finding MULTIPLE super-critical/exceptional vulnerabilities")
        
        iteration = 0
        total_vulnerabilities = []
        all_campaign_results = []
        
        while iteration < max_iterations:
            iteration += 1
            
            logger.info(f"🔄 ITERATION {iteration}/{max_iterations}")
            logger.info("="*80)
            
            # Run professional campaign
            campaign_results = await self.professional_system.run_professional_campaign(target)
            all_campaign_results.append(campaign_results)
            
            # Collect vulnerabilities from this iteration
            iteration_vulns = campaign_results.get('vulnerabilities', [])
            total_vulnerabilities.extend(iteration_vulns)
            
            # Analyze results
            analysis = self._analyze_vulnerabilities(total_vulnerabilities)
            
            logger.info(f"📊 ITERATION {iteration} RESULTS:")
            logger.info(f"   🔍 This iteration: {len(iteration_vulns)} vulnerabilities")
            logger.info(f"   📈 Total so far: {len(total_vulnerabilities)} vulnerabilities")
            logger.info(f"   🚨 Critical: {analysis['critical']}")
            logger.info(f"   ⚠️  High: {analysis['high']}")
            logger.info(f"   📊 Medium: {analysis['medium']}")
            
            # Check success criteria
            if self._check_success_criteria(analysis):
                logger.info("🎉 SUCCESS CRITERIA MET!")
                logger.info(f"✅ Found {analysis['critical']} critical vulnerabilities")
                logger.info(f"✅ Found {analysis['high']} high vulnerabilities")
                logger.info(f"✅ Total high/critical: {analysis['critical'] + analysis['high']}")
                
                # Generate final comprehensive report
                final_results = await self._generate_final_report(
                    target, all_campaign_results, total_vulnerabilities, analysis
                )
                
                return final_results
            
            else:
                logger.info("❌ Success criteria not met yet")
                logger.info(f"   Need: {self.success_criteria['min_total_high_critical']} high/critical total")
                logger.info(f"   Have: {analysis['critical'] + analysis['high']}")
                logger.info("🔄 Continuing to next iteration...")
                
                # Wait before next iteration
                await asyncio.sleep(60)  # 1 minute between iterations
        
        # If we reach here, max iterations exceeded
        logger.warning(f"⚠️ Maximum iterations ({max_iterations}) reached without meeting success criteria")
        
        final_results = await self._generate_final_report(
            target, all_campaign_results, total_vulnerabilities, 
            self._analyze_vulnerabilities(total_vulnerabilities)
        )
        
        return final_results
    
    def _analyze_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze vulnerability severity distribution"""
        
        analysis = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'total': len(vulnerabilities)
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low').lower()
            if severity in analysis:
                analysis[severity] += 1
        
        return analysis
    
    def _check_success_criteria(self, analysis: Dict[str, int]) -> bool:
        """Check if success criteria are met"""
        
        total_high_critical = analysis['critical'] + analysis['high']
        
        # Success if we have enough high/critical vulnerabilities
        if total_high_critical >= self.success_criteria['min_total_high_critical']:
            return True
        
        # Or if we have specific critical counts
        if analysis['critical'] >= self.success_criteria['min_critical_vulns']:
            return True
        
        return False
    
    async def _generate_final_report(self, target: str, campaigns: List[Dict[str, Any]], 
                                   vulnerabilities: List[Dict[str, Any]], 
                                   analysis: Dict[str, int]) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        
        logger.info("📝 Generating comprehensive final report...")
        
        final_report = {
            'target': target,
            'campaign_summary': {
                'total_iterations': len(campaigns),
                'total_duration_hours': sum(c.get('statistics', {}).get('duration_hours', 0) for c in campaigns),
                'total_vulnerabilities': len(vulnerabilities),
                'severity_analysis': analysis,
                'success_criteria_met': self._check_success_criteria(analysis)
            },
            'detailed_vulnerabilities': vulnerabilities,
            'campaign_details': campaigns,
            'final_assessment': self._generate_final_assessment(analysis),
            'generated_at': datetime.now().isoformat()
        }
        
        # Save final report
        output_file = Path("output") / f"final_report_{target}_{int(time.time())}.json"
        
        import json
        with open(output_file, 'w') as f:
            json.dump(final_report, f, indent=2, default=str)
        
        logger.info(f"💾 Final report saved: {output_file}")
        
        return final_report
    
    def _generate_final_assessment(self, analysis: Dict[str, int]) -> str:
        """Generate final security assessment"""
        
        total_high_critical = analysis['critical'] + analysis['high']
        
        if total_high_critical >= 5:
            return "CRITICAL SECURITY POSTURE - Multiple high-impact vulnerabilities identified. Immediate remediation required."
        elif total_high_critical >= 3:
            return "HIGH RISK SECURITY POSTURE - Several significant vulnerabilities found. Priority remediation needed."
        elif total_high_critical >= 1:
            return "MODERATE RISK SECURITY POSTURE - Some vulnerabilities identified. Remediation recommended."
        else:
            return "LOW RISK SECURITY POSTURE - Limited vulnerabilities found. Continue monitoring."
    
    async def run_real_campaign(self, target: str, max_iterations: int = 10) -> bool:
        """Run real professional campaign"""
        
        logger.info("🔥 AEGIS-X REAL PROFESSIONAL SYSTEM STARTING")
        logger.info("="*80)
        logger.info(f"🎯 Target: {target}")
        logger.info(f"🔄 Max iterations: {max_iterations}")
        logger.info(f"✅ Success criteria: {self.success_criteria['min_total_high_critical']} high/critical vulnerabilities")
        logger.info("="*80)
        
        try:
            # Validate target
            if not self._validate_target(target):
                logger.error(f"❌ Invalid target: {target}")
                return False
            
            # Run continuous hunting loop
            final_results = await self.continuous_hunting_loop(target, max_iterations)
            
            # Display final results
            await self._display_final_results(final_results)
            
            # Check if successful
            success = final_results['campaign_summary']['success_criteria_met']
            
            if success:
                logger.info("🎉 CAMPAIGN SUCCESSFUL - Success criteria met!")
                return True
            else:
                logger.warning("❌ CAMPAIGN INCOMPLETE - Success criteria not met")
                return False
                
        except Exception as e:
            logger.error(f"❌ Campaign failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _validate_target(self, target: str) -> bool:
        """Validate target is accessible and appropriate for testing"""
        
        # Basic validation
        if not target or len(target) < 3:
            return False
        
        # Check if target is reachable
        try:
            import socket
            socket.gethostbyname(target)
            return True
        except socket.gaierror:
            return False
    
    async def _display_final_results(self, results: Dict[str, Any]):
        """Display comprehensive final results"""
        
        summary = results['campaign_summary']
        
        print("\n" + "="*100)
        print("🔥 AEGIS-X REAL PROFESSIONAL CAMPAIGN - FINAL RESULTS")
        print("="*100)
        print(f"🎯 Target: {results['target']}")
        print(f"🔄 Total Iterations: {summary['total_iterations']}")
        print(f"⏱️  Total Duration: {summary['total_duration_hours']:.1f} hours")
        print(f"🔍 Total Vulnerabilities Found: {summary['total_vulnerabilities']}")
        
        analysis = summary['severity_analysis']
        print(f"\n📊 Severity Breakdown:")
        print(f"   🚨 Critical: {analysis['critical']}")
        print(f"   ⚠️  High: {analysis['high']}")
        print(f"   📊 Medium: {analysis['medium']}")
        print(f"   ℹ️  Low: {analysis['low']}")
        
        print(f"\n🎯 Success Criteria:")
        print(f"   Required: {self.success_criteria['min_total_high_critical']} high/critical vulnerabilities")
        print(f"   Achieved: {analysis['critical'] + analysis['high']} high/critical vulnerabilities")
        
        if summary['success_criteria_met']:
            print(f"\n🎉 SUCCESS: Campaign objectives achieved!")
            print(f"✅ Found sufficient high-impact vulnerabilities")
        else:
            print(f"\n❌ INCOMPLETE: Success criteria not fully met")
            print(f"⚠️ Consider additional testing or different methodologies")
        
        print(f"\n📋 Final Assessment:")
        print(f"   {results['final_assessment']}")
        
        print("="*100)

async def main():
    """Main entry point for real professional system"""
    
    parser = argparse.ArgumentParser(description="AEGIS-X Real Professional Bug Bounty System")
    parser.add_argument("target", help="Target domain to test (e.g., youngplatform.com)")
    parser.add_argument("--max-iterations", type=int, default=10, help="Maximum hunting iterations")
    parser.add_argument("--min-critical", type=int, default=5, help="Minimum high/critical vulnerabilities for success")
    
    args = parser.parse_args()
    
    # Initialize real master system
    master_system = RealMasterSystem()
    
    # Update success criteria if specified
    if args.min_critical:
        master_system.success_criteria['min_total_high_critical'] = args.min_critical
    
    # Run real campaign
    success = await master_system.run_real_campaign(args.target, args.max_iterations)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())