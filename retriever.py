# src/retriever.py
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from src.config import settings
from pathlib import Path
import json

class KnowledgeRetriever:
    """Retrieve relevant knowledge from vector database."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key
        )
        self.vector_store = self._load_or_create_db()
    
    def _load_or_create_db(self):
        """Load existing vector DB or create new from knowledge base."""
        db_path = Path(settings.vector_db_path)
        
        if (db_path / "index.faiss").exists():
            print(f"Loading existing vector DB from {db_path}")
            return FAISS.load_local(
                str(db_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            print("Creating new vector DB from knowledge base...")
            return self._create_from_docs()
    
    def _load_knowledge_base(self) -> list[Document]:
        """
        Load knowledge base from JSONL file.
        
        Expected format:
        {"id": "q001", "category": "...", "query": "...", "answer": "...", "source": "..."}
        """
        kb_path = Path(settings.knowledge_base_path)
        jsonl_file = kb_path / "faq.jsonl"
        
        docs = []
        
        if jsonl_file.exists():
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        qa = json.loads(line)
                        doc = Document(
                            page_content=f"Q: {qa['query']}\nA: {qa['answer']}",
                            metadata={
                                "id": qa.get('id', ''),
                                "category": qa.get('category', ''),
                                "source": qa.get('source', '')
                            }
                        )
                        docs.append(doc)
            print(f"✓ Loaded {len(docs)} Q&A pairs from knowledge base")
        else:
            # Fallback: create default document
            docs = [Document(
                page_content="Default knowledge base. Replace with your content.",
                metadata={"source": "default"}
            )]
            print("⚠️  No knowledge base found, using default content")
        
        return docs
    
    def _create_from_docs(self):
        """Create FAISS vector store from documents."""
        docs = self._load_knowledge_base()
        
        # Create vector store
        vector_store = FAISS.from_documents(docs, self.embeddings)
        
        # Save for future use
        db_path = Path(settings.vector_db_path)
        db_path.mkdir(parents=True, exist_ok=True)
        vector_store.save_local(str(db_path))
        
        print(f"✅ Vector DB created with {len(docs)} documents")
        
        return vector_store
    
    def retrieve(self, query: str, k: int = None) -> list[str]:
        """
        Retrieve top-k relevant documents.
        
        Args:
            query: Search query
            k: Number of results (default from settings)
        
        Returns:
            List of document contents
        """
        k = k or settings.retrieval_top_k
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]
