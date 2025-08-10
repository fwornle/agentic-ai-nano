# src/session3/error_handling.py
"""
Error handling and recovery patterns for LangGraph workflows.
"""

from langgraph.graph import StateGraph, END
from langgraph_basics import AgentState
import logging
from datetime import datetime
from typing import Dict, Any


class WorkflowError(Exception):
    """Custom exception for workflow errors"""
    pass


class RetryableError(WorkflowError):
    """Error that can be retried"""
    pass


class FatalError(WorkflowError):
    """Fatal error that should stop the workflow"""
    pass


def risky_operation(state: AgentState) -> AgentState:
    """Simulates an operation that might fail"""
    current_task = state["current_task"]
    iteration_count = state.get("iteration_count", 0)
    
    # Simulate different failure scenarios based on iteration
    if iteration_count == 1:
        # First attempt - simulate network error
        error_info = {
            "error_type": "NetworkError",
            "error_message": "Connection timeout",
            "is_retryable": True,
            "timestamp": datetime.now().isoformat()
        }
        
        updated_results = state["results"].copy()
        updated_results["error"] = error_info
        
        return {
            "results": updated_results,
            "current_task": "operation_failed"
        }
    
    elif iteration_count == 2:
        # Second attempt - simulate data error
        error_info = {
            "error_type": "DataError", 
            "error_message": "Invalid data format",
            "is_retryable": True,
            "timestamp": datetime.now().isoformat()
        }
        
        updated_results = state["results"].copy()
        updated_results["error"] = error_info
        
        return {
            "results": updated_results,
            "current_task": "operation_failed"
        }
    
    else:
        # Third attempt or later - succeed
        success_result = f"Operation completed successfully for: {current_task}"
        
        updated_results = state["results"].copy()
        updated_results["operation_result"] = success_result
        updated_results.pop("error", None)  # Clear any previous errors
        
        return {
            "results": updated_results,
            "current_task": "operation_successful"
        }


def error_handler(state: AgentState) -> AgentState:
    """Handle errors and decide on recovery strategy"""
    error_info = state["results"].get("error", {})
    iteration_count = state.get("iteration_count", 0)
    
    error_type = error_info.get("error_type", "Unknown")
    is_retryable = error_info.get("is_retryable", False)
    
    # Determine recovery strategy
    recovery_strategy = determine_recovery_strategy(error_type, is_retryable, iteration_count)
    
    error_handling_result = {
        "original_error": error_info,
        "recovery_strategy": recovery_strategy,
        "retry_count": iteration_count,
        "max_retries": 3,
        "handled_at": datetime.now().isoformat()
    }
    
    updated_results = state["results"].copy()
    updated_results["error_handling"] = error_handling_result
    
    return {
        "results": updated_results,
        "current_task": "error_handled",
        "iteration_count": iteration_count + 1
    }


def retry_operation(state: AgentState) -> AgentState:
    """Retry the failed operation with backoff"""
    retry_count = state.get("iteration_count", 0)
    
    # Implement exponential backoff logic (simulated)
    backoff_seconds = 2 ** retry_count
    
    retry_info = {
        "retry_attempt": retry_count,
        "backoff_seconds": backoff_seconds,
        "retry_timestamp": datetime.now().isoformat()
    }
    
    updated_results = state["results"].copy()
    updated_results["retry_info"] = retry_info
    
    return {
        "results": updated_results,
        "current_task": state["current_task"]  # Keep original task for retry
    }


def fallback_operation(state: AgentState) -> AgentState:
    """Fallback operation when retries are exhausted"""
    original_task = state["current_task"]
    error_info = state["results"].get("error", {})
    
    # Implement fallback logic
    fallback_result = {
        "fallback_used": True,
        "original_task": original_task,
        "fallback_result": f"Fallback solution for: {original_task}",
        "original_error": error_info,
        "fallback_timestamp": datetime.now().isoformat(),
        "success": True
    }
    
    updated_results = state["results"].copy()
    updated_results["fallback_result"] = fallback_result
    updated_results.pop("error", None)  # Clear error
    
    return {
        "results": updated_results,
        "current_task": "fallback_complete"
    }


