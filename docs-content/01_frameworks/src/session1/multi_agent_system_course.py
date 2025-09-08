#!/usr/bin/env python3
"""
Multi-Agent System implementation matching Session 1 course content
Coordinator for distributed data processing agents
"""

from base_agent_course import BaseAgent
from typing import Dict, List, Any
import time
from dataclasses import dataclass


@dataclass
class ProcessingResult:
    """Result from agent processing"""
    agent_name: str
    success: bool
    data: Dict[str, Any]
    processing_time: float
    quality_score: float = 0.0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class DataIngestionAgent(BaseAgent):
    """Specialized agent for multi-source data intake"""
    
    def ingest_data_batch(self, data_batch: dict) -> ProcessingResult:
        """Ingest data from multiple sources"""
        print("📥 DataIngestionAgent: Starting data ingestion")
        
        start_time = time.time()
        
        # Simulate ingestion from multiple sources
        sources = data_batch.get("sources", ["s3", "database", "api"])
        ingested_data = {
            "total_records": 0,
            "sources_processed": [],
            "data_formats": [],
            "ingestion_metadata": {}
        }
        
        errors = []
        
        for source in sources:
            try:
                source_data = self._ingest_from_source(source, data_batch)
                ingested_data["total_records"] += source_data["records"]
                ingested_data["sources_processed"].append(source)
                ingested_data["data_formats"].extend(source_data["formats"])
                ingested_data["ingestion_metadata"][source] = source_data["metadata"]
                
                time.sleep(0.1)  # Simulate processing time
                
            except Exception as e:
                errors.append(f"Failed to ingest from {source}: {str(e)}")
        
        processing_time = time.time() - start_time
        success = len(errors) == 0
        
        return ProcessingResult(
            agent_name="DataIngestionAgent",
            success=success,
            data=ingested_data,
            processing_time=processing_time,
            quality_score=0.9 if success else 0.5,
            errors=errors
        )

    def _ingest_from_source(self, source: str, data_batch: dict) -> dict:
        """Ingest data from specific source"""
        source_configs = {
            "s3": {"records": 10000, "formats": ["parquet", "json"], "latency": 0.5},
            "database": {"records": 25000, "formats": ["structured"], "latency": 0.3},
            "api": {"records": 5000, "formats": ["json", "xml"], "latency": 0.8},
            "kafka": {"records": 50000, "formats": ["avro", "json"], "latency": 0.2}
        }
        
        config = source_configs.get(source, {"records": 1000, "formats": ["unknown"], "latency": 0.1})
        
        return {
            "records": int(config["records"] * data_batch.get("size_multiplier", 1.0)),
            "formats": config["formats"],
            "metadata": {
                "source": source,
                "ingestion_time": time.time(),
                "latency": config["latency"]
            }
        }


