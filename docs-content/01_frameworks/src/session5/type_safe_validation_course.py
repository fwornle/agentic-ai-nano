# src/session5/type_safe_validation_course.py
"""
Advanced type-safe validation patterns with mock PydanticAI framework.
Demonstrates custom validators, complex validation logic, and production-ready patterns.
"""

from typing import Optional, List, Dict, Any, Union, Tuple, Set
from datetime import datetime, date, timedelta
from enum import Enum
import re
import json
import asyncio
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Import our mock framework from the main course file
from pydantic_agents_course import BaseModel, Field, ValidationError, validator, root_validator, MockAgent, Agent

# Advanced validation models

class DataFormat(str, Enum):
    """Supported data formats."""
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    AVRO = "avro"
    ORC = "orc"

class ProcessingComplexity(str, Enum):
    """Processing complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"

class ValidationLevel(str, Enum):
    """Validation strictness levels."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"

class DataSchema(BaseModel):
    """Complex data schema definition with validation."""
    schema_name: str = Field(..., min_length=3, max_length=100, description="Schema identifier")
    version: str = Field(..., regex=r'^\d+\.\d+\.\d+$', description="Semantic version")
    fields: List[Dict[str, str]] = Field(..., min_items=1, description="Schema field definitions")
    constraints: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Data constraints")
    created_date: date = Field(default_factory=date.today)
    valid_from: datetime = Field(default_factory=datetime.now)
    valid_until: Optional[datetime] = Field(None, description="Schema expiration")
    
    @validator('schema_name')
    def validate_schema_name(cls, v):
        """Validate schema naming conventions."""
        if not re.match(r'^[a-z][a-z0-9_]*[a-z0-9]$', v):
            raise ValueError("Schema name must be snake_case starting and ending with letter/number")
        
        reserved_names = {'system', 'admin', 'root', 'config'}
        if v.lower() in reserved_names:
            raise ValueError(f"Schema name '{v}' is reserved")
        
        return v
    
    @validator('fields')
    def validate_fields(cls, v):
        """Validate field definitions."""
        required_keys = {'name', 'type'}
        field_names = set()
        
        for i, field in enumerate(v):
            if not isinstance(field, dict):
                raise ValueError(f"Field {i} must be a dictionary")
            
            # Check required keys
            missing_keys = required_keys - set(field.keys())
            if missing_keys:
                raise ValueError(f"Field {i} missing required keys: {missing_keys}")
            
            # Validate field name
            field_name = field['name']
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', field_name):
                raise ValueError(f"Field name '{field_name}' must start with letter and contain only alphanumeric/underscore")
            
            # Check for duplicate field names
            if field_name in field_names:
                raise ValueError(f"Duplicate field name: {field_name}")
            field_names.add(field_name)
            
            # Validate field type
            valid_types = {'string', 'integer', 'float', 'boolean', 'datetime', 'date', 'array', 'object'}
            field_type = field['type']
            if field_type not in valid_types:
                raise ValueError(f"Field '{field_name}' has invalid type '{field_type}'. Valid types: {valid_types}")
        
        return v
    
    @root_validator
    def validate_schema_consistency(cls, values):
        """Validate overall schema consistency."""
        valid_from = values.get('valid_from')
        valid_until = values.get('valid_until')
        
        if valid_from and valid_until:
            if valid_until <= valid_from:
                raise ValueError("valid_until must be after valid_from")
            
            # Warn about very short validity periods
            duration = valid_until - valid_from
            if duration.days < 7:
                # In production, this might be a warning rather than an error
                pass  # Allow but could log warning
        
        # Validate constraints against fields
        constraints = values.get('constraints', {})
        fields = values.get('fields', [])
        field_names = {field['name'] for field in fields}
        
        for constraint_field in constraints.keys():
            if constraint_field not in field_names:
                raise ValueError(f"Constraint references non-existent field: {constraint_field}")
        
        return values

