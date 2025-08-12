from typing import List
from rag_system import BasicRAGSystem
from document_loader import DocumentLoader
from text_splitter import IntelligentTextSplitter
from config import RAGConfig

class InteractiveRAG:
    """Interactive interface for RAG system."""
    
    def __init__(self):
        self.config = RAGConfig()
        self.rag_system = BasicRAGSystem(self.config)
        self.document_loader = DocumentLoader()
        self.text_splitter = IntelligentTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )
        
    def load_and_index_documents(self, sources: List[str]):
        """Load and index documents from sources."""
        print(f"Loading documents from {len(sources)} sources...")
        
        # Load documents
        documents = self.document_loader.load_documents(sources)
        
        if not documents:
            print("No documents loaded!")
            return
        
        # Split documents into chunks
        print("Splitting documents into chunks...")
        chunks = self.text_splitter.semantic_split(documents)
        
        # Index in vector store
        self.rag_system.vector_store.add_documents(chunks)
        
        print(f"✅ Successfully indexed {len(chunks)} chunks from {len(documents)} documents")

    def start_chat(self):
        """Start interactive chat session."""
        print("=" * 60)
        print("🤖 RAG System Ready!")
        print("=" * 60)
        print("Type your questions. Use 'quit' or 'exit' to stop.")
        print("-" * 60)

        while True:
            try:
                question = input("\n📝 Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not question:
                    print("Please enter a question.")
                    continue
                
                print("\n🔍 Searching and generating answer...")
                result = self.rag_system.query(question)
                
                self._display_result(result)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

    def _display_result(self, result):
        """Display RAG result in a formatted way."""
        print("\n" + "="*50)
        print("🎯 Answer:")
        print("-"*50)
        print(result["answer"])
        
        print(f"\n📊 Confidence: {result['confidence']}")
        print(f"📚 Sources used: {result['num_sources']}")
        
        if result["sources"]:
            print("\n📖 Sources:")
            print("-"*30)
            for i, source in enumerate(result["sources"], 1):
                print(f"{i}. Score: {source['relevance_score']}")
                print(f"   Source: {source['metadata'].get('source', 'Unknown')}")
                print(f"   Preview: {source['content']}")
                print()
        
        print("="*50)