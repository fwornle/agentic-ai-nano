"""
Advanced Conflict Resolution for Multi-Agent Systems
Session 8: Game-Theoretic and Negotiation-Based Conflict Resolution

This module implements sophisticated conflict resolution mechanisms including
negotiation protocols, game-theoretic solutions, and mediation systems for
handling strategic interactions and disputes in multi-agent environments.
"""

from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import random
import logging
import itertools
import numpy as np
from datetime import datetime, timedelta
import uuid
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of conflicts in multi-agent systems"""
    RESOURCE_COMPETITION = "resource_competition"
    GOAL_CONFLICT = "goal_conflict"
    STRATEGY_DISAGREEMENT = "strategy_disagreement"
    INFORMATION_ASYMMETRY = "information_asymmetry"
    COORDINATION_FAILURE = "coordination_failure"
    VALUE_CONFLICT = "value_conflict"
    PRIORITY_DISPUTE = "priority_dispute"


class ResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    NEGOTIATION = "negotiation"
    ARBITRATION = "arbitration"
    MAJORITY_RULE = "majority_rule"
    WEIGHTED_COMPROMISE = "weighted_compromise"
    AUCTION = "auction"
    GAME_THEORY = "game_theory"
    MEDIATION = "mediation"
    COLLABORATIVE_FILTERING = "collaborative_filtering"


class NegotiationStyle(Enum):
    """Negotiation styles for agents"""
    COMPETITIVE = "competitive"
    COLLABORATIVE = "collaborative"
    ACCOMMODATING = "accommodating"
    AVOIDING = "avoiding"
    COMPROMISING = "compromising"


class GameType(Enum):
    """Types of game-theoretic scenarios"""
    ZERO_SUM = "zero_sum"
    NON_ZERO_SUM = "non_zero_sum"
    COOPERATIVE = "cooperative"
    PRISONERS_DILEMMA = "prisoners_dilemma"
    COORDINATION_GAME = "coordination_game"
    AUCTION_GAME = "auction_game"


@dataclass
class ConflictScenario:
    """Represents a conflict situation between agents"""
    conflict_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conflict_type: ConflictType = ConflictType.RESOURCE_COMPETITION
    involved_agents: List[str] = field(default_factory=list)
    disputed_items: List[str] = field(default_factory=list)
    agent_positions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    urgency_level: int = 5  # 1-10 scale
    resolution_deadline: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict to dictionary"""
        return {
            'conflict_id': self.conflict_id,
            'conflict_type': self.conflict_type.value,
            'involved_agents': self.involved_agents,
            'disputed_items': self.disputed_items,
            'agent_positions': self.agent_positions,
            'urgency_level': self.urgency_level,
            'created_at': self.created_at.isoformat(),
            'context': self.context
        }


@dataclass
class NegotiationProposal:
    """Represents a proposal in negotiation"""
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proposer_id: str = ""
    proposal_terms: Dict[str, Any] = field(default_factory=dict)
    concessions: List[str] = field(default_factory=list)
    demands: List[str] = field(default_factory=list)
    rationale: str = ""
    validity_period: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_expired(self) -> bool:
        """Check if proposal has expired"""
        return datetime.now() > self.created_at + self.validity_period


@dataclass
class ResolutionResult:
    """Result of conflict resolution process"""
    conflict_id: str = ""
    resolution_strategy: ResolutionStrategy = ResolutionStrategy.NEGOTIATION
    success: bool = False
    agreed_terms: Optional[Dict[str, Any]] = None
    participating_agents: List[str] = field(default_factory=list)
    resolution_duration: timedelta = field(default_factory=timedelta)
    satisfaction_scores: Dict[str, float] = field(default_factory=dict)  # Agent satisfaction
    fairness_score: float = 0.0
    stability_score: float = 0.0  # How likely the agreement is to hold
    resolution_quality: str = "unknown"
    implementation_plan: Dict[str, Any] = field(default_factory=dict)
    monitoring_requirements: List[str] = field(default_factory=list)
    
    def calculate_overall_satisfaction(self) -> float:
        """Calculate overall satisfaction across all agents"""
        if not self.satisfaction_scores:
            return 0.0
        return statistics.mean(self.satisfaction_scores.values())


