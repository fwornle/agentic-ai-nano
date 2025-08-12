# Production GraphRAG system orchestrator
from typing import Dict, List, Any
from knowledge_graph_extractor import KnowledgeGraphExtractor
from code_graphrag import CodeGraphRAG
from neo4j_manager import Neo4jGraphManager
from hybrid_graph_vector_rag import HybridGraphVectorRAG
from noderag_extractor import NodeRAGExtractor
import time


class ProductionGraphRAG:
    """Production-ready GraphRAG system that combines all components.
    
    This system integrates:
    - Traditional GraphRAG for document analysis
    - NodeRAG for advanced heterogeneous graph reasoning
    - Code GraphRAG for software repository analysis
    - Neo4j for production-grade graph storage
    - Hybrid search combining graph traversal with vector similarity
    
    The system is designed for production deployment with:
    - Scalable graph storage and querying
    - Performance monitoring and optimization
    - Flexible configuration for different use cases
    - Comprehensive error handling and recovery
    """
    
    def __init__(self, config: Dict):
        """Initialize production GraphRAG system with configuration."""
        
        self.config = config
        
        # Initialize core components based on configuration
        print("Initializing Production GraphRAG System...")
        
        # Knowledge graph extractor for traditional GraphRAG
        self.kg_extractor = KnowledgeGraphExtractor(
            llm_model=config['llm_model']
        )
        print("✓ Traditional GraphRAG extractor initialized")
        
        # NodeRAG extractor for heterogeneous graph architecture
        if config.get('enable_noderag', True):
            self.noderag_extractor = NodeRAGExtractor(
                llm_model=config['llm_model'],
                spacy_model=config.get('spacy_model', 'en_core_web_lg')
            )
            print("✓ NodeRAG heterogeneous extractor initialized")
        else:
            self.noderag_extractor = None
        
        # Code analyzer for software repositories
        if config.get('enable_code_analysis', True):
            self.code_analyzer = CodeGraphRAG(
                supported_languages=config.get('languages', ['python', 'javascript'])
            )
            print("✓ Code GraphRAG analyzer initialized")
        else:
            self.code_analyzer = None
        
        # Neo4j manager for production graph storage
        if config.get('neo4j_uri'):
            self.neo4j_manager = Neo4jGraphManager(
                uri=config['neo4j_uri'],
                username=config['neo4j_user'], 
                password=config['neo4j_password']
            )
            print("✓ Neo4j production storage initialized")
        else:
            self.neo4j_manager = None
            print("⚠ Neo4j not configured, using in-memory graphs only")
        
        # Hybrid search system
        if config.get('vector_store') and self.neo4j_manager:
            self.hybrid_rag = HybridGraphVectorRAG(
                neo4j_manager=self.neo4j_manager,
                vector_store=config['vector_store'],
                embedding_model=config['embedding_model'],
                llm_model=config['llm_model']
            )
            print("✓ Hybrid graph-vector search initialized")
        else:
            self.hybrid_rag = None
            print("⚠ Hybrid search not available - requires both vector store and Neo4j")
        
        # Performance monitoring
        self.performance_metrics = {
            'ingestion_times': [],
            'search_times': [],
            'graph_sizes': [],
            'system_health': {}
        }
        
        print(f"🚀 Production GraphRAG System Ready")
        print(f"   Components: {self._get_enabled_components()}")
    
    def ingest_documents(self, documents: List[str], 
                        ingestion_config: Dict = None) -> Dict[str, Any]:
        """Ingest documents and build knowledge graph using specified method."""
        
        config = ingestion_config or {
            'method': 'traditional',  # 'traditional', 'noderag', or 'both'
            'store_in_neo4j': True,
            'enable_entity_merging': True,
            'confidence_threshold': 0.6
        }
        
        start_time = time.time()
        print(f"\n📥 Ingesting {len(documents)} documents using {config['method']} method...")
        
        ingestion_results = {}
        
        # Traditional GraphRAG extraction
        if config['method'] in ['traditional', 'both']:
            print("Extracting traditional knowledge graph...")
            traditional_result = self.kg_extractor.extract_knowledge_graph(
                documents, {
                    'merge_similar_entities': config.get('enable_entity_merging', True),
                    'min_entity_confidence': config.get('confidence_threshold', 0.6),
                    'use_llm_enhancement': config.get('use_llm_enhancement', True)
                }
            )
            ingestion_results['traditional_kg'] = traditional_result
            print(f"✓ Traditional KG: {len(traditional_result['entities'])} entities, {len(traditional_result['relationships'])} relationships")
        
        # NodeRAG extraction
        if config['method'] in ['noderag', 'both'] and self.noderag_extractor:
            print("Extracting NodeRAG heterogeneous graph...")
            noderag_result = self.noderag_extractor.extract_noderag_graph(
                documents, {
                    'node_types': config.get('node_types', ['entity', 'concept', 'document', 'relationship']),
                    'enable_pagerank': config.get('enable_pagerank', True),
                    'enable_hnsw_similarity': config.get('enable_hnsw_similarity', True),
                    'reasoning_integration': config.get('reasoning_integration', True)
                }
            )
            ingestion_results['noderag_kg'] = noderag_result
            print(f"✓ NodeRAG: {len(noderag_result['heterogeneous_nodes'])} specialized nodes, {len(noderag_result['reasoning_pathways'])} pathways")
        
        # Store in Neo4j if configured
        if config.get('store_in_neo4j', True) and self.neo4j_manager:
            storage_results = {}
            
            # Store traditional KG
            if 'traditional_kg' in ingestion_results:
                traditional_storage = self.neo4j_manager.store_knowledge_graph(
                    ingestion_results['traditional_kg']['entities'],
                    ingestion_results['traditional_kg']['relationships']
                )
                storage_results['traditional_storage'] = traditional_storage
                print(f"✓ Stored traditional KG in Neo4j: {traditional_storage['entities_stored']} entities")
            
            # Store NodeRAG (convert to compatible format)
            if 'noderag_kg' in ingestion_results:
                # Convert NodeRAG nodes to traditional format for Neo4j storage
                noderag_entities, noderag_relationships = self._convert_noderag_for_storage(
                    ingestion_results['noderag_kg']
                )
                noderag_storage = self.neo4j_manager.store_knowledge_graph(
                    noderag_entities, noderag_relationships
                )
                storage_results['noderag_storage'] = noderag_storage
                print(f"✓ Stored NodeRAG in Neo4j: {noderag_storage['entities_stored']} specialized nodes")
            
            ingestion_results['storage'] = storage_results
        
        ingestion_time = time.time() - start_time
        self.performance_metrics['ingestion_times'].append(ingestion_time)
        
        # Calculate comprehensive statistics
        total_entities = 0
        total_relationships = 0
        
        if 'traditional_kg' in ingestion_results:
            total_entities += len(ingestion_results['traditional_kg']['entities'])
            total_relationships += len(ingestion_results['traditional_kg']['relationships'])
        
        if 'noderag_kg' in ingestion_results:
            total_entities += len(ingestion_results['noderag_kg']['heterogeneous_nodes'])
            # NodeRAG relationships are embedded in the graph structure
        
        self.performance_metrics['graph_sizes'].append({
            'entities': total_entities,
            'relationships': total_relationships,
            'timestamp': time.time()
        })
        
        print(f"✅ Document ingestion complete in {ingestion_time:.2f}s")
        print(f"   Total entities: {total_entities}, Total relationships: {total_relationships}")
        
        return {
            'extraction_results': ingestion_results,
            'performance': {
                'ingestion_time_seconds': ingestion_time,
                'entities_per_second': total_entities / ingestion_time if ingestion_time > 0 else 0,
                'total_entities': total_entities,
                'total_relationships': total_relationships
            },
            'config_used': config
        }
    
    def analyze_repository(self, repo_path: str, 
                          analysis_config: Dict = None) -> Dict[str, Any]:
        """Analyze code repository and build code knowledge graph."""
        
        if not self.code_analyzer:
            return {'error': 'Code analysis not enabled in configuration'}
        
        config = analysis_config or {
            'max_files': 1000,
            'include_patterns': ['*.py', '*.js', '*.ts'],
            'exclude_patterns': ['*test*', '*__pycache__*', '*.min.js'],
            'store_in_neo4j': True,
            'build_call_graph': True,
            'analyze_dependencies': True
        }
        
        start_time = time.time()
        print(f"\n🔍 Analyzing code repository: {repo_path}")
        
        # Analyze repository using Code GraphRAG
        code_analysis = self.code_analyzer.analyze_repository(repo_path, config)
        
        # Store in Neo4j if configured
        if config.get('store_in_neo4j', True) and self.neo4j_manager:
            print("Storing code graph in Neo4j...")
            code_storage = self.neo4j_manager.store_knowledge_graph(
                code_analysis['entities'],
                code_analysis['relationships']
            )
            code_analysis['storage_result'] = code_storage
            print(f"✓ Stored code graph: {code_storage['entities_stored']} code entities")
        
        analysis_time = time.time() - start_time
        
        print(f"✅ Repository analysis complete in {analysis_time:.2f}s")
        print(f"   Files analyzed: {code_analysis['analysis_stats']['files_analyzed']}")
        print(f"   Code entities: {len(code_analysis['entities'])}")
        print(f"   Relationships: {len(code_analysis['relationships'])}")
        
        return {
            'code_analysis': code_analysis,
            'performance': {
                'analysis_time_seconds': analysis_time,
                'files_per_second': code_analysis['analysis_stats']['files_analyzed'] / analysis_time if analysis_time > 0 else 0
            },
            'config_used': config
        }
    
    def search(self, query: str, search_config: Dict = None) -> Dict[str, Any]:
        """Perform GraphRAG search using configured method."""
        
        config = search_config or {
            'search_type': 'hybrid',  # 'hybrid', 'graph_only', 'vector_only'
            'max_results': 10,
            'include_reasoning_paths': True,
            'response_detail': 'comprehensive'  # 'brief', 'comprehensive'
        }
        
        if not self.hybrid_rag and config['search_type'] == 'hybrid':
            return {'error': 'Hybrid search not available - requires both vector store and Neo4j configuration'}
        
        start_time = time.time()
        print(f"\n🔍 Searching: {query[:80]}...")
        print(f"   Method: {config['search_type']}")
        
        search_results = {}
        
        if config['search_type'] == 'hybrid' and self.hybrid_rag:
            # Use hybrid graph-vector search
            hybrid_config = {
                'max_vector_results': config.get('max_vector_results', 20),
                'max_graph_paths': config.get('max_graph_paths', 15),
                'fusion_strategy': config.get('fusion_strategy', 'adaptive_selection'),
                'max_final_contexts': config.get('max_results', 10)
            }
            
            search_results = self.hybrid_rag.hybrid_search(query, hybrid_config)
            
        elif config['search_type'] == 'graph_only' and self.neo4j_manager:
            # Use graph-only search
            search_results = self._graph_only_search(query, config)
            
        elif config['search_type'] == 'vector_only' and self.config.get('vector_store'):
            # Use vector-only search
            search_results = self._vector_only_search(query, config)
            
        else:
            return {'error': f"Search type '{config['search_type']}' not supported with current configuration"}
        
        search_time = time.time() - start_time
        self.performance_metrics['search_times'].append(search_time)
        
        # Add performance metadata
        if isinstance(search_results, dict):
            search_results['performance'] = {
                'search_time_seconds': search_time,
                'search_type': config['search_type']
            }
        
        print(f"✅ Search complete in {search_time:.2f}s")
        
        return search_results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status and health metrics."""
        
        status = {
            'system_info': {
                'components_enabled': self._get_enabled_components(),
                'configuration': {
                    'noderag_enabled': self.noderag_extractor is not None,
                    'code_analysis_enabled': self.code_analyzer is not None,
                    'neo4j_enabled': self.neo4j_manager is not None,
                    'hybrid_search_enabled': self.hybrid_rag is not None
                }
            },
            'performance_metrics': {
                'avg_ingestion_time': sum(self.performance_metrics['ingestion_times']) / len(self.performance_metrics['ingestion_times']) if self.performance_metrics['ingestion_times'] else 0,
                'avg_search_time': sum(self.performance_metrics['search_times']) / len(self.performance_metrics['search_times']) if self.performance_metrics['search_times'] else 0,
                'total_ingestions': len(self.performance_metrics['ingestion_times']),
                'total_searches': len(self.performance_metrics['search_times'])
            },
            'graph_statistics': {
                'current_graph_size': self.performance_metrics['graph_sizes'][-1] if self.performance_metrics['graph_sizes'] else None,
                'total_graph_operations': len(self.performance_metrics['graph_sizes'])
            }
        }
        
        # Test Neo4j connectivity if available
        if self.neo4j_manager:
            try:
                with self.neo4j_manager.driver.session() as session:
                    result = session.run("MATCH (n) RETURN count(n) as node_count")
                    node_count = result.single()['node_count']
                    
                    result = session.run("MATCH ()-[r]->() RETURN count(r) as relationship_count")
                    relationship_count = result.single()['relationship_count']
                    
                    status['neo4j_status'] = {
                        'connected': True,
                        'node_count': node_count,
                        'relationship_count': relationship_count
                    }
            except Exception as e:
                status['neo4j_status'] = {
                    'connected': False,
                    'error': str(e)
                }
        
        return status
    
    def _convert_noderag_for_storage(self, noderag_result: Dict) -> tuple[Dict, List[Dict]]:
        """Convert NodeRAG nodes to format compatible with Neo4j storage."""
        
        entities = {}
        relationships = []
        
        # Convert heterogeneous nodes to entities
        for node_id, node_data in noderag_result['heterogeneous_nodes'].items():
            if hasattr(node_data, 'canonical'):
                # NodeRAGNode object
                entities[node_data.canonical] = {
                    'type': node_data.node_type.value if hasattr(node_data.node_type, 'value') else str(node_data.node_type),
                    'confidence': node_data.confidence,
                    'text_variants': [node_data.canonical],
                    'context': node_data.content[:500],
                    'extraction_method': 'noderag',
                    'node_metadata': node_data.metadata
                }
                
                # Create relationships from connections
                for connection in node_data.connections:
                    relationships.append({
                        'subject': node_data.canonical,
                        'predicate': 'connected_to',
                        'object': connection,
                        'confidence': 0.8,
                        'extraction_method': 'noderag_connection'
                    })
            
            elif isinstance(node_data, dict):
                # Dictionary representation
                canonical = node_data.get('canonical', node_id)
                entities[canonical] = {
                    'type': node_data.get('type', 'UNKNOWN'),
                    'confidence': node_data.get('confidence', 0.7),
                    'text_variants': node_data.get('text_variants', [canonical]),
                    'context': str(node_data.get('content', ''))[:500],
                    'extraction_method': 'noderag'
                }
        
        return entities, relationships
    
    def _graph_only_search(self, query: str, config: Dict) -> Dict[str, Any]:
        """Perform graph-only search using Neo4j."""
        
        # Extract entities from query
        query_entities = self._extract_entities_from_query(query)
        
        if not query_entities:
            return {'error': 'No entities found in query for graph search'}
        
        # Use graph traversal engine
        if hasattr(self, 'hybrid_rag') and self.hybrid_rag:
            traversal_results = self.hybrid_rag.graph_traversal.multi_hop_retrieval(
                query, query_entities, {
                    'max_hops': config.get('max_hops', 3),
                    'max_paths': config.get('max_results', 10)
                }
            )
            
            return {
                'search_type': 'graph_only',
                'results': traversal_results,
                'query': query
            }
        
        return {'error': 'Graph traversal engine not available'}
    
    def _vector_only_search(self, query: str, config: Dict) -> Dict[str, Any]:
        """Perform vector-only search."""
        
        vector_store = self.config.get('vector_store')
        if not vector_store:
            return {'error': 'Vector store not configured'}
        
        try:
            results = vector_store.similarity_search(
                query, k=config.get('max_results', 10)
            )
            
            vector_results = []
            for doc in results:
                vector_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata
                })
            
            return {
                'search_type': 'vector_only',
                'results': vector_results,
                'query': query
            }
            
        except Exception as e:
            return {'error': f'Vector search failed: {str(e)}'}
    
    def _extract_entities_from_query(self, query: str) -> List[str]:
        """Extract entities from query for graph search."""
        
        # Simple entity extraction - could be enhanced
        import re
        
        # Extract capitalized words that might be entities
        potential_entities = re.findall(r'\b[A-Z][a-zA-Z]+\b', query)
        
        # Verify entities exist in graph
        if self.neo4j_manager:
            verified_entities = []
            with self.neo4j_manager.driver.session() as session:
                for entity in potential_entities:
                    result = session.run(
                        "MATCH (e:Entity {canonical: $canonical}) RETURN e.canonical",
                        canonical=entity
                    )
                    if result.single():
                        verified_entities.append(entity)
            
            return verified_entities
        
        return potential_entities[:5]  # Limit to prevent excessive processing
    
    def _get_enabled_components(self) -> List[str]:
        """Get list of enabled components."""
        
        components = []
        
        if self.kg_extractor:
            components.append('traditional_graphrag')
        
        if self.noderag_extractor:
            components.append('noderag')
        
        if self.code_analyzer:
            components.append('code_graphrag')
        
        if self.neo4j_manager:
            components.append('neo4j_storage')
        
        if self.hybrid_rag:
            components.append('hybrid_search')
        
        return components
    
    def close(self):
        """Clean up resources."""
        
        if self.neo4j_manager:
            self.neo4j_manager.close()
        
        print("🔒 Production GraphRAG system closed")


def create_production_config(
    llm_model,
    embedding_model,
    vector_store,
    neo4j_uri: str = None,
    neo4j_user: str = None,
    neo4j_password: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Create production configuration for GraphRAG system."""
    
    config = {
        'llm_model': llm_model,
        'embedding_model': embedding_model,
        'vector_store': vector_store,
        
        # Neo4j configuration
        'neo4j_uri': neo4j_uri,
        'neo4j_user': neo4j_user,
        'neo4j_password': neo4j_password,
        
        # Component enablement
        'enable_noderag': kwargs.get('enable_noderag', True),
        'enable_code_analysis': kwargs.get('enable_code_analysis', True),
        
        # Language support
        'languages': kwargs.get('languages', ['python', 'javascript', 'typescript']),
        'spacy_model': kwargs.get('spacy_model', 'en_core_web_lg'),
        
        # Performance settings
        'batch_size': kwargs.get('batch_size', 1000),
        'max_concurrent_requests': kwargs.get('max_concurrent_requests', 10),
        
        # Quality settings
        'confidence_threshold': kwargs.get('confidence_threshold', 0.6),
        'similarity_threshold': kwargs.get('similarity_threshold', 0.7),
        
        # Search settings
        'default_search_type': kwargs.get('default_search_type', 'hybrid'),
        'max_search_results': kwargs.get('max_search_results', 10)
    }
    
    return config