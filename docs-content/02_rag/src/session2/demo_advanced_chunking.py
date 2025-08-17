"""
Advanced Chunking and Preprocessing Demo

This script demonstrates the advanced document processing capabilities
including hierarchical chunking, metadata extraction, and quality assessment.
"""

import os
from pathlib import Path
from langchain.schema import Document
from advanced_chunking import (
    AdvancedProcessingPipeline,
    ChunkQualityAssessor,
    DocumentStructureAnalyzer,
    HierarchicalChunker,
    MetadataEnhancedChunker
)

def create_sample_document() -> Document:
    """Create a sample document with various content types."""
    sample_content = """
# Advanced RAG Systems: A Comprehensive Guide

## Introduction

Retrieval-Augmented Generation (RAG) systems represent a significant advancement in AI technology. These systems combine the power of large language models with external knowledge bases to provide more accurate and contextual responses.

### Key Components

The main components of a RAG system include:

- **Document Processing Pipeline**: Handles ingestion and preprocessing
- **Vector Database**: Stores and retrieves semantic embeddings
- **Query Engine**: Processes user queries and retrieves relevant content
- **Generation Model**: Produces final responses based on retrieved context

## Technical Architecture

### Data Flow

```python
def process_document(document):
    # Chunk the document
    chunks = chunker.create_chunks(document)
    
    # Create embeddings
    embeddings = embed_model.encode(chunks)
    
    # Store in vector database
    vector_db.add(embeddings, chunks)
    
    return chunks
```

### Performance Metrics

| Metric | Basic RAG | Advanced RAG | Improvement |
|--------|-----------|--------------|-------------|
| Accuracy | 65% | 87% | +22% |
| Response Time | 2.3s | 1.8s | -0.5s |
| User Satisfaction | 3.2/5 | 4.6/5 | +1.4 |

## Implementation Considerations

When implementing advanced chunking strategies, consider:

1. **Document Structure**: Preserve hierarchical relationships
2. **Content Types**: Handle tables, code blocks, and images differently
3. **Metadata Extraction**: Capture entities, topics, and context
4. **Quality Assessment**: Measure and optimize chunk effectiveness

> "The quality of your chunks determines the quality of your RAG system's responses." - RAG Expert

### Best Practices

For optimal results:
- Use structure-aware chunking algorithms
- Extract and preserve rich metadata
- Implement quality assessment frameworks
- Monitor and iterate on performance metrics

## Conclusion

Advanced chunking and preprocessing transform RAG systems from simple text splitters into intelligent document understanding engines. This foundation enables superior retrieval accuracy and user experience.
"""
    
    return Document(
        page_content=sample_content,
        metadata={
            "source": "advanced_rag_guide.md",
            "title": "Advanced RAG Systems: A Comprehensive Guide",
            "author": "RAG Expert",
            "created_date": "2024-01-01"
        }
    )

def demo_document_analysis():
    """Demonstrate document structure analysis."""
    print("=== Document Structure Analysis Demo ===")
    
    # Create sample document
    document = create_sample_document()
    
    # Initialize analyzer
    analyzer = DocumentStructureAnalyzer()
    
    # Analyze document structure
    elements = analyzer.analyze_structure(document)
    
    print(f"Document analyzed into {len(elements)} elements:")
    
    for i, element in enumerate(elements[:10]):  # Show first 10 elements
        print(f"{i+1}. Type: {element.element_type.value}, Level: {element.level}")
        print(f"   Content preview: {element.content[:100]}...")
        print(f"   Metadata: {element.metadata}")
        print()

def demo_hierarchical_chunking():
    """Demonstrate hierarchical chunking."""
    print("=== Hierarchical Chunking Demo ===")
    
    # Create sample document
    document = create_sample_document()
    
    # Initialize chunker
    chunker = HierarchicalChunker(max_chunk_size=800, overlap_ratio=0.1)
    
    # Create hierarchical chunks
    chunks = chunker.create_hierarchical_chunks(document)
    
    print(f"Document chunked into {len(chunks)} hierarchical chunks:")
    
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"Size: {len(chunk.page_content)} characters")
        print(f"Section: {chunk.metadata.get('section_title', 'N/A')}")
        print(f"Content types: {chunk.metadata.get('content_types', [])}")
        print(f"Preview: {chunk.page_content[:200]}...")

