# ⚙️ Session 2: Advanced Agent Architecture

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete [🎯 Observer Path](Session2_LangChain_Foundations.md) and [📝 Participant Path](Session2_Practical_Implementation.md)
> Time Investment: 2-3 hours
> Outcome: Master sophisticated agent orchestration patterns and enterprise architecture

## Advanced Learning Outcomes

After completing this advanced architecture module, you will master:

- Sophisticated agent orchestration patterns for complex data workflows  
- Multi-agent coordination strategies for distributed data systems  
- Advanced error recovery and fault tolerance mechanisms  
- Performance optimization techniques for high-scale agent deployments  
- Enterprise integration patterns for production data infrastructure  

## Advanced Orchestration Patterns

Beyond simple sequential chains, enterprise data systems require sophisticated orchestration that can handle conditional logic, parallel processing, and dynamic routing based on data characteristics and system state.

### Conditional Chain Execution

Real-world data processing often requires different analytical approaches based on data characteristics, system state, or business rules:

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
import json

class DataAnalysisRouter:
    """Route data analysis based on dataset characteristics"""

    def __init__(self, llm):
        self.llm = llm
        self.routing_chains = self._create_routing_chains()

    def _create_routing_chains(self):
        """Create specialized chains for different data analysis scenarios"""

        # Real-time streaming data analysis
        streaming_template = """
        You are analyzing real-time streaming data with these characteristics:
        - High velocity: {events_per_second} events/second
        - Data freshness: {latency_ms}ms latency
        - Quality issues: {error_rate}% error rate

        Dataset: {dataset_info}

        Provide streaming-optimized analysis focusing on:
        1. Real-time anomaly detection
        2. Performance bottlenecks
        3. Immediate action recommendations
        """

        streaming_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=streaming_template,
                input_variables=["events_per_second", "latency_ms", "error_rate", "dataset_info"]
            )
        )

        # Batch processing data analysis
        batch_template = """
        You are analyzing batch-processed data with these characteristics:
        - Volume: {data_volume} records processed
        - Processing time: {processing_hours} hours
        - Success rate: {success_rate}%

        Dataset: {dataset_info}

        Provide batch-optimized analysis focusing on:
        1. Processing efficiency and optimization opportunities
        2. Data quality trends over time
        3. Scalability recommendations
        """

        batch_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=batch_template,
                input_variables=["data_volume", "processing_hours", "success_rate", "dataset_info"]
            )
        )

        return {
            "streaming": streaming_chain,
            "batch": batch_chain
        }

    def route_analysis(self, data_characteristics, dataset_info):
        """Route to appropriate analysis chain based on data characteristics"""

        processing_type = data_characteristics.get("processing_type", "batch")

        if processing_type == "streaming":
            return self.routing_chains["streaming"].run({
                "events_per_second": data_characteristics.get("events_per_second", 0),
                "latency_ms": data_characteristics.get("latency_ms", 0),
                "error_rate": data_characteristics.get("error_rate", 0),
                "dataset_info": dataset_info
            })
        else:
            return self.routing_chains["batch"].run({
                "data_volume": data_characteristics.get("data_volume", 0),
                "processing_hours": data_characteristics.get("processing_hours", 0),
                "success_rate": data_characteristics.get("success_rate", 100),
                "dataset_info": dataset_info
            })