class DataProcessingJob(BaseModel):
    """Complex job definition with advanced validation."""
    job_id: str = Field(..., regex=r'^job_[0-9]{8}_[a-f0-9]{8}$', description="Job identifier")
    name: str = Field(..., min_length=5, max_length=200, description="Human readable job name")
    input_schema: DataSchema = Field(..., description="Input data schema")
    output_format: DataFormat = Field(default=DataFormat.PARQUET, description="Output data format")
    complexity: ProcessingComplexity = Field(default=ProcessingComplexity.MODERATE)
    validation_level: ValidationLevel = Field(default=ValidationLevel.STANDARD)
    max_memory_gb: int = Field(default=4, ge=1, le=1024, description="Maximum memory allocation")
    max_runtime_hours: int = Field(default=2, ge=1, le=48, description="Maximum runtime")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="Number of retry attempts")
    dependencies: List[str] = Field(default_factory=list, description="Job dependencies")
    tags: Set[str] = Field(default_factory=set, description="Job classification tags")
    priority_score: float = Field(default=5.0, ge=1.0, le=10.0, description="Job priority")
    environment_config: Dict[str, Any] = Field(default_factory=dict, description="Environment variables")
    
    @validator('name')
    def validate_job_name(cls, v):
        """Validate job name conventions."""
        # No special characters except spaces, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError("Job name can only contain letters, numbers, spaces, hyphens, and underscores")
        
        # Must not be all caps (shouting)
        if v.isupper() and len(v) > 10:
            raise ValueError("Job name should not be all uppercase")
        
        # Check for common typos
        problematic_words = ['temp', 'test', 'debug', 'tmp']
        name_lower = v.lower()
        for word in problematic_words:
            if word in name_lower and len(v) < 20:
                raise ValueError(f"Job name contains '{word}' - ensure this is not a temporary/test job")
        
        return v
    
    @validator('dependencies')
    def validate_dependencies(cls, v):
        """Validate job dependencies."""
        if len(v) > 20:
            raise ValueError("Too many dependencies (max 20)")
        
        # Check for self-dependency (would need job_id from root_validator)
        dependency_set = set(v)
        if len(dependency_set) != len(v):
            raise ValueError("Duplicate dependencies found")
        
        # Validate dependency format
        for dep in v:
            if not re.match(r'^job_[0-9]{8}_[a-f0-9]{8}$', dep):
                raise ValueError(f"Invalid dependency format: {dep}")
        
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate job tags."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError("All tags must be strings")
            if len(tag) < 2 or len(tag) > 30:
                raise ValueError(f"Tag '{tag}' must be 2-30 characters")
            if not re.match(r'^[a-z0-9\-_]+$', tag):
                raise ValueError(f"Tag '{tag}' must be lowercase alphanumeric with hyphens/underscores only")
        
        return v
    
    @validator('environment_config')
    def validate_environment_config(cls, v):
        """Validate environment configuration."""
        if len(v) > 50:
            raise ValueError("Maximum 50 environment variables allowed")
        
        # Check for sensitive data patterns
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'credential']
        for key, value in v.items():
            key_lower = key.lower()
            for pattern in sensitive_patterns:
                if pattern in key_lower:
                    if not isinstance(value, str) or len(value) < 10:
                        raise ValueError(f"Environment variable '{key}' appears to contain sensitive data but is too short")
        
        # Validate key names
        for key in v.keys():
            if not re.match(r'^[A-Z][A-Z0-9_]*$', key):
                raise ValueError(f"Environment variable '{key}' must be UPPERCASE_WITH_UNDERSCORES")
        
        return v
    
    @root_validator
    def validate_job_configuration(cls, values):
        """Validate overall job configuration."""
        complexity = values.get('complexity')
        max_memory_gb = values.get('max_memory_gb', 4)
        max_runtime_hours = values.get('max_runtime_hours', 2)
        validation_level = values.get('validation_level')
        
        # Memory requirements based on complexity
        if complexity == ProcessingComplexity.SIMPLE and max_memory_gb > 8:
            raise ValueError("Simple jobs should not require more than 8GB memory")
        elif complexity == ProcessingComplexity.ENTERPRISE and max_memory_gb < 16:
            raise ValueError("Enterprise jobs typically require at least 16GB memory")
        
        # Runtime validation based on complexity
        if complexity == ProcessingComplexity.SIMPLE and max_runtime_hours > 4:
            raise ValueError("Simple jobs should complete within 4 hours")
        elif complexity == ProcessingComplexity.COMPLEX and max_runtime_hours < 2:
            raise ValueError("Complex jobs typically need at least 2 hours")
        
        # Validation level consistency
        if complexity == ProcessingComplexity.ENTERPRISE and validation_level == ValidationLevel.BASIC:
            raise ValueError("Enterprise jobs should use at least STANDARD validation")
        
        # Check for circular dependencies (simplified check)
        job_id = values.get('job_id')
        dependencies = values.get('dependencies', [])
        if job_id and job_id in dependencies:
            raise ValueError("Job cannot depend on itself")
        
        return values

