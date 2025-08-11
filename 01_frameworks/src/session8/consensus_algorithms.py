"""
Advanced Consensus Algorithms for Multi-Agent Systems
Session 8: Byzantine Fault Tolerance and Distributed Agreement

This module implements sophisticated consensus algorithms including Raft,
Practical Byzantine Fault Tolerance (pBFT), and other distributed agreement
protocols for robust multi-agent coordination.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import hashlib
import random
import logging
from datetime import datetime, timedelta
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConsensusType(Enum):
    """Types of consensus algorithms"""
    SIMPLE_MAJORITY = "simple_majority"
    QUALIFIED_MAJORITY = "qualified_majority"
    UNANIMOUS = "unanimous"
    WEIGHTED_VOTING = "weighted_voting"
    RAFT = "raft"
    PBFT = "pbft"  # Practical Byzantine Fault Tolerance
    PROOF_OF_STAKE = "proof_of_stake"


class NodeState(Enum):
    """States for Raft consensus nodes"""
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


class MessagePhase(Enum):
    """Phases in pBFT consensus"""
    PRE_PREPARE = "pre_prepare"
    PREPARE = "prepare"
    COMMIT = "commit"


@dataclass
class ConsensusProposal:
    """Represents a proposal for consensus"""
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proposer_id: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    signatures: List[str] = field(default_factory=list)
    votes: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert proposal to dictionary"""
        return {
            'proposal_id': self.proposal_id,
            'proposer_id': self.proposer_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'signatures': self.signatures,
            'votes': self.votes,
            'status': self.status,
            'metadata': self.metadata
        }
    
    def compute_digest(self) -> str:
        """Compute digest for Byzantine consensus"""
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]


