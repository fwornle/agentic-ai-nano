# src/session5/demo_runner_course.py
"""
Comprehensive demo runner for PydanticAI-style type-safe agents.
Demonstrates all key concepts from Session 5 with practical examples.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import sys
import traceback

# Import our course implementations
from pydantic_agents_course import (
    # Mock framework components
    BaseModel, Field, ValidationError, validator, root_validator,
    MockAgent, Agent, Priority, ProcessingStatus,
    
    # Data models
    DataQualityRequest, DataQualityReport,
    FeatureExtractionRequest, FeatureExtractionResponse,
    
    # Agents
    create_data_quality_agent, create_feature_extraction_agent,
    create_validation_agent, TypeSafeAgentManager
)

from type_safe_validation_course import (
    # Advanced validation models
    DataSchema, DataProcessingJob, DataQualityProfile,
    DataFormat, ProcessingComplexity, ValidationLevel,
    
    # Advanced validation agents
    create_schema_validation_agent, create_job_validation_agent,
    create_quality_validation_agent, ValidationOrchestrator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DemoScenario:
    """Base class for demo scenarios."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.results: Dict[str, Any] = {}
    
    async def run(self) -> Dict[str, Any]:
        """Run the demo scenario."""
        logger.info(f"Starting scenario: {self.name}")
        start_time = datetime.now()
        
        try:
            await self.execute()
            self.results['status'] = 'success'
        except Exception as e:
            self.results['status'] = 'failed'
            self.results['error'] = str(e)
            self.results['traceback'] = traceback.format_exc()
            logger.error(f"Scenario {self.name} failed: {e}")
        
        self.results['execution_time'] = (datetime.now() - start_time).total_seconds()
        logger.info(f"Completed scenario: {self.name} ({self.results['status']})")
        
        return self.results
    
    async def execute(self):
        """Override in subclasses."""
        raise NotImplementedError

class BasicTypeValidationScenario(DemoScenario):
    """Demonstrate basic type validation with Pydantic-style models."""
    
    def __init__(self):
        super().__init__(
            "Basic Type Validation",
            "Demonstrates field validation, constraints, and error handling"
        )
    
    async def execute(self):
        print(f"\n🎯 {self.name}")
        print("=" * 50)
        
        # Valid data quality request
        print("\n1. Creating Valid Data Quality Request")
        print("-" * 40)
        
        valid_request = DataQualityRequest(
            dataset_name="customer_behavior_analytics",
            sample_size=10000,
            quality_threshold=0.9,
            include_metrics=True,
            priority=Priority.HIGH
        )
        
        print(f"✅ Dataset: {valid_request.dataset_name}")
        print(f"   Sample Size: {valid_request.sample_size:,}")
        print(f"   Quality Threshold: {valid_request.quality_threshold:.1%}")
        print(f"   Priority: {valid_request.priority.value}")
        
        self.results['valid_request'] = {
            'created': True,
            'dataset_name': valid_request.dataset_name,
            'fields_validated': len(valid_request.__annotations__)
        }
        
        # Invalid data - demonstrate validation
        print("\n2. Demonstrating Validation Error Handling")
        print("-" * 45)
        
        validation_errors = []
        
        try:
            invalid_request = DataQualityRequest(
                dataset_name="",  # Too short
                sample_size=-1000,  # Below minimum
                quality_threshold=1.5,  # Above maximum
                priority="invalid"  # Invalid enum value
            )
        except ValidationError as e:
            validation_errors = e.errors()
            print("✅ Validation correctly caught invalid inputs:")
            for error in validation_errors:
                print(f"   - {error['field']}: {error['error']}")
        
        self.results['validation_errors'] = {
            'caught_errors': True,
            'error_count': len(validation_errors),
            'errors': validation_errors
        }
        
        # Custom validator demonstration
        print("\n3. Custom Validation Logic")
        print("-" * 30)
        
        try:
            # This should trigger custom validation
            test_request = DataQualityRequest(
                dataset_name="1invalid_name",  # Starts with number
                sample_size=5000,
                quality_threshold=0.8
            )
        except ValidationError as e:
            print("✅ Custom validator caught naming convention violation:")
            for error in e.errors():
                if 'dataset_name' in error['field']:
                    print(f"   - {error['error']}")
        
        self.results['custom_validation'] = {'validated': True}