class DataQualityProfile(BaseModel):
    """Advanced data quality profile with comprehensive validation."""
    profile_id: str = Field(..., regex=r'^profile_[a-z0-9_]+$')
    dataset_name: str = Field(..., min_length=1, max_length=100)
    quality_dimensions: Dict[str, float] = Field(..., description="Quality scores by dimension")
    sample_statistics: Dict[str, Any] = Field(default_factory=dict)
    anomalies_detected: List[Dict[str, Any]] = Field(default_factory=list)
    data_lineage: Optional[List[str]] = Field(default=None)
    assessment_date: datetime = Field(default_factory=datetime.now)
    next_assessment: datetime = Field(..., description="Scheduled next assessment")
    compliance_status: Dict[str, bool] = Field(default_factory=dict)
    remediation_actions: List[str] = Field(default_factory=list)
    
    @validator('quality_dimensions')
    def validate_quality_dimensions(cls, v):
        """Validate quality dimension scores."""
        required_dimensions = {
            'completeness', 'accuracy', 'consistency', 
            'timeliness', 'validity', 'uniqueness'
        }
        
        # Check for required dimensions
        missing_dimensions = required_dimensions - set(v.keys())
        if missing_dimensions:
            raise ValueError(f"Missing required quality dimensions: {missing_dimensions}")
        
        # Validate score ranges
        for dimension, score in v.items():
            if not isinstance(score, (int, float)):
                raise ValueError(f"Quality score for '{dimension}' must be numeric")
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"Quality score for '{dimension}' must be between 0.0 and 1.0")
        
        # Business rule: overall quality should be consistent
        overall_avg = sum(v.values()) / len(v)
        extreme_variations = [dim for dim, score in v.items() if abs(score - overall_avg) > 0.5]
        if len(extreme_variations) > 2:
            raise ValueError(f"Too many dimensions with extreme variations from average: {extreme_variations}")
        
        return v
    
    @validator('anomalies_detected')
    def validate_anomalies(cls, v):
        """Validate anomaly detection results."""
        if len(v) > 1000:
            raise ValueError("Too many anomalies detected (max 1000) - check detection parameters")
        
        required_keys = {'type', 'severity', 'field', 'description'}
        severity_levels = {'low', 'medium', 'high', 'critical'}
        
        for i, anomaly in enumerate(v):
            if not isinstance(anomaly, dict):
                raise ValueError(f"Anomaly {i} must be a dictionary")
            
            missing_keys = required_keys - set(anomaly.keys())
            if missing_keys:
                raise ValueError(f"Anomaly {i} missing keys: {missing_keys}")
            
            if anomaly['severity'] not in severity_levels:
                raise ValueError(f"Anomaly {i} has invalid severity: {anomaly['severity']}")
            
            if len(anomaly['description']) < 10:
                raise ValueError(f"Anomaly {i} description too short (minimum 10 characters)")
        
        return v
    
    @validator('next_assessment')
    def validate_next_assessment(cls, v, values):
        """Validate next assessment scheduling."""
        assessment_date = values.get('assessment_date', datetime.now())
        
        if v <= assessment_date:
            raise ValueError("Next assessment must be scheduled after current assessment")
        
        time_diff = v - assessment_date
        if time_diff.days > 365:
            raise ValueError("Next assessment cannot be scheduled more than 1 year in advance")
        elif time_diff.days < 1:
            raise ValueError("Next assessment must be at least 1 day in the future")
        
        return v
    
    @root_validator
    def validate_profile_consistency(cls, values):
        """Validate overall profile consistency."""
        quality_dimensions = values.get('quality_dimensions', {})
        anomalies_detected = values.get('anomalies_detected', [])
        compliance_status = values.get('compliance_status', {})
        
        # High number of anomalies should correlate with lower quality scores
        if len(anomalies_detected) > 100:
            avg_quality = sum(quality_dimensions.values()) / len(quality_dimensions) if quality_dimensions else 0
            if avg_quality > 0.8:
                raise ValueError("High anomaly count inconsistent with high quality scores")
        
        # Critical anomalies should trigger compliance failures
        critical_anomalies = [a for a in anomalies_detected if a.get('severity') == 'critical']
        if critical_anomalies and all(compliance_status.values()):
            raise ValueError("Critical anomalies detected but all compliance checks passed")
        
        return values