@dataclass
class ConsensusMessage:
    """Message for consensus protocols"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    message_type: str = ""
    phase: Optional[MessagePhase] = None
    view_number: int = 0
    sequence_number: int = 0
    proposal_digest: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    signature: Optional[str] = None


class RaftConsensusNode:
    """Implementation of Raft consensus algorithm for agent coordination"""
    
    def __init__(self, node_id: str, cluster_nodes: List[str]):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[Dict[str, Any]] = []
        self.commit_index = 0
        self.last_applied = 0
        self.state = NodeState.FOLLOWER
        
        # Leader state (volatile)
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}
        
        # Timing
        self.last_heartbeat = datetime.now()
        self.election_timeout = timedelta(seconds=random.uniform(5, 10))
        self.heartbeat_interval = timedelta(seconds=2)
        
        # Statistics
        self.consensus_stats = {
            'terms_served_as_leader': 0,
            'elections_won': 0,
            'proposals_committed': 0,
            'messages_sent': 0,
            'messages_received': 0
        }
        
        logger.info(f"Raft node {node_id} initialized with {len(cluster_nodes)} cluster nodes")
    
    async def participate_in_consensus(self, proposal: ConsensusProposal) -> Dict[str, Any]:
        """Participate in Raft consensus for the given proposal"""
        
        logger.info(f"Node {self.node_id} participating in consensus for proposal {proposal.proposal_id}")
        
        if self.state == NodeState.LEADER:
            return await self._leader_handle_proposal(proposal)
        elif self.state == NodeState.CANDIDATE:
            return await self._candidate_handle_proposal(proposal)
        else:  # FOLLOWER
            return await self._follower_handle_proposal(proposal)
    
    async def _leader_handle_proposal(self, proposal: ConsensusProposal) -> Dict[str, Any]:
        """Handle proposal as cluster leader"""
        
        logger.info(f"Leader {self.node_id} handling proposal {proposal.proposal_id}")
        
        # Add proposal to log
        log_entry = {
            'term': self.current_term,
            'proposal': proposal.to_dict(),
            'timestamp': datetime.now(),
            'committed': False
        }
        self.log.append(log_entry)
        
        # Replicate to followers
        replication_results = await self._replicate_to_followers(log_entry)
        
        # Check if majority accepted
        successful_replications = sum(1 for r in replication_results if r.get('success', False))
        majority_threshold = len(self.cluster_nodes) // 2
        
        if successful_replications >= majority_threshold:
            # Commit the entry
            self.commit_index = len(self.log) - 1
            log_entry['committed'] = True
            
            # Notify followers to commit
            await self._send_commit_notifications(self.commit_index)
            
            self.consensus_stats['proposals_committed'] += 1
            
            return {
                'consensus_reached': True,
                'decision': proposal.content,
                'term': self.current_term,
                'commit_index': self.commit_index,
                'replications': successful_replications,
                'required': majority_threshold
            }
        else:
            return {
                'consensus_reached': False,
                'reason': 'Failed to achieve majority replication',
                'successful_replications': successful_replications,
                'required': majority_threshold
            }
    
    async def _candidate_handle_proposal(self, proposal: ConsensusProposal) -> Dict[str, Any]:
        """Handle proposal as candidate (redirect to leader election)"""
        
        # Candidate should focus on election first
        election_result = await self._conduct_leader_election()
        
        if election_result['won_election']:
            self.state = NodeState.LEADER
            self.consensus_stats['elections_won'] += 1
            return await self._leader_handle_proposal(proposal)
        else:
            self.state = NodeState.FOLLOWER
            return {
                'consensus_reached': False,
                'reason': 'Election failed, proposal deferred',
                'election_result': election_result
            }
    
    async def _follower_handle_proposal(self, proposal: ConsensusProposal) -> Dict[str, Any]:
        """Handle proposal as follower (forward to leader or trigger election)"""
        
        leader_id = await self._find_current_leader()
        
        if leader_id:
            return {
                'consensus_reached': False,
                'reason': 'Forwarded to leader',
                'leader_id': leader_id,
                'action': 'forwarded'
            }
        else:
            # No leader found, become candidate
            self.state = NodeState.CANDIDATE
            return await self._candidate_handle_proposal(proposal)
    
    async def _replicate_to_followers(self, log_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Replicate log entry to follower nodes"""
        
        replication_tasks = []
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                task = self._send_append_entries(node_id, log_entry)
                replication_tasks.append(task)
        
        results = await asyncio.gather(*replication_tasks, return_exceptions=True)
        
        # Filter out exceptions and convert to results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                valid_results.append({'success': False, 'error': str(result)})
            else:
                valid_results.append(result)
        
        self.consensus_stats['messages_sent'] += len(valid_results)
        return valid_results
    
    async def _send_append_entries(self, node_id: str, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Send AppendEntries RPC to follower"""
        
        # Mock implementation - in real system would use network RPC
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Simulate varying success rates
        success = random.random() > 0.1  # 90% success rate
        
        return {
            'node_id': node_id,
            'success': success,
            'term': self.current_term,
            'match_index': len(self.log) - 1 if success else 0
        }
    
    async def _conduct_leader_election(self) -> Dict[str, Any]:
        """Conduct leader election as candidate"""
        
        logger.info(f"Node {self.node_id} conducting leader election")
        
        # Increment term and vote for self
        self.current_term += 1
        self.voted_for = self.node_id
        votes_received = 1  # Vote for self
        
        # Request votes from other nodes
        vote_requests = []
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                task = self._request_vote(node_id)
                vote_requests.append(task)
        
        vote_responses = await asyncio.gather(*vote_requests, return_exceptions=True)
        
        # Count votes
        for response in vote_responses:
            if isinstance(response, dict) and response.get('vote_granted', False):
                votes_received += 1
        
        majority_needed = (len(self.cluster_nodes) // 2) + 1
        won_election = votes_received >= majority_needed
        
        if won_election:
            self.state = NodeState.LEADER
            logger.info(f"Node {self.node_id} won election with {votes_received} votes")
        
        return {
            'won_election': won_election,
            'votes_received': votes_received,
            'majority_needed': majority_needed,
            'term': self.current_term
        }
    
    async def _request_vote(self, node_id: str) -> Dict[str, Any]:
        """Request vote from another node"""
        
        # Mock implementation
        await asyncio.sleep(0.05)  # Simulate network delay
        
        # Simulate vote decision (simplified)
        vote_granted = random.random() > 0.3  # 70% chance of granting vote
        
        return {
            'node_id': node_id,
            'term': self.current_term,
            'vote_granted': vote_granted
        }
    
    async def _find_current_leader(self) -> Optional[str]:
        """Find current cluster leader"""
        
        # Mock implementation - would query cluster state
        if self.state == NodeState.LEADER:
            return self.node_id
        
        # Simulate finding leader
        potential_leaders = [n for n in self.cluster_nodes if n != self.node_id]
        return random.choice(potential_leaders) if potential_leaders and random.random() > 0.5 else None
    
    async def _send_commit_notifications(self, commit_index: int):
        """Notify followers to commit up to commit_index"""
        
        commit_tasks = []
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                task = self._send_commit_notification(node_id, commit_index)
                commit_tasks.append(task)
        
        await asyncio.gather(*commit_tasks, return_exceptions=True)
    
    async def _send_commit_notification(self, node_id: str, commit_index: int):
        """Send commit notification to specific node"""
        
        # Mock implementation
        await asyncio.sleep(0.05)
        self.consensus_stats['messages_sent'] += 1
        logger.debug(f"Sent commit notification to {node_id} for index {commit_index}")


class ByzantineConsensusNode:
    """Practical Byzantine Fault Tolerance (pBFT) implementation"""
    
    def __init__(self, node_id: str, cluster_nodes: List[str], f: int):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.f = f  # Number of Byzantine nodes we can tolerate
        self.n = len(cluster_nodes)  # Total number of nodes
        
        # Verify Byzantine fault tolerance requirements
        if self.n < 3 * f + 1:
            raise ValueError(f"Need at least {3*f+1} nodes to tolerate {f} Byzantine faults")
        
        self.view_number = 0
        self.sequence_number = 0
        self.primary_id = self._compute_primary_id()
        
        # Message logs for each phase
        self.message_log: Dict[MessagePhase, List[ConsensusMessage]] = {
            MessagePhase.PRE_PREPARE: [],
            MessagePhase.PREPARE: [],
            MessagePhase.COMMIT: []
        }
        
        # Consensus state
        self.prepared_requests: Set[str] = set()
        self.committed_requests: Set[str] = set()
        
        # Performance statistics
        self.byzantine_stats = {
            'consensus_rounds': 0,
            'byzantine_detected': 0,
            'view_changes': 0,
            'successful_commits': 0
        }
        
        logger.info(f"pBFT node {node_id} initialized (f={f}, n={n})")
    
    def _compute_primary_id(self) -> str:
        """Compute primary node for current view"""
        primary_index = self.view_number % len(self.cluster_nodes)
        return sorted(self.cluster_nodes)[primary_index]
    
    def _is_primary(self) -> bool:
        """Check if this node is the primary"""
        return self.node_id == self.primary_id
    
    async def byzantine_consensus(self, proposal: ConsensusProposal) -> Dict[str, Any]:
        """Execute pBFT consensus protocol"""
        
        consensus_start = datetime.now()
        self.byzantine_stats['consensus_rounds'] += 1
        
        logger.info(f"Node {self.node_id} starting pBFT consensus for proposal {proposal.proposal_id}")
        
        try:
            # Phase 1: Pre-prepare (only primary sends this)
            if self._is_primary():
                pre_prepare_result = await self._send_pre_prepare(proposal)
                if not pre_prepare_result['success']:
                    return {
                        'consensus_reached': False, 
                        'phase': 'pre-prepare',
                        'error': pre_prepare_result['error']
                    }
            else:
                pre_prepare_result = await self._wait_for_pre_prepare(proposal)
                if not pre_prepare_result['success']:
                    return {
                        'consensus_reached': False,
                        'phase': 'pre-prepare',
                        'error': pre_prepare_result['error']
                    }
            
            # Phase 2: Prepare (all non-faulty nodes participate)
            prepare_result = await self._participate_in_prepare_phase(proposal)
            if not prepare_result['success']:
                return {
                    'consensus_reached': False,
                    'phase': 'prepare',
                    'error': prepare_result['error']
                }
            
            # Phase 3: Commit (all non-faulty nodes participate)
            commit_result = await self._participate_in_commit_phase(proposal)
            
            consensus_duration = datetime.now() - consensus_start
            
            if commit_result['success']:
                self.byzantine_stats['successful_commits'] += 1
                self.committed_requests.add(proposal.proposal_id)
            
            return {
                'consensus_reached': commit_result['success'],
                'decision': proposal.content if commit_result['success'] else None,
                'view_number': self.view_number,
                'sequence_number': self.sequence_number,
                'phases_completed': ['pre-prepare', 'prepare', 'commit'] if commit_result['success'] else [],
                'consensus_time': consensus_duration,
                'byzantine_safety': True,  # pBFT guarantees safety
                'f_tolerance': self.f,
                'nodes_participated': commit_result.get('nodes_participated', 0)
            }
            
        except Exception as e:
            logger.error(f"pBFT consensus failed: {str(e)}")
            return {
                'consensus_reached': False,
                'error': str(e),
                'phase': 'exception'
            }
    
    async def _send_pre_prepare(self, proposal: ConsensusProposal) -> Dict[str, Any]:
        """Primary sends pre-prepare message"""
        
        if not self._is_primary():
            return {'success': False, 'error': 'Only primary can send pre-prepare'}
        
        self.sequence_number += 1
        
        pre_prepare_msg = ConsensusMessage(
            sender_id=self.node_id,
            message_type="pre_prepare",
            phase=MessagePhase.PRE_PREPARE,
            view_number=self.view_number,
            sequence_number=self.sequence_number,
            proposal_digest=proposal.compute_digest(),
            content={'proposal': proposal.to_dict()}
        )
        
        # Broadcast to all other nodes
        broadcast_results = await self._broadcast_consensus_message(pre_prepare_msg)
        
        successful_sends = sum(1 for r in broadcast_results if r.get('success', False))
        required_sends = len(self.cluster_nodes) - 1  # All except self
        
        return {
            'success': successful_sends >= required_sends * 0.7,  # Allow some failures
            'successful_sends': successful_sends,
            'required_sends': required_sends
        }
    
    async def _wait_for_pre_prepare(self, proposal: ConsensusProposal) -> Dict[str, Any]:
        """Non-primary nodes wait for pre-prepare message"""
        
        # Mock waiting for pre-prepare (in real implementation would listen for messages)
        await asyncio.sleep(0.1)
        
        # Simulate receiving pre-prepare message
        received_pre_prepare = random.random() > 0.1  # 90% success rate
        
        if received_pre_prepare:
            # Validate pre-prepare message
            is_valid = await self._validate_pre_prepare_message(proposal)
            return {'success': is_valid, 'error': None if is_valid else 'Invalid pre-prepare'}
        else:
            return {'success': False, 'error': 'Pre-prepare timeout'}
    
    async def _validate_pre_prepare_message(self, proposal: ConsensusProposal) -> bool:
        """Validate received pre-prepare message"""
        
        # Mock validation - in real system would check:
        # 1. Message is from primary
        # 2. View number matches
        # 3. Sequence number is correct
        # 4. Proposal digest matches
        
        # Simulate validation with high success rate
        return random.random() > 0.05  # 95% validation success
    
    async def _participate_in_prepare_phase(self, proposal: ConsensusProposal) -> Dict[str, Any]:
        """Participate in the prepare phase of pBFT"""
        
        logger.debug(f"Node {self.node_id} entering prepare phase")
        
        # Send prepare message to all nodes
        prepare_message = ConsensusMessage(
            sender_id=self.node_id,
            message_type="prepare",
            phase=MessagePhase.PREPARE,
            view_number=self.view_number,
            sequence_number=self.sequence_number,
            proposal_digest=proposal.compute_digest(),
            content={'node_state': 'prepared'}
        )
        
        # Broadcast prepare message
        broadcast_results = await self._broadcast_consensus_message(prepare_message)
        
        # Wait for prepare messages from others (mock implementation)
        prepare_responses = await self._collect_prepare_messages(proposal)
        
        # Validate prepare messages
        valid_prepares = await self._validate_prepare_messages(prepare_responses, proposal)
        
        # Check if we have enough valid prepares (2f+1 including our own)
        required_prepares = 2 * self.f + 1
        
        if len(valid_prepares) >= required_prepares:
            self.prepared_requests.add(proposal.proposal_id)
            return {
                'success': True,
                'valid_prepares': len(valid_prepares),
                'required': required_prepares,
                'phase': 'prepare_complete'
            }
        else:
            return {
                'success': False,
                'valid_prepares': len(valid_prepares),
                'required': required_prepares,
                'error': 'Insufficient valid prepare messages'
            }
    
    async def _participate_in_commit_phase(self, proposal: ConsensusProposal) -> Dict[str, Any]:
        """Participate in the commit phase of pBFT"""
        
        logger.debug(f"Node {self.node_id} entering commit phase")
        
        # Send commit message to all nodes
        commit_message = ConsensusMessage(
            sender_id=self.node_id,
            message_type="commit",
            phase=MessagePhase.COMMIT,
            view_number=self.view_number,
            sequence_number=self.sequence_number,
            proposal_digest=proposal.compute_digest(),
            content={'node_state': 'committed'}
        )
        
        # Broadcast commit message
        await self._broadcast_consensus_message(commit_message)
        
        # Wait for commit messages from others
        commit_responses = await self._collect_commit_messages(proposal)
        
        # Validate commit messages
        valid_commits = await self._validate_commit_messages(commit_responses, proposal)
        
        # Check if we have enough valid commits (2f+1 including our own)
        required_commits = 2 * self.f + 1
        
        if len(valid_commits) >= required_commits:
            return {
                'success': True,
                'valid_commits': len(valid_commits),
                'required': required_commits,
                'nodes_participated': len(valid_commits),
                'phase': 'commit_complete'
            }
        else:
            return {
                'success': False,
                'valid_commits': len(valid_commits),
                'required': required_commits,
                'error': 'Insufficient valid commit messages'
            }
    
    async def _broadcast_consensus_message(self, message: ConsensusMessage) -> List[Dict[str, Any]]:
        """Broadcast consensus message to all other nodes"""
        
        broadcast_tasks = []
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                task = self._send_consensus_message(node_id, message)
                broadcast_tasks.append(task)
        
        results = await asyncio.gather(*broadcast_tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({'success': False, 'error': str(result)})
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _send_consensus_message(self, node_id: str, message: ConsensusMessage) -> Dict[str, Any]:
        """Send consensus message to specific node"""
        
        # Mock implementation with network delay and potential failures
        await asyncio.sleep(random.uniform(0.01, 0.05))  # Simulate network delay
        
        # Simulate Byzantine behavior detection
        if random.random() < 0.02:  # 2% chance of detecting Byzantine behavior
            self.byzantine_stats['byzantine_detected'] += 1
            return {'success': False, 'error': 'Byzantine behavior detected', 'node_id': node_id}
        
        # Normal message delivery
        success = random.random() > 0.05  # 95% success rate
        return {'success': success, 'node_id': node_id}
    
    async def _collect_prepare_messages(self, proposal: ConsensusProposal) -> List[ConsensusMessage]:
        """Collect prepare messages from other nodes"""
        
        # Mock implementation - simulate receiving messages
        await asyncio.sleep(0.2)  # Simulate message collection time
        
        # Generate mock prepare messages
        messages = []
        for node_id in self.cluster_nodes:
            if node_id != self.node_id and random.random() > 0.1:  # 90% response rate
                msg = ConsensusMessage(
                    sender_id=node_id,
                    message_type="prepare",
                    phase=MessagePhase.PREPARE,
                    view_number=self.view_number,
                    sequence_number=self.sequence_number,
                    proposal_digest=proposal.compute_digest()
                )
                messages.append(msg)
        
        return messages
    
    async def _collect_commit_messages(self, proposal: ConsensusProposal) -> List[ConsensusMessage]:
        """Collect commit messages from other nodes"""
        
        # Mock implementation
        await asyncio.sleep(0.2)
        
        messages = []
        for node_id in self.cluster_nodes:
            if node_id != self.node_id and random.random() > 0.1:  # 90% response rate
                msg = ConsensusMessage(
                    sender_id=node_id,
                    message_type="commit",
                    phase=MessagePhase.COMMIT,
                    view_number=self.view_number,
                    sequence_number=self.sequence_number,
                    proposal_digest=proposal.compute_digest()
                )
                messages.append(msg)
        
        return messages
    
    async def _validate_prepare_messages(self, messages: List[ConsensusMessage], 
                                        proposal: ConsensusProposal) -> List[ConsensusMessage]:
        """Validate prepare messages and detect Byzantine behavior"""
        
        valid_messages = []
        expected_digest = proposal.compute_digest()
        
        for msg in messages:
            # Validate message consistency
            if (msg.view_number == self.view_number and
                msg.sequence_number == self.sequence_number and
                msg.proposal_digest == expected_digest):
                valid_messages.append(msg)
            else:
                # Potential Byzantine behavior
                self.byzantine_stats['byzantine_detected'] += 1
                logger.warning(f"Invalid prepare message from {msg.sender_id}")
        
        return valid_messages
    
    async def _validate_commit_messages(self, messages: List[ConsensusMessage],
                                       proposal: ConsensusProposal) -> List[ConsensusMessage]:
        """Validate commit messages"""
        
        valid_messages = []
        expected_digest = proposal.compute_digest()
        
        for msg in messages:
            if (msg.view_number == self.view_number and
                msg.sequence_number == self.sequence_number and
                msg.proposal_digest == expected_digest):
                valid_messages.append(msg)
            else:
                self.byzantine_stats['byzantine_detected'] += 1
                logger.warning(f"Invalid commit message from {msg.sender_id}")
        
        return valid_messages


class ConsensusOrchestrator:
    """Orchestrates different consensus algorithms based on requirements"""
    
    def __init__(self):
        self.consensus_algorithms = {
            ConsensusType.RAFT: self._raft_consensus,
            ConsensusType.PBFT: self._pbft_consensus,
            ConsensusType.SIMPLE_MAJORITY: self._simple_majority_consensus,
            ConsensusType.WEIGHTED_VOTING: self._weighted_voting_consensus
        }
        self.orchestrator_stats = {
            'total_consensus_rounds': 0,
            'successful_consensus': 0,
            'algorithm_usage': {}
        }
    
    async def reach_consensus(self, proposal: ConsensusProposal, 
                             algorithm: ConsensusType,
                             participants: List[str],
                             algorithm_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Reach consensus using specified algorithm"""
        
        self.orchestrator_stats['total_consensus_rounds'] += 1
        
        if algorithm not in self.consensus_algorithms:
            return {
                'consensus_reached': False,
                'error': f'Unknown consensus algorithm: {algorithm}'
            }
        
        # Update algorithm usage stats
        if algorithm.value not in self.orchestrator_stats['algorithm_usage']:
            self.orchestrator_stats['algorithm_usage'][algorithm.value] = 0
        self.orchestrator_stats['algorithm_usage'][algorithm.value] += 1
        
        # Execute consensus algorithm
        consensus_func = self.consensus_algorithms[algorithm]
        result = await consensus_func(proposal, participants, algorithm_params or {})
        
        if result.get('consensus_reached', False):
            self.orchestrator_stats['successful_consensus'] += 1
        
        result['algorithm_used'] = algorithm.value
        result['orchestrator_stats'] = self.orchestrator_stats.copy()
        
        return result
    
    async def _raft_consensus(self, proposal: ConsensusProposal, 
                             participants: List[str],
                             params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Raft consensus"""
        
        if len(participants) < 3:
            return {
                'consensus_reached': False,
                'error': 'Raft requires at least 3 participants'
            }
        
        # Create Raft node (simplified - normally would have persistent nodes)
        leader_id = participants[0]  # Simple leader selection
        raft_node = RaftConsensusNode(leader_id, participants)
        raft_node.state = NodeState.LEADER
        
        return await raft_node.participate_in_consensus(proposal)
    
    async def _pbft_consensus(self, proposal: ConsensusProposal,
                             participants: List[str],
                             params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pBFT consensus"""
        
        f = params.get('byzantine_tolerance', 1)
        
        if len(participants) < 3 * f + 1:
            return {
                'consensus_reached': False,
                'error': f'pBFT requires at least {3*f+1} participants for f={f} Byzantine tolerance'
            }
        
        # Create pBFT node
        primary_id = participants[0]  # Simple primary selection
        pbft_node = ByzantineConsensusNode(primary_id, participants, f)
        
        return await pbft_node.byzantine_consensus(proposal)
    
    async def _simple_majority_consensus(self, proposal: ConsensusProposal,
                                        participants: List[str],
                                        params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simple majority voting"""
        
        # Mock voting process
        votes = []
        for participant in participants:
            # Simulate vote with 70% approval rate
            vote = "approve" if random.random() > 0.3 else "reject"
            votes.append({'participant': participant, 'vote': vote})
        
        approve_count = sum(1 for v in votes if v['vote'] == 'approve')
        majority_threshold = len(participants) // 2 + 1
        
        return {
            'consensus_reached': approve_count >= majority_threshold,
            'decision': proposal.content if approve_count >= majority_threshold else None,
            'votes': votes,
            'approve_count': approve_count,
            'threshold': majority_threshold,
            'algorithm': 'simple_majority'
        }
    
    async def _weighted_voting_consensus(self, proposal: ConsensusProposal,
                                        participants: List[str],
                                        params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute weighted voting consensus"""
        
        weights = params.get('weights', {})
        threshold = params.get('threshold', 0.6)
        
        # Default equal weights if not specified
        if not weights:
            weights = {p: 1.0 for p in participants}
        
        # Mock weighted voting
        total_weight = 0.0
        approve_weight = 0.0
        votes = []
        
        for participant in participants:
            weight = weights.get(participant, 1.0)
            # Simulate vote
            vote = "approve" if random.random() > 0.3 else "reject"
            
            total_weight += weight
            if vote == "approve":
                approve_weight += weight
            
            votes.append({
                'participant': participant,
                'vote': vote,
                'weight': weight
            })
        
        approval_ratio = approve_weight / total_weight if total_weight > 0 else 0
        
        return {
            'consensus_reached': approval_ratio >= threshold,
            'decision': proposal.content if approval_ratio >= threshold else None,
            'votes': votes,
            'approval_ratio': approval_ratio,
            'threshold': threshold,
            'total_weight': total_weight,
            'approve_weight': approve_weight,
            'algorithm': 'weighted_voting'
        }


# Demonstration and testing functions
async def demonstrate_consensus_algorithms():
    """Demonstrate various consensus algorithms"""
    
    print("🤝 Advanced Consensus Algorithms Demonstration")
    print("=" * 55)
    
    # Create test proposal
    test_proposal = ConsensusProposal(
        proposer_id="agent_1",
        content={
            "action": "approve_budget",
            "amount": 100000,
            "department": "engineering",
            "justification": "Infrastructure upgrade"
        }
    )
    
    print(f"📋 Test Proposal: {test_proposal.content['action']}")
    print(f"💰 Amount: ${test_proposal.content['amount']:,}")
    
    # Test participants
    participants = ["agent_1", "agent_2", "agent_3", "agent_4", "agent_5", "agent_6", "agent_7"]
    
    # Initialize orchestrator
    orchestrator = ConsensusOrchestrator()
    
    # Test different consensus algorithms
    algorithms_to_test = [
        (ConsensusType.SIMPLE_MAJORITY, {}),
        (ConsensusType.WEIGHTED_VOTING, {
            'weights': {'agent_1': 2.0, 'agent_2': 1.5, 'agent_3': 1.0},
            'threshold': 0.6
        }),
        (ConsensusType.RAFT, {}),
        (ConsensusType.PBFT, {'byzantine_tolerance': 2})
    ]
    
    results = {}
    
    for algorithm, params in algorithms_to_test:
        print(f"\n🔍 Testing {algorithm.value.upper()} Consensus:")
        print("-" * 40)
        
        try:
            result = await orchestrator.reach_consensus(
                test_proposal, algorithm, participants, params
            )
            
            results[algorithm.value] = result
            
            print(f"✅ Consensus Reached: {result['consensus_reached']}")
            
            if result['consensus_reached']:
                print(f"🎯 Decision: Approved")
                if 'approval_ratio' in result:
                    print(f"📊 Approval Rate: {result['approval_ratio']:.1%}")
                if 'consensus_time' in result:
                    print(f"⏱️  Time: {result['consensus_time'].total_seconds():.2f}s")
            else:
                print(f"❌ Reason: {result.get('error', 'Consensus failed')}")
                
        except Exception as e:
            print(f"💥 Error: {str(e)}")
            results[algorithm.value] = {'error': str(e)}
    
    # Test Byzantine fault tolerance specifically
    print(f"\n🛡️ Byzantine Fault Tolerance Test:")
    print("-" * 40)
    
    # Test with adequate nodes for Byzantine tolerance
    byzantine_nodes = ["node_1", "node_2", "node_3", "node_4", "node_5", "node_6", "node_7"]
    
    pbft_node = ByzantineConsensusNode("node_1", byzantine_nodes, f=2)
    byzantine_result = await pbft_node.byzantine_consensus(test_proposal)
    
    print(f"🔒 Byzantine Safety: {byzantine_result.get('byzantine_safety', False)}")
    print(f"🎯 Consensus Success: {byzantine_result['consensus_reached']}")
    print(f"⚖️  Fault Tolerance: Can handle {pbft_node.f} Byzantine nodes")
    print(f"🔧 Total Nodes: {pbft_node.n}")
    
    # Show overall statistics
    stats = orchestrator.orchestrator_stats
    print(f"\n📈 Overall Statistics:")
    print(f"   Total rounds: {stats['total_consensus_rounds']}")
    print(f"   Success rate: {stats['successful_consensus']/max(1,stats['total_consensus_rounds']):.1%}")
    print(f"   Algorithm usage: {stats['algorithm_usage']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(demonstrate_consensus_algorithms())