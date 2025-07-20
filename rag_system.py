import os
import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import torch

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set PyTorch to use CPU by default to avoid device issues
torch.set_default_device('cpu')

class OppenheimerRAG:
    def __init__(self):
        """Initialize the RAG system for Oppenheimer knowledge base."""
        # Configure Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use Sentence Transformers embedding function with device handling
        try:
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2",
                device="cpu"  # Force CPU to avoid device issues
            )
        except Exception as e:
            logger.warning(f"Failed to initialize sentence transformer: {e}")
            # Fallback to default embedding function
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(
                name="oppenheimer_knowledge",
                embedding_function=self.embedding_function
            )
            logger.info("Loaded existing knowledge base")
        except:
            self.collection = self.client.create_collection(
                name="oppenheimer_knowledge",
                embedding_function=self.embedding_function
            )
            logger.info("Created new knowledge base")
            self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load and process all knowledge base files."""
        knowledge_files = [
            'knowledge_base/oppenheimer_biography.txt',
            'knowledge_base/oppenheimer_quotes.txt',
            'knowledge_base/historical_context.txt'
        ]
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        for file_path in knowledge_files:
            if os.path.exists(file_path):
                logger.info(f"Processing {file_path}")
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Split text into chunks
                chunks = text_splitter.split_text(content)
                
                # Add chunks to ChromaDB
                for i, chunk in enumerate(chunks):
                    doc_id = f"{file_path}_{i}"
                    metadata = {
                        "source": file_path,
                        "chunk_id": i,
                        "file_type": file_path.split('/')[-1].replace('.txt', '')
                    }
                    
                    self.collection.add(
                        documents=[chunk],
                        metadatas=[metadata],
                        ids=[doc_id]
                    )
                
                logger.info(f"Added {len(chunks)} chunks from {file_path}")
    
    def search_knowledge(self, query, n_results=5):
        """Search the knowledge base for relevant information."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if results['documents'] and results['documents'][0]:
                relevant_docs = []
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    relevant_docs.append({
                        'content': doc,
                        'metadata': metadata,
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })
                return relevant_docs
            return []
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_relevant_context(self, query, max_context_length=3000):
        """Get relevant context for a query, formatted for the LLM."""
        search_results = self.search_knowledge(query, n_results=5)
        
        if not search_results:
            return "I don't have specific information about that topic in my knowledge base."
        
        context_parts = []
        total_length = 0
        
        for result in search_results:
            content = result['content']
            if total_length + len(content) < max_context_length:
                context_parts.append(content)
                total_length += len(content)
            else:
                # Add partial content if it fits
                remaining_space = max_context_length - total_length
                if remaining_space > 100:  # Only add if meaningful amount of space
                    context_parts.append(content[:remaining_space] + "...")
                break
        
        return "\n\n".join(context_parts)

def test_rag_system():
    """Test the RAG system with sample queries."""
    rag = OppenheimerRAG()
    
    test_queries = [
        "What did Oppenheimer say about the Trinity test?",
        "Tell me about Oppenheimer's childhood and education",
        "What was Oppenheimer's role in the Manhattan Project?",
        "What did Oppenheimer think about the hydrogen bomb?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("=" * 50)
        context = rag.get_relevant_context(query)
        print(f"Context: {context[:200]}...")
        print()

if __name__ == "__main__":
    test_rag_system()