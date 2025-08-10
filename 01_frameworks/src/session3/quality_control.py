# src/session3/quality_control.py
"""
Quality control and validation patterns for LangGraph workflows.
"""

from langgraph.graph import StateGraph, END
from langgraph_basics import AgentState
from datetime import datetime
from typing import Dict, List, Any, Callable


class QualityMetrics:
    """Quality metrics for workflow outputs"""
    
    def __init__(self):
        self.metrics = {}
    
    def add_metric(self, name: str, value: float, weight: float = 1.0):
        """Add a quality metric"""
        self.metrics[name] = {"value": value, "weight": weight}
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall quality score"""
        if not self.metrics:
            return 0.0
        
        weighted_sum = sum(metric["value"] * metric["weight"] for metric in self.metrics.values())
        total_weight = sum(metric["weight"] for metric in self.metrics.values())
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed quality metrics"""
        return {
            "individual_metrics": self.metrics,
            "overall_score": self.calculate_overall_score(),
            "metric_count": len(self.metrics)
        }


def generate_content(state: AgentState) -> AgentState:
    """Generate initial content"""
    current_task = state["current_task"]
    
    # Simulate content generation
    generated_content = f"Generated content for: {current_task}"
    
    updated_results = state["results"].copy()
    updated_results["generated_content"] = generated_content
    updated_results["generation_timestamp"] = datetime.now().isoformat()
    
    return {
        "results": updated_results,
        "current_task": "content_generated"
    }


def quality_check(state: AgentState) -> AgentState:
    """Perform quality checks on content"""
    content = state["results"].get("generated_content", "")
    
    # Initialize quality metrics
    quality_metrics = QualityMetrics()
    
    # Content length check
    length_score = min(len(content) / 100, 1.0)  # Normalize to max 1.0
    quality_metrics.add_metric("length", length_score, weight=0.2)
    
    # Content complexity check
    complexity_score = calculate_complexity_score(content)
    quality_metrics.add_metric("complexity", complexity_score, weight=0.3)
    
    # Content coherence check
    coherence_score = calculate_coherence_score(content)
    quality_metrics.add_metric("coherence", coherence_score, weight=0.3)
    
    # Content completeness check
    completeness_score = calculate_completeness_score(content, state["current_task"])
    quality_metrics.add_metric("completeness", completeness_score, weight=0.2)
    
    # Calculate overall quality
    overall_quality = quality_metrics.calculate_overall_score()
    
    quality_assessment = {
        "overall_quality": overall_quality,
        "detailed_metrics": quality_metrics.get_detailed_metrics(),
        "quality_threshold": 0.7,
        "passes_quality": overall_quality >= 0.7,
        "assessment_timestamp": datetime.now().isoformat()
    }
    
    updated_results = state["results"].copy()
    updated_results["quality_assessment"] = quality_assessment
    
    return {
        "results": updated_results,
        "current_task": "quality_assessed"
    }


def improve_content(state: AgentState) -> AgentState:
    """Improve content based on quality feedback"""
    quality_assessment = state["results"].get("quality_assessment", {})
    original_content = state["results"].get("generated_content", "")
    
    # Identify improvement areas
    detailed_metrics = quality_assessment.get("detailed_metrics", {}).get("individual_metrics", {})
    improvements = []
    
    for metric_name, metric_data in detailed_metrics.items():
        if metric_data["value"] < 0.7:
            improvements.append(metric_name)
    
    # Apply improvements
    improved_content = apply_improvements(original_content, improvements)
    
    improvement_info = {
        "original_content": original_content,
        "improved_content": improved_content,
        "improvements_applied": improvements,
        "improvement_timestamp": datetime.now().isoformat()
    }
    
    updated_results = state["results"].copy()
    updated_results["improved_content"] = improved_content
    updated_results["improvement_info"] = improvement_info
    
    return {
        "results": updated_results,
        "current_task": "content_improved"
    }


def final_validation(state: AgentState) -> AgentState:
    """Final validation before approval"""
    content = state["results"].get("improved_content") or state["results"].get("generated_content", "")
    
    # Run final validation checks
    validation_checks = {
        "content_exists": bool(content.strip()),
        "minimum_length": len(content) >= 20,
        "contains_task_reference": state["current_task"].lower() in content.lower(),
        "no_placeholder_text": "TODO" not in content and "PLACEHOLDER" not in content,
        "proper_formatting": check_formatting(content)
    }
    
    # Calculate validation score
    passed_checks = sum(1 for check in validation_checks.values() if check)
    validation_score = passed_checks / len(validation_checks)
    
    validation_result = {
        "validation_checks": validation_checks,
        "validation_score": validation_score,
        "validation_passed": validation_score >= 0.8,
        "final_content": content,
        "validation_timestamp": datetime.now().isoformat()
    }
    
    updated_results = state["results"].copy()
    updated_results["final_validation"] = validation_result
    
    return {
        "results": updated_results,
        "current_task": "validation_complete"
    }


def create_quality_control_workflow():
    """Create workflow with comprehensive quality control"""
    
    workflow = StateGraph(AgentState)
    
    # Add quality control nodes
    workflow.add_node("generator", generate_content)
    workflow.add_node("quality_checker", quality_check)
    workflow.add_node("improver", improve_content)
    workflow.add_node("validator", final_validation)
    
    # Start with content generation
    workflow.set_entry_point("generator")
    
    # Always check quality after generation
    workflow.add_edge("generator", "quality_checker")
    
    # Route based on quality assessment
    workflow.add_conditional_edges(
        "quality_checker",
        check_quality_result,
        {
            "approve": "validator",
            "improve": "improver"
        }
    )
    
    # After improvement, go to final validation
    workflow.add_edge("improver", "validator")
    
    # Final validation determines completion
    workflow.add_conditional_edges(
        "validator",
        check_validation_result,
        {
            "approved": END,
            "needs_more_work": "improver"
        }
    )
    
    return workflow.compile()


