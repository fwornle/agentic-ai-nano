#!/usr/bin/env python3
"""
Base Agent implementation matching Session 1 course content
Foundation for data pipeline agents with cloud-native deployment
"""

import time
import logging
from typing import Dict, Union, Any, Optional
from datetime import datetime

# Mock pandas DataFrame for demonstration
class MockDataFrame:
    def __init__(self, data=None):
        self.data = data or {}
        self.columns = ["id", "value", "timestamp"] if not data else list(data.keys())
    
    def memory_usage(self, deep=True):
        class MemoryUsage:
            def sum(self):
                return 1024 * len(self.columns)
        return MemoryUsage()
        
    def __len__(self):
        return 100  # Mock row count

# Simulate metrics client for production monitoring
class MetricsClient:
    def timer(self, metric_name: str):
        return self
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        print(f"⏱️  {duration:.3f}s processing time")
    
    def increment(self, metric_name: str, tags: list = None):
        print(f"📊 Metric {metric_name} incremented {f'with tags {tags}' if tags else ''}")

class CostTracker:
    def __init__(self):
        self.total_cost = 0.0
        self.api_calls = 0
    
    def track_api_call(self, model_name: str, estimated_tokens: int = 100):
        # Simplified cost calculation
        cost_per_token = 0.00002 if "gpt-4" in model_name else 0.000002
        call_cost = estimated_tokens * cost_per_token
        self.total_cost += call_cost
        self.api_calls += 1
        return call_cost