class DataQualityAgent(BaseAgent):
    """Specialized agent for data integrity validation"""
    
    def validate_data_quality(self, ingested_result: ProcessingResult) -> ProcessingResult:
        """Check data integrity and quality"""
        print("🔍 DataQualityAgent: Validating data quality")
        
        start_time = time.time()
        
        if not ingested_result.success:
            return ProcessingResult(
                agent_name="DataQualityAgent",
                success=False,
                data={},
                processing_time=time.time() - start_time,
                errors=["Cannot validate quality of failed ingestion"]
            )
        
        ingested_data = ingested_result.data
        quality_metrics = self._run_quality_checks(ingested_data)
        
        # Determine overall quality score
        quality_score = self._calculate_quality_score(quality_metrics)
        
        validation_result = {
            "quality_score": quality_score,
            "total_records_validated": ingested_data["total_records"],
            "quality_metrics": quality_metrics,
            "validation_passed": quality_score > 0.7,
            "data_ready_for_processing": quality_score > 0.6,
            "recommendations": self._generate_quality_recommendations(quality_metrics)
        }
        
        processing_time = time.time() - start_time
        
        return ProcessingResult(
            agent_name="DataQualityAgent", 
            success=True,
            data=validation_result,
            processing_time=processing_time,
            quality_score=quality_score
        )

    def _run_quality_checks(self, ingested_data: dict) -> dict:
        """Run comprehensive quality validation checks"""
        total_records = ingested_data["total_records"]
        
        # Simulate quality check results
        return {
            "completeness": min(0.95, 0.8 + (total_records % 100) / 500),
            "accuracy": min(0.92, 0.85 + (total_records % 73) / 365),
            "consistency": min(0.88, 0.82 + (total_records % 47) / 235),
            "timeliness": 0.94,
            "validity": min(0.90, 0.83 + (total_records % 29) / 145),
            "duplicate_rate": max(0.02, (total_records % 17) / 850),
            "null_rate": max(0.01, (total_records % 23) / 1150),
            "schema_compliance": 0.96
        }

    def _calculate_quality_score(self, metrics: dict) -> float:
        """Calculate overall quality score"""
        weights = {
            "completeness": 0.2,
            "accuracy": 0.25,
            "consistency": 0.15,
            "timeliness": 0.1,
            "validity": 0.2,
            "schema_compliance": 0.1
        }
        
        # Penalize for high duplicate and null rates
        penalties = metrics["duplicate_rate"] * 0.5 + metrics["null_rate"] * 0.3
        
        weighted_score = sum(metrics[metric] * weight for metric, weight in weights.items())
        return max(0.0, min(1.0, weighted_score - penalties))

    def _generate_quality_recommendations(self, metrics: dict) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if metrics["completeness"] < 0.8:
            recommendations.append("Improve data completeness - significant missing values detected")
        if metrics["accuracy"] < 0.8:
            recommendations.append("Review data accuracy - validation rules may need adjustment")
        if metrics["duplicate_rate"] > 0.05:
            recommendations.append("Implement deduplication process - high duplicate rate detected")
        if metrics["null_rate"] > 0.1:
            recommendations.append("Address null values - consider imputation or exclusion strategies")
        if metrics["consistency"] < 0.8:
            recommendations.append("Improve data consistency across sources")
            
        return recommendations


class DataTransformationAgent(BaseAgent):
    """Specialized agent for data processing and enrichment"""
    
    def transform_data(self, validated_result: ProcessingResult) -> ProcessingResult:
        """Transform high-quality data using standard pipeline"""
        print("⚙️  DataTransformationAgent: Applying standard transformations")
        return self._apply_transformations(validated_result, "standard")
    
    def clean_and_transform(self, validated_result: ProcessingResult) -> ProcessingResult:
        """Clean and transform lower-quality data with enhanced processing"""
        print("🧹 DataTransformationAgent: Applying enhanced cleaning and transformation")
        return self._apply_transformations(validated_result, "enhanced")
    
    def _apply_transformations(self, validated_result: ProcessingResult, mode: str) -> ProcessingResult:
        """Apply data transformations based on processing mode"""
        start_time = time.time()
        
        if not validated_result.success:
            return ProcessingResult(
                agent_name="DataTransformationAgent",
                success=False,
                data={},
                processing_time=time.time() - start_time,
                errors=["Cannot transform invalid data"]
            )
        
        validated_data = validated_result.data
        original_records = validated_data.get("total_records_validated", 0)
        
        # Apply transformations based on mode
        if mode == "enhanced":
            transformation_result = self._enhanced_transformation(validated_data)
        else:
            transformation_result = self._standard_transformation(validated_data)
        
        processing_time = time.time() - start_time
        
        return ProcessingResult(
            agent_name="DataTransformationAgent",
            success=transformation_result["success"],
            data=transformation_result,
            processing_time=processing_time,
            quality_score=transformation_result["output_quality_score"]
        )

    def _standard_transformation(self, validated_data: dict) -> dict:
        """Apply standard data transformations"""
        time.sleep(0.3)  # Simulate processing
        
        records_processed = validated_data.get("total_records_validated", 0)
        
        return {
            "transformation_mode": "standard",
            "records_input": records_processed,
            "records_output": int(records_processed * 0.98),  # Small loss due to filtering
            "transformations_applied": [
                "data_type_conversion",
                "basic_validation",
                "standard_formatting",
                "primary_key_generation"
            ],
            "output_quality_score": min(0.92, validated_data.get("quality_score", 0.8) + 0.05),
            "success": True,
            "processing_efficiency": 0.94
        }

    def _enhanced_transformation(self, validated_data: dict) -> dict:
        """Apply enhanced data cleaning and transformations"""
        time.sleep(0.5)  # More processing time for enhanced mode
        
        records_processed = validated_data.get("total_records_validated", 0)
        
        return {
            "transformation_mode": "enhanced",
            "records_input": records_processed,
            "records_output": int(records_processed * 0.92),  # More loss due to aggressive cleaning
            "transformations_applied": [
                "aggressive_deduplication",
                "null_value_imputation", 
                "outlier_detection_removal",
                "schema_normalization",
                "data_enrichment",
                "quality_scoring",
                "validation_tagging"
            ],
            "output_quality_score": min(0.95, validated_data.get("quality_score", 0.6) + 0.25),
            "success": True,
            "processing_efficiency": 0.88,
            "cleaning_stats": {
                "duplicates_removed": int(records_processed * 0.03),
                "nulls_imputed": int(records_processed * 0.05),
                "outliers_removed": int(records_processed * 0.02)
            }
        }


