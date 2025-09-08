# src/session5/pydantic_agents_course.py
"""
PydanticAI-style type-safe agent implementation with mock framework.
Demonstrates type safety, validation, and structured outputs without external dependencies.
"""

from typing import Optional, List, Dict, Any, Union, Callable, TypeVar, Generic
from datetime import datetime
from enum import Enum
import json
import asyncio
import logging
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import re

# Mock Pydantic functionality for course demonstration

class ValidationError(Exception):
    """Mock ValidationError for field validation failures."""
    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors_list = errors
        super().__init__(f"Validation failed: {errors}")
    
    def errors(self):
        return self.errors_list

class MockField:
    """Mock Pydantic Field for validation constraints."""
    def __init__(self, default=None, min_length=None, max_length=None, 
                 ge=None, le=None, regex=None, description=None, **kwargs):
        self.default = default
        self.min_length = min_length  
        self.max_length = max_length
        self.ge = ge  # greater or equal
        self.le = le  # less or equal
        self.regex = regex
        self.description = description
        self.kwargs = kwargs

def Field(default=None, **kwargs):
    """Mock Field function matching Pydantic API."""
    if default is ...:  # Ellipsis means required field
        default = None
        kwargs['required'] = True
    return MockField(default=default, **kwargs)

class BaseModel:
    """Mock BaseModel with validation functionality."""
    
    def __init__(self, **data):
        self._validate_and_set(data)
    
    def _validate_and_set(self, data):
        """Validate fields and set attributes."""
        errors = []
        annotations = getattr(self.__class__, '__annotations__', {})
        
        for field_name, field_type in annotations.items():
            # Get field definition from class
            field_def = getattr(self.__class__, field_name, None)
            
            if field_name in data:
                value = data[field_name]
                try:
                    validated_value = self._validate_field(field_name, value, field_type, field_def)
                    setattr(self, field_name, validated_value)
                except ValueError as e:
                    errors.append({
                        'field': field_name,
                        'error': str(e),
                        'input': value
                    })
            else:
                # Handle defaults
                if isinstance(field_def, MockField) and field_def.default is not None:
                    setattr(self, field_name, field_def.default)
                elif hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
                    # Optional field
                    setattr(self, field_name, None)
                else:
                    errors.append({
                        'field': field_name,
                        'error': 'Field is required',
                        'input': None
                    })
        
        if errors:
            raise ValidationError(errors)
        
        # Run custom validators
        self._run_custom_validators()
    
    def _validate_field(self, field_name, value, field_type, field_def):
        """Validate individual field."""
        if isinstance(field_def, MockField):
            # String length validation
            if isinstance(value, str):
                if field_def.min_length is not None and len(value) < field_def.min_length:
                    raise ValueError(f"String too short, minimum {field_def.min_length} characters")
                if field_def.max_length is not None and len(value) > field_def.max_length:
                    raise ValueError(f"String too long, maximum {field_def.max_length} characters")
                if field_def.regex and not re.match(field_def.regex, value):
                    raise ValueError(f"String does not match pattern {field_def.regex}")
            
            # Numeric validation
            if isinstance(value, (int, float)):
                if field_def.ge is not None and value < field_def.ge:
                    raise ValueError(f"Value must be >= {field_def.ge}")
                if field_def.le is not None and value > field_def.le:
                    raise ValueError(f"Value must be <= {field_def.le}")
            
            # List validation
            if isinstance(value, list) and hasattr(field_def, 'min_items'):
                if len(value) < field_def.min_items:
                    raise ValueError(f"List must have at least {field_def.min_items} items")
        
        return value
    
    def _run_custom_validators(self):
        """Run custom validation methods."""
        for method_name in dir(self.__class__):
            method = getattr(self.__class__, method_name)
            if hasattr(method, '_validator_field'):
                field_name = method._validator_field
                if hasattr(self, field_name):
                    field_value = getattr(self, field_name)
                    try:
                        validated = method(self.__class__, field_value)
                        setattr(self, field_name, validated)
                    except ValueError as e:
                        raise ValidationError([{
                            'field': field_name,
                            'error': str(e),
                            'input': field_value
                        }])
    
    def dict(self):
        """Convert model to dictionary."""
        result = {}
        annotations = getattr(self.__class__, '__annotations__', {})
        for field_name in annotations.keys():
            if hasattr(self, field_name):
                result[field_name] = getattr(self, field_name)
        return result
    
    def json(self, indent=2):
        """Convert model to JSON string."""
        return json.dumps(self.dict(), indent=indent, default=str)

