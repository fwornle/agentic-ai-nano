# Configuration settings for RAG evaluation system
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class EvaluationConfig:
    """Configuration for RAG evaluation system."""
    
    # Model configurations
    llm_judge_model: str = "gpt-4"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Evaluation settings
    batch_size: int = 32
    max_contexts: int = 5
    evaluation_timeout: int = 300  # seconds
    
    # Quality thresholds
    min_quality_score: float = 0.6
    min_relevance_score: float = 0.7
    min_faithfulness_score: float = 0.8
    
    # Performance thresholds
    max_response_time: float = 5.0  # seconds
    min_throughput: float = 0.5     # requests per second
    
    # A/B testing settings
    ab_test_confidence_level: float = 0.95
    min_ab_test_samples: int = 100
    ab_test_significance_threshold: float = 0.05
    
    # Monitoring settings
    monitoring_window_hours: int = 24
    alert_cooldown_minutes: int = 15
    anomaly_detection_sensitivity: float = 2.5  # z-score threshold
    
    # File paths
    benchmark_data_path: str = "data/benchmarks/"
    results_output_path: str = "results/"
    logs_path: str = "logs/"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'llm_judge_model': self.llm_judge_model,
            'embedding_model': self.embedding_model,
            'batch_size': self.batch_size,
            'max_contexts': self.max_contexts,
            'evaluation_timeout': self.evaluation_timeout,
            'min_quality_score': self.min_quality_score,
            'min_relevance_score': self.min_relevance_score,
            'min_faithfulness_score': self.min_faithfulness_score,
            'max_response_time': self.max_response_time,
            'min_throughput': self.min_throughput,
            'ab_test_confidence_level': self.ab_test_confidence_level,
            'min_ab_test_samples': self.min_ab_test_samples,
            'ab_test_significance_threshold': self.ab_test_significance_threshold,
            'monitoring_window_hours': self.monitoring_window_hours,
            'alert_cooldown_minutes': self.alert_cooldown_minutes,
            'anomaly_detection_sensitivity': self.anomaly_detection_sensitivity,
            'benchmark_data_path': self.benchmark_data_path,
            'results_output_path': self.results_output_path,
            'logs_path': self.logs_path
        }

# Default configuration
DEFAULT_CONFIG = EvaluationConfig()

# Environment-specific configurations
ENVIRONMENT_CONFIGS = {
    'development': EvaluationConfig(
        llm_judge_model="gpt-3.5-turbo",
        batch_size=16,
        evaluation_timeout=120,
        min_quality_score=0.5,
        monitoring_window_hours=12
    ),
    
    'staging': EvaluationConfig(
        llm_judge_model="gpt-4",
        batch_size=32,
        evaluation_timeout=300,
        min_quality_score=0.6,
        monitoring_window_hours=24
    ),
    
    'production': EvaluationConfig(
        llm_judge_model="gpt-4",
        embedding_model="sentence-transformers/all-mpnet-base-v2",
        batch_size=64,
        evaluation_timeout=600,
        min_quality_score=0.7,
        min_relevance_score=0.75,
        min_faithfulness_score=0.85,
        max_response_time=3.0,
        min_throughput=1.0,
        monitoring_window_hours=24,
        alert_cooldown_minutes=5,
        anomaly_detection_sensitivity=2.0
    )
}

# Alert channel configurations
ALERT_CHANNELS = {
    'console': {
        'enabled': True,
        'min_severity': 'low'
    },
    'email': {
        'enabled': False,  # Configure SMTP settings to enable
        'min_severity': 'medium',
        'recipients': ['admin@example.com']
    },
    'slack': {
        'enabled': False,  # Configure Slack webhook to enable
        'min_severity': 'high',
        'webhook_url': os.getenv('SLACK_WEBHOOK_URL', '')
    },
    'webhook': {
        'enabled': False,
        'min_severity': 'critical',
        'url': os.getenv('ALERT_WEBHOOK_URL', ''),
        'headers': {'Content-Type': 'application/json'}
    }
}

