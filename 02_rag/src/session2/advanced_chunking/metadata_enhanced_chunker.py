# src/advanced_chunking/metadata_enhanced_chunker.py
from typing import List, Dict, Any
from langchain.schema import Document
from datetime import datetime
from .metadata_extractor import MetadataExtractor
from .hierarchical_chunker import HierarchicalChunker

class MetadataEnhancedChunker:
    """Chunker that enriches chunks with extracted metadata."""
    
    def __init__(self, max_chunk_size: int = 1000):
        self.hierarchical_chunker = HierarchicalChunker(max_chunk_size=max_chunk_size)
        self.metadata_extractor = MetadataExtractor()
    
    def create_enhanced_chunks(self, document: Document) -> List[Document]:
        """Create chunks with rich metadata."""
        # First, create hierarchical chunks
        chunks = self.hierarchical_chunker.create_hierarchical_chunks(document)
        
        # Enhance each chunk with extracted metadata
        enhanced_chunks = []
        for chunk in chunks:
            enhanced_chunk = self._enhance_chunk_metadata(chunk)
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks

    def _enhance_chunk_metadata(self, chunk: Document) -> Document:
        """Enhance chunk with extracted metadata."""
        # Extract metadata from chunk content
        extracted_metadata = self.metadata_extractor.extract_enhanced_metadata(chunk)
        
        # Merge with existing metadata
        enhanced_metadata = {
            **chunk.metadata,
            "entities": extracted_metadata.entities,
            "keywords": extracted_metadata.keywords,
            "topics": extracted_metadata.topics,
            "dates": extracted_metadata.dates,
            "technical_terms": extracted_metadata.technical_terms,
            "difficulty_level": extracted_metadata.difficulty_level,
            "content_summary": extracted_metadata.content_summary,
            "word_count": len(chunk.page_content.split()),
            "char_count": len(chunk.page_content),
            "enhanced_at": datetime.now().isoformat()
        }
        
        # Create searchable content that includes metadata
        searchable_content = self._create_searchable_content(chunk.page_content, extracted_metadata)
        
        return Document(
            page_content=searchable_content,
            metadata=enhanced_metadata
        )
    
    def _create_searchable_content(self, original_content: str, metadata: Any) -> str:
        """Create enhanced searchable content."""
        # Add metadata as searchable text
        metadata_text_parts = []
        
        if metadata.keywords:
            metadata_text_parts.append(f"Keywords: {', '.join(metadata.keywords)}")
        
        if metadata.topics:
            metadata_text_parts.append(f"Topics: {', '.join(metadata.topics)}")
        
        if metadata.entities:
            metadata_text_parts.append(f"Entities: {', '.join(metadata.entities[:5])}")
        
        if metadata.content_summary:
            metadata_text_parts.append(f"Summary: {metadata.content_summary}")
        
        metadata_text = "\n".join(metadata_text_parts)
        
        # Combine original content with metadata
        if metadata_text:
            return f"{original_content}\n\n--- Metadata ---\n{metadata_text}"
        else:
            return original_content