class DataAnalyticsAgent(BaseAgent):
    """Specialized agent for analytical processing"""
    
    def run_analytics(self, transformed_result: ProcessingResult) -> ProcessingResult:
        """Run analytical processing on transformed data"""
        print("📊 DataAnalyticsAgent: Running analytical computations")
        
        start_time = time.time()
        
        if not transformed_result.success:
            return ProcessingResult(
                agent_name="DataAnalyticsAgent",
                success=False,
                data={},
                processing_time=time.time() - start_time,
                errors=["Cannot analyze failed transformation"]
            )
        
        transformed_data = transformed_result.data
        analytics_results = self._compute_analytics(transformed_data)
        
        processing_time = time.time() - start_time
        
        return ProcessingResult(
            agent_name="DataAnalyticsAgent",
            success=True,
            data=analytics_results,
            processing_time=processing_time,
            quality_score=0.9
        )

    def _compute_analytics(self, transformed_data: dict) -> dict:
        """Compute comprehensive analytics"""
        time.sleep(0.4)  # Simulate analytical processing
        
        records_processed = transformed_data.get("records_output", 0)
        
        return {
            "analytics_type": "comprehensive",
            "records_analyzed": records_processed,
            "statistical_summary": {
                "total_records": records_processed,
                "processing_efficiency": transformed_data.get("processing_efficiency", 0.9),
                "data_quality_improvement": 0.15,
                "completeness_score": 0.94
            },
            "insights_generated": [
                "Data quality improved significantly after transformation",
                f"Successfully processed {records_processed:,} records",
                "All analytical requirements met",
                "Data ready for downstream consumption"
            ],
            "performance_metrics": {
                "throughput_records_per_second": int(records_processed / 30),
                "memory_efficiency": 0.87,
                "cpu_utilization": 0.72
            },
            "output_datasets": [
                "processed_fact_table",
                "quality_metrics_summary", 
                "analytics_insights",
                "performance_dashboard_data"
            ]
        }


