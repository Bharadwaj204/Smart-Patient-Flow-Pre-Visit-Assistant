"""
Enhanced Smart Patient Flow & Pre-Visit Assistant (SPFPA)
Next-generation healthcare interface with innovative features.
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import json
import pandas as pd

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rag_pipeline import setup_rag_pipeline
from src.patient_intake import PatientIntakeSystem, PatientInfo, VisitPlan

# Page configuration with enhanced settings
st.set_page_config(
    page_title="SuperHealth AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "SuperHealth AI Assistant - Your intelligent healthcare companion"
    }
)

# Enhanced CSS with improved visibility and contrast
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global text styling for better readability */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        padding: 2rem;
        border-radius: 15px;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        animation: slideInDown 0.8s ease-out;
    }
    
    .main-header h1 {
        color: #ffffff !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: #e0e7ff !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
        margin: 0 !important;
    }
    
    .ai-chat-container {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid #e2e8f0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .ai-chat-container h3 {
        color: #1e293b !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .ai-chat-container p {
        color: #475569 !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    .symptom-checker {
        background: linear-gradient(145deg, #f0f9ff, #dbeafe);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #2563eb;
        border: 2px solid #bfdbfe;
    }
    
    .symptom-checker h3 {
        color: #1e40af !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .symptom-checker p {
        color: #1e40af !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    .live-metrics {
        background: linear-gradient(145deg, #f0fdf4, #dcfce7);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 2px solid #bbf7d0;
    }
    
    .progress-tracker {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 2px solid #e2e8f0;
    }
    
    .progress-tracker h4 {
        color: #1e293b !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    .progress-tracker p {
        color: #475569 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        margin-top: 0.5rem !important;
    }
    
    .emergency-alert {
        background: linear-gradient(145deg, #fef2f2, #fee2e2);
        border: 3px solid #dc2626;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    .emergency-alert h3 {
        color: #dc2626 !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .emergency-alert p {
        color: #991b1b !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    
    .smart-recommendation {
        background: linear-gradient(145deg, #f0fdfa, #ccfbf1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #059669;
        border: 2px solid #6ee7b7;
    }
    
    .smart-recommendation h4 {
        color: #059669 !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    
    .voice-input-btn {
        background: linear-gradient(145deg, #3b82f6, #2563eb);
        border: none;
        border-radius: 50px;
        padding: 0.8rem 1.5rem;
        color: #ffffff;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    .voice-input-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
    }
    
    @keyframes slideInDown {
        from { transform: translateY(-50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(220, 38, 38, 0); }
        100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 2px solid #e2e8f0;
        min-height: 120px;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-card h3 {
        color: #374151 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .metric-card h2 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    
    .chat-message {
        background: linear-gradient(145deg, #f8fafc, #f1f5f9);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #3b82f6;
        border: 1px solid #e2e8f0;
    }
    
    .chat-message strong {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    .chat-message small {
        color: #64748b !important;
        font-size: 0.85rem !important;
    }
    
    .user-message {
        background: linear-gradient(145deg, #ecfdf5, #d1fae5);
        border-left: 4px solid #059669;
        margin-left: 2rem;
        border: 1px solid #a7f3d0;
    }
    
    .user-message strong {
        color: #065f46 !important;
    }
    
    /* Fix Streamlit component text visibility */
    .stSelectbox label {
        color: #374151 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    .stTextInput label {
        color: #374151 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    .stTextArea label {
        color: #374151 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    .stMultiSelect label {
        color: #374151 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    /* Improve button visibility */
    .stButton > button {
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.6rem 1.2rem !important;
    }
    
    /* Better text contrast in info/warning/error boxes */
    .stAlert {
        border-radius: 12px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
    }
    
    /* Improve sidebar text visibility */
    .css-1d391kg {
        background-color: #f8fafc !important;
    }
    
    .sidebar .sidebar-content {
        color: #374151 !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize enhanced session state with new features."""
    if 'rag_pipeline' not in st.session_state:
        with st.spinner("🤖 Initializing AI Healthcare Assistant..."):
            try:
                st.session_state.rag_pipeline = setup_rag_pipeline()
                st.session_state.intake_system = PatientIntakeSystem(st.session_state.rag_pipeline)
                st.session_state.initialized = True
            except Exception as e:
                st.session_state.initialized = False
                st.session_state.init_error = str(e)
    
    # Enhanced session state variables
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_symptoms' not in st.session_state:
        st.session_state.current_symptoms = []
    
    if 'ai_insights' not in st.session_state:
        st.session_state.ai_insights = []
    
    if 'live_metrics' not in st.session_state:
        st.session_state.live_metrics = {
            'current_wait_time': '12 min',
            'er_capacity': 78,
            'urgent_care_wait': '5 min',
            'appointments_today': 247
        }
    
    if 'patient_session' not in st.session_state:
        st.session_state.patient_session = None
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'welcome'
    
    if 'visit_plan' not in st.session_state:
        st.session_state.visit_plan = None