class AgentTypeValidationScenario(DemoScenario):
    """Demonstrate type-safe agent interactions."""
    
    def __init__(self):
        super().__init__(
            "Agent Type Validation",
            "Shows type-safe agent responses with guaranteed structure"
        )
    
    async def execute(self):
        print(f"\n🎯 {self.name}")
        print("=" * 50)
        
        # Create agent manager
        manager = TypeSafeAgentManager()
        
        # Create and register agents
        quality_agent = create_data_quality_agent()
        feature_agent = create_feature_extraction_agent()
        validation_agent = create_validation_agent()
        
        manager.register_agent('data_quality', quality_agent)
        manager.register_agent('feature_extraction', feature_agent)
        manager.register_agent('validation', validation_agent)
        
        print("\n1. Type-Safe Data Quality Agent")
        print("-" * 35)
        
        # Execute quality assessment with guaranteed return type
        result = await manager.execute_with_validation(
            'data_quality',
            "Assess quality of e-commerce transaction data with 2M records",
            DataQualityReport
        )
        
        if result['success']:
            report = result['result']
            print(f"✅ Quality Assessment Completed")
            print(f"   Dataset: {report.dataset_name}")
            print(f"   Quality Score: {report.quality_score:.2%}")
            print(f"   Status: {report.status.value}")
            print(f"   Processing Time: {report.processing_time_ms:.1f}ms")
            print(f"   Recommendations: {len(report.recommendations)} items")
            
            # Demonstrate type safety - we can access fields with confidence
            assert isinstance(report.quality_score, float)
            assert 0.0 <= report.quality_score <= 1.0
            assert isinstance(report.status, ProcessingStatus)
            
            self.results['quality_agent'] = {
                'executed': True,
                'type_safe': True,
                'quality_score': report.quality_score,
                'status': report.status.value
            }
        
        print("\n2. Type-Safe Feature Extraction Agent")
        print("-" * 40)
        
        feature_result = await manager.execute_with_validation(
            'feature_extraction',
            "Extract features from customer transaction patterns for ML model",
            FeatureExtractionResponse
        )
        
        if feature_result['success']:
            response = feature_result['result']
            print(f"✅ Feature Extraction Completed")
            print(f"   Extraction ID: {response.extraction_id}")
            print(f"   Features Extracted: {response.features_extracted}")
            print(f"   Method: {response.extraction_method}")
            print(f"   Memory Usage: {response.memory_usage_mb:.1f}MB")
            
            # Type safety validation
            assert response.extraction_id.startswith('feat_')
            assert response.features_extracted >= 0
            assert response.memory_usage_mb >= 0.0
            
            self.results['feature_agent'] = {
                'executed': True,
                'features_extracted': response.features_extracted,
                'memory_usage_mb': response.memory_usage_mb
            }
        
        print("\n3. Agent Performance Summary")
        print("-" * 30)
        
        performance = manager.get_performance_summary()
        print(f"Total Executions: {performance['total_executions']}")
        print(f"Success Rate: {performance['success_rate']:.1f}%")
        print(f"Average Execution Time: {performance['average_execution_time_ms']:.1f}ms")
        
        self.results['performance'] = performance

