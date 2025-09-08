#!/usr/bin/env python3
"""
Reflection Agent implementation matching Session 1 course content
Agent with self-monitoring for data pipeline optimization
"""

from base_agent_course import BaseAgent, CostTracker
from typing import Dict, Any
import time


class ReflectiveAgent(BaseAgent):
    """Agent with self-monitoring for data pipeline optimization"""

    def __init__(self, model_name="gpt-4"):
        super().__init__(model_name)
        self.performance_history = []
        self.cost_tracker = CostTracker()
        self.optimization_threshold = 0.8

    def reflect_on_performance(self, metrics: dict) -> dict:
        """Analyze data processing performance and optimize workflows"""
        reflection_prompt = f"""
        Analyze this data processing performance:
        - Throughput: {metrics['throughput_gb_per_hour']} GB/hour of data processed
        - Cost efficiency: ${metrics['cost_per_gb']} per GB processed
        - Error rate: {metrics['error_rate']}% across ETL pipelines
        - Queue depth: {metrics['queue_depth']} pending processing jobs
        - Average latency: {metrics['avg_latency_ms']}ms for data transformation

        Identify bottlenecks and suggest optimizations for:
        1. Kubernetes resource allocation (CPU/memory for data processing)
        2. Batch size configuration for optimal throughput
        3. Parallel processing strategy for distributed workloads
        4. Cost optimization for petabyte-scale processing requirements
        """

        optimization = self.llm_call(reflection_prompt)

        # Apply performance insights to future data processing
        self.update_processing_strategy(optimization)

        return optimization

    def llm_call(self, prompt: str) -> dict:
        """Simulate LLM call for reflection analysis"""
        # Track cost
        cost = self.cost_tracker.track_api_call(self.model_name, len(prompt) // 4)
        
        # Simulate processing time
        time.sleep(0.2)
        
        # Generate reflection insights
        insights = {
            "cost_analysis": f"Current processing cost: ${cost:.4f}",
            "performance_assessment": "Throughput within acceptable range",
            "optimization_recommendations": [
                "Consider increasing batch size for better throughput",
                "Implement parallel processing for large datasets", 
                "Use cost-effective model for routine validation tasks"
            ],
            "resource_optimization": {
                "cpu_recommendation": "Increase CPU allocation by 20%",
                "memory_recommendation": "Current memory usage is optimal",
                "scaling_strategy": "Horizontal scaling recommended for peak hours"
            }
        }
        
        return insights

    def update_processing_strategy(self, optimization: dict) -> None:
        """Apply optimization insights to processing strategy"""
        strategy_updates = {
            "timestamp": time.time(),
            "optimization_applied": optimization.get("optimization_recommendations", []),
            "resource_changes": optimization.get("resource_optimization", {}),
            "estimated_improvement": "15-25% throughput increase"
        }
        
        self.performance_history.append(strategy_updates)
        print(f"🔄 Strategy updated: {len(strategy_updates['optimization_applied'])} optimizations applied")

    def run_performance_analysis(self, current_metrics: dict) -> dict:
        """Run complete performance analysis cycle"""
        print("📊 Running performance analysis...")
        
        # Perform reflection
        reflection_result = self.reflect_on_performance(current_metrics)
        
        # Generate improvement plan
        improvement_plan = self.generate_improvement_plan(reflection_result)
        
        return {
            "reflection_analysis": reflection_result,
            "improvement_plan": improvement_plan,
            "cost_tracking": {
                "total_cost": self.cost_tracker.total_cost,
                "api_calls": self.cost_tracker.api_calls
            },
            "performance_trend": self.analyze_performance_trend()
        }

    def generate_improvement_plan(self, reflection: dict) -> dict:
        """Generate actionable improvement plan based on reflection"""
        recommendations = reflection.get("optimization_recommendations", [])
        
        return {
            "immediate_actions": recommendations[:2],
            "medium_term_goals": recommendations[2:],
            "success_metrics": [
                "Reduce processing latency by 20%",
                "Decrease cost per GB by 15%",
                "Improve error rate to <1%"
            ],
            "implementation_timeline": "2-4 weeks"
        }

    def analyze_performance_trend(self) -> dict:
        """Analyze performance trends over time"""
        if len(self.performance_history) < 2:
            return {"trend": "insufficient_data", "history_count": len(self.performance_history)}
        
        recent_optimizations = len(self.performance_history[-3:])
        
        return {
            "trend": "improving" if recent_optimizations >= 2 else "stable",
            "total_optimizations": len(self.performance_history),
            "recent_optimizations": recent_optimizations,
            "optimization_frequency": f"{len(self.performance_history)} optimizations applied"
        }


if __name__ == "__main__":
    print("🎯 ReflectiveAgent Course Example - Pipeline Performance Optimization")
    
    # Create reflective agent
    reflective_agent = ReflectiveAgent(model_name="gpt-4")
    
    # Simulate performance metrics from a data processing pipeline
    sample_metrics = {
        "throughput_gb_per_hour": 150.5,
        "cost_per_gb": 0.02,
        "error_rate": 2.3,
        "queue_depth": 15,
        "avg_latency_ms": 450
    }
    
    # Run performance analysis
    analysis_result = reflective_agent.run_performance_analysis(sample_metrics)
    
    # Display results
    print("\n📈 Performance Analysis Results:")
    print(f"Cost Analysis: {analysis_result['reflection_analysis']['cost_analysis']}")
    print(f"Assessment: {analysis_result['reflection_analysis']['performance_assessment']}")
    
    print("\n🎯 Improvement Plan:")
    for action in analysis_result['improvement_plan']['immediate_actions']:
        print(f"• {action}")
    
    print(f"\n💰 Cost Tracking: ${analysis_result['cost_tracking']['total_cost']:.4f} total")
    print(f"📊 Performance Trend: {analysis_result['performance_trend']['trend']}")
    
    # Test multiple cycles to show trend analysis
    print("\n--- Running Additional Analysis Cycles ---")
    for cycle in range(2):
        # Simulate improved metrics over time
        sample_metrics['throughput_gb_per_hour'] += 10
        sample_metrics['cost_per_gb'] -= 0.002
        sample_metrics['error_rate'] -= 0.3
        
        result = reflective_agent.run_performance_analysis(sample_metrics)
        print(f"Cycle {cycle + 2}: {result['performance_trend']['trend']} trend")