"""
Session 4: Query Enhancement & Context Augmentation

This module implements advanced query enhancement techniques for RAG systems,
including HyDE (Hypothetical Document Embeddings), query expansion, 
multi-query generation, context optimization, and prompt engineering.
"""

from .semantic_gap_analyzer import SemanticGapAnalyzer
from .hyde_enhancer import HyDEQueryEnhancer
from .query_expander import IntelligentQueryExpander
from .multi_query_generator import MultiQueryGenerator
from .context_optimizer import ContextWindowOptimizer
from .prompt_engineer import RAGPromptEngineer, DynamicPromptAdapter
from .comprehensive_enhancer import ComprehensiveQueryEnhancer

__all__ = [
    'SemanticGapAnalyzer',
    'HyDEQueryEnhancer', 
    'IntelligentQueryExpander',
    'MultiQueryGenerator',
    'ContextWindowOptimizer',
    'RAGPromptEngineer',
    'DynamicPromptAdapter',
    'ComprehensiveQueryEnhancer'
]