"""
RAG (Retrieval-Augmented Generation) pipeline for healthcare pre-visit assistance.
Integrates with vector database and LLM for intelligent responses.
"""

import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_db import HealthcareVectorDB
from src.data_processor import Document

# Try different LLM options
try:
    from langchain_community.llms import OpenAI
    from langchain_community.chat_models import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    OPENAI_AVAILABLE = True
except ImportError:
    try:
        from langchain.llms import OpenAI
        from langchain.chat_models import ChatOpenAI
        from langchain.schema import HumanMessage, SystemMessage
        OPENAI_AVAILABLE = True
    except ImportError:
        # Type placeholders for when imports fail
        ChatOpenAI = None  # type: ignore
        OpenAI = None  # type: ignore
        HumanMessage = None  # type: ignore
        SystemMessage = None  # type: ignore
        OPENAI_AVAILABLE = False

try:
    from langchain.llms import HuggingFacePipeline
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False


@dataclass
class RAGResponse:
    """Response from the RAG pipeline."""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    triage_info: Optional[Dict[str, Any]] = None
    next_steps: Optional[List[str]] = None


class HealthcareRAGPipeline:
    """RAG pipeline for healthcare information retrieval and generation."""
    
    def __init__(
        self, 
        vector_db: HealthcareVectorDB,
        llm_type: str = "simple",
        openai_api_key: Optional[str] = None,
        temperature: float = 0.3
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            vector_db: Initialized vector database
            llm_type: Type of LLM to use ("openai", "huggingface", "simple")
            openai_api_key: OpenAI API key if using OpenAI
            temperature: LLM temperature for response generation
        """
        self.vector_db = vector_db
        self.llm_type = llm_type
        self.temperature = temperature
        
        # Initialize LLM
        self._initialize_llm(openai_api_key)
        
        # Healthcare context templates
        self.system_prompt = """You are a helpful healthcare pre-visit assistant for SuperHealth Medical Center. 
Your role is to help patients prepare for their visits by providing information about:
- Department recommendations based on symptoms
- Insurance coverage and copays
- Required documents and preparation
- Wait times and scheduling
- Hospital policies and procedures

IMPORTANT GUIDELINES:
1. Always include a medical disclaimer: "This is not medical advice. Please consult a qualified healthcare provider."
2. For emergency symptoms, always recommend immediate emergency care or calling 911
3. Be empathetic and helpful while staying within your role
4. Provide specific, actionable information when possible
5. If you don't know something, say so and suggest contacting the hospital directly

Use the provided context to answer questions accurately and helpfully."""

    def _initialize_llm(self, openai_api_key: Optional[str]):
        """Initialize the appropriate LLM based on availability and configuration."""
        if self.llm_type == "openai" and OPENAI_AVAILABLE and openai_api_key:
            try:
                if ChatOpenAI is not None:
                    self.llm = ChatOpenAI(
                        openai_api_key=openai_api_key,
                        temperature=self.temperature,
                        model_name="gpt-3.5-turbo"
                    )
                    self.use_advanced_llm = True
                    print("Using OpenAI GPT-3.5-turbo")
                else:
                    self.use_advanced_llm = False
                    print("ChatOpenAI not available, using simple LLM")
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")
                self.use_advanced_llm = False
        elif self.llm_type == "huggingface" and HUGGINGFACE_AVAILABLE:
            try:
                # Note: This would require additional setup for local models
                self.use_advanced_llm = False
                print("HuggingFace integration not fully implemented, using simple LLM")
            except Exception as e:
                print(f"Failed to initialize HuggingFace: {e}")
                self.use_advanced_llm = False
        else:
            self.use_advanced_llm = False
            print("Using simple rule-based responses")

    def retrieve_context(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from the vector database."""
        results = self.vector_db.search(query, n_results=max_results)
        
        context_docs = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                context_docs.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
        
        return context_docs

    def format_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context string."""
        if not context_docs:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for doc in context_docs:
            metadata = doc['metadata']
            content = doc['content']
            
            # Add source type for better context
            source_type = metadata.get('type', 'unknown')
            if source_type == 'triage':
                context_parts.append(f"TRIAGE INFO: {content}")
            elif source_type == 'department':
                context_parts.append(f"DEPARTMENT INFO: {content}")
            elif source_type == 'insurance':
                context_parts.append(f"INSURANCE INFO: {content}")
            elif source_type == 'faq':
                context_parts.append(f"FAQ: {content}")
            elif source_type == 'hospital_info':
                context_parts.append(f"HOSPITAL INFO: {content}")
            else:
                context_parts.append(content)
        
        return "\n\n".join(context_parts)

    def extract_triage_info(self, context_docs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract triage information from context documents."""
        for doc in context_docs:
            if doc['metadata'].get('type') == 'triage':
                metadata = doc['metadata']
                return {
                    'urgency_level': metadata.get('urgency_level'),
                    'department': metadata.get('department'),
                    'priority': metadata.get('priority'),
                    'symptoms': metadata.get('symptoms'),
                    'warning_signs': metadata.get('warning_signs')
                }
        return None

    def generate_simple_response(self, query: str, context: str) -> str:
        """Generate a simple rule-based response when advanced LLM is not available."""
        query_lower = query.lower()
        
        # Emergency keywords
        emergency_keywords = ['severe', 'emergency', 'urgent', 'chest pain', 'difficulty breathing', 'unconscious']
        if any(keyword in query_lower for keyword in emergency_keywords):
            return """🚨 IMPORTANT: Based on your symptoms, you may need immediate medical attention. 
            
If you're experiencing severe symptoms, please:
- Call 911 for emergency care
- Go to the nearest emergency room
- Don't wait for an appointment

For urgent but non-emergency symptoms, visit our Urgent Care department.

DISCLAIMER: This is not medical advice. Please consult a qualified healthcare provider for proper medical evaluation."""

        # Insurance questions
        if 'insurance' in query_lower or 'copay' in query_lower or 'coverage' in query_lower:
            return f"""Based on our records:

{context}

✅ We accept most major insurance plans
💰 Copays vary by plan and service type
📞 Please call to verify your specific plan coverage

DISCLAIMER: This is not medical advice. Please consult a qualified healthcare provider."""

        # General appointment/visit questions
        if 'appointment' in query_lower or 'visit' in query_lower or 'documents' in query_lower:
            return f"""Here's what you need to know:

{context}

📋 Required documents: Photo ID, insurance card, medication list
⏰ Arrive 15-30 minutes early for check-in
📞 Call ahead to confirm appointment and requirements

DISCLAIMER: This is not medical advice. Please consult a qualified healthcare provider."""

        # Default response with context
        return f"""Based on our hospital information:

{context}

For specific medical questions or to schedule appointments, please contact SuperHealth Medical Center directly at (555) 123-HEALTH.

DISCLAIMER: This is not medical advice. Please consult a qualified healthcare provider."""

    def generate_advanced_response(self, query: str, context: str) -> str:
        """Generate response using advanced LLM."""
        if not self.use_advanced_llm:
            return self.generate_simple_response(query, context)
        
        try:
            if SystemMessage is not None and HumanMessage is not None:
                messages = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=f"""Context from hospital knowledge base:
{context}

Patient Question: {query}

Please provide a helpful, accurate response based on the context. Include specific recommendations and next steps when appropriate.""")
                ]
                
                response = self.llm(messages)
                return response.content
            else:
                return self.generate_simple_response(query, context)
        except Exception as e:
            print(f"Error with advanced LLM: {e}")
            return self.generate_simple_response(query, context)

    def generate_next_steps(self, triage_info: Optional[Dict[str, Any]], query: str) -> List[str]:
        """Generate next steps based on triage information and query."""
        steps = []
        
        if triage_info:
            urgency = triage_info.get('urgency_level', '').upper()
            department = triage_info.get('department', '')
            
            if urgency == 'EMERGENCY':
                steps = [
                    "🚨 Seek immediate emergency care or call 911",
                    "Go to the nearest emergency room",
                    "Bring valid ID and insurance card",
                    "Don't drive yourself if experiencing severe symptoms"
                ]
            elif urgency == 'URGENT':
                steps = [
                    f"📞 Schedule same-day appointment with {department}",
                    "Consider urgent care if department unavailable",
                    "Prepare symptom timeline and current medications",
                    "Arrive 15-30 minutes early for check-in"
                ]
            elif urgency == 'ROUTINE':
                steps = [
                    f"📅 Schedule appointment with {department}",
                    "Gather medical history and current medications",
                    "Prepare list of questions for provider",
                    "Verify insurance coverage and copay"
                ]
        
        # Add general steps if none generated
        if not steps:
            steps = [
                "📞 Contact hospital for specific guidance",
                "Prepare required documents (ID, insurance card)",
                "Review hospital policies and procedures",
                "Plan arrival time based on appointment type"
            ]
        
        return steps

    def calculate_confidence(self, context_docs: List[Dict[str, Any]], query: str) -> float:
        """Calculate confidence score for the response."""
        if not context_docs:
            return 0.1
        
        # Base confidence on relevance (distance scores)
        distances = [doc['distance'] for doc in context_docs]
        avg_distance = sum(distances) / len(distances)
        
        # Lower distance = higher confidence (inverse relationship)
        base_confidence = max(0.1, 1.0 - avg_distance)
        
        # Boost confidence for exact matches
        query_lower = query.lower()
        for doc in context_docs:
            if query_lower in doc['content'].lower():
                base_confidence = min(1.0, base_confidence + 0.2)
                break
        
        return round(base_confidence, 2)

    def process_query(self, query: str) -> RAGResponse:
        """Process a user query through the complete RAG pipeline."""
        print(f"Processing query: {query}")
        
        # Retrieve relevant context
        context_docs = self.retrieve_context(query)
        
        if not context_docs:
            return RAGResponse(
                answer="I don't have specific information about that topic in our knowledge base. Please contact SuperHealth Medical Center directly at (555) 123-HEALTH for assistance.",
                sources=[],
                confidence=0.1,
                next_steps=["📞 Contact hospital directly for assistance"]
            )
        
        # Format context
        context = self.format_context(context_docs)
        
        # Extract triage information
        triage_info = self.extract_triage_info(context_docs)
        
        # Generate response
        if self.use_advanced_llm:
            answer = self.generate_advanced_response(query, context)
        else:
            answer = self.generate_simple_response(query, context)
        
        # Generate next steps
        next_steps = self.generate_next_steps(triage_info, query)
        
        # Calculate confidence
        confidence = self.calculate_confidence(context_docs, query)
        
        # Prepare sources for transparency
        sources = []
        for doc in context_docs:
            sources.append({
                'type': doc['metadata'].get('type', 'unknown'),
                'content_preview': doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
                'relevance_score': round(1.0 - doc['distance'], 2)
            })
        
        return RAGResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            triage_info=triage_info,
            next_steps=next_steps
        )


