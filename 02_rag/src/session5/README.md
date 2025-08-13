# Session 5: RAG Evaluation & Quality Assessment Framework

A comprehensive framework for evaluating, testing, and monitoring RAG (Retrieval-Augmented Generation) systems in production environments.

## 🎯 Overview

This package provides enterprise-grade tools for:

- **Multi-dimensional RAG evaluation** (retrieval, generation, end-to-end)
- **RAGAS integration** for standardized metrics
- **Custom evaluation metrics** for specialized use cases
- **Automated benchmark testing** with regression detection
- **A/B testing framework** for component optimization
- **Production monitoring** with real-time quality assessment
- **Alerting system** for quality degradation and anomalies

## 📁 Package Structure

```
session5/
├── __init__.py                 # Package exports and initialization
├── config.py                   # Configuration management
├── evaluation_framework.py     # Core evaluation framework
├── ragas_evaluator.py         # RAGAS integration
├── custom_metrics.py          # Custom evaluation metrics
├── retrieval_evaluator.py     # Specialized retrieval evaluation
├── llm_judge_evaluator.py     # LLM-as-a-judge evaluation
├── benchmark_system.py        # Automated benchmarking
├── ab_testing.py              # A/B testing and multi-armed bandits
├── production_monitor.py      # Production monitoring
├── alerting_system.py         # Alert management
├── evaluation_ecosystem.py    # Complete evaluation system
├── demo_evaluation_system.py  # Demonstration script
├── requirements.txt           # Package dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### Installation

1. Install dependencies:
```bash
cd session5
pip install -r requirements.txt
```

2. Set up environment variables (optional):
```bash
export ENVIRONMENT=development  # or staging, production
export LLM_JUDGE_MODEL=gpt-4
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Basic Usage

```python
from session5 import create_evaluation_system

# Initialize with your models
evaluation_system = create_evaluation_system(
    llm_judge=your_llm_judge,
    embedding_model=your_embedding_model,
    environment='development'
)

# Run comprehensive evaluation
results = evaluation_system.run_comprehensive_evaluation(
    rag_system=your_rag_system,
    evaluation_suite='full'
)

print(f"Overall quality score: {results['overall_score']}")
```

### Quick Evaluation

```python
from session5 import quick_evaluate

# Quick evaluation on test queries
test_queries = [
    "What is machine learning?",
    "How do neural networks work?",
    "What is the difference between AI and ML?"
]

results = quick_evaluate(
    rag_system=your_rag_system,
    test_queries=test_queries,
    llm_judge=your_llm_judge,
    embedding_model=your_embedding_model
)
```

## 🏗️ Architecture

### Core Components

#### 1. Evaluation Framework

- Multi-dimensional assessment (retrieval, generation, end-to-end)
- Pluggable evaluator architecture
- Comprehensive metric registry

#### 2. RAGAS Integration

- Standardized evaluation metrics
- Faithfulness, relevancy, precision, recall
- Ground truth comparison

#### 3. Custom Metrics

- Answer completeness assessment
- Citation quality evaluation
- Domain-specific accuracy
- Coherence and depth analysis

#### 4. A/B Testing

- Component variant comparison
- Statistical significance testing
- Multi-armed bandit optimization

#### 5. Production Monitoring

- Real-time quality assessment
- Performance tracking
- Anomaly detection
- Alert management

## 📊 Evaluation Metrics

### Retrieval Quality

- **Semantic Relevance**: Context-query similarity
- **Context Diversity**: Information variety
- **Precision@K**: Relevant documents in top-K
- **Recall@K**: Coverage of relevant documents
- **NDCG**: Normalized discounted cumulative gain

### Generation Quality

- **Faithfulness**: Factual consistency with context
- **Answer Relevancy**: Response relevance to query
- **Completeness**: Comprehensive answer coverage
- **Coherence**: Logical flow and structure
- **Citation Quality**: Source attribution accuracy

### End-to-End Performance

- **Overall Quality**: Weighted combination score
- **User Satisfaction**: Task completion rate
- **Response Time**: System latency
- **Throughput**: Requests per second

## 🧪 Testing and Benchmarking

### Automated Benchmarking

```python
from session5 import AutomatedRAGBenchmark

# Create benchmark system
benchmark = AutomatedRAGBenchmark(
    evaluation_framework=your_framework,
    test_datasets=your_test_datasets
)

# Run comprehensive benchmark
results = benchmark.run_comprehensive_benchmark(
    rag_system=your_system,
    benchmark_config={'include_ragas': True}
)

# Detect performance regression
regression_analysis = benchmark.detect_performance_regression(
    current_results=results,
    threshold=0.05
)
```

### A/B Testing

```python
from session5 import RAGABTestFramework

# Setup A/B test
ab_test = RAGABTestFramework(evaluation_framework)

variants = {
    'baseline': {'retrieval_method': 'basic'},
    'enhanced': {'retrieval_method': 'hybrid'}
}

test_setup = ab_test.setup_ab_test(
    test_name="retrieval_comparison",
    component_variants=variants,
    test_dataset=your_test_data
)

# Run test and analyze results
results = ab_test.run_ab_test("retrieval_comparison")
print(f"Winner: {results['analysis']['winner']}")
```

