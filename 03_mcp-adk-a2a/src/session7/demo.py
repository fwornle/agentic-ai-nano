#!/usr/bin/env python3
"""
A2A Communication System Demonstration

This script demonstrates the complete A2A communication system with:
- Agent registration and discovery
- Message routing and choreography
- Multi-agent coordination scenarios

Run this script to see the A2A system in action.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import A2A system components
from a2a.protocol import create_request_message, Priority
from a2a.agent_registry import AgentRegistry
from a2a.message_router import MessageRouter, InMemoryMessageTransport
from agents.customer_service import CustomerServiceAgent
from agents.technical_support import TechnicalSupportAgent
from coordination.choreography import ChoreographyEngine, create_hybrid_choreography
from config import create_sample_config, setup_logging


class A2ADemoSystem:
    """Demonstration of the A2A communication system."""
    
    def __init__(self):
        self.registry = None
        self.router = None
        self.choreography = None
        self.agents = {}
        self.config = create_sample_config()
        
    async def initialize(self):
        """Initialize the A2A system components."""
        
        logger.info("Initializing A2A Demo System...")
        
        # Setup logging
        setup_logging(self.config.logging)
        
        # Initialize registry (using in-memory for demo)
        self.registry = AgentRegistry(use_redis=False)
        await self.registry.start()
        
        # Initialize message router with in-memory transport
        transport = InMemoryMessageTransport()
        self.router = MessageRouter(self.registry, transport)
        await self.router.start()
        
        # Initialize choreography engine
        self.choreography = create_hybrid_choreography(self.router, self.registry)
        await self.choreography.start()
        
        logger.info("A2A system initialized successfully")
    
    async def create_agents(self):
        """Create and start demonstration agents."""
        
        logger.info("Creating demonstration agents...")
        
        # Create customer service agents
        cs_agent1 = CustomerServiceAgent("cs_agent_001", "Customer Service Agent 1")
        cs_agent2 = CustomerServiceAgent("cs_agent_002", "Customer Service Agent 2") 
        
        # Create technical support agents
        tech_agent1 = TechnicalSupportAgent("tech_agent_001", "Technical Support Agent 1", 
                                           specializations=["api_integration", "database_optimization"])
        tech_agent2 = TechnicalSupportAgent("tech_agent_002", "Technical Support Agent 2",
                                           specializations=["network_security", "performance_tuning"])
        
        # Start all agents
        agents = [cs_agent1, cs_agent2, tech_agent1, tech_agent2]
        
        for agent in agents:
            await agent.start(self.registry, self.router)
            self.agents[agent.agent_id] = agent
            logger.info(f"Started agent: {agent.name} ({agent.agent_id})")
        
        # Wait for agents to register
        await asyncio.sleep(1)
        
        # Display registry stats
        stats = await self.registry.get_registry_stats()
        logger.info(f"Registry stats: {json.dumps(stats, indent=2)}")
    
    async def demonstrate_agent_discovery(self):
        """Demonstrate agent discovery functionality."""
        
        logger.info("\n" + "="*50)
        logger.info("DEMONSTRATION: Agent Discovery")
        logger.info("="*50)
        
        # Discover all agents
        all_agents = await self.registry.discover_agents()
        logger.info(f"Discovered {len(all_agents)} total agents")
        
        for agent in all_agents:
            logger.info(f"  - {agent.name} ({agent.agent_id}): {[cap.name for cap in agent.capabilities]}")
        
        # Discover agents by capability
        customer_support_agents = await self.registry.discover_agents(
            required_capabilities=["customer_inquiry_handling"]
        )
        logger.info(f"\nFound {len(customer_support_agents)} customer support agents")
        
        technical_support_agents = await self.registry.discover_agents(
            required_capabilities=["technical_support"]
        )
        logger.info(f"Found {len(technical_support_agents)} technical support agents")
        
        # Discover specialists
        api_specialists = await self.registry.discover_agents(
            required_capabilities=["api_integration_specialist"]
        )
        logger.info(f"Found {len(api_specialists)} API integration specialists")
    
    async def demonstrate_direct_messaging(self):
        """Demonstrate direct agent-to-agent messaging."""
        
        logger.info("\n" + "="*50)
        logger.info("DEMONSTRATION: Direct Agent Messaging")
        logger.info("="*50)
        
        # Send a customer inquiry to customer service
        cs_agents = await self.registry.discover_agents(
            required_capabilities=["customer_inquiry_handling"]
        )
        
        if cs_agents:
            target_agent = cs_agents[0]
            
            message = create_request_message(
                sender_id="demo_system",
                action="handle_inquiry",
                payload={
                    "inquiry": "I'm having trouble logging into my account. It says my password is incorrect but I'm sure it's right.",
                    "customer_id": "customer_12345",
                    "priority": "normal",
                    "category": "authentication"
                },
                recipient_id=target_agent.agent_id,
                priority=Priority.NORMAL,
                requires_response=True,
                timeout=30
            )
            
            logger.info(f"Sending inquiry to {target_agent.name}...")
            response = await self.router.send_message(message, wait_for_response=True)
            
            if response:
                logger.info("Received response:")
                logger.info(f"  Ticket ID: {response.payload.get('ticket_id')}")
                logger.info(f"  Response: {response.payload.get('response')}")
                logger.info(f"  Escalation needed: {response.payload.get('escalation_needed')}")
            else:
                logger.error("No response received")
    
    async def demonstrate_choreography(self):
        """Demonstrate event-driven choreography."""
        
        logger.info("\n" + "="*50)
        logger.info("DEMONSTRATION: Event-Driven Choreography")
        logger.info("="*50)
        
        # Publish a customer inquiry event
        await self.choreography.publish_event(
            event_type="customer_inquiry",
            event_data={
                "customer_id": "customer_54321",
                "subject": "API integration not working",
                "description": "Our API calls are failing with 500 errors since yesterday",
                "category": "technical",
                "priority": "high",
                "customer_tier": "enterprise"
            },
            source_agent="demo_system"
        )
        
        logger.info("Published customer inquiry event - choreography should trigger routing")
        
        # Wait for choreography to process
        await asyncio.sleep(2)
        
        # Publish a technical issue event
        await self.choreography.publish_event(
            event_type="technical_issue",
            event_data={
                "issue_description": "Database connection timeouts in production",
                "severity": "critical",
                "category": "database",
                "customer_id": "customer_98765",
                "system_info": {
                    "environment": "production",
                    "database": "postgresql",
                    "version": "14.2"
                }
            },
            source_agent="monitoring_system"
        )
        
        logger.info("Published critical technical issue event")
        
        # Wait for processing
        await asyncio.sleep(2)
    
    async def demonstrate_escalation_workflow(self):
        """Demonstrate escalation workflow between agents."""
        
        logger.info("\n" + "="*50)
        logger.info("DEMONSTRATION: Escalation Workflow")
        logger.info("="*50)
        
        # Create a complex technical issue that will need escalation
        cs_agents = await self.registry.discover_agents(
            required_capabilities=["customer_inquiry_handling"]
        )
        
        if cs_agents:
            cs_agent = cs_agents[0]
            
            # Send complex technical inquiry
            message = create_request_message(
                sender_id="demo_system",
                action="handle_inquiry",
                payload={
                    "inquiry": "Our entire API is down, database connections are failing, and we're getting security alerts. This is affecting all our enterprise customers and we need immediate help!",
                    "customer_id": "enterprise_customer_001",
                    "priority": "urgent",
                    "category": "technical",
                    "system_info": {
                        "environment": "production",
                        "errors": ["connection_timeout", "ssl_certificate_expired", "database_lock"]
                    }
                },
                recipient_id=cs_agent.agent_id,
                priority=Priority.URGENT,
                requires_response=True
            )
            
            logger.info("Sending complex technical issue that should trigger escalation...")
            response = await self.router.send_message(message)
            
            if response:
                logger.info("Response received:")
                logger.info(f"  Escalation needed: {response.payload.get('escalation_needed')}")
                logger.info(f"  Escalation type: {response.payload.get('escalation_type')}")
                
                # Wait for escalation to process
                await asyncio.sleep(3)
        
        # Check agent metrics
        await self.show_agent_metrics()
    
    async def demonstrate_load_balancing(self):
        """Demonstrate load balancing across agents."""
        
        logger.info("\n" + "="*50)
        logger.info("DEMONSTRATION: Load Balancing")
        logger.info("="*50)
        
        # Send multiple inquiries to see load distribution
        inquiries = [
            {"inquiry": "How do I reset my password?", "customer_id": f"customer_{i}", "category": "account"}
            for i in range(5)
        ]
        
        tasks = []
        for inquiry in inquiries:
            message = create_request_message(
                sender_id="demo_system",
                action="handle_inquiry",
                payload=inquiry,
                capabilities_required=["customer_inquiry_handling"],
                priority=Priority.NORMAL
            )
            
            task = asyncio.create_task(self.router.send_message(message))
            tasks.append(task)
        
        logger.info(f"Sending {len(inquiries)} inquiries simultaneously...")
        await asyncio.gather(*tasks)
        
        # Show load distribution
        await asyncio.sleep(1)
        await self.show_agent_metrics()
    
    async def show_agent_metrics(self):
        """Display metrics for all agents."""
        
        logger.info("\n" + "="*30)
        logger.info("AGENT METRICS")
        logger.info("="*30)
        
        for agent_id, agent in self.agents.items():
            metrics = agent.get_metrics()
            logger.info(f"\n{agent.name} ({agent_id}):")
            logger.info(f"  Tickets/Issues Handled: {metrics.get('tickets_handled', metrics.get('issues_handled', 0))}")
            logger.info(f"  Resolved: {metrics.get('tickets_resolved', metrics.get('issues_resolved', 0))}")
            logger.info(f"  Escalated: {metrics.get('tickets_escalated', metrics.get('issues_escalated', 0))}")
            logger.info(f"  Current Load: {agent.agent_profile.load:.2f}")
            
            if 'average_resolution_time' in metrics:
                logger.info(f"  Avg Resolution Time: {metrics['average_resolution_time']:.2f} min")
            
            if 'customer_satisfaction' in metrics:
                logger.info(f"  Customer Satisfaction: {metrics['customer_satisfaction']:.2f}/5.0")
    
    async def show_system_statistics(self):
        """Display overall system statistics."""
        
        logger.info("\n" + "="*30)
        logger.info("SYSTEM STATISTICS")
        logger.info("="*30)
        
        # Registry statistics
        registry_stats = await self.registry.get_registry_stats()
        logger.info(f"\nRegistry Statistics:")
        logger.info(f"  Total Agents: {registry_stats['total_agents']}")
        logger.info(f"  Active Agents: {registry_stats['active_agents']}")
        logger.info(f"  Average Load: {registry_stats['average_load']:.2f}")
        logger.info(f"  Capabilities: {registry_stats['capabilities']}")
        
        # Router statistics
        router_stats = self.router.get_stats()
        logger.info(f"\nRouter Statistics:")
        logger.info(f"  Messages Sent: {router_stats['messages_sent']}")
        logger.info(f"  Messages Received: {router_stats['messages_received']}")
        logger.info(f"  Messages Failed: {router_stats['messages_failed']}")
        logger.info(f"  Broadcasts Sent: {router_stats['broadcasts_sent']}")
        logger.info(f"  Responses Matched: {router_stats['responses_matched']}")
        
        # Choreography statistics
        choreography_stats = self.choreography.get_stats()
        logger.info(f"\nChoreography Statistics:")
        logger.info(f"  Events Published: {choreography_stats['events_published']}")
        logger.info(f"  Events Processed: {choreography_stats['events_processed']}")
        logger.info(f"  Patterns Triggered: {choreography_stats['patterns_triggered']}")
        logger.info(f"  Actions Executed: {choreography_stats['actions_executed']}")
        logger.info(f"  Active Patterns: {choreography_stats['active_patterns']}")
    
    async def cleanup(self):
        """Clean up system resources."""
        
        logger.info("\nCleaning up A2A system...")
        
        # Stop agents
        for agent in self.agents.values():
            await agent.stop()
        
        # Stop system components
        if self.choreography:
            await self.choreography.stop()
        
        if self.router:
            await self.router.stop()
        
        if self.registry:
            await self.registry.stop()
        
        logger.info("Cleanup completed")


async def run_demo():
    """Run the complete A2A system demonstration."""
    
    demo = A2ADemoSystem()
    
    try:
        # Initialize system
        await demo.initialize()
        await demo.create_agents()
        
        # Run demonstrations
        await demo.demonstrate_agent_discovery()
        await asyncio.sleep(1)
        
        await demo.demonstrate_direct_messaging()
        await asyncio.sleep(1)
        
        await demo.demonstrate_choreography()
        await asyncio.sleep(2)
        
        await demo.demonstrate_escalation_workflow()
        await asyncio.sleep(1)
        
        await demo.demonstrate_load_balancing()
        await asyncio.sleep(1)
        
        # Show final statistics
        await demo.show_system_statistics()
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise
    
    finally:
        await demo.cleanup()


def main():
    """Main entry point for the demonstration."""
    
    print("\n" + "="*60)
    print("A2A COMMUNICATION SYSTEM DEMONSTRATION")
    print("="*60)
    print("This demo shows agent-to-agent communication with:")
    print("- Service discovery and registration")
    print("- Direct messaging between agents")  
    print("- Event-driven choreography patterns")
    print("- Automatic escalation workflows")
    print("- Load balancing and coordination")
    print("="*60 + "\n")
    
    try:
        asyncio.run(run_demo())
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("Key Features Demonstrated:")
        print("✓ Agent registration and discovery")
        print("✓ Message routing and delivery") 
        print("✓ Event-driven choreography")
        print("✓ Multi-agent coordination")
        print("✓ Automatic escalation")
        print("✓ Load balancing")
        print("✓ System monitoring and metrics")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        logger.exception("Demo error details:")


if __name__ == "__main__":
    main()