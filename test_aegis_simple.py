#!/usr/bin/env python3
"""
Simple test script to verify AEGIS-X core functionality
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AEGIS-X.Test")

async def test_basic_functionality():
    """Test basic AEGIS-X functionality"""
    
    logger.info("🚀 Starting AEGIS-X Basic Functionality Test")
    
    try:
        # Test 1: Import core modules
        logger.info("📦 Testing module imports...")
        
        from core.advanced_exploitation_engine import AdvancedExploitationEngine
        from core.severity_classifier import ProfessionalSeverityClassifier
        from core.professional_report_generator import ProfessionalReportGenerator
        
        logger.info("✅ Core modules imported successfully")
        
        # Test 2: Initialize components
        logger.info("🔧 Testing component initialization...")
        
        exploitation_engine = AdvancedExploitationEngine()
        severity_classifier = ProfessionalSeverityClassifier()
        report_generator = ProfessionalReportGenerator()
        
        logger.info("✅ Components initialized successfully")
        
        # Test 3: Test payload generation
        logger.info("🎯 Testing payload generation...")
        
        xss_payloads = exploitation_engine.payloads_db.get('xss', [])
        sqli_payloads = exploitation_engine.payloads_db.get('sqli', [])
        
        logger.info(f"✅ Generated {len(xss_payloads)} XSS payloads")
        logger.info(f"✅ Generated {len(sqli_payloads)} SQL injection payloads")
        
        # Test 4: Test severity classification
        logger.info("📊 Testing severity classification...")
        
        test_vulnerability = {
            'id': 'test_001',
            'title': 'Test XSS Vulnerability',
            'type': 'xss',
            'description': 'Test XSS vulnerability for system verification',
            'url': 'https://example.com/test',
            'parameter': 'q',
            'payload': '<script>alert("test")</script>',
            'verified': True
        }
        
        assessment = await severity_classifier.assess_vulnerability_severity(test_vulnerability)
        logger.info(f"✅ Severity assessment completed: {assessment.cvss_score.severity_level.value.upper()}")
        logger.info(f"   CVSS Score: {assessment.cvss_score.overall_score}")
        
        # Test 5: Test report generation components
        logger.info("📝 Testing report generation...")
        
        # Create test finding
        from core.professional_report_generator import VulnerabilityFinding, ReportMetadata
        
        test_finding = VulnerabilityFinding(
            id="TEST-001",
            title="Test Cross-Site Scripting Vulnerability",
            severity="high",
            cvss_score=7.5,
            cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
            description="Test XSS vulnerability for system verification",
            impact="Potential for session hijacking and data theft",
            affected_url="https://example.com/test",
            affected_parameter="q",
            payload="<script>alert('test')</script>",
            proof_of_concept="Navigate to https://example.com/test?q=<script>alert('test')</script>",
            remediation="Implement proper input validation and output encoding",
            references=["https://owasp.org/www-project-top-ten/"],
            evidence_files=[],
            discovery_date=datetime.now().isoformat(),
            verification_status="Verified",
            bug_bounty_program="Test Program",
            reward_potential="$100-$500",
            technical_details={"vulnerability_type": "xss"},
            business_impact="Low to medium impact on user security",
            risk_rating="High"
        )
        
        test_metadata = ReportMetadata(
            report_id="TEST-REPORT-001",
            report_type="test_assessment",
            target_name="Test Application",
            target_scope=["example.com"],
            assessment_period="2024-01-01",
            generated_date=datetime.now().isoformat(),
            generated_by="AEGIS-X Test System",
            client_name="Test Client",
            engagement_type="System Verification",
            report_classification="Test",
            version="1.0"
        )
        
        # Generate test reports
        reports = await report_generator.generate_comprehensive_report([test_finding], test_metadata)
        logger.info(f"✅ Generated {len(reports)} report formats")
        
        for format_type, path in reports.items():
            if Path(path).exists():
                logger.info(f"   📄 {format_type.upper()}: {path}")
        
        # Test 6: Test bug bounty report generation
        logger.info("🎯 Testing bug bounty report generation...")
        
        bug_bounty_reports = await report_generator.generate_bug_bounty_reports([test_finding])
        logger.info(f"✅ Generated bug bounty reports for {len(bug_bounty_reports)} platforms")
        
        for platform, platform_reports in bug_bounty_reports.items():
            logger.info(f"   🏆 {platform.upper()}: {len(platform_reports)} reports")
        
        logger.info("🎉 All tests completed successfully!")
        logger.info("✅ AEGIS-X system is functioning correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def test_payload_effectiveness():
    """Test payload effectiveness"""
    
    logger.info("🧪 Testing Payload Effectiveness")
    
    try:
        from core.advanced_exploitation_engine import AdvancedExploitationEngine
        
        engine = AdvancedExploitationEngine()
        
        # Test against a safe target (httpbin.org)
        test_url = "https://httpbin.org/get"
        
        logger.info(f"🎯 Testing payloads against: {test_url}")
        
        # Test XSS payloads
        results = await engine.execute_advanced_exploitation(test_url, "xss")
        
        logger.info(f"📊 Tested {len(results)} payloads")
        successful_tests = [r for r in results if r.success]
        logger.info(f"✅ {len(successful_tests)} payloads showed potential indicators")
        
        if successful_tests:
            logger.info("🔍 Sample successful test:")
            sample = successful_tests[0]
            logger.info(f"   Payload ID: {sample.payload_id}")
            logger.info(f"   Response Code: {sample.response_code}")
            logger.info(f"   Impact Level: {sample.impact_level}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Payload test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 AEGIS-X System Verification Test")
    print("=" * 50)
    
    async def run_tests():
        # Test 1: Basic functionality
        basic_test = await test_basic_functionality()
        
        if basic_test:
            print("\n" + "=" * 50)
            # Test 2: Payload effectiveness (optional)
            payload_test = await test_payload_effectiveness()
            
            if payload_test:
                print("\n🎉 All tests passed! AEGIS-X is ready for operation.")
                print("🔥 System Status: OPERATIONAL")
                return True
        
        print("\n❌ Some tests failed. Please check the logs.")
        return False
    
    # Run tests
    success = asyncio.run(run_tests())
    
    if success:
        print("\n📋 Next Steps:")
        print("1. Run full system test: python aegis_x_master.py --test")
        print("2. Start hunting campaign: python aegis_x_master.py --targets https://example.com")
        print("3. Check output directory for reports and evidence")
    
    return success

if __name__ == "__main__":
    main()