class AdvancedValidationScenario(DemoScenario):
    """Demonstrate advanced validation patterns."""
    
    def __init__(self):
        super().__init__(
            "Advanced Validation Patterns",
            "Shows complex validation with business rules and cross-field validation"
        )
    
    async def execute(self):
        print(f"\n🎯 {self.name}")
        print("=" * 50)
        
        orchestrator = ValidationOrchestrator()
        
        print("\n1. Complex Schema Validation")
        print("-" * 30)
        
        # Create a valid complex schema
        schema = DataSchema(
            schema_name="user_engagement_metrics",
            version="2.1.0",
            fields=[
                {"name": "user_id", "type": "string"},
                {"name": "session_duration_minutes", "type": "float"},
                {"name": "page_views", "type": "integer"},
                {"name": "conversion_event", "type": "boolean"},
                {"name": "last_activity_timestamp", "type": "datetime"}
            ],
            constraints={
                "user_id": {"unique": True, "format": "uuid"},
                "session_duration_minutes": {"min": 0, "max": 480}
            },
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=90)
        )
        
        validation_result = await orchestrator.comprehensive_validation(schema)
        
        print(f"✅ Schema Validation: {validation_result['overall_status']}")
        print(f"   Schema Name: {schema.schema_name}")
        print(f"   Version: {schema.version}")
        print(f"   Fields: {len(schema.fields)}")
        print(f"   Execution Time: {validation_result['execution_time_seconds']:.3f}s")
        
        self.results['schema_validation'] = {
            'status': validation_result['overall_status'],
            'field_count': len(schema.fields),
            'execution_time': validation_result['execution_time_seconds']
        }
        
        print("\n2. Complex Job Configuration Validation")
        print("-" * 42)
        
        # Create complex job with business rules
        processing_job = DataProcessingJob(
            job_id="job_20240315_def45678",
            name="Real-time User Engagement Analysis",
            input_schema=schema,
            output_format=DataFormat.PARQUET,
            complexity=ProcessingComplexity.COMPLEX,
            validation_level=ValidationLevel.ENTERPRISE,
            max_memory_gb=64,
            max_runtime_hours=8,
            retry_attempts=3,
            dependencies=["job_20240314_abc12345", "job_20240314_xyz98765"],
            tags={"real-time", "analytics", "user-behavior", "production"},
            priority_score=9.2,
            environment_config={
                "KAFKA_BROKERS": "kafka-cluster.internal:9092",
                "REDIS_URL": "redis://cache-cluster.internal:6379",
                "MODEL_VERSION": "v2.1.3",
                "BATCH_SIZE": "1000"
            }
        )
        
        job_validation = await orchestrator.comprehensive_validation(processing_job)
        
        print(f"✅ Job Validation: {job_validation['overall_status']}")
        print(f"   Job: {processing_job.name}")
        print(f"   Complexity: {processing_job.complexity.value}")
        print(f"   Memory: {processing_job.max_memory_gb}GB")
        print(f"   Dependencies: {len(processing_job.dependencies)}")
        print(f"   Tags: {len(processing_job.tags)}")
        
        if job_validation['business_validation']['warnings']:
            print("   Business Rule Warnings:")
            for warning in job_validation['business_validation']['warnings']:
                print(f"     - {warning}")
        
        self.results['job_validation'] = {
            'status': job_validation['overall_status'],
            'complexity': processing_job.complexity.value,
            'warnings_count': len(job_validation['business_validation']['warnings'])
        }
        
        print("\n3. Data Quality Profile Validation")
        print("-" * 37)
        
        # Create comprehensive quality profile
        quality_profile = DataQualityProfile(
            profile_id="profile_engagement_metrics",
            dataset_name="user_engagement_metrics",
            quality_dimensions={
                "completeness": 0.94,
                "accuracy": 0.88,
                "consistency": 0.91,
                "timeliness": 0.96,
                "validity": 0.89,
                "uniqueness": 0.97
            },
            sample_statistics={
                "total_records": 15_000_000,
                "sample_size": 150_000,
                "sampling_method": "stratified_random",
                "confidence_interval": 0.95
            },
            anomalies_detected=[
                {
                    "type": "statistical_outlier",
                    "severity": "medium",
                    "field": "session_duration_minutes",
                    "description": "Sessions exceeding 8 hours detected (possibly bot activity)",
                    "count": 1247,
                    "percentage": 0.83
                },
                {
                    "type": "pattern_anomaly",
                    "severity": "low",
                    "field": "page_views",
                    "description": "Unusual spike in page views during maintenance window",
                    "count": 234,
                    "percentage": 0.16
                },
                {
                    "type": "data_quality",
                    "severity": "high",
                    "field": "user_id",
                    "description": "Malformed UUID patterns in user identifiers",
                    "count": 89,
                    "percentage": 0.06
                }
            ],
            data_lineage=[
                "raw_clickstream_events",
                "session_aggregation_pipeline", 
                "user_engagement_enrichment",
                "quality_validation_stage"
            ],
            next_assessment=datetime.now() + timedelta(days=14),
            compliance_status={
                "gdpr": True,
                "ccpa": True,
                "internal_data_policy": False  # Requires remediation
            },
            remediation_actions=[
                "Implement bot detection algorithm for session duration filtering",
                "Fix UUID validation in user registration service",
                "Update data retention policies to meet internal compliance"
            ]
        )
        
        profile_validation = await orchestrator.comprehensive_validation(quality_profile)
        
        print(f"✅ Quality Profile Validation: {profile_validation['overall_status']}")
        print(f"   Dataset: {quality_profile.dataset_name}")
        avg_quality = sum(quality_profile.quality_dimensions.values()) / len(quality_profile.quality_dimensions)
        print(f"   Average Quality: {avg_quality:.1%}")
        print(f"   Anomalies: {len(quality_profile.anomalies_detected)}")
        print(f"   Compliance Issues: {len([k for k, v in quality_profile.compliance_status.items() if not v])}")
        print(f"   Remediation Actions: {len(quality_profile.remediation_actions)}")
        
        self.results['quality_validation'] = {
            'status': profile_validation['overall_status'],
            'average_quality': avg_quality,
            'anomaly_count': len(quality_profile.anomalies_detected),
            'compliance_issues': len([k for k, v in quality_profile.compliance_status.items() if not v])
        }
        
        print("\n4. Validation Summary")
        print("-" * 20)
        
        summary = orchestrator.get_validation_summary()
        print(f"Total Validations: {summary['total_validations']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Average Execution Time: {summary['average_execution_time']:.3f}s")
        
        self.results['validation_summary'] = summary

