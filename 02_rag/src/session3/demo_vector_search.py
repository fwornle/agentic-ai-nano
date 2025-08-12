"""Demo script for Session 3 vector search capabilities."""

import asyncio
import os
from typing import List
from config import config
from production_vector_search import ProductionVectorSearch


def create_sample_documents() -> List[str]:
    """Create sample documents for testing."""
    return [
        "Vector databases are specialized systems for storing and querying high-dimensional vectors efficiently.",
        "ChromaDB is an open-source vector database that offers excellent performance for development and moderate-scale production.",
        "Pinecone provides enterprise-grade managed vector search with automatic scaling and high availability.",
        "HNSW (Hierarchical Navigable Small World) algorithm creates graph-based indices for fast approximate nearest neighbor search.",
        "Hybrid search combines semantic vector search with traditional keyword search for improved relevance.",
        "BM25 is a probabilistic ranking function that outperforms TF-IDF for many information retrieval tasks.",
        "Reciprocal Rank Fusion (RRF) effectively combines rankings from multiple search systems.",
        "Cross-encoder reranking provides more accurate relevance scoring by jointly processing query-document pairs.",
        "IVF (Inverted File) indexing uses clustering to efficiently search large vector collections.",
        "Product Quantization (PQ) enables compression of vectors for memory-efficient storage."
    ]


async def demo_production_search():
    """Demonstrate production vector search capabilities."""
    print("🚀 Session 3: Vector Databases & Search Optimization Demo")
    print("=" * 60)
    
    # Setup configuration
    demo_config = config.get_production_config()
    demo_config['documents'] = create_sample_documents()
    demo_config['use_pinecone'] = False  # Disable for demo (requires API key)
    
    # Initialize production search system
    print("\n📊 Initializing Production Vector Search System...")
    search_system = ProductionVectorSearch(demo_config)
    
    # Demo queries
    demo_queries = [
        "What is vector database indexing?",
        "How does hybrid search work?",
        "What are the benefits of HNSW algorithm?",
        "How to optimize vector search performance?"
    ]
    
    print("\n🔍 Testing Different Search Methods...")
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        
        try:
            # Test hybrid search
            print("🔄 Hybrid Search:")
            hybrid_results = await search_system.production_search(
                query, search_type="hybrid", top_k=3
            )
            print(f"   Results: {hybrid_results['total_results']}")
            print(f"   Time: {hybrid_results['search_time']:.3f}s")
            
            # Test multi-stage search  
            print("🎯 Multi-Stage Search:")
            multi_stage_results = await search_system.production_search(
                query, search_type="multi_stage", top_k=3
            )
            print(f"   Results: {multi_stage_results['total_results']}")
            print(f"   Time: {multi_stage_results['search_time']:.3f}s")
            
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    # Display performance metrics
    print("\n📈 Performance Metrics:")
    for search_type, metrics in search_system.performance_metrics.items():
        avg_time = metrics['total_time'] / metrics['total_queries']
        print(f"   {search_type}: {avg_time:.3f}s avg, {metrics['total_queries']} queries")


def demo_architecture_recommendations():
    """Demo architecture recommendation system."""
    print("\n🏗️  Architecture Recommendations Demo")
    print("=" * 40)
    
    from production_vector_search import RAGArchitectureOptimizer
    
    # Test scenarios
    scenarios = [
        {
            'name': 'High-Performance RAG',
            'requirements': {
                'daily_queries': 10000,
                'document_count': 500000,
                'max_latency_ms': 50,
                'monthly_budget_usd': 1000,
                'min_recall': 0.95
            }
        },
        {
            'name': 'Cost-Optimized RAG',
            'requirements': {
                'daily_queries': 1000,
                'document_count': 2000000,
                'max_latency_ms': 300,
                'monthly_budget_usd': 150,
                'min_recall': 0.85
            }
        },
        {
            'name': 'Balanced RAG',
            'requirements': {
                'daily_queries': 5000,
                'document_count': 100000,
                'max_latency_ms': 200,
                'monthly_budget_usd': 500,
                'min_recall': 0.90
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        recommendation = RAGArchitectureOptimizer.recommend_architecture(
            scenario['requirements']
        )
        
        print(f"   Recommended: {recommendation['database']} with {recommendation['index_type']}")
        print(f"   Rationale: {recommendation['rationale']}")
        
        if 'expected_performance' in recommendation:
            perf = recommendation['expected_performance']
            print(f"   Expected Performance:")
            for metric, value in perf.items():
                print(f"     {metric}: {value}")


def main():
    """Main demo function."""
    try:
        # Run async demos
        asyncio.run(demo_production_search())
        
        # Run sync demos
        demo_architecture_recommendations()
        
        print("\n✅ Session 3 Demo Completed Successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("   • Multi-database vector store support")
        print("   • Hybrid search with BM25 + semantic similarity")
        print("   • Multi-stage retrieval pipeline")
        print("   • Architecture recommendation system")
        print("   • Performance monitoring and optimization")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Note: Some features require API keys or running databases")


if __name__ == "__main__":
    main()