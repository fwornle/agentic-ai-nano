#!/usr/bin/env python3
"""
Tool Use Agent implementation matching Session 1 course content
Agent with cloud data service integration capabilities
"""

from base_agent_course import BaseAgent
from typing import Dict, Any, List
import json
import time


class ToolUseAgent(BaseAgent):
    """Agent with cloud data service integration capabilities"""

    def __init__(self):
        super().__init__()
        self.register_data_tools()

    def register_data_tools(self):
        """Register cloud service interfaces for data processing"""
        self.tools = {
            "query_data_lake": self.query_s3_data_bucket,
            "execute_analytics_query": self.execute_postgres_analytics_query,
            "trigger_etl_workflow": self.trigger_airflow_dag,
            "publish_data_stream": self.publish_to_kafka_topic,
            "search_data_catalog": self.search_elasticsearch_catalog,
            "update_pipeline_status": self.update_grafana_annotation
        }
        print(f"🔧 Registered {len(self.tools)} data processing tools")

    def query_s3_data_bucket(self, bucket_name: str, prefix: str = "", limit: int = 100) -> dict:
        """Query S3 data lake for available datasets"""
        # Simulate S3 query operation
        time.sleep(0.3)  # Simulate network latency
        
        mock_objects = [
            f"{prefix}dataset_2024_01_{i:03d}.parquet" for i in range(min(limit, 25))
        ]
        
        return {
            "bucket": bucket_name,
            "prefix": prefix,
            "objects_found": len(mock_objects),
            "sample_objects": mock_objects[:5],
            "total_size_gb": len(mock_objects) * 1.2,
            "last_modified": "2024-01-15T10:30:00Z"
        }

    def execute_postgres_analytics_query(self, query: str, database: str = "analytics") -> dict:
        """Execute analytical queries against PostgreSQL"""
        # Simulate PostgreSQL query execution
        time.sleep(0.5)  # Simulate query execution time
        
        # Parse query type for realistic response
        query_lower = query.lower()
        if "count" in query_lower:
            result = {"count": 125847}
        elif "avg" in query_lower or "average" in query_lower:
            result = {"average_value": 42.7}
        elif "select" in query_lower:
            result = {
                "rows": [
                    {"id": 1, "value": 100, "category": "A"},
                    {"id": 2, "value": 150, "category": "B"},
                    {"id": 3, "value": 200, "category": "A"}
                ]
            }
        else:
            result = {"status": "query_executed", "rows_affected": 5432}

        return {
            "database": database,
            "query": query[:100] + "..." if len(query) > 100 else query,
            "execution_time_ms": 487,
            "result": result,
            "success": True
        }

    def trigger_airflow_dag(self, dag_id: str, config: dict = None) -> dict:
        """Trigger Airflow DAG for ETL workflow execution"""
        time.sleep(0.2)  # Simulate API call
        
        run_id = f"manual__{int(time.time())}"
        
        return {
            "dag_id": dag_id,
            "run_id": run_id,
            "state": "running",
            "execution_date": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "config": config or {},
            "estimated_duration": "15-20 minutes",
            "tasks_scheduled": 8
        }

    def publish_to_kafka_topic(self, topic: str, message: dict, partition: int = None) -> dict:
        """Publish message to Kafka topic for real-time streaming"""
        time.sleep(0.1)  # Simulate network operation
        
        message_size = len(json.dumps(message))
        
        return {
            "topic": topic,
            "partition": partition or 0,
            "offset": int(time.time() * 1000) % 1000000,
            "message_size": message_size,
            "timestamp": int(time.time() * 1000),
            "success": True,
            "latency_ms": 12
        }

    def search_elasticsearch_catalog(self, query: str, index: str = "data_catalog") -> dict:
        """Search Elasticsearch data catalog for datasets"""
        time.sleep(0.3)  # Simulate search operation
        
        # Mock search results based on query
        mock_hits = [
            {
                "dataset_id": "customer_data_2024",
                "description": "Customer transaction data for 2024",
                "size_gb": 15.7,
                "last_updated": "2024-01-10",
                "tags": ["customer", "transactions", "pii"]
            },
            {
                "dataset_id": "product_analytics",
                "description": "Product usage analytics and metrics",
                "size_gb": 8.3,
                "last_updated": "2024-01-12",
                "tags": ["product", "analytics", "metrics"]
            }
        ]
        
        return {
            "index": index,
            "query": query,
            "total_hits": len(mock_hits),
            "results": mock_hits,
            "search_time_ms": 23,
            "suggestions": ["Try: customer OR product", "Filter by: tags.keyword"]
        }

    def update_grafana_annotation(self, title: str, description: str, tags: List[str] = None) -> dict:
        """Update Grafana dashboard with pipeline status annotations"""
        time.sleep(0.1)  # Simulate API call
        
        annotation_id = int(time.time() * 100) % 100000
        
        return {
            "annotation_id": annotation_id,
            "title": title,
            "description": description,
            "tags": tags or ["pipeline", "automated"],
            "timestamp": int(time.time() * 1000),
            "dashboard_url": f"http://grafana.internal/d/pipeline-{annotation_id}",
            "success": True
        }

    def execute_tool(self, tool_name: str, **kwargs) -> dict:
        """Execute a specific tool with parameters"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }

        try:
            print(f"🔧 Executing tool: {tool_name}")
            result = self.tools[tool_name](**kwargs)
            
            return {
                "success": True,
                "tool_name": tool_name,
                "result": result,
                "execution_timestamp": time.time()
            }
        
        except Exception as e:
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e),
                "parameters": kwargs
            }

    def orchestrate_data_workflow(self, workflow_config: dict) -> dict:
        """Orchestrate complex data workflow using multiple tools"""
        workflow_steps = []
        results = {}
        
        # Step 1: Query data availability
        if workflow_config.get("check_data_availability"):
            print("📂 Checking data availability...")
            data_result = self.execute_tool(
                "query_data_lake",
                bucket_name=workflow_config.get("bucket", "data-lake"),
                prefix=workflow_config.get("prefix", "raw/")
            )
            workflow_steps.append("data_availability_check")
            results["data_check"] = data_result

        # Step 2: Execute analytics query if data is available
        if results.get("data_check", {}).get("success") and workflow_config.get("run_analytics"):
            print("📊 Running analytics query...")
            query_result = self.execute_tool(
                "execute_analytics_query",
                query=workflow_config.get("query", "SELECT COUNT(*) FROM processed_data"),
                database=workflow_config.get("database", "analytics")
            )
            workflow_steps.append("analytics_execution")
            results["analytics"] = query_result

        # Step 3: Trigger ETL if needed
        if workflow_config.get("trigger_etl"):
            print("⚙️ Triggering ETL workflow...")
            etl_result = self.execute_tool(
                "trigger_airflow_dag",
                dag_id=workflow_config.get("dag_id", "daily_etl"),
                config=workflow_config.get("etl_config", {})
            )
            workflow_steps.append("etl_trigger")
            results["etl"] = etl_result

        # Step 4: Update monitoring
        print("📈 Updating monitoring dashboard...")
        annotation_result = self.execute_tool(
            "update_grafana_annotation",
            title=f"Workflow Completed: {workflow_config.get('workflow_name', 'Data Processing')}",
            description=f"Successfully executed {len(workflow_steps)} workflow steps",
            tags=["workflow", "automated", workflow_config.get("environment", "production")]
        )
        workflow_steps.append("monitoring_update")
        results["monitoring"] = annotation_result

        return {
            "workflow_name": workflow_config.get("workflow_name", "data_workflow"),
            "steps_executed": workflow_steps,
            "total_steps": len(workflow_steps),
            "results": results,
            "success": all(r.get("success", False) for r in results.values()),
            "execution_time": time.time()
        }


if __name__ == "__main__":
    print("🎯 ToolUseAgent Course Example - Cloud Service Integration")
    
    # Create tool use agent
    tool_agent = ToolUseAgent()
    
    print("\n--- Individual Tool Testing ---")
    
    # Test S3 data lake query
    s3_result = tool_agent.execute_tool(
        "query_data_lake",
        bucket_name="customer-data-lake",
        prefix="2024/transactions/",
        limit=10
    )
    print(f"S3 Query: Found {s3_result['result']['objects_found']} objects")
    
    # Test PostgreSQL analytics
    postgres_result = tool_agent.execute_tool(
        "execute_analytics_query",
        query="SELECT AVG(transaction_amount) FROM customer_transactions WHERE date >= '2024-01-01'",
        database="analytics"
    )
    print(f"PostgreSQL: Query completed in {postgres_result['result']['execution_time_ms']}ms")
    
    # Test Kafka streaming
    kafka_result = tool_agent.execute_tool(
        "publish_data_stream",
        topic="user-events",
        message={"user_id": 12345, "event_type": "purchase", "amount": 99.99}
    )
    print(f"Kafka: Published to offset {kafka_result['result']['offset']}")
    
    print("\n--- Orchestrated Workflow Testing ---")
    
    # Test complete workflow orchestration
    workflow_config = {
        "workflow_name": "Daily Customer Analytics",
        "bucket": "customer-data-lake",
        "prefix": "2024/processed/",
        "check_data_availability": True,
        "run_analytics": True,
        "query": "SELECT COUNT(*) as total_customers, AVG(transaction_value) as avg_value FROM customer_summary",
        "trigger_etl": True,
        "dag_id": "customer_analytics_dag",
        "environment": "production"
    }
    
    workflow_result = tool_agent.orchestrate_data_workflow(workflow_config)
    
    print(f"\n📊 Workflow Results:")
    print(f"Workflow: {workflow_result['workflow_name']}")
    print(f"Steps: {' → '.join(workflow_result['steps_executed'])}")
    print(f"Success: {workflow_result['success']}")
    print(f"Total Tools Used: {len(tool_agent.tools)}")