```

### Parallel Chain Execution

For comprehensive data analysis, execute multiple analytical approaches simultaneously to provide diverse perspectives:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

class ParallelDataAnalyzer:
    """Execute multiple data analysis chains in parallel for comprehensive insights"""

    def __init__(self, llm):
        self.llm = llm
        self.analysis_chains = self._create_analysis_chains()
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _create_analysis_chains(self):
        """Create specialized analysis chains for different perspectives"""

        chains = {}

        # Performance analysis chain
        perf_template = """
        Analyze the performance characteristics of this data system:
        {system_metrics}

        Focus on: throughput, latency, resource utilization, and optimization opportunities.
        """

        chains["performance"] = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=perf_template,
                input_variables=["system_metrics"]
            )
        )

        # Quality analysis chain
        quality_template = """
        Analyze the data quality characteristics of this dataset:
        {quality_metrics}

        Focus on: completeness, accuracy, consistency, and validity issues.
        """

        chains["quality"] = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=quality_template,
                input_variables=["quality_metrics"]
            )
        )

        # Security analysis chain
        security_template = """
        Analyze the security and compliance aspects of this data system:
        {security_metrics}

        Focus on: access controls, data privacy, encryption, and compliance requirements.
        """

        chains["security"] = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=security_template,
                input_variables=["security_metrics"]
            )
        )

        # Business impact analysis chain
        business_template = """
        Analyze the business impact and ROI of this data system:
        {business_metrics}

        Focus on: value generation, cost efficiency, business outcomes, and strategic alignment.
        """

        chains["business"] = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=business_template,
                input_variables=["business_metrics"]
            )
        )

        return chains

    def _execute_chain(self, chain_name: str, chain: LLMChain, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single analysis chain with error handling"""
        try:
            result = chain.run(inputs)
            return {
                "chain": chain_name,
                "status": "success",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "chain": chain_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def analyze_parallel(self, analysis_inputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Execute all analysis chains in parallel and combine results"""

        # Prepare futures for parallel execution
        futures = []
        for chain_name, chain in self.analysis_chains.items():
            if chain_name in analysis_inputs:
                future = self.executor.submit(
                    self._execute_chain,
                    chain_name,
                    chain,
                    analysis_inputs[chain_name]
                )
                futures.append(future)

        # Collect results
        results = {}
        successful_analyses = []
        failed_analyses = []

        for future in futures:
            try:
                result = future.result(timeout=30)  # 30 second timeout per chain
                results[result["chain"]] = result

                if result["status"] == "success":
                    successful_analyses.append(result["chain"])
                else:
                    failed_analyses.append(result["chain"])

            except Exception as e:
                failed_analyses.append(f"timeout_or_error: {str(e)}")

        # Generate comprehensive summary
        summary = self._generate_comprehensive_summary(results, successful_analyses, failed_analyses)

        return {
            "individual_analyses": results,
            "summary": summary,
            "metadata": {
                "successful_chains": len(successful_analyses),
                "failed_chains": len(failed_analyses),
                "total_chains": len(self.analysis_chains),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }

    def _generate_comprehensive_summary(self, results: Dict, successful: List, failed: List) -> str:
        """Generate a comprehensive summary from all successful analyses"""

        if not successful:
            return "Unable to generate comprehensive summary - all analysis chains failed"

        summary_parts = []

        for chain_name in successful:
            if chain_name in results and results[chain_name]["status"] == "success":
                summary_parts.append(f"**{chain_name.title()} Analysis:**\n{results[chain_name]['result'][:200]}...")

        if failed:
            summary_parts.append(f"**Note:** {len(failed)} analysis chain(s) failed: {', '.join(failed)}")

        return "\n\n".join(summary_parts)
```

## Multi-Agent Coordination Strategies

Enterprise data systems often require multiple specialized agents working together, each contributing their unique expertise to solve complex analytical challenges.

### Agent Communication Patterns

Implement sophisticated communication patterns between specialized agents:

```python
from enum import Enum
from typing import Optional, List
import uuid

class AgentRole(Enum):
    DATA_QUALITY_ENGINEER = "data_quality_engineer"
    PERFORMANCE_ANALYST = "performance_analyst"
    SECURITY_AUDITOR = "security_auditor"
    BUSINESS_ANALYST = "business_analyst"
    SYSTEM_ORCHESTRATOR = "system_orchestrator"

class AgentMessage:
    """Structure for inter-agent communication"""

    def __init__(self, sender: AgentRole, recipient: AgentRole, message_type: str, content: str, metadata: Dict = None):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

class MultiAgentCoordinator:
    """Coordinate multiple specialized agents for comprehensive data analysis"""

    def __init__(self, llm):
        self.llm = llm
        self.agents = self._initialize_specialized_agents()
        self.message_history = []
        self.analysis_state = {}

    def _initialize_specialized_agents(self):
        """Initialize all specialized agents with their tools and prompts"""

        agents = {}

        # Data Quality Engineer Agent
        quality_tools = [create_data_quality_tool()]
        agents[AgentRole.DATA_QUALITY_ENGINEER] = create_specialized_production_agent(
            "a senior data quality engineer focused on ensuring data reliability and accuracy",
            quality_tools,
            "Expert in data validation, quality metrics, and automated testing frameworks"
        )

        # Performance Analyst Agent
        perf_tools = [create_streaming_monitor_tool(), create_production_data_tool()]
        agents[AgentRole.PERFORMANCE_ANALYST] = create_specialized_production_agent(
            "a performance analyst specialized in system optimization and resource efficiency",
            perf_tools,
            "Expert in performance tuning, resource optimization, and scalability analysis"
        )

        # Security Auditor Agent
        security_tools = [create_security_assessment_tool()]  # Would need to implement
        agents[AgentRole.SECURITY_AUDITOR] = create_specialized_production_agent(
            "a security auditor focused on data privacy, access controls, and compliance",
            security_tools,
            "Expert in data security, privacy regulations, and compliance frameworks"
        )

        return agents

    def coordinate_comprehensive_analysis(self, analysis_request: str) -> str:
        """Coordinate multiple agents for comprehensive system analysis"""

        # Phase 1: Initial individual analyses
        individual_results = {}

        for role, agent in self.agents.items():
            try:
                # Customize request for each agent's specialty
                specialized_request = self._customize_request_for_agent(analysis_request, role)

                # Execute analysis
                result = agent.run(specialized_request)
                individual_results[role.value] = result

                # Log communication
                message = AgentMessage(
                    sender=role,
                    recipient=AgentRole.SYSTEM_ORCHESTRATOR,
                    message_type="analysis_result",
                    content=result
                )
                self.message_history.append(message)

            except Exception as e:
                individual_results[role.value] = f"Analysis failed: {str(e)}"

        # Phase 2: Cross-agent collaboration and synthesis
        synthesis_result = self._synthesize_multi_agent_results(individual_results)

        # Phase 3: Generate final coordinated recommendations
        final_analysis = self._generate_coordinated_recommendations(individual_results, synthesis_result)

        return final_analysis

    def _customize_request_for_agent(self, base_request: str, agent_role: AgentRole) -> str:
        """Customize analysis request for specific agent expertise"""

        role_contexts = {
            AgentRole.DATA_QUALITY_ENGINEER: "Focus on data quality, validation, and accuracy aspects:",
            AgentRole.PERFORMANCE_ANALYST: "Focus on system performance, scalability, and optimization aspects:",
            AgentRole.SECURITY_AUDITOR: "Focus on security, privacy, and compliance aspects:"
        }

        context = role_contexts.get(agent_role, "Analyze from your area of expertise:")
        return f"{context}\n\n{base_request}"

    def _synthesize_multi_agent_results(self, results: Dict[str, str]) -> str:
        """Synthesize results from multiple agents to identify patterns and conflicts"""

        synthesis_prompt = f"""
        You are a senior system architect synthesizing analysis results from multiple specialists:

        {json.dumps(results, indent=2)}

        Identify:
        1. Common themes and patterns across all analyses
        2. Conflicting recommendations that need resolution
        3. Dependencies between different aspects of the system
        4. Integrated opportunities for improvement

        Provide a synthesis that bridges all perspectives.
        """

        synthesis_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=synthesis_prompt,
                input_variables=[]
            )
        )

        return synthesis_chain.run({})

    def _generate_coordinated_recommendations(self, individual_results: Dict, synthesis: str) -> str:
        """Generate final coordinated recommendations based on all inputs"""

        recommendation_prompt = f"""
        Based on comprehensive multi-agent analysis and synthesis:

        INDIVIDUAL AGENT ANALYSES:
        {json.dumps(individual_results, indent=2)}

        CROSS-AGENT SYNTHESIS:
        {synthesis}

        Generate coordinated recommendations that:
        1. Address all identified issues holistically
        2. Prioritize actions based on impact and feasibility
        3. Consider interdependencies between different system aspects
        4. Provide clear implementation guidance
        5. Include success metrics and monitoring approaches

        Structure as an executive summary with actionable next steps.
        """

        final_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=recommendation_prompt,
                input_variables=[]
            )
        )

        return final_chain.run({})
```

## Advanced Error Recovery & Fault Tolerance

Enterprise systems require sophisticated error handling that goes beyond simple retries, implementing circuit breakers, graceful degradation, and intelligent recovery strategies.