def validator(field_name: str):
    """Decorator for custom field validators."""
    def decorator(func):
        func._validator_field = field_name
        return func
    return decorator

def root_validator(func):
    """Decorator for root validators."""
    func._is_root_validator = True
    return func

# Mock PydanticAI classes

@dataclass
class MockRunContext:
    """Mock RunContext for dependency injection."""
    deps: Any = None
    
T = TypeVar('T')

class MockAgent:
    """Mock PydanticAI Agent for type-safe AI interactions."""
    
    def __init__(self, model: str, result_type: type = str, system_prompt: str = "", deps_type: type = None):
        self.model = model
        self.result_type = result_type
        self.system_prompt = system_prompt
        self.deps_type = deps_type
        self.tools: List[Callable] = []
        self.system_prompt_func = None
    
    def tool(self, func: Callable):
        """Register a tool with the agent."""
        self.tools.append(func)
        return func
    
    def system_prompt(self, func: Callable):
        """Register a system prompt function."""
        self.system_prompt_func = func
        return func
    
    async def run(self, query: str, deps=None):
        """Mock agent execution with type-safe response generation."""
        # Simulate AI processing
        await asyncio.sleep(0.1)
        
        # Generate mock response based on result_type
        if self.result_type == str:
            return f"Mock response for: {query}"
        
        # For BaseModel types, create instance with mock data
        if hasattr(self.result_type, '__bases__') and BaseModel in self.result_type.__bases__:
            annotations = getattr(self.result_type, '__annotations__', {})
            mock_data = {}
            
            for field_name, field_type in annotations.items():
                mock_data[field_name] = self._generate_mock_field_value(field_name, field_type)
            
            return self.result_type(**mock_data)
        
        # For dict responses
        if self.result_type == dict or self.result_type == Dict[str, Any]:
            return {
                'query': query,
                'response': 'Mock AI response',
                'confidence': 0.85,
                'timestamp': datetime.now().isoformat()
            }
        
        return f"Mock {self.result_type.__name__} response"
    
    def _generate_mock_field_value(self, field_name: str, field_type: type):
        """Generate mock values for different field types."""
        if field_type == str:
            return f"mock_{field_name}_{datetime.now().strftime('%H%M%S')}"
        elif field_type == int:
            return 42
        elif field_type == float:
            return 0.85
        elif field_type == bool:
            return True
        elif field_type == datetime:
            return datetime.now()
        elif hasattr(field_type, '__origin__') and field_type.__origin__ is list:
            return ["item1", "item2", "item3"]
        elif hasattr(field_type, '__bases__') and Enum in field_type.__bases__:
            return list(field_type)[0]
        else:
            return f"mock_{field_name}"

def Agent(model: str, result_type: type = str, system_prompt: str = "", deps_type: type = None):
    """Create a mock Agent instance."""
    return MockAgent(model, result_type, system_prompt, deps_type)

def RunContext(deps_type: type = None):
    """Create a mock RunContext."""
    return MockRunContext

# Type-safe data models for course demonstration