# Test dataset configurations
TEST_DATASETS = {
    'general_qa': {
        'name': 'General QA Dataset',
        'description': 'General question-answering evaluation dataset',
        'size': 100,
        'categories': ['factual', 'reasoning', 'common_sense']
    },
    'domain_specific': {
        'name': 'Domain-Specific Dataset',
        'description': 'Domain-specific evaluation dataset',
        'size': 50,
        'categories': ['technical', 'specialized']
    },
    'adversarial': {
        'name': 'Adversarial Dataset',
        'description': 'Challenging cases and edge cases',
        'size': 25,
        'categories': ['ambiguous', 'misleading', 'complex']
    }
}

# RAGAS metric configurations
RAGAS_METRICS_CONFIG = {
    'faithfulness': {
        'enabled': True,
        'weight': 0.3,
        'description': 'Factual consistency with retrieved context'
    },
    'answer_relevancy': {
        'enabled': True,
        'weight': 0.25,
        'description': 'Relevance of answer to the question'
    },
    'context_precision': {
        'enabled': True,
        'weight': 0.2,
        'description': 'Precision of retrieved context'
    },
    'context_recall': {
        'enabled': True,
        'weight': 0.15,
        'description': 'Recall of retrieved context'
    },
    'answer_correctness': {
        'enabled': False,  # Requires ground truth
        'weight': 0.1,
        'description': 'Correctness compared to ground truth'
    }
}

# Custom metric configurations
CUSTOM_METRICS_CONFIG = {
    'answer_completeness': {
        'enabled': True,
        'weight': 0.2,
        'description': 'Completeness of the answer'
    },
    'citation_quality': {
        'enabled': True,
        'weight': 0.15,
        'description': 'Quality of source citations'
    },
    'answer_coherence': {
        'enabled': True,
        'weight': 0.15,
        'description': 'Internal coherence of the answer'
    },
    'domain_accuracy': {
        'enabled': False,  # Requires domain knowledge
        'weight': 0.1,
        'description': 'Domain-specific accuracy'
    }
}

def get_config(environment: str = None) -> EvaluationConfig:
    """Get configuration for specified environment."""
    
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'development')
    
    config = ENVIRONMENT_CONFIGS.get(environment, DEFAULT_CONFIG)
    
    # Override with environment variables if present
    if os.getenv('LLM_JUDGE_MODEL'):
        config.llm_judge_model = os.getenv('LLM_JUDGE_MODEL')
    
    if os.getenv('EMBEDDING_MODEL'):
        config.embedding_model = os.getenv('EMBEDDING_MODEL')
    
    if os.getenv('MIN_QUALITY_SCORE'):
        config.min_quality_score = float(os.getenv('MIN_QUALITY_SCORE'))
    
    if os.getenv('MAX_RESPONSE_TIME'):
        config.max_response_time = float(os.getenv('MAX_RESPONSE_TIME'))
    
    return config

def get_alert_config() -> Dict[str, Any]:
    """Get alert configuration."""
    
    config = get_config()
    
    return {
        'min_quality_score': config.min_quality_score,
        'min_relevance_score': config.min_relevance_score,
        'min_faithfulness_score': config.min_faithfulness_score,
        'max_response_time': config.max_response_time,
        'min_throughput': config.min_throughput,
        'default_channels': ['console'],
        'channels': ALERT_CHANNELS
    }

def get_test_datasets_config() -> Dict[str, List[Dict]]:
    """Get test datasets configuration."""
    
    # In production, this would load actual test datasets
    # For now, return configuration metadata
    return {
        'available_datasets': TEST_DATASETS,
        'default_datasets': ['general_qa', 'domain_specific']
    }

def validate_config(config: EvaluationConfig) -> List[str]:
    """Validate configuration and return list of issues."""
    
    issues = []
    
    # Check required fields
    if not config.llm_judge_model:
        issues.append("LLM judge model not specified")
    
    if not config.embedding_model:
        issues.append("Embedding model not specified")
    
    # Check numeric ranges
    if config.batch_size <= 0:
        issues.append("Batch size must be positive")
    
    if config.min_quality_score < 0 or config.min_quality_score > 1:
        issues.append("Quality score threshold must be between 0 and 1")
    
    if config.max_response_time <= 0:
        issues.append("Response time threshold must be positive")
    
    # Check paths
    import os
    
    for path_attr in ['benchmark_data_path', 'results_output_path', 'logs_path']:
        path = getattr(config, path_attr)
        if path and not os.path.exists(os.path.dirname(path)):
            issues.append(f"Directory for {path_attr} does not exist: {path}")
    
    return issues
