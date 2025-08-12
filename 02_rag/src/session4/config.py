"""
Session 4 Configuration

Configuration settings for query enhancement and context augmentation components.
"""

from typing import Dict, Any, List
import os
from dataclasses import dataclass


@dataclass
class HyDEConfig:
    """Configuration for HyDE query enhancement."""
    temperature: float = 0.7
    num_hypotheticals: int = 3
    default_query_type: str = 'factual'
    templates: Dict[str, str] = None


@dataclass
class QueryExpansionConfig:
    """Configuration for query expansion."""
    max_expansions: int = 5
    default_strategies: List[str] = None
    use_domain_corpus: bool = True
    tfidf_max_features: int = 10000
    
    def __post_init__(self):
        if self.default_strategies is None:
            self.default_strategies = ['semantic', 'contextual']


@dataclass
class MultiQueryConfig:
    """Configuration for multi-query generation."""
    total_queries: int = 8
    default_perspectives: List[str] = None
    
    def __post_init__(self):
        if self.default_perspectives is None:
            self.default_perspectives = ['decomposition', 'specificity_levels', 'perspective_shifts']


@dataclass
class ContextOptimizationConfig:
    """Configuration for context window optimization."""
    max_context_tokens: int = 4000
    default_strategy: str = 'relevance_ranking'
    token_buffer: int = 200
    max_summary_length: int = 500


@dataclass
class PromptEngineeringConfig:
    """Configuration for prompt engineering."""
    default_query_type: str = 'factual_qa'
    default_optimizations: List[str] = None
    
    def __post_init__(self):
        if self.default_optimizations is None:
            self.default_optimizations = ['confidence_calibration']


@dataclass
class Session4Config:
    """Main configuration for Session 4 components."""
    
    # API Configuration
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    anthropic_api_key: str = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Model Configuration
    embedding_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
    llm_model_name: str = 'gpt-3.5-turbo'
    tokenizer_model: str = 'gpt-3.5-turbo'
    
    # Component Configurations
    hyde_config: HyDEConfig = None
    expansion_config: QueryExpansionConfig = None
    multi_query_config: MultiQueryConfig = None
    context_config: ContextOptimizationConfig = None
    prompt_config: PromptEngineeringConfig = None
    
    # Enhancement Pipeline Configuration
    enhancement_pipeline: Dict[str, bool] = None
    
    def __post_init__(self):
        # Initialize sub-configurations if not provided
        if self.hyde_config is None:
            self.hyde_config = HyDEConfig()
        
        if self.expansion_config is None:
            self.expansion_config = QueryExpansionConfig()
        
        if self.multi_query_config is None:
            self.multi_query_config = MultiQueryConfig()
        
        if self.context_config is None:
            self.context_config = ContextOptimizationConfig()
        
        if self.prompt_config is None:
            self.prompt_config = PromptEngineeringConfig()
        
        if self.enhancement_pipeline is None:
            self.enhancement_pipeline = {
                'use_hyde': True,
                'use_expansion': True,
                'use_multi_query': True,
                'use_context_optimization': True,
                'use_prompt_engineering': True
            }
    
    def validate_config(self) -> bool:
        """Validate the configuration settings."""
        
        # Check API keys
        if not self.openai_api_key and 'gpt' in self.llm_model_name.lower():
            print("Warning: OpenAI API key not found but GPT model specified")
            return False
        
        if not self.anthropic_api_key and 'claude' in self.llm_model_name.lower():
            print("Warning: Anthropic API key not found but Claude model specified")
            return False
        
        # Validate token limits
        if self.context_config.max_context_tokens <= 0:
            print("Error: max_context_tokens must be positive")
            return False
        
        # Validate enhancement counts
        if self.hyde_config.num_hypotheticals <= 0:
            print("Error: num_hypotheticals must be positive")
            return False
        
        if self.expansion_config.max_expansions <= 0:
            print("Error: max_expansions must be positive")
            return False
        
        return True
    
    def get_enhancement_config(self) -> Dict[str, Any]:
        """Get configuration dictionary for enhancement pipeline."""
        
        return {
            'use_hyde': self.enhancement_pipeline['use_hyde'],
            'use_expansion': self.enhancement_pipeline['use_expansion'],
            'use_multi_query': self.enhancement_pipeline['use_multi_query'],
            'k': 10,  # Number of results to retrieve per query
            'hyde_config': {
                'temperature': self.hyde_config.temperature,
                'num_hypotheticals': self.hyde_config.num_hypotheticals,
                'query_type': self.hyde_config.default_query_type
            },
            'expansion_config': {
                'strategies': self.expansion_config.default_strategies,
                'max_expansions': self.expansion_config.max_expansions
            },
            'multi_query_config': {
                'total_queries': self.multi_query_config.total_queries,
                'perspectives': self.multi_query_config.default_perspectives
            },
            'context_config': {
                'max_tokens': self.context_config.max_context_tokens,
                'strategy': self.context_config.default_strategy
            },
            'prompt_config': {
                'query_type': self.prompt_config.default_query_type,
                'optimizations': self.prompt_config.default_optimizations
            }
        }


# Default configuration instance
default_config = Session4Config()


# Environment-specific configurations
def get_development_config() -> Session4Config:
    """Get configuration optimized for development."""
    config = Session4Config()
    
    # Reduce resource usage for development
    config.hyde_config.num_hypotheticals = 2
    config.expansion_config.max_expansions = 3
    config.multi_query_config.total_queries = 4
    config.context_config.max_context_tokens = 2000
    
    return config


def get_production_config() -> Session4Config:
    """Get configuration optimized for production."""
    config = Session4Config()
    
    # Optimize for production performance
    config.hyde_config.num_hypotheticals = 3
    config.expansion_config.max_expansions = 5
    config.multi_query_config.total_queries = 8
    config.context_config.max_context_tokens = 4000
    
    # Use more robust models in production
    config.llm_model_name = 'gpt-4'
    config.embedding_model_name = 'sentence-transformers/all-mpnet-base-v2'
    
    return config


def get_lightweight_config() -> Session4Config:
    """Get configuration for resource-constrained environments."""
    config = Session4Config()
    
    # Minimal resource usage
    config.hyde_config.num_hypotheticals = 1
    config.expansion_config.max_expansions = 2
    config.multi_query_config.total_queries = 3
    config.context_config.max_context_tokens = 1000
    
    # Disable some features to reduce load
    config.enhancement_pipeline['use_multi_query'] = False
    
    return config