class Priority(str, Enum):
    """Priority levels for data processing tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProcessingStatus(str, Enum):
    """Status values for data processing."""
    QUEUED = "queued"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class DataQualityRequest(BaseModel):
    """Type-safe request for data quality assessment."""
    dataset_name: str = Field(..., min_length=1, max_length=100, description="Name of dataset to analyze")
    sample_size: int = Field(default=1000, ge=100, le=1000000, description="Number of records to sample")
    quality_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Minimum quality score")
    include_metrics: bool = Field(default=True, description="Include detailed metrics")
    priority: Priority = Field(default=Priority.MEDIUM, description="Processing priority")
    
    @validator('dataset_name')
    def validate_dataset_name(cls, v):
        """Ensure dataset name follows naming conventions."""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError("Dataset name must start with letter and contain only alphanumeric, underscore, or dash")
        return v

class DataQualityReport(BaseModel):
    """Type-safe response for data quality assessment."""
    dataset_name: str
    total_records: int = Field(..., ge=0)
    sampled_records: int = Field(..., ge=0)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    missing_values_pct: float = Field(..., ge=0.0, le=100.0)
    duplicate_rows_pct: float = Field(..., ge=0.0, le=100.0)
    outliers_pct: float = Field(..., ge=0.0, le=100.0)
    status: ProcessingStatus
    recommendations: List[str] = Field(default_factory=list)
    processing_time_ms: float = Field(..., ge=0.0)
    timestamp: datetime = Field(default_factory=datetime.now)

class FeatureExtractionRequest(BaseModel):
    """Type-safe request for feature extraction."""
    source_data: str = Field(..., min_length=10, description="Description of source data")
    feature_types: List[str] = Field(..., min_items=1, description="Types of features to extract")
    max_features: int = Field(default=100, ge=1, le=10000)
    algorithm: str = Field(default="auto", regex=r'^(auto|pca|lda|ica|random)$')
    target_correlation: Optional[float] = Field(None, ge=-1.0, le=1.0)
    
    @validator('feature_types')
    def validate_feature_types(cls, v):
        """Validate feature type specifications."""
        valid_types = {'numerical', 'categorical', 'text', 'temporal', 'image', 'audio'}
        for feature_type in v:
            if feature_type not in valid_types:
                raise ValueError(f"Invalid feature type: {feature_type}. Must be one of {valid_types}")
        return v

class FeatureExtractionResponse(BaseModel):
    """Type-safe response for feature extraction."""
    extraction_id: str = Field(..., min_length=1)
    features_extracted: int = Field(..., ge=0)
    feature_names: List[str] = Field(default_factory=list)
    extraction_method: str
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    processing_time_seconds: float = Field(..., ge=0.0)
    memory_usage_mb: float = Field(..., ge=0.0)
    status: ProcessingStatus
    
    @validator('extraction_id')
    def validate_extraction_id(cls, v):
        """Ensure extraction ID follows format."""
        if not re.match(r'^feat_\d{8}_[a-f0-9]{8}$', v):
            raise ValueError("Extraction ID must follow format: feat_YYYYMMDD_hexhexhex")
        return v

# Type-safe agent implementations

def create_data_quality_agent():
    """Create a type-safe data quality assessment agent."""
    
    agent = Agent(
        model='mock-gpt-4',
        result_type=DataQualityReport,
        system_prompt="""You are a data quality specialist who performs comprehensive 
        data quality assessments. You provide detailed quality metrics, identify 
        data issues, and recommend improvements."""
    )
    
    @agent.tool
    async def analyze_data_sample(ctx: MockRunContext, request: DataQualityRequest) -> Dict[str, Any]:
        """Analyze a sample of data for quality metrics."""
        
        # Simulate data sampling and analysis
        await asyncio.sleep(0.2)
        
        # Mock quality analysis based on dataset characteristics
        base_quality = 0.8
        if 'customer' in request.dataset_name.lower():
            base_quality = 0.9  # Customer data typically cleaner
        elif 'log' in request.dataset_name.lower():
            base_quality = 0.7  # Log data often has issues
        
        # Adjust based on sample size
        if request.sample_size > 10000:
            base_quality += 0.05  # Larger samples reveal more issues
        
        quality_metrics = {
            'overall_quality': min(base_quality, 1.0),
            'completeness': 0.95,
            'accuracy': base_quality,
            'consistency': 0.88,
            'timeliness': 0.92,
            'validity': 0.85,
            'uniqueness': 0.93
        }
        
        return quality_metrics
    
    @agent.tool
    async def detect_outliers(ctx: MockRunContext, data_description: str, threshold: float = 2.0) -> Dict[str, Any]:
        """Detect outliers in the dataset."""
        
        # Mock outlier detection
        outlier_info = {
            'outliers_detected': 47,
            'outlier_percentage': 2.3,
            'detection_method': 'statistical_z_score',
            'threshold_used': threshold,
            'outlier_fields': ['age', 'income', 'transaction_amount'],
            'severity_distribution': {
                'mild': 32,
                'moderate': 12, 
                'severe': 3
            }
        }
        
        return outlier_info
    
    @agent.tool
    async def generate_recommendations(ctx: MockRunContext, quality_metrics: Dict[str, float]) -> List[str]:
        """Generate data quality improvement recommendations."""
        
        recommendations = []
        
        if quality_metrics.get('completeness', 1.0) < 0.9:
            recommendations.append("Implement data validation rules to prevent missing values")
            recommendations.append("Consider data imputation strategies for critical fields")
        
        if quality_metrics.get('accuracy', 1.0) < 0.8:
            recommendations.append("Establish data source validation and verification processes")
            recommendations.append("Implement automated data quality checks in ETL pipeline")
        
        if quality_metrics.get('consistency', 1.0) < 0.9:
            recommendations.append("Standardize data formats and naming conventions")
            recommendations.append("Implement data governance policies across data sources")
        
        if quality_metrics.get('uniqueness', 1.0) < 0.95:
            recommendations.append("Implement duplicate detection and removal processes")
            recommendations.append("Create unique identifiers for entity resolution")
        
        if not recommendations:
            recommendations = ["Data quality is excellent - maintain current processes"]
        
        return recommendations
    
    return agent

def create_feature_extraction_agent():
    """Create a type-safe feature extraction agent."""
    
    agent = Agent(
        model='mock-gpt-4',
        result_type=FeatureExtractionResponse,
        system_prompt="""You are a feature engineering specialist who extracts 
        meaningful features from raw data for machine learning. You optimize 
        feature selection and ensure high-quality feature engineering."""
    )
    
    @agent.tool
    async def extract_numerical_features(ctx: MockRunContext, data_info: str, max_features: int) -> Dict[str, Any]:
        """Extract numerical features from data."""
        
        # Simulate feature extraction process
        await asyncio.sleep(0.3)
        
        # Mock numerical feature extraction
        numerical_features = [
            f"num_feature_{i}" for i in range(min(max_features // 3, 20))
        ]
        
        feature_stats = {
            'extracted_count': len(numerical_features),
            'feature_names': numerical_features,
            'correlation_matrix_available': True,
            'scaling_required': True,
            'missing_value_handling': 'mean_imputation'
        }
        
        return feature_stats
    
    @agent.tool 
    async def extract_categorical_features(ctx: MockRunContext, data_info: str, encoding_method: str = 'one_hot') -> Dict[str, Any]:
        """Extract and encode categorical features."""
        
        categorical_features = [
            f"cat_feature_{i}" for i in range(15)
        ]
        
        if encoding_method == 'one_hot':
            # Simulate one-hot encoding expansion
            expanded_features = []
            for feature in categorical_features[:5]:  # Limit for demonstration
                for category in ['A', 'B', 'C']:
                    expanded_features.append(f"{feature}_{category}")
        else:
            expanded_features = [f"{feature}_encoded" for feature in categorical_features]
        
        feature_stats = {
            'original_categorical': len(categorical_features),
            'encoded_features': len(expanded_features),
            'encoding_method': encoding_method,
            'feature_names': expanded_features,
            'cardinality_stats': {
                'low_cardinality': 8,
                'medium_cardinality': 5,
                'high_cardinality': 2
            }
        }
        
        return feature_stats
    
    @agent.tool
    async def extract_temporal_features(ctx: MockRunContext, temporal_columns: List[str]) -> Dict[str, Any]:
        """Extract time-based features."""
        
        temporal_features = []
        for col in temporal_columns:
            temporal_features.extend([
                f"{col}_year", f"{col}_month", f"{col}_day",
                f"{col}_hour", f"{col}_weekday", f"{col}_is_weekend"
            ])
        
        feature_stats = {
            'temporal_columns_processed': len(temporal_columns),
            'temporal_features_created': len(temporal_features),
            'feature_names': temporal_features,
            'seasonality_detected': True,
            'trend_components': ['linear', 'cyclical'],
            'time_granularity': 'hourly'
        }
        
        return feature_stats
    
    return agent

def create_validation_agent():
    """Create an agent that validates other agent outputs."""
    
    agent = Agent(
        model='mock-gpt-4',
        result_type=Dict[str, Any],
        system_prompt="""You are a validation specialist who ensures data processing 
        outputs meet quality standards and business requirements."""
    )
    
    @agent.tool
    async def validate_model_output(ctx: MockRunContext, model_instance: BaseModel) -> Dict[str, Any]:
        """Validate a Pydantic model instance."""
        
        validation_results = {
            'model_type': model_instance.__class__.__name__,
            'validation_passed': True,
            'field_count': len(model_instance.__annotations__),
            'validated_fields': [],
            'issues_found': [],
            'validation_score': 1.0
        }
        
        # Check each field
        for field_name in model_instance.__annotations__.keys():
            if hasattr(model_instance, field_name):
                field_value = getattr(model_instance, field_name)
                field_validation = {
                    'field': field_name,
                    'value_type': type(field_value).__name__,
                    'has_value': field_value is not None,
                    'passes_constraints': True
                }
                validation_results['validated_fields'].append(field_validation)
        
        return validation_results
    
    @agent.tool
    async def check_business_rules(ctx: MockRunContext, data: Dict[str, Any], rules: List[str]) -> Dict[str, Any]:
        """Validate data against business rules."""
        
        rule_results = []
        
        for rule in rules:
            # Mock business rule validation
            rule_result = {
                'rule': rule,
                'passed': True,
                'confidence': 0.95,
                'details': f"Rule '{rule}' validation completed successfully"
            }
            rule_results.append(rule_result)
        
        overall_compliance = {
            'total_rules': len(rules),
            'rules_passed': len([r for r in rule_results if r['passed']]),
            'compliance_rate': 1.0,  # All rules passed in mock
            'rule_details': rule_results
        }
        
        return overall_compliance
    
    return agent

# Production-ready error handling

class TypeSafeAgentManager:
    """Manager for coordinating type-safe agents with error handling."""
    
    def __init__(self):
        self.agents: Dict[str, MockAgent] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, name: str, agent: MockAgent):
        """Register an agent with the manager."""
        self.agents[name] = agent
        self.logger.info(f"Registered agent: {name}")
    
    async def execute_with_validation(self, agent_name: str, query: str, expected_type: type = None) -> Dict[str, Any]:
        """Execute agent with comprehensive validation."""
        start_time = datetime.now()
        
        try:
            if agent_name not in self.agents:
                raise ValueError(f"Agent {agent_name} not found")
            
            agent = self.agents[agent_name]
            result = await agent.run(query)
            
            # Validate result type if specified
            if expected_type and not isinstance(result, expected_type):
                raise TypeError(f"Expected {expected_type}, got {type(result)}")
            
            # Additional validation for BaseModel results
            if isinstance(result, BaseModel):
                validation_check = {
                    'model_valid': True,
                    'field_count': len(result.__annotations__),
                    'data_dict': result.dict()
                }
            else:
                validation_check = {
                    'result_type': type(result).__name__,
                    'result_value': str(result)[:200]  # Truncate for logging
                }
            
            execution_record = {
                'agent_name': agent_name,
                'query': query,
                'success': True,
                'result_type': type(result).__name__,
                'validation': validation_check,
                'execution_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'timestamp': start_time.isoformat()
            }
            
            self.execution_history.append(execution_record)
            
            return {
                'success': True,
                'result': result,
                'execution_info': execution_record
            }
            
        except ValidationError as e:
            error_record = {
                'agent_name': agent_name,
                'query': query,
                'success': False,
                'error_type': 'ValidationError',
                'error_details': e.errors(),
                'execution_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'timestamp': start_time.isoformat()
            }
            
            self.execution_history.append(error_record)
            self.logger.error(f"Validation error in {agent_name}: {e}")
            
            return {
                'success': False,
                'error': 'validation_failed',
                'details': e.errors(),
                'execution_info': error_record
            }
            
        except Exception as e:
            error_record = {
                'agent_name': agent_name,
                'query': query,
                'success': False,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'execution_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'timestamp': start_time.isoformat()
            }
            
            self.execution_history.append(error_record)
            self.logger.error(f"Execution error in {agent_name}: {e}")
            
            return {
                'success': False,
                'error': 'execution_failed',
                'details': str(e),
                'execution_info': error_record
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all agents."""
        if not self.execution_history:
            return {'no_executions': True}
        
        successful = [record for record in self.execution_history if record['success']]
        failed = [record for record in self.execution_history if not record['success']]
        
        execution_times = [record['execution_time_ms'] for record in successful]
        
        return {
            'total_executions': len(self.execution_history),
            'successful_executions': len(successful),
            'failed_executions': len(failed),
            'success_rate': len(successful) / len(self.execution_history) * 100,
            'average_execution_time_ms': sum(execution_times) / len(execution_times) if execution_times else 0,
            'agents_used': list(set(record['agent_name'] for record in self.execution_history)),
            'error_types': list(set(record.get('error_type', 'unknown') for record in failed))
        }

