"""
Patient intake and pre-triage system for healthcare pre-visit assistance.
Collects patient information and provides intelligent triage recommendations.
"""

import os
import sys
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_pipeline import HealthcareRAGPipeline, RAGResponse


@dataclass
class PatientInfo:
    """Patient information collected during intake."""
    # Basic demographics
    age: Optional[int] = None
    gender: Optional[str] = None
    
    # Symptoms and medical info
    chief_complaint: Optional[str] = None
    symptoms: List[str] = field(default_factory=list)
    symptom_duration: Optional[str] = None
    symptom_severity: Optional[int] = None  # 1-10 scale
    pain_location: Optional[str] = None
    
    # Medical history
    medical_history: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    
    # Insurance and contact
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    
    # Visit preferences
    preferred_time: Optional[str] = None
    urgency_perception: Optional[str] = None  # patient's perception
    
    # Internal tracking
    session_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TriageRecommendation:
    """Triage recommendation based on patient intake."""
    urgency_level: str  # EMERGENCY, URGENT, ROUTINE
    recommended_department: str
    estimated_wait_time: str
    priority_score: int  # 1-5, 1 being highest priority
    
    # Recommendations
    next_steps: List[str]
    required_documents: List[str]
    preparation_instructions: List[str]
    
    # Scheduling
    recommended_time_slots: List[str]
    alternative_options: List[str]
    
    # Insurance info
    insurance_coverage: Dict[str, Any]
    estimated_cost: str
    
    # Warnings and disclaimers
    warning_signs: List[str]
    medical_disclaimer: str


@dataclass
class VisitPlan:
    """Comprehensive visit plan for the patient."""
    patient_info: PatientInfo
    triage_recommendation: TriageRecommendation
    
    # Visit logistics
    check_in_time: str
    estimated_total_time: str
    parking_info: str = "Free parking available in main lot. Valet service for emergency patients."
    directions: str = "Enter through main entrance. Follow signs to appropriate department."
    
    # Follow-up
    follow_up_needed: bool = True
    specialist_referral: Optional[str] = None
    
    # Summary
    visit_summary: str = ""
    confidence_score: float = 0.85


