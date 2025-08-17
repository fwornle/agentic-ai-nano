"""
Multi-Agent Patterns & ReAct Implementation
Session 8: Core ReAct Pattern Implementation

This module implements sophisticated ReAct (Reasoning + Acting) patterns with
meta-reasoning capabilities, transparent trace analysis, and adaptive
reasoning strategies for production-ready agent systems.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Enumeration of available action types in ReAct pattern"""
    SEARCH = "search"
    CALCULATE = "calculate"
    REASON = "reason"
    PLAN = "plan"
    EXECUTE = "execute"
    FINAL_ANSWER = "final_answer"
    TOOL_USE = "tool_use"
    META_REASON = "meta_reason"


class ReasoningQuality(Enum):
    """Quality assessment levels for reasoning steps"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    POOR = "poor"
    FAILED = "failed"


@dataclass
class ReActStep:
    """Individual step in ReAct reasoning chain with comprehensive metadata"""
    step_number: int
    thought: str
    action: ActionType
    action_input: str
    observation: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    duration: timedelta = field(default_factory=lambda: timedelta(0))
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary for serialization"""
        return {
            'step_number': self.step_number,
            'thought': self.thought,
            'action': self.action.value,
            'action_input': self.action_input,
            'observation': self.observation,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration.total_seconds(),
            'metadata': self.metadata,
            'quality_score': self.quality_score
        }