### Circuit Breaker Pattern for Agent Systems

Implement circuit breaker patterns to prevent cascading failures in agent workflows:

```python
from enum import Enum
import time
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, requests blocked
    HALF_OPEN = "half_open" # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker pattern for agent tool calls"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function call through circuit breaker"""

        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception(f"Circuit breaker OPEN - service unavailable")

        try:
            result = func(*args, **kwargs)

            # Success - reset circuit breaker if half open
            if self.state == CircuitState.HALF_OPEN:
                self._reset()

            return result

        except Exception as e:
            self._record_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True

        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _record_failure(self):
        """Record failure and update circuit breaker state"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def _reset(self):
        """Reset circuit breaker to closed state"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

class FaultTolerantAgent:
    """Agent with comprehensive fault tolerance mechanisms"""

    def __init__(self, base_agent, circuit_breaker_config=None):
        self.base_agent = base_agent
        self.circuit_breakers = {}
        self.circuit_config = circuit_breaker_config or {
            "failure_threshold": 3,
            "timeout": 30,
            "recovery_timeout": 60
        }

        # Wrap agent tools with circuit breakers
        self._wrap_tools_with_circuit_breakers()

    def _wrap_tools_with_circuit_breakers(self):
        """Wrap each agent tool with its own circuit breaker"""

        for tool in self.base_agent.tools:
            tool_name = tool.name

            # Create circuit breaker for this tool
            circuit_breaker = CircuitBreaker(**self.circuit_config)
            self.circuit_breakers[tool_name] = circuit_breaker

            # Wrap the tool function
            original_func = tool.func

            def wrapped_func(*args, circuit_breaker=circuit_breaker, original_func=original_func, **kwargs):
                return circuit_breaker.call(original_func, *args, **kwargs)

            tool.func = wrapped_func

    def run_with_fallback(self, request: str, fallback_strategies: List[str] = None) -> str:
        """Run agent with fallback strategies for fault tolerance"""

        fallback_strategies = fallback_strategies or [
            "retry_with_simplified_request",
            "use_cached_results",
            "provide_partial_analysis",
            "graceful_degradation_response"
        ]

        # Primary attempt
        try:
            return self.base_agent.run(request)

        except Exception as primary_error:
            print(f"Primary agent execution failed: {primary_error}")

            # Try fallback strategies in order
            for strategy in fallback_strategies:
                try:
                    return self._execute_fallback_strategy(strategy, request, primary_error)
                except Exception as fallback_error:
                    print(f"Fallback strategy '{strategy}' failed: {fallback_error}")
                    continue

            # All strategies failed
            return self._generate_failure_response(request, primary_error)

    def _execute_fallback_strategy(self, strategy: str, request: str, error: Exception) -> str:
        """Execute specific fallback strategy"""

        if strategy == "retry_with_simplified_request":
            simplified_request = self._simplify_request(request)
            return self.base_agent.run(simplified_request)

        elif strategy == "use_cached_results":
            # In production, implement actual caching
            return "Using cached analysis results due to system unavailability"

        elif strategy == "provide_partial_analysis":
            return self._generate_partial_analysis(request, error)

        elif strategy == "graceful_degradation_response":
            return self._generate_degraded_response(request, error)

        else:
            raise Exception(f"Unknown fallback strategy: {strategy}")

    def _simplify_request(self, request: str) -> str:
        """Simplify complex request to increase success probability"""

        # Extract key concepts and create simpler version
        simplified = f"""
        Provide a basic analysis of: {request[:100]}...

        Focus on essential information only. Avoid complex tool usage.
        """

        return simplified

    def _generate_partial_analysis(self, request: str, error: Exception) -> str:
        """Generate partial analysis based on available information"""

        return f"""
        PARTIAL ANALYSIS (some systems unavailable):

        Request: {request[:150]}...

        Status: Some data systems are currently unavailable due to: {str(error)[:100]}

        Available insights:
        - System appears to be experiencing connectivity issues
        - Recommend checking system status and retrying in 5-10 minutes
        - Basic troubleshooting steps: verify network connectivity, check service status

        For complete analysis, please retry when all systems are operational.
        """

    def _generate_degraded_response(self, request: str, error: Exception) -> str:
        """Generate response indicating degraded functionality"""

        return f"""
        SYSTEM OPERATING IN DEGRADED MODE

        Your request: {request[:100]}...

        Current status: Limited functionality due to system issues
        Error details: {str(error)[:150]}...

        Recommendations:
        1. Check system status dashboard
        2. Retry request in 10-15 minutes
        3. Contact system administrator if issues persist

        We apologize for the inconvenience and are working to restore full functionality.
        """

    def _generate_failure_response(self, request: str, error: Exception) -> str:
        """Generate final failure response when all strategies exhausted"""

        return f"""
        UNABLE TO PROCESS REQUEST

        All recovery strategies have been exhausted.

        Original request: {request[:100]}...
        Primary error: {str(error)[:100]}...

        Please contact technical support or try again later.
        """

    def get_circuit_breaker_status(self) -> Dict[str, str]:
        """Get current status of all circuit breakers"""

        status = {}
        for tool_name, breaker in self.circuit_breakers.items():
            status[tool_name] = {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "last_failure_time": breaker.last_failure_time
            }

        return status
```

