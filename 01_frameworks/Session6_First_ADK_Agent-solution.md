# Session 6: Building Your First ADK Agent - Solution Guide

## 🧪 Multiple Choice Quiz - Answer Key

### Quick Check Questions

1. **What is the primary role of the ConversationMemory class?**
   - A) Store user preferences
   - B) Maintain conversation context and history ✅ **CORRECT**
   - C) Handle tool integration
   - D) Manage cloud deployment

   **Explanation:** ConversationMemory maintains the context and history of conversations, allowing agents to provide contextually relevant responses across multiple interaction turns.

2. **How does the ADK agent determine when to use MCP tools?**
   - A) Random selection
   - B) User explicitly requests tools
   - C) Response analysis and pattern matching ✅ **CORRECT**  
   - D) Fixed rule-based system

   **Explanation:** The agent analyzes user messages for patterns and keywords to intelligently determine when specific MCP tools should be invoked, using confidence-based selection.

3. **What advantage does async processing provide in agent implementations?**
   - A) Simpler code structure
   - B) Better error handling
   - C) Non-blocking operations and improved performance ✅ **CORRECT**
   - D) Easier debugging

   **Explanation:** Async processing allows agents to handle multiple concurrent requests efficiently without blocking, significantly improving overall performance and responsiveness.

4. **How does the agent maintain context across conversation turns?**
   - A) Static variables
   - B) ConversationMemory with turn tracking ✅ **CORRECT**
   - C) External database
   - D) Cloud storage

   **Explanation:** The ConversationMemory system tracks individual conversation turns with timestamps, roles, and metadata, maintaining context across the entire conversation session.

5. **What is the purpose of the system prompt in agent responses?**
   - A) User identification
   - B) Provide context about available tools and agent capabilities ✅ **CORRECT**
   - C) Error handling
   - D) Performance optimization

   **Explanation:** The system prompt informs the Gemini model about the agent's capabilities, available tools, and operational context, enabling more accurate and helpful responses.

---

## 💡 Practical Exercise Solution

**Challenge:** Extend the agent with a planning capability.

### Complete Solution:

The planning agent demonstrates advanced ADK capabilities. Let's build it systematically:

**Step 1: Set up the planning agent foundation**

```python
# agents/planning_agent.py
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from agents.base_agent import BaseADKAgent

class PlanningAgent(BaseADKAgent):
    """Agent that can create and manage complex plans and workflows."""
    
    def __init__(self):
        system_instruction = """You are an intelligent planning assistant agent.

Your capabilities include:
- Breaking down complex goals into actionable steps
- Identifying dependencies and prerequisites
- Estimating timelines and resource requirements
- Creating contingency plans and risk assessments
- Monitoring plan progress and suggesting adjustments

You have access to various tools through MCP servers for data analysis, 
scheduling, and resource management. Always create detailed, realistic plans 
that consider constraints and provide clear success criteria.

Provide responses that are:
- Structured and actionable
- Time-bound with realistic estimates
- Considerate of dependencies and risks
- Adaptable to changing circumstances
"""

        capabilities = [
            "goal_decomposition",
            "timeline_estimation", 
            "dependency_analysis",
            "resource_planning",
            "risk_assessment",
            "progress_monitoring",
            "plan_optimization"
        ]
```

**Step 2: Initialize the planning agent with capabilities**

```python        
        super().__init__(
            agent_name="PlanningAgent",
            system_instruction=system_instruction,
            capabilities=capabilities
        )
        
        # Planning-specific state
        self.active_plans: Dict[str, Dict] = {}
        self.plan_templates: Dict[str, Dict] = self._load_plan_templates()
```

The agent inherits from BaseADKAgent and adds planning-specific functionality including active plan tracking and reusable plan templates.

**Step 3: Implement goal analysis and plan creation**

```python
    async def create_plan(self, goal: str, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a detailed plan to achieve a goal.
        
        Args:
            goal: The goal to achieve
            constraints: Any constraints or limitations
            
        Returns:
            Detailed plan with steps, timeline, and resources
        """
        constraints = constraints or {}
        
        try:
            # Generate plan ID
            plan_id = f"plan_{int(datetime.now().timestamp())}"
            
            # Analyze the goal and break it down
            goal_analysis = await self._analyze_goal(goal, constraints)
```

The create_plan method coordinates the entire planning process by calling specialized analysis methods in sequence.

**Step 4: Build the comprehensive plan structure**

