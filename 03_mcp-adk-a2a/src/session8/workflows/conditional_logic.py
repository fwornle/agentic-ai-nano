"""
Conditional Logic Engine - Session 8
Dynamic branching and decision logic for workflow automation.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import operator
import re
import logging

logger = logging.getLogger(__name__)


class ConditionOperator(Enum):
    """Logical operators for conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    REGEX_MATCH = "regex_match"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class LogicalOperator(Enum):
    """Logical operators for combining conditions."""
    AND = "and"
    OR = "or"
    NOT = "not"
    XOR = "xor"


@dataclass
class Condition:
    """Single condition for evaluation."""
    field_path: str                    # Path to field (e.g., "user.profile.age")
    operator: ConditionOperator        # Comparison operator
    value: Any                         # Value to compare against
    description: str = ""              # Human-readable description


@dataclass
class ConditionalRule:
    """Rule containing multiple conditions and logic."""
    id: str
    name: str
    conditions: List[Condition]
    logical_operator: LogicalOperator = LogicalOperator.AND
    description: str = ""
    priority: int = 0                  # Higher priority rules evaluated first
    enabled: bool = True


@dataclass
class ConditionalBranch:
    """Branch in conditional workflow."""
    id: str
    name: str
    rules: List[ConditionalRule]
    actions: List[str]                 # Action IDs to execute if conditions match
    default_branch: bool = False       # True if this is the default/fallback branch
    branch_probability: float = 0.0    # For A/B testing or probability-based routing


@dataclass
class EvaluationContext:
    """Context for condition evaluation."""
    data: Dict[str, Any]              # Data to evaluate against
    variables: Dict[str, Any]         # Runtime variables
    metadata: Dict[str, Any]          # Additional metadata
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EvaluationResult:
    """Result of condition evaluation."""
    rule_id: str
    rule_name: str
    matched: bool
    branch_id: Optional[str] = None
    branch_name: Optional[str] = None
    actions_to_execute: List[str] = field(default_factory=list)
    evaluation_details: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0


class ConditionEvaluator:
    """Evaluates individual conditions against data."""
    
    def __init__(self):
        self.operator_map = {
            ConditionOperator.EQUALS: operator.eq,
            ConditionOperator.NOT_EQUALS: operator.ne,
            ConditionOperator.GREATER_THAN: operator.gt,
            ConditionOperator.LESS_THAN: operator.lt,
            ConditionOperator.GREATER_EQUAL: operator.ge,
            ConditionOperator.LESS_EQUAL: operator.le,
        }
    
    def evaluate_condition(self, condition: Condition, context: EvaluationContext) -> bool:
        """Evaluate a single condition against the context."""
        try:
            # Extract field value using path
            field_value = self._get_field_value(condition.field_path, context.data)
            
            # Apply operator
            if condition.operator in self.operator_map:
                return self.operator_map[condition.operator](field_value, condition.value)
            elif condition.operator == ConditionOperator.CONTAINS:
                return self._evaluate_contains(field_value, condition.value)
            elif condition.operator == ConditionOperator.NOT_CONTAINS:
                return not self._evaluate_contains(field_value, condition.value)
            elif condition.operator == ConditionOperator.REGEX_MATCH:
                return self._evaluate_regex(field_value, condition.value)
            elif condition.operator == ConditionOperator.IN_LIST:
                return field_value in condition.value
            elif condition.operator == ConditionOperator.NOT_IN_LIST:
                return field_value not in condition.value
            elif condition.operator == ConditionOperator.IS_EMPTY:
                return self._is_empty(field_value)
            elif condition.operator == ConditionOperator.IS_NOT_EMPTY:
                return not self._is_empty(field_value)
            else:
                raise ValueError(f"Unknown operator: {condition.operator}")
        
        except Exception as e:
            logger.warning(f"Condition evaluation failed: {condition.field_path} {condition.operator.value} {condition.value} - {str(e)}")
            return False
    
    def _get_field_value(self, field_path: str, data: Dict[str, Any]) -> Any:
        """Extract field value using dot notation path."""
        if not field_path:
            return data
        
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                current = current[index] if 0 <= index < len(current) else None
            else:
                return None
            
            if current is None:
                return None
        
        return current
    
    def _evaluate_contains(self, field_value: Any, target_value: Any) -> bool:
        """Evaluate contains operation."""
        if field_value is None:
            return False
        
        if isinstance(field_value, (str, list, dict)):
            return target_value in field_value
        
        return str(target_value) in str(field_value)
    
    def _evaluate_regex(self, field_value: Any, pattern: str) -> bool:
        """Evaluate regex match."""
        if field_value is None:
            return False
        
        try:
            return bool(re.search(pattern, str(field_value)))
        except re.error:
            logger.warning(f"Invalid regex pattern: {pattern}")
            return False
    
    def _is_empty(self, value: Any) -> bool:
        """Check if value is empty."""
        if value is None:
            return True
        if isinstance(value, (str, list, dict)):
            return len(value) == 0
        return False


