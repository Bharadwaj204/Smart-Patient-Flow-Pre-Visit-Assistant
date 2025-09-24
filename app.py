"""
Streamlit UI for Smart Patient Flow & Pre-Visit Assistant (SPFPA)
Main application interface for patient interaction.
"""

import streamlit as st
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rag_pipeline import setup_rag_pipeline
from src.patient_intake import PatientIntakeSystem, PatientInfo, VisitPlan


# Page configuration
st.set_page_config(
    page_title="SuperHealth Pre-Visit Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .section-header {
        background: #f8fafc;
        padding: 0.8rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    
    .emergency-alert {
        background: #fef2f2;
        border: 2px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .urgent-alert {
        background: #fefbeb;
        border: 2px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .routine-info {
        background: #f0f9ff;
        border: 2px solid #06b6d4;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .confidence-score {
        background: #f9fafb;
        border: 1px solid #d1d5db;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'rag_pipeline' not in st.session_state:
        with st.spinner("Initializing AI system... This may take a moment."):
            try:
                st.session_state.rag_pipeline = setup_rag_pipeline()
                st.session_state.intake_system = PatientIntakeSystem(st.session_state.rag_pipeline)
                st.session_state.initialized = True
            except Exception as e:
                st.session_state.initialized = False
                st.session_state.init_error = str(e)
    
    if 'patient_session' not in st.session_state:
        st.session_state.patient_session = None
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'welcome'
    
    if 'visit_plan' not in st.session_state:
        st.session_state.visit_plan = None


def display_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🏥 SuperHealth Pre-Visit Assistant</h1>
        <p>Zero wait times, fixed pricing, patient-first experience</p>
    </div>
    """, unsafe_allow_html=True)


def display_welcome():
    """Display welcome screen."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Welcome to Your Pre-Visit Assistant")
        st.write("""
        Our AI-powered assistant will help you:
        - ✅ Get personalized department recommendations
        - 💰 Check insurance coverage and copays
        - 📋 Prepare required documents
        - ⏰ Find optimal visit times
        - 🚨 Identify urgent care needs
        """)
        
        st.info("**Important:** This tool provides guidance only. Always consult healthcare professionals for medical advice.")
        
        if st.button("Start Your Pre-Visit Assessment", type="primary", use_container_width=True):
            st.session_state.patient_session = st.session_state.intake_system.start_new_intake()
            st.session_state.current_step = 'basic_info'
            st.rerun()
    
    with col2:
        st.image("https://via.placeholder.com/300x200/3b82f6/ffffff?text=SuperHealth+Medical", caption="SuperHealth Medical Center")
        
        st.markdown("### Quick Access")
        
        if st.button("🚨 Emergency Guidance"):
            st.error("**If this is a medical emergency, call 911 immediately.**")
            st.write("For emergency situations:")
            st.write("- Call 911")
            st.write("- Go to nearest emergency room")
            st.write("- Don't drive yourself if severe symptoms")
        
        if st.button("📞 Contact Hospital"):
            st.info("**SuperHealth Medical Center**\n\nPhone: (555) 123-HEALTH\nAddress: 123 Health Way, Medical City")


def collect_basic_info():
    """Collect basic patient information."""
    st.markdown('<div class="section-header"><h3>👤 Basic Information</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
    
    with col2:
        phone = st.text_input("Phone Number", placeholder="555-123-4567")
        email = st.text_input("Email (optional)", placeholder="patient@email.com")
    
    if st.button("Next: Describe Your Symptoms", type="primary"):
        if age and gender and phone:
            st.session_state.intake_system.collect_basic_info(age, gender)
            st.session_state.intake_system.collect_contact_info(phone, email if email else None)
            st.session_state.current_step = 'symptoms'
            st.rerun()
        else:
            st.error("Please fill in all required fields (Age, Gender, Phone)")


def collect_symptoms():
    """Collect symptom information."""
    st.markdown('<div class="section-header"><h3>🔍 Symptoms & Chief Complaint</h3></div>', unsafe_allow_html=True)
    
    # Main complaint
    chief_complaint = st.text_area(
        "What brings you to the hospital today? (Main concern)",
        placeholder="Describe your main symptom or reason for visit...",
        height=100
    )
    
    # Symptom details
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Symptom Details")
        symptom_options = [
            "Chest pain", "Shortness of breath", "Fever", "Headache", "Nausea",
            "Abdominal pain", "Back pain", "Joint pain", "Skin rash", "Dizziness",
            "Fatigue", "Cough", "Other"
        ]
        symptoms = st.multiselect("Select symptoms you're experiencing:", symptom_options)
        
        if "Other" in symptoms:
            other_symptoms = st.text_input("Describe other symptoms:")
            if other_symptoms:
                symptoms = [s for s in symptoms if s != "Other"] + [other_symptoms]
        
        duration = st.selectbox(
            "How long have you had these symptoms?",
            ["Less than 1 hour", "1-6 hours", "6-24 hours", "1-3 days", "1-2 weeks", "More than 2 weeks"]
        )
    
    with col2:
        st.subheader("Severity & Location")
        severity = st.selectbox(
            "How would you rate your symptom severity?",
            ["Mild", "Moderate", "Severe", "Very Severe"]
        )
        
        pain_scale = st.slider("Pain level (if applicable)", 0, 10, 0)
        
        location = st.text_input("Where is the pain/discomfort located?", placeholder="e.g., chest, abdomen, back")
    
    if st.button("Next: Medical History", type="primary"):
        if chief_complaint and symptoms and duration and severity:
            st.session_state.intake_system.collect_symptoms(
                chief_complaint=chief_complaint,
                symptoms=symptoms,
                duration=duration,
                severity=severity,
                location=location if location else None
            )
            st.session_state.current_step = 'medical_history'
            st.rerun()
        else:
            st.error("Please fill in all required fields")
    
    if st.button("← Back", key="back_from_symptoms"):
        st.session_state.current_step = 'basic_info'
        st.rerun()


def collect_medical_history():
    """Collect medical history information."""
    st.markdown('<div class="section-header"><h3>📋 Medical History</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Medical Conditions")
        medical_conditions = st.multiselect(
            "Do you have any of these conditions?",
            ["Diabetes", "High blood pressure", "Heart disease", "Asthma", "Cancer", 
             "Kidney disease", "Liver disease", "Mental health conditions", "None"]
        )
        
        other_conditions = st.text_area(
            "Other medical conditions:",
            placeholder="List any other medical conditions...",
            height=80
        )
        
        if other_conditions:
            medical_conditions.extend([c.strip() for c in other_conditions.split(',') if c.strip()])
    
    with col2:
        st.subheader("Medications & Allergies")
        medications = st.text_area(
            "Current medications:",
            placeholder="List current medications (one per line)...",
            height=80
        )
        
        allergies = st.text_area(
            "Allergies:",
            placeholder="List any allergies (medications, foods, etc.)...",
            height=80
        )
    
    # Process inputs
    med_list = [m.strip() for m in medications.split('\n') if m.strip()] if medications else []
    allergy_list = [a.strip() for a in allergies.split('\n') if a.strip()] if allergies else []
    history_list = medical_conditions if "None" not in medical_conditions else []
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("Next: Insurance Information", type="primary"):
            st.session_state.intake_system.collect_medical_history(
                medical_history=history_list,
                medications=med_list,
                allergies=allergy_list
            )
            st.session_state.current_step = 'insurance'
            st.rerun()
    
    with col4:
        if st.button("← Back", key="back_from_history"):
            st.session_state.current_step = 'symptoms'
            st.rerun()


def collect_insurance():
    """Collect insurance information."""
    st.markdown('<div class="section-header"><h3>💳 Insurance Information</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        insurance_provider = st.selectbox(
            "Insurance Provider",
            ["Blue Cross Blue Shield", "Aetna", "Cigna", "UnitedHealthcare", 
             "Medicare", "Medicaid", "Tricare", "Self-Pay/Uninsured", "Other"]
        )
        
        if insurance_provider == "Other":
            custom_provider = st.text_input("Specify insurance provider:")
            if custom_provider:
                insurance_provider = custom_provider
        
        member_id = st.text_input("Member ID (optional)", placeholder="Insurance member ID")
    
    with col2:
        st.subheader("Visit Preferences")
        preferred_time = st.selectbox(
            "Preferred visit time",
            ["As soon as possible", "This morning", "This afternoon", 
             "Tomorrow", "Within a week", "Flexible"]
        )
        
        urgency = st.selectbox(
            "How urgent do you feel this is?",
            ["Very urgent", "Somewhat urgent", "Not urgent", "Routine check-up"]
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("Generate Visit Plan", type="primary"):
            st.session_state.intake_system.collect_insurance_info(insurance_provider, member_id)
            st.session_state.intake_system.collect_preferences(preferred_time, urgency)
            
            # Generate visit plan
            with st.spinner("Analyzing your information and generating recommendations..."):
                try:
                    st.session_state.visit_plan = st.session_state.intake_system.generate_visit_plan()
                    st.session_state.current_step = 'results'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating visit plan: {str(e)}")
    
    with col4:
        if st.button("← Back", key="back_from_insurance"):
            st.session_state.current_step = 'medical_history'
            st.rerun()


def display_results():
    """Display the visit plan results."""
    if not st.session_state.visit_plan:
        st.error("No visit plan available. Please complete the intake process.")
        return
    
    plan = st.session_state.visit_plan
    triage = plan.triage_recommendation
    patient = plan.patient_info
    
    # Display appropriate alert based on urgency
    if triage.urgency_level == "EMERGENCY":
        st.markdown(f"""
        <div class="emergency-alert">
            <h2>🚨 EMERGENCY RECOMMENDATION</h2>
            <p><strong>Seek immediate medical attention!</strong></p>
        </div>
        """, unsafe_allow_html=True)
    elif triage.urgency_level == "URGENT":
        st.markdown(f"""
        <div class="urgent-alert">
            <h2>⚠️ URGENT CARE NEEDED</h2>
            <p><strong>Please seek care today.</strong></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="routine-info">
            <h2>ℹ️ ROUTINE CARE RECOMMENDATION</h2>
            <p><strong>Schedule an appointment when convenient.</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main recommendations
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Your Visit Plan")
        
        # Key recommendations
        st.markdown("#### 🏥 Recommended Department")
        st.success(f"**{triage.recommended_department}**")
        
        st.markdown("#### ⏰ Timing")
        st.info(f"**Check-in:** {plan.check_in_time}")
        st.info(f"**Estimated wait:** {triage.estimated_wait_time}")
        st.info(f"**Total visit time:** {plan.estimated_total_time}")
        
        # Next steps
        st.markdown("#### 📝 Next Steps")
        for i, step in enumerate(triage.next_steps, 1):
            st.write(f"{i}. {step}")
        
        # Required documents
        st.markdown("#### 📄 Required Documents")
        for doc in triage.required_documents:
            st.write(f"• {doc}")
    
    with col2:
        st.markdown("### 💡 Quick Info")
        
        # Urgency badge
        urgency_color = {
            "EMERGENCY": "🔴",
            "URGENT": "🟡", 
            "ROUTINE": "🟢"
        }
        
        st.markdown(f"""
        **Urgency Level:** {urgency_color.get(triage.urgency_level, '⚪')} {triage.urgency_level}
        
        **Priority Score:** {triage.priority_score}/5
        
        **Confidence:** {plan.confidence_score:.0%}
        """)
        
        # Insurance info
        if triage.insurance_coverage:
            st.markdown("#### 💳 Insurance")
            provider = triage.insurance_coverage.get('provider', 'Unknown')
            accepted = triage.insurance_coverage.get('accepted', True)
            st.write(f"**Provider:** {provider}")
            st.write(f"**Accepted:** {'✅ Yes' if accepted else '❌ No'}")
            
            if 'emergency_copay' in triage.insurance_coverage:
                st.write(f"**Estimated Copay:** {triage.insurance_coverage['emergency_copay']}")
    
    # Preparation instructions
    if triage.preparation_instructions:
        st.markdown("### 🎯 Preparation Instructions")
        for instruction in triage.preparation_instructions:
            st.write(f"• {instruction}")
    
    # Warning signs
    if triage.warning_signs:
        st.markdown("### ⚠️ Warning Signs to Watch For")
        st.warning("Seek immediate emergency care if you experience:")
        for warning in triage.warning_signs:
            st.write(f"• {warning}")
    
    # Logistics
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 🚗 Logistics")
        st.write(f"**Parking:** {plan.parking_info}")
        st.write(f"**Directions:** {plan.directions}")
    
    with col4:
        st.markdown("### 📞 Contact Information")
        st.write("**SuperHealth Medical Center**")
        st.write("Phone: (555) 123-HEALTH")
        st.write("Emergency: 911")
    
    # Medical disclaimer
    st.markdown("### ⚖️ Important Disclaimer")
    st.error(triage.medical_disclaimer)
    
    # Action buttons
    col5, col6, col7 = st.columns(3)
    
    with col5:
        if st.button("📞 Call Hospital", type="primary"):
            st.info("Call (555) 123-HEALTH to schedule your appointment")
    
    with col6:
        if st.button("🔄 Start New Assessment"):
            # Reset session
            for key in ['patient_session', 'visit_plan', 'current_step']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_step = 'welcome'
            st.rerun()
    
    with col7:
        if st.button("💾 Save Results"):
            # Create downloadable summary
            summary = generate_summary_text(plan)
            st.download_button(
                label="Download Visit Plan",
                data=summary,
                file_name=f"visit_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )


def generate_summary_text(plan: VisitPlan) -> str:
    """Generate a text summary of the visit plan."""
    patient = plan.patient_info
    triage = plan.triage_recommendation
    
    summary = f"""
SUPERHEALTH MEDICAL CENTER - VISIT PLAN
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PATIENT INFORMATION:
- Age: {patient.age}
- Gender: {patient.gender}
- Chief Complaint: {patient.chief_complaint}
- Insurance: {patient.insurance_provider}

RECOMMENDATIONS:
- Urgency Level: {triage.urgency_level}
- Recommended Department: {triage.recommended_department}
- Estimated Wait Time: {triage.estimated_wait_time}
- Check-in Time: {plan.check_in_time}

NEXT STEPS:
{chr(10).join([f"- {step}" for step in triage.next_steps])}

REQUIRED DOCUMENTS:
{chr(10).join([f"- {doc}" for doc in triage.required_documents])}

PREPARATION:
{chr(10).join([f"- {prep}" for prep in triage.preparation_instructions])}

CONTACT:
SuperHealth Medical Center
Phone: (555) 123-HEALTH
Emergency: 911

DISCLAIMER:
{triage.medical_disclaimer}
"""
    return summary


def display_sidebar():
    """Display sidebar with additional information."""
    with st.sidebar:
        st.markdown("### 🏥 SuperHealth Info")
        
        st.markdown("**Hours:**")
        st.write("• Emergency: 24/7")
        st.write("• Clinics: Mon-Fri 7AM-7PM")
        st.write("• Weekend: Sat-Sun 8AM-4PM")
        
        st.markdown("**Services:**")
        st.write("• Emergency Department")
        st.write("• Urgent Care")
        st.write("• Primary Care")
        st.write("• Specialist Care")
        st.write("• Laboratory Services")
        st.write("• Radiology")
        
        st.markdown("**Contact:**")
        st.write("📞 (555) 123-HEALTH")
        st.write("🚨 911 for emergencies")
        st.write("🌐 www.superhealth.com")
        
        if st.session_state.get('current_step') != 'welcome':
            st.markdown("---")
            if st.button("🏠 Start Over", use_container_width=True):
                # Reset session
                for key in ['patient_session', 'visit_plan', 'current_step']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_step = 'welcome'
                st.rerun()


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Check if system is initialized
    if not st.session_state.get('initialized', False):
        if 'init_error' in st.session_state:
            st.error(f"Failed to initialize system: {st.session_state.init_error}")
            st.info("Please check your setup and try refreshing the page.")
        return
    
    # Display sidebar
    display_sidebar()
    
    # Main content based on current step
    current_step = st.session_state.get('current_step', 'welcome')
    
    if current_step == 'welcome':
        display_welcome()
    elif current_step == 'basic_info':
        collect_basic_info()
    elif current_step == 'symptoms':
        collect_symptoms()
    elif current_step == 'medical_history':
        collect_medical_history()
    elif current_step == 'insurance':
        collect_insurance()
    elif current_step == 'results':
        display_results()
    else:
        st.error("Unknown step. Please start over.")
        st.session_state.current_step = 'welcome'
        st.rerun()


if __name__ == "__main__":
    main()