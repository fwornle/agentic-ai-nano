from interactive_rag import InteractiveRAG

def main():
    # Initialize RAG system
    rag = InteractiveRAG()
    
    # Sample documents to index
    sample_sources = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Natural_language_processing"
    ]
    
    # Load and index documents
    rag.load_and_index_documents(sample_sources)
    
    # Start interactive chat
    rag.start_chat()

if __name__ == "__main__":
    main()