def display_enhanced_header():
    """Display enhanced header with live metrics."""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 SuperHealth AI Assistant</h1>
        <p>Intelligent Healthcare • Real-time Insights • Personalized Care</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Live metrics dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ Current Wait</h3>
            <h2 style="color: #38b2ac;">{st.session_state.live_metrics['current_wait_time']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏥 ER Capacity</h3>
            <h2 style="color: #e53e3e;">{st.session_state.live_metrics['er_capacity']}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🚑 Urgent Care</h3>
            <h2 style="color: #38a169;">{st.session_state.live_metrics['urgent_care_wait']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📅 Today's Visits</h3>
            <h2 style="color: #4299e1;">{st.session_state.live_metrics['appointments_today']}</h2>
        </div>
        """, unsafe_allow_html=True)


def ai_chat_interface():
    """Interactive AI chat interface for symptom discussion."""
    st.markdown("""
    <div class="ai-chat-container">
        <h3>💬 Chat with Healthcare AI</h3>
        <p>Describe your symptoms naturally - I'll help guide you to the right care.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Type your question or describe your symptoms:", 
                              placeholder="e.g., I've been having chest pain for 2 hours...")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🎤 Voice Input", help="Click to use voice input (simulated)"):
            st.info("🎤 Voice input would be activated here (feature simulation)")
    
    with col2:
        if st.button("Send Message", type="primary") and user_input:
            # Add user message to chat
            st.session_state.chat_history.append({
                'role': 'user',
                'message': user_input,
                'timestamp': datetime.now()
            })
            
            # Generate AI response
            with st.spinner("🤖 AI is analyzing your symptoms..."):
                try:
                    response = st.session_state.rag_pipeline.process_query(user_input)
                    
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'message': response.answer,
                        'confidence': response.confidence,
                        'sources': response.sources,
                        'timestamp': datetime.now()
                    })
                    
                    # Extract insights
                    if response.triage_info:
                        st.session_state.ai_insights.append({
                            'type': 'triage',
                            'urgency': response.triage_info.get('urgency_level'),
                            'department': response.triage_info.get('department'),
                            'timestamp': datetime.now()
                        })
                    
                except Exception as e:
                    st.error(f"AI processing error: {str(e)}")
            
            st.rerun()
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💭 Conversation History")
        for msg in st.session_state.chat_history[-6:]:  # Show last 6 messages
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {msg['message']}<br>
                    <small>{msg['timestamp'].strftime('%I:%M %p')}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                confidence_bar = "🟢" if msg.get('confidence', 0) > 0.7 else "🟡" if msg.get('confidence', 0) > 0.4 else "🔴"
                st.markdown(f"""
                <div class="chat-message">
                    <strong>AI Assistant {confidence_bar}:</strong> {msg['message']}<br>
                    <small>Confidence: {msg.get('confidence', 0):.0%} • {msg['timestamp'].strftime('%I:%M %p')}</small>
                </div>
                """, unsafe_allow_html=True)