# Demo runner for course

async def demo_type_safe_agents():
    """Demonstrate type-safe agent functionality."""
    print("🎯 PydanticAI-Style Type-Safe Agents Course Demo")
    print("=" * 50)
    
    # Create agent manager
    manager = TypeSafeAgentManager()
    
    # Register agents
    quality_agent = create_data_quality_agent()
    feature_agent = create_feature_extraction_agent()
    validation_agent = create_validation_agent()
    
    manager.register_agent('data_quality', quality_agent)
    manager.register_agent('feature_extraction', feature_agent)
    manager.register_agent('validation', validation_agent)
    
    print("\n1. Data Quality Assessment with Type Safety")
    print("-" * 40)
    
    # Create a valid request
    try:
        quality_request = DataQualityRequest(
            dataset_name="customer_transactions_2024",
            sample_size=5000,
            quality_threshold=0.85,
            priority=Priority.HIGH
        )
        print(f"✅ Created valid request: {quality_request.dataset_name}")
        
        # Execute agent with validation
        result = await manager.execute_with_validation(
            'data_quality', 
            f"Assess quality of {quality_request.dataset_name}",
            DataQualityReport
        )
        
        if result['success']:
            report = result['result']
            print(f"✅ Quality Score: {report.quality_score:.2f}")
            print(f"   Missing Values: {report.missing_values_pct:.1f}%")
            print(f"   Status: {report.status.value}")
            print(f"   Recommendations: {len(report.recommendations)} items")
        
    except ValidationError as e:
        print(f"❌ Validation Error: {e.errors()}")
    
    print("\n2. Invalid Input Handling")
    print("-" * 30)
    
    # Demonstrate validation error handling
    try:
        invalid_request = DataQualityRequest(
            dataset_name="",  # Too short
            sample_size=-100,  # Invalid range
            quality_threshold=1.5  # Out of range
        )
    except ValidationError as e:
        print("✅ Validation correctly caught invalid input:")
        for error in e.errors():
            print(f"   - {error['field']}: {error['error']}")
    
    print("\n3. Feature Extraction with Type Constraints")
    print("-" * 40)
    
    try:
        feature_request = FeatureExtractionRequest(
            source_data="Customer behavioral data with transaction history",
            feature_types=["numerical", "categorical", "temporal"],
            max_features=50,
            algorithm="pca"
        )
        
        result = await manager.execute_with_validation(
            'feature_extraction',
            f"Extract features from {feature_request.source_data}",
            FeatureExtractionResponse
        )
        
        if result['success']:
            response = result['result']
            print(f"✅ Features Extracted: {response.features_extracted}")
            print(f"   Method: {response.extraction_method}")
            print(f"   Processing Time: {response.processing_time_seconds:.2f}s")
            print(f"   Memory Usage: {response.memory_usage_mb:.1f}MB")
    
    except ValidationError as e:
        print(f"❌ Feature extraction validation error: {e}")
    
    print("\n4. Performance Summary")
    print("-" * 20)
    
    summary = manager.get_performance_summary()
    print(f"Total Executions: {summary['total_executions']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Average Execution Time: {summary['average_execution_time_ms']:.1f}ms")
    print(f"Agents Used: {', '.join(summary['agents_used'])}")
    
    print("\n5. Advanced Validation Features")
    print("-" * 35)
    
    # Test custom validators
    try:
        # This should pass validation
        valid_extraction = FeatureExtractionResponse(
            extraction_id="feat_20240101_abc12345",
            features_extracted=25,
            extraction_method="automated_pca",
            quality_metrics={"accuracy": 0.92, "completeness": 0.98},
            processing_time_seconds=2.3,
            memory_usage_mb=45.2,
            status=ProcessingStatus.COMPLETED
        )
        
        validation_result = await manager.execute_with_validation(
            'validation',
            f"Validate extraction {valid_extraction.extraction_id}",
            dict
        )
        
        if validation_result['success']:
            print("✅ Advanced validation successful")
            validation_info = validation_result['result']
            print(f"   Model Type: {validation_info['model_type']}")
            print(f"   Fields Validated: {validation_info['field_count']}")
            print(f"   Validation Score: {validation_info['validation_score']}")
    
    except Exception as e:
        print(f"❌ Advanced validation error: {e}")
    
    print("\n🎯 Course Demo Complete!")
    print("\nKey Type Safety Benefits Demonstrated:")
    print("• Automatic input validation with clear error messages")
    print("• Guaranteed response structure and types")
    print("• Custom validation rules and business logic")
    print("• Comprehensive error handling and recovery")
    print("• Performance monitoring and execution tracking")
    print("• Production-ready agent coordination")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run the demo
    asyncio.run(demo_type_safe_agents())