class StorageOptimizationAgent(BaseAgent):
    """Specialized agent for storage optimization and lifecycle management"""
    
    def store_with_lifecycle_policy(self, analytics_result: ProcessingResult) -> ProcessingResult:
        """Store data with intelligent lifecycle management"""
        print("💾 StorageOptimizationAgent: Optimizing storage with lifecycle policies")
        
        start_time = time.time()
        
        if not analytics_result.success:
            return ProcessingResult(
                agent_name="StorageOptimizationAgent",
                success=False,
                data={},
                processing_time=time.time() - start_time,
                errors=["Cannot store failed analytics data"]
            )
        
        analytics_data = analytics_result.data
        storage_result = self._optimize_storage(analytics_data)
        
        processing_time = time.time() - start_time
        
        return ProcessingResult(
            agent_name="StorageOptimizationAgent",
            success=True,
            data=storage_result,
            processing_time=processing_time,
            quality_score=0.95
        )

    def _optimize_storage(self, analytics_data: dict) -> dict:
        """Apply storage optimization strategies"""
        time.sleep(0.2)  # Simulate storage operations
        
        records_to_store = analytics_data.get("records_analyzed", 0)
        
        # Determine storage strategy based on data characteristics
        storage_tiers = self._determine_storage_tiers(analytics_data)
        compression_applied = self._apply_compression(analytics_data)
        lifecycle_policies = self._create_lifecycle_policies(analytics_data)
        
        return {
            "storage_optimization": "completed",
            "records_stored": records_to_store,
            "storage_tiers": storage_tiers,
            "compression": compression_applied,
            "lifecycle_policies": lifecycle_policies,
            "estimated_cost_savings": 0.35,  # 35% cost reduction
            "storage_efficiency": 0.91,
            "data_accessibility": {
                "hot_tier_access": "immediate",
                "warm_tier_access": "< 1 hour",
                "cold_tier_access": "< 24 hours"
            }
        }

    def _determine_storage_tiers(self, analytics_data: dict) -> dict:
        """Determine optimal storage tier allocation"""
        total_records = analytics_data.get("records_analyzed", 0)
        
        return {
            "hot_tier": int(total_records * 0.2),    # Recent, frequently accessed
            "warm_tier": int(total_records * 0.5),   # Occasionally accessed
            "cold_tier": int(total_records * 0.3),   # Archive, rarely accessed
            "tier_strategy": "analytics_optimized"
        }

    def _apply_compression(self, analytics_data: dict) -> dict:
        """Apply intelligent compression strategies"""
        return {
            "compression_algorithm": "adaptive_hybrid",
            "compression_ratio": 0.73,  # 27% size reduction
            "formats_optimized": ["parquet", "orc", "delta"],
            "compression_efficiency": 0.89
        }

    def _create_lifecycle_policies(self, analytics_data: dict) -> dict:
        """Create data lifecycle management policies"""
        return {
            "retention_period": "7_years",
            "tier_transition_rules": [
                "hot_to_warm: after 30 days",
                "warm_to_cold: after 180 days",
                "cold_to_archive: after 2 years"
            ],
            "automated_deletion": "after 7 years",
            "compliance_tags": ["gdpr_compliant", "sox_compliant"],
            "backup_strategy": "cross_region_replication"
        }