# Advanced validation agents

def create_schema_validation_agent():
    """Create an agent specialized in schema validation."""
    
    agent = Agent(
        model='mock-gpt-4',
        result_type=Dict[str, Any],
        system_prompt="""You are a data schema validation specialist. You ensure 
        data schemas are well-formed, consistent, and follow best practices."""
    )
    
    @agent.tool
    async def validate_schema_evolution(ctx, old_schema: DataSchema, new_schema: DataSchema) -> Dict[str, Any]:
        """Validate schema evolution compatibility."""
        
        # Mock schema evolution validation
        compatibility_check = {
            'backward_compatible': True,
            'forward_compatible': True,
            'breaking_changes': [],
            'recommendations': [],
            'migration_required': False
        }
        
        # Check version progression
        old_version = [int(x) for x in old_schema.version.split('.')]
        new_version = [int(x) for x in new_schema.version.split('.')]
        
        if new_version <= old_version:
            compatibility_check['breaking_changes'].append("Schema version must increase")
            compatibility_check['backward_compatible'] = False
        
        # Check field changes
        old_fields = {f['name']: f for f in old_schema.fields}
        new_fields = {f['name']: f for f in new_schema.fields}
        
        # Removed fields break backward compatibility
        removed_fields = set(old_fields.keys()) - set(new_fields.keys())
        if removed_fields:
            compatibility_check['breaking_changes'].extend([
                f"Field '{field}' was removed" for field in removed_fields
            ])
            compatibility_check['backward_compatible'] = False
        
        # Changed field types
        for field_name in old_fields.keys() & new_fields.keys():
            if old_fields[field_name]['type'] != new_fields[field_name]['type']:
                compatibility_check['breaking_changes'].append(
                    f"Field '{field_name}' type changed from {old_fields[field_name]['type']} to {new_fields[field_name]['type']}"
                )
        
        return compatibility_check
    
    @agent.tool 
    async def suggest_schema_improvements(ctx, schema: DataSchema) -> List[str]:
        """Suggest schema improvements based on best practices."""
        
        suggestions = []
        
        # Check field naming consistency
        field_names = [f['name'] for f in schema.fields]
        snake_case_pattern = re.compile(r'^[a-z][a-z0-9_]*$')
        
        inconsistent_names = [name for name in field_names if not snake_case_pattern.match(name)]
        if inconsistent_names:
            suggestions.append(f"Use snake_case for field names: {inconsistent_names}")
        
        # Check for common missing fields
        common_fields = {'id', 'created_at', 'updated_at'}
        missing_common = common_fields - set(field_names)
        if missing_common:
            suggestions.append(f"Consider adding common fields: {missing_common}")
        
        # Check field count
        if len(schema.fields) > 50:
            suggestions.append("Schema has many fields - consider decomposing into related schemas")
        elif len(schema.fields) < 3:
            suggestions.append("Schema has very few fields - ensure it captures necessary data")
        
        return suggestions
    
    return agent

