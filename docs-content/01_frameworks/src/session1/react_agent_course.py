#!/usr/bin/env python3
"""
ReAct Agent implementation matching Session 1 course content
Agent implementing adaptive processing for data pipelines
"""

from base_agent_course import BaseAgent
from typing import Dict, Any, List
import time


class ReActAgent(BaseAgent):
    """Agent implementing adaptive processing for data pipelines"""

    def __init__(self):
        super().__init__()
        self.processing_history = []
        self.max_retries = 3
        self.adaptive_strategies = {
            "data_quality_low": "apply_enhanced_cleaning",
            "processing_timeout": "reduce_batch_size", 
            "memory_error": "increase_resource_allocation",
            "schema_mismatch": "apply_flexible_schema_mapping"
        }

    def process_with_reasoning(self, data_batch: dict, max_retries: int = 3) -> dict:
        """Process data with reasoning and adaptive strategies"""
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries):
            print(f"🤔 Processing attempt {attempt + 1}/{max_retries}")
            
            # THOUGHT: Analyze current data characteristics
            thought = self.analyze_data_characteristics(data_batch)
            
            # ACTION: Determine processing strategy based on analysis
            action = self.determine_processing_strategy(thought)
            
            # OBSERVATION: Execute processing and observe results
            observation = self.execute_data_processing(action)
            
            # Check if processing was successful
            if self.processing_successful(observation):
                return self.finalize_processing_result(thought, action, observation, attempt + 1)
            
            # ADAPTATION: Adjust strategy based on observations
            print(f"⚠️  Processing issue detected: {observation.get('error_type', 'unknown')}")
            data_batch = self.adjust_processing_params(observation, data_batch)
            
            # Store attempt for learning
            self.processing_history.append({
                "attempt": attempt + 1,
                "thought": thought,
                "action": action,
                "observation": observation,
                "timestamp": time.time()
            })
        
        # If all retries failed
        return self.handle_processing_failure(data_batch, max_retries)

    def analyze_data_characteristics(self, data_batch: dict) -> dict:
        """THOUGHT: Analyze current data characteristics and context"""
        characteristics = {
            "data_size": data_batch.get("size_gb", 0),
            "data_quality": self._assess_data_quality(data_batch),
            "complexity_score": self._calculate_complexity_score(data_batch),
            "processing_requirements": self._analyze_processing_requirements(data_batch),
            "resource_constraints": self._check_resource_constraints(data_batch),
            "risk_factors": self._identify_risk_factors(data_batch)
        }
        
        # Generate reasoning thoughts
        thoughts = []
        
        if characteristics["data_quality"] < 0.7:
            thoughts.append("Data quality is below threshold - enhanced cleaning required")
        
        if characteristics["data_size"] > 50:
            thoughts.append("Large dataset detected - consider parallel processing")
            
        if characteristics["complexity_score"] > 0.8:
            thoughts.append("High complexity data - use robust processing approach")
            
        characteristics["reasoning_thoughts"] = thoughts
        
        print(f"💭 Thought: {'; '.join(thoughts) if thoughts else 'Standard processing approach suitable'}")
        
        return characteristics

    def determine_processing_strategy(self, thought: dict) -> dict:
        """ACTION: Determine optimal processing strategy based on thoughts"""
        strategy = {
            "approach": "standard",
            "batch_size": "medium",
            "parallelism": False,
            "quality_controls": "basic",
            "timeout_seconds": 300,
            "memory_allocation": "standard"
        }
        
        # Adapt strategy based on thoughts
        if thought["data_quality"] < 0.7:
            strategy["quality_controls"] = "enhanced"
            strategy["approach"] = "quality_focused"
        
        if thought["data_size"] > 50:
            strategy["batch_size"] = "large"
            strategy["parallelism"] = True
            strategy["timeout_seconds"] = 600
            
        if thought["complexity_score"] > 0.8:
            strategy["approach"] = "robust"
            strategy["memory_allocation"] = "high"
            
        if len(thought["risk_factors"]) > 2:
            strategy["approach"] = "conservative"
            strategy["timeout_seconds"] = 900
        
        action_description = f"Applying {strategy['approach']} processing with {strategy['quality_controls']} quality controls"
        if strategy["parallelism"]:
            action_description += " and parallel execution"
            
        print(f"⚡ Action: {action_description}")
        
        strategy["description"] = action_description
        return strategy

    def execute_data_processing(self, action: dict) -> dict:
        """OBSERVATION: Execute processing strategy and observe results"""
        # Simulate processing execution
        processing_time = self._simulate_processing(action)
        
        # Generate realistic observations based on strategy
        observation = {
            "execution_time": processing_time,
            "strategy_used": action["approach"],
            "success": True,
            "data_processed": True,
            "quality_score": 0.85,
            "throughput": "normal"
        }
        
        # Simulate various failure scenarios for learning
        failure_probability = self._calculate_failure_probability(action)
        
        if failure_probability > 0.3:  # Simulate occasional failures for learning
            failure_type = self._determine_failure_type(action)
            observation.update({
                "success": False,
                "error_type": failure_type,
                "error_message": self._generate_error_message(failure_type),
                "data_processed": False
            })
        
        result_msg = "✅ Success" if observation["success"] else f"❌ Failed: {observation.get('error_type', 'Unknown')}"
        print(f"👁️  Observation: {result_msg} in {processing_time:.1f}s")
        
        return observation

    def _simulate_processing(self, action: dict) -> float:
        """Simulate actual processing time based on strategy"""
        base_time = 1.0
        
        if action["approach"] == "robust":
            base_time *= 1.5
        elif action["approach"] == "quality_focused":
            base_time *= 1.3
        elif action["approach"] == "conservative":
            base_time *= 1.7
            
        if action["parallelism"]:
            base_time *= 0.7  # Faster with parallelism
            
        if action["quality_controls"] == "enhanced":
            base_time *= 1.2
        
        # Add some randomness
        actual_time = base_time * (0.8 + 0.4 * time.time() % 1)
        time.sleep(min(0.2, actual_time / 10))  # Brief actual delay
        
        return actual_time

    def _calculate_failure_probability(self, action: dict) -> float:
        """Calculate failure probability based on processing strategy"""
        base_prob = 0.1
        
        if action["approach"] == "conservative":
            base_prob *= 0.5  # Conservative approach reduces failure
        elif action["approach"] == "robust":
            base_prob *= 0.7
            
        if action["quality_controls"] == "enhanced":
            base_prob *= 0.8
            
        return base_prob

    def _determine_failure_type(self, action: dict) -> str:
        """Determine type of failure based on processing context"""
        failure_types = ["data_quality_low", "processing_timeout", "memory_error", "schema_mismatch"]
        
        # Weight failure types based on action characteristics
        if action["memory_allocation"] == "standard" and action["batch_size"] == "large":
            return "memory_error"
        elif action["quality_controls"] == "basic":
            return "data_quality_low"
        elif action["timeout_seconds"] < 400:
            return "processing_timeout"
        else:
            return "schema_mismatch"

    def _generate_error_message(self, error_type: str) -> str:
        """Generate realistic error messages"""
        messages = {
            "data_quality_low": "Data quality validation failed: 34% of records failed validation rules",
            "processing_timeout": "Processing exceeded timeout limit during transformation phase",
            "memory_error": "Insufficient memory allocation for large dataset processing",
            "schema_mismatch": "Input data schema doesn't match expected format in 3 columns"
        }
        return messages.get(error_type, "Unknown processing error occurred")

    def processing_successful(self, observation: dict) -> bool:
        """Determine if processing was successful"""
        return observation.get("success", False) and observation.get("data_processed", False)

    def adjust_processing_params(self, observation: dict, data_batch: dict) -> dict:
        """Adapt processing parameters based on failure observations"""
        adjusted_batch = data_batch.copy()
        error_type = observation.get("error_type")
        
        if error_type in self.adaptive_strategies:
            adaptation = self.adaptive_strategies[error_type]
            print(f"🔄 Adapting: {adaptation}")
            
            if adaptation == "apply_enhanced_cleaning":
                adjusted_batch["quality_requirements"] = "enhanced"
                adjusted_batch["cleaning_level"] = "aggressive"
                
            elif adaptation == "reduce_batch_size":
                current_size = adjusted_batch.get("size_gb", 10)
                adjusted_batch["size_gb"] = max(1, current_size * 0.7)
                
            elif adaptation == "increase_resource_allocation":
                adjusted_batch["resource_multiplier"] = adjusted_batch.get("resource_multiplier", 1.0) * 1.5
                
            elif adaptation == "apply_flexible_schema_mapping":
                adjusted_batch["schema_flexibility"] = "high"
                adjusted_batch["auto_mapping"] = True
        
        return adjusted_batch

    def finalize_processing_result(self, thought: dict, action: dict, observation: dict, attempts: int) -> dict:
        """Generate final processing result"""
        return {
            "status": "completed",
            "attempts_required": attempts,
            "final_strategy": action["approach"],
            "quality_score": observation.get("quality_score", 0.85),
            "execution_time": observation["execution_time"],
            "data_characteristics": {
                "size": thought["data_size"],
                "quality": thought["data_quality"],
                "complexity": thought["complexity_score"]
            },
            "reasoning_process": {
                "initial_thoughts": thought["reasoning_thoughts"],
                "action_taken": action["description"],
                "final_observation": "Processing completed successfully"
            },
            "adaptive_learning": {
                "failures_encountered": attempts - 1,
                "strategies_adapted": len([h for h in self.processing_history if not h["observation"]["success"]])
            },
            "timestamp": time.time()
        }

    def handle_processing_failure(self, data_batch: dict, max_retries: int) -> dict:
        """Handle complete processing failure after all retries"""
        return {
            "status": "failed",
            "attempts": max_retries,
            "final_error": "All processing strategies exhausted",
            "data_batch": data_batch,
            "history": self.processing_history[-max_retries:],
            "recommendations": [
                "Review data quality requirements",
                "Consider manual data cleaning",
                "Increase resource allocation",
                "Contact data engineering team"
            ],
            "timestamp": time.time()
        }

    def _assess_data_quality(self, data_batch: dict) -> float:
        """Assess data quality score"""
        base_quality = 0.8
        
        # Adjust based on data characteristics
        if data_batch.get("source") == "legacy_system":
            base_quality -= 0.2
        if data_batch.get("validation_errors", 0) > 100:
            base_quality -= 0.3
        if data_batch.get("missing_values_percent", 0) > 20:
            base_quality -= 0.2
            
        return max(0.0, min(1.0, base_quality))

    def _calculate_complexity_score(self, data_batch: dict) -> float:
        """Calculate data complexity score"""
        complexity = 0.3
        
        # Add complexity based on various factors
        complexity += len(data_batch.get("data_types", [])) * 0.1
        complexity += min(0.3, data_batch.get("size_gb", 0) / 100)
        complexity += len(data_batch.get("transformations", [])) * 0.15
        
        return min(1.0, complexity)

    def _analyze_processing_requirements(self, data_batch: dict) -> list:
        """Analyze processing requirements"""
        requirements = []
        
        if data_batch.get("real_time", False):
            requirements.append("low_latency")
        if data_batch.get("size_gb", 0) > 50:
            requirements.append("high_throughput")
        if data_batch.get("sensitive_data", False):
            requirements.append("security_compliance")
        if data_batch.get("transformations", []):
            requirements.append("complex_transformations")
            
        return requirements

    def _check_resource_constraints(self, data_batch: dict) -> dict:
        """Check current resource constraints"""
        return {
            "cpu_available": True,
            "memory_sufficient": data_batch.get("size_gb", 0) < 100,
            "storage_available": True,
            "network_bandwidth": "adequate"
        }

    def _identify_risk_factors(self, data_batch: dict) -> list:
        """Identify potential risk factors"""
        risks = []
        
        if data_batch.get("size_gb", 0) > 100:
            risks.append("large_dataset")
        if data_batch.get("source") == "external_api":
            risks.append("external_dependency")
        if data_batch.get("schema_version") != "latest":
            risks.append("schema_version_mismatch")
        if not data_batch.get("backup_available", True):
            risks.append("no_data_backup")
            
        return risks

    def get_processing_analytics(self) -> dict:
        """Get analytics on processing performance"""
        if not self.processing_history:
            return {"message": "No processing history available"}
        
        total_attempts = len(self.processing_history)
        successful_attempts = sum(1 for h in self.processing_history if h["observation"]["success"])
        
        return {
            "total_processing_attempts": total_attempts,
            "success_rate": successful_attempts / total_attempts if total_attempts > 0 else 0,
            "average_retries_needed": total_attempts / max(1, len(set(h.get("session_id", 0) for h in self.processing_history))),
            "common_failure_types": self._get_common_failures(),
            "adaptive_strategies_used": len(self.adaptive_strategies),
            "processing_efficiency": "improving" if successful_attempts > total_attempts * 0.7 else "needs_attention"
        }

    def _get_common_failures(self) -> dict:
        """Get common failure types from history"""
        failure_counts = {}
        for history in self.processing_history:
            if not history["observation"]["success"]:
                error_type = history["observation"].get("error_type", "unknown")
                failure_counts[error_type] = failure_counts.get(error_type, 0) + 1
        return failure_counts


