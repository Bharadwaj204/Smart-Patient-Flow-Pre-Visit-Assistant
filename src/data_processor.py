"""
Data processor for loading and preparing healthcare data for vector embeddings.
"""

import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Document:
    """Represents a document for vector storage."""
    content: str
    metadata: Dict[str, Any]
    source: str


class HealthcareDataProcessor:
    """Processes healthcare data files into documents for vector embeddings."""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        
    def load_json_file(self, filename: str) -> List[Dict]:
        """Load JSON data file."""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename}: {e}")
            return []
    
    def load_json_dict(self, filename: str) -> Dict:
        """Load JSON data file as dictionary."""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename}: {e}")
            return {}
    
    def process_faqs(self) -> List[Document]:
        """Process FAQ data into documents."""
        faqs = self.load_json_file('hospital_faqs.json')
        documents = []
        
        for faq in faqs:
            content = f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}"
            metadata = {
                'type': 'faq',
                'category': faq.get('category', 'general'),
                'keywords': ', '.join(faq.get('keywords', []))  # Convert list to string
            }
            documents.append(Document(
                content=content,
                metadata=metadata,
                source='hospital_faqs'
            ))
        
        return documents
    
    def process_departments(self) -> List[Document]:
        """Process department data into documents."""
        departments = self.load_json_file('department_policies.json')
        documents = []
        
        for dept in departments:
            content = f"""Department: {dept.get('department', '')}
Description: {dept.get('description', '')}
Typical Conditions: {', '.join(dept.get('typical_conditions', []))}
Wait Time: {dept.get('wait_time_estimate', '')}
Required Documents: {', '.join(dept.get('required_documents', []))}
Preparation: {dept.get('preparation', '')}
Insurance Notes: {dept.get('insurance_notes', '')}
Contact: {dept.get('contact', '')}"""
            
            metadata = {
                'type': 'department',
                'department_name': dept.get('department', ''),
                'conditions': ', '.join(dept.get('typical_conditions', [])),  # Convert list to string
                'wait_time': dept.get('wait_time_estimate', ''),
                'contact_type': dept.get('contact', '')
            }
            
            documents.append(Document(
                content=content,
                metadata=metadata,
                source='department_policies'
            ))
        
        return documents
    
    def process_triage_mapping(self) -> List[Document]:
        """Process triage mapping data into documents."""
        triage_data = self.load_json_file('triage_mapping.json')
        documents = []
        
        for triage in triage_data:
            symptoms_str = ', '.join(triage.get('symptoms', []))
            warning_signs_str = ', '.join(triage.get('warning_signs', []))
            
            content = f"""Symptoms: {symptoms_str}
Urgency Level: {triage.get('urgency_level', '')}
Recommended Department: {triage.get('recommended_department', '')}
Triage Priority: {triage.get('triage_priority', '')}
Estimated Wait: {triage.get('estimated_wait', '')}
Next Steps: {triage.get('next_steps', '')}
Warning Signs: {warning_signs_str}"""
            
            metadata = {
                'type': 'triage',
                'urgency_level': triage.get('urgency_level', ''),
                'department': triage.get('recommended_department', ''),
                'priority': triage.get('triage_priority', 0),
                'symptoms': ', '.join(triage.get('symptoms', [])),  # Convert list to string
                'warning_signs': ', '.join(triage.get('warning_signs', []))  # Convert list to string
            }
            
            documents.append(Document(
                content=content,
                metadata=metadata,
                source='triage_mapping'
            ))
        
        return documents
    
    def process_insurance_rules(self) -> List[Document]:
        """Process insurance rules data into documents."""
        insurance_data = self.load_json_file('insurance_rules.json')
        documents = []
        
        for insurance in insurance_data:
            content = f"""Insurance Provider: {insurance.get('insurance_provider', '')}
Accepted: {insurance.get('accepted', False)}
Emergency Copay: {insurance.get('copay_emergency', '')}
Urgent Care Copay: {insurance.get('copay_urgent_care', '')}
Specialist Copay: {insurance.get('copay_specialist', '')}
Primary Care Copay: {insurance.get('copay_primary_care', '')}
Deductible Info: {insurance.get('deductible_info', '')}
Prior Authorization Required: {', '.join(insurance.get('prior_auth_required', []))}
Coverage Notes: {insurance.get('coverage_notes', '')}
Verification Phone: {insurance.get('verification_phone', '')}"""
            
            metadata = {
                'type': 'insurance',
                'provider': insurance.get('insurance_provider', ''),
                'accepted': insurance.get('accepted', False),
                'emergency_copay': insurance.get('copay_emergency', ''),
                'urgent_care_copay': insurance.get('copay_urgent_care', ''),
                'specialist_copay': insurance.get('copay_specialist', ''),
                'primary_care_copay': insurance.get('copay_primary_care', '')
            }
            
            documents.append(Document(
                content=content,
                metadata=metadata,
                source='insurance_rules'
            ))
        
        return documents
    
    def process_hospital_info(self) -> List[Document]:
        """Process hospital information into documents."""
        hospital_data = self.load_json_dict('hospital_info.json')
        documents = []
        
        if not hospital_data:
            return documents
        
        # Process hospital basic info
        hospital_info = hospital_data.get('hospital_info', {})
        content = f"""Hospital: {hospital_info.get('name', '')}
Mission: {hospital_info.get('mission', '')}
Address: {hospital_info.get('address', '')}
Phone: {hospital_info.get('phone', '')}
Emergency Phone: {hospital_info.get('emergency_phone', '')}
Website: {hospital_info.get('website', '')}"""
        
        documents.append(Document(
            content=content,
            metadata={'type': 'hospital_info', 'category': 'basic_info'},
            source='hospital_info'
        ))
        
        # Process operational hours
        hours = hospital_data.get('operational_hours', {})
        hours_content = "Operational Hours:\n" + "\n".join([
            f"{service.replace('_', ' ').title()}: {time_info}" 
            for service, time_info in hours.items()
        ])
        
        documents.append(Document(
            content=hours_content,
            metadata={'type': 'hospital_info', 'category': 'hours'},
            source='hospital_info'
        ))
        
        # Process general policies
        policies = hospital_data.get('general_policies', [])
        for policy in policies:
            policy_content = f"Policy: {policy.get('title', '')}\nDescription: {policy.get('description', '')}"
            documents.append(Document(
                content=policy_content,
                metadata={'type': 'hospital_info', 'category': 'policy', 'policy_title': policy.get('title', '')},
                source='hospital_info'
            ))
        
        # Process wait time optimization info
        wait_times = hospital_data.get('wait_time_optimization', {})
        best_times = wait_times.get('best_times', {})
        busy_times = wait_times.get('busy_times', {})
        
        wait_time_content = "Best Times to Visit:\n" + "\n".join([
            f"{service.replace('_', ' ').title()}: {time}" 
            for service, time in best_times.items()
        ])
        wait_time_content += "\n\nBusy Times to Avoid:\n" + "\n".join([
            f"{service.replace('_', ' ').title()}: {time}" 
            for service, time in busy_times.items()
        ])
        
        documents.append(Document(
            content=wait_time_content,
            metadata={'type': 'hospital_info', 'category': 'wait_times'},
            source='hospital_info'
        ))
        
        return documents
    
    def process_all_data(self) -> List[Document]:
        """Process all healthcare data files into documents."""
        all_documents = []
        
        print("Processing FAQs...")
        all_documents.extend(self.process_faqs())
        
        print("Processing department policies...")
        all_documents.extend(self.process_departments())
        
        print("Processing triage mapping...")
        all_documents.extend(self.process_triage_mapping())
        
        print("Processing insurance rules...")
        all_documents.extend(self.process_insurance_rules())
        
        print("Processing hospital information...")
        all_documents.extend(self.process_hospital_info())
        
        print(f"Total documents processed: {len(all_documents)}")
        return all_documents


if __name__ == "__main__":
    # Test the data processor
    processor = HealthcareDataProcessor("../data")
    documents = processor.process_all_data()
    
    print("\nSample documents:")
    for i, doc in enumerate(documents[:3]):
        print(f"\nDocument {i+1}:")
        print(f"Source: {doc.source}")
        print(f"Content: {doc.content[:200]}...")
        print(f"Metadata: {doc.metadata}")