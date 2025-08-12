"""RAG Evaluation and Quality Assessment Framework.

This package provides a comprehensive framework for evaluating and monitoring
RAG (Retrieval-Augmented Generation) systems in production.

Key Components:
- Multi-dimensional evaluation (retrieval, generation, end-to-end)
- RAGAS integration for standardized metrics
- Custom evaluation metrics for specialized use cases
- Automated benchmark testing with regression detection
- A/B testing framework for component optimization
- Production monitoring with real-time quality assessment
- Alerting system for quality degradation and anomalies

Example Usage:
    ```python
    from session5 import RAGEvaluationEcosystem
    from session5.config import get_config
    
    # Initialize evaluation ecosystem
    config = get_config('production')
    ecosystem = RAGEvaluationEcosystem(
        llm_judge=your_llm_judge,
        embedding_model=your_embedding_model,
        config=config
    )
    
    # Run comprehensive evaluation
    results = ecosystem.run_comprehensive_evaluation(your_rag_system)
    ```
"""

from .evaluation_framework import RAGEvaluationFramework, RAGEvaluationResult
from .ragas_evaluator import RAGASEvaluator
from .custom_metrics import CustomRAGMetrics
from .retrieval_evaluator import RetrievalEvaluator
from .llm_judge_evaluator import LLMJudgeEvaluator
from .benchmark_system import AutomatedRAGBenchmark
from .ab_testing import RAGABTestFramework, RAGMultiArmedBandit
from .production_monitor import RAGProductionMonitor
from .alerting_system import RAGAlertingSystem
from .evaluation_ecosystem import RAGEvaluationEcosystem
from .config import (
    EvaluationConfig,
    get_config,
    get_alert_config,
    get_test_datasets_config,
    validate_config
)

__version__ = "1.0.0"
__author__ = "RAG Evaluation Team"

# Main exports
__all__ = [
    # Core evaluation framework
    'RAGEvaluationFramework',
    'RAGEvaluationResult',
    
    # Evaluators
    'RAGASEvaluator',
    'CustomRAGMetrics',
    'RetrievalEvaluator',
    'LLMJudgeEvaluator',
    
    # Testing and benchmarking
    'AutomatedRAGBenchmark',
    'RAGABTestFramework',
    'RAGMultiArmedBandit',
    
    # Production monitoring
    'RAGProductionMonitor',
    'RAGAlertingSystem',
    
    # Complete ecosystem
    'RAGEvaluationEcosystem',
    
    # Configuration
    'EvaluationConfig',
    'get_config',
    'get_alert_config',
    'get_test_datasets_config',
    'validate_config'
]

# Package metadata
__package_info__ = {
    'name': 'rag-evaluation',
    'version': __version__,
    'description': 'Comprehensive RAG evaluation and monitoring framework',
    'author': __author__,
    'license': 'MIT',
    'keywords': ['RAG', 'evaluation', 'monitoring', 'LLM', 'AI'],
    'dependencies': [
        'numpy>=1.21.0',
        'scipy>=1.7.0',
        'ragas>=0.0.20',
        'datasets>=2.10.0',
        'transformers>=4.20.0',
        'sentence-transformers>=2.2.0'
    ]
}

# Version check and compatibility
import sys

if sys.version_info < (3, 8):
    raise RuntimeError(
        "RAG Evaluation Framework requires Python 3.8 or later. "
        f"You are using Python {sys.version_info.major}.{sys.version_info.minor}."
    )

# Optional dependency warnings
try:
    import ragas
except ImportError:
    import warnings
    warnings.warn(
        "RAGAS not found. Install with 'pip install ragas' for full functionality.",
        ImportWarning
    )

try:
    import sentence_transformers
except ImportError:
    import warnings
    warnings.warn(
        "SentenceTransformers not found. Install with 'pip install sentence-transformers' "
        "for embedding-based evaluations.",
        ImportWarning
    )

# Initialize logging
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

# Set up basic configuration if no handlers are configured
if not logging.getLogger(__name__).handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Package-level functions for convenience
def create_evaluation_system(llm_judge, embedding_model, environment: str = 'development'):
    """Create a complete RAG evaluation system with default configuration.
    
    Args:
        llm_judge: LLM model for judging responses
        embedding_model: Model for generating embeddings
        environment: Environment configuration ('development', 'staging', 'production')
    
    Returns:
        RAGEvaluationEcosystem: Complete evaluation system ready to use
    """
    config = get_config(environment)
    
    # Create test datasets config
    test_datasets_config = get_test_datasets_config()
    alert_config = get_alert_config()
    
    ecosystem_config = {
        'test_datasets': {},  # Would be populated with actual datasets
        'alert_thresholds': alert_config,
        'evaluation_config': config.to_dict()
    }
    
    return RAGEvaluationEcosystem(
        llm_judge=llm_judge,
        embedding_model=embedding_model,
        config=ecosystem_config
    )

def quick_evaluate(rag_system, test_queries: list, llm_judge, embedding_model):
    """Quick evaluation of RAG system on provided test queries.
    
    Args:
        rag_system: RAG system to evaluate
        test_queries: List of test queries
        llm_judge: LLM model for judging responses
        embedding_model: Model for generating embeddings
    
    Returns:
        Dict: Evaluation results
    """
    framework = RAGEvaluationFramework(llm_judge, embedding_model)
    
    # Convert test queries to evaluation dataset format
    test_dataset = [
        {'query': query, 'expected_answer': None}
        for query in test_queries
    ]
    
    return framework.evaluate_rag_system(
        test_dataset=test_dataset,
        rag_system=rag_system,
        evaluation_config={'quick_eval': True}
    )
