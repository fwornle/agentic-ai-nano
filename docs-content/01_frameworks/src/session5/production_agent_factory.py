# src/session5/production_agent_factory.py
"""
Production-ready agent factory for scalable PydanticAI agent creation and management.
Implements factory patterns, agent pools, lifecycle management, and configuration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable, Union
from pydantic import BaseModel, Field, validator
from pydantic_ai import Agent, RunContext
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import threading
import weakref
from dataclasses import dataclass, field
import uuid
from collections import defaultdict
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class AgentState(str, Enum):
    """Possible states for agents."""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    TERMINATED = "terminated"

class AgentType(str, Enum):
    """Types of agents that can be created."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    VALIDATION = "validation"

class AgentCapability(str, Enum):
    """Agent capabilities."""
    TEXT_PROCESSING = "text_processing"
    DATA_ANALYSIS = "data_analysis"
    CODE_GENERATION = "code_generation"
    RESEARCH = "research"
    PLANNING = "planning"
    VALIDATION = "validation"
    MONITORING = "monitoring"

class AgentConfiguration(BaseModel):
    """Configuration for agent instances."""
    agent_type: AgentType = Field(..., description="Type of agent")
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")
    max_concurrent_tasks: int = Field(default=5, ge=1, description="Max concurrent tasks")
    timeout_seconds: float = Field(default=30.0, gt=0, description="Default timeout")
    retry_attempts: int = Field(default=3, ge=0, description="Number of retry attempts")
    memory_limit_mb: Optional[int] = Field(None, ge=1, description="Memory limit in MB")
    priority: int = Field(default=0, description="Agent priority (higher = more important)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('capabilities')
    def validate_capabilities(cls, v, values):
        """Validate capabilities match agent type."""
        agent_type = values.get('agent_type')
        if agent_type == AgentType.RESEARCH and AgentCapability.RESEARCH not in v:
            raise ValueError("Research agents must have research capability")
        return v

class AgentMetrics(BaseModel):
    """Metrics for agent instances."""
    agent_id: str = Field(..., description="Agent identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    total_tasks: int = Field(default=0, ge=0)
    successful_tasks: int = Field(default=0, ge=0)
    failed_tasks: int = Field(default=0, ge=0)
    average_response_time: float = Field(default=0.0, ge=0)
    current_load: int = Field(default=0, ge=0)
    error_rate: float = Field(default=0.0, ge=0, le=1)
    uptime_seconds: float = Field(default=0.0, ge=0)

class AgentInstance(BaseModel):
    """Represents a managed agent instance."""
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: AgentType = Field(..., description="Agent type")
    state: AgentState = Field(default=AgentState.INITIALIZING, description="Current state")
    configuration: AgentConfiguration = Field(..., description="Agent configuration")
    metrics: AgentMetrics = Field(..., description="Agent metrics")
    created_at: datetime = Field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = Field(None, description="Last health check")
    error_message: Optional[str] = Field(None, description="Last error message")
    
    class Config:
        arbitrary_types_allowed = True

# Abstract factory interface

class AgentFactory(ABC):
    """Abstract factory for creating agents."""
    
    @abstractmethod
    async def create_agent(
        self, 
        config: AgentConfiguration
    ) -> AgentInstance:
        """Create a new agent instance."""
        pass
    
    @abstractmethod
    async def destroy_agent(self, agent_id: str) -> bool:
        """Destroy an agent instance."""
        pass
    
    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """Get agent by ID."""
        pass
    
    @abstractmethod
    def list_agents(self) -> List[AgentInstance]:
        """List all managed agents."""
        pass

# Concrete factory implementation

class ProductionAgentFactory(AgentFactory):
    """Production-ready agent factory with pooling and lifecycle management."""
    
    def __init__(self, max_agents: int = 100):
        self.max_agents = max_agents
        self.agents: Dict[str, AgentInstance] = {}
        self.agent_pools: Dict[AgentType, List[str]] = defaultdict(list)
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__ + ".ProductionAgentFactory")
        self._health_check_task: Optional[asyncio.Task] = None
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        if self._health_check_task is None or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def _health_check_loop(self):
        """Background health check loop."""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(30)  # Health check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _perform_health_checks(self):
        """Perform health checks on all agents."""
        async with self.lock:
            current_time = datetime.now()
            unhealthy_agents = []
            
            for agent_id, agent in self.agents.items():
                try:
                    # Update uptime
                    agent.metrics.uptime_seconds = (current_time - agent.created_at).total_seconds()
                    
                    # Check for stale agents (no activity in last 5 minutes)
                    if (current_time - agent.metrics.last_activity).total_seconds() > 300:
                        if agent.state != AgentState.ERROR:
                            agent.state = AgentState.ERROR
                            agent.error_message = "Agent appears to be stale"
                            unhealthy_agents.append(agent_id)
                    
                    # Update health check timestamp
                    agent.last_health_check = current_time
                
                except Exception as e:
                    self.logger.error(f"Health check failed for agent {agent_id}: {str(e)}")
                    unhealthy_agents.append(agent_id)
            
            # Clean up unhealthy agents
            for agent_id in unhealthy_agents:
                await self._cleanup_agent(agent_id)
    
    async def _cleanup_agent(self, agent_id: str):
        """Clean up an unhealthy agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.state = AgentState.TERMINATED
            
            # Remove from pools
            for pool in self.agent_pools.values():
                if agent_id in pool:
                    pool.remove(agent_id)
            
            self.logger.warning(f"Cleaned up unhealthy agent: {agent_id}")
    
    async def create_agent(self, config: AgentConfiguration) -> AgentInstance:
        """Create a new agent instance."""
        async with self.lock:
            if len(self.agents) >= self.max_agents:
                raise ValueError(f"Maximum agent limit ({self.max_agents}) reached")
            
            agent_id = str(uuid.uuid4())
            
            # Create metrics
            metrics = AgentMetrics(agent_id=agent_id)
            
            # Create agent instance
            agent = AgentInstance(
                agent_id=agent_id,
                agent_type=config.agent_type,
                configuration=config,
                metrics=metrics
            )
            
            try:
                # Initialize agent (simulate initialization)
                await asyncio.sleep(0.1)  # Simulate initialization time
                
                agent.state = AgentState.READY
                self.agents[agent_id] = agent
                self.agent_pools[config.agent_type].append(agent_id)
                
                self.logger.info(f"Created agent {agent_id} of type {config.agent_type}")
                return agent
            
            except Exception as e:
                agent.state = AgentState.ERROR
                agent.error_message = f"Failed to initialize: {str(e)}"
                raise ValueError(f"Failed to create agent: {str(e)}")
    
    async def destroy_agent(self, agent_id: str) -> bool:
        """Destroy an agent instance."""
        async with self.lock:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            agent.state = AgentState.SHUTTING_DOWN
            
            try:
                # Graceful shutdown (simulate cleanup)
                await asyncio.sleep(0.1)
                
                agent.state = AgentState.TERMINATED
                
                # Remove from pools
                for pool in self.agent_pools.values():
                    if agent_id in pool:
                        pool.remove(agent_id)
                
                # Remove from active agents
                del self.agents[agent_id]
                
                self.logger.info(f"Destroyed agent {agent_id}")
                return True
            
            except Exception as e:
                agent.state = AgentState.ERROR
                agent.error_message = f"Failed to destroy: {str(e)}"
                self.logger.error(f"Failed to destroy agent {agent_id}: {str(e)}")
                return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[AgentInstance]:
        """List all managed agents."""
        return list(self.agents.values())
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[AgentInstance]:
        """Get agents by type."""
        agent_ids = self.agent_pools.get(agent_type, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    def get_available_agent(self, agent_type: AgentType) -> Optional[AgentInstance]:
        """Get an available agent of the specified type."""
        agents = self.get_agents_by_type(agent_type)
        
        # Find agent with lowest load
        available_agents = [
            agent for agent in agents 
            if agent.state == AgentState.READY and 
               agent.metrics.current_load < agent.configuration.max_concurrent_tasks
        ]
        
        if not available_agents:
            return None
        
        return min(available_agents, key=lambda a: a.metrics.current_load)
    
    async def get_or_create_agent(
        self, 
        agent_type: AgentType,
        config: Optional[AgentConfiguration] = None
    ) -> AgentInstance:
        """Get an available agent or create a new one."""
        # Try to get existing agent
        agent = self.get_available_agent(agent_type)
        if agent:
            return agent
        
        # Create new agent if none available
        if config is None:
            config = self._get_default_config(agent_type)
        
        return await self.create_agent(config)
    
    def _get_default_config(self, agent_type: AgentType) -> AgentConfiguration:
        """Get default configuration for agent type."""
        capability_map = {
            AgentType.RESEARCH: [AgentCapability.RESEARCH, AgentCapability.TEXT_PROCESSING],
            AgentType.ANALYSIS: [AgentCapability.DATA_ANALYSIS, AgentCapability.TEXT_PROCESSING],
            AgentType.PLANNING: [AgentCapability.PLANNING, AgentCapability.TEXT_PROCESSING],
            AgentType.EXECUTION: [AgentCapability.CODE_GENERATION, AgentCapability.TEXT_PROCESSING],
            AgentType.MONITORING: [AgentCapability.MONITORING, AgentCapability.DATA_ANALYSIS],
            AgentType.VALIDATION: [AgentCapability.VALIDATION, AgentCapability.TEXT_PROCESSING],
        }
        
        return AgentConfiguration(
            agent_type=agent_type,
            capabilities=capability_map.get(agent_type, [AgentCapability.TEXT_PROCESSING]),
            max_concurrent_tasks=3,
            timeout_seconds=30.0,
            retry_attempts=2
        )
    
    def get_factory_stats(self) -> Dict[str, Any]:
        """Get factory statistics."""
        stats = {
            "total_agents": len(self.agents),
            "max_agents": self.max_agents,
            "agents_by_type": {},
            "agents_by_state": {},
            "overall_metrics": {
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "average_response_time": 0.0,
                "average_uptime": 0.0
            }
        }
        
        # Count by type and state
        for agent in self.agents.values():
            # By type
            agent_type = agent.agent_type.value
            if agent_type not in stats["agents_by_type"]:
                stats["agents_by_type"][agent_type] = 0
            stats["agents_by_type"][agent_type] += 1
            
            # By state
            state = agent.state.value
            if state not in stats["agents_by_state"]:
                stats["agents_by_state"][state] = 0
            stats["agents_by_state"][state] += 1
            
            # Aggregate metrics
            metrics = agent.metrics
            stats["overall_metrics"]["total_tasks"] += metrics.total_tasks
            stats["overall_metrics"]["successful_tasks"] += metrics.successful_tasks
            stats["overall_metrics"]["failed_tasks"] += metrics.failed_tasks
        
        # Calculate averages
        if self.agents:
            total_response_time = sum(a.metrics.average_response_time for a in self.agents.values())
            total_uptime = sum(a.metrics.uptime_seconds for a in self.agents.values())
            stats["overall_metrics"]["average_response_time"] = total_response_time / len(self.agents)
            stats["overall_metrics"]["average_uptime"] = total_uptime / len(self.agents)
        
        return stats

# Agent pool manager

class AgentPoolManager:
    """Manages pools of agents for different workloads."""
    
    def __init__(self, factory: AgentFactory):
        self.factory = factory
        self.pools: Dict[str, List[str]] = defaultdict(list)
        self.pool_configs: Dict[str, AgentConfiguration] = {}
        self.logger = logging.getLogger(__name__ + ".AgentPoolManager")
    
    async def create_pool(
        self, 
        pool_name: str, 
        config: AgentConfiguration, 
        pool_size: int = 5
    ) -> bool:
        """Create a pool of agents."""
        try:
            self.pool_configs[pool_name] = config
            
            for _ in range(pool_size):
                agent = await self.factory.create_agent(config)
                self.pools[pool_name].append(agent.agent_id)
            
            self.logger.info(f"Created pool '{pool_name}' with {pool_size} agents")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to create pool '{pool_name}': {str(e)}")
            return False
    
    async def get_agent_from_pool(self, pool_name: str) -> Optional[AgentInstance]:
        """Get an available agent from the pool."""
        if pool_name not in self.pools:
            return None
        
        agent_ids = self.pools[pool_name]
        
        for agent_id in agent_ids:
            agent = self.factory.get_agent(agent_id)
            if agent and agent.state == AgentState.READY:
                if agent.metrics.current_load < agent.configuration.max_concurrent_tasks:
                    return agent
        
        return None
    
    async def scale_pool(self, pool_name: str, target_size: int) -> bool:
        """Scale a pool to target size."""
        if pool_name not in self.pools or pool_name not in self.pool_configs:
            return False
        
        try:
            current_size = len(self.pools[pool_name])
            config = self.pool_configs[pool_name]
            
            if target_size > current_size:
                # Scale up
                for _ in range(target_size - current_size):
                    agent = await self.factory.create_agent(config)
                    self.pools[pool_name].append(agent.agent_id)
                
            elif target_size < current_size:
                # Scale down
                agents_to_remove = current_size - target_size
                for _ in range(agents_to_remove):
                    if self.pools[pool_name]:
                        agent_id = self.pools[pool_name].pop()
                        await self.factory.destroy_agent(agent_id)
            
            self.logger.info(f"Scaled pool '{pool_name}' to {target_size} agents")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to scale pool '{pool_name}': {str(e)}")
            return False

# Example usage and demonstrations

def demo_production_agent_factory():
    """Demonstrate production agent factory usage."""
    print("\n=== Production Agent Factory Demo ===")
    
    async def run_demo():
        # Create factory
        factory = ProductionAgentFactory(max_agents=20)
        
        # Create different types of agents
        research_config = AgentConfiguration(
            agent_type=AgentType.RESEARCH,
            capabilities=[AgentCapability.RESEARCH, AgentCapability.TEXT_PROCESSING],
            max_concurrent_tasks=3
        )
        
        analysis_config = AgentConfiguration(
            agent_type=AgentType.ANALYSIS,
            capabilities=[AgentCapability.DATA_ANALYSIS, AgentCapability.TEXT_PROCESSING],
            max_concurrent_tasks=5
        )
        
        print("Creating research agent...")
        research_agent = await factory.create_agent(research_config)
        print(f"Created: {research_agent.agent_id} ({research_agent.agent_type})")
        
        print("Creating analysis agent...")
        analysis_agent = await factory.create_agent(analysis_config)
        print(f"Created: {analysis_agent.agent_id} ({analysis_agent.agent_type})")
        
        # Test agent pool manager
        print("\nTesting agent pool manager...")
        pool_manager = AgentPoolManager(factory)
        
        await pool_manager.create_pool("research_pool", research_config, 3)
        await pool_manager.create_pool("analysis_pool", analysis_config, 2)
        
        # Get agents from pools
        pool_agent = await pool_manager.get_agent_from_pool("research_pool")
        if pool_agent:
            print(f"Got agent from pool: {pool_agent.agent_id}")
        
        # Show factory stats
        print("\nFactory Statistics:")
        stats = factory.get_factory_stats()
        print(json.dumps(stats, indent=2, default=str))
        
        # Simulate some work and metrics updates
        print("\nSimulating agent work...")
        research_agent.metrics.total_tasks += 5
        research_agent.metrics.successful_tasks += 4
        research_agent.metrics.failed_tasks += 1
        research_agent.metrics.average_response_time = 1.5
        research_agent.metrics.last_activity = datetime.now()
        
        # Scale pool
        print("Scaling research pool...")
        await pool_manager.scale_pool("research_pool", 5)
        
        # Final stats
        print("\nFinal Factory Statistics:")
        final_stats = factory.get_factory_stats()
        print(json.dumps(final_stats, indent=2, default=str))
        
        # Cleanup
        print("\nCleaning up...")
        for agent in factory.list_agents():
            await factory.destroy_agent(agent.agent_id)
    
    # Run the async demo
    asyncio.run(run_demo())

if __name__ == "__main__":
    demo_production_agent_factory()