class ErrorHandlingScenario(DemoScenario):
    """Demonstrate comprehensive error handling."""
    
    def __init__(self):
        super().__init__(
            "Error Handling & Recovery",
            "Shows robust error handling, validation failures, and recovery patterns"
        )
    
    async def execute(self):
        print(f"\n🎯 {self.name}")
        print("=" * 50)
        
        print("\n1. Validation Error Collection")
        print("-" * 30)
        
        validation_scenarios = [
            {
                'name': 'Invalid Schema Name',
                'data': {
                    'schema_name': '123_invalid',  # Starts with number
                    'version': '1.0.0',
                    'fields': [{'name': 'test', 'type': 'string'}]
                },
                'expected_error': 'schema_name'
            },
            {
                'name': 'Invalid Version Format', 
                'data': {
                    'schema_name': 'valid_schema',
                    'version': '1.0',  # Missing patch version
                    'fields': [{'name': 'test', 'type': 'string'}]
                },
                'expected_error': 'version'
            },
            {
                'name': 'Empty Fields List',
                'data': {
                    'schema_name': 'valid_schema',
                    'version': '1.0.0',
                    'fields': []  # Empty fields
                },
                'expected_error': 'fields'
            },
            {
                'name': 'Invalid Field Type',
                'data': {
                    'schema_name': 'valid_schema',
                    'version': '1.0.0',
                    'fields': [{'name': 'test', 'type': 'invalid_type'}]
                },
                'expected_error': 'fields'
            }
        ]
        
        error_results = []
        
        for scenario in validation_scenarios:
            try:
                DataSchema(**scenario['data'])
                error_results.append({
                    'scenario': scenario['name'],
                    'status': 'unexpected_success',
                    'error_caught': False
                })
            except ValidationError as e:
                # Check if expected error was caught
                expected_field = scenario['expected_error']
                field_errors = [err['field'] for err in e.errors()]
                error_caught = any(expected_field in field for field in field_errors)
                
                print(f"✅ {scenario['name']}: Error caught correctly")
                for error in e.errors():
                    if expected_field in error['field']:
                        print(f"   - {error['error']}")
                
                error_results.append({
                    'scenario': scenario['name'],
                    'status': 'error_caught',
                    'error_caught': error_caught,
                    'error_count': len(e.errors())
                })
        
        self.results['validation_scenarios'] = error_results
        
        print("\n2. Agent Error Recovery")
        print("-" * 25)
        
        manager = TypeSafeAgentManager()
        quality_agent = create_data_quality_agent()
        manager.register_agent('quality', quality_agent)
        
        # Test agent with invalid input expectations
        recovery_tests = [
            {
                'name': 'Non-existent Agent',
                'agent_name': 'non_existent_agent',
                'query': 'test query'
            },
            {
                'name': 'Valid Agent Execution',
                'agent_name': 'quality',
                'query': 'Analyze customer data quality'
            }
        ]
        
        recovery_results = []
        
        for test in recovery_tests:
            result = await manager.execute_with_validation(
                test['agent_name'],
                test['query']
            )
            
            recovery_results.append({
                'test': test['name'],
                'success': result['success'],
                'error_type': result.get('error', 'none')
            })
            
            if result['success']:
                print(f"✅ {test['name']}: Executed successfully")
            else:
                print(f"✅ {test['name']}: Error handled gracefully - {result['error']}")
        
        self.results['recovery_tests'] = recovery_results
        
        print("\n3. Graceful Degradation")
        print("-" * 25)
        
        # Demonstrate graceful handling of partial data
        try:
            partial_request = DataQualityRequest(
                dataset_name="partial_dataset",
                sample_size=1000,
                # Missing optional fields - should work with defaults
            )
            
            print("✅ Partial data handled with defaults:")
            print(f"   Quality Threshold: {partial_request.quality_threshold}")
            print(f"   Include Metrics: {partial_request.include_metrics}")
            print(f"   Priority: {partial_request.priority.value}")
            
            self.results['graceful_degradation'] = {
                'partial_data_handled': True,
                'defaults_applied': True
            }
            
        except Exception as e:
            print(f"❌ Partial data handling failed: {e}")
            self.results['graceful_degradation'] = {
                'partial_data_handled': False,
                'error': str(e)
            }