## 📈 Production Monitoring

### Real-time Monitoring

```python
from session5 import RAGProductionMonitor

# Initialize monitor
monitor = RAGProductionMonitor(
    evaluation_framework=your_framework,
    alert_thresholds=your_thresholds
)

# Monitor individual interactions
monitoring_result = monitor.monitor_rag_interaction(
    query="User question",
    response="RAG response",
    contexts=["Context 1", "Context 2"],
    metadata={'response_time': 2.1}
)

# Generate health report
health_report = monitor.get_system_health_report(
    time_window_hours=24
)
```

### Alert Management

```python
from session5 import RAGAlertingSystem

# Setup alerting
alerting = RAGAlertingSystem(alert_config)

# Evaluate alert conditions
alerts = alerting.evaluate_alert_conditions(monitoring_data)

# Send alerts through configured channels
for alert in alerts:
    alerting.send_alert(alert, channels=['console', 'email'])
```

## ⚙️ Configuration

### Environment Configuration

```python
from session5.config import get_config, EvaluationConfig

# Get environment-specific config
config = get_config('production')

# Custom configuration
custom_config = EvaluationConfig(
    llm_judge_model="gpt-4",
    min_quality_score=0.8,
    max_response_time=3.0,
    alert_cooldown_minutes=5
)
```

### Alert Configuration

```python
alert_config = {
    'min_quality_score': 0.6,
    'max_response_time': 5.0,
    'channels': {
        'console': {'enabled': True, 'min_severity': 'low'},
        'email': {'enabled': True, 'min_severity': 'medium'},
        'slack': {'enabled': True, 'min_severity': 'high'}
    }
}
```

## 🎮 Demo and Examples

Run the comprehensive demonstration:

```bash
cd session5
python demo_evaluation_system.py
```

The demo includes:
1. **Basic Evaluation**: Core framework demonstration
2. **RAGAS Integration**: Standardized metrics showcase
3. **A/B Testing**: Component comparison testing
4. **Production Monitoring**: Real-time quality assessment
5. **Comprehensive Ecosystem**: Full system integration

## 📋 API Reference

### Core Classes

#### RAGEvaluationFramework

Main evaluation framework for comprehensive RAG assessment.

```python
framework = RAGEvaluationFramework(llm_judge, embedding_model)
results = framework.evaluate_rag_system(test_dataset, rag_system, config)
```

#### RAGASEvaluator

RASAS integration for standardized evaluation metrics.

```python
ragas_eval = RAGASEvaluator(llm_model, embedding_model)
results = ragas_eval.evaluate_with_ragas(rag_results)
```

#### CustomRAGMetrics

Custom evaluation metrics for specialized assessments.

```python
custom_metrics = CustomRAGMetrics(llm_judge, domain_knowledge)
score = custom_metrics.evaluate_answer_completeness(query, answer, contexts)
```

#### RAGProductionMonitor

Production monitoring with real-time quality assessment.

```python
monitor = RAGProductionMonitor(framework, alert_thresholds)
result = monitor.monitor_rag_interaction(query, response, contexts, metadata)
```

## 🔧 Extending the Framework

### Custom Evaluators

```python
from session5.evaluation_framework import BaseEvaluator

class MyCustomEvaluator(BaseEvaluator):
    def evaluate(self, query, response, contexts):
        # Your custom evaluation logic
        return {'custom_score': score}

# Register with framework
framework.evaluators['my_custom'] = MyCustomEvaluator()
```

### Custom Metrics

```python
def my_custom_metric(query, response, contexts):
    # Your metric implementation
    return score

# Add to metrics registry
framework.metrics_registry['my_metric'] = my_custom_metric
```

## 🚨 Production Deployment

### Best Practices

1. **Environment Separation**: Use different configs for dev/staging/production
2. **Alert Tuning**: Start with conservative thresholds and adjust based on data
3. **Monitoring Gradual Rollout**: Begin with sampling, increase coverage gradually
4. **Baseline Establishment**: Collect baseline metrics before making changes
5. **Regular Review**: Periodically review and update evaluation criteria

### Monitoring Setup

```python
# Production monitoring initialization
monitor = RAGProductionMonitor(
    evaluation_framework=production_framework,
    alert_thresholds={
        'min_quality_score': 0.7,
        'max_response_time': 3.0,
        'min_throughput': 1.0
    }
)

# Integrate with your RAG system
def enhanced_rag_query(query):
    response = your_rag_system.query(query)

    # Monitor the interaction
    monitor.monitor_rag_interaction(
        query=query,
        response=response['answer'],
        contexts=response['contexts'],
        metadata=response['metadata']
    )

    return response
```

## 📚 Additional Resources

- **Session 5 Documentation**: Detailed evaluation methodology
- **RAGAS Documentation**: https://github.com/explodinggradients/ragas
- **Best Practices Guide**: RAG evaluation in production
- **Troubleshooting Guide**: Common issues and solutions

## 🤝 Contributing

Contributions are welcome! Please:

1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update documentation for changes
4. Ensure backward compatibility

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Next Steps**: Ready to implement GraphRAG? Check out Session 6 for graph-based RAG architectures that build upon these proven evaluation techniques!
