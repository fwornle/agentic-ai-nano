#!/usr/bin/env python3
"""
Comprehensive Demo Runner for Session 1 Course Content
Demonstrates all five agentic patterns in action
"""

import sys
import time
from typing import Dict, Any

# Import all course agents
from base_agent_course import BaseAgent
from reflection_agent_course import ReflectiveAgent
from tool_use_agent_course import ToolUseAgent
from planning_agent_course import PlanningAgent
from react_agent_course import ReActAgent
from multi_agent_system_course import DataPipelineCoordinator


class CourseDemo:
    """Comprehensive demonstration of bare metal agent patterns"""
    
    def __init__(self):
        self.demo_results = {}
        print("🎯 Session 1 Course Demo: Bare Metal Agent Patterns")
        print("=" * 60)
        
    def run_complete_demo(self):
        """Run complete demonstration of all agent patterns"""
        print("🚀 Starting comprehensive agent pattern demonstration...\n")
        
        # Demo 1: Base Agent Foundation
        self.demo_base_agent()
        
        # Demo 2: Reflection Pattern
        self.demo_reflection_pattern()
        
        # Demo 3: Tool Use Pattern  
        self.demo_tool_use_pattern()
        
        # Demo 4: Planning Pattern
        self.demo_planning_pattern()
        
        # Demo 5: ReAct Pattern
        self.demo_react_pattern()
        
        # Demo 6: Multi-Agent Coordination
        self.demo_multi_agent_system()
        
        # Final Summary
        self.display_demo_summary()
        
    def demo_base_agent(self):
        """Demonstrate BaseAgent foundation capabilities"""
        print("🔧 DEMO 1: BaseAgent Foundation")
        print("-" * 40)
        
        agent = BaseAgent(model_name="gpt-4", max_memory_mb=512)
        
        # Test different input types
        test_inputs = [
            {"type": "analytics_query", "content": "Analyze Q1 revenue trends"},
            {"stream_protocol": "kafka", "data": {"user_events": 1000}},
            {"size_gb": 25, "format": "parquet", "source": "data_lake"}
        ]
        
        results = []
        for i, input_data in enumerate(test_inputs, 1):
            print(f"   Test {i}: Processing {input_data.get('type', 'data')}")
            result = agent.run(input_data)
            results.append(result)
            print(f"   Result: {result['status']} in {result.get('execution_time', 'N/A')}")
        
        self.demo_results["base_agent"] = {
            "tests_run": len(test_inputs),
            "success_rate": sum(1 for r in results if r['status'] == 'completed') / len(results),
            "patterns_demonstrated": ["input_processing", "cost_optimization", "error_handling"]
        }
        print()

    def demo_reflection_pattern(self):
        """Demonstrate ReflectiveAgent self-optimization"""
        print("🔍 DEMO 2: Reflection Pattern - Self-Optimization")
        print("-" * 50)
        
        reflective_agent = ReflectiveAgent(model_name="gpt-4")
        
        # Simulate performance metrics from different time periods
        performance_scenarios = [
            {
                "name": "Peak Hours",
                "throughput_gb_per_hour": 120.5,
                "cost_per_gb": 0.025,
                "error_rate": 3.2,
                "queue_depth": 45,
                "avg_latency_ms": 650
            },
            {
                "name": "Optimized Period",
                "throughput_gb_per_hour": 180.2,
                "cost_per_gb": 0.018,
                "error_rate": 1.1,
                "queue_depth": 12,
                "avg_latency_ms": 380
            }
        ]
        
        optimization_results = []
        for scenario in performance_scenarios:
            print(f"   Analyzing: {scenario['name']}")
            result = reflective_agent.run_performance_analysis(scenario)
            optimization_results.append(result)
            
            trend = result['performance_trend']['trend']
            cost = result['cost_tracking']['total_cost']
            print(f"   Trend: {trend.upper()} | Cost: ${cost:.4f}")
        
        self.demo_results["reflection"] = {
            "scenarios_analyzed": len(performance_scenarios),
            "optimizations_identified": len(optimization_results[0]['improvement_plan']['immediate_actions']),
            "cost_tracking": True,
            "performance_trend": optimization_results[-1]['performance_trend']['trend']
        }
        print()

    def demo_tool_use_pattern(self):
        """Demonstrate ToolUseAgent cloud service integration"""
        print("🔧 DEMO 3: Tool Use Pattern - Cloud Service Integration")
        print("-" * 55)
        
        tool_agent = ToolUseAgent()
        
        # Demonstrate individual tool usage
        tool_tests = [
            ("query_data_lake", {"bucket_name": "analytics-lake", "prefix": "2024/events/"}),
            ("execute_analytics_query", {"query": "SELECT COUNT(*) FROM user_sessions WHERE date >= '2024-01-01'"}),
            ("publish_data_stream", {"topic": "processed-events", "message": {"event_id": 12345, "processed": True}})
        ]
        
        individual_results = []
        print("   Individual Tool Tests:")
        for tool_name, params in tool_tests:
            result = tool_agent.execute_tool(tool_name, **params)
            individual_results.append(result)
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {tool_name}: {result.get('result', {}).get('status', 'executed')}")
        
        # Demonstrate orchestrated workflow
        print("\n   Orchestrated Workflow Test:")
        workflow_config = {
            "workflow_name": "Demo Data Pipeline",
            "bucket": "demo-data-lake",
            "check_data_availability": True,
            "run_analytics": True,
            "trigger_etl": True,
            "dag_id": "demo_pipeline"
        }
        
        workflow_result = tool_agent.orchestrate_data_workflow(workflow_config)
        print(f"   📊 Workflow: {workflow_result['workflow_name']}")
        print(f"   🔧 Steps: {' → '.join(workflow_result['steps_executed'])}")
        print(f"   ✅ Success: {workflow_result['success']}")
        
        self.demo_results["tool_use"] = {
            "tools_available": len(tool_agent.tools),
            "individual_success_rate": sum(1 for r in individual_results if r['success']) / len(individual_results),
            "workflow_orchestration": workflow_result['success'],
            "integrations": ["s3", "postgresql", "airflow", "kafka", "elasticsearch", "grafana"]
        }
        print()

    def demo_planning_pattern(self):
        """Demonstrate PlanningAgent workflow orchestration"""
        print("📋 DEMO 4: Planning Pattern - Workflow Orchestration")
        print("-" * 52)
        
        planning_agent = PlanningAgent()
        
        # Test different planning scenarios
        planning_scenarios = [
            {
                "name": "Real-time Analytics",
                "batch": {
                    "size_gb": 15,
                    "data_types": ["JSON", "Avro"],
                    "priority": "real-time",
                    "sla_hours": 1,
                    "processing_type": "analytics",
                    "budget": 100
                }
            },
            {
                "name": "Large ETL Job",
                "batch": {
                    "size_gb": 200,
                    "data_types": ["Parquet", "CSV", "JSON"],
                    "priority": "batch",
                    "sla_hours": 8,
                    "processing_type": "ETL",
                    "budget": 500
                }
            }
        ]
        
        planning_results = []
        for scenario in planning_scenarios:
            print(f"   Planning: {scenario['name']}")
            plan = planning_agent.create_processing_plan(scenario['batch'])
            planning_results.append(plan)
            
            summary = plan['plan_summary']
            print(f"   Steps: {summary['total_steps']} | "
                  f"Duration: {summary['execution_summary']['sequential_duration']} min | "
                  f"Valid: {plan['resource_allocation_valid']}")
        
        self.demo_results["planning"] = {
            "scenarios_planned": len(planning_scenarios),
            "average_steps": sum(p['plan_summary']['total_steps'] for p in planning_results) / len(planning_results),
            "resource_validation": all(p['resource_allocation_valid'] for p in planning_results),
            "infrastructure_awareness": True
        }
        print()

    def demo_react_pattern(self):
        """Demonstrate ReActAgent adaptive processing"""
        print("🤔 DEMO 5: ReAct Pattern - Adaptive Processing")
        print("-" * 47)
        
        react_agent = ReActAgent()
        
        # Test adaptive processing scenarios
        adaptive_scenarios = [
            {
                "name": "High Quality Data",
                "batch": {
                    "size_gb": 10,
                    "source": "validated_api",
                    "validation_errors": 2,
                    "missing_values_percent": 1,
                    "data_types": ["JSON"]
                }
            },
            {
                "name": "Problematic Dataset",
                "batch": {
                    "size_gb": 50,
                    "source": "legacy_system",
                    "validation_errors": 500,
                    "missing_values_percent": 40,
                    "data_types": ["CSV", "XML", "proprietary"],
                    "schema_version": "outdated"
                }
            }
        ]
        
        react_results = []
        for scenario in adaptive_scenarios:
            print(f"   Processing: {scenario['name']}")
            result = react_agent.process_with_reasoning(scenario['batch'], max_retries=3)
            react_results.append(result)
            
            if result['status'] == 'completed':
                print(f"   ✅ Success: {result['attempts_required']} attempts | "
                      f"Strategy: {result['final_strategy']} | "
                      f"Quality: {result['quality_score']:.2f}")
            else:
                print(f"   ❌ Failed: {result['final_error']}")
        
        # Show analytics
        analytics = react_agent.get_processing_analytics()
        
        self.demo_results["react"] = {
            "scenarios_processed": len(adaptive_scenarios),
            "success_rate": analytics.get('success_rate', 0),
            "adaptive_strategies": len(react_agent.adaptive_strategies),
            "reasoning_transparency": True
        }
        print()

    def demo_multi_agent_system(self):
        """Demonstrate Multi-Agent coordination"""
        print("🤖 DEMO 6: Multi-Agent System - Distributed Processing")
        print("-" * 57)
        
        coordinator = DataPipelineCoordinator()
        
        # Test multi-agent coordination
        test_batch = {
            "batch_id": "demo_comprehensive_batch",
            "sources": ["s3", "database", "api"],
            "size_multiplier": 1.0,
            "expected_quality": "mixed"
        }
        
        print(f"   Coordinating: {test_batch['batch_id']}")
        print(f"   Agents: {len(coordinator.agents)} specialized agents")
        
        # Execute multi-agent pipeline
        pipeline_result = coordinator.orchestrate_data_pipeline(test_batch)
        
        if pipeline_result['status'] == 'completed':
            data_flow = pipeline_result['data_flow_summary']
            performance = pipeline_result['performance_summary']
            
            print(f"   ✅ Success: {len(pipeline_result['stages_completed'])} stages completed")
            print(f"   📊 Data Flow: {data_flow['initial_records']:,} → {data_flow['final_records']:,} records")
            print(f"   ⚡ Throughput: {performance['throughput_records_per_second']:.0f} records/sec")
            print(f"   📈 Quality Improvement: +{data_flow['quality_improvement']:.2f}")
            
            print(f"   🤖 Agent Performance:")
            for agent, perf in pipeline_result['agent_performance'].items():
                status = "✅" if perf['success'] else "❌"
                print(f"      {status} {agent}: {perf['processing_time']:.2f}s")
        else:
            print(f"   ❌ Pipeline Failed: {pipeline_result['failed_at_stage']}")
        
        self.demo_results["multi_agent"] = {
            "agents_coordinated": len(coordinator.agents),
            "pipeline_success": pipeline_result['overall_success'],
            "stages_completed": len(pipeline_result['stages_completed']),
            "coordination_pattern": "sequential_with_validation"
        }
        print()

    def display_demo_summary(self):
        """Display comprehensive demo summary"""
        print("📊 DEMO SUMMARY: Bare Metal Agent Patterns")
        print("=" * 60)
        
        total_patterns = len(self.demo_results)
        successful_demos = sum(1 for demo in self.demo_results.values() 
                             if self._is_demo_successful(demo))
        
        print(f"🎯 Patterns Demonstrated: {total_patterns}")
        print(f"✅ Successful Demonstrations: {successful_demos}/{total_patterns}")
        print(f"📈 Success Rate: {successful_demos/total_patterns:.1%}")
        
        print("\n🔍 Pattern-by-Pattern Results:")
        
        pattern_details = {
            "base_agent": ("Foundation Architecture", "Core agent processing capabilities"),
            "reflection": ("Self-Optimization", "Performance analysis and improvement"),
            "tool_use": ("Cloud Integration", "Service orchestration and tool management"),
            "planning": ("Workflow Orchestration", "Resource allocation and planning"),
            "react": ("Adaptive Processing", "Reasoning and dynamic adaptation"),
            "multi_agent": ("Distributed Coordination", "Multi-agent system orchestration")
        }
        
        for pattern_name, (title, description) in pattern_details.items():
            if pattern_name in self.demo_results:
                result = self.demo_results[pattern_name]
                status = "✅" if self._is_demo_successful(result) else "❌"
                print(f"   {status} {title}: {description}")
                
                # Show key metrics
                key_metrics = self._extract_key_metrics(pattern_name, result)
                for metric in key_metrics:
                    print(f"      • {metric}")
        
        print(f"\n🏆 Demo Highlights:")
        print(f"   • Cloud-native architecture with Kubernetes integration")
        print(f"   • Comprehensive cost optimization and monitoring")
        print(f"   • Production-ready error handling and resilience")
        print(f"   • Enterprise-scale data processing capabilities")
        print(f"   • Multi-agent coordination for complex workflows")
        
        print(f"\n💡 Key Takeaways:")
        print(f"   • Bare metal implementation provides full control over resources")
        print(f"   • Five fundamental patterns enable sophisticated AI behaviors")
        print(f"   • Agent coordination scales processing capabilities")
        print(f"   • Cost optimization is critical for production deployments")
        print(f"   • Reflection enables continuous system improvement")
        
        print(f"\n🔧 Ready for Production:")
        production_features = [
            "Kubernetes deployment configurations",
            "Prometheus metrics and Grafana dashboards", 
            "Cost tracking and budget management",
            "Enterprise security and compliance",
            "Scalable multi-agent architecture"
        ]
        
        for feature in production_features:
            print(f"   ✓ {feature}")
        
        print("\n" + "=" * 60)
        print("🎓 Session 1 Complete: Ready for LangChain Foundations!")
        print("=" * 60)

    def _is_demo_successful(self, demo_result: Dict[str, Any]) -> bool:
        """Determine if a demo was successful based on its results"""
        # Base agent: Check success rate
        if 'success_rate' in demo_result:
            return demo_result['success_rate'] > 0.8
        
        # Planning: Check resource validation
        if 'resource_validation' in demo_result:
            return demo_result['resource_validation']
        
        # Multi-agent: Check pipeline success
        if 'pipeline_success' in demo_result:
            return demo_result['pipeline_success']
        
        # Tool use: Check workflow orchestration
        if 'workflow_orchestration' in demo_result:
            return demo_result['workflow_orchestration']
        
        # Default: assume successful if no specific failure indicators
        return True

    def _extract_key_metrics(self, pattern_name: str, result: Dict[str, Any]) -> list:
        """Extract key metrics for display"""
        if pattern_name == "base_agent":
            return [
                f"Tests executed: {result.get('tests_run', 0)}",
                f"Success rate: {result.get('success_rate', 0):.1%}"
            ]
        elif pattern_name == "reflection":
            return [
                f"Performance scenarios: {result.get('scenarios_analyzed', 0)}",
                f"Trend: {result.get('performance_trend', 'unknown').upper()}"
            ]
        elif pattern_name == "tool_use":
            return [
                f"Cloud integrations: {len(result.get('integrations', []))}",
                f"Workflow success: {result.get('workflow_orchestration', False)}"
            ]
        elif pattern_name == "planning":
            return [
                f"Scenarios planned: {result.get('scenarios_planned', 0)}",
                f"Resource validation: {result.get('resource_validation', False)}"
            ]
        elif pattern_name == "react":
            return [
                f"Adaptive strategies: {result.get('adaptive_strategies', 0)}",
                f"Success rate: {result.get('success_rate', 0):.1%}"
            ]
        elif pattern_name == "multi_agent":
            return [
                f"Agents coordinated: {result.get('agents_coordinated', 0)}",
                f"Stages completed: {result.get('stages_completed', 0)}"
            ]
        
        return ["Metrics available"]


def main():
    """Main demo execution function"""
    # Check if running with quick mode
    quick_mode = "--quick" in sys.argv
    
    if quick_mode:
        print("🚀 Quick Demo Mode Activated")
        time.sleep(0.1)  # Minimal delays
    else:
        print("🎓 Full Demo Mode - Comprehensive Demonstration")
        print("   (Use --quick flag for faster execution)")
        time.sleep(1)
    
    # Create and run demo
    demo = CourseDemo()
    
    try:
        demo.run_complete_demo()
        print("\n🎉 Demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("   This may indicate issues with agent implementations")
        
    finally:
        print("   Thank you for exploring Session 1: Bare Metal Agents!")


if __name__ == "__main__":
    main()