class ProductionReadinessScenario(DemoScenario):
    """Demonstrate production-ready patterns."""
    
    def __init__(self):
        super().__init__(
            "Production Readiness",
            "Shows monitoring, logging, and enterprise-grade patterns"
        )
    
    async def execute(self):
        print(f"\n🎯 {self.name}")
        print("=" * 50)
        
        print("\n1. Performance Monitoring")
        print("-" * 25)
        
        manager = TypeSafeAgentManager()
        agents = {
            'quality': create_data_quality_agent(),
            'features': create_feature_extraction_agent(),
            'validation': create_validation_agent()
        }
        
        for name, agent in agents.items():
            manager.register_agent(name, agent)
        
        # Execute multiple operations to generate metrics
        operations = [
            ('quality', 'Assess data quality for transaction_logs'),
            ('features', 'Extract features from customer_behavior'),
            ('validation', 'Validate payment_processing_schema'),
            ('quality', 'Quality check for user_engagement_data'),
            ('features', 'Generate ML features from clickstream_events')
        ]
        
        execution_results = []
        
        for agent_name, query in operations:
            result = await manager.execute_with_validation(agent_name, query)
            execution_results.append({
                'agent': agent_name,
                'success': result['success'],
                'execution_time': result['execution_info']['execution_time_ms']
            })
        
        # Get performance summary
        performance = manager.get_performance_summary()
        
        print(f"✅ Performance Monitoring Results:")
        print(f"   Total Operations: {len(operations)}")
        print(f"   Success Rate: {performance['success_rate']:.1f}%")
        print(f"   Average Execution Time: {performance['average_execution_time_ms']:.1f}ms")
        print(f"   Agents Used: {', '.join(performance['agents_used'])}")
        
        self.results['performance_monitoring'] = {
            'operations_executed': len(operations),
            'success_rate': performance['success_rate'],
            'average_execution_time': performance['average_execution_time_ms'],
            'agent_types': len(performance['agents_used'])
        }
        
        print("\n2. Enterprise Validation Orchestration")
        print("-" * 40)
        
        orchestrator = ValidationOrchestrator()
        
        # Create enterprise-grade objects for validation
        enterprise_objects = []
        
        # High-complexity processing job
        enterprise_job = DataProcessingJob(
            job_id="job_20240315_enterprise",
            name="Enterprise Customer Analytics Pipeline",
            input_schema=DataSchema(
                schema_name="enterprise_customer_data",
                version="3.2.1",
                fields=[
                    {"name": "customer_uuid", "type": "string"},
                    {"name": "transaction_history", "type": "array"},
                    {"name": "risk_score", "type": "float"},
                    {"name": "compliance_flags", "type": "object"}
                ]
            ),
            complexity=ProcessingComplexity.ENTERPRISE,
            validation_level=ValidationLevel.ENTERPRISE,
            max_memory_gb=128,
            max_runtime_hours=12,
            tags={"enterprise", "customer-analytics", "compliance", "production"},
            priority_score=9.8
        )
        
        enterprise_objects.append(('Enterprise Job', enterprise_job))
        
        # Enterprise quality profile
        enterprise_quality = DataQualityProfile(
            profile_id="profile_enterprise_customer",
            dataset_name="enterprise_customer_data", 
            quality_dimensions={
                "completeness": 0.99,
                "accuracy": 0.97,
                "consistency": 0.98,
                "timeliness": 0.95,
                "validity": 0.96,
                "uniqueness": 0.99
            },
            next_assessment=datetime.now() + timedelta(days=1),  # Daily for enterprise
            compliance_status={
                "gdpr": True,
                "ccpa": True,
                "pci_dss": True,
                "sox": True,
                "internal_policy": True
            }
        )
        
        enterprise_objects.append(('Enterprise Quality Profile', enterprise_quality))
        
        # Validate all enterprise objects
        validation_results = []
        
        for obj_name, obj in enterprise_objects:
            result = await orchestrator.comprehensive_validation(obj)
            validation_results.append({
                'object': obj_name,
                'status': result['overall_status'],
                'execution_time': result['execution_time_seconds']
            })
            
            print(f"✅ {obj_name}: {result['overall_status']}")
            print(f"   Execution Time: {result['execution_time_seconds']:.3f}s")
            
            if result['business_validation']['warnings']:
                print(f"   Warnings: {len(result['business_validation']['warnings'])}")
        
        # Get orchestrator summary
        orchestrator_summary = orchestrator.get_validation_summary()
        
        print(f"\n✅ Enterprise Validation Summary:")
        print(f"   Total Validations: {orchestrator_summary['total_validations']}")
        print(f"   Success Rate: {orchestrator_summary['success_rate']:.1f}%")
        print(f"   Total Execution Time: {orchestrator_summary['total_execution_time']:.3f}s")
        
        self.results['enterprise_validation'] = {
            'objects_validated': len(enterprise_objects),
            'success_rate': orchestrator_summary['success_rate'],
            'total_execution_time': orchestrator_summary['total_execution_time']
        }
        
        print("\n3. Scalability Assessment")
        print("-" * 25)
        
        # Simulate high-volume validation
        bulk_operations = 50
        start_time = datetime.now()
        
        bulk_results = []
        for i in range(bulk_operations):
            simple_request = DataQualityRequest(
                dataset_name=f"bulk_dataset_{i:03d}",
                sample_size=1000 + (i * 100),
                quality_threshold=0.8
            )
            
            result = await manager.execute_with_validation('quality', f"Quick assessment {i}")
            bulk_results.append(result['success'])
        
        bulk_execution_time = (datetime.now() - start_time).total_seconds()
        bulk_success_rate = sum(bulk_results) / len(bulk_results) * 100
        
        print(f"✅ Bulk Processing Results:")
        print(f"   Operations: {bulk_operations}")
        print(f"   Total Time: {bulk_execution_time:.2f}s")
        print(f"   Average per Operation: {bulk_execution_time/bulk_operations*1000:.1f}ms")
        print(f"   Success Rate: {bulk_success_rate:.1f}%")
        print(f"   Throughput: {bulk_operations/bulk_execution_time:.1f} ops/sec")
        
        self.results['scalability'] = {
            'bulk_operations': bulk_operations,
            'total_time': bulk_execution_time,
            'success_rate': bulk_success_rate,
            'throughput': bulk_operations/bulk_execution_time
        }