def setup_rag_pipeline(
    data_dir: str = "./data",
    db_dir: str = "./chroma_db",
    llm_type: str = "simple",
    openai_api_key: Optional[str] = None
) -> HealthcareRAGPipeline:
    """
    Set up the complete RAG pipeline.
    
    Args:
        data_dir: Directory containing healthcare data
        db_dir: Directory for vector database
        llm_type: Type of LLM to use
        openai_api_key: OpenAI API key if using OpenAI
        
    Returns:
        Initialized HealthcareRAGPipeline
    """
    print("Setting up Healthcare RAG Pipeline...")
    
    # Initialize vector database
    from src.vector_db import setup_vector_database
    vector_db = setup_vector_database(data_dir, db_dir)
    
    # Initialize RAG pipeline
    rag_pipeline = HealthcareRAGPipeline(
        vector_db=vector_db,
        llm_type=llm_type,
        openai_api_key=openai_api_key
    )
    
    print("RAG Pipeline setup complete!")
    return rag_pipeline


def test_rag_pipeline():
    """Test the RAG pipeline with sample queries."""
    print("Testing Healthcare RAG Pipeline...")
    
    # Setup pipeline
    rag = setup_rag_pipeline()
    
    # Test queries
    test_queries = [
        "I'm 55 and having chest tightness on and off since this morning. I have ABC insurance.",
        "What documents do I need to bring for my visit?",
        "What are the copays for emergency visits with Blue Cross Blue Shield?",
        "I have a skin rash that appeared yesterday. What should I do?",
        "What are the best times to visit for lab work?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        response = rag.process_query(query)
        
        print(f"\nAnswer (Confidence: {response.confidence}):")
        print(response.answer)
        
        if response.triage_info:
            print(f"\nTriage Info:")
            print(f"- Urgency: {response.triage_info.get('urgency_level')}")
            print(f"- Department: {response.triage_info.get('department')}")
            print(f"- Priority: {response.triage_info.get('priority')}")
        
        if response.next_steps:
            print(f"\nNext Steps:")
            for step in response.next_steps:
                print(f"- {step}")
        
        print(f"\nSources ({len(response.sources)} found):")
        for i, source in enumerate(response.sources[:2]):  # Show top 2 sources
            print(f"{i+1}. {source['type']}: {source['content_preview']}")


if __name__ == "__main__":
    # Test the RAG pipeline
    test_rag_pipeline()