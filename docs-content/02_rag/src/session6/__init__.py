# Session 6: Graph-Based RAG Package
"""
Session 6: Graph-Based RAG Implementation

This package provides comprehensive GraphRAG implementations including:

1. **NodeRAG Architecture**: Heterogeneous graph systems with specialized node types
2. **Traditional GraphRAG**: Entity-relationship extraction from documents
3. **Code GraphRAG**: AST-based analysis for software repositories
4. **Neo4j Integration**: Production-grade graph database storage
5. **Graph Traversal**: Multi-hop reasoning and semantic-guided exploration
6. **Hybrid Search**: Combines graph traversal with vector similarity
7. **Production System**: Complete orchestration for production deployment

Key Components:
- NodeRAGExtractor: Advanced heterogeneous graph construction
- KnowledgeGraphExtractor: Traditional entity-relationship extraction
- CodeGraphRAG: Software repository analysis
- Neo4jGraphManager: Production database integration
- GraphTraversalEngine: Multi-hop reasoning capabilities
- HybridGraphVectorRAG: Combined graph-vector search
- ProductionGraphRAG: Complete system orchestration

Usage Example:
```python
from session6 import ProductionGraphRAG, create_production_config

# Create configuration
config = create_production_config(
    llm_model=your_llm_model,
    embedding_model=your_embedding_model,
    vector_store=your_vector_store,
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

# Initialize system
graphrag = ProductionGraphRAG(config)

# Ingest documents
result = graphrag.ingest_documents(documents, {
    'method': 'both',  # Use both traditional and NodeRAG
    'store_in_neo4j': True
})

# Perform searches
search_result = graphrag.search("What are the relationships between entities?", {
    'search_type': 'hybrid'
})
```
"""

from .noderag_extractor import NodeRAGExtractor, NodeType, NodeRAGNode
from .knowledge_graph_extractor import KnowledgeGraphExtractor
from .code_graphrag import CodeGraphRAG
from .neo4j_manager import Neo4jGraphManager
from .graph_traversal_engine import GraphTraversalEngine
from .hybrid_graph_vector_rag import HybridGraphVectorRAG
from .production_graphrag import ProductionGraphRAG, create_production_config
from .config import GraphRAGConfig, ConfigManager, get_config
from .utils import (
    setup_logging, 
    timer, 
    GraphMetrics, 
    TextProcessor, 
    FileUtils, 
    PerformanceMonitor,
    ValidationUtils
)

__version__ = "1.0.0"
__author__ = "GraphRAG Session 6"

# Main components
__all__ = [
    # Core GraphRAG components
    'NodeRAGExtractor',
    'KnowledgeGraphExtractor',
    'CodeGraphRAG',
    'Neo4jGraphManager',
    'GraphTraversalEngine',
    'HybridGraphVectorRAG',
    'ProductionGraphRAG',
    
    # Configuration
    'GraphRAGConfig',
    'ConfigManager',
    'get_config',
    'create_production_config',
    
    # Data structures
    'NodeType',
    'NodeRAGNode',
    
    # Utilities
    'setup_logging',
    'timer',
    'GraphMetrics',
    'TextProcessor',
    'FileUtils',
    'PerformanceMonitor',
    'ValidationUtils',
]

# Package metadata
__package_info__ = {
    'name': 'graphrag-session6',
    'version': __version__,
    'description': 'Advanced Graph-based RAG implementation with NodeRAG, traditional GraphRAG, and hybrid search',
    'components': {
        'NodeRAG': 'Heterogeneous graph architecture with specialized node types',
        'Traditional GraphRAG': 'Entity-relationship extraction from documents',
        'Code GraphRAG': 'AST-based software repository analysis',
        'Neo4j Integration': 'Production-grade graph database storage',
        'Graph Traversal': 'Multi-hop reasoning and semantic exploration',
        'Hybrid Search': 'Combined graph-vector search system',
        'Production System': 'Complete orchestration for deployment'
    },
    'features': [
        'Three-stage NodeRAG processing pipeline',
        'Personalized PageRank for semantic traversal',
        'HNSW similarity edges for high-performance retrieval',
        'Multi-hop graph reasoning',
        'Adaptive fusion strategies',
        'Production-ready Neo4j integration',
        'Comprehensive performance monitoring',
        'Flexible configuration management'
    ]
}


def get_package_info():
    """Get package information and capabilities."""
    return __package_info__


def create_simple_graphrag(documents, llm_model, embedding_model, vector_store):
    """Create a simple GraphRAG system for quick setup.
    
    This is a convenience function for rapid prototyping.
    For production use, use ProductionGraphRAG with proper configuration.
    """
    
    config = {
        'llm_model': llm_model,
        'embedding_model': embedding_model,
        'vector_store': vector_store,
        'enable_noderag': True,
        'enable_code_analysis': False,  # Disable for simple setup
        'neo4j_uri': None  # Use in-memory graphs
    }
    
    # Create knowledge graph extractor
    kg_extractor = KnowledgeGraphExtractor(llm_model)
    
    # Extract knowledge graph
    kg_result = kg_extractor.extract_knowledge_graph(documents)
    
    return {
        'entities': kg_result['entities'],
        'relationships': kg_result['relationships'],
        'graph': kg_result['graph'],
        'extractor': kg_extractor
    }


# Setup logging by default
setup_logging()

print(f"📊 GraphRAG Session 6 Package v{__version__} loaded")
print(f"   Components: {len(__all__)} modules available")
print(f"   Features: NodeRAG, Traditional GraphRAG, Code Analysis, Hybrid Search")
print(f"   Ready for production deployment with Neo4j and vector stores")