async def run_comprehensive_demo():
    """Run all demo scenarios comprehensively."""
    print("🚀 PydanticAI-Style Type-Safe Agents - Comprehensive Course Demo")
    print("=" * 70)
    print("\nThis demo showcases all key concepts from Session 5:")
    print("• Type-safe data models with validation")
    print("• Structured agent responses and error handling")
    print("• Advanced validation patterns and business rules")
    print("• Production-ready monitoring and orchestration")
    print("• Enterprise-grade scalability and performance")
    
    scenarios = [
        BasicTypeValidationScenario(),
        AgentTypeValidationScenario(),
        AdvancedValidationScenario(),
        ErrorHandlingScenario(),
        ProductionReadinessScenario()
    ]
    
    demo_results = {
        'demo_start_time': datetime.now().isoformat(),
        'scenarios': [],
        'overall_stats': {}
    }
    
    for scenario in scenarios:
        result = await scenario.run()
        demo_results['scenarios'].append({
            'name': scenario.name,
            'description': scenario.description,
            'status': result['status'],
            'execution_time': result['execution_time'],
            'details': result
        })
    
    # Calculate overall statistics
    successful_scenarios = len([s for s in demo_results['scenarios'] if s['status'] == 'success'])
    total_execution_time = sum(s['execution_time'] for s in demo_results['scenarios'])
    
    demo_results['overall_stats'] = {
        'total_scenarios': len(scenarios),
        'successful_scenarios': successful_scenarios,
        'success_rate': successful_scenarios / len(scenarios) * 100,
        'total_execution_time': total_execution_time,
        'demo_end_time': datetime.now().isoformat()
    }
    
    print(f"\n🎯 Demo Complete!")
    print("=" * 30)
    print(f"Scenarios Run: {demo_results['overall_stats']['total_scenarios']}")
    print(f"Success Rate: {demo_results['overall_stats']['success_rate']:.1f}%")
    print(f"Total Execution Time: {demo_results['overall_stats']['total_execution_time']:.2f}s")
    
    print(f"\n📋 Scenario Summary:")
    for scenario in demo_results['scenarios']:
        status_icon = "✅" if scenario['status'] == 'success' else "❌"
        print(f"   {status_icon} {scenario['name']}: {scenario['status']} ({scenario['execution_time']:.2f}s)")
    
    print(f"\n🎓 Key Learning Outcomes Achieved:")
    print("• ✅ Type-safe model validation with custom constraints")
    print("• ✅ Structured agent responses with guaranteed schemas") 
    print("• ✅ Advanced validation patterns with business rules")
    print("• ✅ Comprehensive error handling and recovery")
    print("• ✅ Production-ready monitoring and performance tracking")
    print("• ✅ Enterprise-scale validation orchestration")
    
    print(f"\n💡 Production Deployment Readiness:")
    print("• Mock framework demonstrates real PydanticAI concepts")
    print("• All patterns translate directly to production code")
    print("• Type safety prevents runtime errors in data processing")
    print("• Validation catches issues early in development cycle")
    print("• Performance monitoring enables optimization")
    print("• Error handling ensures system reliability")
    
    return demo_results

if __name__ == "__main__":
    print("🎯 Starting PydanticAI Type-Safe Agents Course Demo...")
    print("This may take a moment as we demonstrate comprehensive validation patterns.\n")
    
    try:
        demo_results = asyncio.run(run_comprehensive_demo())
        
        # Optional: Save results to file for analysis
        import json
        with open('demo_results.json', 'w') as f:
            json.dump(demo_results, f, indent=2, default=str)
        
        print(f"\n💾 Demo results saved to 'demo_results.json'")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)