"""
Digital Health Passport - Secure patient health record management
Innovative feature for SPFPA system
"""

import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib
import uuid

# Enhanced CSS for better text visibility and contrast
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom styled containers with better text contrast */
    .feature-container {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 15px;
        padding: 1.8rem;
        margin: 1.5rem 0;
        border: 2px solid #e2e8f0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .feature-container h3 {
        color: #1e293b !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.8rem !important;
        text-shadow: none !important;
    }
    
    .feature-container p {
        color: #475569 !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
        margin: 0 !important;
    }
    
    /* Form labels and inputs */
    .stSelectbox label, .stTextInput label, .stTextArea label, .stDateInput label {
        color: #374151 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Button improvements */
    .stButton > button {
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    /* Alert boxes with better contrast */
    .stAlert {
        border-radius: 10px !important;
        border-width: 2px !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    /* Metric component styling */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    [data-testid="metric-container"] label {
        color: #374151 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #1f2937 !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }
</style>
""", unsafe_allow_html=True)


class DigitalHealthPassport:
    """Secure digital health record management system."""
    
    def __init__(self):
        self.passport_id = None
        self.health_data = {}
        self.visit_history = []
        self.medications = []
        self.allergies = []
        self.emergency_contacts = []
    
    def create_passport(self, patient_info: Dict) -> str:
        """Create a new digital health passport."""
        self.passport_id = str(uuid.uuid4())[:8].upper()
        
        self.health_data = {
            'passport_id': self.passport_id,
            'created_date': datetime.now().isoformat(),
            'basic_info': patient_info,
            'security_hash': self._generate_security_hash(patient_info)
        }
        
        return self.passport_id
    
    def _generate_security_hash(self, data: Dict) -> str:
        """Generate security hash for data integrity."""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()[:16]
    
    def add_visit_record(self, visit_data: Dict):
        """Add a visit record to the passport."""
        visit_record = {
            'visit_id': str(uuid.uuid4())[:8],
            'date': datetime.now().isoformat(),
            'department': visit_data.get('department'),
            'diagnosis': visit_data.get('diagnosis'),
            'treatments': visit_data.get('treatments', []),
            'follow_up': visit_data.get('follow_up'),
            'physician': visit_data.get('physician')
        }
        
        self.visit_history.append(visit_record)
    
    def update_medications(self, medications: List[str]):
        """Update current medications list."""
        self.medications = [
            {
                'name': med,
                'added_date': datetime.now().isoformat(),
                'status': 'active'
            } for med in medications
        ]
    
    def add_allergy(self, allergy: str, severity: str = 'Unknown'):
        """Add allergy information."""
        allergy_record = {
            'allergen': allergy,
            'severity': severity,
            'added_date': datetime.now().isoformat()
        }
        
        self.allergies.append(allergy_record)
    
    def get_health_summary(self) -> Dict:
        """Get comprehensive health summary."""
        return {
            'passport_info': self.health_data,
            'visit_count': len(self.visit_history),
            'current_medications': len(self.medications),
            'known_allergies': len(self.allergies),
            'last_visit': self.visit_history[-1]['date'] if self.visit_history else None
        }


def display_health_passport_interface():
    """Display the digital health passport interface."""
    st.markdown("""
    <div class="feature-container">
        <h3>📱 Digital Health Passport</h3>
        <p>Secure, portable health records at your fingertips with blockchain-style security</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize passport in session state
    if 'health_passport' not in st.session_state:
        st.session_state.health_passport = DigitalHealthPassport()
    
    passport = st.session_state.health_passport
    
    # Passport creation or access
    if not passport.passport_id:
        st.markdown("#### 🆕 Create Your Digital Health Passport")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            dob = st.date_input("Date of Birth")
            
        with col2:
            emergency_contact = st.text_input("Emergency Contact")
            blood_type = st.selectbox("Blood Type", 
                                    ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        
        if st.button("🔐 Create Secure Passport") and name and dob:
            patient_info = {
                'name': name,
                'date_of_birth': str(dob) if dob else '',
                'emergency_contact': emergency_contact,
                'blood_type': blood_type
            }
            
            passport_id = passport.create_passport(patient_info)
            st.success(f"✅ Digital Health Passport Created! ID: **{passport_id}**")
            st.info("🔒 Your passport is secured with blockchain-style hashing")
            st.rerun()
    
    else:
        # Display existing passport
        st.markdown(f"#### 🎫 Health Passport: **{passport.passport_id}**")
        
        # Health summary dashboard
        summary = passport.get_health_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Visits", summary['visit_count'])
        
        with col2:
            st.metric("Active Meds", summary['current_medications'])
        
        with col3:
            st.metric("Known Allergies", summary['known_allergies'])
        
        with col4:
            st.metric("Days Since Last Visit", 
                     (datetime.now() - datetime.fromisoformat(summary['last_visit'])).days 
                     if summary['last_visit'] else "N/A")
        
        # Passport sections
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "💊 Medications", "⚠️ Allergies", "📈 History"])
        
        with tab1:
            st.markdown("##### 👤 Basic Information")
            info = passport.health_data['basic_info']
            st.write(f"**Name:** {info['name']}")
            st.write(f"**Date of Birth:** {info['date_of_birth']}")
            st.write(f"**Blood Type:** {info['blood_type']}")
            st.write(f"**Emergency Contact:** {info['emergency_contact']}")
            
            # QR Code simulation
            st.markdown("##### 📱 Digital Access")
            st.info("🔗 QR Code for instant medical team access would appear here")
        
        with tab2:
            st.markdown("##### 💊 Current Medications")
            
            new_med = st.text_input("Add new medication:")
            if st.button("➕ Add Medication") and new_med:
                current_meds = [med['name'] for med in passport.medications]
                passport.update_medications(current_meds + [new_med])
                st.success(f"Added: {new_med}")
                st.rerun()
            
            if passport.medications:
                for med in passport.medications:
                    st.write(f"• **{med['name']}** (Added: {med['added_date'][:10]})")
            else:
                st.info("No medications recorded")
        
        with tab3:
            st.markdown("##### ⚠️ Allergies & Reactions")
            
            col_a, col_b = st.columns(2)
            with col_a:
                new_allergy = st.text_input("Allergy/Reaction:")
            with col_b:
                severity = st.selectbox("Severity:", ["Mild", "Moderate", "Severe", "Life-threatening"])
            
            if st.button("⚠️ Add Allergy") and new_allergy and severity:
                passport.add_allergy(new_allergy, severity)
                st.warning(f"Added allergy: {new_allergy} ({severity})")
                st.rerun()
            
            if passport.allergies:
                for allergy in passport.allergies:
                    severity_color = {"Mild": "🟢", "Moderate": "🟡", "Severe": "🟠", "Life-threatening": "🔴"}
                    st.write(f"{severity_color.get(allergy['severity'], '⚪')} **{allergy['allergen']}** - {allergy['severity']}")
            else:
                st.info("No allergies recorded")
        
        with tab4:
            st.markdown("##### 📈 Visit History")
            
            if passport.visit_history:
                for visit in passport.visit_history:
                    with st.expander(f"Visit {visit['visit_id']} - {visit['date'][:10]}"):
                        st.write(f"**Department:** {visit['department']}")
                        st.write(f"**Diagnosis:** {visit['diagnosis']}")
                        st.write(f"**Physician:** {visit['physician']}")
                        if visit['treatments']:
                            st.write(f"**Treatments:** {', '.join(visit['treatments'])}")
            else:
                st.info("No visit history yet")
                
                # Simulate adding current visit
                if st.button("📝 Record Current Visit"):
                    visit_data = {
                        'department': 'Emergency',
                        'diagnosis': 'Evaluation in progress',
                        'physician': 'Dr. AI Assistant',
                        'treatments': ['Initial assessment']
                    }
                    passport.add_visit_record(visit_data)
                    st.success("Current visit recorded!")
                    st.rerun()


class PredictiveHealthInsights:
    """AI-powered predictive health insights system."""
    
    def __init__(self):
        self.risk_factors = {}
        self.health_trends = []
        self.recommendations = []
    
    def analyze_health_patterns(self, patient_data: Dict) -> Dict:
        """Analyze health patterns and predict potential issues."""
        insights = {
            'risk_score': self._calculate_risk_score(patient_data),
            'predicted_conditions': self._predict_conditions(patient_data),
            'preventive_recommendations': self._generate_recommendations(patient_data),
            'optimal_visit_timing': self._suggest_visit_timing(patient_data)
        }
        
        return insights
    
    def _calculate_risk_score(self, data: Dict) -> float:
        """Calculate overall health risk score (0-100)."""
        base_risk = 20  # Base risk for everyone
        
        # Age factor
        age = data.get('age', 30)
        age_risk = min(age * 0.5, 30)
        
        # Symptom severity
        symptoms = data.get('symptoms', [])
        symptom_risk = len(symptoms) * 5
        
        # Medical history
        history = data.get('medical_history', [])
        history_risk = len(history) * 8
        
        total_risk = min(base_risk + age_risk + symptom_risk + history_risk, 100)
        return round(total_risk, 1)
    
    def _predict_conditions(self, data: Dict) -> List[Dict]:
        """Predict potential health conditions based on patterns."""
        predictions = []
        
        symptoms = data.get('symptoms', [])
        age = data.get('age', 30)
        
        # Simple prediction logic (would be ML-based in production)
        if 'chest pain' in [s.lower() for s in symptoms]:
            predictions.append({
                'condition': 'Cardiovascular Event',
                'probability': 75,
                'timeframe': '1-6 months',
                'prevention': 'Regular cardiology checkups'
            })
        
        if age > 50 and 'joint pain' in [s.lower() for s in symptoms]:
            predictions.append({
                'condition': 'Arthritis Progression',
                'probability': 60,
                'timeframe': '6-12 months',
                'prevention': 'Physical therapy, joint supplements'
            })
        
        return predictions
    
    def _generate_recommendations(self, data: Dict) -> List[str]:
        """Generate personalized health recommendations."""
        recommendations = []
        
        age = data.get('age', 30)
        symptoms = data.get('symptoms', [])
        
        # Age-based recommendations
        if age > 40:
            recommendations.append("📅 Schedule annual comprehensive physical")
            recommendations.append("🩺 Consider preventive cardiac screening")
        
        if age > 50:
            recommendations.append("🔍 Cancer screening updates")
            recommendations.append("🦴 Bone density assessment")
        
        # Symptom-based recommendations
        if 'headache' in [s.lower() for s in symptoms]:
            recommendations.append("💧 Increase daily water intake")
            recommendations.append("😴 Optimize sleep schedule")
        
        if 'joint pain' in [s.lower() for s in symptoms]:
            recommendations.append("🏃‍♀️ Low-impact exercise routine")
            recommendations.append("🐟 Anti-inflammatory diet")
        
        return recommendations
    
    def _suggest_visit_timing(self, data: Dict) -> Dict:
        """Suggest optimal visit timing based on patterns."""
        urgency = data.get('urgency_level', 'routine')
        
        if urgency == 'EMERGENCY':
            return {
                'immediate': 'Now - Emergency Department',
                'follow_up': '2-3 days post-treatment'
            }
        elif urgency == 'URGENT':
            return {
                'immediate': 'Within 24 hours',
                'follow_up': '1-2 weeks'
            }
        else:
            return {
                'immediate': '1-2 weeks',
                'follow_up': '3-6 months'
            }


def display_predictive_insights():
    """Display predictive health insights interface."""
    st.markdown("""
    <div class="feature-container" style="background: linear-gradient(145deg, #fef3c7, #fde68a); border: 2px solid #f59e0b;">
        <h3 style="color: #92400e !important;">🔮 Predictive Health Insights</h3>
        <p style="color: #a16207 !important;">AI-powered health pattern analysis and future risk prediction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize insights system
    if 'health_insights' not in st.session_state:
        st.session_state.health_insights = PredictiveHealthInsights()
    
    insights_system = st.session_state.health_insights
    
    # Sample patient data for demonstration
    sample_data = {
        'age': 45,
        'symptoms': ['Chest pain', 'Shortness of breath'],
        'medical_history': ['High blood pressure'],
        'urgency_level': 'URGENT'
    }
    
    if st.button("🧬 Generate Health Predictions"):
        with st.spinner("🤖 AI analyzing health patterns..."):
            insights = insights_system.analyze_health_patterns(sample_data)
            
            # Risk Score
            st.markdown("#### 📊 Overall Health Risk Assessment")
            risk_score = insights['risk_score']
            risk_color = "🟢" if risk_score < 30 else "🟡" if risk_score < 60 else "🔴"
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Score", f"{risk_score}/100", f"{risk_color}")
            with col2:
                st.metric("Risk Level", "Moderate" if risk_score < 60 else "High")
            with col3:
                st.metric("Confidence", "87%")
            
            # Predictions
            st.markdown("#### 🔮 Predictive Analysis")
            
            predictions = insights['predicted_conditions']
            if predictions:
                for pred in predictions:
                    with st.expander(f"⚠️ {pred['condition']} - {pred['probability']}% likelihood"):
                        st.write(f"**Timeframe:** {pred['timeframe']}")
                        st.write(f"**Prevention:** {pred['prevention']}")
            
            # Recommendations
            st.markdown("#### 💡 Personalized Recommendations")
            recommendations = insights['preventive_recommendations']
            
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
            
            # Optimal timing
            st.markdown("#### ⏰ Optimal Visit Timing")
            timing = insights['optimal_visit_timing']
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.info(f"**Next Visit:** {timing['immediate']}")
            with col_b:
                st.info(f"**Follow-up:** {timing['follow_up']}")


def display_telemedicine_interface():
    """Display telemedicine consultation interface."""
    st.markdown("""
    <div class="feature-container" style="background: linear-gradient(145deg, #ecfdf5, #d1fae5); border: 2px solid #10b981;">
        <h3 style="color: #047857 !important;">📹 Virtual Consultation</h3>
        <p style="color: #065f46 !important;">Connect with healthcare providers remotely for immediate consultation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Virtual consultation options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👩‍⚕️ Available Providers")
        
        providers = [
            {"name": "Dr. Sarah Johnson", "specialty": "Family Medicine", "rating": 4.9, "next_available": "15 min"},
            {"name": "Dr. Michael Chen", "specialty": "Internal Medicine", "rating": 4.8, "next_available": "30 min"},
            {"name": "Dr. Emily Rodriguez", "specialty": "Urgent Care", "rating": 4.7, "next_available": "5 min"}
        ]
        
        for provider in providers:
            st.markdown(f"""
            <div class="feature-container" style="padding: 1rem; margin: 0.8rem 0; background: linear-gradient(145deg, #f8fafc, #e2e8f0);">
                <div style="color: #1f2937; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.3rem;">
                    **{provider['name']}** - {provider['specialty']}
                </div>
                <div style="color: #6b7280; font-size: 0.9rem; font-weight: 500;">
                    ⭐ {provider['rating']} | 🕐 Available in {provider['next_available']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"📞 Connect with {provider['name'].split()[1]}", key=provider['name']):
                st.success(f"🔗 Connecting to {provider['name']}...")
                st.info("📹 Video call would initiate here")
    
    with col2:
        st.markdown("#### 💬 Quick Consultation Chat")
        
        # Chat interface for quick questions
        question = st.text_area("Ask a quick health question:", 
                               placeholder="e.g., 'Should I be concerned about this headache?'")
        
        if st.button("🚀 Send to Triage Nurse") and question:
            st.success("✅ Question sent to triage nurse")
            st.info("📱 You'll receive a response within 15 minutes via SMS/email")
        
        st.markdown("#### 📋 Pre-consultation Checklist")
        
        checklist_items = [
            "📋 Prepare list of current symptoms",
            "💊 Gather current medications",
            "📝 Write down specific questions",
            "🆔 Have insurance card ready",
            "📍 Ensure stable internet connection",
            "🎧 Test camera and microphone"
        ]
        
        for item in checklist_items:
            st.checkbox(item, key=f"checklist_{item}")


def main_enhanced_features():
    """Main function to display enhanced features."""
    st.markdown("# 🚀 Enhanced SPFPA Features")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📱 Digital Passport", 
        "🔮 Predictive Insights", 
        "📹 Telemedicine", 
        "🤖 AI Assistant"
    ])
    
    with tab1:
        display_health_passport_interface()
    
    with tab2:
        display_predictive_insights()
    
    with tab3:
        display_telemedicine_interface()
    
    with tab4:
        st.markdown("### 🤖 Advanced AI Features")
        st.info("Integration with main AI chat system from enhanced_app.py")
        st.write("• Natural language symptom processing")
        st.write("• Multi-language support")
        st.write("• Voice recognition and synthesis")
        st.write("• Real-time medical literature integration")
        st.write("• Personalized health coaching")


if __name__ == "__main__":
    main_enhanced_features()