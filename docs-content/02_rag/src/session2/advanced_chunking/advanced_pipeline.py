# src/advanced_chunking/advanced_pipeline.py
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from .hierarchical_chunker import HierarchicalChunker
from .metadata_enhanced_chunker import MetadataEnhancedChunker
from .multimodal_processor import MultiModalProcessor
from .specialized_chunkers import TableAwareChunker

class AdvancedProcessingPipeline:
    """Complete advanced document processing pipeline."""
    
    def __init__(self, 
                 max_chunk_size: int = 1000,
                 enable_metadata_extraction: bool = True,
                 enable_multimodal_processing: bool = True):
        
        self.max_chunk_size = max_chunk_size
        self.enable_metadata_extraction = enable_metadata_extraction
        self.enable_multimodal_processing = enable_multimodal_processing
        
        # Initialize processors
        self.hierarchical_chunker = HierarchicalChunker(max_chunk_size=max_chunk_size)
        self.metadata_chunker = MetadataEnhancedChunker(max_chunk_size=max_chunk_size)
        self.multimodal_processor = MultiModalProcessor()
        self.table_chunker = TableAwareChunker(max_chunk_size=max_chunk_size * 1.5)

    def process_document(self, document: Document) -> List[Document]:
        """Process document using the most appropriate strategy."""
        # Analyze document characteristics
        doc_analysis = self._analyze_document_complexity(document)
        
        # Choose processing strategy based on analysis
        if doc_analysis["has_tables"]:
            print("Using table-aware chunking...")
            processed_docs = self.table_chunker.chunk_with_tables(document)
        else:
            print("Using hierarchical chunking...")
            processed_docs = self.hierarchical_chunker.create_hierarchical_chunks(document)
        
        # Apply multimodal processing if enabled
        if self.enable_multimodal_processing and doc_analysis["has_media"]:
            print("Applying multimodal processing...")
            processed_docs = [
                self.multimodal_processor.process_document_with_images(doc)
                for doc in processed_docs
            ]
        
        # Apply metadata enhancement if enabled
        if self.enable_metadata_extraction:
            print("Enhancing with metadata...")
            final_docs = []
            for doc in processed_docs:
                enhanced_doc = self.metadata_chunker._enhance_chunk_metadata(doc)
                final_docs.append(enhanced_doc)
            processed_docs = final_docs
        
        # Add pipeline metadata
        for doc in processed_docs:
            doc.metadata.update({
                "processing_strategy": doc_analysis["recommended_strategy"],
                "original_complexity": doc_analysis["complexity_score"],
                "processing_pipeline": "advanced_v1"
            })
        
        return processed_docs
    
    def _analyze_document_complexity(self, document: Document) -> Dict[str, Any]:
        """Analyze document to determine optimal processing strategy."""
        content = document.page_content
        
        # Detect various content types
        has_tables = "|" in content and content.count("|") > 5
        has_code = "```" in content or content.count("    ") > 3
        has_lists = content.count("- ") > 3 or content.count("* ") > 3
        has_headings = content.count("#") > 2 or len([line for line in content.split('\n') if line.isupper()]) > 2
        has_media = any(ext in content.lower() for ext in ['.jpg', '.png', '.gif', '.pdf'])
        
        # Calculate complexity score
        complexity_score = 0
        if has_tables: complexity_score += 3
        if has_code: complexity_score += 2
        if has_lists: complexity_score += 1
        if has_headings: complexity_score += 2
        if has_media: complexity_score += 1
        
        # Determine recommended strategy
        if has_tables:
            strategy = "table_aware"
        elif complexity_score > 4:
            strategy = "hierarchical"
        else:
            strategy = "standard"
        
        return {
            "has_tables": has_tables,
            "has_code": has_code,
            "has_lists": has_lists,
            "has_headings": has_headings,
            "has_media": has_media,
            "complexity_score": complexity_score,
            "recommended_strategy": strategy
        }