class PatientIntakeSystem:
    """Main system for patient intake and pre-triage."""
    
    def __init__(self, rag_pipeline: HealthcareRAGPipeline):
        """Initialize the intake system with RAG pipeline."""
        self.rag_pipeline = rag_pipeline
        self.current_patient = None
        
        # Symptom severity mappings
        self.severity_mappings = {
            'mild': 1,
            'moderate': 5,
            'severe': 9,
            'unbearable': 10
        }
        
        # Emergency keywords for immediate triage
        self.emergency_keywords = [
            'chest pain', 'difficulty breathing', 'unconscious', 'bleeding heavily',
            'severe injury', 'overdose', 'suicide', 'heart attack', 'stroke',
            'allergic reaction', 'severe burn', 'broken bone', 'head injury'
        ]
        
        # Time slot templates
        self.time_slots = {
            'emergency': ['immediately', 'ASAP'],
            'urgent': ['within 2 hours', 'today if possible', 'this evening'],
            'routine': ['within 1-2 weeks', 'next available appointment', 'at your convenience']
        }
        
    def start_new_intake(self) -> PatientInfo:
        """Start a new patient intake session."""
        self.current_patient = PatientInfo()
        return self.current_patient
    
    def collect_basic_info(self, age: int, gender: str) -> None:
        """Collect basic demographic information."""
        if self.current_patient is None:
            self.start_new_intake()
        
        # Type guard ensures current_patient is not None
        assert self.current_patient is not None
        self.current_patient.age = age
        self.current_patient.gender = gender.lower()
    
    def collect_symptoms(
        self,
        chief_complaint: str,
        symptoms: List[str],
        duration: str,
        severity: str,
        location: Optional[str] = None
    ) -> None:
        """Collect symptom information."""
        if self.current_patient is None:
            raise ValueError("Must start intake session first")
            
        self.current_patient.chief_complaint = chief_complaint
        self.current_patient.symptoms = symptoms
        self.current_patient.symptom_duration = duration
        self.current_patient.pain_location = location
        
        # Convert severity to numeric scale
        if severity.lower() in self.severity_mappings:
            self.current_patient.symptom_severity = self.severity_mappings[severity.lower()]
        else:
            try:
                self.current_patient.symptom_severity = int(severity)
            except ValueError:
                self.current_patient.symptom_severity = 5  # Default to moderate
    
    def collect_medical_history(
        self,
        medical_history: List[str],
        medications: List[str],
        allergies: List[str]
    ) -> None:
        """Collect medical history information."""
        if self.current_patient is None:
            raise ValueError("Must start intake session first")
            
        self.current_patient.medical_history = medical_history
        self.current_patient.current_medications = medications
        self.current_patient.allergies = allergies
    
    def collect_insurance_info(self, provider: str, member_id: Optional[str] = None) -> None:
        """Collect insurance information."""
        if self.current_patient is None:
            raise ValueError("Must start intake session first")
            
        self.current_patient.insurance_provider = provider
        self.current_patient.insurance_member_id = member_id
    
    def collect_contact_info(self, phone: str, email: Optional[str] = None) -> None:
        """Collect contact information."""
        if self.current_patient is None:
            raise ValueError("Must start intake session first")
            
        self.current_patient.phone_number = phone
        self.current_patient.email = email
    
    def collect_preferences(self, preferred_time: str, urgency_perception: str) -> None:
        """Collect visit preferences."""
        if self.current_patient is None:
            raise ValueError("Must start intake session first")
            
        self.current_patient.preferred_time = preferred_time
        self.current_patient.urgency_perception = urgency_perception
    
    def check_emergency_indicators(self) -> Tuple[bool, List[str]]:
        """Check if patient has emergency indicators."""
        if self.current_patient is None:
            return False, []
            
        emergency_flags = []
        
        # Check for emergency keywords in chief complaint and symptoms
        all_symptoms = [self.current_patient.chief_complaint or ""] + self.current_patient.symptoms
        symptoms_text = " ".join(all_symptoms).lower()
        
        for keyword in self.emergency_keywords:
            if keyword in symptoms_text:
                emergency_flags.append(f"Emergency keyword detected: {keyword}")
        
        # Check severity score
        if self.current_patient.symptom_severity and self.current_patient.symptom_severity >= 8:
            emergency_flags.append(f"High severity score: {self.current_patient.symptom_severity}/10")
        
        # Age-specific considerations
        if self.current_patient.age:
            if self.current_patient.age >= 65 and "chest pain" in symptoms_text:
                emergency_flags.append("Chest pain in elderly patient")
            if self.current_patient.age < 5 and "fever" in symptoms_text:
                emergency_flags.append("Fever in young child")
        
        return len(emergency_flags) > 0, emergency_flags
    
    def get_insurance_info(self, provider: str) -> Dict[str, Any]:
        """Get insurance information from RAG pipeline."""
        query = f"insurance coverage copay {provider}"
        response = self.rag_pipeline.process_query(query)
        
        # Extract insurance info from response
        insurance_info = {
            'provider': provider,
            'accepted': True,  # Default assumption
            'emergency_copay': 'Contact insurance for details',
            'urgent_care_copay': 'Contact insurance for details',
            'specialist_copay': 'Contact insurance for details',
            'primary_care_copay': 'Contact insurance for details',
            'notes': response.answer
        }
        
        # Try to extract specific copay information from sources
        for source in response.sources:
            if source['type'] == 'insurance' and provider.lower() in source['content_preview'].lower():
                # Parse insurance information
                content = source['content_preview']
                if 'Emergency Copay:' in content:
                    try:
                        emergency_copay = content.split('Emergency Copay:')[1].split('\n')[0].strip()
                        insurance_info['emergency_copay'] = emergency_copay
                    except:
                        pass
        
        return insurance_info
    
    def generate_triage_recommendation(self) -> TriageRecommendation:
        """Generate triage recommendation based on collected information."""
        if self.current_patient is None:
            raise ValueError("No patient information available")
        
        # Check for emergency indicators first
        is_emergency, emergency_flags = self.check_emergency_indicators()
        
        if is_emergency:
            return self._generate_emergency_recommendation(emergency_flags)
        
        # Use RAG pipeline for non-emergency triage
        query = self._build_triage_query()
        response = self.rag_pipeline.process_query(query)
        
        # Determine urgency level
        urgency_level = "ROUTINE"
        if response.triage_info:
            urgency_level = response.triage_info.get('urgency_level', 'ROUTINE')
        
        # Get insurance information
        insurance_info = {}
        if self.current_patient.insurance_provider:
            insurance_info = self.get_insurance_info(self.current_patient.insurance_provider)
        
        # Build recommendation
        return TriageRecommendation(
            urgency_level=urgency_level,
            recommended_department=response.triage_info.get('department', 'Internal Medicine') if response.triage_info else 'Internal Medicine',
            estimated_wait_time=response.triage_info.get('estimated_wait', '15-30 minutes') if response.triage_info else '15-30 minutes',
            priority_score=response.triage_info.get('priority', 3) if response.triage_info else 3,
            next_steps=response.next_steps or [],
            required_documents=["Photo ID", "Insurance card", "Medication list"],
            preparation_instructions=self._generate_preparation_instructions(),
            recommended_time_slots=self._get_recommended_time_slots(urgency_level),
            alternative_options=self._get_alternative_options(urgency_level),
            insurance_coverage=insurance_info,
            estimated_cost=insurance_info.get('primary_care_copay', 'Contact insurance for estimate'),
            warning_signs=self._get_warning_signs(),
            medical_disclaimer="This is not medical advice. Please consult a qualified healthcare provider for proper medical evaluation and treatment."
        )
    
    def _generate_emergency_recommendation(self, emergency_flags: List[str]) -> TriageRecommendation:
        """Generate emergency recommendation."""
        return TriageRecommendation(
            urgency_level="EMERGENCY",
            recommended_department="Emergency Department",
            estimated_wait_time="0-5 minutes",
            priority_score=1,
            next_steps=[
                "🚨 Seek immediate emergency care",
                "Call 911 if symptoms are severe",
                "Go to nearest emergency room",
                "Do not drive yourself if experiencing severe symptoms"
            ],
            required_documents=["Photo ID", "Insurance card"],
            preparation_instructions=[
                "Bring all current medications",
                "Prepare to describe symptoms to medical staff",
                "Have emergency contact information ready"
            ],
            recommended_time_slots=["immediately", "ASAP"],
            alternative_options=["Call 911", "Go to nearest emergency room"],
            insurance_coverage={"emergency_coverage": "Emergency care typically covered"},
            estimated_cost="Emergency copay applies",
            warning_signs=emergency_flags,
            medical_disclaimer="This is an emergency situation. Seek immediate medical attention."
        )
    
    def _build_triage_query(self) -> str:
        """Build query for RAG pipeline based on patient information."""
        # Type guard ensures current_patient is not None
        assert self.current_patient is not None
        
        query_parts = []
        
        if self.current_patient.chief_complaint:
            query_parts.append(self.current_patient.chief_complaint)
        
        query_parts.extend(self.current_patient.symptoms)
        
        if self.current_patient.age:
            query_parts.append(f"age {self.current_patient.age}")
        
        if self.current_patient.symptom_severity:
            if self.current_patient.symptom_severity >= 7:
                query_parts.append("severe symptoms")
            elif self.current_patient.symptom_severity >= 4:
                query_parts.append("moderate symptoms")
        
        return " ".join(query_parts)
    
    def _generate_preparation_instructions(self) -> List[str]:
        """Generate preparation instructions based on patient info."""
        # Type guard ensures current_patient is not None
        assert self.current_patient is not None
        
        instructions = [
            "Arrive 15-30 minutes before your appointment",
            "Bring a list of current medications",
            "Prepare questions for your healthcare provider"
        ]
        
        if self.current_patient.allergies:
            instructions.append("Be prepared to discuss your allergies")
        
        if self.current_patient.medical_history:
            instructions.append("Bring relevant medical history documents")
        
        return instructions
    
    def _get_recommended_time_slots(self, urgency_level: str) -> List[str]:
        """Get recommended time slots based on urgency."""
        return self.time_slots.get(urgency_level.lower(), self.time_slots['routine'])
    
    def _get_alternative_options(self, urgency_level: str) -> List[str]:
        """Get alternative care options."""
        if urgency_level == "EMERGENCY":
            return ["Emergency Department", "Call 911", "Urgent Care (if symptoms improve)"]
        elif urgency_level == "URGENT":
            return ["Urgent Care", "Same-day appointment", "Telehealth consultation"]
        else:
            return ["Regular appointment", "Telehealth consultation", "Walk-in clinic"]
    
    def _get_warning_signs(self) -> List[str]:
        """Get warning signs to watch for."""
        # Type guard ensures current_patient is not None
        assert self.current_patient is not None
        
        warning_signs = [
            "Worsening symptoms",
            "New severe symptoms",
            "Difficulty breathing",
            "Severe pain (8/10 or higher)"
        ]
        
        # Add specific warning signs based on symptoms
        symptoms_text = " ".join([self.current_patient.chief_complaint or ""] + self.current_patient.symptoms).lower()
        
        if "chest" in symptoms_text:
            warning_signs.extend([
                "Pain radiating to arm or jaw",
                "Sweating with chest pain",
                "Nausea with chest pain"
            ])
        
        if "headache" in symptoms_text:
            warning_signs.extend([
                "Sudden severe headache",
                "Headache with stiff neck",
                "Headache with vision changes"
            ])
        
        return warning_signs
    
    def generate_visit_plan(self) -> VisitPlan:
        """Generate comprehensive visit plan."""
        if self.current_patient is None:
            raise ValueError("No patient information available")
        
        triage_rec = self.generate_triage_recommendation()
        
        # Calculate check-in time
        now = datetime.now()
        if triage_rec.urgency_level == "EMERGENCY":
            check_in_time = "Immediately"
            estimated_total_time = "2-4 hours"
        elif triage_rec.urgency_level == "URGENT":
            check_in_time = (now + timedelta(hours=2)).strftime("%I:%M %p today")
            estimated_total_time = "1-2 hours"
        else:
            check_in_time = "Next available appointment"
            estimated_total_time = "1 hour"
        
        # Generate visit summary
        visit_summary = self._generate_visit_summary(triage_rec)
        
        return VisitPlan(
            patient_info=self.current_patient,
            triage_recommendation=triage_rec,
            check_in_time=check_in_time,
            estimated_total_time=estimated_total_time,
            parking_info="Free parking available in main lot. Valet service for emergency patients.",
            directions="Enter through main entrance. Follow signs to appropriate department.",
            follow_up_needed=triage_rec.urgency_level in ["URGENT", "ROUTINE"],
            visit_summary=visit_summary,
            confidence_score=0.85  # Base confidence score
        )
    
    def _generate_visit_summary(self, triage_rec: TriageRecommendation) -> str:
        """Generate a summary of the visit plan."""
        # Type guard ensures current_patient is not None
        assert self.current_patient is not None
        
        patient = self.current_patient
        
        summary_parts = [
            f"Patient: {patient.age}-year-old {patient.gender}",
            f"Chief complaint: {patient.chief_complaint}",
            f"Recommended: {triage_rec.recommended_department}",
            f"Urgency: {triage_rec.urgency_level}",
            f"Estimated wait: {triage_rec.estimated_wait_time}"
        ]
        
        if patient.insurance_provider:
            summary_parts.append(f"Insurance: {patient.insurance_provider}")
        
        return " | ".join(summary_parts)


