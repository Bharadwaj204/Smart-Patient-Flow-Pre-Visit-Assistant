"""
Vector database setup and management using ChromaDB.
"""

import os
import sys
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import numpy as np

# Try different embedding approaches
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    SentenceTransformer = None  # Type: ignore
    EMBEDDING_AVAILABLE = False
    print("Warning: sentence-transformers not available, using fallback embeddings")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_processor import Document, HealthcareDataProcessor


class HealthcareVectorDB:
    """Vector database for healthcare information using ChromaDB."""
    
    def __init__(self, persist_directory: str = "./chroma_db", embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector database.
        
        Args:
            persist_directory: Directory to persist the ChromaDB data
            embedding_model: Sentence transformer model for embeddings
        """
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        if EMBEDDING_AVAILABLE:
            print(f"Loading embedding model: {embedding_model}")
            try:
                if SentenceTransformer is not None:
                    self.embedding_model = SentenceTransformer(embedding_model)
                    self.use_custom_embeddings = False
                else:
                    print("SentenceTransformer not available, using simple custom embeddings")
                    self.use_custom_embeddings = True
            except Exception as e:
                print(f"Failed to load SentenceTransformer: {e}")
                print("Using simple custom embeddings")
                self.use_custom_embeddings = True
        else:
            print("Using simple custom embeddings")
            self.use_custom_embeddings = True
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="healthcare_knowledge",
            metadata={"description": "Healthcare information for patient pre-visit assistance"}
        )
        
    def simple_embedding(self, text: str) -> List[float]:
        """Create simple hash-based embedding for fallback."""
        # Simple word-based embedding for testing
        words = text.lower().split()
        
        # Create a simple vector based on word characteristics
        embedding = [0.0] * 384  # Standard embedding size
        
        for i, word in enumerate(words[:20]):  # Limit to first 20 words
            # Simple hash-based features
            word_hash = hash(word) % 1000
            pos = (word_hash * 13) % 384
            embedding[pos] += 1.0 / (i + 1)
            
            # Add some semantic features for medical terms
            if word in ['pain', 'chest', 'heart', 'emergency']:
                embedding[0] += 2.0
            if word in ['insurance', 'copay', 'coverage']:
                embedding[1] += 2.0
            if word in ['appointment', 'schedule', 'time']:
                embedding[2] += 2.0
                
        # Normalize
        norm = sum(x*x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x/norm for x in embedding]
            
        return embedding
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts."""
        if self.use_custom_embeddings:
            return [self.simple_embedding(text) for text in texts]
        else:
            if self.embedding_model is not None:
                embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
                # Handle both tensor and numpy array cases
                if hasattr(embeddings, 'tolist'):
                    return embeddings.tolist()  # type: ignore
                elif hasattr(embeddings, 'numpy'):
                    return embeddings.numpy().tolist()  # type: ignore
                else:
                    return embeddings  # type: ignore
            else:
                # Fallback to simple embeddings
                return [self.simple_embedding(text) for text in texts]
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector database."""
        if not documents:
            print("No documents to add")
            return
        
        print(f"Adding {len(documents)} documents to vector database...")
        
        # Prepare data for ChromaDB
        ids = []
        documents_text = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            ids.append(f"{doc.source}_{i}")
            documents_text.append(doc.content)
            metadatas.append(doc.metadata)
        
        # Create embeddings
        print("Creating embeddings...")
        embeddings = self.create_embeddings(documents_text)
        
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                documents=documents_text,
                metadatas=metadatas,
                embeddings=embeddings  # type: ignore
            )
        except Exception as e:
            print(f"Error adding documents to collection: {e}")
            raise
        
        print(f"Successfully added {len(documents)} documents to vector database")
    
    def search(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Search the vector database for relevant documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            Search results with documents, metadata, and distances
        """
        # Create embedding for query
        query_embedding = self.create_embeddings([query])[0]
        
        # Search the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )
        
        # Convert QueryResult to Dict for type compatibility
        return dict(results)  # type: ignore
    
    def search_by_type(self, query: str, doc_type: str, n_results: int = 3) -> Dict[str, Any]:
        """Search for documents of a specific type."""
        filter_metadata = {"type": doc_type}
        return self.search(query, n_results, filter_metadata)
    
    def search_departments(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """Search for department-related information."""
        return self.search_by_type(query, "department", n_results)
    
    def search_triage(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search for triage-related information."""
        return self.search_by_type(query, "triage", n_results)
    
    def search_insurance(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """Search for insurance-related information."""
        return self.search_by_type(query, "insurance", n_results)
    
    def search_faqs(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """Search for FAQ information."""
        return self.search_by_type(query, "faq", n_results)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection.name,
            "embedding_model": self.embedding_model_name
        }
    
    def reset_database(self) -> None:
        """Reset the vector database (delete all data)."""
        print("Resetting vector database...")
        self.client.reset()
        self.collection = self.client.get_or_create_collection(
            name="healthcare_knowledge",
            metadata={"description": "Healthcare information for patient pre-visit assistance"}
        )
        print("Vector database reset complete")


def setup_vector_database(data_dir: str = "./data", db_dir: str = "./chroma_db", reset: bool = False) -> HealthcareVectorDB:
    """
    Set up the vector database with healthcare data.
    
    Args:
        data_dir: Directory containing healthcare data files
        db_dir: Directory for ChromaDB persistence
        reset: Whether to reset the database before setup
        
    Returns:
        Initialized HealthcareVectorDB instance
    """
    print("Setting up Healthcare Vector Database...")
    
    # Initialize vector database
    vector_db = HealthcareVectorDB(persist_directory=db_dir)
    
    if reset:
        vector_db.reset_database()
    
    # Check if database already has data
    stats = vector_db.get_collection_stats()
    if stats["total_documents"] > 0:
        print(f"Database already contains {stats['total_documents']} documents")
        return vector_db
    
    # Process healthcare data
    processor = HealthcareDataProcessor(data_dir)
    documents = processor.process_all_data()
    
    if not documents:
        print("No documents found to add to database")
        return vector_db
    
    # Add documents to vector database
    vector_db.add_documents(documents)
    
    # Print final stats
    final_stats = vector_db.get_collection_stats()
    print(f"Vector database setup complete!")
    print(f"Total documents: {final_stats['total_documents']}")
    print(f"Embedding model: {final_stats['embedding_model']}")
    
    return vector_db


def test_vector_database():
    """Test the vector database functionality."""
    print("Testing Vector Database...")
    
    # Setup database
    vector_db = setup_vector_database()
    
    # Test queries
    test_queries = [
        "chest pain symptoms",
        "insurance copay emergency",
        "cardiology appointment",
        "what documents do I need",
        "wait times"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        results = vector_db.search(query, n_results=2)
        
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                print(f"Result {i+1}: {doc[:100]}...")
                print(f"Metadata: {results['metadatas'][0][i]}")
                print(f"Distance: {results['distances'][0][i]:.4f}")
        else:
            print("No results found")


if __name__ == "__main__":
    # Run setup and test
    test_vector_database()