"""
Agno Reasoning and Reflection Agents
Session 7: Agno Production-Ready Agents

This module implements advanced reasoning patterns including Chain of Thought,
Plan-and-Solve, reflection mechanisms, and self-correction capabilities.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field

try:
    from agno import Agent
    from agno.reasoning import ChainOfThought, PlanAndSolve, Reflection
    from agno.tools import DuckDuckGoTools, CalculatorTool, WebSearchTool
    from agno.patterns import ReasoningPattern
except ImportError:
    # Fallback implementations
    print("Warning: Agno reasoning modules not available, using mock implementations")
    
    class Agent:
        def __init__(self, name: str, model: str = "gpt-4o", **kwargs):
            self.name = name
            self.model = model
            self.config = kwargs
            
        async def run(self, prompt: str) -> 'AgentResponse':
            return AgentResponse(f"Reasoning agent {self.name} processed: {prompt}")
    
    class AgentResponse:
        def __init__(self, content: str):
            self.content = content
            self.processing_time = 1.2
            self.model = "gpt-4o"
            self.reasoning_steps = []
            self.confidence_score = 0.85
    
    class ChainOfThought:
        pass
    
    class PlanAndSolve:
        pass
    
    class Reflection:
        pass
    
    class ReasoningPattern:
        pass
    
    class DuckDuckGoTools:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReasoningType(Enum):
    """Types of reasoning patterns"""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    PLAN_AND_SOLVE = "plan_and_solve"
    REFLECTION = "reflection"
    SELF_CORRECTION = "self_correction"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"

@dataclass
class ReasoningStep:
    """Individual reasoning step in a chain"""
    step_number: int
    description: str
    reasoning: str
    conclusion: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ReasoningChain:
    """Complete reasoning chain with validation"""
    steps: List[ReasoningStep]
    overall_conclusion: str
    confidence_score: float
    reasoning_type: ReasoningType
    validation_result: Optional[Dict] = None
    reflection_notes: List[str] = field(default_factory=list)

class ChainOfThoughtAgent:
    """
    Advanced Chain of Thought reasoning agent
    
    Implements step-by-step reasoning with explicit thought processes,
    confidence tracking, and validation mechanisms.
    """
    
    def __init__(self, name: str = "cot_reasoning_agent"):
        """Initialize Chain of Thought reasoning agent"""
        self.name = name
        self.reasoning_history = []
        
        try:
            self.agent = Agent(
                name=self.name,
                model="gpt-4o",
                reasoning=[ChainOfThought()],
                tools=[DuckDuckGoTools(), CalculatorTool()],
                temperature=0.1,  # Low temperature for consistent reasoning
                instructions="""
                You are an expert reasoning agent that uses Chain of Thought methodology.
                
                For every problem, follow this systematic approach:
                1. Problem Understanding: Clearly state what needs to be solved
                2. Information Gathering: Identify what information is needed
                3. Step-by-Step Reasoning: Break down the solution into logical steps
                4. Evidence Collection: Gather supporting evidence for each step
                5. Conclusion Formation: Synthesize findings into a clear conclusion
                6. Confidence Assessment: Evaluate the reliability of your reasoning
                
                Always show your thinking process explicitly.
                Provide confidence scores (0.0-1.0) for each step.
                Question your assumptions and validate your logic.
                """
            )
            logger.info(f"Initialized Chain of Thought agent: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CoT agent: {e}")
            raise

    async def reason_through_problem(self, problem: str, context: Optional[Dict] = None) -> ReasoningChain:
        """
        Apply Chain of Thought reasoning to a complex problem
        
        Args:
            problem: The problem to solve
            context: Additional context or constraints
            
        Returns:
            Complete reasoning chain with steps and validation
        """
        start_time = datetime.utcnow()
        
        try:
            # Prepare structured reasoning prompt
            reasoning_prompt = f"""
            Problem to Analyze: {problem}
            
            Context: {json.dumps(context) if context else 'None provided'}
            
            Please solve this problem using explicit Chain of Thought reasoning:
            
            STEP 1 - PROBLEM UNDERSTANDING:
            - What exactly is being asked?
            - What are the key components of this problem?
            - What assumptions can I identify?
            
            STEP 2 - INFORMATION GATHERING:
            - What information do I already have?
            - What additional information do I need?
            - What tools or resources should I use?
            
            STEP 3 - STEP-BY-STEP REASONING:
            - Break the problem into smaller, manageable parts
            - Address each part systematically
            - Show your thinking process for each step
            
            STEP 4 - EVIDENCE COLLECTION:
            - What evidence supports each reasoning step?
            - Are there any contradictions or uncertainties?
            - How reliable is each piece of evidence?
            
            STEP 5 - CONCLUSION FORMATION:
            - What conclusion can I draw from my analysis?
            - How confident am I in this conclusion?
            - What are the limitations of my reasoning?
            
            STEP 6 - VALIDATION CHECK:
            - Does my conclusion make logical sense?
            - Have I addressed all aspects of the original problem?
            - What could I do to strengthen this analysis?
            
            Format each step clearly and provide confidence scores.
            """
            
            result = await self.agent.run(reasoning_prompt)
            
            # Parse reasoning steps from response
            reasoning_steps = self._parse_reasoning_steps(result.content)
            
            # Create reasoning chain
            reasoning_chain = ReasoningChain(
                steps=reasoning_steps,
                overall_conclusion=self._extract_conclusion(result.content),
                confidence_score=self._calculate_overall_confidence(reasoning_steps),
                reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
                validation_result=await self._validate_reasoning(reasoning_steps, problem)
            )
            
            # Store in history
            self.reasoning_history.append({
                "problem": problem,
                "context": context,
                "reasoning_chain": reasoning_chain,
                "timestamp": start_time,
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            })
            
            logger.info(f"Completed CoT reasoning for problem: {problem[:100]}...")
            return reasoning_chain
            
        except Exception as e:
            logger.error(f"Chain of Thought reasoning failed: {e}")
            raise
    
    def _parse_reasoning_steps(self, content: str) -> List[ReasoningStep]:
        """Parse reasoning steps from agent response"""
        steps = []
        step_sections = content.split("STEP ")
        
        for i, section in enumerate(step_sections[1:], 1):  # Skip first empty section
            lines = section.strip().split('\n')
            step_title = lines[0] if lines else f"Step {i}"
            step_content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            # Extract confidence from content (simple pattern matching)
            confidence = self._extract_confidence_from_text(step_content)
            
            # Extract key reasoning and conclusion
            reasoning_text = self._extract_reasoning_text(step_content)
            conclusion_text = self._extract_conclusion_text(step_content)
            
            step = ReasoningStep(
                step_number=i,
                description=step_title.strip(' -:'),
                reasoning=reasoning_text,
                conclusion=conclusion_text,
                confidence=confidence,
                evidence=self._extract_evidence(step_content)
            )
            steps.append(step)
        
        return steps[:6]  # Limit to 6 main steps
    
    def _extract_confidence_from_text(self, text: str) -> float:
        """Extract confidence score from text"""
        # Look for confidence indicators
        confidence_patterns = [
            r'confidence[:\s]*([0-9.]+)',
            r'confident[:\s]*([0-9.]+)',
            r'certainty[:\s]*([0-9.]+)',
        ]
        
        import re
        for pattern in confidence_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    confidence = float(match.group(1))
                    return min(1.0, max(0.0, confidence if confidence <= 1.0 else confidence / 100))
                except ValueError:
                    continue
        
        # Default confidence based on language used
        if any(word in text.lower() for word in ['certain', 'definitely', 'clearly']):
            return 0.9
        elif any(word in text.lower() for word in ['likely', 'probably', 'appears']):
            return 0.7
        elif any(word in text.lower() for word in ['possibly', 'might', 'uncertain']):
            return 0.5
        else:
            return 0.6  # Default confidence
    
    def _extract_reasoning_text(self, content: str) -> str:
        """Extract reasoning content from step"""
        lines = content.split('\n')
        reasoning_lines = []
        
        for line in lines:
            if line.strip() and not line.startswith('-') and not line.startswith('*'):
                reasoning_lines.append(line.strip())
        
        return ' '.join(reasoning_lines[:3])  # First 3 substantive lines
    
    def _extract_conclusion_text(self, content: str) -> str:
        """Extract conclusion from step content"""
        # Look for conclusion indicators
        conclusion_markers = ['conclusion:', 'therefore', 'thus', 'result:', 'finding:']
        lines = content.lower().split('\n')
        
        for line in lines:
            for marker in conclusion_markers:
                if marker in line:
                    return line.split(marker)[1].strip()
        
        # Return last substantial line as conclusion
        substantial_lines = [line.strip() for line in content.split('\n') if line.strip()]
        return substantial_lines[-1] if substantial_lines else "No clear conclusion identified"
    
    def _extract_evidence(self, content: str) -> List[str]:
        """Extract evidence points from content"""
        evidence = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                evidence.append(line[1:].strip())
        
        return evidence[:5]  # Limit to 5 evidence points
    
    def _extract_conclusion(self, content: str) -> str:
        """Extract overall conclusion from reasoning response"""
        # Look for conclusion section
        conclusion_markers = ['STEP 5', 'CONCLUSION', 'FINAL', 'OVERALL']
        content_lower = content.lower()
        
        for marker in conclusion_markers:
            if marker.lower() in content_lower:
                sections = content_lower.split(marker.lower())
                if len(sections) > 1:
                    conclusion_section = sections[1].split('STEP')[0]  # Take until next step
                    return conclusion_section.strip()[:500]  # Limit length
        
        # Fallback: return last paragraph
        paragraphs = content.strip().split('\n\n')
        return paragraphs[-1][:500] if paragraphs else "No conclusion identified"
    
    def _calculate_overall_confidence(self, steps: List[ReasoningStep]) -> float:
        """Calculate overall confidence from individual step confidences"""
        if not steps:
            return 0.0
        
        # Weighted average with higher weight for later steps
        total_weight = 0
        weighted_sum = 0
        
        for i, step in enumerate(steps):
            weight = i + 1  # Later steps have more weight
            weighted_sum += step.confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _validate_reasoning(self, steps: List[ReasoningStep], original_problem: str) -> Dict[str, Any]:
        """Validate the reasoning chain for logical consistency"""
        validation_result = {
            "logical_consistency": True,
            "completeness": True,
            "evidence_quality": "good",
            "issues": [],
            "strengths": []
        }
        
        # Check for logical gaps
        if len(steps) < 3:
            validation_result["completeness"] = False
            validation_result["issues"].append("Reasoning chain too short")
        
        # Check confidence consistency
        low_confidence_steps = [s for s in steps if s.confidence < 0.3]
        if len(low_confidence_steps) > len(steps) / 2:
            validation_result["logical_consistency"] = False
            validation_result["issues"].append("Too many low-confidence steps")
        
        # Check for evidence
        steps_with_evidence = [s for s in steps if s.evidence]
        if len(steps_with_evidence) < len(steps) / 2:
            validation_result["evidence_quality"] = "weak"
            validation_result["issues"].append("Insufficient evidence provided")
        
        # Identify strengths
        if len(steps) >= 5:
            validation_result["strengths"].append("Comprehensive step-by-step analysis")
        
        high_confidence_steps = [s for s in steps if s.confidence > 0.8]
        if len(high_confidence_steps) > len(steps) / 2:
            validation_result["strengths"].append("High confidence in reasoning")
        
        return validation_result

class PlanAndSolveAgent:
    """
    Plan-and-Solve reasoning agent
    
    Implements strategic planning followed by systematic execution,
    ideal for complex multi-step problems requiring coordination.
    """
    
    def __init__(self, name: str = "plan_solve_agent"):
        """Initialize Plan-and-Solve agent"""
        self.name = name
        self.active_plans = {}
        
        try:
            self.agent = Agent(
                name=self.name,
                model="gpt-4o",
                reasoning=[PlanAndSolve()],
                tools=[DuckDuckGoTools(), CalculatorTool(), WebSearchTool()],
                temperature=0.2,
                instructions="""
                You are a strategic planning and execution agent.
                
                Your approach to problem-solving:
                1. PLANNING PHASE:
                   - Analyze the problem comprehensively
                   - Identify all required sub-tasks
                   - Sequence tasks logically
                   - Estimate resources and time needed
                   - Identify potential risks and mitigation strategies
                
                2. EXECUTION PHASE:
                   - Execute each planned step systematically
                   - Monitor progress and adapt as needed
                   - Validate results at each step
                   - Adjust the plan based on new information
                
                Always show both your planning and execution thinking.
                """
            )
            logger.info(f"Initialized Plan-and-Solve agent: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Plan-and-Solve agent: {e}")
            raise

    async def plan_and_execute(self, problem: str, constraints: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a comprehensive plan and execute it step by step
        
        Args:
            problem: The complex problem to solve
            constraints: Resource, time, or other constraints
            
        Returns:
            Complete planning and execution results
        """
        start_time = datetime.utcnow()
        plan_id = f"plan_{int(start_time.timestamp())}"
        
        try:
            # Phase 1: Planning
            planning_prompt = f"""
            PROBLEM TO SOLVE: {problem}
            
            CONSTRAINTS: {json.dumps(constraints) if constraints else 'None specified'}
            
            PLANNING PHASE - Create a comprehensive plan:
            
            1. PROBLEM ANALYSIS:
               - What is the core problem?
               - What are the success criteria?
               - What are the key challenges?
            
            2. TASK BREAKDOWN:
               - List all required sub-tasks
               - Identify dependencies between tasks
               - Estimate effort/complexity for each task
            
            3. RESOURCE PLANNING:
               - What tools/information do I need?
               - What are the time requirements?
               - What could go wrong?
            
            4. EXECUTION SEQUENCE:
               - Optimal order for task execution
               - Checkpoints for validation
               - Contingency plans
            
            Create a detailed plan before proceeding to execution.
            """
            
            planning_result = await self.agent.run(planning_prompt)
            
            # Parse the plan
            execution_plan = self._parse_execution_plan(planning_result.content)
            
            # Store active plan
            self.active_plans[plan_id] = {
                "problem": problem,
                "constraints": constraints,
                "plan": execution_plan,
                "status": "planned",
                "created_at": start_time
            }
            
            # Phase 2: Execution
            execution_results = []
            
            for i, task in enumerate(execution_plan["tasks"]):
                task_result = await self._execute_planned_task(task, i + 1, len(execution_plan["tasks"]))
                execution_results.append(task_result)
                
                # Check if we should continue based on results
                if not task_result["success"] and task["critical"]:
                    logger.warning(f"Critical task failed: {task['description']}")
                    break
            
            # Update plan status
            self.active_plans[plan_id]["status"] = "completed"
            self.active_plans[plan_id]["execution_results"] = execution_results
            
            # Generate final summary
            summary = await self._generate_execution_summary(
                problem, execution_plan, execution_results
            )
            
            return {
                "plan_id": plan_id,
                "problem": problem,
                "constraints": constraints,
                "planning_phase": {
                    "plan": execution_plan,
                    "planning_time": (datetime.utcnow() - start_time).total_seconds()
                },
                "execution_phase": {
                    "results": execution_results,
                    "successful_tasks": len([r for r in execution_results if r["success"]]),
                    "total_tasks": len(execution_results)
                },
                "summary": summary,
                "total_time": (datetime.utcnow() - start_time).total_seconds(),
                "success": all(r["success"] for r in execution_results if r.get("critical", False))
            }
            
        except Exception as e:
            logger.error(f"Plan-and-solve execution failed: {e}")
            if plan_id in self.active_plans:
                self.active_plans[plan_id]["status"] = "failed"
                self.active_plans[plan_id]["error"] = str(e)
            raise

    def _parse_execution_plan(self, planning_content: str) -> Dict[str, Any]:
        """Parse execution plan from planning response"""
        # Simple parsing - in production, use more sophisticated NLP
        plan = {
            "tasks": [],
            "dependencies": [],
            "estimated_time": 0,
            "risk_factors": []
        }
        
        # Extract tasks (look for numbered lists or bullet points)
        lines = planning_content.split('\n')
        task_number = 1
        
        for line in lines:
            line = line.strip()
            if (line.startswith(f"{task_number}.") or 
                line.startswith(f"Task {task_number}") or
                line.startswith("- ") or
                line.startswith("* ")):
                
                task_description = line.split('.', 1)[1].strip() if '.' in line else line[2:].strip()
                
                plan["tasks"].append({
                    "id": task_number,
                    "description": task_description,
                    "status": "pending",
                    "critical": "critical" in task_description.lower(),
                    "estimated_time": 5  # Default 5 minutes
                })
                task_number += 1
        
        # If no tasks found, create generic ones
        if not plan["tasks"]:
            plan["tasks"] = [
                {"id": 1, "description": "Research and gather information", "status": "pending", "critical": True, "estimated_time": 10},
                {"id": 2, "description": "Analyze and process findings", "status": "pending", "critical": True, "estimated_time": 15},
                {"id": 3, "description": "Formulate solution and recommendations", "status": "pending", "critical": True, "estimated_time": 10}
            ]
        
        plan["estimated_time"] = sum(task["estimated_time"] for task in plan["tasks"])
        return plan

    async def _execute_planned_task(self, task: Dict, task_num: int, total_tasks: int) -> Dict[str, Any]:
        """Execute a single planned task"""
        start_time = datetime.utcnow()
        
        try:
            execution_prompt = f"""
            EXECUTING TASK {task_num} of {total_tasks}
            
            Task Description: {task['description']}
            Task Critical: {'Yes' if task['critical'] else 'No'}
            
            Execute this task systematically:
            1. Understand exactly what needs to be done
            2. Gather any required information
            3. Perform the task step by step
            4. Validate the results
            5. Report on completion status
            
            Provide clear results and next steps.
            """
            
            result = await self.agent.run(execution_prompt)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "task_id": task["id"],
                "description": task["description"],
                "result": result.content,
                "processing_time": processing_time,
                "success": True,
                "critical": task["critical"],
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Task execution failed: {e}")
            
            return {
                "task_id": task["id"],
                "description": task["description"],
                "error": str(e),
                "processing_time": processing_time,
                "success": False,
                "critical": task["critical"],
                "timestamp": start_time.isoformat()
            }

    async def _generate_execution_summary(self, problem: str, plan: Dict, results: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive execution summary"""
        successful_tasks = [r for r in results if r["success"]]
        failed_tasks = [r for r in results if not r["success"]]
        
        summary = {
            "problem": problem,
            "total_tasks": len(results),
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(failed_tasks),
            "success_rate": len(successful_tasks) / len(results) if results else 0,
            "total_time": sum(r["processing_time"] for r in results),
            "key_achievements": [],
            "issues_encountered": [],
            "recommendations": []
        }
        
        # Extract key achievements
        for result in successful_tasks:
            if result.get("critical"):
                summary["key_achievements"].append(f"Completed critical task: {result['description']}")
        
        # Extract issues
        for result in failed_tasks:
            summary["issues_encountered"].append(f"Failed: {result['description']} - {result.get('error', 'Unknown error')}")
        
        # Generate recommendations
        if failed_tasks:
            summary["recommendations"].append("Review and retry failed tasks")
        if summary["success_rate"] < 0.8:
            summary["recommendations"].append("Consider breaking down complex tasks further")
        
        return summary

class ReflectionAgent:
    """
    Reflection-based reasoning agent
    
    Implements self-reflection and iterative improvement patterns,
    capable of critiquing and improving its own reasoning.
    """
    
    def __init__(self, name: str = "reflection_agent"):
        """Initialize reflection agent"""
        self.name = name
        self.reflection_history = []
        
        try:
            self.agent = Agent(
                name=self.name,
                model="gpt-4o",
                reasoning=[Reflection()],
                tools=[DuckDuckGoTools()],
                temperature=0.3,
                instructions="""
                You are a reflective reasoning agent with self-improvement capabilities.
                
                Your process:
                1. INITIAL RESPONSE: Provide your first attempt at solving the problem
                2. CRITICAL REFLECTION: Analyze your response critically
                   - What are the strengths of your answer?
                   - What are potential weaknesses or gaps?
                   - What assumptions did you make?
                   - What could be improved?
                3. ITERATIVE IMPROVEMENT: Based on reflection, provide an improved response
                4. VALIDATION: Check your improved response against the original problem
                
                Always show your reflection process and improvements made.
                """
            )
            logger.info(f"Initialized Reflection agent: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Reflection agent: {e}")
            raise

    async def reflective_reasoning(self, problem: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Apply reflective reasoning with iterative improvement
        
        Args:
            problem: The problem to solve with reflection
            max_iterations: Maximum number of reflection iterations
            
        Returns:
            Complete reflection process with iterations
        """
        start_time = datetime.utcnow()
        iterations = []
        
        try:
            current_response = ""
            
            for iteration in range(max_iterations):
                iteration_start = datetime.utcnow()
                
                if iteration == 0:
                    # Initial response
                    prompt = f"""
                    PROBLEM: {problem}
                    
                    Provide your initial response to this problem.
                    Think carefully and provide your best answer.
                    """
                else:
                    # Reflective improvement
                    prompt = f"""
                    ORIGINAL PROBLEM: {problem}
                    
                    PREVIOUS RESPONSE (Iteration {iteration}):
                    {current_response}
                    
                    REFLECTION TASK:
                    1. Critically analyze your previous response
                    2. Identify strengths and weaknesses
                    3. Consider alternative approaches
                    4. Provide an improved response
                    
                    Focus on improving accuracy, completeness, and clarity.
                    """
                
                result = await self.agent.run(prompt)
                current_response = result.content
                
                # Extract reflection insights for this iteration
                reflection_insights = self._extract_reflection_insights(result.content, iteration)
                
                iteration_data = {
                    "iteration": iteration + 1,
                    "response": result.content,
                    "insights": reflection_insights,
                    "processing_time": (datetime.utcnow() - iteration_start).total_seconds(),
                    "timestamp": iteration_start.isoformat()
                }
                iterations.append(iteration_data)
                
                # Check if we should continue (simple stopping criteria)
                if iteration > 0 and self._should_stop_reflection(reflection_insights):
                    logger.info(f"Stopping reflection after {iteration + 1} iterations")
                    break
            
            # Generate final reflection summary
            final_summary = await self._generate_reflection_summary(problem, iterations)
            
            reflection_result = {
                "problem": problem,
                "iterations": iterations,
                "final_response": current_response,
                "reflection_summary": final_summary,
                "total_iterations": len(iterations),
                "total_time": (datetime.utcnow() - start_time).total_seconds(),
                "improvement_detected": len(iterations) > 1
            }
            
            self.reflection_history.append(reflection_result)
            return reflection_result
            
        except Exception as e:
            logger.error(f"Reflective reasoning failed: {e}")
            raise

    def _extract_reflection_insights(self, content: str, iteration: int) -> Dict[str, Any]:
        """Extract reflection insights from agent response"""
        insights = {
            "strengths": [],
            "weaknesses": [],
            "improvements": [],
            "confidence_change": 0.0,
            "key_realizations": []
        }
        
        content_lower = content.lower()
        
        # Look for reflection indicators
        reflection_markers = [
            ("strength", "strengths"),
            ("weakness", "weaknesses"),
            ("improve", "improvements"),
            ("better", "improvements"),
            ("realize", "key_realizations"),
            ("understand", "key_realizations")
        ]
        
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            if not line_lower:
                continue
                
            for marker, category in reflection_markers:
                if marker in line_lower:
                    insights[category].append(line.strip())
                    break
        
        # Estimate confidence change (simple heuristic)
        if iteration > 0:
            if any(word in content_lower for word in ['confident', 'certain', 'clear']):
                insights["confidence_change"] = 0.1
            elif any(word in content_lower for word in ['uncertain', 'unclear', 'doubt']):
                insights["confidence_change"] = -0.1
        
        return insights

    def _should_stop_reflection(self, insights: Dict[str, Any]) -> bool:
        """Determine if reflection should stop based on insights"""
        # Stop if no significant improvements identified
        if not insights["improvements"] and not insights["weaknesses"]:
            return True
        
        # Stop if confidence is decreasing
        if insights["confidence_change"] < -0.05:
            return True
        
        return False

    async def _generate_reflection_summary(self, problem: str, iterations: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive reflection summary"""
        if not iterations:
            return {"error": "No iterations to summarize"}
        
        summary = {
            "problem": problem,
            "total_iterations": len(iterations),
            "evolution": [],
            "key_improvements": [],
            "final_insights": {},
            "reflection_quality": "good"
        }
        
        # Track evolution across iterations
        for i, iteration in enumerate(iterations):
            evolution_step = {
                "iteration": i + 1,
                "improvements_made": len(iteration["insights"]["improvements"]),
                "weaknesses_identified": len(iteration["insights"]["weaknesses"]),
                "processing_time": iteration["processing_time"]
            }
            summary["evolution"].append(evolution_step)
        
        # Aggregate key improvements
        all_improvements = []
        for iteration in iterations:
            all_improvements.extend(iteration["insights"]["improvements"])
        
        # Remove duplicates and take top improvements
        unique_improvements = list(set(all_improvements))
        summary["key_improvements"] = unique_improvements[:5]
        
        # Final insights from last iteration
        if iterations:
            final_iteration = iterations[-1]
            summary["final_insights"] = final_iteration["insights"]
        
        # Assess reflection quality
        total_improvements = sum(len(it["insights"]["improvements"]) for it in iterations)
        if total_improvements >= 5:
            summary["reflection_quality"] = "excellent"
        elif total_improvements >= 3:
            summary["reflection_quality"] = "good"
        else:
            summary["reflection_quality"] = "basic"
        
        return summary

async def demonstrate_reasoning_agents():
    """Comprehensive demonstration of reasoning agents"""
    print("=" * 70)
    print("AGNO REASONING AGENTS DEMONSTRATION")
    print("=" * 70)
    
    # Chain of Thought Agent Demo
    print("\n1. Chain of Thought Agent - Step-by-Step Reasoning")
    print("-" * 55)
    
    cot_agent = ChainOfThoughtAgent("demo_cot_agent")
    
    complex_problem = """
    A startup company is deciding between three cloud providers for their AI platform.
    They need to consider cost, performance, security, and scalability.
    Provider A: $5000/month, excellent performance, good security, limited scaling
    Provider B: $7000/month, good performance, excellent security, auto-scaling  
    Provider C: $4000/month, fair performance, basic security, manual scaling
    What should they choose and why?
    """
    
    cot_result = await cot_agent.reason_through_problem(
        complex_problem, 
        {"budget": "$8000/month", "priority": "security_and_performance"}
    )
    
    print(f"Problem: {complex_problem[:100]}...")
    print(f"Reasoning Steps: {len(cot_result.steps)}")
    print(f"Overall Confidence: {cot_result.confidence_score:.2f}")
    print(f"Validation Issues: {len(cot_result.validation_result.get('issues', []))}")
    print(f"Conclusion: {cot_result.overall_conclusion[:200]}...")
    
    # Plan and Solve Agent Demo
    print("\n\n2. Plan-and-Solve Agent - Strategic Planning")
    print("-" * 50)
    
    plan_solve_agent = PlanAndSolveAgent("demo_planner")
    
    planning_problem = """
    Design and implement a customer support chatbot for an e-commerce platform.
    The chatbot should handle order inquiries, return requests, and basic troubleshooting.
    Timeline: 3 months, Budget: $150K, Team: 4 developers
    """
    
    constraints = {
        "timeline": "3 months",
        "budget": "$150,000",
        "team_size": 4,
        "must_integrate_with": ["existing_CRM", "order_system", "payment_gateway"]
    }
    
    plan_result = await plan_solve_agent.plan_and_execute(planning_problem, constraints)
    
    print(f"Problem: {planning_problem[:100]}...")
    print(f"Total Tasks Planned: {len(plan_result['planning_phase']['plan']['tasks'])}")
    print(f"Successful Tasks: {plan_result['execution_phase']['successful_tasks']}")
    print(f"Success Rate: {plan_result['execution_phase']['successful_tasks']/plan_result['execution_phase']['total_tasks']*100:.1f}%")
    print(f"Total Time: {plan_result['total_time']:.1f} seconds")
    print(f"Overall Success: {plan_result['success']}")
    
    # Reflection Agent Demo
    print("\n\n3. Reflection Agent - Iterative Improvement")
    print("-" * 50)
    
    reflection_agent = ReflectionAgent("demo_reflector")
    
    reflection_problem = """
    Analyze the ethical implications of using AI agents in hiring processes.
    Consider bias, fairness, transparency, and legal compliance.
    """
    
    reflection_result = await reflection_agent.reflective_reasoning(
        reflection_problem, 
        max_iterations=3
    )
    
    print(f"Problem: {reflection_problem[:100]}...")
    print(f"Total Iterations: {reflection_result['total_iterations']}")
    print(f"Improvement Detected: {reflection_result['improvement_detected']}")
    print(f"Reflection Quality: {reflection_result['reflection_summary']['reflection_quality']}")
    print(f"Key Improvements: {len(reflection_result['reflection_summary']['key_improvements'])}")
    print(f"Total Processing Time: {reflection_result['total_time']:.1f} seconds")
    
    # Show evolution across iterations
    print("\nReflection Evolution:")
    for step in reflection_result['reflection_summary']['evolution']:
        print(f"  Iteration {step['iteration']}: {step['improvements_made']} improvements, "
              f"{step['weaknesses_identified']} weaknesses identified")
    
    print("\n" + "=" * 70)
    print("REASONING DEMONSTRATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    # Run comprehensive demonstration
    asyncio.run(demonstrate_reasoning_agents())