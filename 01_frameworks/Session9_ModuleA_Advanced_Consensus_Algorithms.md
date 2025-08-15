# Session 9 - Module A: Advanced Consensus Algorithms (70 minutes)

**Prerequisites**: [Session 9 Core Section Complete](Session9_Multi_Agent_Patterns.md)  
**Target Audience**: System architects building robust coordination systems  
**Cognitive Load**: 6 advanced concepts

---

## 🎯 Module Overview

This module explores sophisticated consensus algorithms for multi-agent systems including Byzantine Fault Tolerance, Practical Byzantine Fault Tolerance (pBFT), game-theoretic conflict resolution, auction mechanisms, and strategic behavior analysis. You'll learn to build robust multi-agent systems that can handle adversarial conditions and competitive scenarios.

### Learning Objectives
By the end of this module, you will:
- Implement Byzantine Fault Tolerance algorithms with mathematical guarantees
- Design game-theoretic solutions for competitive multi-agent scenarios
- Create auction-based coordination mechanisms with strategic behavior analysis
- Build resilient consensus systems that handle malicious agents and network failures

---

## Part 1: Byzantine Fault Tolerance Implementation (35 minutes)

### Practical Byzantine Fault Tolerance (pBFT)

🗂️ **File**: `src/session9/byzantine_consensus.py` - Byzantine fault tolerance algorithms

