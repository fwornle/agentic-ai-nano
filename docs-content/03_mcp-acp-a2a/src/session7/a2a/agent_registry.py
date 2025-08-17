"""
Agent Registry and Discovery System

This module provides a centralized registry for agent discovery and coordination.
It manages agent profiles, capabilities, and health monitoring.
"""

import asyncio
import json
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import asdict

# For production, use Redis. For development/testing, use in-memory storage
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    import threading

from .protocol import AgentProfile, AgentCapability, A2AMessage, MessageType

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Centralized agent registry for discovery and coordination."""
    
    def __init__(self, redis_client=None, use_redis: bool = True):
        self.use_redis = use_redis and REDIS_AVAILABLE and redis_client is not None
        
        if self.use_redis:
            self.redis_client = redis_client
            self.registry_prefix = "agent_registry:"
            self.capability_index = "capability_index:"
        else:
            # In-memory storage for development/testing
            self._agents: Dict[str, Dict] = {}
            self._capability_index: Dict[str, Set[str]] = {}
            self._lock = threading.RLock()
        
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_timeout = 90   # seconds
        
        # Background tasks
        self._heartbeat_task = None
        self._cleanup_task = None
        self._running = False
    
    async def start(self):
        """Start the registry background tasks."""
        if self._running:
            return
        
        self._running = True
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Agent registry started")
    
    async def stop(self):
        """Stop the registry background tasks."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Agent registry stopped")
    
    async def register_agent(self, profile: AgentProfile) -> bool:
        """Register an agent in the registry."""
        try:
            profile_data = profile.to_dict()
            
            if self.use_redis:
                # Store agent profile
                profile_key = f"{self.registry_prefix}{profile.agent_id}"
                profile_json = json.dumps(profile_data)
                
                self.redis_client.set(profile_key, profile_json)
                self.redis_client.expire(profile_key, self.heartbeat_timeout)
                
                # Index capabilities for fast lookup
                for capability in profile.capabilities:
                    cap_key = f"{self.capability_index}{capability.name}"
                    self.redis_client.sadd(cap_key, profile.agent_id)
                    self.redis_client.expire(cap_key, self.heartbeat_timeout)
            else:
                # In-memory storage
                with self._lock:
                    self._agents[profile.agent_id] = profile_data
                    
                    # Index capabilities
                    for capability in profile.capabilities:
                        cap_name = capability.name
                        if cap_name not in self._capability_index:
                            self._capability_index[cap_name] = set()
                        self._capability_index[cap_name].add(profile.agent_id)
            
            logger.info(f"Registered agent {profile.agent_id} with {len(profile.capabilities)} capabilities")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {profile.agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry."""
        try:
            # Get agent profile first to clean up capability indices
            profile = await self.get_agent_profile(agent_id)
            
            if self.use_redis:
                if profile:
                    # Remove from capability indices
                    for capability in profile.capabilities:
                        cap_key = f"{self.capability_index}{capability.name}"
                        self.redis_client.srem(cap_key, agent_id)
                
                # Remove agent profile
                profile_key = f"{self.registry_prefix}{agent_id}"
                self.redis_client.delete(profile_key)
            else:
                # In-memory storage
                with self._lock:
                    if agent_id in self._agents and profile:
                        # Remove from capability indices
                        for capability in profile.capabilities:
                            cap_name = capability.name
                            if cap_name in self._capability_index:
                                self._capability_index[cap_name].discard(agent_id)
                                if not self._capability_index[cap_name]:
                                    del self._capability_index[cap_name]
                    
                    # Remove agent profile
                    self._agents.pop(agent_id, None)
            
            logger.info(f"Unregistered agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    async def update_heartbeat(self, agent_id: str, load: float = None, 
                             status: str = None, metadata: Dict = None) -> bool:
        """Update agent heartbeat and status."""
        try:
            profile = await self.get_agent_profile(agent_id)
            if not profile:
                logger.warning(f"Agent {agent_id} not found for heartbeat update")
                return False
            
            # Update profile with new information
            profile.last_heartbeat = datetime.now().isoformat()
            if load is not None:
                profile.load = load
            if status is not None:
                profile.status = status
            if metadata is not None:
                profile.metadata.update(metadata)
            
            # Store updated profile
            if self.use_redis:
                profile_key = f"{self.registry_prefix}{agent_id}"
                profile_data = json.dumps(profile.to_dict())
                
                self.redis_client.set(profile_key, profile_data)
                self.redis_client.expire(profile_key, self.heartbeat_timeout)
            else:
                with self._lock:
                    self._agents[agent_id] = profile.to_dict()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update heartbeat for {agent_id}: {e}")
            return False
    
    async def discover_agents(self, required_capabilities: List[str] = None,
                            status_filter: str = "active",
                            max_load: float = 0.8,
                            sort_by: str = "load") -> List[AgentProfile]:
        """Discover agents matching the specified criteria."""
        try:
            candidate_agents = set()
            
            if required_capabilities:
                # Find agents with required capabilities
                if self.use_redis:
                    for capability in required_capabilities:
                        cap_key = f"{self.capability_index}{capability}"
                        agents_with_cap = self.redis_client.smembers(cap_key)
                        agents_with_cap = {a.decode() if isinstance(a, bytes) else a for a in agents_with_cap}
                        
                        if not candidate_agents:
                            candidate_agents = agents_with_cap
                        else:
                            # Intersection - agents must have ALL required capabilities
                            candidate_agents = candidate_agents.intersection(agents_with_cap)
                else:
                    with self._lock:
                        for capability in required_capabilities:
                            agents_with_cap = self._capability_index.get(capability, set())
                            
                            if not candidate_agents:
                                candidate_agents = agents_with_cap.copy()
                            else:
                                candidate_agents = candidate_agents.intersection(agents_with_cap)
            else:
                # Get all registered agents
                if self.use_redis:
                    pattern = f"{self.registry_prefix}*"
                    keys = self.redis_client.keys(pattern)
                    candidate_agents = {key.decode().split(':')[-1] for key in keys}
                else:
                    with self._lock:
                        candidate_agents = set(self._agents.keys())
            
            # Filter by status, load, and health
            matching_agents = []
            for agent_id in candidate_agents:
                profile = await self.get_agent_profile(agent_id)
                
                if profile and self._is_agent_alive(profile):
                    # Check if agent meets criteria
                    if (profile.status == status_filter and 
                        profile.load <= max_load):
                        matching_agents.append(profile)
            
            # Sort agents
            if sort_by == "load":
                matching_agents.sort(key=lambda x: x.load)
            elif sort_by == "reliability":
                matching_agents.sort(key=lambda x: max([cap.reliability for cap in x.capabilities] or [0]), reverse=True)
            elif sort_by == "latency":
                matching_agents.sort(key=lambda x: min([cap.latency for cap in x.capabilities] or [float('inf')]))
            
            return matching_agents
            
        except Exception as e:
            logger.error(f"Failed to discover agents: {e}")
            return []
    
    async def get_agent_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get detailed profile for a specific agent."""
        try:
            if self.use_redis:
                profile_key = f"{self.registry_prefix}{agent_id}"
                profile_data = self.redis_client.get(profile_key)
                
                if profile_data:
                    if isinstance(profile_data, bytes):
                        profile_data = profile_data.decode()
                    data = json.loads(profile_data)
                    return AgentProfile.from_dict(data)
            else:
                with self._lock:
                    profile_data = self._agents.get(agent_id)
                    if profile_data:
                        return AgentProfile.from_dict(profile_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get profile for agent {agent_id}: {e}")
            return None
    
    async def get_agents_by_capability(self, capability_name: str) -> List[AgentProfile]:
        """Get all agents that have a specific capability."""
        try:
            agent_ids = set()
            
            if self.use_redis:
                cap_key = f"{self.capability_index}{capability_name}"
                agent_ids = self.redis_client.smembers(cap_key)
                agent_ids = {a.decode() if isinstance(a, bytes) else a for a in agent_ids}
            else:
                with self._lock:
                    agent_ids = self._capability_index.get(capability_name, set()).copy()
            
            agents = []
            for agent_id in agent_ids:
                profile = await self.get_agent_profile(agent_id)
                if profile and self._is_agent_alive(profile):
                    agents.append(profile)
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to get agents by capability {capability_name}: {e}")
            return []
    
    async def get_registry_stats(self) -> Dict[str, any]:
        """Get registry statistics."""
        try:
            stats = {
                "total_agents": 0,
                "active_agents": 0,
                "busy_agents": 0,
                "offline_agents": 0,
                "capabilities": {},
                "average_load": 0.0,
                "last_updated": datetime.now().isoformat()
            }
            
            all_agents = []
            if self.use_redis:
                pattern = f"{self.registry_prefix}*"
                keys = self.redis_client.keys(pattern)
                for key in keys:
                    agent_id = key.decode().split(':')[-1]
                    profile = await self.get_agent_profile(agent_id)
                    if profile:
                        all_agents.append(profile)
            else:
                with self._lock:
                    for agent_id in self._agents:
                        profile = await self.get_agent_profile(agent_id)
                        if profile:
                            all_agents.append(profile)
            
            stats["total_agents"] = len(all_agents)
            
            if all_agents:
                total_load = 0
                for agent in all_agents:
                    total_load += agent.load
                    
                    # Count by status
                    if agent.status == "active":
                        stats["active_agents"] += 1
                    elif agent.status == "busy":
                        stats["busy_agents"] += 1
                    else:
                        stats["offline_agents"] += 1
                    
                    # Count capabilities
                    for cap in agent.capabilities:
                        cap_name = cap.name
                        if cap_name not in stats["capabilities"]:
                            stats["capabilities"][cap_name] = 0
                        stats["capabilities"][cap_name] += 1
                
                stats["average_load"] = total_load / len(all_agents)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get registry stats: {e}")
            return {"error": str(e)}
    
    def _is_agent_alive(self, profile: AgentProfile) -> bool:
        """Check if agent is still alive based on heartbeat."""
        try:
            last_heartbeat = datetime.fromisoformat(profile.last_heartbeat)
            now = datetime.now()
            
            return (now - last_heartbeat).total_seconds() < self.heartbeat_timeout
            
        except Exception:
            return False
    
    async def _periodic_cleanup(self):
        """Periodically clean up dead agents."""
        while self._running:
            try:
                await self.cleanup_dead_agents()
                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def cleanup_dead_agents(self):
        """Remove agents that haven't sent heartbeats."""
        try:
            dead_agents = []
            
            if self.use_redis:
                pattern = f"{self.registry_prefix}*"
                keys = self.redis_client.keys(pattern)
                
                for key in keys:
                    agent_id = key.decode().split(':')[-1]
                    profile = await self.get_agent_profile(agent_id)
                    
                    if profile and not self._is_agent_alive(profile):
                        dead_agents.append(agent_id)
            else:
                with self._lock:
                    for agent_id in list(self._agents.keys()):
                        profile = await self.get_agent_profile(agent_id)
                        
                        if profile and not self._is_agent_alive(profile):
                            dead_agents.append(agent_id)
            
            # Remove dead agents
            for agent_id in dead_agents:
                await self.unregister_agent(agent_id)
                logger.info(f"Cleaned up dead agent: {agent_id}")
            
            if dead_agents:
                logger.info(f"Cleaned up {len(dead_agents)} dead agents")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class AgentRegistryClient:
    """Client interface for agents to interact with the registry."""
    
    def __init__(self, registry: AgentRegistry, agent_profile: AgentProfile):
        self.registry = registry
        self.agent_profile = agent_profile
        self._heartbeat_task = None
        self._running = False
    
    async def start(self):
        """Start the registry client and register the agent."""
        if self._running:
            return
        
        # Register agent
        success = await self.registry.register_agent(self.agent_profile)
        if not success:
            raise Exception(f"Failed to register agent {self.agent_profile.agent_id}")
        
        self._running = True
        
        # Start heartbeat task
        self._heartbeat_task = asyncio.create_task(self._send_heartbeats())
        logger.info(f"Registry client started for agent {self.agent_profile.agent_id}")
    
    async def stop(self):
        """Stop the registry client and unregister the agent."""
        self._running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Unregister agent
        await self.registry.unregister_agent(self.agent_profile.agent_id)
        logger.info(f"Registry client stopped for agent {self.agent_profile.agent_id}")
    
    async def update_status(self, load: float = None, status: str = None, metadata: Dict = None):
        """Update agent status in the registry."""
        if load is not None:
            self.agent_profile.load = load
        if status is not None:
            self.agent_profile.status = status
        if metadata is not None:
            self.agent_profile.metadata.update(metadata)
        
        await self.registry.update_heartbeat(
            self.agent_profile.agent_id,
            load=self.agent_profile.load,
            status=self.agent_profile.status,
            metadata=self.agent_profile.metadata
        )
    
    async def discover_peers(self, required_capabilities: List[str] = None,
                           status_filter: str = "active",
                           max_load: float = 0.8) -> List[AgentProfile]:
        """Discover other agents in the registry."""
        agents = await self.registry.discover_agents(
            required_capabilities=required_capabilities,
            status_filter=status_filter,
            max_load=max_load
        )
        
        # Filter out self
        return [agent for agent in agents if agent.agent_id != self.agent_profile.agent_id]
    
    async def _send_heartbeats(self):
        """Send periodic heartbeats to the registry."""
        while self._running:
            try:
                await self.registry.update_heartbeat(
                    self.agent_profile.agent_id,
                    load=self.agent_profile.load,
                    status=self.agent_profile.status,
                    metadata=self.agent_profile.metadata
                )
                await asyncio.sleep(self.registry.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                await asyncio.sleep(self.registry.heartbeat_interval)