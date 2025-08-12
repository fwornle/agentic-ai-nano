# Automated benchmark testing system
import time
import numpy as np
from typing import Dict, List, Any
from collections import defaultdict

class AutomatedRAGBenchmark:
    """Automated benchmark testing for RAG systems."""
    
    def __init__(self, evaluation_framework, test_datasets: Dict[str, List]):
        self.evaluation_framework = evaluation_framework
        self.test_datasets = test_datasets
        self.benchmark_history = []
        
    def run_comprehensive_benchmark(self, rag_system,
                                   benchmark_config: Dict) -> Dict[str, Any]:
        """Run comprehensive benchmark across multiple test datasets."""
        
        benchmark_results = {
            'timestamp': time.time(),
            'config': benchmark_config,
            'dataset_results': {},
            'aggregate_performance': {}
        }
        
        print("Starting comprehensive RAG benchmark...")
        
        # Run evaluation on each test dataset
        for dataset_name, dataset in self.test_datasets.items():
            print(f"\nEvaluating on {dataset_name} dataset ({len(dataset)} examples)")
            
            dataset_result = self.evaluation_framework.evaluate_rag_system(
                dataset, rag_system, benchmark_config
            )
            
            benchmark_results['dataset_results'][dataset_name] = dataset_result
            
            # Extract key metrics for aggregation
            self._extract_key_metrics(dataset_name, dataset_result, benchmark_results)
        
        # Calculate cross-dataset aggregates
        benchmark_results['aggregate_performance'] = self._calculate_aggregate_performance(
            benchmark_results['dataset_results']
        )
        
        # Store in benchmark history
        self.benchmark_history.append(benchmark_results)
        
        # Generate performance report
        performance_report = self._generate_performance_report(benchmark_results)
        benchmark_results['performance_report'] = performance_report
        
        return benchmark_results
    
    def _extract_key_metrics(self, dataset_name: str, dataset_result: Dict, 
                           benchmark_results: Dict):
        """Extract key metrics from dataset evaluation results."""
        
        # Initialize aggregate performance structure
        if 'key_metrics' not in benchmark_results:
            benchmark_results['key_metrics'] = defaultdict(list)
        
        # Extract aggregate metrics if available
        if 'aggregate_metrics' in dataset_result:
            for metric_name, metric_value in dataset_result['aggregate_metrics'].items():
                benchmark_results['key_metrics'][metric_name].append({
                    'dataset': dataset_name,
                    'value': metric_value
                })
    
    def _calculate_aggregate_performance(self, dataset_results: Dict) -> Dict[str, Any]:
        """Calculate aggregate performance across all datasets."""
        
        aggregate_metrics = {}
        
        # Collect all metrics across datasets
        all_metrics = defaultdict(list)
        
        for dataset_name, result in dataset_results.items():
            if 'aggregate_metrics' in result:
                for metric_name, metric_value in result['aggregate_metrics'].items():
                    if isinstance(metric_value, (int, float)):
                        all_metrics[metric_name].append(metric_value)
        
        # Calculate aggregate statistics
        for metric_name, values in all_metrics.items():
            if values:
                aggregate_metrics[metric_name] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'median': np.median(values)
                }
        
        return aggregate_metrics
    
    def _generate_performance_report(self, benchmark_results: Dict) -> str:
        """Generate human-readable performance report."""
        
        report_lines = []
        report_lines.append("RAG System Benchmark Report")
        report_lines.append("=" * 40)
        report_lines.append(f"Timestamp: {time.ctime(benchmark_results['timestamp'])}")
        report_lines.append(f"Datasets Evaluated: {len(benchmark_results['dataset_results'])}")
        report_lines.append("")
        
        # Dataset-level results
        report_lines.append("Dataset Performance:")
        report_lines.append("-" * 20)
        
        for dataset_name, result in benchmark_results['dataset_results'].items():
            report_lines.append(f"\n{dataset_name}:")
            report_lines.append(f"  Examples: {result.get('dataset_size', 'N/A')}")
            
            if 'aggregate_metrics' in result:
                for metric, value in result['aggregate_metrics'].items():
                    if isinstance(value, float):
                        report_lines.append(f"  {metric}: {value:.3f}")
                    else:
                        report_lines.append(f"  {metric}: {value}")
        
        # Aggregate performance
        if 'aggregate_performance' in benchmark_results:
            report_lines.append("\n\nAggregate Performance:")
            report_lines.append("-" * 22)
            
            for metric, stats in benchmark_results['aggregate_performance'].items():
                report_lines.append(f"\n{metric}:")
                report_lines.append(f"  Mean: {stats['mean']:.3f}")
                report_lines.append(f"  Std:  {stats['std']:.3f}")
                report_lines.append(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}]")
        
        return "\n".join(report_lines)
    
    def detect_performance_regression(self, current_results: Dict,
                                    threshold: float = 0.05) -> Dict[str, Any]:
        """Detect performance regression compared to previous benchmarks."""
        
        if len(self.benchmark_history) < 2:
            return {'regression_detected': False, 'message': 'Insufficient history for comparison'}
        
        previous_results = self.benchmark_history[-2]  # Previous benchmark
        
        regression_analysis = {
            'regression_detected': False,
            'declining_metrics': [],
            'improving_metrics': [],
            'stable_metrics': [],
            'overall_change': 0.0
        }
        
        # Compare key metrics across datasets
        for dataset_name in current_results['dataset_results']:
            if dataset_name in previous_results['dataset_results']:
                current_metrics = current_results['dataset_results'][dataset_name]['aggregate_metrics']
                previous_metrics = previous_results['dataset_results'][dataset_name]['aggregate_metrics']
                
                for metric_name in current_metrics:
                    if metric_name in previous_metrics:
                        current_score = current_metrics[metric_name]
                        previous_score = previous_metrics[metric_name]
                        
                        if isinstance(current_score, (int, float)) and isinstance(previous_score, (int, float)):
                            change = current_score - previous_score
                            
                            if change < -threshold:  # Significant decline
                                regression_analysis['declining_metrics'].append({
                                    'dataset': dataset_name,
                                    'metric': metric_name,
                                    'change': change,
                                    'current': current_score,
                                    'previous': previous_score
                                })
                                regression_analysis['regression_detected'] = True
                            elif change > threshold:  # Significant improvement
                                regression_analysis['improving_metrics'].append({
                                    'dataset': dataset_name,
                                    'metric': metric_name,
                                    'change': change,
                                    'current': current_score,
                                    'previous': previous_score
                                })
                            else:  # Stable performance
                                regression_analysis['stable_metrics'].append({
                                    'dataset': dataset_name,
                                    'metric': metric_name,
                                    'change': change
                                })
        
        # Calculate overall performance change
        if regression_analysis['declining_metrics'] or regression_analysis['improving_metrics']:
            all_changes = [m['change'] for m in regression_analysis['declining_metrics']] + \
                         [m['change'] for m in regression_analysis['improving_metrics']]
            regression_analysis['overall_change'] = np.mean(all_changes)
        
        return regression_analysis
    
    def get_benchmark_history_summary(self) -> Dict[str, Any]:
        """Get summary of benchmark history."""
        
        if not self.benchmark_history:
            return {'message': 'No benchmark history available'}
        
        summary = {
            'total_benchmarks': len(self.benchmark_history),
            'date_range': {
                'first': time.ctime(self.benchmark_history[0]['timestamp']),
                'latest': time.ctime(self.benchmark_history[-1]['timestamp'])
            },
            'performance_trends': self._analyze_performance_trends()
        }
        
        return summary
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends across benchmark history."""
        
        if len(self.benchmark_history) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        # Extract performance metrics over time
        trends = defaultdict(list)
        timestamps = []
        
        for benchmark in self.benchmark_history:
            timestamps.append(benchmark['timestamp'])
            
            # Collect aggregate metrics
            if 'aggregate_performance' in benchmark:
                for metric_name, stats in benchmark['aggregate_performance'].items():
                    if 'mean' in stats:
                        trends[metric_name].append(stats['mean'])
        
        # Analyze trends
        trend_analysis = {}
        for metric_name, values in trends.items():
            if len(values) >= 2:
                # Simple linear trend
                x = np.arange(len(values))
                slope, intercept = np.polyfit(x, values, 1)
                
                trend_analysis[metric_name] = {
                    'slope': slope,
                    'trend': 'improving' if slope > 0 else 'declining' if slope < 0 else 'stable',
                    'latest_value': values[-1],
                    'change_from_first': values[-1] - values[0]
                }
        
        return trend_analysis
    
    def export_benchmark_results(self, filepath: str, format: str = 'json') -> bool:
        """Export benchmark results to file."""
        
        try:
            import json
            
            if format.lower() == 'json':
                with open(filepath, 'w') as f:
                    json.dump(self.benchmark_history, f, indent=2, default=str)
                return True
            else:
                print(f"Unsupported export format: {format}")
                return False
                
        except Exception as e:
            print(f"Error exporting benchmark results: {e}")
            return False
