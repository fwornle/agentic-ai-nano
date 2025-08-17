"""
Message Router Implementation

This module provides message routing functionality for A2A communication,
handling message delivery, response correlation, and broadcast capabilities.
"""

import asyncio
import json
from typing import Dict, List, Optional, Callable, Any, Union
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass

# For production, use aiohttp. For development/testing, use mock transport
try:
    import aiohttp
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

from .protocol import A2AMessage, MessageType, Priority, AgentProfile
from .agent_registry import AgentRegistry

logger = logging.getLogger(__name__)


@dataclass
class RoutingRule:
    """Defines a message routing rule."""
    name: str
    condition: Callable[[A2AMessage], bool]
    target_agent_id: str = None
    target_capability: str = None
    priority: int = 1
    description: str = ""


class MessageTransport:
    """Abstract base class for message transport implementations."""
    
    async def send_message(self, message: A2AMessage, endpoint: str) -> Optional[A2AMessage]:
        """Send a message to an endpoint and optionally wait for response."""
        raise NotImplementedError
    
    async def start(self):
        """Start the transport."""
        pass
    
    async def stop(self):
        """Stop the transport."""
        pass


class HTTPMessageTransport(MessageTransport):
    """HTTP-based message transport."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        """Start the HTTP transport."""
        if HTTP_AVAILABLE:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        else:
            logger.warning("aiohttp not available, using mock transport")
    
    async def stop(self):
        """Stop the HTTP transport."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def send_message(self, message: A2AMessage, endpoint: str) -> Optional[A2AMessage]:
        """Send message via HTTP POST."""
        if not self.session:
            # Mock response for testing
            return self._create_mock_response(message)
        
        try:
            url = f"{endpoint.rstrip('/')}/a2a/message"
            
            async with self.session.post(
                url,
                json=message.to_dict(),
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    response_data = await response.json()
                    
                    # Handle response if this was a request
                    if message.requires_response:
                        return A2AMessage.from_dict(response_data)
                    else:
                        return None
                else:
                    logger.error(f"HTTP error {response.status} sending to {endpoint}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error sending HTTP message to {endpoint}: {e}")
            return None
    
    def _create_mock_response(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Create a mock response for testing when HTTP is not available."""
        if not message.requires_response:
            return None
        
        return A2AMessage(
            message_type=MessageType.RESPONSE,
            correlation_id=message.message_id,
            sender_id="mock_agent",
            recipient_id=message.sender_id,
            payload={
                "status": "mock_response",
                "message": "This is a mock response for testing",
                "success": True
            }
        )


class InMemoryMessageTransport(MessageTransport):
    """In-memory message transport for testing and development."""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.message_log: List[Dict] = []
    
    def register_handler(self, agent_id: str, handler: Callable):
        """Register a message handler for an agent."""
        self.handlers[agent_id] = handler
    
    async def send_message(self, message: A2AMessage, endpoint: str) -> Optional[A2AMessage]:
        """Send message via in-memory delivery."""
        # Extract agent_id from endpoint (assume format: agent://agent_id)
        if endpoint.startswith("agent://"):
            agent_id = endpoint[8:]
        else:
            agent_id = endpoint
        
        # Log message
        self.message_log.append({
            "timestamp": datetime.now().isoformat(),
            "message": message.to_dict(),
            "endpoint": endpoint,
            "agent_id": agent_id
        })
        
        # Deliver to handler if available
        if agent_id in self.handlers:
            try:
                handler = self.handlers[agent_id]
                result = await handler(message)
                
                if message.requires_response and isinstance(result, dict):
                    return A2AMessage(
                        message_type=MessageType.RESPONSE,
                        correlation_id=message.message_id,
                        sender_id=agent_id,
                        recipient_id=message.sender_id,
                        payload=result
                    )
            except Exception as e:
                logger.error(f"Error in message handler for {agent_id}: {e}")
        
        return None


class MessageRouter:
    """Routes messages between agents in an A2A network."""
    
    def __init__(self, registry: AgentRegistry, transport: MessageTransport = None):
        self.registry = registry
        self.transport = transport or InMemoryMessageTransport()
        
        self.message_handlers: Dict[str, Callable] = {}
        self.routing_rules: List[RoutingRule] = []
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        
        # Message statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_failed": 0,
            "broadcasts_sent": 0,
            "responses_matched": 0
        }
        
        # Background tasks
        self._processor_task = None
        self._running = False
    
    async def start(self):
        """Start the message router."""
        if self._running:
            return
        
        self._running = True
        await self.transport.start()
        self._processor_task = asyncio.create_task(self._process_messages())
        logger.info("Message router started")
    
    async def stop(self):
        """Stop the message router."""
        self._running = False
        
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        await self.transport.stop()
        
        # Cancel pending requests
        for future in self.pending_requests.values():
            if not future.done():
                future.cancel()
        self.pending_requests.clear()
        
        logger.info("Message router stopped")
    
    def register_handler(self, action: str, handler: Callable):
        """Register a message handler for a specific action."""
        self.message_handlers[action] = handler
        logger.info(f"Registered handler for action: {action}")
    
    def add_routing_rule(self, rule: RoutingRule):
        """Add a routing rule."""
        self.routing_rules.append(rule)
        # Sort by priority (higher priority first)
        self.routing_rules.sort(key=lambda x: x.priority, reverse=True)
        logger.info(f"Added routing rule: {rule.name}")
    
    async def send_message(self, message: A2AMessage, 
                         wait_for_response: bool = None) -> Optional[A2AMessage]:
        """Send a message to another agent."""
        
        if wait_for_response is None:
            wait_for_response = message.requires_response
        
        try:
            # Add to message queue for processing
            await self.message_queue.put(message)
            
            # If response is required, wait for it
            if wait_for_response:
                future = asyncio.Future()
                self.pending_requests[message.message_id] = future
                
                try:
                    response = await asyncio.wait_for(future, timeout=message.timeout)
                    self.stats["responses_matched"] += 1
                    return response
                except asyncio.TimeoutError:
                    logger.warning(f"Message {message.message_id} timed out")
                    return None
                finally:
                    self.pending_requests.pop(message.message_id, None)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.stats["messages_failed"] += 1
            return None
    
    async def broadcast_message(self, message: A2AMessage, 
                              capability_filter: List[str] = None,
                              status_filter: str = "active",
                              max_recipients: int = None) -> int:
        """Broadcast a message to multiple agents."""
        
        # Discover target agents
        agents = await self.registry.discover_agents(
            required_capabilities=capability_filter,
            status_filter=status_filter
        )
        
        if max_recipients:
            agents = agents[:max_recipients]
        
        sent_count = 0
        tasks = []
        
        for agent in agents:
            # Create individual message for each agent
            agent_message = A2AMessage(
                message_type=MessageType.BROADCAST,
                sender_id=message.sender_id,
                recipient_id=agent.agent_id,
                action=message.action,
                payload=message.payload.copy(),
                priority=message.priority
            )
            
            # Send message asynchronously
            task = asyncio.create_task(self._route_message(agent_message))
            tasks.append(task)
        
        # Wait for all messages to be sent
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                sent_count += 1
            else:
                logger.error(f"Failed to send broadcast to {agents[i].agent_id}: {result}")
        
        self.stats["broadcasts_sent"] += 1
        logger.info(f"Broadcast sent to {sent_count}/{len(agents)} agents")
        return sent_count
    
    async def _process_messages(self):
        """Process messages from the queue."""
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                await self._route_message(message)
                self.message_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def _route_message(self, message: A2AMessage):
        """Route a message to its destination."""
        try:
            target_agent = None
            
            # Check routing rules first
            for rule in self.routing_rules:
                if rule.condition(message):
                    if rule.target_agent_id:
                        target_agent = await self.registry.get_agent_profile(rule.target_agent_id)
                    elif rule.target_capability:
                        agents = await self.registry.discover_agents(
                            required_capabilities=[rule.target_capability]
                        )
                        if agents:
                            target_agent = agents[0]  # Use best available
                    break
            
            # If no routing rule matched, use message routing information
            if not target_agent:
                if message.recipient_id:
                    # Direct message to specific agent
                    target_agent = await self.registry.get_agent_profile(message.recipient_id)
                else:
                    # Discover suitable agents
                    agents = await self.registry.discover_agents(
                        required_capabilities=message.capabilities_required
                    )
                    
                    if agents:
                        target_agent = agents[0]  # Use best available agent (lowest load)
            
            # Send message to target agent
            if target_agent:
                await self._send_to_agent(message, target_agent)
            else:
                logger.warning(f"No suitable agent found for message {message.message_id}")
                self.stats["messages_failed"] += 1
                
        except Exception as e:
            logger.error(f"Error routing message {message.message_id}: {e}")
            self.stats["messages_failed"] += 1
    
    async def _send_to_agent(self, message: A2AMessage, target_agent: AgentProfile):
        """Send message to a specific agent."""
        try:
            response = await self.transport.send_message(message, target_agent.endpoint)
            
            self.stats["messages_sent"] += 1
            
            # Handle response if this was a request
            if response and message.requires_response:
                await self._handle_response(response)
            
        except Exception as e:
            logger.error(f"Error sending message to {target_agent.agent_id}: {e}")
            self.stats["messages_failed"] += 1
    
    async def _handle_response(self, response: A2AMessage):
        """Handle a response message."""
        
        # Check if we have a pending request for this response
        correlation_id = response.correlation_id
        
        if correlation_id in self.pending_requests:
            future = self.pending_requests[correlation_id]
            if not future.done():
                future.set_result(response)
    
    async def handle_incoming_message(self, message_data: Union[Dict[str, Any], A2AMessage]) -> Dict[str, Any]:
        """Handle an incoming message from another agent."""
        
        try:
            if isinstance(message_data, dict):
                message = A2AMessage.from_dict(message_data)
            else:
                message = message_data
            
            self.stats["messages_received"] += 1
            
            # Check if this is a response to our request
            if message.message_type == MessageType.RESPONSE:
                await self._handle_response(message)
                return {"status": "response_processed"}
            
            # Handle the message using registered handlers
            if message.action in self.message_handlers:
                handler = self.message_handlers[message.action]
                result = await handler(message)
                
                # Send response if required
                if message.requires_response:
                    response = A2AMessage(
                        message_type=MessageType.RESPONSE,
                        correlation_id=message.message_id,
                        sender_id=message.recipient_id,
                        recipient_id=message.sender_id,
                        payload=result if isinstance(result, dict) else {"result": result}
                    )
                    
                    return response.to_dict()
                
                return {"status": "message_processed"}
            else:
                logger.warning(f"No handler for action: {message.action}")
                return {"error": f"No handler for action: {message.action}"}
                
        except Exception as e:
            logger.error(f"Error handling incoming message: {e}")
            self.stats["messages_failed"] += 1
            return {"error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message routing statistics."""
        return {
            **self.stats,
            "pending_requests": len(self.pending_requests),
            "queue_size": self.message_queue.qsize(),
            "active_rules": len(self.routing_rules),
            "registered_handlers": len(self.message_handlers),
            "last_updated": datetime.now().isoformat()
        }
    
    def create_message_filter(self, **kwargs) -> Callable[[A2AMessage], bool]:
        """Create a message filter function for routing rules."""
        def filter_func(message: A2AMessage) -> bool:
            for key, value in kwargs.items():
                if hasattr(message, key):
                    msg_value = getattr(message, key)
                    if isinstance(value, list):
                        if msg_value not in value:
                            return False
                    elif msg_value != value:
                        return False
                elif key == "payload_contains":
                    if not any(k in message.payload for k in value):
                        return False
                elif key == "capability_matches":
                    if not any(cap in message.capabilities_required for cap in value):
                        return False
            return True
        
        return filter_func


# Utility functions for creating common routing rules
def create_priority_routing_rule(name: str, priority_level: Priority, 
                               target_capability: str) -> RoutingRule:
    """Create a routing rule based on message priority."""
    return RoutingRule(
        name=name,
        condition=lambda msg: msg.priority == priority_level,
        target_capability=target_capability,
        priority=10,
        description=f"Route {priority_level.name} priority messages to {target_capability}"
    )


def create_capability_routing_rule(name: str, required_capability: str,
                                 target_capability: str) -> RoutingRule:
    """Create a routing rule based on required capabilities."""
    return RoutingRule(
        name=name,
        condition=lambda msg: required_capability in msg.capabilities_required,
        target_capability=target_capability,
        priority=5,
        description=f"Route messages requiring {required_capability} to {target_capability}"
    )


def create_action_routing_rule(name: str, action: str, 
                             target_agent_id: str = None,
                             target_capability: str = None) -> RoutingRule:
    """Create a routing rule based on message action."""
    return RoutingRule(
        name=name,
        condition=lambda msg: msg.action == action,
        target_agent_id=target_agent_id,
        target_capability=target_capability,
        priority=7,
        description=f"Route {action} actions to specific target"
    )


def create_sender_routing_rule(name: str, sender_id: str,
                             target_capability: str) -> RoutingRule:
    """Create a routing rule based on message sender."""
    return RoutingRule(
        name=name,
        condition=lambda msg: msg.sender_id == sender_id,
        target_capability=target_capability,
        priority=3,
        description=f"Route messages from {sender_id} to {target_capability}"
    )


# Example usage and testing utilities
async def test_message_routing():
    """Test the message routing functionality."""
    from .agent_registry import AgentRegistry
    
    # Create registry (using in-memory storage for testing)
    registry = AgentRegistry(use_redis=False)
    await registry.start()
    
    # Create transport and router
    transport = InMemoryMessageTransport()
    router = MessageRouter(registry, transport)
    
    # Add some routing rules
    router.add_routing_rule(create_priority_routing_rule(
        "urgent_to_support", Priority.URGENT, "customer_support"
    ))
    router.add_routing_rule(create_action_routing_rule(
        "help_requests", "help_request", target_capability="customer_support"
    ))
    
    await router.start()
    
    print("Message router test completed successfully")
    
    await router.stop()
    await registry.stop()