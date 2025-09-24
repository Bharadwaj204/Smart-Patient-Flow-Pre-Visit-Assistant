"""
Demo examples for Smart Patient Flow & Pre-Visit Assistant (SPFPA)
Showcases various patient scenarios and system capabilities.
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rag_pipeline import setup_rag_pipeline
from src.patient_intake import PatientIntakeSystem


class SPFPADemo:
    """Demo class for SPFPA system showcasing various scenarios."""
    
    def __init__(self):
        """Initialize the demo system."""
        print("🏥 Initializing SuperHealth Pre-Visit Assistant Demo")
        print("=" * 60)
        
        try:
            self.rag_pipeline = setup_rag_pipeline()
            self.intake_system = PatientIntakeSystem(self.rag_pipeline)
            print("✅ System initialized successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize system: {e}")
            self.rag_pipeline = None
            self.intake_system = None
    
    def demo_emergency_case(self):
        """Demo: Emergency case - 55-year-old with chest pain."""
        print("\n" + "🚨 DEMO 1: EMERGENCY CASE" + "\n" + "=" * 50)
        print("Scenario: 55-year-old male with chest tightness and Blue Cross insurance")
        
        if not self.intake_system:
            print("❌ System not available")
            return
        
        try:
            # Create patient session
            patient = self.intake_system.start_new_intake()
            
            # Collect information
            self.intake_system.collect_basic_info(age=55, gender="male")
            self.intake_system.collect_symptoms(
                chief_complaint="chest tightness on and off since this morning",
                symptoms=["chest tightness", "mild discomfort"],
                duration="since this morning",
                severity="moderate"
            )
            self.intake_system.collect_medical_history(
                medical_history=["hypertension"],
                medications=["lisinopril 10mg"],
                allergies=["penicillin"]
            )
            self.intake_system.collect_insurance_info("Blue Cross Blue Shield")
            self.intake_system.collect_preferences(
                preferred_time="as soon as possible",
                urgency_perception="very urgent"
            )
            
            # Generate visit plan
            visit_plan = self.intake_system.generate_visit_plan()
            
            # Display results
            self.display_visit_plan(visit_plan)
            
        except Exception as e:
            print(f"❌ Error in emergency demo: {e}")
    
    def demo_routine_case(self):
        """Demo: Routine case - 28-year-old with skin rash."""
        print("\n" + "🏥 DEMO 2: ROUTINE CASE" + "\n" + "=" * 50)
        print("Scenario: 28-year-old female with skin rash and Aetna insurance")
        
        if not self.intake_system:
            print("❌ System not available")
            return
        
        try:
            # Create patient session
            patient = self.intake_system.start_new_intake()
            
            # Collect information
            self.intake_system.collect_basic_info(age=28, gender="female")
            self.intake_system.collect_symptoms(
                chief_complaint="skin rash appeared yesterday on arms",
                symptoms=["rash", "mild itching"],
                duration="1 day",
                severity="mild"
            )
            self.intake_system.collect_medical_history(
                medical_history=[],
                medications=[],
                allergies=["shellfish"]
            )
            self.intake_system.collect_insurance_info("Aetna")
            self.intake_system.collect_preferences(
                preferred_time="within a week",
                urgency_perception="not urgent"
            )
            
            # Generate visit plan
            visit_plan = self.intake_system.generate_visit_plan()
            
            # Display results
            self.display_visit_plan(visit_plan)
            
        except Exception as e:
            print(f"❌ Error in routine demo: {e}")
    
    def demo_urgent_case(self):
        """Demo: Urgent case - 45-year-old with severe headache."""
        print("\n" + "⚠️  DEMO 3: URGENT CASE" + "\n" + "=" * 50)
        print("Scenario: 45-year-old with severe headache and fever")
        
        if not self.intake_system:
            print("❌ System not available")
            return
        
        try:
            # Create patient session
            patient = self.intake_system.start_new_intake()
            
            # Collect information
            self.intake_system.collect_basic_info(age=45, gender="male")
            self.intake_system.collect_symptoms(
                chief_complaint="severe headache with fever for 6 hours",
                symptoms=["severe headache", "fever", "nausea"],
                duration="6 hours",
                severity="severe"
            )
            self.intake_system.collect_medical_history(
                medical_history=["diabetes"],
                medications=["metformin"],
                allergies=[]
            )
            self.intake_system.collect_insurance_info("UnitedHealthcare")
            self.intake_system.collect_preferences(
                preferred_time="today",
                urgency_perception="somewhat urgent"
            )
            
            # Generate visit plan
            visit_plan = self.intake_system.generate_visit_plan()
            
            # Display results
            self.display_visit_plan(visit_plan)
            
        except Exception as e:
            print(f"❌ Error in urgent demo: {e}")
    
    def demo_insurance_query(self):
        """Demo: Insurance coverage query."""
        print("\n" + "💳 DEMO 4: INSURANCE QUERY" + "\n" + "=" * 50)
        print("Scenario: Patient asking about Medicare coverage")
        
        if not self.rag_pipeline:
            print("❌ System not available")
            return
        
        try:
            query = "What does Medicare cover for emergency visits and what are the copays?"
            print(f"Query: {query}")
            
            response = self.rag_pipeline.process_query(query)
            
            print(f"\n🤖 AI Response (Confidence: {response.confidence:.1%}):")
            print("-" * 40)
            print(response.answer)
            
            if response.sources:
                print(f"\n📚 Sources ({len(response.sources)} found):")
                for i, source in enumerate(response.sources[:2], 1):
                    print(f"{i}. {source['type']}: {source['content_preview'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error in insurance demo: {e}")
    
    def demo_general_faq(self):
        """Demo: General FAQ query."""
        print("\n" + "❓ DEMO 5: GENERAL FAQ" + "\n" + "=" * 50)
        print("Scenario: Patient asking about required documents")
        
        if not self.rag_pipeline:
            print("❌ System not available")
            return
        
        try:
            query = "What documents do I need to bring for my first visit?"
            print(f"Query: {query}")
            
            response = self.rag_pipeline.process_query(query)
            
            print(f"\n🤖 AI Response (Confidence: {response.confidence:.1%}):")
            print("-" * 40)
            print(response.answer)
            
            if response.next_steps:
                print(f"\n📝 Next Steps:")
                for step in response.next_steps:
                    print(f"• {step}")
            
        except Exception as e:
            print(f"❌ Error in FAQ demo: {e}")
    
    def demo_wait_times(self):
        """Demo: Wait time optimization query."""
        print("\n" + "⏰ DEMO 6: WAIT TIME QUERY" + "\n" + "=" * 50)
        print("Scenario: Patient asking about best times to visit")
        
        if not self.rag_pipeline:
            print("❌ System not available")
            return
        
        try:
            query = "What are the best times to visit for lab work to minimize wait times?"
            print(f"Query: {query}")
            
            response = self.rag_pipeline.process_query(query)
            
            print(f"\n🤖 AI Response (Confidence: {response.confidence:.1%}):")
            print("-" * 40)
            print(response.answer)
            
        except Exception as e:
            print(f"❌ Error in wait time demo: {e}")
    
    def display_visit_plan(self, visit_plan):
        """Display a formatted visit plan."""
        if not visit_plan:
            print("❌ No visit plan generated")
            return
        
        triage = visit_plan.triage_recommendation
        patient = visit_plan.patient_info
        
        # Urgency-based styling
        urgency_icons = {
            "EMERGENCY": "🚨",
            "URGENT": "⚠️",
            "ROUTINE": "ℹ️"
        }
        
        urgency_colors = {
            "EMERGENCY": "RED ALERT",
            "URGENT": "YELLOW ALERT", 
            "ROUTINE": "GREEN - ROUTINE"
        }
        
        icon = urgency_icons.get(triage.urgency_level, "ℹ️")
        color = urgency_colors.get(triage.urgency_level, "INFO")
        
        print(f"\n{icon} VISIT PLAN - {color}")
        print("=" * 50)
        
        # Patient summary
        print(f"👤 Patient: {patient.age}-year-old {patient.gender}")
        print(f"🏥 Recommended: {triage.recommended_department}")
        print(f"⏰ Check-in: {visit_plan.check_in_time}")
        print(f"⌛ Wait time: {triage.estimated_wait_time}")
        print(f"🕐 Total time: {visit_plan.estimated_total_time}")
        
        # Next steps
        print(f"\n📝 Next Steps:")
        for i, step in enumerate(triage.next_steps, 1):
            print(f"{i}. {step}")
        
        # Required documents
        print(f"\n📄 Required Documents:")
        for doc in triage.required_documents:
            print(f"• {doc}")
        
        # Insurance info
        if triage.insurance_coverage:
            print(f"\n💳 Insurance Information:")
            provider = triage.insurance_coverage.get('provider', 'Unknown')
            print(f"• Provider: {provider}")
            if 'emergency_copay' in triage.insurance_coverage:
                print(f"• Estimated Copay: {triage.insurance_coverage['emergency_copay']}")
        
        # Warning signs (for non-routine cases)
        if triage.warning_signs and triage.urgency_level != "ROUTINE":
            print(f"\n⚠️  Warning Signs - Seek immediate care if you experience:")
            for warning in triage.warning_signs[:3]:  # Show top 3
                print(f"• {warning}")
        
        print(f"\n⚖️  {triage.medical_disclaimer}")
        print("-" * 50)
    
    def run_all_demos(self):
        """Run all demo scenarios."""
        print("🎭 Running All SPFPA Demo Scenarios")
        print("=" * 60)
        
        if not self.rag_pipeline or not self.intake_system:
            print("❌ System not properly initialized. Cannot run demos.")
            return
        
        # Run all demos
        self.demo_emergency_case()
        self.demo_routine_case()
        self.demo_urgent_case()
        self.demo_insurance_query()
        self.demo_general_faq()
        self.demo_wait_times()
        
        print("\n" + "🎉 ALL DEMOS COMPLETED!" + "\n" + "=" * 60)
        print("Key Takeaways:")
        print("• Emergency cases are automatically prioritized")
        print("• Insurance coverage is verified in real-time")
        print("• Personalized recommendations based on symptoms")
        print("• Clear next steps and preparation instructions")
        print("• Medical disclaimers ensure appropriate care")
        
        print(f"\nDemo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main demo function."""
    demo = SPFPADemo()
    
    print("Select a demo to run:")
    print("1. Emergency Case (Chest Pain)")
    print("2. Routine Case (Skin Rash)")
    print("3. Urgent Case (Severe Headache)")
    print("4. Insurance Query")
    print("5. General FAQ")
    print("6. Wait Time Query")
    print("7. Run All Demos")
    print("0. Exit")
    
    try:
        choice = input("\nEnter your choice (0-7): ").strip()
        
        if choice == "1":
            demo.demo_emergency_case()
        elif choice == "2":
            demo.demo_routine_case()
        elif choice == "3":
            demo.demo_urgent_case()
        elif choice == "4":
            demo.demo_insurance_query()
        elif choice == "5":
            demo.demo_general_faq()
        elif choice == "6":
            demo.demo_wait_times()
        elif choice == "7":
            demo.run_all_demos()
        elif choice == "0":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice. Running all demos...")
            demo.run_all_demos()
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Error running demo: {e}")


if __name__ == "__main__":
    main()