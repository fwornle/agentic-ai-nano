# src/session3/circuit_breaker.py
"""
Circuit breaker pattern for preventing cascading failures in workflows.
"""

from langgraph.graph import StateGraph, END
from langgraph_basics import AgentState
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open" # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker implementation for workflow protection"""
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout_seconds)
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "time_until_retry": self._time_until_retry()
        }
    
    def _time_until_retry(self) -> int:
        """Calculate seconds until retry attempt"""
        if self.state != CircuitBreakerState.OPEN or self.last_failure_time is None:
            return 0
        
        elapsed = datetime.now() - self.last_failure_time
        remaining = self.timeout_seconds - elapsed.total_seconds()
        return max(0, int(remaining))


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


# Global circuit breaker instance for workflow
workflow_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=30)


def protected_operation(state: AgentState) -> AgentState:
    """Operation protected by circuit breaker"""
    current_task = state["current_task"]
    
    try:
        # Execute operation through circuit breaker
        result = workflow_circuit_breaker.call(_risky_operation, current_task)
        
        # Success case
        updated_results = state["results"].copy()
        updated_results["operation_result"] = result
        updated_results["circuit_breaker_state"] = workflow_circuit_breaker.get_state_info()
        
        return {
            "results": updated_results,
            "current_task": "operation_successful"
        }
        
    except CircuitBreakerError as e:
        # Circuit breaker blocked the request
        updated_results = state["results"].copy()
        updated_results["circuit_breaker_error"] = {
            "error_type": "CircuitBreakerOpen",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
        updated_results["circuit_breaker_state"] = workflow_circuit_breaker.get_state_info()
        
        return {
            "results": updated_results,
            "current_task": "circuit_breaker_blocked"
        }
        
    except Exception as e:
        # Actual operation failure
        updated_results = state["results"].copy()
        updated_results["operation_error"] = {
            "error_type": type(e).__name__,
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
        updated_results["circuit_breaker_state"] = workflow_circuit_breaker.get_state_info()
        
        return {
            "results": updated_results,
            "current_task": "operation_failed"
        }


def _risky_operation(task: str) -> str:
    """Simulated risky operation that might fail"""
    import random
    
    # 30% chance of failure for demonstration
    if random.random() < 0.3:
        raise Exception(f"Operation failed for task: {task}")
    
    return f"Successfully completed: {task}"


def fallback_operation(state: AgentState) -> AgentState:
    """Fallback when circuit breaker is open"""
    current_task = state["current_task"]
    
    fallback_result = {
        "fallback_used": True,
        "original_task": current_task,
        "fallback_result": f"Fallback solution for: {current_task}",
        "circuit_breaker_bypassed": True,
        "timestamp": datetime.now().isoformat()
    }
    
    updated_results = state["results"].copy()
    updated_results["fallback_result"] = fallback_result
    
    return {
        "results": updated_results,
        "current_task": "fallback_complete"
    }


def wait_and_retry(state: AgentState) -> AgentState:
    """Wait for circuit breaker to allow retry"""
    circuit_breaker_state = workflow_circuit_breaker.get_state_info()
    
    wait_info = {
        "waiting_for_retry": True,
        "circuit_breaker_state": circuit_breaker_state["state"],
        "time_until_retry": circuit_breaker_state["time_until_retry"],
        "wait_timestamp": datetime.now().isoformat()
    }
    
    updated_results = state["results"].copy()
    updated_results["wait_info"] = wait_info
    
    return {
        "results": updated_results,
        "current_task": "waiting_for_retry"
    }


def create_circuit_breaker_workflow():
    """Create workflow with circuit breaker protection"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("protected_op", protected_operation)
    workflow.add_node("fallback", fallback_operation)
    workflow.add_node("wait_retry", wait_and_retry)
    
    # Start with protected operation
    workflow.set_entry_point("protected_op")
    
    # Route based on operation result
    workflow.add_conditional_edges(
        "protected_op",
        check_circuit_breaker_result,
        {
            "success": END,
            "circuit_breaker_blocked": "fallback",
            "operation_failed": "wait_retry",
            "fallback": "fallback"
        }
    )
    
    # After waiting, retry the protected operation
    workflow.add_edge("wait_retry", "protected_op")
    
    # Fallback completes the workflow
    workflow.add_edge("fallback", END)
    
    return workflow.compile()


def check_circuit_breaker_result(state: AgentState) -> str:
    """Check result of circuit breaker protected operation"""
    results = state["results"]
    current_task = state["current_task"]
    
    if current_task == "operation_successful":
        return "success"
    elif current_task == "circuit_breaker_blocked":
        return "circuit_breaker_blocked"
    elif current_task == "operation_failed":
        # Check if we should use fallback or wait
        circuit_state = results.get("circuit_breaker_state", {})
        if circuit_state.get("state") == "open":
            return "fallback"
        else:
            return "operation_failed"
    else:
        return "fallback"


# Advanced circuit breaker with custom policies
class AdvancedCircuitBreaker(CircuitBreaker):
    """Advanced circuit breaker with custom failure policies"""
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60, 
                 failure_policy=None, success_threshold: int = 2):
        super().__init__(failure_threshold, timeout_seconds)
        self.failure_policy = failure_policy or self._default_failure_policy
        self.success_threshold = success_threshold
        self.success_count = 0
        
    def _default_failure_policy(self, exception: Exception) -> bool:
        """Default policy - all exceptions count as failures"""
        return True
    
    def _on_failure(self):
        """Handle failed operation with custom policy"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0  # Reset success count
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
    
    def _on_success(self):
        """Handle successful operation in half-open state"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.failure_count = 0
                self.success_count = 0
                self.state = CircuitBreakerState.CLOSED
        else:
            self.failure_count = 0
            self.state = CircuitBreakerState.CLOSED


# Circuit breaker metrics collector
class CircuitBreakerMetrics:
    """Collect metrics for circuit breaker monitoring"""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_breaker_blocks": 0,
            "state_transitions": []
        }
    
    def record_request(self, success: bool, blocked: bool = False):
        """Record a request"""
        self.metrics["total_requests"] += 1
        
        if blocked:
            self.metrics["circuit_breaker_blocks"] += 1
        elif success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
    
    def record_state_transition(self, from_state: CircuitBreakerState, 
                              to_state: CircuitBreakerState):
        """Record state transition"""
        self.metrics["state_transitions"].append({
            "from": from_state.value,
            "to": to_state.value,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        total = self.metrics["total_requests"]
        if total == 0:
            return self.metrics
        
        return {
            **self.metrics,
            "success_rate": self.metrics["successful_requests"] / total,
            "failure_rate": self.metrics["failed_requests"] / total,
            "block_rate": self.metrics["circuit_breaker_blocks"] / total
        }