if __name__ == "__main__":
    print("🎯 ReActAgent Course Example - Adaptive Data Processing")
    
    # Create ReAct agent
    react_agent = ReActAgent()
    
    # Test scenarios with different characteristics
    test_scenarios = [
        {
            "name": "High Quality Small Dataset",
            "batch": {
                "size_gb": 5,
                "source": "clean_api",
                "validation_errors": 5,
                "missing_values_percent": 2,
                "data_types": ["JSON"],
                "transformations": ["basic_cleanup"]
            }
        },
        {
            "name": "Large Legacy Dataset",
            "batch": {
                "size_gb": 75,
                "source": "legacy_system",
                "validation_errors": 250,
                "missing_values_percent": 35,
                "data_types": ["CSV", "XML", "proprietary"],
                "transformations": ["format_conversion", "data_enrichment", "validation"],
                "schema_version": "v1.2"
            }
        },
        {
            "name": "Real-time Stream",
            "batch": {
                "size_gb": 2,
                "source": "kafka_stream",
                "real_time": True,
                "sensitive_data": True,
                "validation_errors": 0,
                "data_types": ["JSON"],
                "transformations": ["real_time_aggregation"]
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'='*60}")
        print(f"🧪 Testing Scenario: {scenario['name']}")
        print(f"{'='*60}")
        
        # Process with ReAct pattern
        result = react_agent.process_with_reasoning(scenario['batch'], max_retries=3)
        
        # Display results
        print(f"\n📊 Processing Results:")
        print(f"   Status: {result['status'].upper()}")
        print(f"   Attempts Required: {result.get('attempts_required', 'N/A')}")
        
        if result['status'] == 'completed':
            print(f"   Final Strategy: {result['final_strategy']}")
            print(f"   Quality Score: {result['quality_score']:.2f}")
            print(f"   Execution Time: {result['execution_time']:.1f}s")
            
            print(f"\n🧠 Reasoning Process:")
            reasoning = result['reasoning_process']
            print(f"   Initial Thoughts: {reasoning['initial_thoughts']}")
            print(f"   Action Taken: {reasoning['action_taken']}")
            
            adaptive = result['adaptive_learning']
            print(f"\n🔄 Adaptive Learning:")
            print(f"   Failures Encountered: {adaptive['failures_encountered']}")
            print(f"   Strategies Adapted: {adaptive['strategies_adapted']}")
        
        else:
            print(f"   Final Error: {result.get('final_error')}")
            print(f"   Recommendations: {result.get('recommendations', [])}")
    
    # Show overall analytics
    print(f"\n{'='*60}")
    print("📈 Overall Processing Analytics")
    print(f"{'='*60}")
    
    analytics = react_agent.get_processing_analytics()
    for key, value in analytics.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")