```python
            # Create step breakdown
            steps = await self._create_step_breakdown(goal_analysis)
            
            # Estimate timeline and dependencies
            timeline = await self._estimate_timeline(steps, constraints)
            
            # Identify required resources
            resources = await self._identify_resources(steps, constraints)
            
            # Assess risks and create contingencies
            risk_assessment = await self._assess_risks(steps, constraints)
```

Each method specializes in one aspect of planning: steps, timeline, resources, and risks.

**Step 5: Assemble and store the final plan**

```python
            # Create the complete plan
            plan = {
                "plan_id": plan_id,
                "goal": goal,
                "created_at": datetime.now().isoformat(),
                "status": "draft",
                "constraints": constraints,
                "analysis": goal_analysis,
                "steps": steps,
                "timeline": timeline,
                "resources": resources,
                "risks": risk_assessment,
                "success_criteria": await self._define_success_criteria(goal, steps),
                "milestones": await self._create_milestones(steps, timeline)
            }
            
            # Store the plan
            self.active_plans[plan_id] = plan
            
            # Add plan creation to memory
            await self.memory.add_message(
                session_id="planning",
                role="assistant", 
                content=f"Created comprehensive plan '{plan_id}' for goal: {goal}"
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return {
                "error": f"Failed to create plan: {str(e)}",
                "goal": goal,
                "timestamp": datetime.now().isoformat()
            }
```

This method completes the plan creation and error handling. The plan is stored in memory and tracked for future reference.

**Step 6: Implement goal analysis with Gemini**

```python
    async def _analyze_goal(self, goal: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the goal to understand scope and requirements."""
        
        # Use Gemini to analyze the goal
        analysis_prompt = f"""
        Analyze this goal for planning purposes:
        Goal: {goal}
        Constraints: {json.dumps(constraints, indent=2)}
        
        Provide analysis including:
        1. Goal category and complexity level
        2. Key success factors
        3. Potential challenges
        4. Required expertise areas
        5. Estimated effort level (1-10)
        """
        
        # Create a temporary chat session for analysis
        chat_session = self.model.start_chat()
        response = chat_session.send_message(analysis_prompt)
```

This method leverages Gemini to intelligently analyze the goal and extract key planning insights.

**Step 7: Parse analysis results and structure data**

```python        
        # Parse the analysis (simplified - in production use structured parsing)
        analysis = {
            "goal_category": self._extract_category(response.text),
            "complexity_level": self._extract_complexity(response.text),
            "key_factors": self._extract_key_factors(response.text),
            "challenges": self._extract_challenges(response.text),
            "expertise_areas": self._extract_expertise_areas(response.text),
            "effort_estimate": self._extract_effort_estimate(response.text),
            "full_analysis": response.text
        }
        
        return analysis
    
```

The analysis results are parsed into structured data that drives the planning process.

**Step 8: Create step breakdown using templates**

```python
    async def _create_step_breakdown(self, goal_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break down the goal into actionable steps."""
        
        complexity = goal_analysis.get("complexity_level", 5)
        category = goal_analysis.get("goal_category", "general")
        
        # Use appropriate template based on category
        if category in self.plan_templates:
            template_steps = self.plan_templates[category]["steps"]
        else:
            template_steps = self.plan_templates["general"]["steps"]
```

This method selects the appropriate planning template based on the goal category (software development, research, or general).

**Step 9: Generate detailed step objects**

```python        
        steps = []
        for i, template_step in enumerate(template_steps):
            step = {
                "step_id": f"step_{i+1:02d}",
                "title": template_step["title"],
                "description": template_step["description"],
                "type": template_step.get("type", "action"),
                "estimated_duration": self._adjust_duration_by_complexity(
                    template_step["duration"], complexity
                ),
                "prerequisites": template_step.get("prerequisites", []),
                "deliverables": template_step.get("deliverables", []),
                "success_criteria": template_step.get("success_criteria", []),
                "status": "not_started"
            }
            steps.append(step)
        
        return steps
    
```

Each step gets enriched with detailed metadata including duration estimates adjusted for complexity.

**Step 10: Estimate timeline and dependencies**

```python
    async def _estimate_timeline(self, steps: List[Dict], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate timeline for plan execution."""
        
        total_duration = 0
        critical_path = []
        
        # Calculate total duration considering dependencies
        for step in steps:
            duration = step["estimated_duration"]
            total_duration += duration
            
            # Identify critical path steps
            if step.get("prerequisites"):
                critical_path.append(step["step_id"])
```

This method calculates the total time needed and identifies critical path steps that have dependencies.

**Step 11: Apply constraints and validate timeline**