class ConditionalEngine:
    """Engine for evaluating conditional logic and routing."""
    
    def __init__(self):
        self.evaluator = ConditionEvaluator()
        self.evaluation_history: List[EvaluationResult] = []
        self.performance_metrics: Dict[str, Any] = {}
    
    async def evaluate_branches(self, branches: List[ConditionalBranch], 
                               context: EvaluationContext) -> EvaluationResult:
        """Evaluate branches and return the first matching branch."""
        start_time = datetime.now()
        
        # Sort branches by priority (higher priority first)
        sorted_branches = sorted(branches, key=lambda b: max((r.priority for r in b.rules), default=0), reverse=True)
        
        for branch in sorted_branches:
            if not branch.rules and not branch.default_branch:
                continue
            
            # Evaluate each rule in the branch
            for rule in branch.rules:
                if not rule.enabled:
                    continue
                
                rule_matched = await self._evaluate_rule(rule, context)
                
                if rule_matched:
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    result = EvaluationResult(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        matched=True,
                        branch_id=branch.id,
                        branch_name=branch.name,
                        actions_to_execute=branch.actions.copy(),
                        execution_time_ms=execution_time,
                        evaluation_details={
                            "branch_priority": max((r.priority for r in branch.rules), default=0),
                            "conditions_evaluated": len(rule.conditions),
                            "logical_operator": rule.logical_operator.value
                        }
                    )
                    
                    self.evaluation_history.append(result)
                    self._update_performance_metrics(result)
                    
                    return result
        
        # If no branch matched, check for default branch
        default_branches = [b for b in branches if b.default_branch]
        if default_branches:
            default_branch = default_branches[0]
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = EvaluationResult(
                rule_id="default",
                rule_name="Default Branch",
                matched=True,
                branch_id=default_branch.id,
                branch_name=default_branch.name,
                actions_to_execute=default_branch.actions.copy(),
                execution_time_ms=execution_time,
                evaluation_details={"reason": "default_branch"}
            )
            
            self.evaluation_history.append(result)
            return result
        
        # No match found
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        result = EvaluationResult(
            rule_id="no_match",
            rule_name="No Match",
            matched=False,
            execution_time_ms=execution_time,
            evaluation_details={"branches_evaluated": len(branches)}
        )
        
        self.evaluation_history.append(result)
        return result
    
    async def _evaluate_rule(self, rule: ConditionalRule, context: EvaluationContext) -> bool:
        """Evaluate a single rule with its conditions and logical operators."""
        if not rule.conditions:
            return False
        
        condition_results = []
        
        for condition in rule.conditions:
            result = self.evaluator.evaluate_condition(condition, context)
            condition_results.append(result)
        
        # Apply logical operator
        if rule.logical_operator == LogicalOperator.AND:
            return all(condition_results)
        elif rule.logical_operator == LogicalOperator.OR:
            return any(condition_results)
        elif rule.logical_operator == LogicalOperator.NOT:
            # For NOT, we typically negate the first condition
            return not condition_results[0] if condition_results else False
        elif rule.logical_operator == LogicalOperator.XOR:
            # XOR: exactly one condition should be true
            true_count = sum(condition_results)
            return true_count == 1
        else:
            return False
    
    def _update_performance_metrics(self, result: EvaluationResult):
        """Update performance metrics based on evaluation result."""
        if not hasattr(self, '_metrics_initialized'):
            self.performance_metrics = {
                "total_evaluations": 0,
                "successful_matches": 0,
                "average_execution_time": 0.0,
                "rule_hit_count": {},
                "branch_hit_count": {}
            }
            self._metrics_initialized = True
        
        self.performance_metrics["total_evaluations"] += 1
        
        if result.matched:
            self.performance_metrics["successful_matches"] += 1
            
            # Update rule hit count
            rule_id = result.rule_id
            self.performance_metrics["rule_hit_count"][rule_id] = \
                self.performance_metrics["rule_hit_count"].get(rule_id, 0) + 1
            
            # Update branch hit count
            if result.branch_id:
                branch_id = result.branch_id
                self.performance_metrics["branch_hit_count"][branch_id] = \
                    self.performance_metrics["branch_hit_count"].get(branch_id, 0) + 1
        
        # Update average execution time
        total_time = (self.performance_metrics["average_execution_time"] * 
                     (self.performance_metrics["total_evaluations"] - 1) + 
                     result.execution_time_ms)
        self.performance_metrics["average_execution_time"] = \
            total_time / self.performance_metrics["total_evaluations"]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report."""
        if not self.performance_metrics:
            return {"message": "No evaluations performed yet"}
        
        total_evals = self.performance_metrics["total_evaluations"]
        successful_matches = self.performance_metrics["successful_matches"]
        
        return {
            "performance_summary": {
                "total_evaluations": total_evals,
                "successful_matches": successful_matches,
                "match_rate": (successful_matches / total_evals * 100) if total_evals > 0 else 0,
                "average_execution_time_ms": self.performance_metrics["average_execution_time"]
            },
            "rule_performance": {
                "most_used_rules": sorted(
                    self.performance_metrics["rule_hit_count"].items(),
                    key=lambda x: x[1], reverse=True
                )[:5],
                "total_unique_rules": len(self.performance_metrics["rule_hit_count"])
            },
            "branch_performance": {
                "most_used_branches": sorted(
                    self.performance_metrics["branch_hit_count"].items(),
                    key=lambda x: x[1], reverse=True
                )[:5],
                "total_unique_branches": len(self.performance_metrics["branch_hit_count"])
            },
            "recent_evaluations": [
                {
                    "rule_name": r.rule_name,
                    "matched": r.matched,
                    "branch_name": r.branch_name,
                    "execution_time_ms": r.execution_time_ms
                }
                for r in self.evaluation_history[-10:]  # Last 10 evaluations
            ]
        }


class ABTestingManager:
    """Manager for A/B testing and probability-based routing."""
    
    def __init__(self, seed: Optional[int] = None):
        import random
        if seed:
            random.seed(seed)
        self.random = random
        self.test_results: Dict[str, Dict[str, Any]] = {}
    
    def create_ab_test_branches(self, test_name: str, 
                               variants: List[Dict[str, Any]]) -> List[ConditionalBranch]:
        """Create branches for A/B testing."""
        branches = []
        
        for i, variant in enumerate(variants):
            branch_id = f"{test_name}_variant_{i}"
            probability = variant.get('probability', 1.0 / len(variants))
            
            branch = ConditionalBranch(
                id=branch_id,
                name=variant.get('name', f"Variant {i}"),
                rules=[],  # A/B testing doesn't use traditional rules
                actions=variant.get('actions', []),
                branch_probability=probability
            )
            branches.append(branch)
        
        return branches
    
    async def route_ab_test(self, test_name: str, 
                           branches: List[ConditionalBranch],
                           context: EvaluationContext) -> EvaluationResult:
        """Route traffic based on A/B test probabilities."""
        # Get user identifier for consistent routing
        user_id = context.data.get('user_id') or context.data.get('session_id', 'anonymous')
        
        # Use hash for deterministic routing based on user
        import hashlib
        hash_value = int(hashlib.md5(f"{test_name}_{user_id}".encode()).hexdigest(), 16)
        random_value = (hash_value % 100) / 100.0  # Convert to 0-1 range
        
        # Select branch based on cumulative probabilities
        cumulative_probability = 0.0
        selected_branch = None
        
        for branch in branches:
            cumulative_probability += branch.branch_probability
            if random_value <= cumulative_probability:
                selected_branch = branch
                break
        
        # Fallback to first branch if no selection made
        if not selected_branch and branches:
            selected_branch = branches[0]
        
        if selected_branch:
            result = EvaluationResult(
                rule_id=f"ab_test_{test_name}",
                rule_name=f"A/B Test: {test_name}",
                matched=True,
                branch_id=selected_branch.id,
                branch_name=selected_branch.name,
                actions_to_execute=selected_branch.actions.copy(),
                evaluation_details={
                    "test_name": test_name,
                    "user_id": user_id,
                    "random_value": random_value,
                    "selected_probability": selected_branch.branch_probability,
                    "routing_type": "ab_test"
                }
            )
            
            # Track test participation
            self._track_test_participation(test_name, selected_branch.id, user_id)
            
            return result
        
        # No branch selected
        return EvaluationResult(
            rule_id="ab_test_no_match",
            rule_name="A/B Test No Match",
            matched=False,
            evaluation_details={"test_name": test_name}
        )
    
    def _track_test_participation(self, test_name: str, branch_id: str, user_id: str):
        """Track user participation in A/B test."""
        if test_name not in self.test_results:
            self.test_results[test_name] = {
                "participants": {},
                "branch_counts": {},
                "start_time": datetime.now().isoformat()
            }
        
        test_data = self.test_results[test_name]
        test_data["participants"][user_id] = {
            "branch_id": branch_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update branch counts
        test_data["branch_counts"][branch_id] = \
            test_data["branch_counts"].get(branch_id, 0) + 1
    
    def get_ab_test_results(self, test_name: str) -> Dict[str, Any]:
        """Get A/B test results and statistics."""
        if test_name not in self.test_results:
            return {"error": f"No test data found for {test_name}"}
        
        test_data = self.test_results[test_name]
        total_participants = len(test_data["participants"])
        branch_counts = test_data["branch_counts"]
        
        branch_statistics = {}
        for branch_id, count in branch_counts.items():
            branch_statistics[branch_id] = {
                "participant_count": count,
                "percentage": (count / total_participants * 100) if total_participants > 0 else 0
            }
        
        return {
            "test_name": test_name,
            "total_participants": total_participants,
            "branch_statistics": branch_statistics,
            "start_time": test_data["start_time"],
            "duration_days": (datetime.now() - datetime.fromisoformat(test_data["start_time"])).days
        }