@dataclass
class ReActTrace:
    """Complete ReAct reasoning trace with analysis"""
    problem: str
    steps: List[ReActStep]
    final_answer: Optional[str] = None
    success: bool = False
    total_duration: timedelta = field(default_factory=lambda: timedelta(0))
    quality_assessment: Optional[Dict[str, Any]] = None
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class MockLLM:
    """Mock LLM client for demonstration purposes"""
    
    async def generate(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate mock response based on prompt keywords"""
        await asyncio.sleep(0.1)  # Simulate API call
        
        if "thought" in prompt.lower():
            return "I need to analyze this problem step by step and determine the best approach."
        elif "action" in prompt.lower():
            if "search" in prompt.lower():
                return '{"action": "search", "input": "relevant query"}'
            elif "calculate" in prompt.lower():
                return '{"action": "calculate", "input": "mathematical expression"}'
            else:
                return '{"action": "reason", "input": "deeper analysis needed"}'
        else:
            return "This is a mock response for demonstration purposes."


class AdvancedReActAgent:
    """
    Advanced ReAct agent with meta-reasoning, quality assessment, and
    adaptive strategies for sophisticated problem-solving scenarios.
    """
    
    def __init__(self, llm_client=None, tools: Optional[Dict[str, Any]] = None, 
                 max_steps: int = 15, confidence_threshold: float = 0.8):
        self.llm = llm_client or MockLLM()
        self.tools = tools or {}
        self.max_steps = max_steps
        self.confidence_threshold = confidence_threshold
        self.reasoning_history: List[ReActTrace] = []
        self.meta_reasoner = MetaReActAnalyzer(self.llm)
        self.adaptation_engine = AdaptationEngine()
        
    async def solve_with_react(self, problem: str, context: Optional[Dict[str, Any]] = None) -> ReActTrace:
        """
        Solve problem using advanced ReAct pattern with meta-reasoning
        
        Args:
            problem: The problem to solve
            context: Optional context information
            
        Returns:
            Complete ReAct trace with solution
        """
        logger.info(f"Starting ReAct solution for problem: {problem[:50]}...")
        start_time = datetime.now()
        
        trace = ReActTrace(problem=problem)
        current_step = 1
        current_context = problem
        
        # Initial problem analysis
        initial_thought = await self._generate_initial_analysis(problem, context)
        
        while current_step <= self.max_steps:
            step_start = datetime.now()
            
            # Execute reasoning step
            step = await self._execute_reasoning_step(
                current_context, initial_thought, current_step, trace
            )
            step.duration = datetime.now() - step_start
            trace.steps.append(step)
            
            # Check for completion
            if step.action == ActionType.FINAL_ANSWER:
                trace.final_answer = step.action_input
                trace.success = True
                break
                
            # Adaptive confidence checking
            if step.confidence < 0.3 and current_step > 3:
                # Trigger meta-reasoning for low confidence
                meta_step = await self._trigger_meta_reasoning(trace, current_step)
                if meta_step:
                    trace.steps.append(meta_step)
                    current_step += 1
                    
            # Update context for next iteration
            current_context = self._build_context_from_history(trace.steps[-3:])
            current_step += 1
            
        # Final trace analysis and quality assessment
        trace.total_duration = datetime.now() - start_time
        trace.quality_assessment = await self.meta_reasoner.analyze_reasoning_quality(trace.steps)
        
        # Learn from this execution
        await self.adaptation_engine.learn_from_trace(trace)
        
        # Store in history
        self.reasoning_history.append(trace)
        
        logger.info(f"ReAct solution completed in {trace.total_duration.total_seconds():.2f}s")
        return trace
    
    async def _generate_initial_analysis(self, problem: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate comprehensive initial analysis of the problem"""
        
        analysis_prompt = f"""
        Analyze this problem comprehensively:
        Problem: {problem}
        Context: {context or "No additional context"}
        
        Consider:
        1. What type of problem is this?
        2. What information do we have vs. need?
        3. What approaches might work?
        4. What are potential challenges?
        5. How should we proceed?
        
        Provide a clear initial analysis:
        """
        
        return await self.llm.generate(analysis_prompt)
    
    async def _execute_reasoning_step(
        self, context: str, previous_thought: str, step_num: int, trace: ReActTrace
    ) -> ReActStep:
        """Execute a single ReAct reasoning step with enhanced error handling"""
        
        # Generate thought based on current context
        thought_prompt = self._build_enhanced_thought_prompt(context, previous_thought, trace)
        thought = await self.llm.generate(thought_prompt)
        
        # Determine action based on thought and context
        action_decision = await self._decide_optimal_action(thought, context, trace)
        action_type = ActionType(action_decision['action'])
        action_input = action_decision['input']
        
        # Execute action with comprehensive error handling
        observation = await self._execute_action_with_fallback(action_type, action_input)
        
        # Calculate multi-dimensional confidence
        confidence = await self._calculate_enhanced_confidence(
            thought, action_type, observation, trace
        )
        
        # Quality scoring
        quality_score = await self._assess_step_quality(thought, action_type, observation)
        
        return ReActStep(
            step_number=step_num,
            thought=thought,
            action=action_type,
            action_input=action_input,
            observation=observation,
            confidence=confidence,
            quality_score=quality_score,
            metadata={
                'context_length': len(context),
                'previous_steps': len(trace.steps),
                'action_success': 'error' not in observation.lower()
            }
        )
    
    def _build_enhanced_thought_prompt(
        self, context: str, previous_thought: str, trace: ReActTrace
    ) -> str:
        """Build sophisticated thought prompt with reasoning guidelines"""
        
        recent_history = self._get_recent_history_summary(trace.steps[-3:] if trace.steps else [])
        
        return f"""
        CURRENT SITUATION: {context}
        PREVIOUS THOUGHT: {previous_thought}
        RECENT PROGRESS: {recent_history}
        
        Think systematically about the current situation:
        
        1. ASSESSMENT: What have we learned so far?
        2. GAPS: What information or analysis is still needed?
        3. OPTIONS: What actions could move us forward?
        4. RISKS: What could go wrong with each option?
        5. STRATEGY: What's the most productive next step?
        6. CONFIDENCE: How certain am I about this direction?
        
        Based on this analysis, what should I think about next?
        Provide clear, focused reasoning:
        """
    
    async def _decide_optimal_action(
        self, thought: str, context: str, trace: ReActTrace
    ) -> Dict[str, Any]:
        """Enhanced action decision with strategic thinking"""
        
        available_actions = list(self.tools.keys()) + [
            'search', 'calculate', 'reason', 'plan', 'final_answer'
        ]
        
        # Analyze recent action patterns to avoid loops
        recent_actions = [step.action.value for step in trace.steps[-3:]]
        
        decision_prompt = f"""
        THOUGHT: {thought}
        CONTEXT: {context}
        AVAILABLE ACTIONS: {available_actions}
        RECENT ACTIONS: {recent_actions}
        
        Choose the most strategic action based on:
        1. What would provide the most valuable information?
        2. What moves us closest to a solution?
        3. What avoids repeating ineffective patterns?
        4. What balances exploration vs. exploitation?
        
        Action selection guidelines:
        - Use 'search' for information gathering and research
        - Use 'calculate' for mathematical operations and computations
        - Use 'reason' for deeper analysis and logical deduction
        - Use 'plan' for breaking down complex problems
        - Use 'final_answer' only when confident in complete solution
        
        Return JSON: {{"action": "action_name", "input": "specific_detailed_input"}}
        """
        
        response = await self.llm.generate(decision_prompt)
        return self._parse_action_decision(response)
    
    async def _execute_action_with_fallback(self, action: ActionType, action_input: str) -> str:
        """Execute action with comprehensive fallback mechanisms"""
        
        try:
            if action == ActionType.SEARCH:
                return await self._execute_search_action(action_input)
            elif action == ActionType.CALCULATE:
                return await self._execute_calculation_action(action_input)
            elif action == ActionType.REASON:
                return await self._execute_reasoning_action(action_input)
            elif action == ActionType.PLAN:
                return await self._execute_planning_action(action_input)
            elif action == ActionType.FINAL_ANSWER:
                return f"Final answer provided: {action_input}"
            elif action == ActionType.TOOL_USE:
                return await self._execute_tool_action(action_input)
            else:
                return await self._execute_generic_action(action.value, action_input)
                
        except Exception as e:
            logger.warning(f"Action {action.value} failed: {str(e)}")
            return f"Action failed: {str(e)}. Consider alternative approach."
    
    async def _execute_search_action(self, query: str) -> str:
        """Execute search with mock implementation"""
        await asyncio.sleep(0.2)  # Simulate search time
        return f"Search results for '{query}': Found relevant information about the topic. Key insights include technical details, best practices, and current trends."
    
    async def _execute_calculation_action(self, expression: str) -> str:
        """Execute calculation with error handling"""
        try:
            # Simple expression evaluation (in production, use safer evaluation)
            if all(c in '0123456789+-*/.() ' for c in expression):
                result = eval(expression)
                return f"Calculation result: {expression} = {result}"
            else:
                return f"Invalid calculation expression: {expression}"
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    async def _execute_reasoning_action(self, focus: str) -> str:
        """Execute deep reasoning analysis"""
        reasoning_prompt = f"""
        Conduct deep reasoning analysis focused on: {focus}
        
        Provide systematic analysis covering:
        1. Key assumptions and their validity
        2. Logical connections and implications
        3. Potential counterarguments or alternatives
        4. Synthesis of insights
        
        Analysis:
        """
        
        return await self.llm.generate(reasoning_prompt, max_tokens=200)
    
    async def _execute_planning_action(self, objective: str) -> str:
        """Execute planning with breakdown"""
        planning_prompt = f"""
        Create a structured plan for: {objective}
        
        Break down into:
        1. Sub-objectives and dependencies
        2. Required resources and information
        3. Potential obstacles and mitigations
        4. Success criteria and milestones
        
        Plan:
        """
        
        return await self.llm.generate(planning_prompt, max_tokens=200)
    
    async def _trigger_meta_reasoning(self, trace: ReActTrace, step_num: int) -> Optional[ReActStep]:
        """Trigger meta-reasoning when confidence is low"""
        
        meta_analysis = await self.meta_reasoner.analyze_reasoning_quality(trace.steps)
        
        if meta_analysis['needs_intervention']:
            meta_thought = f"Meta-reasoning triggered: {meta_analysis['primary_issue']}"
            meta_observation = f"Recommendation: {meta_analysis['recommendation']}"
            
            return ReActStep(
                step_number=step_num,
                thought=meta_thought,
                action=ActionType.META_REASON,
                action_input="quality_improvement",
                observation=meta_observation,
                confidence=0.8,
                metadata={'meta_reasoning': True, 'intervention_type': meta_analysis['intervention_type']}
            )
        
        return None
    
    def _build_context_from_history(self, recent_steps: List[ReActStep]) -> str:
        """Build context string from recent reasoning history"""
        
        if not recent_steps:
            return "No previous steps completed."
        
        context_parts = []
        for step in recent_steps[-3:]:  # Use last 3 steps
            context_parts.append(
                f"Step {step.step_number}: Thought: {step.thought[:100]}... "
                f"Action: {step.action.value} -> {step.observation[:100]}..."
            )
        
        return "\n".join(context_parts)
    
    def _get_recent_history_summary(self, recent_steps: List[ReActStep]) -> str:
        """Get concise summary of recent history"""
        
        if not recent_steps:
            return "Starting analysis."
        
        actions_taken = [step.action.value for step in recent_steps]
        avg_confidence = sum(step.confidence for step in recent_steps) / len(recent_steps)
        
        return f"Recent actions: {', '.join(actions_taken)}. Average confidence: {avg_confidence:.2f}"
    
    def _parse_action_decision(self, response: str) -> Dict[str, Any]:
        """Parse action decision from LLM response"""
        
        try:
            # Try to parse as JSON first
            if '{' in response and '}' in response:
                json_part = response[response.find('{'):response.rfind('}')+1]
                return json.loads(json_part)
        except:
            pass
        
        # Fallback parsing
        if 'search' in response.lower():
            return {'action': 'search', 'input': 'general query'}
        elif 'calculate' in response.lower():
            return {'action': 'calculate', 'input': '1 + 1'}
        elif 'final' in response.lower():
            return {'action': 'final_answer', 'input': 'Unable to determine specific answer'}
        else:
            return {'action': 'reason', 'input': 'further analysis needed'}
    
    async def _calculate_enhanced_confidence(
        self, thought: str, action: ActionType, observation: str, trace: ReActTrace
    ) -> float:
        """Calculate multi-dimensional confidence score"""
        
        base_confidence = 0.7  # Base confidence
        
        # Adjust based on observation quality
        if 'error' in observation.lower() or 'failed' in observation.lower():
            base_confidence -= 0.3
        elif 'success' in observation.lower() or 'found' in observation.lower():
            base_confidence += 0.2
        
        # Adjust based on thought clarity
        if len(thought) > 50 and 'analyze' in thought.lower():
            base_confidence += 0.1
        elif len(thought) < 20:
            base_confidence -= 0.1
        
        # Adjust based on recent progress
        if trace.steps and len(trace.steps) > 0:
            recent_confidence = sum(step.confidence for step in trace.steps[-2:]) / min(2, len(trace.steps))
            base_confidence = 0.7 * base_confidence + 0.3 * recent_confidence
        
        return max(0.0, min(1.0, base_confidence))
    
    async def _assess_step_quality(self, thought: str, action: ActionType, observation: str) -> float:
        """Assess the quality of a reasoning step"""
        
        quality_score = 0.5  # Base quality
        
        # Thought quality
        if len(thought) > 30 and any(word in thought.lower() for word in ['because', 'therefore', 'analyze']):
            quality_score += 0.2
        
        # Action appropriateness
        if action in [ActionType.SEARCH, ActionType.CALCULATE, ActionType.REASON]:
            quality_score += 0.1
        
        # Observation usefulness
        if len(observation) > 20 and 'error' not in observation.lower():
            quality_score += 0.2
        
        return max(0.0, min(1.0, quality_score))
    
    async def _execute_tool_action(self, tool_input: str) -> str:
        """Execute tool action with available tools"""
        
        if not self.tools:
            return "No tools available for execution."
        
        # Mock tool execution
        return f"Tool executed with input: {tool_input}. Results: Mock tool output."
    
    async def _execute_generic_action(self, action_name: str, action_input: str) -> str:
        """Execute generic action with fallback"""
        
        return f"Executed {action_name} with input: {action_input}. Generic action completed."


class MetaReActAnalyzer:
    """Analyzes and improves ReAct reasoning quality through meta-reasoning"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.quality_patterns: Dict[str, List[str]] = {
            'good_patterns': ['systematic analysis', 'clear reasoning', 'appropriate actions'],
            'bad_patterns': ['circular reasoning', 'unclear thoughts', 'irrelevant actions']
        }
    
    async def analyze_reasoning_quality(self, reasoning_history: List[ReActStep]) -> Dict[str, Any]:
        """Comprehensive analysis of reasoning chain quality"""
        
        if len(reasoning_history) < 2:
            return {
                'quality_score': 0.5,
                'issues': ['Insufficient reasoning steps'],
                'recommendations': ['Continue with more detailed analysis'],
                'needs_intervention': False
            }
        
        # Run multiple analyses in parallel
        analyses = await asyncio.gather(
            self._detect_circular_reasoning(reasoning_history),
            self._assess_progress_quality(reasoning_history),
            self._evaluate_action_choices(reasoning_history),
            self._check_confidence_patterns(reasoning_history),
            return_exceptions=True
        )
        
        return self._synthesize_quality_assessment(analyses)
    
    async def _detect_circular_reasoning(self, history: List[ReActStep]) -> Dict[str, Any]:
        """Detect if agent is stuck in reasoning loops"""
        
        if len(history) < 4:
            return {'has_circular_reasoning': False}
        
        recent_steps = history[-5:]
        action_sequence = [step.action.value for step in recent_steps]
        
        # Check for repeated action patterns
        if len(set(action_sequence)) <= 2 and len(action_sequence) >= 4:
            return {
                'has_circular_reasoning': True,
                'pattern': action_sequence,
                'severity': 'high'
            }
        
        # Check for repeated similar thoughts
        thoughts = [step.thought.lower()[:50] for step in recent_steps]
        similar_count = 0
        for i in range(len(thoughts)):
            for j in range(i+1, len(thoughts)):
                if self._calculate_text_similarity(thoughts[i], thoughts[j]) > 0.8:
                    similar_count += 1
        
        if similar_count > 2:
            return {
                'has_circular_reasoning': True,
                'pattern': 'similar_thoughts',
                'severity': 'medium'
            }
        
        return {'has_circular_reasoning': False}
    
    async def _assess_progress_quality(self, history: List[ReActStep]) -> Dict[str, Any]:
        """Assess the quality of progress through reasoning steps"""
        
        if not history:
            return {'progress_quality': 0.0}
        
        # Calculate confidence trend
        confidences = [step.confidence for step in history]
        if len(confidences) > 1:
            confidence_trend = (confidences[-1] - confidences[0]) / len(confidences)
        else:
            confidence_trend = 0.0
        
        # Calculate action diversity
        actions = [step.action.value for step in history]
        action_diversity = len(set(actions)) / len(actions) if actions else 0.0
        
        # Calculate observation quality
        observation_quality = sum(
            1 for step in history if len(step.observation) > 20 and 'error' not in step.observation.lower()
        ) / len(history)
        
        overall_quality = (confidence_trend + action_diversity + observation_quality) / 3
        
        return {
            'progress_quality': max(0.0, min(1.0, overall_quality)),
            'confidence_trend': confidence_trend,
            'action_diversity': action_diversity,
            'observation_quality': observation_quality
        }
    
    async def _evaluate_action_choices(self, history: List[ReActStep]) -> Dict[str, Any]:
        """Evaluate appropriateness of action choices"""
        
        if not history:
            return {'action_quality': 0.5}
        
        appropriate_actions = 0
        for step in history:
            # Check if action matches thought content
            thought_lower = step.thought.lower()
            if step.action == ActionType.SEARCH and 'search' in thought_lower:
                appropriate_actions += 1
            elif step.action == ActionType.CALCULATE and ('calculate' in thought_lower or 'math' in thought_lower):
                appropriate_actions += 1
            elif step.action == ActionType.REASON and 'analyze' in thought_lower:
                appropriate_actions += 1
            elif step.action == ActionType.FINAL_ANSWER and 'answer' in thought_lower:
                appropriate_actions += 1
            else:
                # Generic appropriateness check
                if len(step.thought) > 10:
                    appropriate_actions += 0.5
        
        action_quality = appropriate_actions / len(history)
        
        return {'action_quality': min(1.0, action_quality)}
    
    async def _check_confidence_patterns(self, history: List[ReActStep]) -> Dict[str, Any]:
        """Check confidence patterns for anomalies"""
        
        if not history:
            return {'confidence_pattern': 'insufficient_data'}
        
        confidences = [step.confidence for step in history]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Check for confidence degradation
        if len(confidences) > 2:
            recent_avg = sum(confidences[-3:]) / min(3, len(confidences))
            early_avg = sum(confidences[:3]) / min(3, len(confidences))
            degradation = early_avg - recent_avg
        else:
            degradation = 0.0
        
        pattern_type = 'normal'
        if avg_confidence < 0.4:
            pattern_type = 'low_confidence'
        elif degradation > 0.3:
            pattern_type = 'degrading_confidence'
        elif avg_confidence > 0.8:
            pattern_type = 'high_confidence'
        
        return {
            'confidence_pattern': pattern_type,
            'average_confidence': avg_confidence,
            'confidence_degradation': degradation
        }
    
    def _synthesize_quality_assessment(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize overall quality assessment from component analyses"""
        
        # Handle any exceptions in analyses
        valid_analyses = [a for a in analyses if isinstance(a, dict)]
        
        if not valid_analyses:
            return {
                'quality_score': 0.3,
                'issues': ['Analysis failed'],
                'recommendations': ['Retry with simpler approach'],
                'needs_intervention': True
            }
        
        # Extract key metrics
        issues = []
        recommendations = []
        quality_factors = []
        
        for analysis in valid_analyses:
            if analysis.get('has_circular_reasoning'):
                issues.append('Circular reasoning detected')
                recommendations.append('Break out of reasoning loops')
            
            if 'progress_quality' in analysis:
                quality_factors.append(analysis['progress_quality'])
            
            if 'action_quality' in analysis:
                quality_factors.append(analysis['action_quality'])
            
            if analysis.get('confidence_pattern') == 'low_confidence':
                issues.append('Low confidence pattern')
                recommendations.append('Gather more information')
        
        # Calculate overall quality score
        if quality_factors:
            quality_score = sum(quality_factors) / len(quality_factors)
        else:
            quality_score = 0.5
        
        needs_intervention = quality_score < 0.4 or len(issues) > 2
        
        return {
            'quality_score': quality_score,
            'issues': issues or ['No significant issues detected'],
            'recommendations': recommendations or ['Continue current approach'],
            'needs_intervention': needs_intervention,
            'primary_issue': issues[0] if issues else None,
            'recommendation': recommendations[0] if recommendations else 'Continue analysis',
            'intervention_type': 'quality_improvement' if needs_intervention else None
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity score"""
        
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0


class AdaptationEngine:
    """Engine for learning and adapting from ReAct experiences"""
    
    def __init__(self):
        self.learning_history: List[Dict[str, Any]] = []
        self.adaptation_patterns: Dict[str, Any] = {}
    
    async def learn_from_trace(self, trace: ReActTrace):
        """Learn from a completed ReAct trace"""
        
        learning_record = {
            'trace_id': trace.trace_id,
            'success': trace.success,
            'duration': trace.total_duration.total_seconds(),
            'steps_count': len(trace.steps),
            'quality_score': trace.quality_assessment.get('quality_score', 0.5) if trace.quality_assessment else 0.5,
            'timestamp': datetime.now()
        }
        
        self.learning_history.append(learning_record)
        
        # Identify patterns for successful vs unsuccessful traces
        await self._identify_success_patterns()
        
        logger.info(f"Learned from trace {trace.trace_id}: Success={trace.success}, Quality={learning_record['quality_score']:.2f}")
    
    async def _identify_success_patterns(self):
        """Identify patterns that lead to successful reasoning"""
        
        if len(self.learning_history) < 5:
            return
        
        successful_traces = [r for r in self.learning_history if r['success']]
        failed_traces = [r for r in self.learning_history if not r['success']]
        
        if successful_traces and failed_traces:
            success_avg_duration = sum(r['duration'] for r in successful_traces) / len(successful_traces)
            failure_avg_duration = sum(r['duration'] for r in failed_traces) / len(failed_traces)
            
            self.adaptation_patterns['optimal_duration_range'] = (
                success_avg_duration * 0.8, success_avg_duration * 1.2
            )
            
            success_avg_steps = sum(r['steps_count'] for r in successful_traces) / len(successful_traces)
            self.adaptation_patterns['optimal_steps_range'] = (
                max(1, int(success_avg_steps * 0.7)), int(success_avg_steps * 1.3)
            )


# Demonstration and testing functions
async def demonstrate_react_agent():
    """Demonstrate the ReAct agent capabilities"""
    
    print("🤖 Advanced ReAct Agent Demonstration")
    print("=" * 50)
    
    # Initialize agent
    agent = AdvancedReActAgent(max_steps=8)
    
    # Test problems of varying complexity
    test_problems = [
        "How do I calculate the compound interest on $1000 invested at 5% annually for 3 years?",
        "What are the key considerations for implementing a multi-agent system in production?",
        "Explain the Byzantine Generals Problem and its relevance to distributed systems."
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print(f"\n🔍 Problem {i}: {problem}")
        print("-" * 40)
        
        # Solve with ReAct pattern
        trace = await agent.solve_with_react(problem)
        
        # Display results
        print(f"✅ Success: {trace.success}")
        print(f"⏱️  Duration: {trace.total_duration.total_seconds():.2f}s")
        print(f"🎯 Steps: {len(trace.steps)}")
        print(f"🏆 Quality: {trace.quality_assessment.get('quality_score', 0.0):.2f}")
        
        if trace.final_answer:
            print(f"💡 Answer: {trace.final_answer}")
        
        # Show reasoning trace summary
        print("\n📝 Reasoning Trace:")
        for step in trace.steps[:3]:  # Show first 3 steps
            print(f"  Step {step.step_number}: {step.action.value} (conf: {step.confidence:.2f})")
            print(f"    Thought: {step.thought[:80]}...")
            print(f"    Result: {step.observation[:80]}...")


if __name__ == "__main__":
    asyncio.run(demonstrate_react_agent())