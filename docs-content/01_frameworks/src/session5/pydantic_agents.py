# src/session5/pydantic_agents.py
"""
PydanticAI implementation showing type-safe agent development.
"""

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import json

# Type-safe data models

class Priority(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ResearchResult(BaseModel):
    """Type-safe research result structure."""
    topic: str = Field(..., description="Research topic")
    key_findings: List[str] = Field(..., description="Main research findings")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in findings")
    sources: List[str] = Field(..., description="Information sources")
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: Priority = Field(default=Priority.MEDIUM)
    
    @validator('key_findings')
    def validate_findings(cls, v):
        """Ensure we have meaningful findings."""
        if len(v) == 0:
            raise ValueError("At least one finding is required")
        for finding in v:
            if len(finding.strip()) < 10:
                raise ValueError("Findings must be at least 10 characters")
        return v
    
    @validator('sources')
    def validate_sources(cls, v):
        """Ensure sources are valid URLs or citations."""
        if len(v) == 0:
            raise ValueError("At least one source is required")
        for source in v:
            if not (source.startswith('http') or source.startswith('www') or 
                   'journal' in source.lower() or 'book' in source.lower()):
                raise ValueError(f"Invalid source format: {source}")
        return v

class AnalysisRequest(BaseModel):
    """Input validation for analysis requests."""
    data: List[float] = Field(..., min_items=1, description="Data to analyze")
    analysis_type: str = Field(..., regex=r'^(mean|median|std|trend|correlation)$')
    confidence_level: Optional[float] = Field(default=0.95, ge=0.5, le=0.99)
    include_visualization: bool = Field(default=False)
    
    @validator('data')
    def validate_data(cls, v):
        """Ensure data is meaningful."""
        if any(x < 0 for x in v):
            raise ValueError("Negative values not allowed")
        if len(set(v)) == 1:
            raise ValueError("Data must have variation for meaningful analysis")
        return v

class CodeGenerationRequest(BaseModel):
    """Request structure for code generation."""
    language: str = Field(..., regex=r'^(python|javascript|typescript|java|go)$')
    task_description: str = Field(..., min_length=10, max_length=500)
    complexity: str = Field(..., regex=r'^(simple|intermediate|advanced)$')
    include_tests: bool = Field(default=True)
    style_guide: Optional[str] = Field(default="pep8")

class GeneratedCode(BaseModel):
    """Type-safe code generation output."""
    language: str
    main_code: str = Field(..., min_length=50)
    test_code: Optional[str] = None
    documentation: str = Field(..., min_length=20)
    complexity_score: float = Field(..., ge=0.0, le=1.0)
    estimated_lines: int = Field(..., gt=0)

# Type-safe agent implementations

def create_research_agent():
    """Create a type-safe research agent."""
    
    research_agent = Agent(
        'openai:gpt-4',
        result_type=ResearchResult,
        system_prompt="""You are a research analyst who provides structured, 
        validated research results. Always include confidence scores and proper 
        source citations."""
    )
    
    @research_agent.tool
    def web_search(ctx: RunContext[str], query: str, max_results: int = 5) -> str:
        """Search the web for information with type safety."""
        
        # Input validation
        if not query.strip():
            raise ValueError("Query cannot be empty")
        if max_results < 1 or max_results > 20:
            raise ValueError("max_results must be between 1 and 20")
        
        # Simulate web search with structured results
        search_results = {
            'query': query,
            'results': [
                {
                    'title': f'Research result {i+1} for {query}',
                    'url': f'https://example.com/research/{i+1}',
                    'snippet': f'Relevant information about {query} from source {i+1}',
                    'relevance_score': 0.9 - (i * 0.1)
                }
                for i in range(min(max_results, 5))
            ],
            'search_time': datetime.now().isoformat()
        }
        
        return json.dumps(search_results, indent=2)
    
    @research_agent.tool
    def analyze_credibility(ctx: RunContext[str], source: str) -> Dict[str, Any]:
        """Analyze source credibility with structured output."""
        
        credibility_indicators = {
            'domain_authority': 0.8,
            'publication_date': 'recent',
            'author_expertise': 'verified',
            'peer_review_status': 'peer-reviewed' if 'journal' in source.lower() else 'not-peer-reviewed',
            'citation_count': 42,
            'overall_score': 0.85
        }
        
        return credibility_indicators
    
    return research_agent

def create_data_analysis_agent():
    """Create a type-safe data analysis agent."""
    
    analysis_agent = Agent(
        'openai:gpt-4',
        result_type=Dict[str, Any],  # Flexible output for various analysis types
        system_prompt="""You are a data analyst who performs statistical analysis 
        with proper validation and error handling."""
    )
    
    @analysis_agent.tool
    def statistical_analysis(
        ctx: RunContext[AnalysisRequest], 
        request: AnalysisRequest
    ) -> Dict[str, Any]:
        """Perform statistical analysis with type-safe inputs."""
        
        import statistics
        import numpy as np
        
        data = np.array(request.data)
        analysis_type = request.analysis_type
        
        results = {
            'analysis_type': analysis_type,
            'data_points': len(data),
            'confidence_level': request.confidence_level
        }
        
        if analysis_type == 'mean':
            results.update({
                'mean': float(np.mean(data)),
                'standard_error': float(np.std(data) / np.sqrt(len(data)))
            })
        
        elif analysis_type == 'median':
            results.update({
                'median': float(np.median(data)),
                'mad': float(np.median(np.abs(data - np.median(data))))  # Median Absolute Deviation
            })
        
        elif analysis_type == 'std':
            results.update({
                'standard_deviation': float(np.std(data)),
                'variance': float(np.var(data)),
                'coefficient_of_variation': float(np.std(data) / np.mean(data))
            })
        
        elif analysis_type == 'trend':
            # Simple linear trend
            x = np.arange(len(data))
            coefficients = np.polyfit(x, data, 1)
            results.update({
                'trend_slope': float(coefficients[0]),
                'trend_intercept': float(coefficients[1]),
                'trend_direction': 'increasing' if coefficients[0] > 0 else 'decreasing'
            })
        
        elif analysis_type == 'correlation':
            if len(data) < 3:
                raise ValueError("Correlation analysis requires at least 3 data points")
            
            # Auto-correlation (lag-1)
            correlation = np.corrcoef(data[:-1], data[1:])[0, 1]
            results.update({
                'autocorrelation_lag1': float(correlation),
                'correlation_strength': 'strong' if abs(correlation) > 0.7 else 'moderate' if abs(correlation) > 0.3 else 'weak'
            })
        
        # Add visualization data if requested
        if request.include_visualization:
            results['visualization_data'] = {
                'x_values': list(range(len(data))),
                'y_values': data.tolist(),
                'chart_type': 'line' if analysis_type == 'trend' else 'histogram'
            }
        
        return results
    
    @analysis_agent.tool
    def validate_data_quality(ctx: RunContext[List[float]], data: List[float]) -> Dict[str, Any]:
        """Validate data quality with type-safe checks."""
        
        import numpy as np
        
        arr = np.array(data)
        
        quality_metrics = {
            'total_points': len(data),
            'missing_values': 0,  # Assuming no missing values in this implementation
            'outliers_count': 0,
            'data_range': {
                'min': float(np.min(arr)),
                'max': float(np.max(arr)),
                'range': float(np.max(arr) - np.min(arr))
            },
            'distribution': {
                'mean': float(np.mean(arr)),
                'std': float(np.std(arr)),
                'skewness': float(np.mean(((arr - np.mean(arr)) / np.std(arr)) ** 3))
            }
        }
        
        # Detect outliers using IQR method
        q1, q3 = np.percentile(arr, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = arr[(arr < lower_bound) | (arr > upper_bound)]
        
        quality_metrics['outliers_count'] = len(outliers)
        quality_metrics['outlier_percentage'] = len(outliers) / len(arr) * 100
        
        # Overall quality score
        if quality_metrics['outlier_percentage'] < 5:
            quality_score = 0.9
        elif quality_metrics['outlier_percentage'] < 15:
            quality_score = 0.7
        else:
            quality_score = 0.5
        
        quality_metrics['quality_score'] = quality_score
        quality_metrics['quality_level'] = (
            'excellent' if quality_score > 0.8 else
            'good' if quality_score > 0.6 else
            'acceptable' if quality_score > 0.4 else
            'poor'
        )
        
        return quality_metrics
    
    return analysis_agent

def create_code_generation_agent():
    """Create a type-safe code generation agent."""
    
    code_agent = Agent(
        'openai:gpt-4',
        result_type=GeneratedCode,
        system_prompt="""You are a software developer who generates high-quality, 
        well-documented code with proper testing."""
    )
    
    @code_agent.tool
    def generate_code_snippet(
        ctx: RunContext[CodeGenerationRequest], 
        request: CodeGenerationRequest
    ) -> Dict[str, Any]:
        """Generate code with type-safe inputs and outputs."""
        
        templates = {
            'python': {
                'simple': _generate_simple_python,
                'intermediate': _generate_intermediate_python,
                'advanced': _generate_advanced_python
            },
            'javascript': {
                'simple': _generate_simple_javascript,
                'intermediate': _generate_intermediate_javascript,
                'advanced': _generate_advanced_javascript
            }
        }
        
        if request.language in templates and request.complexity in templates[request.language]:
            code_data = templates[request.language][request.complexity](request.task_description)
        else:
            code_data = _generate_generic_code(request.language, request.task_description)
        
        # Add metadata
        code_data.update({
            'language': request.language,
            'complexity_score': _calculate_complexity_score(request.complexity),
            'estimated_lines': len(code_data['main_code'].split('\n')),
            'style_guide': request.style_guide
        })
        
        # Generate tests if requested
        if request.include_tests:
            code_data['test_code'] = _generate_test_code(request.language, code_data['main_code'])
        
        return code_data
    
    return code_agent

# Helper functions for code generation

def _generate_simple_python(task_description: str) -> Dict[str, str]:
    """Generate simple Python code."""
    return {
        'main_code': f'''def solve_task():
    """
    {task_description}
    
    Returns:
        dict: Result of the task
    """
    result = {{
        'status': 'completed',
        'description': '{task_description}',
        'timestamp': datetime.now().isoformat()
    }}
    
    # Task implementation goes here
    # This is a simple template
    
    return result

if __name__ == "__main__":
    result = solve_task()
    print(result)
''',
        'documentation': f"Simple Python implementation for: {task_description}"
    }

def _generate_intermediate_python(task_description: str) -> Dict[str, str]:
    """Generate intermediate Python code."""
    return {
        'main_code': f'''from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class TaskResult:
    """Result structure for task execution."""
    success: bool
    data: Optional[Dict]
    message: str
    timestamp: datetime

class TaskProcessor:
    """
    Processes tasks with error handling and logging.
    
    Task: {task_description}
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.processed_count = 0
    
    def process(self, input_data: Dict) -> TaskResult:
        """
        Process the task with input validation.
        
        Args:
            input_data: Input parameters for the task
            
        Returns:
            TaskResult: Processing result
        """
        try:
            self.logger.info(f"Processing task: {{input_data}}")
            
            # Validate input
            if not input_data:
                raise ValueError("Input data cannot be empty")
            
            # Process the task
            result_data = self._execute_task(input_data)
            
            self.processed_count += 1
            
            return TaskResult(
                success=True,
                data=result_data,
                message="Task completed successfully",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Task processing failed: {{e}}")
            return TaskResult(
                success=False,
                data=None,
                message=str(e),
                timestamp=datetime.now()
            )
    
    def _execute_task(self, input_data: Dict) -> Dict:
        """Execute the specific task logic."""
        # Task-specific implementation
        return {{
            'processed': True,
            'input_received': input_data,
            'processing_id': self.processed_count
        }}

# Usage example
if __name__ == "__main__":
    processor = TaskProcessor()
    result = processor.process({{'sample': 'data'}})
    print(result)
''',
        'documentation': f"Intermediate Python class-based implementation for: {task_description}. Includes error handling, logging, and type hints."
    }

def _generate_advanced_python(task_description: str) -> Dict[str, str]:
    """Generate advanced Python code."""
    return {
        'main_code': f'''from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Generic, TypeVar, Protocol
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio
import logging
from contextlib import asynccontextmanager

# Type definitions
T = TypeVar('T')
ProcessorResult = TypeVar('ProcessorResult')

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Processor(Protocol[T]):
    """Protocol for task processors."""
    async def process(self, data: T) -> ProcessorResult: ...

@dataclass
class TaskMetrics:
    """Metrics for task execution."""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    memory_used: Optional[int] = None

class TaskProcessor(ABC, Generic[T]):
    """
    Abstract base class for task processors.
    
    Task: {task_description}
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{{self.__class__.__name__}}.{{name}}")
        self._metrics: List[TaskMetrics] = []
    
    @abstractmethod
    async def _execute_core_logic(self, data: T) -> Dict:
        """Execute the core task logic."""
        pass
    
    async def process_with_monitoring(self, data: T) -> Dict:
        """Process task with full monitoring and error handling."""
        metrics = TaskMetrics(start_time=datetime.now())
        
        try:
            async with self._execution_context():
                self.logger.info(f"Starting task processing: {{type(data)}}")
                
                # Validate input
                await self._validate_input(data)
                
                # Execute core logic
                result = await self._execute_core_logic(data)
                
                # Post-process results
                final_result = await self._post_process(result)
                
                metrics.end_time = datetime.now()
                metrics.duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
                
                self._metrics.append(metrics)
                
                return {{
                    'status': TaskStatus.COMPLETED.value,
                    'data': final_result,
                    'metrics': {{
                        'duration_ms': metrics.duration_ms,
                        'processor': self.name
                    }}
                }}
                
        except Exception as e:
            self.logger.error(f"Task processing failed: {{e}}")
            metrics.end_time = datetime.now()
            self._metrics.append(metrics)
            
            return {{
                'status': TaskStatus.FAILED.value,
                'error': str(e),
                'metrics': {{
                    'duration_ms': (metrics.end_time - metrics.start_time).total_seconds() * 1000
                }}
            }}
    
    async def _validate_input(self, data: T) -> None:
        """Validate input data."""
        if data is None:
            raise ValueError("Input data cannot be None")
    
    async def _post_process(self, result: Dict) -> Dict:
        """Post-process execution results."""
        return {{
            **result,
            'processed_by': self.name,
            'processing_time': datetime.now().isoformat()
        }}
    
    @asynccontextmanager
    async def _execution_context(self):
        """Context manager for execution."""
        self.logger.debug("Entering execution context")
        try:
            yield
        finally:
            self.logger.debug("Exiting execution context")
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics."""
        if not self._metrics:
            return {{'no_metrics': True}}
        
        durations = [m.duration_ms for m in self._metrics if m.duration_ms is not None]
        
        return {{
            'total_executions': len(self._metrics),
            'avg_duration_ms': sum(durations) / len(durations) if durations else 0,
            'min_duration_ms': min(durations) if durations else 0,
            'max_duration_ms': max(durations) if durations else 0
        }}

class ConcreteTaskProcessor(TaskProcessor[Dict]):
    """Concrete implementation of the task processor."""
    
    async def _execute_core_logic(self, data: Dict) -> Dict:
        """Execute the specific task logic."""
        # Simulate async processing
        await asyncio.sleep(0.1)
        
        return {{
            'input_processed': data,
            'task_description': '{task_description}',
            'execution_id': id(self),
            'complex_processing': True
        }}

# Usage example
async def main():
    processor = ConcreteTaskProcessor("advanced_processor")
    
    test_data = {{'sample': 'data', 'complexity': 'high'}}
    result = await processor.process_with_monitoring(test_data)
    
    print("Result:", result)
    print("Metrics:", processor.get_performance_metrics())

if __name__ == "__main__":
    asyncio.run(main())
''',
        'documentation': f"Advanced Python implementation for: {task_description}. Features async processing, abstract base classes, generics, protocols, context managers, and comprehensive monitoring."
    }

def _generate_simple_javascript(task_description: str) -> Dict[str, str]:
    """Generate simple JavaScript code."""
    return {
        'main_code': f'''/**
 * Simple JavaScript implementation
 * Task: {task_description}
 */

function solveTask(inputData) {{
    const result = {{
        status: 'completed',
        description: '{task_description}',
        timestamp: new Date().toISOString(),
        data: inputData
    }};
    
    // Task implementation goes here
    console.log('Processing:', inputData);
    
    return result;
}}

// Usage example
const testData = {{ sample: 'data' }};
const result = solveTask(testData);
console.log('Result:', result);

module.exports = {{ solveTask }};
''',
        'documentation': f"Simple JavaScript function for: {task_description}"
    }

def _generate_intermediate_javascript(task_description: str) -> Dict[str, str]:
    """Generate intermediate JavaScript code."""
    return {
        'main_code': f'''/**
 * Intermediate JavaScript implementation
 * Task: {task_description}
 */

class TaskProcessor {{
    constructor(name = 'DefaultProcessor') {{
        this.name = name;
        this.processedCount = 0;
        this.errors = [];
    }}
    
    async process(inputData) {{
        try {{
            this.validateInput(inputData);
            
            console.log(`Processing task with processor: ${{this.name}}`);
            
            const result = await this.executeTask(inputData);
            this.processedCount++;
            
            return {{
                success: true,
                data: result,
                processorName: this.name,
                processedCount: this.processedCount,
                timestamp: new Date().toISOString()
            }};
            
        }} catch (error) {{
            this.errors.push({{
                error: error.message,
                timestamp: new Date().toISOString(),
                input: inputData
            }});
            
            return {{
                success: false,
                error: error.message,
                processorName: this.name
            }};
        }}
    }}
    
    validateInput(inputData) {{
        if (!inputData || typeof inputData !== 'object') {{
            throw new Error('Input must be a non-null object');
        }}
    }}
    
    async executeTask(inputData) {{
        // Simulate async processing
        await new Promise(resolve => setTimeout(resolve, 100));
        
        return {{
            processed: true,
            originalInput: inputData,
            taskDescription: '{task_description}',
            processingTime: Date.now()
        }};
    }}
    
    getStats() {{
        return {{
            processedCount: this.processedCount,
            errorCount: this.errors.length,
            successRate: this.processedCount / (this.processedCount + this.errors.length) || 0
        }};
    }}
}}

// Usage example
(async () => {{
    const processor = new TaskProcessor('IntermediateProcessor');
    
    const testData = {{ sample: 'data', type: 'test' }};
    const result = await processor.process(testData);
    
    console.log('Result:', result);
    console.log('Stats:', processor.getStats());
}})();

module.exports = {{ TaskProcessor }};
''',
        'documentation': f"Intermediate JavaScript class-based implementation for: {task_description}. Includes async processing, error handling, and statistics tracking."
    }

def _generate_advanced_javascript(task_description: str) -> Dict[str, str]:
    """Generate advanced JavaScript code."""
    return {
        'main_code': f'''/**
 * Advanced JavaScript implementation with TypeScript-style patterns
 * Task: {task_description}
 */

// Abstract base class simulation
class AbstractTaskProcessor {{
    constructor(name) {{
        if (new.target === AbstractTaskProcessor) {{
            throw new Error('Cannot instantiate abstract class');
        }}
        this.name = name;
        this.metrics = [];
        this.middlewares = [];
    }}
    
    // Abstract method (must be implemented by subclasses)
    async executeCoreLogic(data) {{
        throw new Error('executeCoreLogic must be implemented by subclass');
    }}
    
    // Template method pattern
    async processWithMonitoring(data) {{
        const startTime = Date.now();
        const metadata = {{ processorName: this.name, startTime }};
        
        try {{
            // Run pre-processing middlewares
            const processedData = await this.runMiddlewares(data, 'pre');
            
            // Validate input
            await this.validateInput(processedData);
            
            // Execute core logic (implemented by subclass)
            const result = await this.executeCoreLogic(processedData);
            
            // Post-process
            const finalResult = await this.runMiddlewares(result, 'post');
            
            const endTime = Date.now();
            const metrics = {{
                ...metadata,
                endTime,
                duration: endTime - startTime,
                success: true
            }};
            
            this.metrics.push(metrics);
            
            return {{
                status: 'completed',
                data: finalResult,
                metadata: metrics
            }};
            
        }} catch (error) {{
            const endTime = Date.now();
            const errorMetrics = {{
                ...metadata,
                endTime,
                duration: endTime - startTime,
                success: false,
                error: error.message
            }};
            
            this.metrics.push(errorMetrics);
            
            return {{
                status: 'failed',
                error: error.message,
                metadata: errorMetrics
            }};
        }}
    }}
    
    addMiddleware(middleware, type = 'pre') {{
        this.middlewares.push({{ middleware, type }});
    }}
    
    async runMiddlewares(data, type) {{
        const applicableMiddlewares = this.middlewares.filter(m => m.type === type);
        
        let result = data;
        for (const {{ middleware }} of applicableMiddlewares) {{
            result = await middleware(result);
        }}
        
        return result;
    }}
    
    async validateInput(data) {{
        if (data === null || data === undefined) {{
            throw new Error('Input data cannot be null or undefined');
        }}
    }}
    
    getPerformanceReport() {{
        if (this.metrics.length === 0) {{
            return {{ noMetrics: true }};
        }}
        
        const successful = this.metrics.filter(m => m.success);
        const failed = this.metrics.filter(m => !m.success);
        const durations = successful.map(m => m.duration);
        
        return {{
            totalExecutions: this.metrics.length,
            successfulExecutions: successful.length,
            failedExecutions: failed.length,
            successRate: (successful.length / this.metrics.length) * 100,
            averageDuration: durations.reduce((a, b) => a + b, 0) / durations.length || 0,
            minDuration: Math.min(...durations) || 0,
            maxDuration: Math.max(...durations) || 0
        }};
    }}
}}

// Concrete implementation
class ConcreteTaskProcessor extends AbstractTaskProcessor {{
    constructor(name = 'ConcreteProcessor') {{
        super(name);
        this.cache = new Map();
        this.cacheHits = 0;
    }}
    
    async executeCoreLogic(data) {{
        const cacheKey = JSON.stringify(data);
        
        // Check cache first
        if (this.cache.has(cacheKey)) {{
            this.cacheHits++;
            return {{
                ...this.cache.get(cacheKey),
                fromCache: true,
                cacheHits: this.cacheHits
            }};
        }}
        
        // Simulate complex processing
        await new Promise(resolve => setTimeout(resolve, Math.random() * 200));
        
        const result = {{
            taskDescription: '{task_description}',
            processedData: data,
            processingId: Math.random().toString(36).substr(2, 9),
            complexity: 'advanced',
            features: ['caching', 'middleware', 'metrics', 'inheritance']
        }};
        
        // Cache the result
        this.cache.set(cacheKey, result);
        
        return result;
    }}
    
    getCacheStats() {{
        return {{
            cacheSize: this.cache.size,
            cacheHits: this.cacheHits,
            hitRate: (this.cacheHits / (this.cacheHits + this.cache.size)) * 100 || 0
        }};
    }}
}}

// Factory pattern for processor creation
class ProcessorFactory {{
    static create(type, name) {{
        switch (type) {{
            case 'concrete':
                return new ConcreteTaskProcessor(name);
            default:
                throw new Error(`Unknown processor type: ${{type}}`);
        }}
    }}
}}

// Usage example with advanced patterns
(async () => {{
    const processor = ProcessorFactory.create('concrete', 'AdvancedProcessor');
    
    // Add logging middleware
    processor.addMiddleware(async (data) => {{
        console.log('Pre-processing:', {{ timestamp: new Date().toISOString(), data }});
        return data;
    }}, 'pre');
    
    processor.addMiddleware(async (result) => {{
        console.log('Post-processing:', {{ timestamp: new Date().toISOString(), result }});
        return {{ ...result, postProcessed: true }};
    }}, 'post');
    
    // Process multiple tasks
    const tasks = [
        {{ id: 1, data: 'sample1' }},
        {{ id: 2, data: 'sample2' }},
        {{ id: 1, data: 'sample1' }}  // This should hit cache
    ];
    
    for (const task of tasks) {{
        const result = await processor.processWithMonitoring(task);
        console.log(`Task ${{task.id}} result:`, result);
    }}
    
    // Display performance and cache statistics
    console.log('Performance Report:', processor.getPerformanceReport());
    console.log('Cache Stats:', processor.getCacheStats());
}})();

module.exports = {{ AbstractTaskProcessor, ConcreteTaskProcessor, ProcessorFactory }};
''',
        'documentation': f"Advanced JavaScript implementation for: {task_description}. Features abstract classes, template method pattern, middleware system, caching, factory pattern, and comprehensive performance monitoring."
    }

def _generate_generic_code(language: str, task_description: str) -> Dict[str, str]:
    """Generate generic code template."""
    return {
        'main_code': f"# {language.upper()} implementation for: {task_description}\n# TODO: Implement specific logic",
        'documentation': f"Generic {language} code template for: {task_description}"
    }

def _generate_test_code(language: str, main_code: str) -> str:
    """Generate test code for the given language."""
    if language == 'python':
        return '''import unittest
from unittest.mock import patch, MagicMock

class TestGeneratedCode(unittest.TestCase):
    """Test cases for the generated code."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Add your test cases here
        self.assertTrue(True)
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Add edge case tests here
        self.assertIsNotNone(None or "default")
    
    def test_error_handling(self):
        """Test error handling."""
        # Add error handling tests here
        with self.assertRaises(ValueError):
            pass  # Add code that should raise ValueError

if __name__ == '__main__':
    unittest.main()
'''
    elif language == 'javascript':
        return '''const assert = require('assert');

describe('Generated Code Tests', function() {
    describe('Basic Functionality', function() {
        it('should work correctly', function() {
            assert.strictEqual(true, true);
        });
    });
    
    describe('Edge Cases', function() {
        it('should handle edge cases', function() {
            assert.ok(true);
        });
    });
    
    describe('Error Handling', function() {
        it('should throw errors when appropriate', function() {
            assert.throws(() => {
                // Add code that should throw
            });
        });
    });
});
'''
    else:
        return f"# Test code for {language}\n# TODO: Add appropriate test framework and test cases"

def _calculate_complexity_score(complexity: str) -> float:
    """Calculate complexity score."""
    scores = {
        'simple': 0.3,
        'intermediate': 0.6,
        'advanced': 0.9
    }
    return scores.get(complexity, 0.5)

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create agents
        research_agent = create_research_agent()
        analysis_agent = create_data_analysis_agent()
        code_agent = create_code_generation_agent()
        
        # Example research task
        research_result = await research_agent.run("Research the benefits of type-safe programming")
        print("Research Result:", research_result)
        
        # Example analysis task
        analysis_request = AnalysisRequest(
            data=[1.0, 2.0, 3.0, 4.0, 5.0],
            analysis_type="mean",
            include_visualization=True
        )
        analysis_result = await analysis_agent.run(analysis_request)
        print("Analysis Result:", analysis_result)
        
        # Example code generation task
        code_request = CodeGenerationRequest(
            language="python",
            task_description="Create a function that processes user data",
            complexity="intermediate",
            include_tests=True
        )
        code_result = await code_agent.run(code_request)
        print("Generated Code:", code_result)
    
    asyncio.run(main())