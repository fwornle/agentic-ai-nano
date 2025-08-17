# Configuration management for Session 6 GraphRAG
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GraphRAGConfig:
    """Configuration class for GraphRAG systems."""
    
    # LLM Configuration
    llm_model_name: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2000
    
    # Embedding Configuration
    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    
    # GraphRAG Configuration
    enable_traditional_graphrag: bool = True
    enable_noderag: bool = True
    enable_code_graphrag: bool = True
    enable_hybrid_search: bool = True
    
    # Entity Extraction Configuration
    entity_confidence_threshold: float = 0.6
    relationship_confidence_threshold: float = 0.7
    similarity_threshold: float = 0.75
    enable_entity_merging: bool = True
    
    # Graph Traversal Configuration
    max_traversal_hops: int = 3
    max_paths_per_query: int = 50
    semantic_filter_threshold: float = 0.7
    
    # NodeRAG Configuration
    noderag_node_types: list = None
    enable_pagerank: bool = True
    enable_hnsw_similarity: bool = True
    reasoning_integration: bool = True
    max_pathway_depth: int = 5
    
    # Code Analysis Configuration
    supported_languages: list = None
    max_files_per_analysis: int = 1000
    code_include_patterns: list = None
    code_exclude_patterns: list = None
    
    # Performance Configuration
    batch_size: int = 1000
    max_concurrent_requests: int = 10
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __post_init__(self):
        """Set default values for list fields."""
        if self.noderag_node_types is None:
            self.noderag_node_types = ['entity', 'concept', 'document', 'relationship']
        
        if self.supported_languages is None:
            self.supported_languages = ['python', 'javascript', 'typescript']
        
        if self.code_include_patterns is None:
            self.code_include_patterns = ['*.py', '*.js', '*.ts']
        
        if self.code_exclude_patterns is None:
            self.code_exclude_patterns = ['*test*', '*__pycache__*', '*.min.js']
    
    @classmethod
    def from_env(cls) -> 'GraphRAGConfig':
        """Create configuration from environment variables."""
        
        return cls(
            # LLM Configuration
            llm_model_name=os.getenv('LLM_MODEL_NAME', 'gpt-3.5-turbo'),
            llm_temperature=float(os.getenv('LLM_TEMPERATURE', '0.1')),
            llm_max_tokens=int(os.getenv('LLM_MAX_TOKENS', '2000')),
            
            # Embedding Configuration
            embedding_model_name=os.getenv('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2'),
            embedding_dimension=int(os.getenv('EMBEDDING_DIMENSION', '384')),
            
            # Neo4j Configuration
            neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            neo4j_username=os.getenv('NEO4J_USERNAME', 'neo4j'),
            neo4j_password=os.getenv('NEO4J_PASSWORD', 'password'),
            
            # GraphRAG Configuration
            enable_traditional_graphrag=os.getenv('ENABLE_TRADITIONAL_GRAPHRAG', 'true').lower() == 'true',
            enable_noderag=os.getenv('ENABLE_NODERAG', 'true').lower() == 'true',
            enable_code_graphrag=os.getenv('ENABLE_CODE_GRAPHRAG', 'true').lower() == 'true',
            enable_hybrid_search=os.getenv('ENABLE_HYBRID_SEARCH', 'true').lower() == 'true',
            
            # Thresholds
            entity_confidence_threshold=float(os.getenv('ENTITY_CONFIDENCE_THRESHOLD', '0.6')),
            relationship_confidence_threshold=float(os.getenv('RELATIONSHIP_CONFIDENCE_THRESHOLD', '0.7')),
            similarity_threshold=float(os.getenv('SIMILARITY_THRESHOLD', '0.75')),
            
            # Performance
            batch_size=int(os.getenv('BATCH_SIZE', '1000')),
            max_concurrent_requests=int(os.getenv('MAX_CONCURRENT_REQUESTS', '10')),
            
            # Logging
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        
        return {
            'llm_config': {
                'model_name': self.llm_model_name,
                'temperature': self.llm_temperature,
                'max_tokens': self.llm_max_tokens
            },
            'embedding_config': {
                'model_name': self.embedding_model_name,
                'dimension': self.embedding_dimension
            },
            'neo4j_config': {
                'uri': self.neo4j_uri,
                'username': self.neo4j_username,
                'password': self.neo4j_password
            },
            'graphrag_config': {
                'enable_traditional': self.enable_traditional_graphrag,
                'enable_noderag': self.enable_noderag,
                'enable_code_analysis': self.enable_code_graphrag,
                'enable_hybrid_search': self.enable_hybrid_search
            },
            'extraction_config': {
                'entity_confidence_threshold': self.entity_confidence_threshold,
                'relationship_confidence_threshold': self.relationship_confidence_threshold,
                'similarity_threshold': self.similarity_threshold,
                'enable_entity_merging': self.enable_entity_merging
            },
            'traversal_config': {
                'max_hops': self.max_traversal_hops,
                'max_paths': self.max_paths_per_query,
                'semantic_threshold': self.semantic_filter_threshold
            },
            'noderag_config': {
                'node_types': self.noderag_node_types,
                'enable_pagerank': self.enable_pagerank,
                'enable_hnsw_similarity': self.enable_hnsw_similarity,
                'reasoning_integration': self.reasoning_integration,
                'max_pathway_depth': self.max_pathway_depth
            },
            'code_config': {
                'supported_languages': self.supported_languages,
                'max_files': self.max_files_per_analysis,
                'include_patterns': self.code_include_patterns,
                'exclude_patterns': self.code_exclude_patterns
            },
            'performance_config': {
                'batch_size': self.batch_size,
                'max_concurrent_requests': self.max_concurrent_requests,
                'cache_enabled': self.cache_enabled,
                'cache_ttl': self.cache_ttl
            }
        }


class ConfigManager:
    """Manages configuration for GraphRAG systems."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            Path(__file__).parent, "config", "default.json"
        )
        self._config = None
    
    def load_config(self) -> GraphRAGConfig:
        """Load configuration from file or environment."""
        
        # Try to load from environment first
        config = GraphRAGConfig.from_env()
        
        # Override with file-based config if available
        if os.path.exists(self.config_path):
            import json
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                
                # Update config with file values
                for key, value in file_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                        
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_path}: {e}")
        
        self._config = config
        return config
    
    def save_config(self, config: GraphRAGConfig, path: Optional[str] = None) -> None:
        """Save configuration to file."""
        
        save_path = path or self.config_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        import json
        with open(save_path, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
    
    @property
    def config(self) -> GraphRAGConfig:
        """Get current configuration."""
        if self._config is None:
            self._config = self.load_config()
        return self._config


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> GraphRAGConfig:
    """Get the current GraphRAG configuration."""
    return config_manager.config


def update_config(**kwargs) -> GraphRAGConfig:
    """Update configuration with new values."""
    config = config_manager.config
    
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            print(f"Warning: Unknown configuration key: {key}")
    
    return config


# Environment-specific configurations
def get_development_config() -> GraphRAGConfig:
    """Get development configuration."""
    return GraphRAGConfig(
        neo4j_uri="bolt://localhost:7687",
        neo4j_username="neo4j",
        neo4j_password="dev_password",
        log_level="DEBUG",
        batch_size=100,
        max_files_per_analysis=50,
        cache_enabled=False
    )


def get_production_config() -> GraphRAGConfig:
    """Get production configuration."""
    return GraphRAGConfig(
        neo4j_uri=os.getenv('NEO4J_URI', 'bolt://prod-neo4j:7687'),
        neo4j_username=os.getenv('NEO4J_USERNAME', 'neo4j'),
        neo4j_password=os.getenv('NEO4J_PASSWORD'),
        log_level="INFO",
        batch_size=2000,
        max_files_per_analysis=5000,
        cache_enabled=True,
        cache_ttl=7200
    )


def get_testing_config() -> GraphRAGConfig:
    """Get testing configuration."""
    return GraphRAGConfig(
        neo4j_uri="bolt://localhost:7688",  # Different port for testing
        neo4j_username="neo4j",
        neo4j_password="test_password",
        log_level="DEBUG",
        batch_size=10,
        max_files_per_analysis=5,
        entity_confidence_threshold=0.5,  # Lower threshold for testing
        cache_enabled=False
    )