def test_patient_intake():
    """Test the patient intake system."""
    print("Testing Patient Intake System...")
    
    # Setup RAG pipeline
    from src.rag_pipeline import setup_rag_pipeline
    rag_pipeline = setup_rag_pipeline()
    
    # Initialize intake system
    intake_system = PatientIntakeSystem(rag_pipeline)
    
    # Test case: Chest pain patient
    print("\n" + "="*60)
    print("Test Case: 55-year-old with chest tightness")
    print("="*60)
    
    # Start intake
    patient = intake_system.start_new_intake()
    
    # Collect information
    intake_system.collect_basic_info(age=55, gender="male")
    intake_system.collect_symptoms(
        chief_complaint="chest tightness on and off since this morning",
        symptoms=["chest tightness", "mild discomfort"],
        duration="since this morning",
        severity="moderate",
        location="chest"
    )
    intake_system.collect_medical_history(
        medical_history=["hypertension"],
        medications=["lisinopril"],
        allergies=["penicillin"]
    )
    intake_system.collect_insurance_info("Blue Cross Blue Shield")
    intake_system.collect_contact_info(phone="555-123-4567", email="patient@email.com")
    intake_system.collect_preferences(
        preferred_time="this morning",
        urgency_perception="somewhat urgent"
    )
    
    # Generate visit plan
    visit_plan = intake_system.generate_visit_plan()
    
    # Display results
    print(f"\nVisit Summary: {visit_plan.visit_summary}")
    print(f"Urgency Level: {visit_plan.triage_recommendation.urgency_level}")
    print(f"Recommended Department: {visit_plan.triage_recommendation.recommended_department}")
    print(f"Check-in Time: {visit_plan.check_in_time}")
    print(f"Estimated Total Time: {visit_plan.estimated_total_time}")
    
    print(f"\nNext Steps:")
    for step in visit_plan.triage_recommendation.next_steps:
        print(f"- {step}")
    
    print(f"\nRequired Documents:")
    for doc in visit_plan.triage_recommendation.required_documents:
        print(f"- {doc}")
    
    print(f"\nInsurance Coverage:")
    for key, value in visit_plan.triage_recommendation.insurance_coverage.items():
        print(f"- {key}: {value}")
    
    print(f"\n{visit_plan.triage_recommendation.medical_disclaimer}")


if __name__ == "__main__":
    test_patient_intake()