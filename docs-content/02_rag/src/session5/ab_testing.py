# A/B testing framework for RAG systems
import time
import numpy as np
from typing import Dict, List, Any
from collections import defaultdict

class RAGABTestFramework:
    """A/B testing framework for RAG system optimization."""
    
    def __init__(self, evaluation_framework):
        self.evaluation_framework = evaluation_framework
        self.active_tests = {}
        self.test_history = []
        
    def setup_ab_test(self, test_name: str, 
                     component_variants: Dict[str, Any],
                     test_dataset: List[Dict],
                     test_config: Dict) -> Dict[str, Any]:
        """Setup A/B test for RAG component comparison."""
        
        test_setup = {
            'test_name': test_name,
            'variants': component_variants,
            'dataset': test_dataset,
            'config': test_config,
            'start_time': time.time(),
            'status': 'setup'
        }
        
        # Validate test setup
        validation_result = self._validate_test_setup(test_setup)
        if not validation_result['valid']:
            raise ValueError(f"Invalid test setup: {validation_result['errors']}")
        
        self.active_tests[test_name] = test_setup
        
        print(f"A/B test '{test_name}' setup complete with {len(component_variants)} variants")
        return test_setup
    
    def run_ab_test(self, test_name: str) -> Dict[str, Any]:
        """Execute A/B test and collect results."""
        
        if test_name not in self.active_tests:
            raise ValueError(f"Test '{test_name}' not found in active tests")
        
        test_setup = self.active_tests[test_name]
        test_setup['status'] = 'running'
        
        print(f"Running A/B test: {test_name}")
        
        variant_results = {}
        
        # Test each variant
        for variant_name, variant_config in test_setup['variants'].items():
            print(f"  Testing variant: {variant_name}")
            
            # Create RAG system with variant configuration
            rag_system = self._create_rag_variant(variant_config)
            
            # Evaluate variant
            variant_result = self.evaluation_framework.evaluate_rag_system(
                test_setup['dataset'], 
                rag_system, 
                test_setup['config']
            )
            
            variant_results[variant_name] = variant_result
        
        # Analyze results
        analysis_result = self._analyze_ab_results(variant_results, test_setup)
        
        # Complete test
        test_result = {
            'test_name': test_name,
            'test_setup': test_setup,
            'variant_results': variant_results,
            'analysis': analysis_result,
            'completion_time': time.time(),
            'duration': time.time() - test_setup['start_time']
        }
        
        # Update test status
        test_setup['status'] = 'completed'
        self.test_history.append(test_result)
        
        return test_result
    
    def _validate_test_setup(self, test_setup: Dict) -> Dict[str, Any]:
        """Validate A/B test setup configuration."""
        
        errors = []
        
        # Check required fields
        required_fields = ['test_name', 'variants', 'dataset', 'config']
        for field in required_fields:
            if field not in test_setup:
                errors.append(f"Missing required field: {field}")
        
        # Validate variants
        if 'variants' in test_setup:
            if len(test_setup['variants']) < 2:
                errors.append("At least 2 variants required for A/B testing")
            
            # Check variant configurations
            for variant_name, variant_config in test_setup['variants'].items():
                if not isinstance(variant_config, dict):
                    errors.append(f"Variant '{variant_name}' configuration must be a dictionary")
        
        # Validate dataset
        if 'dataset' in test_setup:
            if not isinstance(test_setup['dataset'], list) or len(test_setup['dataset']) == 0:
                errors.append("Dataset must be a non-empty list")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _create_rag_variant(self, variant_config: Dict):
        """Create RAG system instance with variant configuration."""
        
        # Placeholder implementation - would create actual RAG system
        # based on variant configuration
        class MockRAGSystem:
            def __init__(self, config):
                self.config = config
            
            def query(self, question: str):
                return {
                    'answer': f"Answer from variant with config: {self.config}",
                    'contexts': [],
                    'metadata': self.config
                }
        
        return MockRAGSystem(variant_config)
    
    def _analyze_ab_results(self, variant_results: Dict, 
                          test_setup: Dict) -> Dict[str, Any]:
        """Analyze A/B test results with statistical significance testing."""
        
        analysis = {
            'winner': None,
            'statistical_significance': {},
            'effect_sizes': {},
            'recommendations': [],
            'detailed_comparison': {}
        }
        
        # Extract key metrics for comparison
        metric_comparisons = defaultdict(dict)
        
        for variant_name, result in variant_results.items():
            for metric_name, metric_value in result['aggregate_metrics'].items():
                metric_comparisons[metric_name][variant_name] = metric_value
        
        # Perform pairwise comparisons
        variant_names = list(variant_results.keys())
        
        for metric_name, metric_data in metric_comparisons.items():
            analysis['detailed_comparison'][metric_name] = {}
            
            for i, variant_a in enumerate(variant_names):
                for variant_b in variant_names[i+1:]:
                    
                    score_a = metric_data[variant_a]
                    score_b = metric_data[variant_b]
                    
                    # Calculate effect size (Cohen's d approximation)
                    effect_size = abs(score_a - score_b) / max(
                        np.std([score_a, score_b]), 0.01
                    )
                    
                    # Simple significance test (would need individual scores for proper test)
                    difference = abs(score_a - score_b)
                    is_significant = difference > 0.05  # Simple threshold
                    
                    comparison_key = f"{variant_a}_vs_{variant_b}"
                    analysis['detailed_comparison'][metric_name][comparison_key] = {
                        'variant_a_score': score_a,
                        'variant_b_score': score_b,
                        'difference': score_a - score_b,
                        'effect_size': effect_size,
                        'is_significant': is_significant,
                        'better_variant': variant_a if score_a > score_b else variant_b
                    }
        
        # Determine overall winner
        analysis['winner'] = self._determine_overall_winner(
            variant_results, analysis['detailed_comparison']
        )
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_test_recommendations(analysis)
        
        return analysis
    
    def _determine_overall_winner(self, variant_results: Dict, 
                                detailed_comparison: Dict) -> str:
        """Determine overall winner across all metrics."""
        
        variant_names = list(variant_results.keys())
        
        # Simple scoring: count wins across metrics
        win_counts = {variant: 0 for variant in variant_names}
        
        for metric_name, comparisons in detailed_comparison.items():
            for comparison_key, comparison_data in comparisons.items():
                if comparison_data['is_significant']:
                    winner = comparison_data['better_variant']
                    win_counts[winner] += 1
        
        # Return variant with most wins
        if any(count > 0 for count in win_counts.values()):
            return max(win_counts.items(), key=lambda x: x[1])[0]
        else:
            return "No significant winner"
    
    def _generate_test_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on test results."""
        
        recommendations = []
        
        if analysis['winner'] and analysis['winner'] != "No significant winner":
            recommendations.append(f"Deploy variant '{analysis['winner']}' as it shows best overall performance")
        else:
            recommendations.append("No clear winner - consider running longer test or different variants")
        
        # Check for metrics with large effect sizes
        for metric_name, comparisons in analysis['detailed_comparison'].items():
            for comparison_key, data in comparisons.items():
                if data['effect_size'] > 0.8:  # Large effect size
                    recommendations.append(
                        f"Large effect size detected for {metric_name} in {comparison_key} - "
                        f"investigate '{data['better_variant']}' configuration"
                    )
        
        return recommendations
    
    def get_test_summary(self, test_name: str) -> Dict[str, Any]:
        """Get summary of completed A/B test."""
        
        # Find test in history
        test_result = None
        for test in self.test_history:
            if test['test_name'] == test_name:
                test_result = test
                break
        
        if not test_result:
            return {'error': f"Test '{test_name}' not found in history"}
        
        summary = {
            'test_name': test_name,
            'duration': test_result['duration'],
            'variants_tested': len(test_result['variant_results']),
            'winner': test_result['analysis']['winner'],
            'key_findings': test_result['analysis']['recommendations'],
            'dataset_size': len(test_result['test_setup']['dataset'])
        }
        
        return summary


# Multi-armed bandit for RAG optimization
class RAGMultiArmedBandit:
    """Multi-armed bandit for adaptive RAG system optimization."""
    
    def __init__(self, variants: List[str], exploration_rate: float = 0.1):
        self.variants = variants
        self.exploration_rate = exploration_rate
        
        # Initialize bandit arms
        self.arm_counts = {variant: 0 for variant in variants}
        self.arm_rewards = {variant: 0.0 for variant in variants}
        self.arm_avg_rewards = {variant: 0.0 for variant in variants}
        
        self.total_trials = 0
        self.trial_history = []
    
    def select_variant(self) -> str:
        """Select variant using epsilon-greedy strategy."""
        
        # Exploration: random selection
        if np.random.random() < self.exploration_rate:
            selected_variant = np.random.choice(self.variants)
            selection_reason = "exploration"
        else:
            # Exploitation: select best performing variant
            if self.total_trials == 0:
                selected_variant = np.random.choice(self.variants)
                selection_reason = "random_initial"
            else:
                best_variant = max(self.arm_avg_rewards.items(), key=lambda x: x[1])[0]
                selected_variant = best_variant
                selection_reason = "exploitation"
        
        return selected_variant
    
    def update_reward(self, variant: str, reward: float):
        """Update reward for selected variant."""
        
        self.arm_counts[variant] += 1
        self.arm_rewards[variant] += reward
        self.arm_avg_rewards[variant] = self.arm_rewards[variant] / self.arm_counts[variant]
        
        self.total_trials += 1
        
        # Record trial
        self.trial_history.append({
            'trial': self.total_trials,
            'variant': variant,
            'reward': reward,
            'avg_reward': self.arm_avg_rewards[variant],
            'timestamp': time.time()
        })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary."""
        
        return {
            'total_trials': self.total_trials,
            'variant_performance': {
                variant: {
                    'trials': self.arm_counts[variant],
                    'total_reward': self.arm_rewards[variant],
                    'average_reward': self.arm_avg_rewards[variant],
                    'selection_rate': self.arm_counts[variant] / max(self.total_trials, 1)
                }
                for variant in self.variants
            },
            'best_variant': max(self.arm_avg_rewards.items(), key=lambda x: x[1])[0] if self.total_trials > 0 else None,
            'exploration_rate': self.exploration_rate
        }
    
    def update_exploration_rate(self, new_rate: float):
        """Update exploration rate."""
        
        self.exploration_rate = max(0.0, min(1.0, new_rate))
    
    def reset_bandit(self):
        """Reset bandit to initial state."""
        
        self.arm_counts = {variant: 0 for variant in self.variants}
        self.arm_rewards = {variant: 0.0 for variant in self.variants}
        self.arm_avg_rewards = {variant: 0.0 for variant in self.variants}
        self.total_trials = 0
        self.trial_history = []
