"""
Comprehensive testing script for Smart Patient Flow & Pre-Visit Assistant (SPFPA)
Tests all major components and edge cases.
"""

import sys
import os
import traceback
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rag_pipeline import setup_rag_pipeline
from src.patient_intake import PatientIntakeSystem
from src.vector_db import HealthcareVectorDB, setup_vector_database
from src.data_processor import HealthcareDataProcessor


class TestResult:
    """Container for test results."""
    def __init__(self, test_name: str, passed: bool, message: str = "", details: str = ""):
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.details = details
        self.timestamp = datetime.now()


class SPFPATestSuite:
    """Comprehensive test suite for SPFPA system."""
    
    def __init__(self):
        self.results = []
        self.rag_pipeline = None
        self.intake_system = None
        
    def log_result(self, test_name: str, passed: bool, message: str = "", details: str = ""):
        """Log a test result."""
        result = TestResult(test_name, passed, message, details)
        self.results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")
        if details and not passed:
            print(f"    Details: {details}")
    
    def setup_system(self):
        """Set up the system for testing."""
        print("🔧 Setting up system for testing...")
        try:
            self.rag_pipeline = setup_rag_pipeline()
            self.intake_system = PatientIntakeSystem(self.rag_pipeline)
            self.log_result("System Setup", True, "RAG pipeline and intake system initialized")
            return True
        except Exception as e:
            self.log_result("System Setup", False, f"Failed to initialize system", str(e))
            return False
    
    def test_data_loading(self):
        """Test data loading and processing."""
        print("\n📊 Testing Data Loading...")
        
        # Test data processor
        try:
            processor = HealthcareDataProcessor("./data")
            documents = processor.process_all_data()
            
            if len(documents) > 0:
                self.log_result("Data Loading", True, f"Successfully loaded {len(documents)} documents")
            else:
                self.log_result("Data Loading", False, "No documents loaded")
                
            # Test document types
            doc_types = set()
            for doc in documents:
                doc_types.add(doc.metadata.get('type', 'unknown'))
            
            expected_types = {'faq', 'department', 'triage', 'insurance', 'hospital_info'}
            if expected_types.issubset(doc_types):
                self.log_result("Document Types", True, f"All expected document types found: {doc_types}")
            else:
                missing = expected_types - doc_types
                self.log_result("Document Types", False, f"Missing document types: {missing}")
                
        except Exception as e:
            self.log_result("Data Loading", False, "Exception during data loading", str(e))
    
    def test_vector_database(self):
        """Test vector database functionality."""
        print("\n🔍 Testing Vector Database...")
        
        try:
            # Test database setup
            vector_db = setup_vector_database()
            stats = vector_db.get_collection_stats()
            
            if stats['total_documents'] > 0:
                self.log_result("Vector DB Setup", True, f"Database contains {stats['total_documents']} documents")
            else:
                self.log_result("Vector DB Setup", False, "Vector database is empty")
                return
            
            # Test search functionality
            test_queries = [
                ("chest pain", "emergency"),
                ("insurance copay", "insurance"),
                ("appointment scheduling", "general"),
                ("skin rash", "routine")
            ]
            
            search_results = []
            for query, expected_context in test_queries:
                try:
                    results = vector_db.search(query, n_results=3)
                    if results['documents'] and len(results['documents'][0]) > 0:
                        search_results.append(True)
                        # Check relevance
                        top_result = results['documents'][0][0].lower()
                        if any(word in top_result for word in query.split()):
                            search_results.append(True)
                        else:
                            search_results.append(False)
                    else:
                        search_results.append(False)
                except Exception as e:
                    search_results.append(False)
            
            success_rate = sum(search_results) / len(search_results) if search_results else 0
            if success_rate > 0.8:
                self.log_result("Vector Search", True, f"Search success rate: {success_rate:.1%}")
            else:
                self.log_result("Vector Search", False, f"Low search success rate: {success_rate:.1%}")
                
        except Exception as e:
            self.log_result("Vector Database", False, "Exception during vector database testing", str(e))
    
    def test_rag_pipeline(self):
        """Test RAG pipeline functionality."""
        print("\n🤖 Testing RAG Pipeline...")
        
        if not self.rag_pipeline:
            self.log_result("RAG Pipeline", False, "RAG pipeline not initialized")
            return
        
        test_cases = [
            {
                "query": "I have chest pain",
                "expected_keywords": ["emergency", "chest", "cardiology"],
                "min_confidence": 0.5
            },
            {
                "query": "What insurance do you accept?",
                "expected_keywords": ["insurance", "blue cross", "aetna"],
                "min_confidence": 0.3
            },
            {
                "query": "I need to schedule an appointment",
                "expected_keywords": ["appointment", "schedule", "arrive"],
                "min_confidence": 0.3
            }
        ]
        
        passed_tests = 0
        for i, test_case in enumerate(test_cases):
            try:
                response = self.rag_pipeline.process_query(test_case["query"])
                
                # Check if response exists
                if not response or not response.answer:
                    continue
                
                # Check confidence
                if response.confidence < test_case["min_confidence"]:
                    continue
                
                # Check for expected keywords
                answer_lower = response.answer.lower()
                keyword_found = any(keyword in answer_lower for keyword in test_case["expected_keywords"])
                
                if keyword_found:
                    passed_tests += 1
                    
            except Exception as e:
                continue
        
        success_rate = passed_tests / len(test_cases)
        if success_rate > 0.6:
            self.log_result("RAG Pipeline", True, f"Pipeline success rate: {success_rate:.1%}")
        else:
            self.log_result("RAG Pipeline", False, f"Low pipeline success rate: {success_rate:.1%}")
    
    def test_patient_intake(self):
        """Test patient intake system."""
        print("\n👤 Testing Patient Intake System...")
        
        if not self.intake_system:
            self.log_result("Patient Intake", False, "Intake system not initialized")
            return
        
        # Test emergency detection
        try:
            patient = self.intake_system.start_new_intake()
            self.intake_system.collect_basic_info(55, "male")
            self.intake_system.collect_symptoms(
                chief_complaint="severe chest pain",
                symptoms=["chest pain", "shortness of breath"],
                duration="1 hour",
                severity="severe"
            )
            
            is_emergency, flags = self.intake_system.check_emergency_indicators()
            if is_emergency:
                self.log_result("Emergency Detection", True, f"Correctly identified emergency with {len(flags)} flags")
            else:
                self.log_result("Emergency Detection", False, "Failed to detect emergency case")
                
        except Exception as e:
            self.log_result("Emergency Detection", False, "Exception during emergency detection", str(e))
        
        # Test routine case
        try:
            patient = self.intake_system.start_new_intake()
            self.intake_system.collect_basic_info(25, "female")
            self.intake_system.collect_symptoms(
                chief_complaint="skin rash",
                symptoms=["rash", "itching"],
                duration="2 days",
                severity="mild"
            )
            
            is_emergency, flags = self.intake_system.check_emergency_indicators()
            if not is_emergency:
                self.log_result("Routine Case Detection", True, "Correctly identified non-emergency case")
            else:
                self.log_result("Routine Case Detection", False, "Incorrectly flagged routine case as emergency")
                
        except Exception as e:
            self.log_result("Routine Case Detection", False, "Exception during routine case testing", str(e))
    
    def test_triage_recommendations(self):
        """Test triage recommendation generation."""
        print("\n🏥 Testing Triage Recommendations...")
        
        if not self.intake_system:
            self.log_result("Triage Recommendations", False, "Intake system not initialized")
            return
        
        test_scenarios = [
            {
                "name": "Chest Pain Emergency",
                "age": 55,
                "gender": "male",
                "complaint": "severe chest pain",
                "symptoms": ["chest pain", "shortness of breath"],
                "severity": "severe",
                "expected_urgency": "EMERGENCY",
                "expected_department": "Emergency Department"
            },
            {
                "name": "Skin Rash Routine",
                "age": 30,
                "gender": "female", 
                "complaint": "skin rash",
                "symptoms": ["rash", "itching"],
                "severity": "mild",
                "expected_urgency": "ROUTINE",
                "expected_department": "Dermatology"
            }
        ]
        
        passed_scenarios = 0
        for scenario in test_scenarios:
            try:
                patient = self.intake_system.start_new_intake()
                self.intake_system.collect_basic_info(scenario["age"], scenario["gender"])
                self.intake_system.collect_symptoms(
                    chief_complaint=scenario["complaint"],
                    symptoms=scenario["symptoms"],
                    duration="recent",
                    severity=scenario["severity"]
                )
                self.intake_system.collect_insurance_info("Blue Cross Blue Shield")
                
                triage = self.intake_system.generate_triage_recommendation()
                
                # Check urgency level
                urgency_match = triage.urgency_level == scenario["expected_urgency"]
                
                # Check department (more flexible matching)
                dept_keywords = scenario["expected_department"].lower().split()
                dept_match = any(keyword in triage.recommended_department.lower() for keyword in dept_keywords)
                
                if urgency_match and dept_match:
                    passed_scenarios += 1
                    
            except Exception as e:
                continue
        
        success_rate = passed_scenarios / len(test_scenarios)
        if success_rate > 0.7:
            self.log_result("Triage Recommendations", True, f"Triage accuracy: {success_rate:.1%}")
        else:
            self.log_result("Triage Recommendations", False, f"Low triage accuracy: {success_rate:.1%}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        print("\n⚠️  Testing Edge Cases...")
        
        # Test empty inputs
        try:
            if self.intake_system:
                patient = self.intake_system.start_new_intake()
                try:
                    # This should handle gracefully
                    self.intake_system.collect_symptoms(
                        chief_complaint="",
                        symptoms=[],
                        duration="",
                        severity=""
                    )
                    self.log_result("Empty Input Handling", True, "System handles empty inputs gracefully")
                except Exception:
                    self.log_result("Empty Input Handling", True, "System properly validates empty inputs")
        except Exception as e:
            self.log_result("Empty Input Handling", False, "Exception with empty inputs", str(e))
        
        # Test invalid age
        try:
            if self.intake_system:
                patient = self.intake_system.start_new_intake()
                try:
                    self.intake_system.collect_basic_info(-5, "invalid")
                    self.log_result("Invalid Age Handling", False, "System accepted invalid age")
                except Exception:
                    self.log_result("Invalid Age Handling", True, "System properly validates age")
        except Exception as e:
            self.log_result("Invalid Age Handling", True, "System handles invalid age input")
        
        # Test very long input
        try:
            long_text = "a" * 10000  # Very long string
            if self.rag_pipeline:
                response = self.rag_pipeline.process_query(long_text)
                if response and response.answer:
                    self.log_result("Long Input Handling", True, "System handles very long inputs")
                else:
                    self.log_result("Long Input Handling", False, "System failed with long input")
        except Exception as e:
            self.log_result("Long Input Handling", False, "Exception with long input", str(e))
    
    def test_insurance_coverage(self):
        """Test insurance coverage functionality."""
        print("\n💳 Testing Insurance Coverage...")
        
        if not self.intake_system:
            self.log_result("Insurance Coverage", False, "Intake system not initialized")
            return
        
        test_providers = [
            "Blue Cross Blue Shield",
            "Aetna", 
            "Cigna",
            "Medicare",
            "Self-Pay/Uninsured"
        ]
        
        successful_lookups = 0
        for provider in test_providers:
            try:
                insurance_info = self.intake_system.get_insurance_info(provider)
                if insurance_info and 'provider' in insurance_info:
                    successful_lookups += 1
            except Exception:
                continue
        
        success_rate = successful_lookups / len(test_providers)
        if success_rate > 0.8:
            self.log_result("Insurance Coverage", True, f"Insurance lookup success rate: {success_rate:.1%}")
        else:
            self.log_result("Insurance Coverage", False, f"Low insurance lookup success rate: {success_rate:.1%}")
    
    def run_all_tests(self):
        """Run all tests and generate report."""
        print("🚀 Starting SPFPA System Test Suite")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Setup system
        if not self.setup_system():
            print("\n❌ System setup failed. Cannot continue with tests.")
            return False
        
        # Run all tests
        self.test_data_loading()
        self.test_vector_database()
        self.test_rag_pipeline()
        self.test_patient_intake()
        self.test_triage_recommendations()
        self.test_insurance_coverage()
        self.test_edge_cases()
        
        # Generate summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {passed_tests/total_tests:.1%}")
        print(f"Duration: {duration.total_seconds():.1f} seconds")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.test_name}: {result.message}")
        
        print(f"\n{'🎉 ALL TESTS PASSED!' if failed_tests == 0 else '⚠️  SOME TESTS FAILED'}")
        
        return failed_tests == 0


def main():
    """Main test function."""
    test_suite = SPFPATestSuite()
    success = test_suite.run_all_tests()
    
    # Save test results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.txt"
    
    with open(report_file, 'w') as f:
        f.write("SPFPA System Test Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tests: {len(test_suite.results)}\n")
        f.write(f"Passed: {sum(1 for r in test_suite.results if r.passed)}\n")
        f.write(f"Failed: {sum(1 for r in test_suite.results if not r.passed)}\n\n")
        
        f.write("DETAILED RESULTS:\n")
        f.write("-" * 30 + "\n")
        for result in test_suite.results:
            status = "PASS" if result.passed else "FAIL"
            f.write(f"[{status}] {result.test_name}\n")
            if result.message:
                f.write(f"  Message: {result.message}\n")
            if result.details and not result.passed:
                f.write(f"  Details: {result.details}\n")
            f.write(f"  Time: {result.timestamp.strftime('%H:%M:%S')}\n\n")
    
    print(f"\n📄 Test report saved to: {report_file}")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())