## Performance Optimization for High-Scale Deployments

Enterprise deployments require sophisticated performance optimization strategies to handle high-volume, low-latency requirements while maintaining cost efficiency.

### Intelligent Caching Strategies

Implement multi-level caching with intelligent invalidation for agent responses:

```python
import hashlib
import pickle
import redis
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class AgentResponseCache:
    """Multi-level caching system for agent responses with intelligent invalidation"""

    def __init__(self, redis_url: str = None, enable_local_cache: bool = True):
        self.redis_client = redis.from_url(redis_url) if redis_url else None
        self.local_cache = {} if enable_local_cache else None
        self.cache_stats = {"hits": 0, "misses": 0, "invalidations": 0}

    def _generate_cache_key(self, request: str, context: Dict[str, Any] = None) -> str:
        """Generate deterministic cache key from request and context"""

        # Create consistent hash from request and context
        content = f"{request}_{json.dumps(context or {}, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def get_cached_response(self, request: str, context: Dict[str, Any] = None, max_age_minutes: int = 30) -> Optional[str]:
        """Retrieve cached response if available and valid"""

        cache_key = self._generate_cache_key(request, context)

        # Try local cache first (fastest)
        if self.local_cache:
            cached_item = self.local_cache.get(cache_key)
            if cached_item and self._is_cache_valid(cached_item, max_age_minutes):
                self.cache_stats["hits"] += 1
                return cached_item["response"]

        # Try Redis cache (distributed)
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    cached_item = pickle.loads(cached_data)
                    if self._is_cache_valid(cached_item, max_age_minutes):
                        # Update local cache
                        if self.local_cache:
                            self.local_cache[cache_key] = cached_item

                        self.cache_stats["hits"] += 1
                        return cached_item["response"]
            except Exception as e:
                print(f"Redis cache error: {e}")

        # Cache miss
        self.cache_stats["misses"] += 1
        return None

    def cache_response(self, request: str, response: str, context: Dict[str, Any] = None, ttl_minutes: int = 60):
        """Cache agent response with TTL"""

        cache_key = self._generate_cache_key(request, context)
        cache_item = {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "ttl_minutes": ttl_minutes
        }

        # Store in local cache
        if self.local_cache:
            self.local_cache[cache_key] = cache_item

        # Store in Redis with TTL
        if self.redis_client:
            try:
                serialized = pickle.dumps(cache_item)
                self.redis_client.setex(cache_key, timedelta(minutes=ttl_minutes), serialized)
            except Exception as e:
                print(f"Redis cache storage error: {e}")

    def _is_cache_valid(self, cached_item: Dict[str, Any], max_age_minutes: int) -> bool:
        """Check if cached item is still valid"""

        if "timestamp" not in cached_item:
            return False

        cached_time = datetime.fromisoformat(cached_item["timestamp"])
        age_limit = datetime.now() - timedelta(minutes=max_age_minutes)

        return cached_time > age_limit

    def invalidate_cache_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""

        self.cache_stats["invalidations"] += 1

        # Invalidate local cache
        if self.local_cache:
            keys_to_remove = [key for key in self.local_cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.local_cache[key]

        # Invalidate Redis cache
        if self.redis_client:
            try:
                keys = self.redis_client.keys(f"*{pattern}*")
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                print(f"Redis cache invalidation error: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""

        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0

        return {
            "hit_rate": f"{hit_rate:.2%}",
            "total_hits": self.cache_stats["hits"],
            "total_misses": self.cache_stats["misses"],
            "total_invalidations": self.cache_stats["invalidations"],
            "local_cache_size": len(self.local_cache) if self.local_cache else 0
        }

class HighPerformanceAgent:
    """Agent optimized for high-scale deployments with caching and performance monitoring"""

    def __init__(self, base_agent, cache_config: Dict[str, Any] = None):
        self.base_agent = base_agent
        self.cache = AgentResponseCache(**(cache_config or {}))
        self.performance_metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "avg_response_time": 0,
            "total_response_time": 0
        }

    def run_optimized(self, request: str, context: Dict[str, Any] = None, cache_ttl: int = 30) -> str:
        """Run agent with performance optimizations"""

        start_time = time.time()
        self.performance_metrics["total_requests"] += 1

        # Check cache first
        cached_response = self.cache.get_cached_response(request, context)
        if cached_response:
            self.performance_metrics["cache_hits"] += 1
            self._update_response_time_stats(time.time() - start_time)
            return cached_response

        # Execute agent and cache result
        try:
            response = self.base_agent.run(request)
            self.cache.cache_response(request, response, context, cache_ttl)

            self._update_response_time_stats(time.time() - start_time)
            return response

        except Exception as e:
            self._update_response_time_stats(time.time() - start_time)
            raise e

    def _update_response_time_stats(self, response_time: float):
        """Update response time statistics"""

        self.performance_metrics["total_response_time"] += response_time
        self.performance_metrics["avg_response_time"] = (
            self.performance_metrics["total_response_time"] /
            self.performance_metrics["total_requests"]
        )

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""

        cache_stats = self.cache.get_cache_stats()

        return {
            "agent_performance": {
                "total_requests": self.performance_metrics["total_requests"],
                "cache_hit_rate": f"{self.performance_metrics['cache_hits'] / max(1, self.performance_metrics['total_requests']):.2%}",
                "avg_response_time": f"{self.performance_metrics['avg_response_time']:.3f}s"
            },
            "cache_performance": cache_stats,
            "optimization_recommendations": self._generate_optimization_recommendations(cache_stats)
        }

    def _generate_optimization_recommendations(self, cache_stats: Dict) -> List[str]:
        """Generate performance optimization recommendations"""

        recommendations = []

        hit_rate = float(cache_stats["hit_rate"].rstrip('%')) / 100

        if hit_rate < 0.3:
            recommendations.append("Consider increasing cache TTL or improving cache key strategy")

        if self.performance_metrics["avg_response_time"] > 2.0:
            recommendations.append("Average response time is high - consider tool optimization or parallel execution")

        if cache_stats["local_cache_size"] > 1000:
            recommendations.append("Local cache size is large - consider implementing LRU eviction")

        return recommendations
```