def create_job_validation_agent():
    """Create an agent specialized in job configuration validation."""
    
    agent = Agent(
        model='mock-gpt-4',
        result_type=Dict[str, Any],
        system_prompt="""You are a data processing job validation specialist. 
        You ensure job configurations are optimal, secure, and follow best practices."""
    )
    
    @agent.tool
    async def validate_resource_allocation(ctx, job: DataProcessingJob) -> Dict[str, Any]:
        """Validate job resource allocation."""
        
        allocation_analysis = {
            'memory_appropriate': True,
            'runtime_realistic': True,
            'cost_estimate': 'reasonable',
            'optimization_suggestions': [],
            'risk_factors': []
        }
        
        # Memory analysis based on complexity
        complexity_memory_map = {
            ProcessingComplexity.SIMPLE: (1, 4),
            ProcessingComplexity.MODERATE: (2, 8),
            ProcessingComplexity.COMPLEX: (8, 32),
            ProcessingComplexity.ENTERPRISE: (16, 128)
        }
        
        min_mem, max_mem = complexity_memory_map[job.complexity]
        
        if job.max_memory_gb < min_mem:
            allocation_analysis['memory_appropriate'] = False
            allocation_analysis['optimization_suggestions'].append(
                f"Increase memory allocation to at least {min_mem}GB for {job.complexity.value} complexity"
            )
        elif job.max_memory_gb > max_mem:
            allocation_analysis['optimization_suggestions'].append(
                f"Memory allocation of {job.max_memory_gb}GB may be excessive for {job.complexity.value} complexity"
            )
            allocation_analysis['cost_estimate'] = 'high'
        
        # Runtime analysis
        if job.max_runtime_hours > 24:
            allocation_analysis['risk_factors'].append("Long-running jobs have higher failure risk")
        
        return allocation_analysis
    
    @agent.tool
    async def analyze_job_dependencies(ctx, jobs: List[DataProcessingJob]) -> Dict[str, Any]:
        """Analyze job dependency graph for issues."""
        
        dependency_analysis = {
            'dependency_graph_valid': True,
            'circular_dependencies': [],
            'orphaned_jobs': [],
            'critical_path_analysis': {},
            'recommendations': []
        }
        
        # Build dependency graph
        job_map = {job.job_id: job for job in jobs}
        
        # Check for missing dependencies
        for job in jobs:
            missing_deps = [dep for dep in job.dependencies if dep not in job_map]
            if missing_deps:
                dependency_analysis['dependency_graph_valid'] = False
                dependency_analysis['recommendations'].append(
                    f"Job {job.job_id} has missing dependencies: {missing_deps}"
                )
        
        # Simple circular dependency check (full implementation would use graph algorithms)
        for job in jobs:
            if job.job_id in job.dependencies:
                dependency_analysis['circular_dependencies'].append(job.job_id)
        
        return dependency_analysis
    
    return agent

