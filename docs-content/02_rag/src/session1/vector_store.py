from typing import List, Optional
import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from config import RAGConfig

class VectorStore:
    """Manages vector storage and retrieval operations."""
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config.OPENAI_API_KEY,
            model=config.EMBEDDING_MODEL
        )
        self.vectorstore = None
        self._initialize_store()

    def _initialize_store(self):
        """Initialize ChromaDB vector store."""
        try:
            # Try to load existing store
            self.vectorstore = Chroma(
                persist_directory=self.config.VECTOR_DB_PATH,
                embedding_function=self.embeddings,
                collection_name=self.config.COLLECTION_NAME
            )
            print("Loaded existing vector store")
            
        except Exception as e:
            print(f"Creating new vector store: {e}")
            self.vectorstore = Chroma(
                persist_directory=self.config.VECTOR_DB_PATH,
                embedding_function=self.embeddings,
                collection_name=self.config.COLLECTION_NAME
            )

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to vector store."""
        if not documents:
            return []
        
        print(f"Adding {len(documents)} documents to vector store...")
        
        # Generate unique IDs for documents
        doc_ids = [f"doc_{i}_{hash(doc.page_content[:100])}" 
                  for i, doc in enumerate(documents)]
        
        # Add documents with IDs
        self.vectorstore.add_documents(documents, ids=doc_ids)
        
        # Persist the store
        self.vectorstore.persist()
        
        print(f"Successfully indexed {len(documents)} document chunks")
        return doc_ids

    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Perform similarity search."""
        k = k or self.config.TOP_K
        
        results = self.vectorstore.similarity_search(
            query=query,
            k=k
        )
        
        return results
    
    def similarity_search_with_scores(self, query: str, k: Optional[int] = None) -> List[tuple]:
        """Perform similarity search with relevance scores."""
        k = k or self.config.TOP_K
        
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k
        )
        
        return results