class DataPipelineCoordinator:
    """Coordinator for distributed data processing agents"""

    def __init__(self):
        self.agents = {
            "data_ingestion": DataIngestionAgent("DataIngestion", "Multi-source data intake specialist"),
            "quality_validation": DataQualityAgent("QualityValidation", "Data integrity validation specialist"),
            "transformation": DataTransformationAgent("DataTransformation", "Data processing and enrichment specialist"),
            "analytics": DataAnalyticsAgent("DataAnalytics", "Analytical processing specialist"),
            "storage_optimization": StorageOptimizationAgent("StorageOptimization", "Storage lifecycle management specialist")
        }
        self.pipeline_history = []

    def orchestrate_data_pipeline(self, data_batch: dict) -> dict:
        """Coordinate multi-agent data processing"""
        print("🎯 DataPipelineCoordinator: Starting multi-agent pipeline orchestration")
        print(f"📦 Processing batch: {data_batch.get('batch_id', 'unknown')}")
        
        pipeline_start = time.time()
        results = {}
        
        # Step 1: Ingestion agent handles multi-source data intake
        print("\n--- Step 1: Data Ingestion ---")
        ingested = self.agents["data_ingestion"].ingest_data_batch(data_batch)
        results["ingestion"] = ingested
        
        if not ingested.success:
            return self._handle_pipeline_failure("ingestion", results, pipeline_start)
        
        # Step 2: Quality validation agent checks data integrity  
        print("\n--- Step 2: Quality Validation ---")
        validated = self.agents["quality_validation"].validate_data_quality(ingested)
        results["validation"] = validated
        
        if not validated.success:
            return self._handle_pipeline_failure("validation", results, pipeline_start)
        
        # Step 3: Transformation agent processes and enriches data
        print("\n--- Step 3: Data Transformation ---")
        if validated.data["quality_score"] > 0.85:  # High quality threshold for analytics
            transformed = self.agents["transformation"].transform_data(validated)
        else:
            transformed = self.agents["transformation"].clean_and_transform(validated)
        
        results["transformation"] = transformed
        
        if not transformed.success:
            return self._handle_pipeline_failure("transformation", results, pipeline_start)
        
        # Step 4: Analytics agent runs analytical processing
        print("\n--- Step 4: Analytics Processing ---")
        analytics_results = self.agents["analytics"].run_analytics(transformed)
        results["analytics"] = analytics_results
        
        if not analytics_results.success:
            return self._handle_pipeline_failure("analytics", results, pipeline_start)
        
        # Step 5: Storage optimization for long-term data retention
        print("\n--- Step 5: Storage Optimization ---")
        storage_result = self.agents["storage_optimization"].store_with_lifecycle_policy(analytics_results)
        results["storage"] = storage_result
        
        # Generate final pipeline result
        pipeline_result = self._generate_pipeline_result(data_batch, results, pipeline_start)
        
        # Store pipeline execution for analysis
        self.pipeline_history.append(pipeline_result)
        
        return pipeline_result

    def _handle_pipeline_failure(self, failed_stage: str, results: dict, pipeline_start: float) -> dict:
        """Handle pipeline failure at specific stage"""
        return {
            "status": "failed",
            "failed_at_stage": failed_stage,
            "total_pipeline_time": time.time() - pipeline_start,
            "completed_stages": list(results.keys()),
            "results": results,
            "error_summary": self._extract_errors(results),
            "recovery_recommendations": self._generate_recovery_recommendations(failed_stage, results)
        }

    def _generate_pipeline_result(self, data_batch: dict, results: dict, pipeline_start: float) -> dict:
        """Generate comprehensive pipeline result"""
        total_time = time.time() - pipeline_start
        
        # Calculate overall statistics
        initial_records = results["ingestion"].data.get("total_records", 0)
        final_records = results["analytics"].data.get("records_analyzed", 0)
        
        return {
            "status": "completed",
            "batch_id": data_batch.get("batch_id", f"batch_{int(time.time())}"),
            "total_pipeline_time": total_time,
            "stages_completed": list(results.keys()),
            "overall_success": all(result.success for result in results.values()),
            "data_flow_summary": {
                "initial_records": initial_records,
                "final_records": final_records,
                "record_retention_rate": final_records / initial_records if initial_records > 0 else 0,
                "quality_improvement": self._calculate_quality_improvement(results)
            },
            "performance_summary": {
                "total_processing_time": total_time,
                "average_stage_time": total_time / len(results),
                "throughput_records_per_second": final_records / total_time if total_time > 0 else 0,
                "pipeline_efficiency": self._calculate_pipeline_efficiency(results)
            },
            "agent_performance": {
                agent_name: {
                    "processing_time": result.processing_time,
                    "quality_score": result.quality_score,
                    "success": result.success
                }
                for agent_name, result in results.items()
            },
            "final_outputs": results["analytics"].data.get("output_datasets", []),
            "storage_optimization": results["storage"].data,
            "timestamp": time.time()
        }

    def _calculate_quality_improvement(self, results: dict) -> float:
        """Calculate overall quality improvement through pipeline"""
        initial_quality = 0.7  # Assumed baseline
        final_quality = results["analytics"].quality_score
        return final_quality - initial_quality

    def _calculate_pipeline_efficiency(self, results: dict) -> float:
        """Calculate overall pipeline efficiency"""
        stage_efficiencies = []
        
        for result in results.values():
            # Base efficiency on processing time and quality score
            efficiency = result.quality_score * (1.0 / max(0.1, result.processing_time))
            stage_efficiencies.append(efficiency)
        
        return sum(stage_efficiencies) / len(stage_efficiencies) if stage_efficiencies else 0.0

    def _extract_errors(self, results: dict) -> List[str]:
        """Extract all errors from pipeline results"""
        all_errors = []
        for stage, result in results.items():
            if result.errors:
                all_errors.extend([f"{stage}: {error}" for error in result.errors])
        return all_errors

    def _generate_recovery_recommendations(self, failed_stage: str, results: dict) -> List[str]:
        """Generate recovery recommendations for failed pipeline"""
        recommendations = [
            f"Review {failed_stage} stage configuration",
            "Check data quality requirements",
            "Validate resource allocation"
        ]
        
        if failed_stage == "ingestion":
            recommendations.extend([
                "Verify data source connectivity",
                "Check source data availability",
                "Review ingestion permissions"
            ])
        elif failed_stage == "validation":
            recommendations.extend([
                "Review data quality thresholds", 
                "Check validation rule configuration",
                "Consider data cleaning pipeline"
            ])
        
        return recommendations

    def get_pipeline_analytics(self) -> dict:
        """Get comprehensive pipeline performance analytics"""
        if not self.pipeline_history:
            return {"message": "No pipeline history available"}
        
        successful_runs = [p for p in self.pipeline_history if p["overall_success"]]
        
        return {
            "total_pipeline_runs": len(self.pipeline_history),
            "success_rate": len(successful_runs) / len(self.pipeline_history),
            "average_processing_time": sum(p["total_pipeline_time"] for p in successful_runs) / len(successful_runs) if successful_runs else 0,
            "average_throughput": sum(p["performance_summary"]["throughput_records_per_second"] for p in successful_runs) / len(successful_runs) if successful_runs else 0,
            "quality_improvement_trend": sum(p["data_flow_summary"]["quality_improvement"] for p in successful_runs) / len(successful_runs) if successful_runs else 0,
            "most_common_failures": self._analyze_failure_patterns(),
            "agent_performance_summary": self._analyze_agent_performance()
        }

    def _analyze_failure_patterns(self) -> dict:
        """Analyze common failure patterns"""
        failed_runs = [p for p in self.pipeline_history if not p.get("overall_success", True)]
        failure_stages = {}
        
        for run in failed_runs:
            stage = run.get("failed_at_stage", "unknown")
            failure_stages[stage] = failure_stages.get(stage, 0) + 1
        
        return failure_stages

    def _analyze_agent_performance(self) -> dict:
        """Analyze individual agent performance across all runs"""
        agent_stats = {}
        
        for run in self.pipeline_history:
            if "agent_performance" in run:
                for agent_name, performance in run["agent_performance"].items():
                    if agent_name not in agent_stats:
                        agent_stats[agent_name] = {
                            "total_runs": 0,
                            "successful_runs": 0,
                            "total_time": 0,
                            "total_quality_score": 0
                        }
                    
                    stats = agent_stats[agent_name]
                    stats["total_runs"] += 1
                    if performance["success"]:
                        stats["successful_runs"] += 1
                    stats["total_time"] += performance["processing_time"]
                    stats["total_quality_score"] += performance["quality_score"]
        
        # Calculate averages
        for agent_name, stats in agent_stats.items():
            stats["success_rate"] = stats["successful_runs"] / stats["total_runs"] if stats["total_runs"] > 0 else 0
            stats["avg_processing_time"] = stats["total_time"] / stats["total_runs"] if stats["total_runs"] > 0 else 0
            stats["avg_quality_score"] = stats["total_quality_score"] / stats["total_runs"] if stats["total_runs"] > 0 else 0
        
        return agent_stats