```python
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import hashlib
import json
import logging
from collections import defaultdict, Counter

class MessageType(Enum):
    """Byzantine consensus message types"""
    REQUEST = "request"
    PREPARE = "prepare" 
    COMMIT = "commit"
    REPLY = "reply"
    VIEW_CHANGE = "view_change"
    NEW_VIEW = "new_view"
    CHECKPOINT = "checkpoint"

@dataclass
class ByzantineMessage:
    """Message format for Byzantine consensus protocol"""
    msg_type: MessageType
    view: int
    sequence: int
    digest: str
    sender: str
    timestamp: datetime = field(default_factory=datetime.now)
    payload: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None

class ByzantineNode:
    """Byzantine fault tolerant node implementing pBFT"""
    
    def __init__(self, node_id: str, total_nodes: int, byzantine_threshold: int = None):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.byzantine_threshold = byzantine_threshold or (total_nodes - 1) // 3
        self.view = 0
        self.sequence = 0
        self.is_primary = False
        
        # Message logs for different phases
        self.request_log: Dict[str, ByzantineMessage] = {}
        self.prepare_log: Dict[str, Dict[str, ByzantineMessage]] = defaultdict(dict)
        self.commit_log: Dict[str, Dict[str, ByzantineMessage]] = defaultdict(dict)
        self.reply_log: Dict[str, List[ByzantineMessage]] = defaultdict(list)
        
        # State management
        self.executed_requests: Set[str] = set()
        self.current_state: Dict[str, Any] = {}
        self.checkpoint_log: Dict[int, Dict[str, Any]] = {}
        
        # Network simulation
        self.message_handlers = {
            MessageType.REQUEST: self._handle_request,
            MessageType.PREPARE: self._handle_prepare,
            MessageType.COMMIT: self._handle_commit,
            MessageType.REPLY: self._handle_reply,
            MessageType.VIEW_CHANGE: self._handle_view_change,
        }
        
        self.logger = logging.getLogger(f"ByzantineNode-{node_id}")
        
    async def process_client_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process client request through Byzantine consensus"""
        
        # Create request message
        request_digest = self._compute_digest(request)
        request_msg = ByzantineMessage(
            msg_type=MessageType.REQUEST,
            view=self.view,
            sequence=self.sequence,
            digest=request_digest,
            sender="client",
            payload=request
        )
        
        # If this node is primary, initiate consensus
        if self.is_primary:
            return await self._initiate_consensus(request_msg)
        else:
            # Forward to primary or handle as backup
            return await self._forward_to_primary(request_msg)
    
    async def _initiate_consensus(self, request: ByzantineMessage) -> Dict[str, Any]:
        """Primary node initiates three-phase consensus"""
        
        self.logger.info(f"Primary {self.node_id} initiating consensus for request {request.digest}")
        
        # Phase 1: Prepare phase
        prepare_msg = ByzantineMessage(
            msg_type=MessageType.PREPARE,
            view=self.view,
            sequence=self.sequence,
            digest=request.digest,
            sender=self.node_id,
            payload={"request": request.payload}
        )
        
        # Store request and prepare message
        self.request_log[request.digest] = request
        self.prepare_log[request.digest][self.node_id] = prepare_msg
        
        # Broadcast prepare to all nodes
        prepare_responses = await self._broadcast_and_collect_responses(
            prepare_msg, MessageType.PREPARE, 
            required_responses=2 * self.byzantine_threshold
        )
        
        if not prepare_responses['success']:
            return {
                'success': False,
                'phase': 'prepare',
                'error': 'Insufficient prepare responses'
            }
        
        # Phase 2: Commit phase
        commit_msg = ByzantineMessage(
            msg_type=MessageType.COMMIT,
            view=self.view,
            sequence=self.sequence,
            digest=request.digest,
            sender=self.node_id
        )
        
        # Store commit message
        self.commit_log[request.digest][self.node_id] = commit_msg
        
        # Broadcast commit to all nodes
        commit_responses = await self._broadcast_and_collect_responses(
            commit_msg, MessageType.COMMIT,
            required_responses=2 * self.byzantine_threshold
        )
        
        if not commit_responses['success']:
            return {
                'success': False,
                'phase': 'commit', 
                'error': 'Insufficient commit responses'
            }
        
        # Phase 3: Execute and reply
        execution_result = await self._execute_request(request)
        
        # Generate reply
        reply_msg = ByzantineMessage(
            msg_type=MessageType.REPLY,
            view=self.view,
            sequence=self.sequence,
            digest=request.digest,
            sender=self.node_id,
            payload=execution_result
        )
        
        self.reply_log[request.digest].append(reply_msg)
        self.sequence += 1
        
        return {
            'success': True,
            'request_digest': request.digest,
            'execution_result': execution_result,
            'consensus_phases': {
                'prepare': prepare_responses,
                'commit': commit_responses
            }
        }
    
    async def _broadcast_and_collect_responses(self, message: ByzantineMessage, 
                                            expected_type: MessageType,
                                            required_responses: int) -> Dict[str, Any]:
        """Broadcast message and collect required responses"""
        
        # Simulate network broadcast and response collection
        responses = []
        timeout = timedelta(seconds=10)
        start_time = datetime.now()
        
        # In a real implementation, this would use actual network communication
        # Here we simulate the consensus process
        simulated_responses = await self._simulate_network_responses(
            message, expected_type, required_responses
        )
        
        return {
            'success': len(simulated_responses) >= required_responses,
            'responses': simulated_responses,
            'response_count': len(simulated_responses),
            'required': required_responses
        }
    
    async def _simulate_network_responses(self, message: ByzantineMessage,
                                        expected_type: MessageType,
                                        required_count: int) -> List[ByzantineMessage]:
        """Simulate network responses for demonstration"""
        
        responses = []
        
        # Simulate honest nodes responding
        for i in range(min(required_count + 1, self.total_nodes - 1)):
            if i == int(self.node_id):  # Skip self
                continue
                
            response = ByzantineMessage(
                msg_type=expected_type,
                view=message.view,
                sequence=message.sequence, 
                digest=message.digest,
                sender=f"node_{i}",
                payload={"agreement": True, "original_sender": message.sender}
            )
            responses.append(response)
            
            # Store response in appropriate log
            if expected_type == MessageType.PREPARE:
                self.prepare_log[message.digest][response.sender] = response
            elif expected_type == MessageType.COMMIT:
                self.commit_log[message.digest][response.sender] = response
        
        return responses
    
    async def _execute_request(self, request: ByzantineMessage) -> Dict[str, Any]:
        """Execute the agreed-upon request"""
        
        if request.digest in self.executed_requests:
            return {'status': 'already_executed', 'digest': request.digest}
        
        # Simulate request execution based on payload
        execution_result = {
            'status': 'executed',
            'request_digest': request.digest,
            'execution_time': datetime.now().isoformat(),
            'result': f"Executed operation: {request.payload}",
            'state_changes': self._apply_state_changes(request.payload)
        }
        
        # Mark as executed
        self.executed_requests.add(request.digest)
        
        self.logger.info(f"Executed request {request.digest}")
        
        return execution_result
    
    def _apply_state_changes(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply state changes from executed operation"""
        
        state_changes = {}
        
        # Simple state machine for demonstration
        if operation.get('type') == 'set_value':
            key = operation.get('key')
            value = operation.get('value')
            if key and value is not None:
                old_value = self.current_state.get(key)
                self.current_state[key] = value
                state_changes[key] = {'old': old_value, 'new': value}
        
        elif operation.get('type') == 'increment':
            key = operation.get('key', 'counter')
            increment = operation.get('amount', 1)
            old_value = self.current_state.get(key, 0)
            new_value = old_value + increment
            self.current_state[key] = new_value
            state_changes[key] = {'old': old_value, 'new': new_value}
        
        return state_changes
    
    def _compute_digest(self, data: Any) -> str:
        """Compute cryptographic digest of data"""
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]
    
    async def handle_view_change(self, suspected_faulty_primary: str) -> Dict[str, Any]:
        """Handle view change when primary is suspected to be faulty"""
        
        self.logger.warning(f"Initiating view change due to suspected faulty primary: {suspected_faulty_primary}")
        
        new_view = self.view + 1
        
        view_change_msg = ByzantineMessage(
            msg_type=MessageType.VIEW_CHANGE,
            view=new_view,
            sequence=self.sequence,
            digest="view_change",
            sender=self.node_id,
            payload={
                'suspected_primary': suspected_faulty_primary,
                'last_executed_sequence': max(self.executed_requests) if self.executed_requests else 0,
                'prepare_log_summary': self._summarize_prepare_log(),
                'commit_log_summary': self._summarize_commit_log()
            }
        )
        
        # Collect view change messages from 2f+1 nodes
        view_change_responses = await self._broadcast_and_collect_responses(
            view_change_msg, MessageType.VIEW_CHANGE,
            required_responses=2 * self.byzantine_threshold
        )
        
        if view_change_responses['success']:
            # Elect new primary
            new_primary_id = self._elect_new_primary(new_view)
            
            if new_primary_id == self.node_id:
                self.is_primary = True
                self.view = new_view
                
                # Send NEW-VIEW message
                new_view_result = await self._send_new_view_message(new_view, view_change_responses['responses'])
                
                return {
                    'success': True,
                    'new_view': new_view,
                    'new_primary': new_primary_id,
                    'view_change_result': new_view_result
                }
            else:
                self.is_primary = False
                self.view = new_view
                
                return {
                    'success': True,
                    'new_view': new_view,
                    'new_primary': new_primary_id,
                    'role': 'backup'
                }
        
        return {'success': False, 'error': 'View change failed'}
    
    def _elect_new_primary(self, view: int) -> str:
        """Elect new primary based on view number"""
        # Simple round-robin primary election
        return f"node_{view % self.total_nodes}"
    
    def get_consensus_metrics(self) -> Dict[str, Any]:
        """Get comprehensive consensus performance metrics"""
        
        return {
            'node_id': self.node_id,
            'current_view': self.view,
            'current_sequence': self.sequence,
            'is_primary': self.is_primary,
            'byzantine_threshold': self.byzantine_threshold,
            'total_nodes': self.total_nodes,
            'executed_requests': len(self.executed_requests),
            'pending_requests': len(self.request_log) - len(self.executed_requests),
            'consensus_logs': {
                'prepare_entries': sum(len(prepares) for prepares in self.prepare_log.values()),
                'commit_entries': sum(len(commits) for commits in self.commit_log.values()),
                'reply_entries': sum(len(replies) for replies in self.reply_log.values())
            },
            'current_state': dict(self.current_state),
            'fault_tolerance': {
                'max_byzantine_faults': self.byzantine_threshold,
                'safety_guarantee': f"Safe with up to {self.byzantine_threshold} Byzantine faults",
                'liveness_guarantee': f"Live with up to {self.byzantine_threshold} Byzantine faults"
            }
        }

class ByzantineCluster:
    """Cluster of Byzantine fault tolerant nodes"""
    
    def __init__(self, node_count: int = 4):
        self.node_count = node_count
        self.byzantine_threshold = (node_count - 1) // 3
        self.nodes: Dict[str, ByzantineNode] = {}
        self.primary_node = "node_0"
        
        # Initialize nodes
        for i in range(node_count):
            node_id = f"node_{i}"
            node = ByzantineNode(node_id, node_count, self.byzantine_threshold)
            node.is_primary = (i == 0)  # First node is primary
            self.nodes[node_id] = node
    
    async def execute_consensus_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute request through Byzantine consensus across cluster"""
        
        primary = self.nodes[self.primary_node]
        result = await primary.process_client_request(request)
        
        return {
            'consensus_result': result,
            'cluster_state': self.get_cluster_state(),
            'fault_tolerance_info': {
                'total_nodes': self.node_count,
                'byzantine_threshold': self.byzantine_threshold,
                'can_tolerate_faults': self.byzantine_threshold
            }
        }
    
    def get_cluster_state(self) -> Dict[str, Any]:
        """Get comprehensive cluster state"""
        
        cluster_metrics = {}
        for node_id, node in self.nodes.items():
            cluster_metrics[node_id] = node.get_consensus_metrics()
        
        return {
            'cluster_size': self.node_count,
            'current_primary': self.primary_node,
            'byzantine_threshold': self.byzantine_threshold,
            'nodes': cluster_metrics,
            'consensus_health': self._assess_consensus_health()
        }
    
    def _assess_consensus_health(self) -> Dict[str, Any]:
        """Assess overall health of consensus system"""
        
        healthy_nodes = sum(1 for node in self.nodes.values() 
                          if len(node.executed_requests) > 0 or node.is_primary)
        
        return {
            'healthy_nodes': healthy_nodes,
            'unhealthy_nodes': self.node_count - healthy_nodes,
            'consensus_active': healthy_nodes >= (2 * self.byzantine_threshold + 1),
            'fault_tolerance_remaining': self.byzantine_threshold,
            'recommended_actions': self._get_health_recommendations(healthy_nodes)
        }
    
    def _get_health_recommendations(self, healthy_nodes: int) -> List[str]:
        """Get health recommendations based on cluster state"""
        
        recommendations = []
        
        if healthy_nodes <= 2 * self.byzantine_threshold + 1:
            recommendations.append("Consider adding more nodes to improve fault tolerance")
        
        if healthy_nodes <= self.byzantine_threshold + 1:
            recommendations.append("CRITICAL: Consensus may be compromised, immediate action required")
        
        if not any(node.is_primary for node in self.nodes.values()):
            recommendations.append("No active primary found, initiate view change")
        
        return recommendations
```