def smart_symptom_checker():
    """Enhanced symptom checker with AI suggestions."""
    st.markdown("""
    <div class="symptom-checker">
        <h3>🎯 Smart Symptom Checker</h3>
        <p>Select symptoms and get instant AI-powered recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Symptom categories
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🫀 Cardiovascular")
        cardio_symptoms = st.multiselect(
            "Heart/Circulation:",
            ["Chest pain", "Shortness of breath", "Rapid heartbeat", "Dizziness", "Leg swelling"],
            key="cardio"
        )
    
    with col2:
        st.subheader("🧠 Neurological")
        neuro_symptoms = st.multiselect(
            "Brain/Nervous system:",
            ["Headache", "Confusion", "Weakness", "Numbness", "Vision changes"],
            key="neuro"
        )
    
    with col3:
        st.subheader("🦴 Musculoskeletal")
        musculo_symptoms = st.multiselect(
            "Muscles/Bones:",
            ["Joint pain", "Back pain", "Muscle weakness", "Stiffness", "Swelling"],
            key="musculo"
        )
    
    all_symptoms = cardio_symptoms + neuro_symptoms + musculo_symptoms
    
    if all_symptoms:
        st.session_state.current_symptoms = all_symptoms
        
        # AI-powered risk assessment
        high_risk = any(symptom in ["Chest pain", "Shortness of breath", "Confusion"] for symptom in all_symptoms)
        
        if high_risk:
            st.markdown("""
            <div class="emergency-alert">
                <h3>🚨 High Priority Symptoms Detected</h3>
                <p>Based on your symptoms, you may need urgent medical attention.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Smart recommendations
        st.markdown("""
        <div class="smart-recommendation">
            <h4>🤖 AI Recommendations</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if "Chest pain" in all_symptoms:
            st.warning("⚠️ Chest pain can be serious. Consider emergency evaluation.")
        
        if len(all_symptoms) >= 3:
            st.info("💡 Multiple symptoms detected. Comprehensive evaluation recommended.")
        
        # Department suggestion
        dept_suggestions = {
            "Chest pain": "Emergency/Cardiology",
            "Headache": "Neurology/Primary Care",
            "Joint pain": "Orthopedics/Rheumatology"
        }
        
        suggested_dept = None
        for symptom in all_symptoms:
            if symptom in dept_suggestions:
                suggested_dept = dept_suggestions[symptom]
                break
        
        if suggested_dept:
            st.success(f"🎯 Suggested Department: **{suggested_dept}**")


def display_enhanced_welcome():
    """Enhanced welcome screen with AI features."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🌟 Welcome to Your AI Healthcare Companion")
        st.write("""
        Experience the future of healthcare with our AI-powered assistant:
        
        🤖 **AI Chat Support** - Natural conversation about your health
        📊 **Real-time Metrics** - Live hospital capacity and wait times
        🎯 **Smart Symptom Checker** - Intelligent symptom analysis
        📱 **Digital Health Passport** - Secure health record management
        🔮 **Predictive Insights** - Personalized health recommendations
        ⚡ **Instant Triage** - Immediate priority assessment
        """)
        
        # Quick action buttons
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🚀 Start AI Assessment", type="primary", use_container_width=True):
                st.session_state.current_step = 'ai_mode'
                st.rerun()
        
        with col_b:
            if st.button("📋 Traditional Intake", use_container_width=True):
                st.session_state.patient_session = st.session_state.intake_system.start_new_intake()
                st.session_state.current_step = 'basic_info'
                st.rerun()
        
        # Live features
        st.markdown("### ⚡ Live Features")
        ai_chat_interface()
        
    with col2:
        st.markdown("### 📊 Live Hospital Status")
        
        # Simulated live data
        wait_times = {
            "Emergency": 15,
            "Urgent Care": 5,
            "Primary Care": 25,
            "Specialists": 45
        }
        
        for dept, wait in wait_times.items():
            color = "🟢" if wait < 10 else "🟡" if wait < 30 else "🔴"
            st.metric(dept, f"{wait} min", delta=f"{wait-20} min")
        
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("🚨 Emergency Guidance", use_container_width=True):
            st.error("**🚨 For life-threatening emergencies, call 911 immediately!**")
            st.write("""
            **Emergency Signs:**
            - Severe chest pain
            - Difficulty breathing
            - Loss of consciousness
            - Severe bleeding
            - Stroke symptoms
            """)
        
        if st.button("🔍 Find Specialist", use_container_width=True):
            st.info("**Available Specialists:**\n- Cardiology\n- Neurology\n- Orthopedics\n- Gastroenterology")
        
        # Smart symptom checker
        smart_symptom_checker()


def ai_enhanced_mode():
    """AI-enhanced assessment mode."""
    st.markdown("### 🤖 AI-Powered Health Assessment")
    
    # Progress tracker
    st.markdown("""
    <div class="progress-tracker">
        <h4>📈 Assessment Progress</h4>
        <div style="background: #e2e8f0; border-radius: 10px; padding: 3px;">
            <div style="background: linear-gradient(90deg, #4299e1, #3182ce); width: 60%; height: 20px; border-radius: 8px;"></div>
        </div>
        <p>60% Complete • AI Confidence: 85%</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Interview
    st.markdown("#### 🎙️ AI Health Interview")
    
    questions = [
        "What's the main reason for your visit today?",
        "When did your symptoms first start?",
        "How would you rate your pain on a scale of 1-10?",
        "Any recent changes in your medications?",
        "Any family history of similar conditions?"
    ]
    
    current_q = st.session_state.get('current_question', 0)
    
    if current_q < len(questions):
        st.write(f"**AI:** {questions[current_q]}")
        
        response = st.text_area("Your response:", key=f"q_{current_q}")
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("Next →") and response:
                st.session_state[f'answer_{current_q}'] = response
                st.session_state.current_question = current_q + 1
                st.rerun()
        
        with col2:
            if current_q > 0 and st.button("← Previous"):
                st.session_state.current_question = current_q - 1
                st.rerun()
    else:
        st.success("🎉 AI Assessment Complete!")
        
        # Generate AI insights
        st.markdown("### 🧠 AI Analysis Results")
        
        # Simulated AI insights
        insights = [
            {"type": "Priority", "value": "Moderate", "confidence": 85},
            {"type": "Department", "value": "Internal Medicine", "confidence": 92},
            {"type": "Urgency", "value": "Schedule within 2 days", "confidence": 78},
            {"type": "Risk Level", "value": "Low-Medium", "confidence": 88}
        ]
        
        for insight in insights:
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{insight['type']}:** {insight['value']}")
            with col2:
                st.progress(insight['confidence'] / 100)
            with col3:
                st.write(f"{insight['confidence']}%")
        
        if st.button("📋 Generate Full Report", type="primary"):
            st.session_state.current_step = 'ai_results'
            st.rerun()
    
    # Real-time AI chat
    st.markdown("---")
    ai_chat_interface()


def main():
    """Enhanced main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Display enhanced header
    display_enhanced_header()
    
    # Check if system is initialized
    if not st.session_state.get('initialized', False):
        if 'init_error' in st.session_state:
            st.error(f"Failed to initialize AI system: {st.session_state.init_error}")
            st.info("Please check your setup and try refreshing the page.")
        return
    
    # Enhanced sidebar
    with st.sidebar:
        st.markdown("### 🤖 AI Assistant Panel")
        
        # AI Insights
        if st.session_state.ai_insights:
            st.markdown("#### 🧠 Recent Insights")
            for insight in st.session_state.ai_insights[-3:]:
                st.info(f"**{insight['type']}:** {insight.get('urgency', 'N/A')}")
        
        # Quick stats
        st.markdown("#### 📊 Your Session")
        st.metric("Messages Exchanged", len(st.session_state.chat_history))
        st.metric("Symptoms Tracked", len(st.session_state.current_symptoms))
        
        st.markdown("---")
        st.markdown("### 🏥 Hospital Info")
        st.write("📞 Emergency: 911")
        st.write("📞 Main: (555) 123-HEALTH")
        st.write("🌐 superhealth.com")
        
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['rag_pipeline', 'intake_system', 'initialized']:
                    del st.session_state[key]
            st.session_state.current_step = 'welcome'
            st.rerun()
    
    # Main content routing
    current_step = st.session_state.get('current_step', 'welcome')
    
    if current_step == 'welcome':
        display_enhanced_welcome()
    elif current_step == 'ai_mode':
        ai_enhanced_mode()
    elif current_step == 'ai_results':
        st.markdown("### 🎯 AI Assessment Results")
        st.success("AI has generated your personalized health report!")
        
        # Would contain comprehensive AI-generated results
        st.info("This would display the full AI analysis, recommendations, and next steps.")
        
        if st.button("🏠 Start New Session", type="primary"):
            st.session_state.current_step = 'welcome'
            st.rerun()
    else:
        # Fallback to traditional flow
        st.info("Enhanced AI features coming soon! Using traditional mode.")
        st.session_state.current_step = 'welcome'
        st.rerun()


if __name__ == "__main__":
    main()