if __name__ == "__main__":
    print("🎯 Multi-Agent System Course Example - Distributed Data Processing")
    
    # Create multi-agent coordinator
    coordinator = DataPipelineCoordinator()
    
    # Test different data batch scenarios
    test_batches = [
        {
            "batch_id": "high_quality_batch_001",
            "sources": ["s3", "database"],
            "size_multiplier": 1.0,
            "expected_quality": "high"
        },
        {
            "batch_id": "complex_multi_source_002", 
            "sources": ["s3", "database", "api", "kafka"],
            "size_multiplier": 1.5,
            "expected_quality": "mixed"
        },
        {
            "batch_id": "large_legacy_batch_003",
            "sources": ["legacy_system", "database"],
            "size_multiplier": 2.0,
            "expected_quality": "low"
        }
    ]
    
    print("Processing multiple data batches through multi-agent pipeline...\n")
    
    for batch in test_batches:
        print(f"{'='*80}")
        print(f"🚀 Processing: {batch['batch_id']}")
        print(f"{'='*80}")
        
        # Execute pipeline
        result = coordinator.orchestrate_data_pipeline(batch)
        
        # Display results
        print(f"\n📊 Pipeline Results:")
        print(f"   Status: {result['status'].upper()}")
        print(f"   Total Time: {result['total_pipeline_time']:.2f}s")
        
        if result['status'] == 'completed':
            data_flow = result['data_flow_summary']
            performance = result['performance_summary']
            
            print(f"   Records: {data_flow['initial_records']:,} → {data_flow['final_records']:,}")
            print(f"   Retention Rate: {data_flow['record_retention_rate']:.1%}")
            print(f"   Quality Improvement: +{data_flow['quality_improvement']:.2f}")
            print(f"   Throughput: {performance['throughput_records_per_second']:.0f} records/sec")
            
            print(f"\n🤖 Agent Performance:")
            for agent, perf in result['agent_performance'].items():
                status = "✅" if perf['success'] else "❌"
                print(f"   {status} {agent}: {perf['processing_time']:.2f}s (quality: {perf['quality_score']:.2f})")
        
        else:
            print(f"   Failed at: {result['failed_at_stage']}")
            print(f"   Errors: {result['error_summary']}")
        
        print()  # Empty line for readability
    
    # Display overall analytics
    print(f"{'='*80}")
    print("📈 Overall Multi-Agent Pipeline Analytics")
    print(f"{'='*80}")
    
    analytics = coordinator.get_pipeline_analytics()
    print(f"Total Pipeline Runs: {analytics['total_pipeline_runs']}")
    print(f"Success Rate: {analytics['success_rate']:.1%}")
    print(f"Average Processing Time: {analytics['average_processing_time']:.2f}s")
    print(f"Average Throughput: {analytics['average_throughput']:.0f} records/sec")
    print(f"Quality Improvement Trend: +{analytics['quality_improvement_trend']:.2f}")
    
    print(f"\n🎯 Individual Agent Performance:")
    agent_performance = analytics['agent_performance_summary']
    for agent_name, stats in agent_performance.items():
        print(f"   {agent_name}:")
        print(f"      Success Rate: {stats['success_rate']:.1%}")
        print(f"      Avg Time: {stats['avg_processing_time']:.2f}s")
        print(f"      Avg Quality: {stats['avg_quality_score']:.2f}")
    
    print(f"\n🔧 Available Agents: {len(coordinator.agents)}")
    for agent_name, agent in coordinator.agents.items():
        print(f"   • {agent_name}: {agent.description}")