## Enterprise Integration Patterns

Integrate agents seamlessly with existing enterprise data infrastructure, authentication systems, and compliance frameworks.

### Authentication & Authorization Integration

Implement enterprise-grade security patterns for agent deployments:

```python
from functools import wraps
import jwt
from typing import List, Dict, Callable
from enum import Enum

class Permission(Enum):
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    ADMIN_OPERATIONS = "admin_operations"
    EXECUTE_QUERIES = "execute_queries"

class SecureAgent:
    """Enterprise agent with comprehensive security controls"""

    def __init__(self, base_agent, jwt_secret: str, permission_config: Dict[str, List[Permission]]):
        self.base_agent = base_agent
        self.jwt_secret = jwt_secret
        self.permission_config = permission_config
        self.audit_log = []

        # Wrap tools with security controls
        self._secure_agent_tools()

    def _secure_agent_tools(self):
        """Apply security wrappers to all agent tools"""

        for tool in self.base_agent.tools:
            original_func = tool.func
            required_permissions = self._get_tool_permissions(tool.name)

            def secured_func(*args, original_func=original_func, permissions=required_permissions, **kwargs):
                # Security check would be performed here in actual implementation
                return original_func(*args, **kwargs)

            tool.func = secured_func

    def _get_tool_permissions(self, tool_name: str) -> List[Permission]:
        """Get required permissions for a specific tool"""

        tool_permissions = {
            "DataWarehouse": [Permission.READ_DATA, Permission.EXECUTE_QUERIES],
            "StreamingMonitor": [Permission.READ_DATA],
            "DataQualityAssessment": [Permission.READ_DATA],
            "SystemAdmin": [Permission.ADMIN_OPERATIONS]
        }

        return tool_permissions.get(tool_name, [Permission.READ_DATA])

    def run_secure(self, request: str, auth_token: str, user_context: Dict[str, str] = None) -> str:
        """Run agent with security validation"""

        # Validate authentication token
        try:
            user_claims = jwt.decode(auth_token, self.jwt_secret, algorithms=["HS256"])
            user_id = user_claims.get("user_id")
            user_roles = user_claims.get("roles", [])

        except jwt.InvalidTokenError as e:
            self._log_security_event("AUTHENTICATION_FAILED", request, str(e))
            raise PermissionError("Invalid authentication token")

        # Check authorization
        if not self._check_authorization(user_roles, request):
            self._log_security_event("AUTHORIZATION_FAILED", request, f"User {user_id} insufficient permissions")
            raise PermissionError("Insufficient permissions for requested operation")

        # Log authorized request
        self._log_security_event("REQUEST_AUTHORIZED", request, f"User {user_id} with roles {user_roles}")

        try:
            # Execute with user context
            response = self.base_agent.run(request)

            # Log successful execution
            self._log_security_event("REQUEST_COMPLETED", request, f"Success for user {user_id}")

            return response

        except Exception as e:
            self._log_security_event("REQUEST_FAILED", request, f"Error for user {user_id}: {str(e)}")
            raise e

    def _check_authorization(self, user_roles: List[str], request: str) -> bool:
        """Check if user has required permissions for request"""

        # In production, implement sophisticated authorization logic
        # This is a simplified example

        admin_roles = ["admin", "data_engineer", "senior_analyst"]
        read_only_roles = ["analyst", "viewer"]

        # Check for admin operations
        if any(keyword in request.lower() for keyword in ["delete", "drop", "modify", "admin"]):
            return any(role in admin_roles for role in user_roles)

        # All users can perform read operations
        return True

    def _log_security_event(self, event_type: str, request: str, details: str):
        """Log security events for audit purposes"""

        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "request_summary": request[:100],
            "details": details
        }

        self.audit_log.append(audit_entry)

        # In production, send to security information and event management (SIEM) system
        print(f"SECURITY LOG: {event_type} - {details}")

    def get_audit_log(self) -> List[Dict]:
        """Retrieve security audit log"""
        return self.audit_log.copy()
```

