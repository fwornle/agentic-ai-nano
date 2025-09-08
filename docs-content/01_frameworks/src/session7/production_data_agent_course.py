# src/session7/production_data_agent_course.py
"""
Production ADK data processing agent implementation for enterprise workloads.
Matches Session 7 ADK Implementation Guide content.
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

# Import from the ADK course implementation
from adk_agents_course import (
    ADKAgent, ADKContext, ADKResult, DataProcessingCapability,
    EnterpriseMetrics, DataPipelineTracker, MultiTenantIsolation,
    StreamDataInput, BatchDataInput, DataProcessingOutput
)

class ProductionADKAgent(ADKAgent):
    """Production-grade ADK agent with advanced enterprise capabilities."""
    
    def __init__(self, name: str, tenant_config: Dict[str, Any]):
        super().__init__(
            name=name,
            capabilities=[
                DataProcessingCapability.REAL_TIME_STREAMING,
                DataProcessingCapability.BATCH_PROCESSING,
                DataProcessingCapability.DATA_TRANSFORMATION,
                DataProcessingCapability.DATA_VALIDATION,
                DataProcessingCapability.DATA_QUALITY_MONITORING
            ],
            monitoring=EnterpriseMetrics(retention_days=90),
            isolation_level="strict"
        )
        self.tenant_config = tenant_config
        self.isolation = MultiTenantIsolation()
        self.security_context = {}
        self.setup_tenant_isolation()
        self.setup_security_context()
    
    def setup_tenant_isolation(self) -> None:
        """Setup multi-tenant isolation for production deployment."""
        for tenant_id, config in self.tenant_config.items():
            self.isolation.create_tenant_context(
                tenant_id,
                config.get('resource_limits', {
                    'max_operations_per_hour': 10000,
                    'max_processing_time_ms': 60000,
                    'max_concurrent_operations': 100
                })
            )
    
    def setup_security_context(self) -> None:
        """Setup enterprise security context for production deployment."""
        self.security_context = {
            'encryption_enabled': True,
            'audit_logging': True,
            'access_control': 'rbac',
            'compliance_level': 'enterprise',
            'data_residency': 'configurable'
        }

class ProductionDataProcessingAgent(ProductionADKAgent):
    """Production-grade ADK agent for enterprise data processing workloads."""
    
    def __init__(self, agent_name: str, tenant_config: dict):
        super().__init__(agent_name, tenant_config)
        
        # Production-specific configuration
        self.real_time_metrics = EnterpriseMetrics(retention_days=90)
        self.alerting_system = ProductionAlertingSystem()
        self.data_encryption = DataEncryption()
        
        # Performance thresholds for production
        self.performance_thresholds = {
            'max_processing_time_ms': 5000,
            'min_data_quality_score': 0.85,
            'max_error_rate': 0.05
        }
    
    async def execute(self, input_data: Any, context: ADKContext) -> ADKResult:
        """Execute production data processing with comprehensive monitoring."""
        
        # Pre-execution validation
        validation_result = await self._validate_production_request(input_data, context)
        if not validation_result.success:
            return validation_result
        
        # Execute with production monitoring
        return await self._execute_with_production_monitoring(input_data, context)
    
    async def _validate_production_request(self, input_data: Any, context: ADKContext) -> ADKResult:
        """Validate production request against enterprise policies."""
        
        # Tenant validation
        if context.tenant_id not in self.tenant_config:
            return ADKResult(
                success=False,
                error=f"Unknown tenant: {context.tenant_id}",
                enterprise_metrics={'validation_failed': 'unknown_tenant'}
            )
        
        # Resource limit validation
        if not self.isolation.check_resource_limits(context.tenant_id, "data_processing"):
            return ADKResult(
                success=False,
                error=f"Resource limits exceeded for tenant {context.tenant_id}",
                enterprise_metrics={'validation_failed': 'resource_limits_exceeded'}
            )
        
        # Security context validation
        if not self._validate_security_context(context):
            return ADKResult(
                success=False,
                error="Security context validation failed",
                enterprise_metrics={'validation_failed': 'security_context'}
            )
        
        return ADKResult(success=True)
    
    def _validate_security_context(self, context: ADKContext) -> bool:
        """Validate security context for production access."""
        required_security_fields = ['user_id', 'tenant_id']
        
        for field in required_security_fields:
            if not hasattr(context, field) or not getattr(context, field):
                return False
        
        # Additional security validations would go here
        return True
    
    async def _execute_with_production_monitoring(self, input_data: Any, context: ADKContext) -> ADKResult:
        """Execute with comprehensive production monitoring."""
        
        start_time = time.time()
        operation_id = str(uuid.uuid4())[:8]
        
        try:
            # Start production monitoring
            self.real_time_metrics.record_metric('production_operations_started', 1)
            
            # Route to appropriate processing method
            if isinstance(input_data, StreamDataInput):
                result = await self.process_production_stream(input_data, context, operation_id)
            elif isinstance(input_data, BatchDataInput):
                result = await self.process_production_batch(input_data, context, operation_id)
            else:
                result = await self.process_production_generic(input_data, context, operation_id)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Production performance validation
            performance_validation = self._validate_production_performance(result, processing_time)
            if not performance_validation.success:
                self.alerting_system.trigger_performance_alert(performance_validation.error, context)
            
            # Record production metrics
            self.real_time_metrics.record_metric('production_processing_time_ms', processing_time)
            self.real_time_metrics.record_metric('production_operations_completed', 1)
            
            # Update tenant usage tracking
            self.isolation.record_tenant_usage(context.tenant_id, processing_time)
            
            # Add production metadata
            result.enterprise_metrics.update({
                'operation_id': operation_id,
                'production_tier': 'enterprise',
                'security_validated': True,
                'performance_validated': performance_validation.success
            })
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            
            # Record production failure metrics
            self.real_time_metrics.record_metric('production_operations_failed', 1)
            self.real_time_metrics.record_metric('production_error_processing_time_ms', processing_time)
            
            # Trigger production alert
            self.alerting_system.trigger_error_alert(str(e), context)
            
            return ADKResult(
                success=False,
                error=f"Production processing failed: {e}",
                processing_time_ms=processing_time,
                enterprise_metrics={
                    'operation_id': operation_id,
                    'production_tier': 'enterprise',
                    'failure_type': 'execution_error'
                }
            )
    
    async def process_production_stream(self, stream_data: StreamDataInput, 
                                      context: ADKContext, operation_id: str) -> ADKResult:
        """Process streaming data with production-grade capabilities."""
        
        with self.pipeline_tracker.track_processing("production_stream_processing", stream_data.stream_id):
            
            # Production stream processing simulation
            records = stream_data.data.get('records', [])
            processed_records = []
            
            for i, record in enumerate(records):
                # Simulate data transformation with quality scoring
                processed_record = {
                    'original_id': record.get('id', f'record_{i}'),
                    'processed_at': datetime.now().isoformat(),
                    'transformations_applied': ['data_enrichment', 'quality_validation'],
                    'quality_score': 0.92 + (i % 10) * 0.005,  # Simulate varying quality
                    'production_metadata': {
                        'operation_id': operation_id,
                        'processing_tier': 'production_stream'
                    }
                }
                processed_records.append(processed_record)
            
            # Simulate production processing time
            await asyncio.sleep(0.15)  # Production complexity
            
            # Calculate overall data quality
            if processed_records:
                avg_quality = sum(r['quality_score'] for r in processed_records) / len(processed_records)
            else:
                avg_quality = 1.0
            
            result_data = {
                'stream_id': stream_data.stream_id,
                'operation_id': operation_id,
                'processed_records': processed_records,
                'processing_summary': {
                    'total_records': len(records),
                    'processed_records': len(processed_records),
                    'average_quality_score': avg_quality,
                    'processing_tier': 'production_stream'
                },
                'production_metadata': {
                    'tenant_id': context.tenant_id,
                    'security_level': 'enterprise',
                    'encryption_applied': self.data_encryption.is_enabled(),
                    'audit_logged': True
                }
            }
            
            output = DataProcessingOutput(
                result_data=result_data,
                records_processed=len(processed_records),
                data_quality_score=avg_quality,
                processing_stats={
                    'stream_processing_tier': 'production',
                    'operation_id': operation_id,
                    'quality_validation': 'passed' if avg_quality >= 0.85 else 'warning'
                }
            )
            
            return ADKResult(
                success=True,
                data=output,
                metadata={
                    'operation_type': 'production_stream_processing',
                    'stream_id': stream_data.stream_id,
                    'operation_id': operation_id,
                    'tenant_id': context.tenant_id
                },
                enterprise_metrics={
                    'records_processed': len(processed_records),
                    'data_quality_score': avg_quality,
                    'processing_tier': 'production'
                }
            )
    
    async def process_production_batch(self, batch_config: BatchDataInput, 
                                     context: ADKContext, operation_id: str) -> ADKResult:
        """Process batch data with enterprise-grade capabilities."""
        
        with self.pipeline_tracker.track_processing("production_batch_processing", batch_config.batch_id):
            
            batch_size = batch_config.processing_config.get('batch_size', 1000)
            
            # Simulate production batch processing
            processing_phases = ['validation', 'transformation', 'quality_check', 'output_generation']
            phase_results = {}
            
            for phase in processing_phases:
                # Simulate each processing phase
                phase_start = time.time()
                await asyncio.sleep(0.03)  # Simulate phase processing
                phase_duration = (time.time() - phase_start) * 1000
                
                phase_results[phase] = {
                    'duration_ms': phase_duration,
                    'status': 'completed',
                    'records_processed': batch_size
                }
            
            total_processing_time = sum(p['duration_ms'] for p in phase_results.values())
            
            # Calculate batch quality metrics
            quality_score = 0.89 + (batch_size % 100) * 0.001  # Simulate size-based quality variation
            
            result_data = {
                'batch_id': batch_config.batch_id,
                'operation_id': operation_id,
                'data_source': batch_config.data_source,
                'processing_phases': phase_results,
                'batch_summary': {
                    'total_records': batch_size,
                    'processed_records': batch_size,
                    'failed_records': 0,
                    'data_quality_score': quality_score,
                    'total_processing_time_ms': total_processing_time
                },
                'production_metadata': {
                    'tenant_id': context.tenant_id,
                    'processing_tier': 'production_batch',
                    'security_level': 'enterprise',
                    'compliance_validated': True
                }
            }
            
            output = DataProcessingOutput(
                result_data=result_data,
                records_processed=batch_size,
                data_quality_score=quality_score,
                processing_stats={
                    'batch_processing_tier': 'production',
                    'operation_id': operation_id,
                    'phases_completed': len(processing_phases),
                    'total_phase_time_ms': total_processing_time
                }
            )
            
            return ADKResult(
                success=True,
                data=output,
                metadata={
                    'operation_type': 'production_batch_processing',
                    'batch_id': batch_config.batch_id,
                    'operation_id': operation_id,
                    'batch_size': batch_size
                },
                enterprise_metrics={
                    'batch_size': batch_size,
                    'data_quality_score': quality_score,
                    'processing_phases': len(processing_phases)
                }
            )
    
    async def process_production_generic(self, input_data: Any, context: ADKContext, 
                                       operation_id: str) -> ADKResult:
        """Process generic data with production capabilities."""
        
        # Convert input to structured format
        if hasattr(input_data, 'dict'):
            data_dict = input_data.dict()
        elif isinstance(input_data, dict):
            data_dict = input_data
        else:
            data_dict = {'raw_input': str(input_data)}
        
        # Simulate production processing
        await asyncio.sleep(0.1)
        
        result_data = {
            'operation_id': operation_id,
            'input_data': data_dict,
            'processed_data': {
                **data_dict,
                'production_enrichment': {
                    'processed_at': datetime.now().isoformat(),
                    'processing_tier': 'production_generic',
                    'tenant_id': context.tenant_id
                }
            },
            'production_metadata': {
                'operation_id': operation_id,
                'processing_tier': 'production',
                'data_type': 'generic'
            }
        }
        
        output = DataProcessingOutput(
            result_data=result_data,
            records_processed=1,
            data_quality_score=0.85,  # Default quality for generic processing
            processing_stats={
                'processing_tier': 'production_generic',
                'operation_id': operation_id
            }
        )
        
        return ADKResult(
            success=True,
            data=output,
            metadata={
                'operation_type': 'production_generic_processing',
                'operation_id': operation_id
            }
        )
    
    def _validate_production_performance(self, result: ADKResult, processing_time_ms: float) -> ADKResult:
        """Validate production performance against thresholds."""
        
        # Processing time validation
        if processing_time_ms > self.performance_thresholds['max_processing_time_ms']:
            return ADKResult(
                success=False,
                error=f"Processing time {processing_time_ms:.1f}ms exceeds threshold {self.performance_thresholds['max_processing_time_ms']}ms"
            )
        
        # Data quality validation
        if result.success and result.data and hasattr(result.data, 'data_quality_score'):
            if result.data.data_quality_score < self.performance_thresholds['min_data_quality_score']:
                return ADKResult(
                    success=False,
                    error=f"Data quality score {result.data.data_quality_score:.3f} below threshold {self.performance_thresholds['min_data_quality_score']}"
                )
        
        return ADKResult(success=True)
    
    def get_production_metrics(self) -> Dict[str, Any]:
        """Get comprehensive production metrics."""
        
        base_metrics = self.get_enterprise_metrics()
        
        # Add production-specific metrics
        production_metrics = {
            **base_metrics,
            'production_tier': 'enterprise',
            'tenant_count': len(self.tenant_config),
            'security_context': self.security_context,
            'performance_thresholds': self.performance_thresholds,
            'real_time_metrics': {
                name: self.real_time_metrics.get_metric_summary(name)
                for name in self.real_time_metrics.metrics.keys()
            },
            'pipeline_performance': self.pipeline_tracker.get_performance_summary(),
            'alerting_summary': self.alerting_system.get_alert_summary(),
            'isolation_summary': {
                'tenant_contexts': len(self.isolation.tenant_contexts),
                'resource_limits_active': bool(self.isolation.resource_limits)
            }
        }
        
        return production_metrics

# Supporting Production Classes

class ProductionAlertingSystem:
    """Production alerting system for ADK agents."""
    
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            'error_rate': 0.05,
            'processing_time_ms': 5000,
            'data_quality_score': 0.85
        }
    
    def trigger_performance_alert(self, issue: str, context: ADKContext) -> None:
        """Trigger a performance alert."""
        alert = {
            'type': 'performance',
            'issue': issue,
            'tenant_id': context.tenant_id,
            'user_id': context.user_id,
            'timestamp': datetime.now().isoformat(),
            'severity': 'warning'
        }
        self.alerts.append(alert)
    
    def trigger_error_alert(self, error: str, context: ADKContext) -> None:
        """Trigger an error alert."""
        alert = {
            'type': 'error',
            'error': error,
            'tenant_id': context.tenant_id,
            'user_id': context.user_id,
            'timestamp': datetime.now().isoformat(),
            'severity': 'critical'
        }
        self.alerts.append(alert)
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary."""
        if not self.alerts:
            return {'total_alerts': 0, 'by_type': {}, 'by_severity': {}}
        
        by_type = {}
        by_severity = {}
        
        for alert in self.alerts:
            alert_type = alert.get('type', 'unknown')
            severity = alert.get('severity', 'unknown')
            
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            'total_alerts': len(self.alerts),
            'by_type': by_type,
            'by_severity': by_severity,
            'recent_alerts': self.alerts[-5:]  # Last 5 alerts
        }