class ConflictResolver:
    """Advanced conflict resolution system for multi-agent environments"""
    
    def __init__(self, mediator_agent: Optional[str] = None):
        self.mediator_agent = mediator_agent
        self.conflict_history: List[ConflictScenario] = []
        self.resolution_history: List[ResolutionResult] = []
        self.agent_profiles: Dict[str, Dict[str, Any]] = {}
        self.resolution_strategies = {
            ResolutionStrategy.NEGOTIATION: self._negotiation_resolution,
            ResolutionStrategy.ARBITRATION: self._arbitration_resolution,
            ResolutionStrategy.MAJORITY_RULE: self._majority_rule_resolution,
            ResolutionStrategy.WEIGHTED_COMPROMISE: self._weighted_compromise_resolution,
            ResolutionStrategy.AUCTION: self._auction_resolution,
            ResolutionStrategy.GAME_THEORY: self._game_theory_resolution,
            ResolutionStrategy.MEDIATION: self._mediation_resolution
        }
        
        # Resolution statistics
        self.resolution_stats = {
            'total_conflicts': 0,
            'resolved_conflicts': 0,
            'average_resolution_time': timedelta(0),
            'strategy_success_rates': {},
            'agent_cooperation_scores': {}
        }
    
    def register_agent_profile(self, agent_id: str, profile: Dict[str, Any]):
        """Register agent profile for conflict resolution"""
        self.agent_profiles[agent_id] = profile
        logger.info(f"Registered profile for agent {agent_id}")
    
    async def resolve_conflict(self, conflict: ConflictScenario, 
                             strategy: ResolutionStrategy = ResolutionStrategy.NEGOTIATION,
                             timeout: timedelta = timedelta(minutes=30)) -> ResolutionResult:
        """
        Resolve conflict using specified strategy
        
        Args:
            conflict: The conflict scenario to resolve
            strategy: Resolution strategy to use
            timeout: Maximum time for resolution process
            
        Returns:
            Resolution result with outcome and metrics
        """
        
        resolution_start = datetime.now()
        self.resolution_stats['total_conflicts'] += 1
        
        logger.info(f"Starting conflict resolution for {conflict.conflict_id} using {strategy.value}")
        
        # Analyze conflict characteristics
        conflict_analysis = await self._analyze_conflict(conflict)
        
        # Select optimal strategy if auto-selection requested
        if strategy == ResolutionStrategy.NEGOTIATION and conflict_analysis.get('recommend_strategy'):
            strategy = conflict_analysis['recommend_strategy']
            logger.info(f"Auto-selected strategy: {strategy.value}")
        
        # Execute resolution strategy
        try:
            if strategy in self.resolution_strategies:
                resolution_result = await asyncio.wait_for(
                    self.resolution_strategies[strategy](conflict, conflict_analysis),
                    timeout=timeout.total_seconds()
                )
            else:
                resolution_result = ResolutionResult(
                    conflict_id=conflict.conflict_id,
                    success=False,
                    resolution_strategy=strategy
                )
                logger.error(f"Unknown resolution strategy: {strategy}")
        
        except asyncio.TimeoutError:
            resolution_result = ResolutionResult(
                conflict_id=conflict.conflict_id,
                success=False,
                resolution_strategy=strategy
            )
            logger.warning(f"Conflict resolution timed out for {conflict.conflict_id}")
        
        except Exception as e:
            resolution_result = ResolutionResult(
                conflict_id=conflict.conflict_id,
                success=False,
                resolution_strategy=strategy
            )
            logger.error(f"Conflict resolution failed: {str(e)}")
        
        # Finalize result
        resolution_result.resolution_duration = datetime.now() - resolution_start
        resolution_result.participating_agents = conflict.involved_agents.copy()
        
        # Update statistics
        self._update_resolution_statistics(resolution_result)
        
        # Store in history
        self.conflict_history.append(conflict)
        self.resolution_history.append(resolution_result)
        
        logger.info(f"Conflict resolution completed: Success={resolution_result.success}, "
                   f"Duration={resolution_result.resolution_duration.total_seconds():.1f}s")
        
        return resolution_result
    
    async def _analyze_conflict(self, conflict: ConflictScenario) -> Dict[str, Any]:
        """Analyze conflict to determine characteristics and optimal approach"""
        
        analysis = {
            'complexity_score': 0.0,
            'cooperation_potential': 0.0,
            'time_pressure': 0.0,
            'power_balance': {},
            'common_ground': [],
            'major_obstacles': [],
            'recommend_strategy': None
        }
        
        # Complexity analysis
        complexity_factors = [
            len(conflict.involved_agents) / 10,  # More agents = more complex
            len(conflict.disputed_items) / 5,    # More items = more complex
            conflict.urgency_level / 10          # Higher urgency = more complex
        ]
        analysis['complexity_score'] = min(1.0, statistics.mean(complexity_factors))
        
        # Cooperation potential based on agent profiles
        cooperation_scores = []
        for agent_id in conflict.involved_agents:
            profile = self.agent_profiles.get(agent_id, {})
            cooperation_score = profile.get('cooperation_tendency', 0.5)
            cooperation_scores.append(cooperation_score)
            
            # Analyze power balance
            power_level = profile.get('influence_level', 0.5)
            analysis['power_balance'][agent_id] = power_level
        
        if cooperation_scores:
            analysis['cooperation_potential'] = statistics.mean(cooperation_scores)
        
        # Time pressure analysis
        if conflict.resolution_deadline:
            time_remaining = conflict.resolution_deadline - datetime.now()
            analysis['time_pressure'] = min(1.0, max(0.0, 1.0 - (time_remaining.total_seconds() / 86400)))  # Normalize to days
        
        # Identify common ground
        if len(conflict.involved_agents) >= 2:
            agent_positions = conflict.agent_positions
            if agent_positions:
                # Find shared interests or compatible goals
                analysis['common_ground'] = await self._find_common_ground(agent_positions)
        
        # Strategy recommendation
        analysis['recommend_strategy'] = await self._recommend_strategy(analysis, conflict)
        
        return analysis
    
    async def _find_common_ground(self, agent_positions: Dict[str, Dict[str, Any]]) -> List[str]:
        """Find areas of common ground between agents"""
        
        common_ground = []
        
        # Look for shared goals or compatible interests
        all_goals = []
        for agent_id, position in agent_positions.items():
            goals = position.get('goals', [])
            all_goals.extend(goals)
        
        # Find goals mentioned by multiple agents
        goal_counts = {}
        for goal in all_goals:
            goal_counts[goal] = goal_counts.get(goal, 0) + 1
        
        common_goals = [goal for goal, count in goal_counts.items() if count > 1]
        common_ground.extend(common_goals)
        
        # Look for compatible values
        all_values = []
        for agent_id, position in agent_positions.items():
            values = position.get('values', [])
            all_values.extend(values)
        
        value_counts = {}
        for value in all_values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        common_values = [value for value, count in value_counts.items() if count > 1]
        common_ground.extend([f"shared_value_{v}" for v in common_values])
        
        return common_ground
    
    async def _recommend_strategy(self, analysis: Dict[str, Any], 
                                conflict: ConflictScenario) -> ResolutionStrategy:
        """Recommend optimal resolution strategy based on analysis"""
        
        complexity = analysis['complexity_score']
        cooperation = analysis['cooperation_potential']
        time_pressure = analysis['time_pressure']
        
        # Strategy selection logic
        if time_pressure > 0.8:
            # High time pressure - use quick resolution
            if complexity < 0.5:
                return ResolutionStrategy.MAJORITY_RULE
            else:
                return ResolutionStrategy.ARBITRATION
        
        elif cooperation > 0.7:
            # High cooperation potential - use collaborative approaches
            if complexity > 0.6:
                return ResolutionStrategy.MEDIATION
            else:
                return ResolutionStrategy.NEGOTIATION
        
        elif complexity > 0.8:
            # High complexity - use sophisticated approaches
            return ResolutionStrategy.GAME_THEORY
        
        elif len(conflict.involved_agents) > 5:
            # Many agents - use scalable approaches
            return ResolutionStrategy.WEIGHTED_COMPROMISE
        
        else:
            # Default to negotiation
            return ResolutionStrategy.NEGOTIATION
    
    async def _negotiation_resolution(self, conflict: ConflictScenario, 
                                    analysis: Dict[str, Any]) -> ResolutionResult:
        """Resolve conflict through structured negotiation"""
        
        logger.info(f"Starting negotiation for conflict {conflict.conflict_id}")
        
        involved_agents = conflict.involved_agents
        agent_positions = conflict.agent_positions.copy()
        
        negotiation_rounds = []
        max_rounds = 8
        current_round = 1
        
        while current_round <= max_rounds:
            round_start = datetime.now()
            
            logger.debug(f"Negotiation round {current_round}")
            
            # Conduct negotiation round
            round_proposals = await self._conduct_negotiation_round(
                involved_agents, agent_positions, conflict.disputed_items, current_round
            )
            
            # Evaluate proposals
            evaluation_results = await self._evaluate_negotiation_proposals(
                round_proposals, agent_positions, conflict
            )
            
            # Check for agreement
            agreement_check = await self._check_negotiation_agreement(
                evaluation_results, threshold=0.8
            )
            
            round_duration = datetime.now() - round_start
            negotiation_rounds.append({
                'round': current_round,
                'proposals': round_proposals,
                'evaluations': evaluation_results,
                'agreement_level': agreement_check['agreement_score'],
                'duration': round_duration
            })
            
            if agreement_check['has_agreement']:
                # Agreement reached
                result = ResolutionResult(
                    conflict_id=conflict.conflict_id,
                    resolution_strategy=ResolutionStrategy.NEGOTIATION,
                    success=True,
                    agreed_terms=agreement_check['agreed_terms'],
                    satisfaction_scores=agreement_check['satisfaction_scores'],
                    fairness_score=agreement_check['fairness_score'],
                    stability_score=0.8,  # Negotiated agreements tend to be stable
                    resolution_quality="negotiated_agreement"
                )
                
                result.implementation_plan = await self._create_implementation_plan(
                    agreement_check['agreed_terms'], involved_agents
                )
                
                return result
            
            # Update positions for next round
            agent_positions = await self._update_agent_positions(
                agent_positions, evaluation_results
            )
            
            current_round += 1
        
        # Negotiation failed to reach agreement
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.NEGOTIATION,
            success=False,
            resolution_quality="negotiation_failed"
        )
    
    async def _conduct_negotiation_round(self, agents: List[str], 
                                       agent_positions: Dict[str, Dict[str, Any]],
                                       disputed_items: List[str], 
                                       round_num: int) -> List[NegotiationProposal]:
        """Conduct a single round of negotiation"""
        
        proposals = []
        
        for agent_id in agents:
            position = agent_positions.get(agent_id, {})
            
            # Generate proposal based on agent's position and negotiation style
            proposal = await self._generate_agent_proposal(
                agent_id, position, disputed_items, round_num
            )
            
            if proposal:
                proposals.append(proposal)
        
        return proposals
    
    async def _generate_agent_proposal(self, agent_id: str, 
                                     position: Dict[str, Any],
                                     disputed_items: List[str], 
                                     round_num: int) -> Optional[NegotiationProposal]:
        """Generate proposal for an agent"""
        
        profile = self.agent_profiles.get(agent_id, {})
        negotiation_style = profile.get('negotiation_style', NegotiationStyle.COMPROMISING.value)
        
        # Base proposal on agent's goals and constraints
        goals = position.get('goals', [])
        constraints = position.get('constraints', [])
        preferences = position.get('preferences', {})
        
        # Generate proposal terms
        proposal_terms = {}
        concessions = []
        demands = []
        
        for item in disputed_items:
            item_preference = preferences.get(item, 0.5)  # 0.0 = don't want, 1.0 = strongly want
            
            if negotiation_style == NegotiationStyle.COMPETITIVE.value:
                # Competitive agents make strong demands initially
                if item_preference > 0.6:
                    proposal_terms[item] = 'strongly_request'
                    demands.append(item)
                else:
                    proposal_terms[item] = 'neutral'
            
            elif negotiation_style == NegotiationStyle.COLLABORATIVE.value:
                # Collaborative agents look for mutual benefit
                if item_preference > 0.7:
                    proposal_terms[item] = 'request_with_compensation'
                elif item_preference < 0.3:
                    proposal_terms[item] = 'willing_to_concede'
                    concessions.append(item)
                else:
                    proposal_terms[item] = 'open_to_discussion'
            
            elif negotiation_style == NegotiationStyle.COMPROMISING.value:
                # Compromising agents adjust based on round number
                adjustment_factor = round_num * 0.1  # Become more flexible over time
                adjusted_preference = item_preference * (1 - adjustment_factor)
                
                if adjusted_preference > 0.5:
                    proposal_terms[item] = 'moderate_request'
                else:
                    proposal_terms[item] = 'flexible'
                    if round_num > 3:  # Offer concessions in later rounds
                        concessions.append(item)
        
        # Create rationale
        rationale = f"Proposal based on {negotiation_style} approach, round {round_num}"
        
        return NegotiationProposal(
            proposer_id=agent_id,
            proposal_terms=proposal_terms,
            concessions=concessions,
            demands=demands,
            rationale=rationale
        )
    
    async def _evaluate_negotiation_proposals(self, proposals: List[NegotiationProposal],
                                            agent_positions: Dict[str, Dict[str, Any]],
                                            conflict: ConflictScenario) -> Dict[str, Any]:
        """Evaluate negotiation proposals for compatibility"""
        
        evaluation_results = {
            'proposal_scores': {},
            'compatibility_matrix': {},
            'potential_agreements': [],
            'major_disagreements': []
        }
        
        # Score each proposal from each agent's perspective
        for proposal in proposals:
            scores = {}
            for agent_id in conflict.involved_agents:
                if agent_id != proposal.proposer_id:
                    score = await self._score_proposal_for_agent(
                        proposal, agent_id, agent_positions
                    )
                    scores[agent_id] = score
            
            evaluation_results['proposal_scores'][proposal.proposal_id] = scores
        
        # Find potential areas of agreement
        for item in conflict.disputed_items:
            item_proposals = {}
            for proposal in proposals:
                item_proposals[proposal.proposer_id] = proposal.proposal_terms.get(item, 'neutral')
            
            # Check if there's potential agreement on this item
            if await self._check_item_agreement_potential(item_proposals):
                evaluation_results['potential_agreements'].append({
                    'item': item,
                    'proposals': item_proposals
                })
            else:
                evaluation_results['major_disagreements'].append({
                    'item': item,
                    'proposals': item_proposals
                })
        
        return evaluation_results
    
    async def _score_proposal_for_agent(self, proposal: NegotiationProposal,
                                      agent_id: str, 
                                      agent_positions: Dict[str, Dict[str, Any]]) -> float:
        """Score how well a proposal aligns with an agent's position"""
        
        agent_position = agent_positions.get(agent_id, {})
        agent_preferences = agent_position.get('preferences', {})
        
        total_score = 0.0
        scored_items = 0
        
        for item, proposed_allocation in proposal.proposal_terms.items():
            if item in agent_preferences:
                item_preference = agent_preferences[item]
                
                # Score based on how well proposal aligns with preference
                if proposed_allocation == 'strongly_request' and item_preference < 0.3:
                    item_score = 0.8  # Good for agent (proposer wants something agent doesn't)
                elif proposed_allocation == 'willing_to_concede' and item_preference > 0.7:
                    item_score = 0.9  # Excellent for agent
                elif proposed_allocation == 'open_to_discussion':
                    item_score = 0.6  # Neutral/moderate
                elif proposed_allocation == 'request_with_compensation':
                    item_score = 0.7 if item_preference < 0.5 else 0.4
                else:
                    item_score = 0.5  # Default neutral score
                
                total_score += item_score
                scored_items += 1
        
        return total_score / scored_items if scored_items > 0 else 0.5
    
    async def _check_item_agreement_potential(self, item_proposals: Dict[str, str]) -> bool:
        """Check if there's potential agreement on a specific item"""
        
        # Look for compatible proposals
        concession_agents = [agent for agent, proposal in item_proposals.items() 
                           if proposal in ['willing_to_concede', 'flexible']]
        
        requesting_agents = [agent for agent, proposal in item_proposals.items()
                           if proposal in ['strongly_request', 'moderate_request']]
        
        # Potential agreement if someone is willing to concede and others want it
        return len(concession_agents) > 0 and len(requesting_agents) > 0
    
    async def _check_negotiation_agreement(self, evaluation_results: Dict[str, Any],
                                         threshold: float = 0.7) -> Dict[str, Any]:
        """Check if negotiation has reached sufficient agreement"""
        
        potential_agreements = evaluation_results['potential_agreements']
        major_disagreements = evaluation_results['major_disagreements']
        
        # Calculate agreement score
        total_items = len(potential_agreements) + len(major_disagreements)
        agreement_score = len(potential_agreements) / total_items if total_items > 0 else 0.0
        
        has_agreement = agreement_score >= threshold
        
        result = {
            'has_agreement': has_agreement,
            'agreement_score': agreement_score,
            'agreed_terms': {},
            'satisfaction_scores': {},
            'fairness_score': 0.0
        }
        
        if has_agreement:
            # Create agreed terms from potential agreements
            for agreement in potential_agreements:
                item = agreement['item']
                proposals = agreement['proposals']
                
                # Simple allocation: give item to agent who requested it most strongly
                # while ensuring others who are willing to concede get fair compensation
                result['agreed_terms'][item] = await self._create_agreement_terms(proposals)
            
            # Calculate satisfaction scores (simplified)
            num_agents = len(evaluation_results.get('proposal_scores', {}))
            base_satisfaction = agreement_score * 0.8
            
            for i in range(num_agents):
                agent_id = f"agent_{i}"  # Simplified for demo
                result['satisfaction_scores'][agent_id] = base_satisfaction + random.uniform(-0.1, 0.1)
            
            result['fairness_score'] = agreement_score * 0.9  # High agreement usually means fair
        
        return result
    
    async def _create_agreement_terms(self, proposals: Dict[str, str]) -> Dict[str, Any]:
        """Create specific agreement terms from proposals"""
        
        # Find who wants the item most and who is willing to concede
        strong_requesters = [agent for agent, prop in proposals.items() 
                           if prop == 'strongly_request']
        moderate_requesters = [agent for agent, prop in proposals.items()
                             if prop == 'moderate_request']
        conceding_agents = [agent for agent, prop in proposals.items()
                          if prop in ['willing_to_concede', 'flexible']]
        
        # Simple allocation logic
        if strong_requesters:
            allocated_to = strong_requesters[0]
        elif moderate_requesters:
            allocated_to = moderate_requesters[0]
        else:
            allocated_to = list(proposals.keys())[0]  # Default allocation
        
        return {
            'allocated_to': allocated_to,
            'compensation_to': conceding_agents,
            'terms': 'standard_allocation'
        }
    
    async def _update_agent_positions(self, agent_positions: Dict[str, Dict[str, Any]],
                                    evaluation_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Update agent positions based on negotiation feedback"""
        
        updated_positions = {}
        
        for agent_id, position in agent_positions.items():
            updated_position = position.copy()
            
            # Agents become more flexible over time in negotiations
            preferences = updated_position.get('preferences', {})
            for item, preference in preferences.items():
                # Slight movement toward center (more flexible)
                if preference > 0.5:
                    updated_position['preferences'][item] = max(0.3, preference - 0.05)
                else:
                    updated_position['preferences'][item] = min(0.7, preference + 0.05)
            
            updated_positions[agent_id] = updated_position
        
        return updated_positions
    
    async def _arbitration_resolution(self, conflict: ConflictScenario,
                                    analysis: Dict[str, Any]) -> ResolutionResult:
        """Resolve conflict through arbitration"""
        
        logger.info(f"Starting arbitration for conflict {conflict.conflict_id}")
        
        # Arbitrator makes binding decision based on evidence
        arbitrator_decision = await self._make_arbitration_decision(conflict, analysis)
        
        # Calculate satisfaction based on how well decision aligns with agent positions
        satisfaction_scores = {}
        for agent_id in conflict.involved_agents:
            agent_position = conflict.agent_positions.get(agent_id, {})
            satisfaction = await self._calculate_arbitration_satisfaction(
                agent_id, agent_position, arbitrator_decision
            )
            satisfaction_scores[agent_id] = satisfaction
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.ARBITRATION,
            success=True,
            agreed_terms=arbitrator_decision,
            satisfaction_scores=satisfaction_scores,
            fairness_score=0.8,  # Arbitration is generally fair
            stability_score=0.9,  # Arbitration decisions are binding and stable
            resolution_quality="arbitrated_decision"
        )
    
    async def _make_arbitration_decision(self, conflict: ConflictScenario,
                                       analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Make arbitration decision based on conflict analysis"""
        
        decision = {}
        
        # Simple arbitration logic: try to balance interests fairly
        for item in conflict.disputed_items:
            # Collect all agent preferences for this item
            item_preferences = {}
            for agent_id, position in conflict.agent_positions.items():
                preferences = position.get('preferences', {})
                item_preferences[agent_id] = preferences.get(item, 0.5)
            
            # Award to agent with strongest preference
            if item_preferences:
                winning_agent = max(item_preferences.items(), key=lambda x: x[1])
                decision[item] = {
                    'allocated_to': winning_agent[0],
                    'rationale': f'Highest preference score: {winning_agent[1]:.2f}'
                }
        
        return decision
    
    async def _calculate_arbitration_satisfaction(self, agent_id: str,
                                                agent_position: Dict[str, Any],
                                                decision: Dict[str, Any]) -> float:
        """Calculate agent satisfaction with arbitration decision"""
        
        preferences = agent_position.get('preferences', {})
        
        total_satisfaction = 0.0
        evaluated_items = 0
        
        for item, allocation in decision.items():
            if item in preferences:
                item_preference = preferences[item]
                
                if allocation['allocated_to'] == agent_id:
                    # Agent got the item - satisfaction based on how much they wanted it
                    satisfaction = item_preference
                else:
                    # Agent didn't get the item - satisfaction is inverse of how much they wanted it
                    satisfaction = 1.0 - item_preference
                
                total_satisfaction += satisfaction
                evaluated_items += 1
        
        return total_satisfaction / evaluated_items if evaluated_items > 0 else 0.5
    
    async def _majority_rule_resolution(self, conflict: ConflictScenario,
                                      analysis: Dict[str, Any]) -> ResolutionResult:
        """Resolve conflict using majority rule voting"""
        
        logger.info(f"Starting majority rule resolution for conflict {conflict.conflict_id}")
        
        voting_results = {}
        
        # For each disputed item, agents vote on allocation
        for item in conflict.disputed_items:
            votes = {}
            
            # Each agent votes for who should get the item (including themselves)
            for voter_id in conflict.involved_agents:
                voter_position = conflict.agent_positions.get(voter_id, {})
                preferences = voter_position.get('preferences', {})
                
                # Agent votes for themselves if they want the item, otherwise random/fair vote
                item_preference = preferences.get(item, 0.5)
                
                if item_preference > 0.7:  # Strong preference - vote for self
                    votes[voter_id] = voter_id
                elif item_preference < 0.3:  # Don't want it - vote for someone else
                    other_agents = [a for a in conflict.involved_agents if a != voter_id]
                    votes[voter_id] = random.choice(other_agents) if other_agents else voter_id
                else:  # Neutral - vote fairly based on others' preferences
                    # Vote for agent who seems to want it most
                    best_candidate = voter_id
                    best_score = item_preference
                    
                    for candidate_id, candidate_position in conflict.agent_positions.items():
                        candidate_prefs = candidate_position.get('preferences', {})
                        candidate_preference = candidate_prefs.get(item, 0.5)
                        
                        if candidate_preference > best_score:
                            best_candidate = candidate_id
                            best_score = candidate_preference
                    
                    votes[voter_id] = best_candidate
            
            # Count votes
            vote_counts = {}
            for candidate in votes.values():
                vote_counts[candidate] = vote_counts.get(candidate, 0) + 1
            
            # Winner is candidate with most votes
            winner = max(vote_counts.items(), key=lambda x: x[1])
            voting_results[item] = {
                'winner': winner[0],
                'votes': winner[1],
                'total_voters': len(votes),
                'vote_breakdown': vote_counts
            }
        
        # Calculate satisfaction scores
        satisfaction_scores = {}
        for agent_id in conflict.involved_agents:
            wins = sum(1 for result in voting_results.values() if result['winner'] == agent_id)
            satisfaction = wins / len(voting_results) if voting_results else 0.5
            satisfaction_scores[agent_id] = satisfaction
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.MAJORITY_RULE,
            success=True,
            agreed_terms=voting_results,
            satisfaction_scores=satisfaction_scores,
            fairness_score=0.7,  # Majority rule is democratic but not always fair to minorities
            stability_score=0.6,  # May face resistance from losing minority
            resolution_quality="democratic_decision"
        )
    
    async def _weighted_compromise_resolution(self, conflict: ConflictScenario,
                                            analysis: Dict[str, Any]) -> ResolutionResult:
        """Resolve conflict through weighted compromise"""
        
        logger.info(f"Starting weighted compromise for conflict {conflict.conflict_id}")
        
        # Determine agent weights based on various factors
        agent_weights = {}
        for agent_id in conflict.involved_agents:
            profile = self.agent_profiles.get(agent_id, {})
            
            # Weight factors: influence, expertise, stake in outcome
            influence = profile.get('influence_level', 0.5)
            expertise = profile.get('expertise_level', 0.5)
            stake = profile.get('stake_in_conflict', 0.5)
            
            # Combined weight
            weight = (influence * 0.4 + expertise * 0.3 + stake * 0.3)
            agent_weights[agent_id] = weight
        
        # Normalize weights
        total_weight = sum(agent_weights.values())
        if total_weight > 0:
            agent_weights = {k: v/total_weight for k, v in agent_weights.items()}
        
        # Create weighted compromise solution
        compromise_terms = {}
        
        for item in conflict.disputed_items:
            # Calculate weighted preference score for each potential recipient
            recipient_scores = {}
            
            for potential_recipient in conflict.involved_agents:
                score = 0.0
                
                for agent_id, weight in agent_weights.items():
                    agent_position = conflict.agent_positions.get(agent_id, {})
                    preferences = agent_position.get('preferences', {})
                    
                    if potential_recipient == agent_id:
                        # How much does this agent want the item for themselves?
                        item_preference = preferences.get(item, 0.5)
                        score += weight * item_preference
                    else:
                        # How much does this agent think the other should get it?
                        # Assume agents are somewhat altruistic in compromise
                        altruism_factor = profile.get('altruism_level', 0.3)
                        score += weight * altruism_factor * 0.5
                
                recipient_scores[potential_recipient] = score
            
            # Award to highest scoring recipient
            best_recipient = max(recipient_scores.items(), key=lambda x: x[1])
            compromise_terms[item] = {
                'allocated_to': best_recipient[0],
                'weighted_score': best_recipient[1],
                'runner_ups': sorted(recipient_scores.items(), 
                                   key=lambda x: x[1], reverse=True)[1:3]
            }
        
        # Calculate satisfaction based on weighted outcomes
        satisfaction_scores = {}
        for agent_id in conflict.involved_agents:
            agent_wins = sum(1 for term in compromise_terms.values() 
                           if term['allocated_to'] == agent_id)
            
            # Satisfaction also considers the agent's weight/influence
            base_satisfaction = agent_wins / len(compromise_terms) if compromise_terms else 0.5
            weight_bonus = agent_weights.get(agent_id, 0.5) * 0.2  # Weight gives small bonus
            
            satisfaction_scores[agent_id] = min(1.0, base_satisfaction + weight_bonus)
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.WEIGHTED_COMPROMISE,
            success=True,
            agreed_terms=compromise_terms,
            satisfaction_scores=satisfaction_scores,
            fairness_score=0.75,  # Weighted systems try to be fair but may favor influential agents
            stability_score=0.8,   # Compromise solutions are generally stable
            resolution_quality="weighted_compromise"
        )
    
    async def _auction_resolution(self, conflict: ConflictScenario,
                                analysis: Dict[str, Any]) -> ResolutionResult:
        """Resolve conflict through auction mechanism"""
        
        logger.info(f"Starting auction resolution for conflict {conflict.conflict_id}")
        
        # Simple auction: agents bid for disputed items
        auction_results = {}
        
        for item in conflict.disputed_items:
            # Collect bids from all agents
            bids = {}
            
            for agent_id in conflict.involved_agents:
                agent_position = conflict.agent_positions.get(agent_id, {})
                preferences = agent_position.get('preferences', {})
                item_preference = preferences.get(item, 0.5)
                
                # Bid amount based on preference and agent's resources
                profile = self.agent_profiles.get(agent_id, {})
                budget = profile.get('budget', 100.0)
                
                # Bid is percentage of budget proportional to preference
                bid_amount = budget * item_preference * random.uniform(0.8, 1.2)
                bids[agent_id] = bid_amount
            
            # Winner is highest bidder
            if bids:
                winner = max(bids.items(), key=lambda x: x[1])
                auction_results[item] = {
                    'winner': winner[0],
                    'winning_bid': winner[1],
                    'all_bids': bids,
                    'auction_type': 'first_price_sealed_bid'
                }
        
        # Calculate satisfaction (winners happy, but paid a price)
        satisfaction_scores = {}
        for agent_id in conflict.involved_agents:
            agent_wins = sum(1 for result in auction_results.values() 
                           if result['winner'] == agent_id)
            
            total_paid = sum(result['winning_bid'] for result in auction_results.values()
                           if result['winner'] == agent_id)
            
            # Satisfaction decreases with amount paid
            profile = self.agent_profiles.get(agent_id, {})
            budget = profile.get('budget', 100.0)
            
            win_satisfaction = agent_wins / len(auction_results) if auction_results else 0
            cost_penalty = (total_paid / budget) * 0.3 if budget > 0 else 0
            
            satisfaction_scores[agent_id] = max(0.0, win_satisfaction - cost_penalty)
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.AUCTION,
            success=True,
            agreed_terms=auction_results,
            satisfaction_scores=satisfaction_scores,
            fairness_score=0.8,  # Auctions are fair but favor wealthy agents
            stability_score=0.9,  # Market-based solutions are stable
            resolution_quality="market_allocation"
        )
    
    async def _game_theory_resolution(self, conflict: ConflictScenario,
                                    analysis: Dict[str, Any]) -> ResolutionResult:
        """Resolve conflict using game-theoretic principles"""
        
        logger.info(f"Starting game-theoretic resolution for conflict {conflict.conflict_id}")
        
        # Model conflict as a game and find Nash equilibrium
        game_result = await self._solve_conflict_game(conflict, analysis)
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.GAME_THEORY,
            success=game_result['solution_found'],
            agreed_terms=game_result.get('nash_equilibrium'),
            satisfaction_scores=game_result.get('satisfaction_scores', {}),
            fairness_score=game_result.get('fairness_score', 0.7),
            stability_score=game_result.get('stability_score', 0.9),
            resolution_quality="game_theoretic_solution"
        )
    
    async def _solve_conflict_game(self, conflict: ConflictScenario,
                                 analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Solve conflict as a game-theoretic problem"""
        
        # Simplified game theory implementation
        # In practice, this would involve complex optimization
        
        agents = conflict.involved_agents
        disputed_items = conflict.disputed_items
        
        # Create payoff matrix for each agent-item combination
        payoff_matrix = {}
        
        for agent_id in agents:
            agent_payoffs = {}
            agent_position = conflict.agent_positions.get(agent_id, {})
            preferences = agent_position.get('preferences', {})
            
            for item in disputed_items:
                # Payoff is based on preference
                item_preference = preferences.get(item, 0.5)
                agent_payoffs[item] = item_preference
            
            payoff_matrix[agent_id] = agent_payoffs
        
        # Find Nash equilibrium (simplified)
        nash_solution = await self._find_nash_equilibrium(payoff_matrix, agents, disputed_items)
        
        # Calculate satisfaction scores
        satisfaction_scores = {}
        for agent_id in agents:
            agent_satisfaction = 0.0
            
            for item in disputed_items:
                if nash_solution.get(item) == agent_id:
                    # Agent got the item
                    item_preference = payoff_matrix[agent_id].get(item, 0.5)
                    agent_satisfaction += item_preference
            
            satisfaction_scores[agent_id] = agent_satisfaction / len(disputed_items)
        
        return {
            'solution_found': True,
            'nash_equilibrium': nash_solution,
            'satisfaction_scores': satisfaction_scores,
            'fairness_score': 0.75,
            'stability_score': 0.9  # Nash equilibria are stable by definition
        }
    
    async def _find_nash_equilibrium(self, payoff_matrix: Dict[str, Dict[str, float]],
                                   agents: List[str], 
                                   items: List[str]) -> Dict[str, str]:
        """Find Nash equilibrium for item allocation"""
        
        # Simplified Nash equilibrium finding
        # Allocate each item to agent with highest payoff
        
        allocation = {}
        
        for item in items:
            best_agent = None
            best_payoff = -1.0
            
            for agent_id in agents:
                payoff = payoff_matrix.get(agent_id, {}).get(item, 0.0)
                if payoff > best_payoff:
                    best_payoff = payoff
                    best_agent = agent_id
            
            if best_agent:
                allocation[item] = best_agent
        
        return allocation
    
    async def _mediation_resolution(self, conflict: ConflictScenario,
                                  analysis: Dict[str, Any]) -> ResolutionResult:
        """Resolve conflict through mediation"""
        
        logger.info(f"Starting mediation for conflict {conflict.conflict_id}")
        
        # Mediator facilitates discussion and helps find mutually acceptable solution
        mediation_result = await self._conduct_mediation_session(conflict, analysis)
        
        return ResolutionResult(
            conflict_id=conflict.conflict_id,
            resolution_strategy=ResolutionStrategy.MEDIATION,
            success=mediation_result['agreement_reached'],
            agreed_terms=mediation_result.get('mediated_agreement'),
            satisfaction_scores=mediation_result.get('satisfaction_scores', {}),
            fairness_score=mediation_result.get('fairness_score', 0.8),
            stability_score=mediation_result.get('stability_score', 0.85),
            resolution_quality="mediated_agreement"
        )
    
    async def _conduct_mediation_session(self, conflict: ConflictScenario,
                                       analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct mediation session"""
        
        # Mediation process: identify interests, generate options, evaluate solutions
        
        # Step 1: Identify underlying interests
        underlying_interests = await self._identify_underlying_interests(conflict)
        
        # Step 2: Generate creative options
        creative_options = await self._generate_mediation_options(
            conflict, underlying_interests, analysis
        )
        
        # Step 3: Evaluate options for mutual acceptability
        best_option = await self._select_best_mediation_option(
            creative_options, conflict, underlying_interests
        )
        
        if best_option:
            # Calculate satisfaction based on how well solution meets interests
            satisfaction_scores = {}
            for agent_id in conflict.involved_agents:
                satisfaction = await self._calculate_mediation_satisfaction(
                    agent_id, best_option, underlying_interests
                )
                satisfaction_scores[agent_id] = satisfaction
            
            return {
                'agreement_reached': True,
                'mediated_agreement': best_option,
                'satisfaction_scores': satisfaction_scores,
                'fairness_score': 0.8,
                'stability_score': 0.85
            }
        else:
            return {'agreement_reached': False}
    
    async def _identify_underlying_interests(self, conflict: ConflictScenario) -> Dict[str, List[str]]:
        """Identify underlying interests behind agent positions"""
        
        interests = {}
        
        for agent_id, position in conflict.agent_positions.items():
            agent_interests = []
            
            # Extract interests from goals and preferences
            goals = position.get('goals', [])
            preferences = position.get('preferences', {})
            
            # Map goals to underlying interests
            for goal in goals:
                if 'efficiency' in goal.lower():
                    agent_interests.append('operational_efficiency')
                elif 'cost' in goal.lower():
                    agent_interests.append('cost_minimization')
                elif 'quality' in goal.lower():
                    agent_interests.append('quality_assurance')
                else:
                    agent_interests.append(f'goal_{goal}')
            
            # Map preferences to interests
            for item, preference in preferences.items():
                if preference > 0.7:
                    agent_interests.append(f'access_to_{item}')
                elif preference < 0.3:
                    agent_interests.append(f'avoid_{item}_responsibility')
            
            interests[agent_id] = agent_interests
        
        return interests
    
    async def _generate_mediation_options(self, conflict: ConflictScenario,
                                        interests: Dict[str, List[str]],
                                        analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate creative options that address multiple interests"""
        
        options = []
        
        # Option 1: Time-sharing solution
        time_sharing_option = {'type': 'time_sharing', 'allocations': {}}
        for item in conflict.disputed_items:
            # Rotate access based on preference strength
            agent_prefs = []
            for agent_id in conflict.involved_agents:
                position = conflict.agent_positions.get(agent_id, {})
                pref = position.get('preferences', {}).get(item, 0.5)
                agent_prefs.append((agent_id, pref))
            
            # Sort by preference and allocate time proportionally
            sorted_prefs = sorted(agent_prefs, key=lambda x: x[1], reverse=True)
            time_allocation = {}
            total_pref = sum(pref for _, pref in sorted_prefs)
            
            for agent_id, pref in sorted_prefs:
                if total_pref > 0:
                    time_share = pref / total_pref
                    time_allocation[agent_id] = time_share
            
            time_sharing_option['allocations'][item] = time_allocation
        
        options.append(time_sharing_option)
        
        # Option 2: Compensation-based solution
        compensation_option = {'type': 'compensation', 'allocations': {}}
        for item in conflict.disputed_items:
            # Give item to agent who wants it most, others get compensation
            agent_prefs = [(agent_id, conflict.agent_positions.get(agent_id, {})
                          .get('preferences', {}).get(item, 0.5))
                          for agent_id in conflict.involved_agents]
            
            winner = max(agent_prefs, key=lambda x: x[1])
            losers = [agent_id for agent_id, _ in agent_prefs if agent_id != winner[0]]
            
            compensation_option['allocations'][item] = {
                'primary_owner': winner[0],
                'compensated_agents': losers,
                'compensation_type': 'alternative_resources'
            }
        
        options.append(compensation_option)
        
        # Option 3: Collaborative solution
        if analysis.get('cooperation_potential', 0) > 0.6:
            collaborative_option = {'type': 'collaborative', 'allocations': {}}
            for item in conflict.disputed_items:
                collaborative_option['allocations'][item] = {
                    'shared_ownership': conflict.involved_agents,
                    'management_rotation': True,
                    'decision_making': 'consensus'
                }
            
            options.append(collaborative_option)
        
        return options
    
    async def _select_best_mediation_option(self, options: List[Dict[str, Any]],
                                          conflict: ConflictScenario,
                                          interests: Dict[str, List[str]]) -> Optional[Dict[str, Any]]:
        """Select the mediation option that best satisfies all parties"""
        
        if not options:
            return None
        
        best_option = None
        best_score = 0.0
        
        for option in options:
            # Score option based on how well it satisfies each agent's interests
            total_satisfaction = 0.0
            
            for agent_id in conflict.involved_agents:
                agent_satisfaction = await self._score_option_for_agent(
                    option, agent_id, interests.get(agent_id, []), conflict
                )
                total_satisfaction += agent_satisfaction
            
            average_satisfaction = total_satisfaction / len(conflict.involved_agents)
            
            if average_satisfaction > best_score:
                best_score = average_satisfaction
                best_option = option
        
        return best_option
    
    async def _score_option_for_agent(self, option: Dict[str, Any], agent_id: str,
                                    agent_interests: List[str],
                                    conflict: ConflictScenario) -> float:
        """Score how well an option satisfies an agent's interests"""
        
        option_type = option.get('type')
        allocations = option.get('allocations', {})
        
        total_score = 0.0
        scored_items = 0
        
        agent_position = conflict.agent_positions.get(agent_id, {})
        preferences = agent_position.get('preferences', {})
        
        for item, allocation in allocations.items():
            item_preference = preferences.get(item, 0.5)
            item_score = 0.0
            
            if option_type == 'time_sharing':
                time_share = allocation.get(agent_id, 0.0)
                item_score = item_preference * time_share
            
            elif option_type == 'compensation':
                if allocation.get('primary_owner') == agent_id:
                    item_score = item_preference
                elif agent_id in allocation.get('compensated_agents', []):
                    # Compensation value (simplified)
                    item_score = (1.0 - item_preference) * 0.7  # 70% compensation value
                else:
                    item_score = 0.0
            
            elif option_type == 'collaborative':
                if agent_id in allocation.get('shared_ownership', []):
                    # Shared ownership gives partial satisfaction
                    sharing_factor = 1.0 / len(allocation.get('shared_ownership', [1]))
                    item_score = item_preference * sharing_factor * 0.8  # 80% of full value
            
            total_score += item_score
            scored_items += 1
        
        return total_score / scored_items if scored_items > 0 else 0.0
    
    async def _calculate_mediation_satisfaction(self, agent_id: str,
                                              solution: Dict[str, Any],
                                              interests: Dict[str, List[str]]) -> float:
        """Calculate agent satisfaction with mediated solution"""
        
        # Satisfaction based on how well solution addresses agent's interests
        agent_interests = interests.get(agent_id, [])
        
        if not agent_interests:
            return 0.5  # Neutral satisfaction if no interests identified
        
        satisfied_interests = 0
        
        for interest in agent_interests:
            # Check if solution addresses this interest (simplified)
            if 'efficiency' in interest and solution.get('type') == 'time_sharing':
                satisfied_interests += 1
            elif 'access' in interest and agent_id in str(solution):
                satisfied_interests += 1
            elif 'cost' in interest and 'compensation' in solution.get('type', ''):
                satisfied_interests += 1
        
        base_satisfaction = satisfied_interests / len(agent_interests)
        
        # Add bonus for collaborative solutions if agent values cooperation
        if solution.get('type') == 'collaborative':
            base_satisfaction += 0.1
        
        return min(1.0, base_satisfaction)
    
    async def _create_implementation_plan(self, agreed_terms: Dict[str, Any],
                                        involved_agents: List[str]) -> Dict[str, Any]:
        """Create implementation plan for agreed resolution"""
        
        return {
            'implementation_steps': [
                'Communicate agreement to all parties',
                'Establish monitoring mechanisms',
                'Set up feedback channels',
                'Schedule follow-up reviews'
            ],
            'timeline': '2 weeks',
            'responsible_parties': involved_agents,
            'success_metrics': ['compliance_rate', 'satisfaction_maintenance'],
            'escalation_procedure': 'return_to_mediation'
        }
    
    def _update_resolution_statistics(self, result: ResolutionResult):
        """Update resolution statistics"""
        
        if result.success:
            self.resolution_stats['resolved_conflicts'] += 1
        
        # Update strategy success rates
        strategy = result.resolution_strategy.value
        if strategy not in self.resolution_stats['strategy_success_rates']:
            self.resolution_stats['strategy_success_rates'][strategy] = {'attempts': 0, 'successes': 0}
        
        self.resolution_stats['strategy_success_rates'][strategy]['attempts'] += 1
        if result.success:
            self.resolution_stats['strategy_success_rates'][strategy]['successes'] += 1
        
        # Update average resolution time
        total_conflicts = self.resolution_stats['total_conflicts']
        current_avg = self.resolution_stats['average_resolution_time']
        new_avg = (current_avg * (total_conflicts - 1) + result.resolution_duration) / total_conflicts
        self.resolution_stats['average_resolution_time'] = new_avg
    
    def get_resolution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive resolution statistics"""
        
        stats = self.resolution_stats.copy()
        
        # Calculate success rates
        if stats['total_conflicts'] > 0:
            stats['overall_success_rate'] = stats['resolved_conflicts'] / stats['total_conflicts']
        
        # Calculate strategy effectiveness
        for strategy, data in stats['strategy_success_rates'].items():
            if data['attempts'] > 0:
                data['success_rate'] = data['successes'] / data['attempts']
        
        return stats


# Demonstration and testing functions
async def demonstrate_conflict_resolution():
    """Demonstrate conflict resolution capabilities"""
    
    print("⚖️ Advanced Conflict Resolution Demonstration")
    print("=" * 55)
    
    # Initialize conflict resolver
    resolver = ConflictResolver(mediator_agent="mediator_1")
    
    # Register agent profiles
    agent_profiles = {
        "alpha_agent": {
            "cooperation_tendency": 0.8,
            "negotiation_style": NegotiationStyle.COLLABORATIVE.value,
            "influence_level": 0.7,
            "expertise_level": 0.9,
            "budget": 500.0
        },
        "beta_agent": {
            "cooperation_tendency": 0.6,
            "negotiation_style": NegotiationStyle.COMPETITIVE.value,
            "influence_level": 0.8,
            "expertise_level": 0.7,
            "budget": 800.0
        },
        "gamma_agent": {
            "cooperation_tendency": 0.9,
            "negotiation_style": NegotiationStyle.COMPROMISING.value,
            "influence_level": 0.5,
            "expertise_level": 0.8,
            "budget": 300.0
        }
    }
    
    for agent_id, profile in agent_profiles.items():
        resolver.register_agent_profile(agent_id, profile)
    
    print(f"👥 Registered {len(agent_profiles)} agent profiles")
    
    # Create test conflict scenarios
    conflicts = [
        ConflictScenario(
            conflict_type=ConflictType.RESOURCE_COMPETITION,
            involved_agents=["alpha_agent", "beta_agent"],
            disputed_items=["server_cluster_A", "budget_allocation_Q3"],
            agent_positions={
                "alpha_agent": {
                    "goals": ["maximize_efficiency", "reduce_costs"],
                    "preferences": {"server_cluster_A": 0.9, "budget_allocation_Q3": 0.6},
                    "constraints": ["deadline_pressure"]
                },
                "beta_agent": {
                    "goals": ["expand_capacity", "improve_performance"],
                    "preferences": {"server_cluster_A": 0.8, "budget_allocation_Q3": 0.9},
                    "constraints": ["budget_limits"]
                }
            },
            urgency_level=7
        ),
        ConflictScenario(
            conflict_type=ConflictType.STRATEGY_DISAGREEMENT,
            involved_agents=["alpha_agent", "beta_agent", "gamma_agent"],
            disputed_items=["project_direction", "resource_priority"],
            agent_positions={
                "alpha_agent": {
                    "goals": ["long_term_stability"],
                    "preferences": {"project_direction": 0.7, "resource_priority": 0.8}
                },
                "beta_agent": {
                    "goals": ["rapid_growth"],
                    "preferences": {"project_direction": 0.9, "resource_priority": 0.5}
                },
                "gamma_agent": {
                    "goals": ["balanced_approach"],
                    "preferences": {"project_direction": 0.5, "resource_priority": 0.7}
                }
            },
            urgency_level=5
        )
    ]
    
    # Test different resolution strategies
    strategies = [
        ResolutionStrategy.NEGOTIATION,
        ResolutionStrategy.MEDIATION,
        ResolutionStrategy.GAME_THEORY,
        ResolutionStrategy.WEIGHTED_COMPROMISE
    ]
    
    print(f"\n🎯 Testing Conflict Resolution Strategies:")
    print("-" * 50)
    
    results = []
    
    for i, (conflict, strategy) in enumerate(zip(conflicts, strategies)):
        print(f"\n🔍 Conflict {i+1}: {conflict.conflict_type.value}")
        print(f"   Agents: {', '.join(conflict.involved_agents)}")
        print(f"   Items: {', '.join(conflict.disputed_items)}")
        print(f"   Strategy: {strategy.value}")
        
        result = await resolver.resolve_conflict(
            conflict, strategy, timeout=timedelta(seconds=5)
        )
        
        results.append(result)
        
        print(f"   ✅ Success: {result.success}")
        if result.success:
            print(f"   📊 Overall satisfaction: {result.calculate_overall_satisfaction():.2f}")
            print(f"   ⚖️  Fairness score: {result.fairness_score:.2f}")
            print(f"   🔒 Stability score: {result.stability_score:.2f}")
            print(f"   ⏱️  Duration: {result.resolution_duration.total_seconds():.1f}s")
            
            # Show individual satisfaction scores
            if result.satisfaction_scores:
                print(f"   👥 Individual satisfaction:")
                for agent_id, score in result.satisfaction_scores.items():
                    print(f"      {agent_id}: {score:.2f}")
        else:
            print(f"   ❌ Resolution failed")
    
    # Show overall statistics
    print(f"\n📈 Conflict Resolution Statistics:")
    stats = resolver.get_resolution_statistics()
    print(f"   - Total conflicts: {stats['total_conflicts']}")
    print(f"   - Resolved conflicts: {stats['resolved_conflicts']}")
    print(f"   - Overall success rate: {stats.get('overall_success_rate', 0):.1%}")
    print(f"   - Average resolution time: {stats['average_resolution_time'].total_seconds():.1f}s")
    
    # Show strategy effectiveness
    print(f"\n🎯 Strategy Effectiveness:")
    for strategy, data in stats['strategy_success_rates'].items():
        success_rate = data.get('success_rate', 0)
        print(f"   {strategy}: {success_rate:.1%} success rate ({data['successes']}/{data['attempts']})")
    
    return {
        'resolver': resolver,
        'results': results,
        'statistics': stats
    }


if __name__ == "__main__":
    asyncio.run(demonstrate_conflict_resolution())