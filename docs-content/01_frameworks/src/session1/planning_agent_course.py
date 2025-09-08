#!/usr/bin/env python3
"""
Planning Agent implementation matching Session 1 course content
Agent for data workflow orchestration and resource planning
"""

from base_agent_course import BaseAgent
from typing import Dict, List, Any
import time
import json


class PlanningAgent(BaseAgent):
    """Agent for data workflow orchestration"""

    def __init__(self):
        super().__init__()
        self.current_infrastructure = self._get_infrastructure_status()
        
    def _get_infrastructure_status(self) -> dict:
        """Get current infrastructure status"""
        return {
            "available_nodes": 12,
            "cpu_cores_available": 48,
            "memory_gb_available": 192,
            "queue_depth": 25,
            "current_budget_used": 2450.00,
            "monthly_budget": 10000.00
        }

    def create_processing_plan(self, data_batch: dict) -> List[dict]:
        """Generate optimal processing plan for data batch"""
        planning_prompt = f"""
        Create processing plan for data batch:
        - Data volume: {data_batch['size_gb']} GB of structured/unstructured data
        - Data types: {data_batch['data_types']} (JSON, Parquet, CSV, logs)
        - Processing priority: {data_batch['priority']} (real-time/batch/archive)
        - SLA requirement: {data_batch['sla_hours']} hours for completion
        - Processing type: {data_batch['processing_type']} (ETL, analytics, ML training)

        Consider current infrastructure:
        - Available Kubernetes nodes: {self.get_available_nodes()}
        - Current processing queue: {self.get_queue_status()} jobs
        - Budget allocation: ${data_batch['budget']} for this processing cycle
        - Compute availability: {self.get_compute_resources()} for data processing

        Generate step-by-step workflow with optimal resource allocation for data processing.
        """

        plan = self.llm_call_planning(planning_prompt, data_batch)
        validated_plan = self.validate_resource_availability(plan)
        
        return validated_plan

    def llm_call_planning(self, prompt: str, data_batch: dict) -> List[dict]:
        """Simulate intelligent planning based on data batch characteristics"""
        # Simulate processing time based on complexity
        complexity_factor = self._calculate_complexity(data_batch)
        time.sleep(0.1 * complexity_factor)
        
        # Generate plan steps based on data characteristics
        base_steps = self._generate_base_plan(data_batch)
        
        # Optimize plan based on current infrastructure
        optimized_steps = self._optimize_for_infrastructure(base_steps, data_batch)
        
        return optimized_steps

    def _calculate_complexity(self, data_batch: dict) -> float:
        """Calculate processing complexity factor"""
        size_factor = min(data_batch.get('size_gb', 1) / 100, 3.0)  # Max 3x for large datasets
        type_factor = len(data_batch.get('data_types', [])) * 0.5  # Multiple data types add complexity
        priority_factor = 1.5 if data_batch.get('priority') == 'real-time' else 1.0
        
        return size_factor + type_factor + priority_factor

    def _generate_base_plan(self, data_batch: dict) -> List[dict]:
        """Generate base processing plan"""
        plan_steps = []
        
        # Step 1: Data Ingestion
        plan_steps.append({
            "step_number": 1,
            "name": "data_ingestion",
            "description": f"Ingest {data_batch['size_gb']} GB of {data_batch.get('data_types', 'mixed')} data",
            "estimated_duration": max(30, data_batch.get('size_gb', 1) * 2),  # minutes
            "resource_requirements": {
                "cpu_cores": min(4, max(1, data_batch.get('size_gb', 1) // 10)),
                "memory_gb": min(16, max(2, data_batch.get('size_gb', 1) // 5)),
                "storage_gb": data_batch.get('size_gb', 1) * 1.2  # Buffer space
            },
            "dependencies": []
        })

        # Step 2: Data Validation
        plan_steps.append({
            "step_number": 2,
            "name": "data_validation",
            "description": "Validate data quality and schema compliance",
            "estimated_duration": max(15, data_batch.get('size_gb', 1) * 1),
            "resource_requirements": {
                "cpu_cores": 2,
                "memory_gb": 4,
                "storage_gb": data_batch.get('size_gb', 1) * 0.1  # Temp validation files
            },
            "dependencies": ["data_ingestion"]
        })

        # Step 3: Processing based on type
        processing_type = data_batch.get('processing_type', 'ETL')
        if processing_type == 'ETL':
            plan_steps.append({
                "step_number": 3,
                "name": "etl_transformation",
                "description": "Transform and load data according to business rules",
                "estimated_duration": max(45, data_batch.get('size_gb', 1) * 3),
                "resource_requirements": {
                    "cpu_cores": min(8, max(2, data_batch.get('size_gb', 1) // 5)),
                    "memory_gb": min(32, max(4, data_batch.get('size_gb', 1) // 2)),
                    "storage_gb": data_batch.get('size_gb', 1) * 1.5
                },
                "dependencies": ["data_validation"]
            })
        elif processing_type == 'analytics':
            plan_steps.append({
                "step_number": 3,
                "name": "analytics_processing",
                "description": "Run analytical computations and generate insights",
                "estimated_duration": max(30, data_batch.get('size_gb', 1) * 2),
                "resource_requirements": {
                    "cpu_cores": min(6, max(2, data_batch.get('size_gb', 1) // 8)),
                    "memory_gb": min(24, max(4, data_batch.get('size_gb', 1) // 3)),
                    "storage_gb": data_batch.get('size_gb', 1) * 0.5
                },
                "dependencies": ["data_validation"]
            })

        # Step 4: Output Generation
        plan_steps.append({
            "step_number": len(plan_steps) + 1,
            "name": "output_generation",
            "description": "Generate processed outputs and reports",
            "estimated_duration": max(10, data_batch.get('size_gb', 1) * 0.5),
            "resource_requirements": {
                "cpu_cores": 1,
                "memory_gb": 2,
                "storage_gb": data_batch.get('size_gb', 1) * 0.3
            },
            "dependencies": [plan_steps[-1]["name"]]
        })

        return plan_steps

    def _optimize_for_infrastructure(self, base_steps: List[dict], data_batch: dict) -> List[dict]:
        """Optimize plan based on current infrastructure constraints"""
        available_resources = self.current_infrastructure
        optimized_steps = []

        for step in base_steps:
            optimized_step = step.copy()
            
            # Adjust CPU allocation based on availability
            required_cpu = step["resource_requirements"]["cpu_cores"]
            available_cpu = available_resources["cpu_cores_available"]
            
            if required_cpu > available_cpu * 0.8:  # Don't use more than 80% of available
                optimized_step["resource_requirements"]["cpu_cores"] = int(available_cpu * 0.6)
                optimized_step["estimated_duration"] = int(step["estimated_duration"] * 1.3)  # Longer duration
                optimized_step["optimization_note"] = "CPU allocation reduced due to resource constraints"
            
            # Adjust memory allocation
            required_memory = step["resource_requirements"]["memory_gb"]
            available_memory = available_resources["memory_gb_available"]
            
            if required_memory > available_memory * 0.8:
                optimized_step["resource_requirements"]["memory_gb"] = int(available_memory * 0.6)
                optimized_step["optimization_note"] = optimized_step.get("optimization_note", "") + " Memory allocation optimized"

            # Add priority-based adjustments
            if data_batch.get('priority') == 'real-time':
                optimized_step["resource_requirements"]["cpu_cores"] = int(optimized_step["resource_requirements"]["cpu_cores"] * 1.2)
                optimized_step["priority_level"] = "high"
            
            optimized_steps.append(optimized_step)

        return optimized_steps

    def validate_resource_availability(self, plan: List[dict]) -> List[dict]:
        """Validate and adjust plan based on resource availability"""
        validated_plan = []
        
        for step in plan:
            validation_result = self._validate_step_resources(step)
            
            if validation_result["is_valid"]:
                step["validation_status"] = "approved"
            else:
                step["validation_status"] = "requires_adjustment"
                step["validation_issues"] = validation_result["issues"]
                # Apply automatic fixes
                step = self._apply_resource_fixes(step, validation_result["issues"])
            
            validated_plan.append(step)
        
        # Add plan summary
        plan_summary = self._generate_plan_summary(validated_plan)
        
        return {
            "plan_steps": validated_plan,
            "plan_summary": plan_summary,
            "total_estimated_duration": sum(step["estimated_duration"] for step in validated_plan),
            "resource_allocation_valid": all(step["validation_status"] == "approved" for step in validated_plan)
        }

    def _validate_step_resources(self, step: dict) -> dict:
        """Validate individual step resource requirements"""
        issues = []
        
        required_cpu = step["resource_requirements"]["cpu_cores"]
        required_memory = step["resource_requirements"]["memory_gb"]
        
        if required_cpu > self.current_infrastructure["cpu_cores_available"]:
            issues.append(f"CPU requirement ({required_cpu}) exceeds available ({self.current_infrastructure['cpu_cores_available']})")
        
        if required_memory > self.current_infrastructure["memory_gb_available"]:
            issues.append(f"Memory requirement ({required_memory}GB) exceeds available ({self.current_infrastructure['memory_gb_available']}GB)")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    def _apply_resource_fixes(self, step: dict, issues: List[str]) -> dict:
        """Apply automatic fixes for resource constraint issues"""
        fixed_step = step.copy()
        
        for issue in issues:
            if "CPU requirement" in issue:
                fixed_step["resource_requirements"]["cpu_cores"] = int(self.current_infrastructure["cpu_cores_available"] * 0.7)
                fixed_step["estimated_duration"] = int(step["estimated_duration"] * 1.4)
                fixed_step["auto_fix_applied"] = "CPU allocation reduced"
            
            if "Memory requirement" in issue:
                fixed_step["resource_requirements"]["memory_gb"] = int(self.current_infrastructure["memory_gb_available"] * 0.7)
                fixed_step["auto_fix_applied"] = fixed_step.get("auto_fix_applied", "") + " Memory allocation reduced"
        
        fixed_step["validation_status"] = "auto_fixed"
        return fixed_step

    def _generate_plan_summary(self, plan_steps: List[dict]) -> dict:
        """Generate comprehensive plan summary"""
        total_cpu = sum(step["resource_requirements"]["cpu_cores"] for step in plan_steps)
        total_memory = sum(step["resource_requirements"]["memory_gb"] for step in plan_steps)
        total_storage = sum(step["resource_requirements"]["storage_gb"] for step in plan_steps)
        
        return {
            "total_steps": len(plan_steps),
            "resource_summary": {
                "peak_cpu_cores": max(step["resource_requirements"]["cpu_cores"] for step in plan_steps),
                "peak_memory_gb": max(step["resource_requirements"]["memory_gb"] for step in plan_steps),
                "total_storage_gb": total_storage
            },
            "execution_summary": {
                "sequential_duration": sum(step["estimated_duration"] for step in plan_steps),
                "parallel_opportunities": self._identify_parallel_opportunities(plan_steps)
            }
        }

    def _identify_parallel_opportunities(self, plan_steps: List[dict]) -> List[dict]:
        """Identify steps that can run in parallel"""
        parallel_groups = []
        
        # Simple parallel identification based on dependencies
        independent_steps = [step for step in plan_steps if not step.get("dependencies")]
        if len(independent_steps) > 1:
            parallel_groups.append({
                "group_id": 1,
                "parallel_steps": [step["name"] for step in independent_steps],
                "estimated_parallel_duration": max(step["estimated_duration"] for step in independent_steps)
            })
        
        return parallel_groups

    def get_available_nodes(self) -> int:
        """Get available Kubernetes nodes"""
        return self.current_infrastructure["available_nodes"]

    def get_queue_status(self) -> int:
        """Get current processing queue depth"""
        return self.current_infrastructure["queue_depth"]

    def get_compute_resources(self) -> dict:
        """Get current compute resource availability"""
        return {
            "cpu_cores": self.current_infrastructure["cpu_cores_available"],
            "memory_gb": self.current_infrastructure["memory_gb_available"]
        }


if __name__ == "__main__":
    print("🎯 PlanningAgent Course Example - Data Workflow Orchestration")
    
    # Create planning agent
    planning_agent = PlanningAgent()
    
    # Test data batch scenarios
    test_scenarios = [
        {
            "name": "Small ETL Job",
            "batch": {
                "size_gb": 5,
                "data_types": ["JSON", "CSV"],
                "priority": "batch",
                "sla_hours": 4,
                "processing_type": "ETL",
                "budget": 50
            }
        },
        {
            "name": "Large Analytics Job",
            "batch": {
                "size_gb": 150,
                "data_types": ["Parquet", "JSON", "logs"],
                "priority": "real-time",
                "sla_hours": 2,
                "processing_type": "analytics",
                "budget": 200
            }
        },
        {
            "name": "ML Training Dataset",
            "batch": {
                "size_gb": 80,
                "data_types": ["Parquet", "CSV"],
                "priority": "batch",
                "sla_hours": 12,
                "processing_type": "ML training",
                "budget": 300
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n--- Planning Scenario: {scenario['name']} ---")
        
        # Generate processing plan
        plan_result = planning_agent.create_processing_plan(scenario['batch'])
        
        # Display plan summary
        summary = plan_result['plan_summary']
        print(f"📋 Plan Summary:")
        print(f"   Steps: {summary['total_steps']}")
        print(f"   Peak CPU: {summary['resource_summary']['peak_cpu_cores']} cores")
        print(f"   Peak Memory: {summary['resource_summary']['peak_memory_gb']} GB")
        print(f"   Estimated Duration: {summary['execution_summary']['sequential_duration']} minutes")
        print(f"   Resource Allocation Valid: {plan_result['resource_allocation_valid']}")
        
        # Show first few plan steps
        print(f"\n📝 Plan Steps:")
        for step in plan_result['plan_steps'][:2]:  # Show first 2 steps
            print(f"   {step['step_number']}. {step['name']}: {step['description']}")
            print(f"      Duration: {step['estimated_duration']} min | "
                  f"CPU: {step['resource_requirements']['cpu_cores']} cores | "
                  f"Memory: {step['resource_requirements']['memory_gb']} GB")
    
    print(f"\n🏗️  Infrastructure Status:")
    infra = planning_agent.current_infrastructure
    print(f"   Available Nodes: {infra['available_nodes']}")
    print(f"   Available CPU: {infra['cpu_cores_available']} cores")
    print(f"   Available Memory: {infra['memory_gb_available']} GB")
    print(f"   Budget Used: ${infra['current_budget_used']:.2f} / ${infra['monthly_budget']:.2f}")