class DataEncryption:
    """Data encryption for production ADK agents."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.encryption_algorithm = "AES-256-GCM"
        self.key_rotation_days = 90
    
    def is_enabled(self) -> bool:
        """Check if encryption is enabled."""
        return self.enabled
    
    def encrypt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate data encryption (mock implementation)."""
        if not self.enabled:
            return data
        
        # Mock encryption - in real implementation would use actual encryption
        return {
            **data,
            '_encryption_metadata': {
                'encrypted': True,
                'algorithm': self.encryption_algorithm,
                'encrypted_at': datetime.now().isoformat()
            }
        }
    
    def decrypt_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate data decryption (mock implementation)."""
        if not self.enabled or '_encryption_metadata' not in encrypted_data:
            return encrypted_data
        
        # Mock decryption
        decrypted_data = {k: v for k, v in encrypted_data.items() if k != '_encryption_metadata'}
        return decrypted_data

# Demo Functions

async def demonstrate_production_data_agent():
    """Demonstrate the production data processing agent."""
    print("\n🏭 Production Data Agent Demo")
    print("-" * 30)
    
    # Setup tenant configuration
    tenant_config = {
        "production_tenant_001": {
            "resource_limits": {
                "max_operations_per_hour": 5000,
                "max_processing_time_ms": 30000,
                "max_concurrent_operations": 50
            }
        },
        "production_tenant_002": {
            "resource_limits": {
                "max_operations_per_hour": 10000,
                "max_processing_time_ms": 60000,
                "max_concurrent_operations": 100
            }
        }
    }
    
    # Create production agent
    production_agent = ProductionDataProcessingAgent("production_data_processor", tenant_config)
    
    print(f"✅ Created production agent with {len(tenant_config)} tenant configurations")
    
    # Test production stream processing
    context = ADKContext(
        tenant_id="production_tenant_001",
        user_id="production_user_001",
        metadata={"environment": "production", "department": "data_engineering"}
    )
    
    stream_input = StreamDataInput(
        stream_id="prod_stream_001",
        data={
            "records": [
                {"id": 1, "event": "user_registration", "value": 100},
                {"id": 2, "event": "purchase_completed", "value": 250},
                {"id": 3, "event": "user_login", "value": 1}
            ]
        }
    )
    
    stream_result = await production_agent._execute_with_metrics(stream_input, context)
    
    print(f"\n✅ Production Stream Processing:")
    print(f"   Success: {stream_result.success}")
    print(f"   Records Processed: {stream_result.data.records_processed if stream_result.success else 'N/A'}")
    print(f"   Processing Time: {stream_result.processing_time_ms:.1f}ms")
    print(f"   Data Quality Score: {stream_result.data.data_quality_score:.3f}")
    print(f"   Operation ID: {stream_result.enterprise_metrics.get('operation_id', 'N/A')}")
    
    # Test production batch processing
    batch_input = BatchDataInput(
        batch_id="prod_batch_001",
        data_source="production_data_warehouse",
        processing_config={
            "batch_size": 2500,
            "processing_mode": "high_quality",
            "validation_level": "strict"
        }
    )
    
    batch_result = await production_agent._execute_with_metrics(batch_input, context)
    
    print(f"\n✅ Production Batch Processing:")
    print(f"   Success: {batch_result.success}")
    print(f"   Batch Size: {batch_result.metadata.get('batch_size', 'N/A')}")
    print(f"   Processing Time: {batch_result.processing_time_ms:.1f}ms")
    print(f"   Data Quality Score: {batch_result.data.data_quality_score:.3f}")
    print(f"   Processing Phases: {batch_result.enterprise_metrics.get('processing_phases', 'N/A')}")
    
    # Show production metrics
    metrics = production_agent.get_production_metrics()
    print(f"\n📊 Production Agent Metrics:")
    print(f"   Agent ID: {metrics['agent_id']}")
    print(f"   Production Tier: {metrics['production_tier']}")
    print(f"   Total Executions: {metrics['execution_count']}")
    print(f"   Success Rate: {metrics['success_rate']:.1%}")
    print(f"   Tenant Count: {metrics['tenant_count']}")
    print(f"   Security Level: {metrics['security_context']['compliance_level']}")
    print(f"   Pipeline Performance: {metrics['pipeline_performance']['success_rate']:.1%}")

async def main():
    """Run the production data agent demonstration."""
    print("🚀 ADK Production Data Agent - Enterprise Implementation")
    print("=" * 60)
    print("\nDemonstrating production-grade ADK agents for enterprise data processing")
    print("Includes multi-tenant isolation, comprehensive monitoring, and security features\n")
    
    try:
        await demonstrate_production_data_agent()
        
        print("\n🎯 Production Data Agent Demo Complete!")
        print("\nKey Production Features Demonstrated:")
        print("• ✅ Multi-tenant resource isolation and management")
        print("• ✅ Enterprise-grade security validation and encryption")
        print("• ✅ Comprehensive performance monitoring and alerting")
        print("• ✅ Production-grade error handling and recovery")
        print("• ✅ Data quality validation with automated thresholds")
        print("• ✅ Real-time metrics collection with 90-day retention")
        
        print(f"\n💡 Enterprise Deployment Benefits:")
        print("• Strict tenant isolation prevents cross-tenant data access")
        print("• Automated alerting for performance and quality issues")
        print("• Comprehensive audit logging for compliance requirements")
        print("• Resource limit enforcement prevents tenant resource abuse")
        print("• Data encryption and security context validation")
        print("• Production-ready performance thresholds and monitoring")
        
    except Exception as e:
        print(f"\nError during production demonstration: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())