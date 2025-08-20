"""
Vector store management for RAG
"""
import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class VectorStore:
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or os.getenv("VECTOR_DB_PATH", "./data/vector_store")
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        if not CHROMADB_AVAILABLE:
            print("Warning: ChromaDB not available. Vector search disabled.")
            self.client = None
            self.collection = None
            return
            
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection("chore_advice")
        except:
            # Create collection with embedding function
            embedding_function = embedding_functions.DefaultEmbeddingFunction()
            self.collection = self.client.create_collection(
                name="chore_advice",
                embedding_function=embedding_function
            )
    
    def is_available(self) -> bool:
        """Check if vector store is available"""
        return CHROMADB_AVAILABLE and self.client is not None
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to vector store"""
        if not self.is_available():
            return False
            
        try:
            ids = []
            texts = []
            metadatas = []
            
            for i, doc in enumerate(documents):
                ids.append(f"doc_{i}")
                texts.append(doc.get("text", ""))
                metadatas.append({
                    "category": doc.get("category", "general"),
                    "source": doc.get("source", "unknown")
                })
            
            self.collection.add(
                documents=texts,
                ids=ids,
                metadatas=metadatas
            )
            return True
            
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def search(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if not self.is_available():
            return []
            
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = []
            if results.get("documents") and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results.get("metadatas", [[]])[0]
                    distance = results.get("distances", [[]])[0]
                    
                    documents.append({
                        "text": doc,
                        "metadata": metadata[i] if i < len(metadata) else {},
                        "score": 1 - distance[i] if i < len(distance) else 0.0
                    })
            
            return documents
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_collection_count(self) -> int:
        """Get number of documents in collection"""
        if not self.is_available():
            return 0
            
        try:
            return self.collection.count()
        except:
            return 0


def initialize_knowledge_base(vector_store: VectorStore, knowledge_file: str = None):
    """Initialize the knowledge base with chore advice"""
    if not vector_store.is_available():
        print("Vector store not available, skipping knowledge base initialization")
        return False
    
    # Check if already initialized
    if vector_store.get_collection_count() > 0:
        print("Knowledge base already initialized")
        return True
    
    knowledge_file = knowledge_file or os.path.join(
        os.path.dirname(__file__), "..", "knowledge", "chore_tips.json"
    )
    
    if not os.path.exists(knowledge_file):
        print(f"Knowledge file not found: {knowledge_file}")
        return False
    
    try:
        with open(knowledge_file, 'r') as f:
            knowledge_data = json.load(f)
        
        documents = []
        for category, tips in knowledge_data.items():
            for tip in tips:
                documents.append({
                    "text": tip,
                    "category": category,
                    "source": "chore_tips"
                })
        
        success = vector_store.add_documents(documents)
        if success:
            print(f"Successfully initialized knowledge base with {len(documents)} documents")
        return success
        
    except Exception as e:
        print(f"Error initializing knowledge base: {e}")
        return False