class BaseAgent:
    """Foundation class for data pipeline agent implementations"""
    
    def __init__(self, model_name="gpt-4", max_memory_mb=512):
        self.model_name = model_name      # LLM endpoint configuration
        self.memory = []                  # Processing context
        self.tools = {}                   # Cloud service integrations
        self.max_memory_mb = max_memory_mb  # Pod memory limit
        self.metrics_client = self._init_metrics()  # Prometheus metrics
        self.cost_threshold = 1.0  # Dollar threshold for model selection
        self.logger = logging.getLogger(f"agent.{self.__class__.__name__}")
        
    def _init_metrics(self) -> MetricsClient:
        """Initialize metrics client for production monitoring"""
        return MetricsClient()

    def run(self, input_data: dict, timeout_seconds: int = 30) -> dict:
        """Processing cycle with cloud resource management and cost optimization"""
        try:
            # Track API costs and latency for budget management
            with self.metrics_client.timer('agent_processing_time'):
                processed_input = self.process_input(input_data)
                action_plan = self.decide_action(processed_input)
                result = self.execute_action(action_plan)
                
                # Track LLM API costs for enterprise-scale processing
                self.metrics_client.increment('llm_api_calls',
                    tags=['model:' + self.model_name])

                return self.format_response(result)
        except TimeoutError:
            return self.handle_timeout(input_data)
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def process_input(self, data: Union[str, dict, bytes, MockDataFrame]) -> dict:
        """Standardize input from data sources"""
        if isinstance(data, bytes):  # Binary data streams (Protobuf, Avro)
            return self.parse_binary_format(data)
        elif isinstance(data, MockDataFrame):  # Structured analytics results
            return self.extract_dataframe_features(data)
        elif isinstance(data, dict) and 'stream_protocol' in data:  # Real-time data streams
            return self.convert_stream_format(data)
        else:  # Natural language queries from data analysts
            return {"type": "nl_query", "content": str(data)}

    def parse_binary_format(self, data: bytes) -> dict:
        """Parse binary data formats"""
        return {
            "type": "binary_stream", 
            "size": len(data),
            "format": "protobuf_avro",
            "content": f"<{len(data)} bytes of binary data>"
        }

    def extract_dataframe_features(self, df: MockDataFrame) -> dict:
        """Extract features from DataFrame"""
        return {
            "type": "dataframe",
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": {"id": "int64", "value": "float64", "timestamp": "datetime64[ns]"},
            "memory_usage": df.memory_usage(deep=True).sum()
        }

    def convert_stream_format(self, data: dict) -> dict:
        """Convert streaming data format"""
        return {
            "type": "stream_data",
            "protocol": data.get("stream_protocol"),
            "metadata": data.get("metadata", {}),
            "content": data.get("data", "")
        }

    def decide_action(self, input_data: dict) -> dict:
        """Intelligent decision making with enterprise-scale cost optimization"""
        # Estimate processing cost based on data complexity and throughput requirements
        estimated_cost = self.estimate_processing_cost(input_data)
        
        if estimated_cost > self.cost_threshold:
            # Use efficient model for routine data validation
            decision = self.llm_inference(input_data, model="gpt-3.5-turbo")
        else:
            # Use advanced model for complex data transformation analysis
            decision = self.llm_inference(input_data, model=self.model_name)
        
        # Validate against data governance and compliance requirements
        if not self.validate_compliance(decision):
            decision = self.get_compliant_alternative(decision)

        return decision

    def estimate_processing_cost(self, input_data: dict) -> float:
        """Estimate processing cost based on data complexity"""
        base_cost = 0.01
        
        # Adjust based on data type and complexity
        data_type = input_data.get("type", "simple")
        if data_type == "dataframe":
            base_cost += input_data.get("rows", 0) * 0.0001
        elif data_type == "binary_stream":
            base_cost += input_data.get("size", 0) * 0.00001
        elif data_type == "stream_data":
            base_cost += 0.05  # Streaming data requires more processing
        
        return base_cost

    def llm_inference(self, input_data: dict, model: str = None) -> dict:
        """Simulate LLM inference call"""
        model = model or self.model_name
        
        # Simulate processing based on model complexity
        processing_time = 2.0 if "gpt-4" in model else 1.0
        time.sleep(0.1)  # Simulate actual processing
        
        return {
            "model_used": model,
            "processing_time": processing_time,
            "recommendation": f"Process {input_data.get('type', 'data')} using optimized pipeline",
            "confidence": 0.85
        }

    def validate_compliance(self, decision: dict) -> bool:
        """Validate against data governance and compliance requirements"""
        # Simplified compliance check
        return decision.get("confidence", 0) > 0.7

    def get_compliant_alternative(self, decision: dict) -> dict:
        """Generate compliant alternative when violations are detected"""
        decision["compliance_adjusted"] = True
        decision["confidence"] = max(0.75, decision.get("confidence", 0))
        return decision

    def execute_action(self, action_plan: dict) -> dict:
        """Execute the decided action plan"""
        return {
            "action_executed": action_plan.get("recommendation", "default_action"),
            "model_used": action_plan.get("model_used"),
            "execution_time": datetime.now().isoformat(),
            "success": True
        }

    def format_response(self, result: dict) -> dict:
        """Format final response for client consumption"""
        return {
            "status": "completed",
            "result": result,
            "agent_type": self.__class__.__name__,
            "timestamp": datetime.now().isoformat()
        }

    def handle_timeout(self, input_data: dict) -> dict:
        """Handle processing timeouts gracefully"""
        return {
            "status": "timeout",
            "message": "Processing exceeded timeout limit",
            "input_type": input_data.get("type"),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Example usage demonstrating the BaseAgent functionality
    print("🎯 BaseAgent Course Example - Data Pipeline Processing")
    
    agent = BaseAgent(model_name="gpt-4", max_memory_mb=512)
    
    # Test different data types
    test_cases = [
        {"type": "nl_query", "content": "Analyze customer churn patterns"},
        {"stream_protocol": "kafka", "data": "real-time events", "metadata": {"topic": "user-events"}},
        b"binary_data_simulation",
        # Simulate DataFrame
        {"dataframe_simulation": True, "rows": 1000, "columns": ["id", "value", "timestamp"]}
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        if test_data == b"binary_data_simulation":
            result = agent.run(test_data)
        else:
            result = agent.run(test_data)
        
        print(f"Result: {result}")