def create_quality_validation_agent():
    """Create an agent specialized in data quality validation."""
    
    agent = Agent(
        model='mock-gpt-4',
        result_type=Dict[str, Any],
        system_prompt="""You are a data quality validation specialist. You assess 
        data quality profiles and ensure they meet enterprise standards."""
    )
    
    @agent.tool
    async def assess_quality_trends(ctx, profiles: List[DataQualityProfile]) -> Dict[str, Any]:
        """Assess quality trends across multiple profiles."""
        
        trend_analysis = {
            'overall_trend': 'stable',
            'improving_dimensions': [],
            'declining_dimensions': [],
            'quality_score_avg': 0.0,
            'risk_assessment': 'low',
            'action_items': []
        }
        
        if not profiles:
            return trend_analysis
        
        # Calculate average quality scores
        all_dimensions = set()
        for profile in profiles:
            all_dimensions.update(profile.quality_dimensions.keys())
        
        dimension_averages = {}
        for dimension in all_dimensions:
            scores = [p.quality_dimensions.get(dimension, 0) for p in profiles]
            dimension_averages[dimension] = sum(scores) / len(scores)
        
        trend_analysis['quality_score_avg'] = sum(dimension_averages.values()) / len(dimension_averages)
        
        # Risk assessment based on quality scores
        if trend_analysis['quality_score_avg'] < 0.6:
            trend_analysis['risk_assessment'] = 'high'
            trend_analysis['action_items'].append('Immediate quality improvement required')
        elif trend_analysis['quality_score_avg'] < 0.8:
            trend_analysis['risk_assessment'] = 'medium'
            trend_analysis['action_items'].append('Quality monitoring recommended')
        
        return trend_analysis
    
    @agent.tool
    async def generate_quality_report(ctx, profile: DataQualityProfile) -> str:
        """Generate a comprehensive quality report."""
        
        report_sections = []
        
        # Executive summary
        avg_quality = sum(profile.quality_dimensions.values()) / len(profile.quality_dimensions)
        report_sections.append(f"Quality Assessment Summary")
        report_sections.append(f"Dataset: {profile.dataset_name}")
        report_sections.append(f"Overall Quality Score: {avg_quality:.2%}")
        
        # Dimension breakdown
        report_sections.append("\nQuality Dimensions:")
        for dimension, score in profile.quality_dimensions.items():
            status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
            report_sections.append(f"  {status} {dimension.capitalize()}: {score:.2%}")
        
        # Anomalies
        if profile.anomalies_detected:
            report_sections.append(f"\nAnomalies Detected: {len(profile.anomalies_detected)}")
            severity_counts = {}
            for anomaly in profile.anomalies_detected:
                severity = anomaly['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            for severity, count in severity_counts.items():
                report_sections.append(f"  {severity.capitalize()}: {count}")
        
        # Recommendations
        if profile.remediation_actions:
            report_sections.append("\nRecommended Actions:")
            for action in profile.remediation_actions:
                report_sections.append(f"  • {action}")
        
        return "\n".join(report_sections)
    
    return agent

# Advanced validation orchestrator

class ValidationOrchestrator:
    """Orchestrates complex validation workflows."""
    
    def __init__(self):
        self.schema_agent = create_schema_validation_agent()
        self.job_agent = create_job_validation_agent()
        self.quality_agent = create_quality_validation_agent()
        self.validation_history: List[Dict[str, Any]] = []
    
    async def comprehensive_validation(self, data_object: BaseModel) -> Dict[str, Any]:
        """Perform comprehensive validation on any BaseModel object."""
        
        validation_start = datetime.now()
        results = {
            'object_type': type(data_object).__name__,
            'validation_timestamp': validation_start.isoformat(),
            'model_validation': {'passed': True, 'errors': []},
            'business_validation': {'passed': True, 'warnings': []},
            'agent_validation': {'completed': False, 'results': {}},
            'overall_status': 'pending'
        }
        
        try:
            # 1. Basic model validation (already done during instantiation)
            results['model_validation'] = {
                'passed': True,
                'errors': [],
                'field_count': len(data_object.__annotations__),
                'validated_fields': list(data_object.__annotations__.keys())
            }
            
            # 2. Business rule validation
            business_results = await self._validate_business_rules(data_object)
            results['business_validation'] = business_results
            
            # 3. Agent-based validation
            if isinstance(data_object, DataSchema):
                agent_results = await self.schema_agent.run(
                    f"Validate schema: {data_object.schema_name}"
                )
                results['agent_validation'] = {
                    'completed': True,
                    'agent_type': 'schema_validation',
                    'results': agent_results
                }
            elif isinstance(data_object, DataProcessingJob):
                agent_results = await self.job_agent.run(
                    f"Validate job configuration: {data_object.name}"
                )
                results['agent_validation'] = {
                    'completed': True,
                    'agent_type': 'job_validation',
                    'results': agent_results
                }
            elif isinstance(data_object, DataQualityProfile):
                agent_results = await self.quality_agent.run(
                    f"Validate quality profile: {data_object.dataset_name}"
                )
                results['agent_validation'] = {
                    'completed': True,
                    'agent_type': 'quality_validation',
                    'results': agent_results
                }
            
            # 4. Overall status determination
            if (results['model_validation']['passed'] and 
                results['business_validation']['passed'] and
                results['agent_validation']['completed']):
                results['overall_status'] = 'passed'
            else:
                results['overall_status'] = 'failed'
            
            # Record execution time
            execution_time = (datetime.now() - validation_start).total_seconds()
            results['execution_time_seconds'] = execution_time
            
            # Store in history
            self.validation_history.append(results)
            
            return results
            
        except Exception as e:
            results['overall_status'] = 'error'
            results['error'] = str(e)
            results['execution_time_seconds'] = (datetime.now() - validation_start).total_seconds()
            
            self.validation_history.append(results)
            return results
    
    async def _validate_business_rules(self, data_object: BaseModel) -> Dict[str, Any]:
        """Apply business rule validation."""
        
        business_results = {
            'passed': True,
            'warnings': [],
            'rule_checks': []
        }
        
        # Example business rules based on object type
        if isinstance(data_object, DataProcessingJob):
            # Business rule: High priority jobs should have adequate resources
            if data_object.priority_score >= 8.0 and data_object.max_memory_gb < 8:
                business_results['warnings'].append(
                    "High priority job may need more memory allocation"
                )
            
            # Business rule: Enterprise jobs should have monitoring tags
            if data_object.complexity == ProcessingComplexity.ENTERPRISE:
                monitoring_tags = {'monitoring', 'production', 'enterprise'}
                if not monitoring_tags & data_object.tags:
                    business_results['warnings'].append(
                        "Enterprise jobs should include monitoring/production tags"
                    )
        
        elif isinstance(data_object, DataQualityProfile):
            # Business rule: Recent assessments for critical data
            if datetime.now() - data_object.assessment_date > timedelta(days=30):
                business_results['warnings'].append(
                    "Quality assessment is over 30 days old - consider refresh"
                )
            
            # Business rule: Critical anomalies require immediate action
            critical_anomalies = [
                a for a in data_object.anomalies_detected 
                if a.get('severity') == 'critical'
            ]
            if critical_anomalies and not data_object.remediation_actions:
                business_results['warnings'].append(
                    "Critical anomalies detected but no remediation actions specified"
                )
        
        return business_results
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validation activities."""
        
        if not self.validation_history:
            return {'no_validations': True}
        
        total_validations = len(self.validation_history)
        passed_validations = len([v for v in self.validation_history if v['overall_status'] == 'passed'])
        failed_validations = len([v for v in self.validation_history if v['overall_status'] == 'failed'])
        error_validations = len([v for v in self.validation_history if v['overall_status'] == 'error'])
        
        object_types = {}
        for validation in self.validation_history:
            obj_type = validation['object_type']
            object_types[obj_type] = object_types.get(obj_type, 0) + 1
        
        execution_times = [
            v['execution_time_seconds'] for v in self.validation_history 
            if 'execution_time_seconds' in v
        ]
        
        return {
            'total_validations': total_validations,
            'passed_validations': passed_validations,
            'failed_validations': failed_validations,
            'error_validations': error_validations,
            'success_rate': (passed_validations / total_validations * 100) if total_validations > 0 else 0,
            'object_types_validated': object_types,
            'average_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
            'total_execution_time': sum(execution_times)
        }

# Demo function

async def demo_advanced_validation():
    """Demonstrate advanced validation patterns."""
    print("🎯 Advanced Type-Safe Validation Course Demo")
    print("=" * 50)
    
    orchestrator = ValidationOrchestrator()
    
    print("\n1. Complex Schema Validation")
    print("-" * 30)
    
    try:
        # Create a valid complex schema
        schema = DataSchema(
            schema_name="customer_transaction_events",
            version="1.2.3",
            fields=[
                {"name": "customer_id", "type": "string", "required": True},
                {"name": "transaction_amount", "type": "float", "constraints": {"min": 0}},
                {"name": "transaction_date", "type": "datetime"},
                {"name": "merchant_category", "type": "string"},
                {"name": "payment_method", "type": "string"}
            ],
            constraints={
                "customer_id": {"unique": True},
                "transaction_amount": {"min": 0.01, "max": 10000.00}
            }
        )
        
        print(f"✅ Created schema: {schema.schema_name} v{schema.version}")
        
        validation_result = await orchestrator.comprehensive_validation(schema)
        print(f"   Validation Status: {validation_result['overall_status']}")
        print(f"   Fields Validated: {validation_result['model_validation']['field_count']}")
        
        if validation_result['business_validation']['warnings']:
            print("   Warnings:")
            for warning in validation_result['business_validation']['warnings']:
                print(f"     - {warning}")
        
    except ValidationError as e:
        print(f"❌ Schema validation failed:")
        for error in e.errors():
            print(f"   - {error['field']}: {error['error']}")
    
    print("\n2. Complex Job Configuration Validation")
    print("-" * 40)
    
    try:
        # Create a complex job configuration
        job = DataProcessingJob(
            job_id="job_20240101_abc12345",
            name="Customer Behavior Analysis Pipeline",
            input_schema=schema,
            complexity=ProcessingComplexity.COMPLEX,
            validation_level=ValidationLevel.STRICT,
            max_memory_gb=32,
            max_runtime_hours=6,
            retry_attempts=2,
            dependencies=["job_20240101_def67890"],
            tags={"machine-learning", "customer-analytics", "production"},
            priority_score=8.5,
            environment_config={
                "SPARK_DRIVER_MEMORY": "8g",
                "SPARK_EXECUTOR_MEMORY": "16g",
                "MAX_PARTITIONS": "200"
            }
        )
        
        print(f"✅ Created job: {job.name}")
        print(f"   Complexity: {job.complexity.value}")
        print(f"   Memory: {job.max_memory_gb}GB")
        print(f"   Runtime: {job.max_runtime_hours}h")
        print(f"   Tags: {len(job.tags)}")
        
        validation_result = await orchestrator.comprehensive_validation(job)
        print(f"   Validation Status: {validation_result['overall_status']}")
        
    except ValidationError as e:
        print(f"❌ Job validation failed:")
        for error in e.errors():
            print(f"   - {error['field']}: {error['error']}")
    
    print("\n3. Data Quality Profile Validation")
    print("-" * 35)
    
    try:
        # Create a data quality profile
        quality_profile = DataQualityProfile(
            profile_id="profile_customer_transactions",
            dataset_name="customer_transaction_events",
            quality_dimensions={
                "completeness": 0.96,
                "accuracy": 0.89,
                "consistency": 0.92,
                "timeliness": 0.85,
                "validity": 0.94,
                "uniqueness": 0.98
            },
            sample_statistics={
                "total_records": 2500000,
                "sample_size": 50000,
                "null_percentage": 0.04
            },
            anomalies_detected=[
                {
                    "type": "outlier",
                    "severity": "medium",
                    "field": "transaction_amount",
                    "description": "Transaction amounts exceeding 3 standard deviations from mean"
                },
                {
                    "type": "pattern",
                    "severity": "low", 
                    "field": "merchant_category",
                    "description": "Unusual merchant category distribution on weekends"
                }
            ],
            next_assessment=datetime.now() + timedelta(days=7),
            compliance_status={
                "gdpr": True,
                "pci_dss": True,
                "sox": True
            },
            remediation_actions=[
                "Implement outlier detection in real-time pipeline",
                "Review weekend transaction patterns with business team"
            ]
        )
        
        print(f"✅ Created quality profile: {quality_profile.dataset_name}")
        avg_quality = sum(quality_profile.quality_dimensions.values()) / len(quality_profile.quality_dimensions)
        print(f"   Average Quality Score: {avg_quality:.2%}")
        print(f"   Anomalies Detected: {len(quality_profile.anomalies_detected)}")
        
        validation_result = await orchestrator.comprehensive_validation(quality_profile)
        print(f"   Validation Status: {validation_result['overall_status']}")
        
    except ValidationError as e:
        print(f"❌ Quality profile validation failed:")
        for error in e.errors():
            print(f"   - {error['field']}: {error['error']}")
    
    print("\n4. Validation Error Handling")
    print("-" * 30)
    
    try:
        # Attempt to create invalid objects to demonstrate error handling
        invalid_schema = DataSchema(
            schema_name="",  # Too short
            version="1.0",   # Invalid format
            fields=[],       # Empty fields
            valid_until=datetime.now() - timedelta(days=1)  # In the past
        )
    except ValidationError as e:
        print("✅ Correctly caught validation errors:")
        for error in e.errors():
            print(f"   - {error['field']}: {error['error']}")
    
    print("\n5. Validation Summary")
    print("-" * 20)
    
    summary = orchestrator.get_validation_summary()
    print(f"Total Validations: {summary['total_validations']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Average Execution Time: {summary['average_execution_time']:.3f}s")
    print("Object Types Validated:")
    for obj_type, count in summary['object_types_validated'].items():
        print(f"  - {obj_type}: {count}")
    
    print("\n🎯 Advanced Validation Demo Complete!")
    print("\nKey Advanced Validation Features Demonstrated:")
    print("• Complex multi-field validation with business rules")
    print("• Cross-field validation and consistency checks")
    print("• Custom validator functions and root validators")
    print("• Agent-based validation for domain-specific rules")
    print("• Comprehensive error handling and reporting")
    print("• Validation orchestration and workflow management")
    print("• Performance monitoring and execution tracking")

if __name__ == "__main__":
    asyncio.run(demo_advanced_validation())