# Decision functions
def check_quality_result(state: AgentState) -> str:
    """Check if content passes quality assessment"""
    quality_assessment = state["results"].get("quality_assessment", {})
    passes_quality = quality_assessment.get("passes_quality", False)
    
    return "approve" if passes_quality else "improve"


def check_validation_result(state: AgentState) -> str:
    """Check if content passes final validation"""
    validation_result = state["results"].get("final_validation", {})
    validation_passed = validation_result.get("validation_passed", False)
    
    return "approved" if validation_passed else "needs_more_work"


# Quality calculation functions
def calculate_complexity_score(content: str) -> float:
    """Calculate content complexity score"""
    if not content:
        return 0.0
    
    # Simple complexity metrics
    words = content.split()
    sentences = content.split('.')
    
    if not words:
        return 0.0
    
    avg_word_length = sum(len(word) for word in words) / len(words)
    avg_sentence_length = len(words) / max(len(sentences), 1)
    
    # Normalize complexity score
    complexity = (avg_word_length + avg_sentence_length) / 20
    return min(complexity, 1.0)


def calculate_coherence_score(content: str) -> float:
    """Calculate content coherence score"""
    if not content:
        return 0.0
    
    # Simple coherence metrics
    sentences = [s.strip() for s in content.split('.') if s.strip()]
    
    if len(sentences) < 2:
        return 0.5
    
    # Check for connecting words and consistent topics
    connecting_words = ['however', 'therefore', 'furthermore', 'additionally', 'moreover']
    connections = sum(1 for word in connecting_words if word in content.lower())
    
    coherence = min((connections + len(sentences)) / (len(sentences) * 2), 1.0)
    return coherence


def calculate_completeness_score(content: str, task: str) -> float:
    """Calculate content completeness score"""
    if not content or not task:
        return 0.0
    
    # Check if content addresses the task
    task_words = task.lower().split()
    content_lower = content.lower()
    
    addressed_words = sum(1 for word in task_words if word in content_lower)
    completeness = addressed_words / max(len(task_words), 1)
    
    return min(completeness, 1.0)


def check_formatting(content: str) -> bool:
    """Check if content has proper formatting"""
    if not content:
        return False
    
    # Basic formatting checks
    has_proper_sentences = content.count('.') > 0
    has_reasonable_length = 10 < len(content) < 10000
    no_excessive_whitespace = not ('  ' in content or '\n\n\n' in content)
    
    return has_proper_sentences and has_reasonable_length and no_excessive_whitespace


def apply_improvements(content: str, improvement_areas: List[str]) -> str:
    """Apply improvements to content"""
    improved_content = content
    
    for area in improvement_areas:
        if area == "length":
            improved_content += " Additional detailed content to improve length and depth."
        elif area == "complexity":
            improved_content = improved_content.replace(".", ". Furthermore,")
        elif area == "coherence":
            improved_content = "Therefore, " + improved_content
        elif area == "completeness":
            improved_content += " This comprehensively addresses the task requirements."
    
    return improved_content


# Quality control decorators
def quality_gate(threshold: float = 0.7):
    """Decorator for quality gates"""
    def decorator(func: Callable) -> Callable:
        def wrapper(state: AgentState) -> AgentState:
            result = func(state)
            
            # Check if quality assessment exists
            quality_assessment = result["results"].get("quality_assessment")
            if quality_assessment:
                quality_score = quality_assessment.get("overall_quality", 0)
                
                if quality_score < threshold:
                    result["results"]["quality_gate_failed"] = True
                    result["results"]["required_threshold"] = threshold
                    result["results"]["actual_score"] = quality_score
            
            return result
        return wrapper
    return decorator


# Quality control pipeline
class QualityControlPipeline:
    """Pipeline for quality control processes"""
    
    def __init__(self):
        self.quality_checks = []
        self.improvement_strategies = {}
        self.validation_rules = []
    
    def add_quality_check(self, name: str, check_func: Callable, weight: float = 1.0):
        """Add quality check to pipeline"""
        self.quality_checks.append({
            "name": name,
            "function": check_func,
            "weight": weight
        })
    
    def add_improvement_strategy(self, metric: str, strategy_func: Callable):
        """Add improvement strategy for specific metric"""
        self.improvement_strategies[metric] = strategy_func
    
    def add_validation_rule(self, rule_func: Callable):
        """Add validation rule"""
        self.validation_rules.append(rule_func)
    
    def run_quality_pipeline(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete quality control pipeline"""
        
        # Run quality checks
        quality_results = {}
        for check in self.quality_checks:
            try:
                score = check["function"](content, context)
                quality_results[check["name"]] = {
                    "score": score,
                    "weight": check["weight"]
                }
            except Exception as e:
                quality_results[check["name"]] = {
                    "score": 0.0,
                    "weight": check["weight"],
                    "error": str(e)
                }
        
        # Calculate overall quality
        if quality_results:
            weighted_sum = sum(result["score"] * result["weight"] 
                             for result in quality_results.values())
            total_weight = sum(result["weight"] for result in quality_results.values())
            overall_quality = weighted_sum / total_weight if total_weight > 0 else 0.0
        else:
            overall_quality = 0.0
        
        return {
            "quality_results": quality_results,
            "overall_quality": overall_quality,
            "pipeline_timestamp": datetime.now().isoformat()
        }