```python        
        # Apply constraint adjustments
        deadline_constraint = constraints.get("deadline")
        resource_constraint = constraints.get("available_hours_per_day", 8)
        
        # Calculate working days needed
        working_days = total_duration / resource_constraint
        
        timeline = {
            "total_estimated_hours": total_duration,
            "estimated_working_days": working_days,
            "critical_path": critical_path,
            "start_date": constraints.get("start_date", datetime.now().isoformat()),
            "estimated_completion": (datetime.now() + timedelta(days=working_days)).isoformat(),
            "buffer_time": total_duration * 0.2,  # 20% buffer
            "timeline_feasible": True
        }
        
        # Check if timeline meets deadline constraint
        if deadline_constraint:
            deadline = datetime.fromisoformat(deadline_constraint)
            estimated_completion = datetime.fromisoformat(timeline["estimated_completion"])
            
            if estimated_completion > deadline:
                timeline["timeline_feasible"] = False
                timeline["deadline_gap_days"] = (estimated_completion - deadline).days
        
        return timeline
    
```

The timeline method validates constraints and determines if the plan is feasible within the given deadline.

**Step 12: Identify required resources**

```python
    async def _identify_resources(self, steps: List[Dict], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Identify required resources for plan execution."""
        
        resources = {
            "human_resources": {
                "estimated_person_hours": 0,
                "required_skills": set(),
                "team_size_recommendation": 1
            },
            "technical_resources": {
                "tools_needed": set(),
                "systems_access": set(),
                "infrastructure": []
            },
            "financial_resources": {
                "estimated_budget": 0,
                "cost_breakdown": {}
            },
            "external_dependencies": []
        }
```

This method structures resource requirements into categories: human, technical, financial, and external dependencies.

**Step 13: Aggregate resource requirements from steps**

```python        
        for step in steps:
            # Accumulate person hours
            resources["human_resources"]["estimated_person_hours"] += step["estimated_duration"]
            
            # Extract required skills from step description
            skills = self._extract_skills_from_step(step)
            resources["human_resources"]["required_skills"].update(skills)
            
            # Identify tools needed
            tools = self._extract_tools_from_step(step)
            resources["technical_resources"]["tools_needed"].update(tools)
        
        # Convert sets to lists for JSON serialization
        resources["human_resources"]["required_skills"] = list(resources["human_resources"]["required_skills"])
        resources["technical_resources"]["tools_needed"] = list(resources["technical_resources"]["tools_needed"])
        
        return resources
    
```

The resource identification method iterates through all steps to aggregate skills, tools, and time requirements.

**Step 14: Assess risks and create mitigation strategies**

```python
    async def _assess_risks(self, steps: List[Dict], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks and create mitigation strategies."""
        
        risks = {
            "high_risk": [],
            "medium_risk": [],
            "low_risk": [],
            "mitigation_strategies": {},
            "contingency_plans": {}
        }
        
        # Common risk patterns
        risk_patterns = [
            {
                "name": "Timeline Overrun",
                "probability": "medium",
                "impact": "high",
                "indicators": ["complex_steps", "external_dependencies"],
                "mitigation": "Add buffer time and create parallel execution paths"
            },
            {
                "name": "Resource Unavailability", 
                "probability": "medium",
                "impact": "medium",
                "indicators": ["specialized_skills", "external_tools"],
                "mitigation": "Identify backup resources and cross-train team members"
            },
            {
                "name": "Scope Creep",
                "probability": "high",
                "impact": "medium", 
                "indicators": ["unclear_requirements", "stakeholder_involvement"],
                "mitigation": "Define clear scope boundaries and change control process"
            }
        ]
```

This method defines common project risk patterns with probability, impact, and mitigation strategies.

**Step 15: Evaluate and categorize risks**