---

## Part 2: Game-Theoretic Conflict Resolution (35 minutes)

### Strategic Agent Behavior and Auction Mechanisms

🗂️ **File**: `src/session9/game_theoretic_coordination.py` - Game theory for multi-agent systems

```python
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import random
import math
from enum import Enum
from abc import ABC, abstractmethod

class BiddingStrategy(Enum):
    """Different bidding strategies for agents"""
    TRUTHFUL = "truthful"
    COMPETITIVE = "competitive"  
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"

@dataclass
class GameTheoryAgent:
    """Agent with strategic behavior capabilities"""
    agent_id: str
    capabilities: Dict[str, float] = field(default_factory=dict)
    resources: Dict[str, float] = field(default_factory=dict)
    utility_function: Optional[callable] = None
    bidding_strategy: BiddingStrategy = BiddingStrategy.TRUTHFUL
    learning_rate: float = 0.1
    exploration_rate: float = 0.1
    
    # Strategic behavior tracking
    bid_history: List[Dict[str, Any]] = field(default_factory=list)
    payoff_history: List[float] = field(default_factory=list)
    strategy_performance: Dict[str, List[float]] = field(default_factory=dict)

class AuctionMechanism(ABC):
    """Abstract base class for auction mechanisms"""
    
    @abstractmethod
    async def conduct_auction(self, task: Dict[str, Any], 
                            agents: List[GameTheoryAgent]) -> Dict[str, Any]:
        pass

class VickreyAuction(AuctionMechanism):
    """Second-price sealed-bid auction (Vickrey auction)"""
    
    def __init__(self):
        self.auction_history: List[Dict[str, Any]] = []
        
    async def conduct_auction(self, task: Dict[str, Any], 
                            agents: List[GameTheoryAgent]) -> Dict[str, Any]:
        """Conduct Vickrey auction for task allocation"""
        
        auction_id = f"auction_{len(self.auction_history)}"
        
        # Phase 1: Collect sealed bids
        bids = []
        for agent in agents:
            bid = await self._collect_agent_bid(agent, task)
            if bid['participation']:
                bids.append({
                    'agent_id': agent.agent_id,
                    'bid_amount': bid['bid_amount'],
                    'estimated_cost': bid['estimated_cost'],
                    'confidence': bid['confidence'],
                    'strategy_used': bid['strategy_used']
                })
        
        if not bids:
            return {
                'success': False,
                'error': 'No bids received',
                'auction_id': auction_id
            }
        
        # Phase 2: Determine winner and payment
        # Sort bids by amount (highest first)
        sorted_bids = sorted(bids, key=lambda x: x['bid_amount'], reverse=True)
        
        winner_bid = sorted_bids[0]
        # In Vickrey auction, winner pays second-highest price
        payment_amount = sorted_bids[1]['bid_amount'] if len(sorted_bids) > 1 else winner_bid['bid_amount']
        
        # Phase 3: Calculate utilities and update agent learning
        auction_result = {
            'success': True,
            'auction_id': auction_id,
            'task': task,
            'winner': winner_bid['agent_id'],
            'winning_bid': winner_bid['bid_amount'],
            'payment_amount': payment_amount,
            'efficiency': self._calculate_auction_efficiency(sorted_bids, task),
            'all_bids': sorted_bids,
            'auction_properties': {
                'truthful': True,  # Vickrey auctions are strategy-proof
                'efficient': True,  # Allocates to highest valuer
                'individual_rational': True  # Winners never pay more than bid
            }
        }
        
        # Update agent learning
        await self._update_agent_learning(agents, auction_result, task)
        
        # Store auction history
        self.auction_history.append(auction_result)
        
        return auction_result
    
    async def _collect_agent_bid(self, agent: GameTheoryAgent, 
                               task: Dict[str, Any]) -> Dict[str, Any]:
        """Collect bid from agent based on their strategy"""
        
        # Calculate agent's true valuation for the task
        true_value = self._calculate_true_valuation(agent, task)
        
        # Apply bidding strategy
        if agent.bidding_strategy == BiddingStrategy.TRUTHFUL:
            bid_amount = true_value
        elif agent.bidding_strategy == BiddingStrategy.COMPETITIVE:
            # Bid slightly above true value to increase win probability
            bid_amount = true_value * (1 + random.uniform(0.05, 0.15))
        elif agent.bidding_strategy == BiddingStrategy.CONSERVATIVE:
            # Bid below true value to ensure profit
            bid_amount = true_value * random.uniform(0.7, 0.9)
        elif agent.bidding_strategy == BiddingStrategy.AGGRESSIVE:
            # Bid significantly above true value
            bid_amount = true_value * (1 + random.uniform(0.2, 0.5))
        elif agent.bidding_strategy == BiddingStrategy.ADAPTIVE:
            # Use learning-based bidding
            bid_amount = await self._adaptive_bidding(agent, task, true_value)
        else:
            bid_amount = true_value
        
        # Determine participation
        participation_threshold = agent.resources.get('min_profit_margin', 0.1)
        estimated_cost = self._estimate_execution_cost(agent, task)
        
        participate = (bid_amount - estimated_cost) >= (estimated_cost * participation_threshold)
        
        bid_info = {
            'participation': participate,
            'bid_amount': max(0, bid_amount) if participate else 0,
            'true_valuation': true_value,
            'estimated_cost': estimated_cost,
            'confidence': self._calculate_confidence(agent, task),
            'strategy_used': agent.bidding_strategy.value
        }
        
        # Store in agent's bid history
        agent.bid_history.append({
            'task_id': task.get('task_id'),
            'timestamp': datetime.now(),
            'bid_info': bid_info
        })
        
        return bid_info
    
    def _calculate_true_valuation(self, agent: GameTheoryAgent, 
                                task: Dict[str, Any]) -> float:
        """Calculate agent's true valuation for a task"""
        
        # Base value from task importance and reward
        base_value = task.get('reward', 100)
        
        # Adjust based on agent capabilities
        capability_match = 0.5  # Default
        required_skills = task.get('required_skills', [])
        
        if required_skills:
            matches = sum(agent.capabilities.get(skill, 0) for skill in required_skills)
            capability_match = min(1.0, matches / len(required_skills))
        
        # Apply utility function if available
        if agent.utility_function:
            utility_value = agent.utility_function(task, agent)
        else:
            utility_value = base_value * capability_match
        
        # Add some randomness to represent uncertainty
        valuation = utility_value * random.uniform(0.8, 1.2)
        
        return max(0, valuation)
    
    def _estimate_execution_cost(self, agent: GameTheoryAgent, 
                               task: Dict[str, Any]) -> float:
        """Estimate cost for agent to execute task"""
        
        base_cost = task.get('complexity', 50)
        
        # Adjust for agent efficiency
        required_skills = task.get('required_skills', [])
        if required_skills:
            efficiency = sum(agent.capabilities.get(skill, 0.5) for skill in required_skills) / len(required_skills)
            cost_multiplier = 2.0 - efficiency  # Higher efficiency = lower cost
        else:
            cost_multiplier = 1.0
        
        estimated_cost = base_cost * cost_multiplier
        
        return estimated_cost
    
    async def _adaptive_bidding(self, agent: GameTheoryAgent, 
                             task: Dict[str, Any], true_value: float) -> float:
        """Implement adaptive bidding based on historical performance"""
        
        if not agent.strategy_performance.get('adaptive'):
            # No history, use truthful bidding
            return true_value
        
        # Analyze recent performance
        recent_performance = agent.strategy_performance['adaptive'][-10:]  # Last 10 auctions
        avg_success_rate = sum(1 for p in recent_performance if p > 0) / len(recent_performance)
        avg_payoff = sum(recent_performance) / len(recent_performance)
        
        # Adjust bidding based on performance
        if avg_success_rate < 0.3:  # Winning too rarely
            # Be more aggressive
            multiplier = 1 + random.uniform(0.1, 0.3)
        elif avg_success_rate > 0.7:  # Winning too often
            # Be more conservative  
            multiplier = random.uniform(0.7, 0.9)
        else:
            # Maintain current strategy
            multiplier = random.uniform(0.9, 1.1)
        
        # Apply exploration
        if random.random() < agent.exploration_rate:
            multiplier = random.uniform(0.5, 1.5)  # Random exploration
        
        return true_value * multiplier
    
    async def _update_agent_learning(self, agents: List[GameTheoryAgent],
                                   auction_result: Dict[str, Any], 
                                   task: Dict[str, Any]):
        """Update agent learning based on auction outcome"""
        
        winner_id = auction_result['winner']
        payment = auction_result['payment_amount']
        
        for agent in agents:
            if not agent.strategy_performance.get(agent.bidding_strategy.value):
                agent.strategy_performance[agent.bidding_strategy.value] = []
            
            if agent.agent_id == winner_id:
                # Winner: calculate actual payoff
                execution_cost = self._estimate_execution_cost(agent, task)
                payoff = payment - execution_cost
                agent.payoff_history.append(payoff)
                agent.strategy_performance[agent.bidding_strategy.value].append(payoff)
            else:
                # Loser: zero payoff
                agent.payoff_history.append(0)
                agent.strategy_performance[agent.bidding_strategy.value].append(0)
            
            # Update strategy if adaptive
            if agent.bidding_strategy == BiddingStrategy.ADAPTIVE:
                await self._update_adaptive_strategy(agent, auction_result)
    
    async def _update_adaptive_strategy(self, agent: GameTheoryAgent, 
                                      auction_result: Dict[str, Any]):
        """Update adaptive strategy parameters based on results"""
        
        recent_payoffs = agent.payoff_history[-5:]  # Last 5 auctions
        avg_recent_payoff = sum(recent_payoffs) / len(recent_payoffs) if recent_payoffs else 0
        
        # Simple learning: if recent performance is poor, increase exploration
        if avg_recent_payoff < 10:  # Arbitrary threshold
            agent.exploration_rate = min(0.3, agent.exploration_rate * 1.1)
        else:
            agent.exploration_rate = max(0.05, agent.exploration_rate * 0.95)

class CooperativeGameSolver:
    """Solver for cooperative games using Shapley value and core concepts"""
    
    def __init__(self):
        self.game_history: List[Dict[str, Any]] = []
    
    def calculate_shapley_value(self, agents: List[str], 
                              value_function: callable) -> Dict[str, float]:
        """Calculate Shapley value for fair payoff distribution"""
        
        n = len(agents)
        shapley_values = {agent: 0.0 for agent in agents}
        
        # Generate all possible coalitions and calculate marginal contributions
        import itertools
        
        for agent in agents:
            marginal_contributions = []
            
            # Consider all possible coalitions not including this agent
            other_agents = [a for a in agents if a != agent]
            
            for r in range(len(other_agents) + 1):
                for coalition in itertools.combinations(other_agents, r):
                    coalition_list = list(coalition)
                    
                    # Value with agent
                    coalition_with_agent = coalition_list + [agent]
                    value_with = value_function(coalition_with_agent)
                    
                    # Value without agent
                    value_without = value_function(coalition_list)
                    
                    # Marginal contribution
                    marginal_contribution = value_with - value_without
                    
                    # Weight by probability of this coalition forming
                    coalition_size = len(coalition_list)
                    weight = (math.factorial(coalition_size) * 
                             math.factorial(n - coalition_size - 1)) / math.factorial(n)
                    
                    marginal_contributions.append(marginal_contribution * weight)
            
            shapley_values[agent] = sum(marginal_contributions)
        
        return shapley_values
    
    def find_core_solutions(self, agents: List[str], 
                          value_function: callable) -> List[Dict[str, float]]:
        """Find core solutions where no coalition has incentive to deviate"""
        
        total_value = value_function(agents)
        
        # Generate candidate allocations
        candidate_allocations = self._generate_candidate_allocations(agents, total_value)
        
        # Check which allocations are in the core
        core_solutions = []
        
        for allocation in candidate_allocations:
            if self._is_in_core(allocation, agents, value_function):
                core_solutions.append(allocation)
        
        return core_solutions
    
    def _is_in_core(self, allocation: Dict[str, float], agents: List[str],
                   value_function: callable) -> bool:
        """Check if allocation is in the core"""
        
        import itertools
        
        # Check all possible coalitions
        for r in range(1, len(agents)):
            for coalition in itertools.combinations(agents, r):
                coalition_list = list(coalition)
                
                # Coalition value
                coalition_value = value_function(coalition_list)
                
                # Coalition allocation in current solution
                coalition_allocation = sum(allocation[agent] for agent in coalition_list)
                
                # If coalition can get more by deviating, not in core
                if coalition_value > coalition_allocation:
                    return False
        
        return True
    
    def solve_coalition_formation(self, agents: List[GameTheoryAgent],
                                tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Solve optimal coalition formation for multiple tasks"""
        
        # Define value function for coalitions
        def coalition_value(agent_ids: List[str]) -> float:
            if not agent_ids:
                return 0.0
                
            # Get agents in coalition
            coalition_agents = [a for a in agents if a.agent_id in agent_ids]
            
            # Calculate total value of tasks this coalition can handle
            total_value = 0.0
            for task in tasks:
                # Check if coalition can handle task
                if self._can_coalition_handle_task(coalition_agents, task):
                    task_value = task.get('reward', 100)
                    # Apply efficiency bonus for larger coalitions
                    efficiency_bonus = 1 + 0.1 * (len(coalition_agents) - 1)
                    total_value += task_value * efficiency_bonus
            
            return total_value
        
        agent_ids = [agent.agent_id for agent in agents]
        
        # Calculate Shapley values
        shapley_values = self.calculate_shapley_value(agent_ids, coalition_value)
        
        # Find core solutions
        core_solutions = self.find_core_solutions(agent_ids, coalition_value)
        
        # Find optimal coalitions for each task
        task_allocations = []
        for task in tasks:
            best_coalition = self._find_best_coalition_for_task(agents, task)
            task_allocations.append({
                'task': task,
                'coalition': best_coalition,
                'expected_value': coalition_value([agent.agent_id for agent in best_coalition])
            })
        
        return {
            'shapley_values': shapley_values,
            'core_solutions': core_solutions,
            'task_allocations': task_allocations,
            'total_system_value': coalition_value(agent_ids),
            'cooperation_analysis': self._analyze_cooperation_benefits(agents, tasks)
        }
    
    def _can_coalition_handle_task(self, coalition: List[GameTheoryAgent],
                                 task: Dict[str, Any]) -> bool:
        """Check if coalition can handle a specific task"""
        
        required_skills = task.get('required_skills', [])
        if not required_skills:
            return len(coalition) > 0
        
        # Check if combined capabilities meet requirements
        for skill in required_skills:
            total_capability = sum(agent.capabilities.get(skill, 0) for agent in coalition)
            required_level = task.get('skill_requirements', {}).get(skill, 0.5)
            
            if total_capability < required_level:
                return False
        
        return True
    
    def _find_best_coalition_for_task(self, agents: List[GameTheoryAgent],
                                    task: Dict[str, Any]) -> List[GameTheoryAgent]:
        """Find the best coalition to handle a specific task"""
        
        import itertools
        
        best_coalition = []
        best_efficiency = 0.0
        
        # Try all possible coalitions
        for r in range(1, len(agents) + 1):
            for coalition_ids in itertools.combinations(range(len(agents)), r):
                coalition = [agents[i] for i in coalition_ids]
                
                if self._can_coalition_handle_task(coalition, task):
                    efficiency = self._calculate_coalition_efficiency(coalition, task)
                    
                    if efficiency > best_efficiency:
                        best_efficiency = efficiency
                        best_coalition = coalition
        
        return best_coalition
    
    def _calculate_coalition_efficiency(self, coalition: List[GameTheoryAgent],
                                     task: Dict[str, Any]) -> float:
        """Calculate efficiency of coalition for a task"""
        
        required_skills = task.get('required_skills', [])
        if not required_skills:
            return 1.0 / len(coalition)  # Prefer smaller coalitions
        
        # Calculate skill match
        total_match = 0.0
        for skill in required_skills:
            coalition_capability = sum(agent.capabilities.get(skill, 0) for agent in coalition)
            required_level = task.get('skill_requirements', {}).get(skill, 0.5)
            match = min(1.0, coalition_capability / required_level)
            total_match += match
        
        skill_efficiency = total_match / len(required_skills)
        
        # Penalize oversized coalitions
        size_penalty = 1.0 / (1 + 0.1 * max(0, len(coalition) - 2))
        
        return skill_efficiency * size_penalty
```

---

## 🎯 Module Summary

You've now mastered advanced consensus algorithms and game theory for multi-agent systems:

✅ **Byzantine Fault Tolerance**: Implemented pBFT with mathematical safety guarantees  
✅ **Strategic Agent Behavior**: Built agents with sophisticated bidding strategies  
✅ **Auction Mechanisms**: Created truthful and efficient Vickrey auctions  
✅ **Cooperative Game Theory**: Implemented Shapley value and core solution concepts  
✅ **Coalition Formation**: Built optimal team formation algorithms with efficiency analysis

### Next Steps
- **Continue to Module B**: [Production Multi-Agent Systems](Session9_ModuleB_Production_Multi_Agent_Systems.md) for enterprise deployment
- **Return to Core**: [Session 9 Main](Session9_Multi_Agent_Patterns.md)
- **Next Session**: [Session 10 - Enterprise Integration](Session10_Enterprise_Integration_Production_Deployment.md)

---

**🗂️ Source Files for Module A:**
- `src/session9/byzantine_consensus.py` - Byzantine fault tolerance implementation
- `src/session9/game_theoretic_coordination.py` - Game theory and auction mechanisms