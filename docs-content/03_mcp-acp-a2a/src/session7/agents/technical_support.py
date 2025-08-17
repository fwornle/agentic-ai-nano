"""
Technical Support Agent Implementation

This module implements a technical support agent specialized in diagnosing
and resolving technical issues. It can analyze problems, provide solutions,
and coordinate with other agents for complex technical scenarios.
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..a2a.protocol import (
    A2AMessage, AgentProfile, AgentCapability, 
    create_request_message, create_response_message,
    Priority, MessageType
)
from ..a2a.agent_registry import AgentRegistry, AgentRegistryClient
from ..a2a.message_router import MessageRouter

logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Technical issue severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueCategory(Enum):
    """Technical issue categories."""
    AUTHENTICATION = "authentication"
    API = "api"
    NETWORK = "network"
    DATABASE = "database"
    PERFORMANCE = "performance"
    SECURITY = "security"
    INTEGRATION = "integration"
    UI_UX = "ui_ux"
    MOBILE = "mobile"
    OTHER = "other"


@dataclass
class TechnicalIssue:
    """Represents a technical issue or ticket."""
    issue_id: str
    customer_id: str
    title: str
    description: str
    category: IssueCategory = IssueCategory.OTHER
    severity: IssueSeverity = IssueSeverity.MEDIUM
    status: str = "open"
    assigned_agent: str = None
    created_at: str = None
    updated_at: str = None
    resolution_steps: List[str] = None
    resolution: str = None
    system_info: Dict[str, Any] = None
    error_logs: str = None
    reproduction_steps: List[str] = None
    workaround: str = None
    estimated_time: float = 0.0  # hours
    actual_time: float = 0.0     # hours
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.resolution_steps is None:
            self.resolution_steps = []
        if self.reproduction_steps is None:
            self.reproduction_steps = []
        if self.system_info is None:
            self.system_info = {}
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "customer_id": self.customer_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value if isinstance(self.category, IssueCategory) else self.category,
            "severity": self.severity.value if isinstance(self.severity, IssueSeverity) else self.severity,
            "status": self.status,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolution_steps": self.resolution_steps,
            "resolution": self.resolution,
            "system_info": self.system_info,
            "error_logs": self.error_logs,
            "reproduction_steps": self.reproduction_steps,
            "workaround": self.workaround,
            "estimated_time": self.estimated_time,
            "actual_time": self.actual_time,
            "metadata": self.metadata
        }


class TechnicalSupportAgent:
    """Technical support agent with advanced diagnostic capabilities."""
    
    def __init__(self, agent_id: str, name: str = None, endpoint: str = None, 
                 specializations: List[str] = None):
        self.agent_id = agent_id
        self.name = name or f"Technical Support Agent {agent_id}"
        self.endpoint = endpoint or f"http://localhost:8000/agents/{agent_id}"
        self.specializations = specializations or ["general_technical"]
        
        # Agent state
        self.issues: Dict[str, TechnicalIssue] = {}
        self.knowledge_base: Dict[str, Dict] = {}
        self.diagnostic_patterns: Dict[str, List[str]] = {}
        self.is_running = False
        
        # Performance metrics
        self.metrics = {
            "issues_handled": 0,
            "issues_resolved": 0,
            "issues_escalated": 0,
            "average_resolution_time": 0.0,
            "accuracy_score": 0.0,
            "specialization_usage": {},
            "last_updated": datetime.now().isoformat()
        }
        
        # A2A components (will be injected)
        self.registry: Optional[AgentRegistry] = None
        self.registry_client: Optional[AgentRegistryClient] = None
        self.router: Optional[MessageRouter] = None
        
        # Initialize capabilities and knowledge
        self._setup_capabilities()
        self._setup_knowledge_base()
        self._setup_diagnostic_patterns()
    
    def _setup_capabilities(self):
        """Setup agent capabilities."""
        capabilities = [
            AgentCapability(
                name="technical_support",
                description="Diagnose and resolve technical issues",
                input_schema={
                    "type": "object",
                    "properties": {
                        "issue_description": {"type": "string"},
                        "error_logs": {"type": "string"},
                        "system_info": {"type": "object"},
                        "reproduction_steps": {"type": "array", "items": {"type": "string"}},
                        "urgency": {"type": "string"}
                    },
                    "required": ["issue_description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "diagnosis": {"type": "string"},
                        "solution_steps": {"type": "array", "items": {"type": "string"}},
                        "estimated_time": {"type": "number"},
                        "severity": {"type": "string"},
                        "escalation_needed": {"type": "boolean"},
                        "workaround": {"type": "string"}
                    }
                },
                cost=2.0,
                latency=5.0,
                reliability=0.90
            ),
            AgentCapability(
                name="issue_diagnosis",
                description="Analyze technical problems and provide detailed diagnosis",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symptoms": {"type": "array", "items": {"type": "string"}},
                        "error_messages": {"type": "array", "items": {"type": "string"}},
                        "environment": {"type": "object"},
                        "recent_changes": {"type": "array"}
                    },
                    "required": ["symptoms"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "root_cause": {"type": "string"},
                        "contributing_factors": {"type": "array"},
                        "confidence": {"type": "number"},
                        "additional_info_needed": {"type": "array"}
                    }
                },
                cost=1.5,
                latency=3.0,
                reliability=0.85
            ),
            AgentCapability(
                name="solution_implementation",
                description="Implement technical solutions and verify fixes",
                input_schema={
                    "type": "object",
                    "properties": {
                        "solution_steps": {"type": "array", "items": {"type": "string"}},
                        "issue_context": {"type": "object"},
                        "validation_criteria": {"type": "array"}
                    },
                    "required": ["solution_steps"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "implementation_status": {"type": "string"},
                        "verification_results": {"type": "object"},
                        "success": {"type": "boolean"},
                        "additional_steps": {"type": "array"}
                    }
                },
                cost=2.5,
                latency=8.0,
                reliability=0.92
            )
        ]
        
        # Add specialization-specific capabilities
        for spec in self.specializations:
            capabilities.append(AgentCapability(
                name=f"{spec}_specialist",
                description=f"Specialized support for {spec.replace('_', ' ')} issues",
                input_schema={
                    "type": "object",
                    "properties": {
                        "specialized_issue": {"type": "object"},
                        "context": {"type": "object"}
                    },
                    "required": ["specialized_issue"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "specialized_diagnosis": {"type": "string"},
                        "expert_solution": {"type": "object"},
                        "recommendations": {"type": "array"}
                    }
                },
                cost=3.0,
                latency=10.0,
                reliability=0.95
            ))
        
        self.agent_profile = AgentProfile(
            agent_id=self.agent_id,
            name=self.name,
            description=f"Technical support agent specializing in {', '.join(self.specializations)}",
            capabilities=capabilities,
            endpoint=self.endpoint,
            status="active",
            load=0.0,
            metadata={"specializations": self.specializations}
        )
    
    def _setup_knowledge_base(self):
        """Setup technical knowledge base."""
        self.knowledge_base = {
            "authentication_issues": {
                "common_causes": ["expired tokens", "incorrect credentials", "session timeout", "2FA issues"],
                "solutions": {
                    "expired_tokens": [
                        "Clear browser cache and cookies",
                        "Log out and log back in",
                        "Check token expiration settings",
                        "Verify system clock synchronization"
                    ],
                    "incorrect_credentials": [
                        "Verify username and password",
                        "Check caps lock status",
                        "Try password reset process",
                        "Check for account lockout"
                    ],
                    "session_timeout": [
                        "Increase session timeout settings",
                        "Check for idle timeout configuration",
                        "Verify session persistence settings"
                    ]
                }
            },
            "api_issues": {
                "common_causes": ["rate limiting", "authentication errors", "malformed requests", "server errors"],
                "solutions": {
                    "rate_limiting": [
                        "Implement exponential backoff",
                        "Check rate limit headers",
                        "Optimize request frequency",
                        "Consider caching strategies"
                    ],
                    "authentication_errors": [
                        "Verify API key validity",
                        "Check authentication headers",
                        "Ensure proper token format",
                        "Test with Postman or curl"
                    ],
                    "malformed_requests": [
                        "Validate JSON schema",
                        "Check required parameters",
                        "Verify HTTP method",
                        "Review API documentation"
                    ]
                }
            },
            "performance_issues": {
                "common_causes": ["slow queries", "memory leaks", "network latency", "resource contention"],
                "solutions": {
                    "slow_queries": [
                        "Analyze query execution plan",
                        "Add appropriate indexes",
                        "Optimize WHERE clauses",
                        "Consider query caching"
                    ],
                    "memory_leaks": [
                        "Profile memory usage",
                        "Check for unclosed connections",
                        "Review object lifecycle",
                        "Implement garbage collection tuning"
                    ],
                    "network_latency": [
                        "Test network connectivity",
                        "Check bandwidth utilization",
                        "Optimize payload sizes",
                        "Implement CDN or caching"
                    ]
                }
            }
        }
    
    def _setup_diagnostic_patterns(self):
        """Setup diagnostic patterns for issue analysis."""
        self.diagnostic_patterns = {
            "authentication": [
                r"login.*fail", r"authentication.*error", r"unauthorized", r"403.*forbidden",
                r"token.*expired", r"invalid.*credentials", r"session.*timeout"
            ],
            "api": [
                r"api.*error", r"http.*[45]\d\d", r"json.*parse", r"malformed.*request",
                r"rate.*limit", r"endpoint.*not.*found", r"cors.*error"
            ],
            "network": [
                r"connection.*timeout", r"network.*unreachable", r"dns.*resolution",
                r"ssl.*certificate", r"proxy.*error", r"firewall.*block"
            ],
            "database": [
                r"database.*connection", r"sql.*error", r"deadlock", r"table.*lock",
                r"query.*timeout", r"constraint.*violation", r"index.*missing"
            ],
            "performance": [
                r"slow.*response", r"memory.*leak", r"cpu.*spike", r"timeout",
                r"high.*latency", r"performance.*degradation", r"resource.*exhaustion"
            ],
            "security": [
                r"security.*violation", r"xss", r"sql.*injection", r"csrf",
                r"privilege.*escalation", r"data.*breach", r"encryption.*error"
            ]
        }
    
    async def start(self, registry: AgentRegistry, router: MessageRouter):
        """Start the technical support agent."""
        if self.is_running:
            return
        
        self.registry = registry
        self.router = router
        
        # Create registry client
        self.registry_client = AgentRegistryClient(registry, self.agent_profile)
        await self.registry_client.start()
        
        # Register message handlers
        self._register_message_handlers()
        
        self.is_running = True
        logger.info(f"Technical support agent {self.agent_id} started with specializations: {self.specializations}")
    
    async def stop(self):
        """Stop the technical support agent."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.registry_client:
            await self.registry_client.stop()
        
        logger.info(f"Technical support agent {self.agent_id} stopped")
    
    def _register_message_handlers(self):
        """Register message handlers with the router."""
        self.router.register_handler("handle_technical_issue", self._handle_technical_issue)
        self.router.register_handler("diagnose_issue", self._handle_diagnose_issue)
        self.router.register_handler("implement_solution", self._handle_implement_solution)
        self.router.register_handler("handle_escalated_ticket", self._handle_escalated_ticket)
        self.router.register_handler("get_issue_status", self._handle_get_issue_status)
        self.router.register_handler("update_issue", self._handle_update_issue)
        
        # Register specialization handlers
        for spec in self.specializations:
            self.router.register_handler(f"handle_{spec}_issue", self._handle_specialized_issue)
    
    async def _handle_technical_issue(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle a technical issue submission."""
        try:
            payload = message.payload
            issue_description = payload.get("issue_description", "")
            error_logs = payload.get("error_logs", "")
            system_info = payload.get("system_info", {})
            urgency = payload.get("urgency", "normal")
            
            # Create technical issue
            issue = TechnicalIssue(
                issue_id=f"TS-{int(datetime.now().timestamp())}",
                customer_id=payload.get("customer_id", message.sender_id),
                title=issue_description[:50] + "..." if len(issue_description) > 50 else issue_description,
                description=issue_description,
                error_logs=error_logs,
                system_info=system_info,
                assigned_agent=self.agent_id
            )
            
            # Analyze and categorize the issue
            diagnosis_result = await self._analyze_issue(issue)
            
            issue.category = diagnosis_result["category"]
            issue.severity = diagnosis_result["severity"]
            issue.estimated_time = diagnosis_result["estimated_time"]
            
            self.issues[issue.issue_id] = issue
            self.metrics["issues_handled"] += 1
            
            # Update specialization usage metrics
            category_name = issue.category.value if isinstance(issue.category, IssueCategory) else issue.category
            if category_name not in self.metrics["specialization_usage"]:
                self.metrics["specialization_usage"][category_name] = 0
            self.metrics["specialization_usage"][category_name] += 1
            
            await self._update_load()
            
            # Check if escalation is needed
            escalation_needed = diagnosis_result["escalation_needed"]
            
            if escalation_needed:
                await self._escalate_issue(issue, diagnosis_result["escalation_reason"])
                self.metrics["issues_escalated"] += 1
            
            return {
                "issue_id": issue.issue_id,
                "diagnosis": diagnosis_result["diagnosis"],
                "solution_steps": diagnosis_result["solution_steps"],
                "estimated_time": diagnosis_result["estimated_time"],
                "severity": diagnosis_result["severity"].value if hasattr(diagnosis_result["severity"], 'value') else diagnosis_result["severity"],
                "escalation_needed": escalation_needed,
                "workaround": diagnosis_result.get("workaround")
            }
            
        except Exception as e:
            logger.error(f"Error handling technical issue: {e}")
            return {
                "error": str(e),
                "diagnosis": "Unable to analyze the issue at this time. Please provide more details or contact advanced support."
            }
    
    async def _handle_diagnose_issue(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle issue diagnosis request."""
        try:
            payload = message.payload
            symptoms = payload.get("symptoms", [])
            error_messages = payload.get("error_messages", [])
            environment = payload.get("environment", {})
            
            # Perform detailed diagnosis
            analysis = self._perform_detailed_analysis(symptoms, error_messages, environment)
            
            return {
                "root_cause": analysis["root_cause"],
                "contributing_factors": analysis["contributing_factors"],
                "confidence": analysis["confidence"],
                "additional_info_needed": analysis["additional_info_needed"],
                "recommended_actions": analysis["recommended_actions"]
            }
            
        except Exception as e:
            logger.error(f"Error diagnosing issue: {e}")
            return {
                "error": str(e),
                "confidence": 0.0
            }
    
    async def _handle_implement_solution(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle solution implementation request."""
        try:
            payload = message.payload
            solution_steps = payload.get("solution_steps", [])
            issue_context = payload.get("issue_context", {})
            
            # Simulate solution implementation
            implementation_result = await self._implement_solution_steps(solution_steps, issue_context)
            
            return {
                "implementation_status": implementation_result["status"],
                "verification_results": implementation_result["verification"],
                "success": implementation_result["success"],
                "additional_steps": implementation_result.get("additional_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Error implementing solution: {e}")
            return {
                "implementation_status": "failed",
                "success": False,
                "error": str(e)
            }
    
    async def _handle_escalated_ticket(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle an escalated ticket from another agent."""
        try:
            payload = message.payload
            ticket_data = payload.get("ticket", {})
            escalation_type = payload.get("escalation_type", "technical_support")
            escalation_reason = payload.get("escalation_reason", "")
            original_agent = payload.get("original_agent", "")
            
            # Convert ticket to technical issue if needed
            issue = TechnicalIssue(
                issue_id=ticket_data.get("ticket_id") or f"ESC-{int(datetime.now().timestamp())}",
                customer_id=ticket_data.get("customer_id", ""),
                title=ticket_data.get("subject", "Escalated Issue"),
                description=ticket_data.get("description", ""),
                assigned_agent=self.agent_id,
                metadata={
                    "escalated_from": original_agent,
                    "escalation_type": escalation_type,
                    "escalation_reason": escalation_reason,
                    "original_ticket": ticket_data
                }
            )
            
            # Analyze the escalated issue
            diagnosis_result = await self._analyze_issue(issue)
            issue.category = diagnosis_result["category"]
            issue.severity = diagnosis_result["severity"]
            
            self.issues[issue.issue_id] = issue
            self.metrics["issues_handled"] += 1
            
            await self._update_load()
            
            logger.info(f"Accepted escalated ticket {issue.issue_id} from {original_agent}")
            
            return {
                "accepted": True,
                "issue_id": issue.issue_id,
                "estimated_resolution": diagnosis_result["estimated_time"],
                "initial_diagnosis": diagnosis_result["diagnosis"]
            }
            
        except Exception as e:
            logger.error(f"Error handling escalated ticket: {e}")
            return {
                "accepted": False,
                "error": str(e)
            }
    
    async def _handle_get_issue_status(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle issue status request."""
        try:
            issue_id = message.payload.get("issue_id")
            
            if issue_id not in self.issues:
                return {
                    "success": False,
                    "error": "Issue not found"
                }
            
            issue = self.issues[issue_id]
            
            return {
                "success": True,
                "issue": issue.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting issue status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_update_issue(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle issue update request."""
        try:
            issue_id = message.payload.get("issue_id")
            updates = message.payload.get("updates", {})
            
            if issue_id not in self.issues:
                return {
                    "success": False,
                    "error": "Issue not found"
                }
            
            issue = self.issues[issue_id]
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(issue, field):
                    setattr(issue, field, value)
            
            issue.updated_at = datetime.now().isoformat()
            
            # If issue is resolved, update metrics
            if updates.get("status") == "resolved":
                self._update_resolution_metrics(issue)
            
            return {
                "success": True,
                "issue_id": issue_id,
                "status": issue.status
            }
            
        except Exception as e:
            logger.error(f"Error updating issue: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_specialized_issue(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle specialized issue based on agent's specializations."""
        try:
            payload = message.payload
            specialized_issue = payload.get("specialized_issue", {})
            context = payload.get("context", {})
            
            # Extract specialization from action
            action_parts = message.action.split("_")
            if len(action_parts) >= 2:
                specialization = "_".join(action_parts[1:-1])  # Remove 'handle_' and '_issue'
            else:
                specialization = "general"
            
            if specialization not in self.specializations:
                return {
                    "error": f"Agent does not specialize in {specialization}",
                    "available_specializations": self.specializations
                }
            
            # Provide specialized analysis
            specialized_analysis = self._get_specialized_analysis(specialization, specialized_issue, context)
            
            return {
                "specialized_diagnosis": specialized_analysis["diagnosis"],
                "expert_solution": specialized_analysis["solution"],
                "recommendations": specialized_analysis["recommendations"],
                "confidence": specialized_analysis["confidence"]
            }
            
        except Exception as e:
            logger.error(f"Error handling specialized issue: {e}")
            return {
                "error": str(e),
                "confidence": 0.0
            }
    
    async def _analyze_issue(self, issue: TechnicalIssue) -> Dict[str, Any]:
        """Analyze a technical issue and provide diagnosis."""
        
        # Categorize the issue based on description and error logs
        category = self._categorize_issue(issue.description, issue.error_logs or "")
        severity = self._assess_severity(issue.description, issue.error_logs or "")
        
        # Generate diagnosis and solution steps
        diagnosis = self._generate_diagnosis(issue, category, severity)
        solution_steps = self._generate_solution_steps(category, issue.description)
        
        # Estimate resolution time
        estimated_time = self._estimate_resolution_time(category, severity)
        
        # Check if escalation is needed
        escalation_needed, escalation_reason = self._check_escalation_needed(category, severity, issue)
        
        # Generate workaround if applicable
        workaround = self._generate_workaround(category, issue.description)
        
        return {
            "category": category,
            "severity": severity,
            "diagnosis": diagnosis,
            "solution_steps": solution_steps,
            "estimated_time": estimated_time,
            "escalation_needed": escalation_needed,
            "escalation_reason": escalation_reason,
            "workaround": workaround
        }
    
    def _categorize_issue(self, description: str, error_logs: str) -> IssueCategory:
        """Categorize the technical issue based on content analysis."""
        text_to_analyze = (description + " " + error_logs).lower()
        
        category_scores = {}
        
        for category, patterns in self.diagnostic_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_to_analyze))
                score += matches
            category_scores[category] = score
        
        # Find the category with the highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return IssueCategory(best_category)
        
        return IssueCategory.OTHER
    
    def _assess_severity(self, description: str, error_logs: str) -> IssueSeverity:
        """Assess the severity of the technical issue."""
        text = (description + " " + error_logs).lower()
        
        critical_indicators = ["critical", "down", "outage", "security breach", "data loss"]
        high_indicators = ["urgent", "production", "cannot", "blocking", "severe"]
        medium_indicators = ["slow", "intermittent", "sometimes", "occasional"]
        
        if any(indicator in text for indicator in critical_indicators):
            return IssueSeverity.CRITICAL
        elif any(indicator in text for indicator in high_indicators):
            return IssueSeverity.HIGH
        elif any(indicator in text for indicator in medium_indicators):
            return IssueSeverity.MEDIUM
        else:
            return IssueSeverity.LOW
    
    def _generate_diagnosis(self, issue: TechnicalIssue, category: IssueCategory, severity: IssueSeverity) -> str:
        """Generate a diagnosis based on the issue analysis."""
        
        category_name = category.value if isinstance(category, IssueCategory) else category
        severity_name = severity.value if isinstance(severity, IssueSeverity) else severity
        
        # Get knowledge base information
        kb_info = self.knowledge_base.get(f"{category_name}_issues", {})
        common_causes = kb_info.get("common_causes", ["Unknown cause"])
        
        diagnosis = f"Based on the analysis, this appears to be a {severity_name} severity {category_name} issue. "
        diagnosis += f"Common causes for this type of issue include: {', '.join(common_causes[:3])}. "
        
        # Add specific observations from the issue
        if issue.error_logs:
            diagnosis += "Error logs indicate specific failure points that will help in resolution. "
        
        if issue.system_info:
            diagnosis += "System information provided will assist in environmental considerations. "
        
        return diagnosis
    
    def _generate_solution_steps(self, category: IssueCategory, description: str) -> List[str]:
        """Generate solution steps for the issue category."""
        
        category_name = category.value if isinstance(category, IssueCategory) else category
        kb_info = self.knowledge_base.get(f"{category_name}_issues", {})
        solutions = kb_info.get("solutions", {})
        
        # Default generic steps
        generic_steps = [
            "Gather additional information about the issue",
            "Reproduce the issue in a controlled environment",
            "Analyze logs and system state",
            "Implement and test potential solution",
            "Verify fix and monitor for recurrence"
        ]
        
        # If we have specific solutions, use them
        if solutions:
            # Pick the most relevant solution based on description
            for cause, steps in solutions.items():
                if any(keyword in description.lower() for keyword in cause.split("_")):
                    return steps
            
            # Return first solution if no specific match
            return list(solutions.values())[0]
        
        return generic_steps
    
    def _estimate_resolution_time(self, category: IssueCategory, severity: IssueSeverity) -> float:
        """Estimate resolution time in hours."""
        
        base_times = {
            IssueSeverity.LOW: 1.0,
            IssueSeverity.MEDIUM: 2.0,
            IssueSeverity.HIGH: 4.0,
            IssueSeverity.CRITICAL: 8.0
        }
        
        category_multipliers = {
            IssueCategory.AUTHENTICATION: 0.8,
            IssueCategory.API: 1.0,
            IssueCategory.NETWORK: 1.2,
            IssueCategory.DATABASE: 1.5,
            IssueCategory.PERFORMANCE: 2.0,
            IssueCategory.SECURITY: 2.5,
            IssueCategory.INTEGRATION: 1.8,
            IssueCategory.OTHER: 1.0
        }
        
        base_time = base_times.get(severity, 2.0)
        multiplier = category_multipliers.get(category, 1.0)
        
        return base_time * multiplier
    
    def _check_escalation_needed(self, category: IssueCategory, severity: IssueSeverity, 
                                issue: TechnicalIssue) -> Tuple[bool, str]:
        """Check if the issue needs escalation."""
        
        # Always escalate critical security issues
        if category == IssueCategory.SECURITY and severity == IssueSeverity.CRITICAL:
            return True, "Critical security issue requires specialist attention"
        
        # Escalate critical issues in specialized areas we don't handle
        if severity == IssueSeverity.CRITICAL:
            category_name = category.value if isinstance(category, IssueCategory) else category
            if category_name not in self.specializations and "general_technical" not in self.specializations:
                return True, f"Critical {category_name} issue requires specialized expertise"
        
        # Escalate complex integration issues
        if category == IssueCategory.INTEGRATION and severity in [IssueSeverity.HIGH, IssueSeverity.CRITICAL]:
            return True, "Complex integration issue may require multiple specialists"
        
        return False, ""
    
    def _generate_workaround(self, category: IssueCategory, description: str) -> Optional[str]:
        """Generate a temporary workaround if possible."""
        
        workarounds = {
            IssueCategory.AUTHENTICATION: "Try clearing browser cache and cookies, or use an incognito window",
            IssueCategory.API: "Implement retry logic with exponential backoff for API calls",
            IssueCategory.NETWORK: "Check network connectivity and try alternative network connection",
            IssueCategory.PERFORMANCE: "Clear cache or reduce data set size for temporary relief",
            IssueCategory.UI_UX: "Try refreshing the page or using keyboard shortcuts as alternative"
        }
        
        return workarounds.get(category, "No immediate workaround available")
    
    def _perform_detailed_analysis(self, symptoms: List[str], error_messages: List[str], 
                                 environment: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed technical analysis."""
        
        # Analyze symptoms and error messages
        all_text = " ".join(symptoms + error_messages).lower()
        
        # Determine most likely root cause
        root_cause = "Unknown - requires further investigation"
        confidence = 0.5
        contributing_factors = []
        additional_info_needed = []
        
        # Pattern matching for common issues
        if "timeout" in all_text:
            root_cause = "Timeout issue - likely network or performance related"
            confidence = 0.8
            contributing_factors = ["Network latency", "Server overload", "Client timeout settings"]
            additional_info_needed = ["Network diagnostics", "Server performance metrics", "Timeout configuration"]
        elif "authentication" in all_text or "unauthorized" in all_text:
            root_cause = "Authentication failure"
            confidence = 0.9
            contributing_factors = ["Invalid credentials", "Expired tokens", "Session issues"]
            additional_info_needed = ["Authentication logs", "Token validity", "Session configuration"]
        elif "database" in all_text or "sql" in all_text:
            root_cause = "Database connectivity or query issue"
            confidence = 0.85
            contributing_factors = ["Database connection pool", "Query performance", "Lock contention"]
            additional_info_needed = ["Database logs", "Query execution plan", "Connection statistics"]
        
        # Generate recommended actions
        recommended_actions = [
            "Collect detailed error logs",
            "Check system resource utilization",
            "Verify configuration settings",
            "Test in isolated environment"
        ]
        
        return {
            "root_cause": root_cause,
            "contributing_factors": contributing_factors,
            "confidence": confidence,
            "additional_info_needed": additional_info_needed,
            "recommended_actions": recommended_actions
        }
    
    async def _implement_solution_steps(self, solution_steps: List[str], 
                                      issue_context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate implementation of solution steps."""
        
        # In a real implementation, this would execute actual remediation steps
        # For now, we simulate the process
        
        implementation_log = []
        success = True
        
        for i, step in enumerate(solution_steps, 1):
            # Simulate step execution
            await asyncio.sleep(0.1)  # Simulate processing time
            
            step_result = {
                "step": i,
                "description": step,
                "status": "completed" if i <= len(solution_steps) * 0.8 else "pending",
                "timestamp": datetime.now().isoformat()
            }
            
            implementation_log.append(step_result)
            
            # Simulate occasional failures
            if "database" in step.lower() and i == len(solution_steps) // 2:
                step_result["status"] = "failed"
                step_result["error"] = "Database connection timeout"
                success = False
        
        verification_results = {
            "tests_passed": len([log for log in implementation_log if log["status"] == "completed"]),
            "tests_failed": len([log for log in implementation_log if log["status"] == "failed"]),
            "implementation_log": implementation_log
        }
        
        additional_steps = []
        if not success:
            additional_steps = [
                "Investigate database connectivity",
                "Retry failed steps with timeout adjustments",
                "Consider alternative solution approach"
            ]
        
        return {
            "status": "completed" if success else "partial",
            "verification": verification_results,
            "success": success,
            "additional_steps": additional_steps
        }
    
    def _get_specialized_analysis(self, specialization: str, issue: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide specialized analysis based on agent's expertise."""
        
        # This would contain deep specialized knowledge
        specialized_knowledge = {
            "api_integration": {
                "diagnosis": "API integration issue requiring detailed protocol analysis",
                "solution": {
                    "immediate": ["Check API documentation version", "Verify endpoint URLs"],
                    "intermediate": ["Test with API client tools", "Review authentication flow"],
                    "advanced": ["Implement circuit breaker pattern", "Add comprehensive logging"]
                },
                "recommendations": [
                    "Implement proper error handling",
                    "Add request/response logging",
                    "Consider API versioning strategy"
                ],
                "confidence": 0.95
            },
            "database_optimization": {
                "diagnosis": "Database performance issue requiring query and index optimization",
                "solution": {
                    "immediate": ["Analyze slow query log", "Check index usage"],
                    "intermediate": ["Optimize problematic queries", "Add missing indexes"],
                    "advanced": ["Consider partitioning", "Implement query caching"]
                },
                "recommendations": [
                    "Regular performance monitoring",
                    "Query optimization reviews",
                    "Index maintenance strategy"
                ],
                "confidence": 0.92
            },
            "general_technical": {
                "diagnosis": "Technical issue requiring systematic troubleshooting approach",
                "solution": {
                    "immediate": ["Gather comprehensive logs", "Reproduce in test environment"],
                    "intermediate": ["Analyze root cause", "Develop targeted fix"],
                    "advanced": ["Implement monitoring", "Create prevention strategy"]
                },
                "recommendations": [
                    "Follow systematic debugging process",
                    "Document resolution steps",
                    "Implement preventive measures"
                ],
                "confidence": 0.80
            }
        }
        
        return specialized_knowledge.get(specialization, specialized_knowledge["general_technical"])
    
    async def _escalate_issue(self, issue: TechnicalIssue, reason: str) -> bool:
        """Escalate a technical issue to appropriate specialist or management."""
        try:
            # Determine escalation target
            escalation_capability = self._determine_escalation_target(issue.category, issue.severity)
            
            # Find appropriate agents
            agents = await self.registry.discover_agents(
                required_capabilities=[escalation_capability],
                status_filter="active"
            )
            
            if not agents:
                logger.warning(f"No agents found with capability {escalation_capability}")
                return False
            
            target_agent = agents[0]
            
            escalation_message = create_request_message(
                sender_id=self.agent_id,
                action="handle_escalated_issue",
                payload={
                    "issue": issue.to_dict(),
                    "escalation_reason": reason,
                    "escalation_capability": escalation_capability,
                    "original_agent": self.agent_id
                },
                recipient_id=target_agent.agent_id,
                priority=Priority.HIGH
            )
            
            response = await self.router.send_message(escalation_message)
            
            if response and response.payload.get("accepted", False):
                issue.status = "escalated"
                issue.assigned_agent = target_agent.agent_id
                issue.metadata["escalation_history"] = issue.metadata.get("escalation_history", [])
                issue.metadata["escalation_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "from_agent": self.agent_id,
                    "to_agent": target_agent.agent_id,
                    "reason": reason,
                    "capability": escalation_capability
                })
                
                logger.info(f"Escalated issue {issue.issue_id} to {target_agent.agent_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error escalating issue: {e}")
            return False
    
    def _determine_escalation_target(self, category: IssueCategory, severity: IssueSeverity) -> str:
        """Determine the appropriate escalation target capability."""
        
        if severity == IssueSeverity.CRITICAL:
            if category == IssueCategory.SECURITY:
                return "security_specialist"
            elif category == IssueCategory.DATABASE:
                return "database_specialist"
            elif category == IssueCategory.NETWORK:
                return "network_specialist"
            else:
                return "senior_technical_support"
        else:
            return "technical_lead"
    
    async def _update_load(self):
        """Update agent load based on current issues."""
        open_issues = sum(1 for issue in self.issues.values() if issue.status == "open")
        max_capacity = 10  # Maximum issues this agent can handle
        
        load = min(open_issues / max_capacity, 1.0)
        
        if self.registry_client:
            await self.registry_client.update_status(
                load=load,
                status="busy" if load > 0.8 else "active"
            )
    
    def _update_resolution_metrics(self, issue: TechnicalIssue):
        """Update resolution metrics when an issue is resolved."""
        self.metrics["issues_resolved"] += 1
        
        try:
            # Calculate resolution time
            created = datetime.fromisoformat(issue.created_at)
            resolved = datetime.fromisoformat(issue.updated_at)
            resolution_time = (resolved - created).total_seconds() / 3600  # hours
            
            # Update average resolution time
            if self.metrics["average_resolution_time"] == 0.0:
                self.metrics["average_resolution_time"] = resolution_time
            else:
                resolved_count = self.metrics["issues_resolved"]
                current_avg = self.metrics["average_resolution_time"]
                self.metrics["average_resolution_time"] = (
                    (current_avg * (resolved_count - 1) + resolution_time) / resolved_count
                )
            
            # Update accuracy score (simplified - in real system would be based on customer feedback)
            estimated_time = issue.estimated_time
            if estimated_time > 0:
                accuracy = min(estimated_time / resolution_time, 2.0) if resolution_time > 0 else 1.0
                if accuracy > 1.0:
                    accuracy = 2.0 - accuracy  # Penalty for overestimating
                
                if self.metrics["accuracy_score"] == 0.0:
                    self.metrics["accuracy_score"] = accuracy
                else:
                    resolved_count = self.metrics["issues_resolved"]
                    current_accuracy = self.metrics["accuracy_score"]
                    self.metrics["accuracy_score"] = (
                        (current_accuracy * (resolved_count - 1) + accuracy) / resolved_count
                    )
        
        except Exception as e:
            logger.error(f"Error updating resolution metrics: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        self.metrics["last_updated"] = datetime.now().isoformat()
        self.metrics["current_issues"] = len([i for i in self.issues.values() if i.status == "open"])
        return self.metrics.copy()
    
    def get_issues(self, status: str = None, category: str = None) -> List[Dict[str, Any]]:
        """Get issues, optionally filtered by status and/or category."""
        issues = list(self.issues.values())
        
        if status:
            issues = [i for i in issues if i.status == status]
        
        if category:
            issues = [i for i in issues if (i.category.value if isinstance(i.category, IssueCategory) else i.category) == category]
        
        return [issue.to_dict() for issue in issues]


# Factory function for easy agent creation
def create_technical_support_agent(
    agent_id: str,
    name: str = None,
    endpoint: str = None,
    specializations: List[str] = None
) -> TechnicalSupportAgent:
    """Create a technical support agent with specific specializations."""
    
    return TechnicalSupportAgent(
        agent_id=agent_id,
        name=name,
        endpoint=endpoint,
        specializations=specializations or ["general_technical"]
    )