def log_error(state: AgentState) -> AgentState:
    """Log error for monitoring and analysis"""
    error_info = state["results"].get("error", {})
    
    # Simulate error logging
    log_entry = {
        "log_level": "ERROR",
        "error_type": error_info.get("error_type", "Unknown"),
        "error_message": error_info.get("error_message", "No message"),
        "task_context": state["current_task"],
        "iteration": state.get("iteration_count", 0),
        "timestamp": datetime.now().isoformat(),
        "logged": True
    }
    
    # In real implementation, would write to logging system
    logging.error(f"Workflow error: {log_entry}")
    
    updated_results = state["results"].copy()
    updated_results["error_log"] = log_entry
    
    return {
        "results": updated_results,
        "current_task": state["current_task"]
    }


def create_error_handling_workflow():
    """Create workflow with comprehensive error handling"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("operation", risky_operation)
    workflow.add_node("error_handler", error_handler)
    workflow.add_node("retry", retry_operation)
    workflow.add_node("fallback", fallback_operation)
    workflow.add_node("logger", log_error)
    
    # Start with the risky operation
    workflow.set_entry_point("operation")
    
    # Route based on operation result
    workflow.add_conditional_edges(
        "operation",
        check_operation_result,
        {
            "success": END,
            "error": "error_handler"
        }
    )
    
    # After error handling, decide next step
    workflow.add_conditional_edges(
        "error_handler",
        decide_recovery_action,
        {
            "retry": "retry",
            "fallback": "fallback",
            "fatal": "logger"
        }
    )
    
    # After retry, go back to operation
    workflow.add_edge("retry", "operation")
    
    # Fallback completes the workflow
    workflow.add_edge("fallback", END)
    
    # Logger ends workflow for fatal errors
    workflow.add_edge("logger", END)
    
    return workflow.compile()


# Decision functions
def check_operation_result(state: AgentState) -> str:
    """Check if operation succeeded or failed"""
    if "error" in state["results"]:
        return "error"
    else:
        return "success"


def decide_recovery_action(state: AgentState) -> str:
    """Decide on recovery action based on error analysis"""
    error_handling = state["results"].get("error_handling", {})
    recovery_strategy = error_handling.get("recovery_strategy", "unknown")
    
    return recovery_strategy


def determine_recovery_strategy(error_type: str, is_retryable: bool, retry_count: int) -> str:
    """Determine the appropriate recovery strategy"""
    
    # Fatal errors
    if error_type in ["AuthenticationError", "PermissionError"]:
        return "fatal"
    
    # Max retries reached
    if retry_count >= 3:
        return "fallback"
    
    # Retryable errors
    if is_retryable and error_type in ["NetworkError", "TimeoutError", "DataError"]:
        return "retry"
    
    # Default to fallback
    return "fallback"


# Error recovery utilities
class ErrorRecoveryManager:
    """Manager for error recovery strategies"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.error_history = []
        self.recovery_strategies = {}
    
    def register_strategy(self, error_type: str, strategy_func):
        """Register recovery strategy for error type"""
        self.recovery_strategies[error_type] = strategy_func
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle error with registered strategy"""
        error_type = type(error).__name__
        
        # Log error
        self.error_history.append({
            "error_type": error_type,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        
        # Apply recovery strategy
        if error_type in self.recovery_strategies:
            return self.recovery_strategies[error_type](error, context)
        else:
            return self._default_recovery(error, context)
    
    def _default_recovery(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Default recovery strategy"""
        return {
            "recovery_action": "log_and_continue",
            "error_handled": True,
            "fallback_used": True
        }
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        if not self.error_history:
            return {"total_errors": 0}
        
        error_types = {}
        for error in self.error_history:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "error_types": error_types,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        }