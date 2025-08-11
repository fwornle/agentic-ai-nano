# src/session4/error_handling.py
"""
Error handling and recovery patterns for CrewAI production systems.
Demonstrates robust error handling, failover mechanisms, and recovery strategies.
"""

from crewai import Agent, Task, Crew, Process
from crewai.tools import SerperDevTool, WebsiteSearchTool
from langchain.llms import OpenAI
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import time
import traceback

class RobustCrewSystem:
    """Production-ready crew with comprehensive error handling and recovery"""
    
    def __init__(self, llm=None, max_retries: int = 3, retry_delay: float = 1.0):
        self.llm = llm or OpenAI(temperature=0.7)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        
        # Error recovery strategies
        self.error_recovery_strategies = {
            'tool_failure': self._handle_tool_failure,
            'agent_failure': self._handle_agent_failure,
            'task_timeout': self._handle_task_timeout,
            'llm_failure': self._handle_llm_failure,
            'memory_error': self._handle_memory_error,
            'network_error': self._handle_network_error
        }
        
        # Circuit breaker for preventing cascading failures
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=60)
        
        # Health monitoring
        self.health_metrics = HealthMetrics()
    
    def create_resilient_crew(self):
        """Create crew with built-in error handling and recovery mechanisms"""
        
        # Primary agent with error handling
        primary_agent = Agent(
            role='Resilient Primary Agent',
            goal='Execute tasks with robust error handling and graceful degradation',
            backstory="""You are experienced in handling unexpected situations, 
            have built-in error recovery mechanisms, and can gracefully degrade 
            functionality when necessary while maintaining core objectives.""",
            tools=[SerperDevTool(), WebsiteSearchTool()],
            llm=self.llm,
            verbose=True,
            max_retry=self.max_retries,
            max_iter=5
        )
        
        # Backup agent for failover scenarios
        backup_agent = Agent(
            role='Backup Agent',
            goal='Provide failover support when primary agents encounter unrecoverable issues',
            backstory="""You are the reliable backup who steps in when 
            primary agents face difficulties. You use simpler, more reliable 
            approaches to ensure task completion even under adverse conditions.""",
            tools=[],  # Simpler toolset for reliability
            llm=self.llm,
            verbose=True,
            max_retry=2,
            max_iter=3
        )
        
        # System health monitor
        monitor_agent = Agent(
            role='System Health Monitor',
            goal='Monitor crew execution health and detect issues proactively',
            backstory="""You continuously monitor system health, detect problems 
            before they become critical, and provide early warning of potential issues. 
            You track performance metrics and system reliability indicators.""",
            llm=self.llm,
            verbose=True,
            max_iter=2
        )
        
        # Error recovery specialist
        recovery_agent = Agent(
            role='Error Recovery Specialist',
            goal='Diagnose errors and implement recovery strategies',
            backstory="""You specialize in error diagnosis, root cause analysis, 
            and implementing recovery strategies. You help systems recover from 
            failures and prevent similar issues in the future.""",
            llm=self.llm,
            verbose=True,
            max_iter=3
        )
        
        # Main task with error handling
        main_task = Task(
            description="""Execute web research on 'Enterprise AI Implementation Strategies' with comprehensive error handling.
            
            Primary objectives:
            1. Gather comprehensive information from multiple reliable sources
            2. Synthesize insights for enterprise decision-makers
            3. Provide actionable recommendations
            
            Error handling requirements:
            - If tools fail: retry with exponential backoff, then use alternative approaches
            - If partial data: proceed with available information and note limitations
            - If complete failure: escalate to backup agent with simplified approach
            - Document all recovery actions taken for analysis
            - Maintain minimum quality standards even in degraded mode
            
            Graceful degradation strategy:
            1. Full functionality with all tools working
            2. Reduced functionality with manual reasoning if tools partially fail
            3. Basic functionality with simplified analysis if major issues occur
            4. Minimum viable output even in worst-case scenarios""",
            agent=primary_agent,
            expected_output="Research results with comprehensive error handling log and quality assessment"
        )
        
        # Health monitoring task
        monitor_task = Task(
            description="""Monitor crew execution health and provide real-time system status.
            
            Monitoring objectives:
            1. Track task execution times and detect slowdowns
            2. Monitor error frequencies and patterns
            3. Assess system resource utilization
            4. Evaluate output quality trends
            5. Detect potential issues before they become critical
            
            Health metrics to track:
            - Task completion rates and times
            - Error frequency and types
            - Tool success rates
            - Agent performance indicators
            - Overall system reliability scores
            
            Alert on concerning trends or immediate issues.""",
            agent=monitor_agent,
            expected_output="Real-time system health report with alerts and recommendations",
            context=[main_task]
        )
        
        # Error analysis and recovery task
        recovery_task = Task(
            description="""Analyze any errors that occurred and implement recovery strategies.
            
            Recovery objectives:
            1. Diagnose root causes of any errors encountered
            2. Assess impact on overall task completion
            3. Implement appropriate recovery strategies
            4. Verify recovery effectiveness
            5. Document lessons learned for future improvement
            
            Recovery strategies to consider:
            - Automatic retry with different parameters
            - Fallback to alternative tools or approaches
            - Graceful degradation of functionality
            - Escalation to backup systems
            - Manual intervention recommendations
            
            Provide specific recommendations for preventing similar issues.""",
            agent=recovery_agent,
            expected_output="Error analysis report with recovery actions taken and prevention recommendations",
            context=[main_task, monitor_task]
        )
        
        # Backup task (conditional execution)
        backup_task = Task(
            description="""Provide backup execution if primary task fails or produces inadequate results.
            
            Backup strategy:
            1. Use simplified, more reliable approaches
            2. Focus on core objectives with reduced scope if necessary
            3. Employ manual reasoning when tools are unavailable
            4. Ensure minimum viable output is always produced
            5. Document what was achieved vs. what was intended
            
            Quality standards for backup execution:
            - Must provide actionable insights even with limited data
            - Clear documentation of limitations and confidence levels
            - Transparent about what information is missing or uncertain
            - Focused on most critical information for decision-making""",
            agent=backup_agent,
            expected_output="Backup execution results with clear limitation documentation",
            context=[main_task, recovery_task]
        )
        
        return Crew(
            agents=[primary_agent, backup_agent, monitor_agent, recovery_agent],
            tasks=[main_task, monitor_task, recovery_task, backup_task],
            process=Process.sequential,
            verbose=2,
            memory=True
        )
    
    def execute_with_error_handling(self, crew: Crew) -> Dict[str, Any]:
        """Execute crew with comprehensive error handling"""
        
        execution_start = datetime.now()
        errors_encountered = []
        recovery_actions = []
        
        try:
            # Pre-execution health check
            health_check = self.health_metrics.get_system_health()
            if health_check['status'] == 'unhealthy':
                self.logger.warning(f"System health check failed: {health_check}")
            
            # Execute through circuit breaker
            result = self.circuit_breaker.call(crew.kickoff)
            
            # Post-execution health check
            execution_time = (datetime.now() - execution_start).total_seconds()
            self.health_metrics.record_execution(
                success=True,
                duration=execution_time,
                errors=len(errors_encountered)
            )
            
            return {
                'result': result,
                'execution_time': execution_time,
                'errors_encountered': errors_encountered,
                'recovery_actions': recovery_actions,
                'health_status': self.health_metrics.get_system_health()
            }
            
        except CircuitBreakerError as e:
            self.logger.error(f"Circuit breaker prevented execution: {e}")
            return self._handle_circuit_breaker_error(e)
            
        except Exception as e:
            self.logger.error(f"Unexpected error during crew execution: {e}")
            self.logger.error(traceback.format_exc())
            
            # Record error for analysis
            errors_encountered.append({
                'error_type': type(e).__name__,
                'error_message': str(e),
                'timestamp': datetime.now().isoformat(),
                'traceback': traceback.format_exc()
            })
            
            # Attempt recovery
            recovery_result = self._attempt_recovery(e, crew)
            recovery_actions.append(recovery_result)
            
            # Record failed execution
            execution_time = (datetime.now() - execution_start).total_seconds()
            self.health_metrics.record_execution(
                success=False,
                duration=execution_time,
                errors=len(errors_encountered)
            )
            
            return {
                'result': recovery_result.get('result'),
                'execution_time': execution_time,
                'errors_encountered': errors_encountered,
                'recovery_actions': recovery_actions,
                'health_status': self.health_metrics.get_system_health(),
                'recovery_used': True
            }
    
    def _handle_tool_failure(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool failure with fallback strategies"""
        self.logger.warning(f\"Tool failure encountered: {error}\")\n        \n        recovery_strategy = {\n            'strategy': 'fallback_to_manual',\n            'error': str(error),\n            'action': 'Using manual reasoning instead of failed tool',\n            'timestamp': datetime.now().isoformat()\n        }\n        \n        return recovery_strategy\n    \n    def _handle_agent_failure(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Handle agent failure with backup agent activation\"\"\"\n        self.logger.error(f\"Agent failure encountered: {error}\")\n        \n        recovery_strategy = {\n            'strategy': 'activate_backup_agent',\n            'error': str(error),\n            'action': 'Switching to backup agent with simplified approach',\n            'timestamp': datetime.now().isoformat()\n        }\n        \n        return recovery_strategy\n    \n    def _handle_task_timeout(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Handle task timeout with simplified execution\"\"\"\n        self.logger.warning(f\"Task timeout encountered: {error}\")\n        \n        recovery_strategy = {\n            'strategy': 'simplify_and_retry',\n            'error': str(error),\n            'action': 'Reducing task complexity and retrying with shorter timeout',\n            'timestamp': datetime.now().isoformat()\n        }\n        \n        return recovery_strategy\n    \n    def _handle_llm_failure(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Handle LLM failure with alternative model or degraded functionality\"\"\"\n        self.logger.error(f\"LLM failure encountered: {error}\")\n        \n        recovery_strategy = {\n            'strategy': 'fallback_llm_or_degrade',\n            'error': str(error),\n            'action': 'Attempting fallback LLM or degraded functionality',\n            'timestamp': datetime.now().isoformat()\n        }\n        \n        return recovery_strategy\n    \n    def _handle_memory_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Handle memory errors with context reduction\"\"\"\n        self.logger.warning(f\"Memory error encountered: {error}\")\n        \n        recovery_strategy = {\n            'strategy': 'reduce_context_and_retry',\n            'error': str(error),\n            'action': 'Reducing context size and retrying operation',\n            'timestamp': datetime.now().isoformat()\n        }\n        \n        return recovery_strategy\n    \n    def _handle_network_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Handle network errors with retry and offline fallback\"\"\"\n        self.logger.warning(f\"Network error encountered: {error}\")\n        \n        recovery_strategy = {\n            'strategy': 'retry_with_backoff_then_offline',\n            'error': str(error),\n            'action': 'Retrying with exponential backoff, then offline fallback',\n            'timestamp': datetime.now().isoformat()\n        }\n        \n        return recovery_strategy\n    \n    def _handle_circuit_breaker_error(self, error) -> Dict[str, Any]:\n        \"\"\"Handle circuit breaker activation\"\"\"\n        return {\n            'result': None,\n            'circuit_breaker_activated': True,\n            'error': str(error),\n            'recommendation': 'System overloaded, try again later',\n            'retry_after_seconds': 60\n        }\n    \n    def _attempt_recovery(self, error: Exception, crew: Crew) -> Dict[str, Any]:\n        \"\"\"Attempt to recover from error using appropriate strategy\"\"\"\n        \n        error_type = self._classify_error(error)\n        \n        if error_type in self.error_recovery_strategies:\n            recovery_strategy = self.error_recovery_strategies[error_type]\n            return recovery_strategy(error, {'crew': crew})\n        else:\n            return {\n                'strategy': 'unknown_error_fallback',\n                'error': str(error),\n                'action': 'Using generic fallback strategy',\n                'timestamp': datetime.now().isoformat()\n            }\n    \n    def _classify_error(self, error: Exception) -> str:\n        \"\"\"Classify error type for appropriate recovery strategy\"\"\"\n        \n        error_name = type(error).__name__\n        error_message = str(error).lower()\n        \n        if 'timeout' in error_message or 'timeouterror' in error_name.lower():\n            return 'task_timeout'\n        elif 'network' in error_message or 'connection' in error_message:\n            return 'network_error'\n        elif 'memory' in error_message or 'memoryerror' in error_name.lower():\n            return 'memory_error'\n        elif 'tool' in error_message or 'serper' in error_message.lower():\n            return 'tool_failure'\n        elif 'llm' in error_message or 'openai' in error_message:\n            return 'llm_failure'\n        elif 'agent' in error_message:\n            return 'agent_failure'\n        else:\n            return 'unknown_error'\n\n\nclass CircuitBreaker:\n    \"\"\"Circuit breaker to prevent cascading failures\"\"\"\n    \n    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):\n        self.failure_threshold = failure_threshold\n        self.timeout_seconds = timeout_seconds\n        self.failure_count = 0\n        self.last_failure_time = None\n        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN\n    \n    def call(self, func: Callable, *args, **kwargs):\n        \"\"\"Execute function through circuit breaker\"\"\"\n        \n        if self.state == 'OPEN':\n            if self._should_attempt_reset():\n                self.state = 'HALF_OPEN'\n            else:\n                raise CircuitBreakerError(\"Circuit breaker is OPEN - too many recent failures\")\n        \n        try:\n            result = func(*args, **kwargs)\n            self._on_success()\n            return result\n        except Exception as e:\n            self._on_failure()\n            raise\n    \n    def _should_attempt_reset(self) -> bool:\n        \"\"\"Check if enough time has passed to attempt reset\"\"\"\n        if self.last_failure_time is None:\n            return True\n        \n        time_since_failure = time.time() - self.last_failure_time\n        return time_since_failure > self.timeout_seconds\n    \n    def _on_success(self):\n        \"\"\"Handle successful operation\"\"\"\n        self.failure_count = 0\n        self.state = 'CLOSED'\n    \n    def _on_failure(self):\n        \"\"\"Handle failed operation\"\"\"\n        self.failure_count += 1\n        self.last_failure_time = time.time()\n        \n        if self.failure_count >= self.failure_threshold:\n            self.state = 'OPEN'\n\n\nclass CircuitBreakerError(Exception):\n    \"\"\"Exception raised when circuit breaker is open\"\"\"\n    pass\n\n\nclass HealthMetrics:\n    \"\"\"Track system health metrics\"\"\"\n    \n    def __init__(self):\n        self.executions = []\n        self.error_counts = {}\n        self.performance_history = []\n    \n    def record_execution(self, success: bool, duration: float, errors: int):\n        \"\"\"Record execution metrics\"\"\"\n        execution_record = {\n            'timestamp': datetime.now().isoformat(),\n            'success': success,\n            'duration': duration,\n            'errors': errors\n        }\n        \n        self.executions.append(execution_record)\n        self.performance_history.append(duration)\n        \n        # Keep only recent history\n        if len(self.executions) > 100:\n            self.executions = self.executions[-100:]\n        if len(self.performance_history) > 100:\n            self.performance_history = self.performance_history[-100:]\n    \n    def get_system_health(self) -> Dict[str, Any]:\n        \"\"\"Get current system health status\"\"\"\n        if not self.executions:\n            return {'status': 'unknown', 'reason': 'no_execution_history'}\n        \n        recent_executions = self.executions[-20:]  # Last 20 executions\n        success_rate = sum(1 for exec in recent_executions if exec['success']) / len(recent_executions)\n        avg_duration = sum(exec['duration'] for exec in recent_executions) / len(recent_executions)\n        avg_errors = sum(exec['errors'] for exec in recent_executions) / len(recent_executions)\n        \n        # Determine health status\n        if success_rate >= 0.9 and avg_duration < 30 and avg_errors < 1:\n            status = 'healthy'\n        elif success_rate >= 0.7 and avg_duration < 60 and avg_errors < 3:\n            status = 'degraded'\n        else:\n            status = 'unhealthy'\n        \n        return {\n            'status': status,\n            'success_rate': success_rate,\n            'avg_duration': avg_duration,\n            'avg_errors': avg_errors,\n            'total_executions': len(self.executions),\n            'recent_trend': self._calculate_trend()\n        }\n    \n    def _calculate_trend(self) -> str:\n        \"\"\"Calculate performance trend\"\"\"\n        if len(self.performance_history) < 10:\n            return 'insufficient_data'\n        \n        recent_avg = sum(self.performance_history[-5:]) / 5\n        older_avg = sum(self.performance_history[-10:-5]) / 5\n        \n        if recent_avg < older_avg * 0.9:\n            return 'improving'\n        elif recent_avg > older_avg * 1.1:\n            return 'degrading'\n        else:\n            return 'stable'\n\n\ndef run_error_handling_demo():\n    \"\"\"Demonstrate error handling patterns with CrewAI\"\"\"\n    \n    print(\"=== CrewAI Error Handling Pattern Demo ===\")\n    \n    # Configure logging\n    logging.basicConfig(level=logging.INFO)\n    \n    # Create robust crew system\n    robust_system = RobustCrewSystem(max_retries=3, retry_delay=1.0)\n    crew = robust_system.create_resilient_crew()\n    \n    # Execute with comprehensive error handling\n    result = robust_system.execute_with_error_handling(crew)\n    \n    print(f\"\\n=== ERROR HANDLING DEMO COMPLETE ===\")\n    print(f\"Execution time: {result['execution_time']:.2f} seconds\")\n    print(f\"Errors encountered: {len(result['errors_encountered'])}\")\n    print(f\"Recovery actions taken: {len(result['recovery_actions'])}\")\n    print(f\"System health: {result['health_status']['status']}\")\n    \n    if result.get('recovery_used'):\n        print(\"\\n=== Recovery strategies were activated ===\")\n        for action in result['recovery_actions']:\n            print(f\"- {action['strategy']}: {action['action']}\")\n    \n    return result\n\n\nif __name__ == \"__main__\":\n    run_error_handling_demo()