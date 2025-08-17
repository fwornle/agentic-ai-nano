"""
Test script to verify the advanced chunking installation and basic functionality.
"""

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        from advanced_chunking import (
            DocumentStructureAnalyzer,
            DocumentElement,
            ContentType,
            HierarchicalChunker,
            MetadataExtractor,
            ExtractedMetadata,
            MetadataEnhancedChunker,
            MultiModalProcessor,
            TableAwareChunker,
            AdvancedProcessingPipeline,
            ChunkQualityAssessor
        )
        print("✓ All advanced_chunking modules imported successfully")
        
        from config import get_config, DEFAULT_CONFIG
        print("✓ Configuration module imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality with a simple document."""
    print("\nTesting basic functionality...")
    
    try:
        from langchain.schema import Document
        from advanced_chunking import DocumentStructureAnalyzer, AdvancedProcessingPipeline
        
        # Create a simple test document
        test_doc = Document(
            page_content="""
# Test Document

This is a test document for the advanced chunking system.

## Introduction

The document contains:
- Multiple sections
- Different content types
- Tables and lists

| Feature | Status |
|---------|--------|
| Import | Working |
| Analysis | Testing |

## Conclusion

The system appears to be working correctly.
""",
            metadata={"source": "test_doc.md"}
        )
        
        # Test document analysis
        analyzer = DocumentStructureAnalyzer()
        elements = analyzer.analyze_structure(test_doc)
        print(f"✓ Document analyzed into {len(elements)} elements")
        
        # Test pipeline processing
        pipeline = AdvancedProcessingPipeline(max_chunk_size=300)
        chunks = pipeline.process_document(test_doc)
        print(f"✓ Document processed into {len(chunks)} chunks")
        
        # Verify chunks have expected metadata
        if chunks and len(chunks) > 0:
            chunk = chunks[0]
            has_metadata = bool(chunk.metadata.get('section_title'))
            print(f"✓ Chunks contain metadata: {has_metadata}")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def test_configuration():
    """Test configuration system."""
    print("\nTesting configuration system...")
    
    try:
        from config import get_config
        
        # Test default config
        default_config = get_config("default")
        print(f"✓ Default config loaded: max_chunk_size = {default_config.chunking.max_chunk_size}")
        
        # Test preset configs
        research_config = get_config("research")
        print(f"✓ Research config loaded: max_chunk_size = {research_config.chunking.max_chunk_size}")
        
        technical_config = get_config("technical")
        print(f"✓ Technical config loaded: max_chunk_size = {technical_config.chunking.max_chunk_size}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test error: {e}")
        return False

def main():
    """Run all tests."""
    print("Advanced Chunking Installation Test")
    print("=" * 40)
    
    all_tests_passed = True
    
    # Run tests
    all_tests_passed &= test_imports()
    all_tests_passed &= test_basic_functionality()
    all_tests_passed &= test_configuration()
    
    print("\n" + "=" * 40)
    if all_tests_passed:
        print("✓ All tests passed! The advanced chunking system is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python demo_advanced_chunking.py' for a full demonstration")
        print("2. Check README.md for usage examples and API documentation")
        print("3. Explore the configuration options in config.py")
    else:
        print("✗ Some tests failed. Please check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that you're running from the correct directory")
        print("3. Verify Python version compatibility (3.8+)")

if __name__ == "__main__":
    main()