def demo_metadata_enhanced_chunking():
    """Demonstrate metadata-enhanced chunking."""
    print("=== Metadata-Enhanced Chunking Demo ===")
    
    # Create sample document
    document = create_sample_document()
    
    # Initialize enhanced chunker
    chunker = MetadataEnhancedChunker(max_chunk_size=800)
    
    # Create enhanced chunks
    chunks = chunker.create_enhanced_chunks(document)
    
    print(f"Document processed into {len(chunks)} metadata-enhanced chunks:")
    
    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"\nChunk {i+1}:")
        print(f"Topics: {chunk.metadata.get('topics', [])}")
        print(f"Entities: {chunk.metadata.get('entities', [])[:5]}")
        print(f"Keywords: {chunk.metadata.get('keywords', [])[:5]}")
        print(f"Difficulty: {chunk.metadata.get('difficulty_level', 'N/A')}")
        print(f"Summary: {chunk.metadata.get('content_summary', 'N/A')[:100]}...")

def demo_advanced_pipeline():
    """Demonstrate the complete advanced processing pipeline."""
    print("=== Advanced Processing Pipeline Demo ===")
    
    # Create sample document
    document = create_sample_document()
    
    # Initialize pipeline
    pipeline = AdvancedProcessingPipeline(
        max_chunk_size=800,
        enable_metadata_extraction=True,
        enable_multimodal_processing=True
    )
    
    # Process document
    chunks = pipeline.process_document(document)
    
    print(f"Pipeline processed document into {len(chunks)} optimized chunks:")
    
    # Show processing strategy used
    if chunks:
        strategy = chunks[0].metadata.get('processing_strategy', 'N/A')
        complexity = chunks[0].metadata.get('original_complexity', 'N/A')
        print(f"Strategy used: {strategy}")
        print(f"Complexity score: {complexity}")
    
    # Display chunk summaries
    for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
        print(f"\nChunk {i+1} Summary:")
        print(f"  Size: {len(chunk.page_content)} chars")
        print(f"  Topics: {chunk.metadata.get('topics', [])}")
        print(f"  Has tables: {chunk.metadata.get('has_table', False)}")
        print(f"  Has code: {chunk.metadata.get('has_code', False)}")

def demo_quality_assessment():
    """Demonstrate chunk quality assessment."""
    print("=== Quality Assessment Demo ===")
    
    # Create sample document and process it
    document = create_sample_document()
    pipeline = AdvancedProcessingPipeline(max_chunk_size=600)
    chunks = pipeline.process_document(document)
    
    # Initialize quality assessor
    assessor = ChunkQualityAssessor()
    
    # Assess quality
    quality_scores = assessor.assess_chunk_quality(chunks)
    
    print("Quality Assessment Results:")
    for metric, score in quality_scores.items():
        print(f"  {metric.replace('_', ' ').title()}: {score:.3f}")
    
    # Generate detailed report
    print("\n" + "="*50)
    report = assessor.generate_quality_report(chunks)
    print(report)

def main():
    """Run all demonstrations."""
    print("Advanced Chunking and Preprocessing Demonstration")
    print("=" * 60)
    
    # Run all demos
    demo_document_analysis()
    print("\n" + "="*60 + "\n")
    
    demo_hierarchical_chunking()
    print("\n" + "="*60 + "\n")
    
    demo_metadata_enhanced_chunking()
    print("\n" + "="*60 + "\n")
    
    demo_advanced_pipeline()
    print("\n" + "="*60 + "\n")
    
    demo_quality_assessment()
    
    print("\n" + "="*60)
    print("Demo completed! All advanced chunking features demonstrated.")

if __name__ == "__main__":
    main()