```python        
        # Assess each risk pattern
        for risk_pattern in risk_patterns:
            risk_score = self._calculate_risk_score(risk_pattern, steps, constraints)
            
            risk_entry = {
                "name": risk_pattern["name"],
                "probability": risk_pattern["probability"],
                "impact": risk_pattern["impact"],
                "score": risk_score,
                "mitigation": risk_pattern["mitigation"]
            }
            
            # Categorize by risk level
            if risk_score >= 7:
                risks["high_risk"].append(risk_entry)
            elif risk_score >= 4:
                risks["medium_risk"].append(risk_entry)
            else:
                risks["low_risk"].append(risk_entry)
        
        return risks
    
    def _load_plan_templates(self) -> Dict[str, Dict]:
        """Load plan templates for different goal categories."""
        
        return {
            "software_development": {
                "steps": [
                    {
                        "title": "Requirements Analysis",
                        "description": "Gather and analyze requirements",
                        "duration": 8,
                        "type": "analysis"
                    },
                    {
                        "title": "System Design", 
                        "description": "Create system architecture and design",
                        "duration": 16,
                        "type": "design",
                        "prerequisites": ["step_01"]
                    },
                    {
                        "title": "Implementation",
                        "description": "Code development and unit testing",
                        "duration": 40,
                        "type": "development",
                        "prerequisites": ["step_02"]
                    },
                    {
                        "title": "Testing & QA",
                        "description": "Integration and system testing",
                        "duration": 16,
                        "type": "testing",
                        "prerequisites": ["step_03"]
                    },
                    {
                        "title": "Deployment",
                        "description": "Production deployment and monitoring",
                        "duration": 8,
                        "type": "deployment",
                        "prerequisites": ["step_04"]
                    }
                ]
            },
            "research": {
                "steps": [
                    {
                        "title": "Literature Review",
                        "description": "Review existing research and publications",
                        "duration": 20,
                        "type": "research"
                    },
                    {
                        "title": "Methodology Design",
                        "description": "Design research methodology and approach",
                        "duration": 12,
                        "type": "planning",
                        "prerequisites": ["step_01"]
                    },
                    {
                        "title": "Data Collection",
                        "description": "Collect and organize research data",
                        "duration": 30,
                        "type": "data_collection",
                        "prerequisites": ["step_02"]
                    },
                    {
                        "title": "Analysis",
                        "description": "Analyze data and generate insights",
                        "duration": 25,
                        "type": "analysis",
                        "prerequisites": ["step_03"]
                    },
                    {
                        "title": "Documentation",
                        "description": "Document findings and conclusions",
                        "duration": 15,
                        "type": "documentation",
                        "prerequisites": ["step_04"]
                    }
                ]
            },
            "general": {
                "steps": [
                    {
                        "title": "Planning & Preparation",
                        "description": "Plan approach and gather resources",
                        "duration": 4,
                        "type": "planning"
                    },
                    {
                        "title": "Execution Phase 1",
                        "description": "Begin primary work activities",
                        "duration": 12,
                        "type": "execution",
                        "prerequisites": ["step_01"]
                    },
                    {
                        "title": "Review & Adjustment",
                        "description": "Review progress and make adjustments",
                        "duration": 2,
                        "type": "review",
                        "prerequisites": ["step_02"]
                    },
                    {
                        "title": "Execution Phase 2",
                        "description": "Continue with refined approach",
                        "duration": 12,
                        "type": "execution",
                        "prerequisites": ["step_03"]
                    },
                    {
                        "title": "Completion & Validation",
                        "description": "Finalize work and validate results",
                        "duration": 4,
                        "type": "completion",
                        "prerequisites": ["step_04"]
                    }
                ]
            }
        }
    
    def _extract_category(self, analysis_text: str) -> str:
        """Extract goal category from analysis text."""
        text_lower = analysis_text.lower()
        
        if any(word in text_lower for word in ["software", "code", "development", "programming"]):
            return "software_development"
        elif any(word in text_lower for word in ["research", "study", "analysis", "investigation"]):
            return "research"
        else:
            return "general"
    
    def _extract_complexity(self, analysis_text: str) -> int:
        """Extract complexity level from analysis text."""
        # Simple heuristic based on text indicators
        text_lower = analysis_text.lower()
        
        complexity_indicators = {
            "simple": 2,
            "easy": 2, 
            "straightforward": 3,
            "moderate": 5,
            "complex": 7,
            "difficult": 8,
            "challenging": 8,
            "very complex": 9,
            "extremely complex": 10
        }
        
        for indicator, level in complexity_indicators.items():
            if indicator in text_lower:
                return level
        
        return 5  # Default moderate complexity
    
    # Additional helper methods...
    def _extract_key_factors(self, text: str) -> List[str]:
        return ["factor_1", "factor_2"]  # Simplified implementation
    
    def _extract_challenges(self, text: str) -> List[str]:
        return ["challenge_1", "challenge_2"]  # Simplified implementation
    
    def _extract_expertise_areas(self, text: str) -> List[str]:
        return ["area_1", "area_2"]  # Simplified implementation
    
    def _extract_effort_estimate(self, text: str) -> int:
        return 5  # Simplified implementation
    
    def _adjust_duration_by_complexity(self, base_duration: int, complexity: int) -> int:
        multiplier = 0.5 + (complexity / 10.0)
        return int(base_duration * multiplier)
    
    def _extract_skills_from_step(self, step: Dict) -> set:
        return {"general_skills"}  # Simplified implementation
    
    def _extract_tools_from_step(self, step: Dict) -> set:
        return {"general_tools"}  # Simplified implementation
    
    def _calculate_risk_score(self, risk_pattern: Dict, steps: List, constraints: Dict) -> int:
        return 5  # Simplified implementation
    
    async def _define_success_criteria(self, goal: str, steps: List) -> List[str]:
        return [f"Goal '{goal}' achieved successfully", "All steps completed", "Quality criteria met"]
    
    async def _create_milestones(self, steps: List, timeline: Dict) -> List[Dict]:
        milestones = []
        step_count = len(steps)
        
        # Create milestone at 25%, 50%, 75%, and 100% completion
        milestone_points = [0.25, 0.5, 0.75, 1.0]
        
        for i, point in enumerate(milestone_points):
            step_index = min(int(step_count * point) - 1, step_count - 1)
            
            milestone = {
                "milestone_id": f"milestone_{i+1}",
                "name": f"{int(point*100)}% Completion",
                "description": f"Milestone reached at {int(point*100)}% of plan completion",
                "target_step": steps[step_index]["step_id"] if step_index >= 0 else steps[0]["step_id"],
                "success_criteria": [f"Steps 1-{step_index+1} completed successfully"]
            }
            milestones.append(milestone)
        
        return milestones

# Example usage
async def demo_planning_agent():
    """Demonstrate the planning agent capabilities."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    
    console = Console()
    
    # Create planning agent
    planner = PlanningAgent()
    await planner.initialize()
    
    console.print(Panel.fit(
        "🎯 Planning Agent Demo\nCreating comprehensive project plans",
        title="Advanced Planning System",
        border_style="blue"
    ))
    
    # Create a sample plan
    goal = "Build a weather monitoring web application with real-time data visualization"
    constraints = {
        "deadline": "2024-03-15T00:00:00",
        "available_hours_per_day": 6,
        "budget": 5000,
        "team_size": 2
    }
    
    console.print(f"🎯 Goal: {goal}")
    console.print(f"📋 Constraints: {json.dumps(constraints, indent=2)}")
    
    # Generate the plan
    plan = await planner.create_plan(goal, constraints)
    
    if "error" not in plan:
        # Display plan summary
        console.print(f"\n✅ Plan created successfully: {plan['plan_id']}")
        
        # Show timeline
        timeline = plan['timeline']
        console.print(f"⏱️  Estimated duration: {timeline['estimated_working_days']:.1f} working days")
        console.print(f"📅 Target completion: {timeline['estimated_completion'][:10]}")
        
        # Show steps in a table
        steps_table = Table(title="Plan Steps")
        steps_table.add_column("Step", style="cyan")
        steps_table.add_column("Title", style="yellow")
        steps_table.add_column("Duration (hrs)", style="green")
        steps_table.add_column("Type", style="blue")
        
        for step in plan['steps']:
            steps_table.add_row(
                step['step_id'],
                step['title'],
                str(step['estimated_duration']),
                step['type']
            )
        
        console.print(steps_table)
        
        # Show risk assessment
        risks = plan['risks']
        if risks['high_risk']:
            console.print("\n🚨 High Risk Items:")
            for risk in risks['high_risk']:
                console.print(f"  • {risk['name']}: {risk['mitigation']}")
    
    else:
        console.print(f"❌ Plan creation failed: {plan['error']}")

if __name__ == "__main__":
    asyncio.run(demo_planning_agent())
```


### Advanced Planning Features:

1. **Goal Analysis**: Uses Gemini to analyze goals and determine complexity
2. **Template-Based Planning**: Different templates for different types of projects
3. **Dependency Management**: Tracks prerequisites between steps
4. **Resource Planning**: Identifies human, technical, and financial resources
5. **Risk Assessment**: Evaluates potential risks and creates mitigation strategies
6. **Timeline Estimation**: Calculates realistic timelines with buffer time
7. **Milestone Tracking**: Creates checkpoints for progress monitoring

### Testing Scenarios:

1. **Software Development Project**: Creates development lifecycle plan
2. **Research Project**: Generates research methodology and timeline
3. **General Goal**: Handles any type of goal with generic template
4. **Constraint Handling**: Adapts plans based on time, budget, and resource constraints
5. **Risk Mitigation**: Identifies and plans for potential obstacles

This comprehensive planning system transforms the basic ADK agent into a sophisticated project management assistant capable of handling complex multi-step goals with realistic constraints and risk assessment.