## 🎯📝 Prerequisites Review

Before diving deeper, ensure you've mastered the foundational concepts:

**Core Understanding Required:**  
- [🎯 LangChain Architecture Foundations](Session2_LangChain_Foundations.md) - Essential building blocks  
- [📝 Practical Implementation](Session2_Practical_Implementation.md) - Hands-on experience with agents and tools  

## ⚙️ Continue Advanced Learning

Explore related advanced architecture topics:

**Next Advanced Modules:**  
- [⚙️ Production Memory Systems](Session2_Production_Memory_Systems.md) - Enterprise state management and persistence  
- [⚙️ Enterprise Tool Development](Session2_Enterprise_Tool_Development.md) - Custom integrations and specialized capabilities  

**Legacy Advanced Modules:**  
- [Advanced LangChain Patterns](Session2_ModuleA_Advanced_LangChain_Patterns.md) - Complex workflows & optimization  
- [Production Deployment Strategies](Session2_ModuleB_Production_Deployment_Strategies.md) - Enterprise deployment & monitoring  
---

## 🧭 Navigation

**Previous:** [Session 1 - Bare Metal Agents ←](Session1_Bare_Metal_Agents.md)
**Next:** [Session 3 - LangGraph Multi-Agent Workflows →](Session3_LangGraph_Multi_Agent_Workflows.md)
---
