from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import tiktoken

class IntelligentTextSplitter:
    """Advanced text splitting with multiple strategies."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoding.encode(text))
    
    def recursive_split(self, documents: List[Document]) -> List[Document]:
        """Split documents using recursive character splitting."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.count_tokens,
            separators=["\n\n", "\n", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(documents)
        
        # Add chunk metadata
        for i, doc in enumerate(split_docs):
            doc.metadata.update({
                "chunk_id": i,
                "chunk_size": self.count_tokens(doc.page_content)
            })
        
        return split_docs

    def semantic_split(self, documents: List[Document]) -> List[Document]:
        """Split based on semantic boundaries (paragraphs, sections)."""
        semantic_chunks = []
        
        for doc in documents:
            content = doc.page_content
            
            # Split by double newlines (paragraphs)
            paragraphs = content.split('\n\n')
            
            current_chunk = ""
            current_tokens = 0

            for paragraph in paragraphs:
                paragraph_tokens = self.count_tokens(paragraph)
                
                # If adding this paragraph exceeds chunk size, save current chunk
                if current_tokens + paragraph_tokens > self.chunk_size and current_chunk:
                    semantic_chunks.append(Document(
                        page_content=current_chunk.strip(),
                        metadata={
                            **doc.metadata,
                            "chunk_type": "semantic",
                            "token_count": current_tokens
                        }
                    ))

                    # Start new chunk with overlap
                    overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                    current_chunk = overlap_text + paragraph
                    current_tokens = self.count_tokens(current_chunk)
                else:
                    current_chunk += "\n\n" + paragraph if current_chunk else paragraph
                    current_tokens += paragraph_tokens
            
            # Add the final chunk
            if current_chunk:
                semantic_chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={
                        **doc.metadata,
                        "chunk_type": "semantic",
                        "token_count": current_tokens
                    }
                ))
        
        return semantic_chunks