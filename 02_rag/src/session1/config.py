import os
from dotenv import load_dotenv

load_dotenv()

class RAGConfig:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    TOP_K = int(os.getenv("TOP_K", 5))
    
    # Vector database settings
    VECTOR_DB_PATH = "./chroma_db"
    COLLECTION_NAME = "rag_documents"
    
    # Model settings
    EMBEDDING_MODEL = "text-embedding-ada-002"
    LLM_MODEL = "gpt-3.5-turbo"