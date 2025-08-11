"""
Advanced Auction Mechanisms for Multi-Agent Task Allocation
Session 8: Competitive Coordination and Market-Based Resource Allocation

This module implements sophisticated auction algorithms for multi-agent systems
including sealed-bid, English, Dutch, and Vickrey auctions for optimal task
allocation and resource distribution.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import random
import logging
from datetime import datetime, timedelta
import uuid
import statistics
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuctionType(Enum):
    """Types of auction mechanisms"""
    SEALED_BID = "sealed_bid"
    ENGLISH = "english"
    DUTCH = "dutch"
    VICKREY = "vickrey"
    COMBINATORIAL = "combinatorial"
    MULTI_UNIT = "multi_unit"
    CONTINUOUS_DOUBLE = "continuous_double"


class BidStatus(Enum):
    """Status of auction bids"""
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    WINNING = "winning"
    LOSING = "losing"


class AuctionStatus(Enum):
    """Status of auction process"""
    PENDING = "pending"
    ACTIVE = "active"
    BIDDING_CLOSED = "bidding_closed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class TaskSpecification:
    """Specification of task to be auctioned"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    requirements: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    deliverables: List[str] = field(default_factory=list)
    estimated_effort: timedelta = field(default_factory=lambda: timedelta(hours=1))
    deadline: Optional[datetime] = None
    budget_range: Tuple[float, float] = (0.0, 1000.0)
    quality_requirements: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task specification to dictionary"""
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements,
            'constraints': self.constraints,
            'deliverables': self.deliverables,
            'estimated_effort': self.estimated_effort.total_seconds(),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'budget_range': self.budget_range,
            'quality_requirements': self.quality_requirements,
            'priority': self.priority
        }


@dataclass
class AgentCapabilities:
    """Represents agent capabilities for auction participation"""
    agent_id: str = ""
    skills: List[str] = field(default_factory=list)
    skill_levels: Dict[str, float] = field(default_factory=dict)  # 0.0 to 1.0
    capacity: int = 1  # Number of concurrent tasks
    current_load: int = 0
    cost_per_hour: float = 50.0
    availability_window: Tuple[datetime, datetime] = field(default_factory=lambda: (datetime.now(), datetime.now() + timedelta(days=30)))
    quality_rating: float = 0.8  # Historical quality score
    reliability_score: float = 0.9  # Completion rate
    specializations: List[str] = field(default_factory=list)
    geographic_location: Optional[str] = None
    
    def matches_requirements(self, task_requirements: Dict[str, Any]) -> Tuple[bool, float]:
        """Check if agent capabilities match task requirements"""
        
        required_skills = task_requirements.get('skills', [])
        
        # Check if agent has required skills
        missing_skills = []
        skill_match_score = 0.0
        
        if required_skills:
            for skill in required_skills:
                if skill in self.skills:
                    skill_level = self.skill_levels.get(skill, 0.5)
                    skill_match_score += skill_level
                else:
                    missing_skills.append(skill)
            
            skill_match_score = skill_match_score / len(required_skills)
        else:
            skill_match_score = 1.0  # No specific skills required
        
        # Check capacity
        has_capacity = self.current_load < self.capacity
        
        # Check availability
        task_deadline = task_requirements.get('deadline')
        available_in_time = True
        if task_deadline:
            available_in_time = self.availability_window[0] <= task_deadline <= self.availability_window[1]
        
        # Overall match
        matches = len(missing_skills) == 0 and has_capacity and available_in_time
        
        # Calculate match score considering multiple factors
        capacity_score = (self.capacity - self.current_load) / self.capacity if self.capacity > 0 else 0
        match_score = (skill_match_score * 0.6 + capacity_score * 0.2 + 
                      self.quality_rating * 0.1 + self.reliability_score * 0.1)
        
        return matches, match_score


@dataclass
class AuctionBid:
    """Represents a bid in an auction"""
    bid_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    auction_id: str = ""
    bidder_id: str = ""
    bid_amount: float = 0.0
    proposed_timeline: timedelta = field(default_factory=lambda: timedelta(hours=1))
    quality_commitment: Dict[str, Any] = field(default_factory=dict)
    additional_terms: Dict[str, Any] = field(default_factory=dict)
    bid_timestamp: datetime = field(default_factory=datetime.now)
    status: BidStatus = BidStatus.SUBMITTED
    confidence_level: float = 0.8
    risk_premium: float = 0.0
    
    # Bid evaluation metrics
    value_score: float = 0.0
    quality_score: float = 0.0
    timeline_score: float = 0.0
    overall_score: float = 0.0
    
    def calculate_total_cost(self) -> float:
        """Calculate total cost including risk premium"""
        return self.bid_amount * (1 + self.risk_premium)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert bid to dictionary"""
        return {
            'bid_id': self.bid_id,
            'auction_id': self.auction_id,
            'bidder_id': self.bidder_id,
            'bid_amount': self.bid_amount,
            'proposed_timeline': self.proposed_timeline.total_seconds(),
            'quality_commitment': self.quality_commitment,
            'bid_timestamp': self.bid_timestamp.isoformat(),
            'status': self.status.value,
            'confidence_level': self.confidence_level,
            'overall_score': self.overall_score
        }


@dataclass
class AuctionResult:
    """Results of a completed auction"""
    auction_id: str = ""
    task_specification: Optional[TaskSpecification] = None
    winning_bid: Optional[AuctionBid] = None
    all_bids: List[AuctionBid] = field(default_factory=list)
    auction_duration: timedelta = field(default_factory=timedelta)
    completion_timestamp: datetime = field(default_factory=datetime.now)
    auction_type: AuctionType = AuctionType.SEALED_BID
    success: bool = False
    failure_reason: Optional[str] = None
    auction_statistics: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_statistics(self):
        """Calculate auction statistics"""
        if not self.all_bids:
            return
        
        bid_amounts = [bid.bid_amount for bid in self.all_bids]
        
        self.auction_statistics = {
            'total_bidders': len(self.all_bids),
            'average_bid': statistics.mean(bid_amounts),
            'median_bid': statistics.median(bid_amounts),
            'bid_range': (min(bid_amounts), max(bid_amounts)),
            'winning_bid_rank': self._get_winning_bid_rank(),
            'participation_rate': len(self.all_bids),  # Would need total invited agents
            'auction_efficiency': self._calculate_efficiency_score()
        }
    
    def _get_winning_bid_rank(self) -> int:
        """Get rank of winning bid by amount (1 = lowest)"""
        if not self.winning_bid or not self.all_bids:
            return 0
        
        sorted_bids = sorted(self.all_bids, key=lambda b: b.bid_amount)
        for i, bid in enumerate(sorted_bids):
            if bid.bid_id == self.winning_bid.bid_id:
                return i + 1
        return 0
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate auction efficiency score"""
        if not self.winning_bid or not self.all_bids:
            return 0.0
        
        # Efficiency based on winning bid's overall score
        return self.winning_bid.overall_score


class BaseAuction(ABC):
    """Abstract base class for auction mechanisms"""
    
    def __init__(self, auction_id: str, task_spec: TaskSpecification, 
                 auction_type: AuctionType):
        self.auction_id = auction_id
        self.task_specification = task_spec
        self.auction_type = auction_type
        self.status = AuctionStatus.PENDING
        self.bids: List[AuctionBid] = []
        self.eligible_agents: List[str] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.bidding_deadline: Optional[datetime] = None
        
    @abstractmethod
    async def conduct_auction(self, agents: Dict[str, AgentCapabilities], 
                            auction_duration: timedelta) -> AuctionResult:
        """Conduct the auction process"""
        pass
    
    @abstractmethod
    async def evaluate_bids(self) -> Optional[AuctionBid]:
        """Evaluate bids and select winner"""
        pass
    
    def add_bid(self, bid: AuctionBid) -> bool:
        """Add bid to auction"""
        if self.status != AuctionStatus.ACTIVE:
            return False
        
        if datetime.now() > self.bidding_deadline:
            return False
        
        self.bids.append(bid)
        return True
    
    def get_eligible_agents(self, agents: Dict[str, AgentCapabilities]) -> List[str]:
        """Determine which agents are eligible to participate"""
        eligible = []
        
        for agent_id, capabilities in agents.items():
            matches, match_score = capabilities.matches_requirements(
                self.task_specification.requirements
            )
            if matches and match_score >= 0.5:  # Minimum match threshold
                eligible.append(agent_id)
        
        return eligible


class SealedBidAuction(BaseAuction):
    """Sealed-bid auction implementation"""
    
    def __init__(self, auction_id: str, task_spec: TaskSpecification):
        super().__init__(auction_id, task_spec, AuctionType.SEALED_BID)
    
    async def conduct_auction(self, agents: Dict[str, AgentCapabilities], 
                            auction_duration: timedelta) -> AuctionResult:
        """Conduct sealed-bid auction"""
        
        logger.info(f"Starting sealed-bid auction {self.auction_id}")
        self.start_time = datetime.now()
        self.status = AuctionStatus.ACTIVE
        self.bidding_deadline = self.start_time + auction_duration
        
        # Determine eligible agents
        self.eligible_agents = self.get_eligible_agents(agents)
        
        if not self.eligible_agents:
            return AuctionResult(
                auction_id=self.auction_id,
                success=False,
                failure_reason="No eligible agents found"
            )
        
        # Collect sealed bids
        await self._collect_sealed_bids(agents)
        
        # Close bidding
        self.status = AuctionStatus.BIDDING_CLOSED
        
        # Evaluate bids
        winning_bid = await self.evaluate_bids()
        
        # Create result
        self.end_time = datetime.now()
        self.status = AuctionStatus.COMPLETED if winning_bid else AuctionStatus.FAILED
        
        result = AuctionResult(
            auction_id=self.auction_id,
            task_specification=self.task_specification,
            winning_bid=winning_bid,
            all_bids=self.bids,
            auction_duration=self.end_time - self.start_time,
            auction_type=self.auction_type,
            success=winning_bid is not None,
            failure_reason="No valid bids received" if not winning_bid else None
        )
        
        result.calculate_statistics()
        
        logger.info(f"Sealed-bid auction {self.auction_id} completed. Winner: {winning_bid.bidder_id if winning_bid else 'None'}")
        
        return result
    
    async def _collect_sealed_bids(self, agents: Dict[str, AgentCapabilities]):
        """Collect sealed bids from eligible agents"""
        
        bid_tasks = []
        for agent_id in self.eligible_agents:
            task = self._request_bid_from_agent(agent_id, agents[agent_id])
            bid_tasks.append(task)
        
        # Wait for all bids or timeout
        bids = await asyncio.gather(*bid_tasks, return_exceptions=True)
        
        # Process valid bids
        for bid in bids:
            if isinstance(bid, AuctionBid):
                self.add_bid(bid)
    
    async def _request_bid_from_agent(self, agent_id: str, 
                                    capabilities: AgentCapabilities) -> Optional[AuctionBid]:
        """Request bid from specific agent"""
        
        # Simulate bid generation based on agent capabilities
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate thinking time
        
        # Agent decides whether to bid
        matches, match_score = capabilities.matches_requirements(
            self.task_specification.requirements
        )
        
        if not matches or random.random() < 0.3:  # 30% chance of not bidding
            return None
        
        # Calculate bid amount
        base_cost = capabilities.cost_per_hour * (
            self.task_specification.estimated_effort.total_seconds() / 3600
        )
        
        # Add margin based on various factors
        complexity_factor = 1.0 + (1.0 - match_score) * 0.5  # Higher price for complex tasks
        capacity_factor = 1.0 + (capabilities.current_load / capabilities.capacity) * 0.3
        quality_factor = 1.0 + (capabilities.quality_rating - 0.5) * 0.2
        
        bid_amount = base_cost * complexity_factor * capacity_factor * quality_factor
        
        # Add some randomness
        bid_amount *= random.uniform(0.9, 1.1)
        
        # Ensure bid is within budget range
        min_budget, max_budget = self.task_specification.budget_range
        bid_amount = max(min_budget, min(bid_amount, max_budget))
        
        # Create bid
        bid = AuctionBid(
            auction_id=self.auction_id,
            bidder_id=agent_id,
            bid_amount=bid_amount,
            proposed_timeline=self.task_specification.estimated_effort * random.uniform(0.8, 1.2),
            quality_commitment={
                'expected_quality': capabilities.quality_rating,
                'guarantees': ['on_time_delivery', 'quality_standards']
            },
            confidence_level=match_score * capabilities.reliability_score,
            risk_premium=random.uniform(0.0, 0.1)  # 0-10% risk premium
        )
        
        return bid
    
    async def evaluate_bids(self) -> Optional[AuctionBid]:
        """Evaluate sealed bids and select winner"""
        
        if not self.bids:
            return None
        
        # Score each bid
        for bid in self.bids:
            await self._score_bid(bid)
        
        # Select highest scoring bid
        winning_bid = max(self.bids, key=lambda b: b.overall_score)
        winning_bid.status = BidStatus.WINNING
        
        # Mark other bids as losing
        for bid in self.bids:
            if bid.bid_id != winning_bid.bid_id:
                bid.status = BidStatus.LOSING
        
        return winning_bid
    
    async def _score_bid(self, bid: AuctionBid):
        """Score a bid based on multiple criteria"""
        
        # Value score (lower cost is better)
        min_budget, max_budget = self.task_specification.budget_range
        if max_budget > min_budget:
            bid.value_score = 1.0 - (bid.bid_amount - min_budget) / (max_budget - min_budget)
        else:
            bid.value_score = 1.0 if bid.bid_amount <= max_budget else 0.0
        
        # Timeline score (faster delivery is better)
        expected_timeline = self.task_specification.estimated_effort
        if expected_timeline.total_seconds() > 0:
            bid.timeline_score = min(1.0, expected_timeline.total_seconds() / 
                                   bid.proposed_timeline.total_seconds())
        else:
            bid.timeline_score = 1.0
        
        # Quality score based on commitment
        bid.quality_score = bid.quality_commitment.get('expected_quality', 0.5)
        
        # Combined score with weights
        bid.overall_score = (
            bid.value_score * 0.4 +
            bid.timeline_score * 0.3 +
            bid.quality_score * 0.2 +
            bid.confidence_level * 0.1
        )


class EnglishAuction(BaseAuction):
    """English (ascending) auction implementation"""
    
    def __init__(self, auction_id: str, task_spec: TaskSpecification):
        super().__init__(auction_id, task_spec, AuctionType.ENGLISH)
        self.current_highest_bid: Optional[AuctionBid] = None
        self.bid_increment = 10.0
        self.round_duration = timedelta(seconds=30)
    
    async def conduct_auction(self, agents: Dict[str, AgentCapabilities], 
                            auction_duration: timedelta) -> AuctionResult:
        """Conduct English auction with ascending bids"""
        
        logger.info(f"Starting English auction {self.auction_id}")
        self.start_time = datetime.now()
        self.status = AuctionStatus.ACTIVE
        self.bidding_deadline = self.start_time + auction_duration
        
        # Determine eligible agents
        self.eligible_agents = self.get_eligible_agents(agents)
        
        if not self.eligible_agents:
            return AuctionResult(
                auction_id=self.auction_id,
                success=False,
                failure_reason="No eligible agents found"
            )
        
        # Start with minimum bid
        min_budget, _ = self.task_specification.budget_range
        current_bid_amount = min_budget
        
        # Conduct bidding rounds
        while datetime.now() < self.bidding_deadline:
            round_start = datetime.now()
            round_end = round_start + self.round_duration
            
            # Collect bids for this round
            round_bids = await self._collect_round_bids(
                agents, current_bid_amount, round_end
            )
            
            if not round_bids:
                # No new bids, auction ends
                break
            
            # Find highest bid in this round
            highest_round_bid = max(round_bids, key=lambda b: b.bid_amount)
            
            if (not self.current_highest_bid or 
                highest_round_bid.bid_amount > self.current_highest_bid.bid_amount):
                self.current_highest_bid = highest_round_bid
                current_bid_amount = highest_round_bid.bid_amount + self.bid_increment
            
            # Add bids to history
            self.bids.extend(round_bids)
            
            # Small delay between rounds
            await asyncio.sleep(0.1)
        
        # Auction complete
        self.end_time = datetime.now()
        self.status = AuctionStatus.COMPLETED if self.current_highest_bid else AuctionStatus.FAILED
        
        if self.current_highest_bid:
            self.current_highest_bid.status = BidStatus.WINNING
        
        result = AuctionResult(
            auction_id=self.auction_id,
            task_specification=self.task_specification,
            winning_bid=self.current_highest_bid,
            all_bids=self.bids,
            auction_duration=self.end_time - self.start_time,
            auction_type=self.auction_type,
            success=self.current_highest_bid is not None
        )
        
        result.calculate_statistics()
        
        logger.info(f"English auction {self.auction_id} completed. Winner: {self.current_highest_bid.bidder_id if self.current_highest_bid else 'None'}")
        
        return result
    
    async def _collect_round_bids(self, agents: Dict[str, AgentCapabilities],
                                 minimum_bid: float, round_end: datetime) -> List[AuctionBid]:
        """Collect bids for current round"""
        
        round_bids = []
        
        # Each eligible agent decides whether to bid
        for agent_id in self.eligible_agents:
            if datetime.now() >= round_end:
                break
            
            # Agent decides whether to increase bid
            should_bid = await self._agent_should_bid(
                agent_id, agents[agent_id], minimum_bid
            )
            
            if should_bid:
                bid_amount = minimum_bid + random.uniform(0, self.bid_increment * 2)
                
                # Ensure within budget
                _, max_budget = self.task_specification.budget_range
                bid_amount = min(bid_amount, max_budget)
                
                if bid_amount >= minimum_bid:
                    bid = AuctionBid(
                        auction_id=self.auction_id,
                        bidder_id=agent_id,
                        bid_amount=bid_amount,
                        proposed_timeline=self.task_specification.estimated_effort,
                        confidence_level=random.uniform(0.6, 0.9)
                    )
                    round_bids.append(bid)
        
        return round_bids
    
    async def _agent_should_bid(self, agent_id: str, capabilities: AgentCapabilities,
                               minimum_bid: float) -> bool:
        """Determine if agent should place a bid in this round"""
        
        # Simple strategy: bid if cost is below valuation
        estimated_cost = capabilities.cost_per_hour * (
            self.task_specification.estimated_effort.total_seconds() / 3600
        )
        
        # Add profit margin
        target_price = estimated_cost * 1.3
        
        # Bid if minimum bid is below target price and some probability
        return minimum_bid <= target_price and random.random() > 0.4
    
    async def evaluate_bids(self) -> Optional[AuctionBid]:
        """For English auction, winner is already determined during process"""
        return self.current_highest_bid


class VickreyAuction(BaseAuction):
    """Vickrey (second-price sealed-bid) auction implementation"""
    
    def __init__(self, auction_id: str, task_spec: TaskSpecification):
        super().__init__(auction_id, task_spec, AuctionType.VICKREY)
    
    async def conduct_auction(self, agents: Dict[str, AgentCapabilities], 
                            auction_duration: timedelta) -> AuctionResult:
        """Conduct Vickrey auction"""
        
        logger.info(f"Starting Vickrey auction {self.auction_id}")
        self.start_time = datetime.now()
        self.status = AuctionStatus.ACTIVE
        self.bidding_deadline = self.start_time + auction_duration
        
        # Determine eligible agents
        self.eligible_agents = self.get_eligible_agents(agents)
        
        if not self.eligible_agents:
            return AuctionResult(
                auction_id=self.auction_id,
                success=False,
                failure_reason="No eligible agents found"
            )
        
        # Collect sealed bids (similar to sealed-bid auction)
        await self._collect_sealed_bids(agents)
        
        # Close bidding
        self.status = AuctionStatus.BIDDING_CLOSED
        
        # Evaluate bids using Vickrey rules
        winning_bid = await self.evaluate_bids()
        
        # Create result
        self.end_time = datetime.now()
        self.status = AuctionStatus.COMPLETED if winning_bid else AuctionStatus.FAILED
        
        result = AuctionResult(
            auction_id=self.auction_id,
            task_specification=self.task_specification,
            winning_bid=winning_bid,
            all_bids=self.bids,
            auction_duration=self.end_time - self.start_time,
            auction_type=self.auction_type,
            success=winning_bid is not None,
            failure_reason="No valid bids received" if not winning_bid else None
        )
        
        result.calculate_statistics()
        
        logger.info(f"Vickrey auction {self.auction_id} completed. Winner: {winning_bid.bidder_id if winning_bid else 'None'}")
        
        return result
    
    async def _collect_sealed_bids(self, agents: Dict[str, AgentCapabilities]):
        """Collect sealed bids (agents bid their true valuations)"""
        
        bid_tasks = []
        for agent_id in self.eligible_agents:
            task = self._request_truthful_bid_from_agent(agent_id, agents[agent_id])
            bid_tasks.append(task)
        
        # Wait for all bids or timeout
        bids = await asyncio.gather(*bid_tasks, return_exceptions=True)
        
        # Process valid bids
        for bid in bids:
            if isinstance(bid, AuctionBid):
                self.add_bid(bid)
    
    async def _request_truthful_bid_from_agent(self, agent_id: str, 
                                             capabilities: AgentCapabilities) -> Optional[AuctionBid]:
        """Request truthful bid from agent (Vickrey incentivizes truth-telling)"""
        
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Agent decides whether to bid
        matches, match_score = capabilities.matches_requirements(
            self.task_specification.requirements
        )
        
        if not matches or random.random() < 0.2:  # 20% chance of not bidding
            return None
        
        # Calculate true valuation (what the task is worth to the agent)
        base_cost = capabilities.cost_per_hour * (
            self.task_specification.estimated_effort.total_seconds() / 3600
        )
        
        # True valuation includes potential profit and strategic value
        profit_margin = random.uniform(0.2, 0.5)  # 20-50% profit margin
        strategic_value = match_score * 0.3  # Strategic value based on fit
        
        true_valuation = base_cost * (1 + profit_margin + strategic_value)
        
        # In Vickrey auctions, agents are incentivized to bid their true valuation
        bid_amount = true_valuation
        
        # Ensure within budget range
        min_budget, max_budget = self.task_specification.budget_range
        bid_amount = max(min_budget, min(bid_amount, max_budget))
        
        bid = AuctionBid(
            auction_id=self.auction_id,
            bidder_id=agent_id,
            bid_amount=bid_amount,
            proposed_timeline=self.task_specification.estimated_effort * random.uniform(0.9, 1.1),
            quality_commitment={
                'expected_quality': capabilities.quality_rating,
                'guarantees': ['truthful_bidding']
            },
            confidence_level=match_score,
            additional_terms={'true_valuation': true_valuation}
        )
        
        return bid
    
    async def evaluate_bids(self) -> Optional[AuctionBid]:
        """Evaluate bids using Vickrey (second-price) rules"""
        
        if len(self.bids) < 2:
            # Need at least 2 bids for Vickrey auction
            if self.bids:
                winning_bid = self.bids[0]
                winning_bid.status = BidStatus.WINNING
                # Winner pays their own bid if only one bidder
                return winning_bid
            return None
        
        # Sort bids by amount (descending)
        sorted_bids = sorted(self.bids, key=lambda b: b.bid_amount, reverse=True)
        
        # Winner is highest bidder
        winning_bid = sorted_bids[0]
        second_highest_bid = sorted_bids[1]
        
        # But winner pays second-highest price (Vickrey rule)
        original_amount = winning_bid.bid_amount
        winning_bid.bid_amount = second_highest_bid.bid_amount
        winning_bid.status = BidStatus.WINNING
        
        # Store original bid for analysis
        winning_bid.additional_terms['original_bid'] = original_amount
        winning_bid.additional_terms['second_price_savings'] = original_amount - second_highest_bid.bid_amount
        
        # Mark other bids as losing
        for bid in self.bids:
            if bid.bid_id != winning_bid.bid_id:
                bid.status = BidStatus.LOSING
        
        return winning_bid


class AuctionCoordinator:
    """Coordinates multiple auction mechanisms for task allocation"""
    
    def __init__(self):
        self.active_auctions: Dict[str, BaseAuction] = {}
        self.completed_auctions: List[AuctionResult] = []
        self.agents: Dict[str, AgentCapabilities] = {}
        self.auction_statistics = {
            'total_auctions': 0,
            'successful_auctions': 0,
            'total_value_allocated': 0.0,
            'average_auction_duration': timedelta(0),
            'auction_type_usage': {}
        }
    
    def register_agent(self, agent_id: str, capabilities: AgentCapabilities):
        """Register agent for auction participation"""
        self.agents[agent_id] = capabilities
        logger.info(f"Registered agent {agent_id} for auction participation")
    
    async def conduct_task_auction(self, task_spec: TaskSpecification, 
                                  auction_type: AuctionType = AuctionType.SEALED_BID,
                                  auction_duration: timedelta = timedelta(minutes=5)) -> AuctionResult:
        """Conduct auction for task allocation"""
        
        auction_id = str(uuid.uuid4())
        logger.info(f"Starting {auction_type.value} auction for task: {task_spec.title}")
        
        # Create appropriate auction instance
        if auction_type == AuctionType.SEALED_BID:
            auction = SealedBidAuction(auction_id, task_spec)
        elif auction_type == AuctionType.ENGLISH:
            auction = EnglishAuction(auction_id, task_spec)
        elif auction_type == AuctionType.VICKREY:
            auction = VickreyAuction(auction_id, task_spec)
        else:
            raise ValueError(f"Unsupported auction type: {auction_type}")
        
        # Track active auction
        self.active_auctions[auction_id] = auction
        
        # Conduct auction
        result = await auction.conduct_auction(self.agents, auction_duration)
        
        # Update statistics
        self._update_statistics(result)
        
        # Store completed auction
        self.completed_auctions.append(result)
        del self.active_auctions[auction_id]
        
        return result
    
    def _update_statistics(self, result: AuctionResult):
        """Update auction statistics"""
        
        self.auction_statistics['total_auctions'] += 1
        
        if result.success:
            self.auction_statistics['successful_auctions'] += 1
            if result.winning_bid:
                self.auction_statistics['total_value_allocated'] += result.winning_bid.bid_amount
        
        # Update average duration
        total_auctions = self.auction_statistics['total_auctions']
        current_avg = self.auction_statistics['average_auction_duration']
        new_avg = (current_avg * (total_auctions - 1) + result.auction_duration) / total_auctions
        self.auction_statistics['average_auction_duration'] = new_avg
        
        # Update auction type usage
        auction_type = result.auction_type.value
        if auction_type not in self.auction_statistics['auction_type_usage']:
            self.auction_statistics['auction_type_usage'][auction_type] = 0
        self.auction_statistics['auction_type_usage'][auction_type] += 1
    
    async def batch_task_allocation(self, tasks: List[TaskSpecification],
                                   allocation_strategy: str = "optimal") -> List[AuctionResult]:
        """Allocate multiple tasks using batch auction strategy"""
        
        logger.info(f"Starting batch allocation for {len(tasks)} tasks")
        
        results = []
        
        if allocation_strategy == "sequential":
            # Allocate tasks one by one
            for task in tasks:
                result = await self.conduct_task_auction(task)
                results.append(result)
                
                # Update agent availability if task was allocated
                if result.success and result.winning_bid:
                    winning_agent = self.agents[result.winning_bid.bidder_id]
                    winning_agent.current_load += 1
        
        elif allocation_strategy == "parallel":
            # Run multiple auctions in parallel
            auction_tasks = []
            for task in tasks:
                auction_task = self.conduct_task_auction(task)
                auction_tasks.append(auction_task)
            
            results = await asyncio.gather(*auction_tasks)
        
        elif allocation_strategy == "optimal":
            # Use combinatorial optimization (simplified)
            results = await self._optimal_task_allocation(tasks)
        
        logger.info(f"Batch allocation completed. {sum(1 for r in results if r.success)}/{len(tasks)} tasks allocated")
        
        return results
    
    async def _optimal_task_allocation(self, tasks: List[TaskSpecification]) -> List[AuctionResult]:
        """Optimal task allocation using simplified combinatorial approach"""
        
        # For demonstration, use sequential allocation with best auction type selection
        results = []
        
        for task in tasks:
            # Choose best auction type based on task characteristics
            best_auction_type = self._select_optimal_auction_type(task)
            
            result = await self.conduct_task_auction(task, best_auction_type)
            results.append(result)
            
            # Update agent state
            if result.success and result.winning_bid:
                winning_agent = self.agents[result.winning_bid.bidder_id]
                winning_agent.current_load += 1
        
        return results
    
    def _select_optimal_auction_type(self, task: TaskSpecification) -> AuctionType:
        """Select optimal auction type based on task characteristics"""
        
        # Simple heuristics for auction type selection
        eligible_agents = len([
            agent for agent in self.agents.values()
            if agent.matches_requirements(task.requirements)[0]
        ])
        
        if eligible_agents < 3:
            # Few agents - use sealed bid
            return AuctionType.SEALED_BID
        elif task.priority > 7:
            # High priority - use Vickrey for efficiency
            return AuctionType.VICKREY
        elif eligible_agents > 5:
            # Many agents - use English auction for price discovery
            return AuctionType.ENGLISH
        else:
            return AuctionType.SEALED_BID
    
    def get_auction_statistics(self) -> Dict[str, Any]:
        """Get comprehensive auction statistics"""
        
        stats = self.auction_statistics.copy()
        
        # Add derived statistics
        if stats['total_auctions'] > 0:
            stats['success_rate'] = stats['successful_auctions'] / stats['total_auctions']
            stats['average_task_value'] = (
                stats['total_value_allocated'] / stats['successful_auctions']
                if stats['successful_auctions'] > 0 else 0
            )
        
        # Add agent statistics
        stats['total_agents'] = len(self.agents)
        stats['active_agents'] = len([
            agent for agent in self.agents.values() 
            if agent.current_load < agent.capacity
        ])
        
        return stats
    
    def get_agent_performance_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get performance summary for each agent"""
        
        agent_performance = {}
        
        for agent_id, capabilities in self.agents.items():
            wins = sum(
                1 for auction in self.completed_auctions
                if auction.winning_bid and auction.winning_bid.bidder_id == agent_id
            )
            
            total_bids = sum(
                1 for auction in self.completed_auctions
                for bid in auction.all_bids
                if bid.bidder_id == agent_id
            )
            
            agent_performance[agent_id] = {
                'wins': wins,
                'total_bids': total_bids,
                'win_rate': wins / total_bids if total_bids > 0 else 0,
                'current_load': capabilities.current_load,
                'capacity_utilization': capabilities.current_load / capabilities.capacity,
                'quality_rating': capabilities.quality_rating
            }
        
        return agent_performance


# Demonstration and testing functions
async def demonstrate_auction_mechanisms():
    """Demonstrate various auction mechanisms"""
    
    print("🎯 Advanced Auction Mechanisms Demonstration")
    print("=" * 55)
    
    # Create auction coordinator
    coordinator = AuctionCoordinator()
    
    # Create diverse agent capabilities
    agents = [
        AgentCapabilities(
            agent_id="data_analyst_1",
            skills=["data_analysis", "python", "statistics"],
            skill_levels={"data_analysis": 0.9, "python": 0.8, "statistics": 0.9},
            capacity=3,
            current_load=1,
            cost_per_hour=60.0,
            quality_rating=0.9,
            reliability_score=0.95
        ),
        AgentCapabilities(
            agent_id="ml_engineer_1",
            skills=["machine_learning", "python", "tensorflow"],
            skill_levels={"machine_learning": 0.95, "python": 0.9, "tensorflow": 0.8},
            capacity=2,
            current_load=0,
            cost_per_hour=80.0,
            quality_rating=0.85,
            reliability_score=0.9
        ),
        AgentCapabilities(
            agent_id="data_scientist_1",
            skills=["data_analysis", "machine_learning", "r", "python"],
            skill_levels={"data_analysis": 0.8, "machine_learning": 0.85, "r": 0.9, "python": 0.7},
            capacity=2,
            current_load=0,
            cost_per_hour=70.0,
            quality_rating=0.88,
            reliability_score=0.92
        ),
        AgentCapabilities(
            agent_id="junior_analyst_1",
            skills=["data_analysis", "excel", "sql"],
            skill_levels={"data_analysis": 0.6, "excel": 0.8, "sql": 0.7},
            capacity=4,
            current_load=1,
            cost_per_hour=35.0,
            quality_rating=0.7,
            reliability_score=0.85
        ),
        AgentCapabilities(
            agent_id="senior_consultant_1",
            skills=["data_analysis", "strategy", "python", "machine_learning"],
            skill_levels={"data_analysis": 0.9, "strategy": 0.95, "python": 0.8, "machine_learning": 0.7},
            capacity=1,
            current_load=0,
            cost_per_hour=120.0,
            quality_rating=0.95,
            reliability_score=0.98
        )
    ]
    
    # Register agents
    for agent in agents:
        coordinator.register_agent(agent.agent_id, agent)
    
    print(f"📊 Registered {len(agents)} agents with diverse capabilities")
    
    # Create test tasks
    tasks = [
        TaskSpecification(
            title="Customer Segmentation Analysis",
            description="Analyze customer data to identify distinct segments for targeted marketing",
            requirements={
                "skills": ["data_analysis", "python", "statistics"],
                "deadline": datetime.now() + timedelta(days=7)
            },
            estimated_effort=timedelta(hours=20),
            budget_range=(800.0, 1500.0),
            priority=8
        ),
        TaskSpecification(
            title="Predictive Model Development",
            description="Develop machine learning model for sales forecasting",
            requirements={
                "skills": ["machine_learning", "python"],
                "deadline": datetime.now() + timedelta(days=14)
            },
            estimated_effort=timedelta(hours=30),
            budget_range=(1500.0, 2500.0),
            priority=9
        ),
        TaskSpecification(
            title="Market Research Dashboard",
            description="Create interactive dashboard for market research insights",
            requirements={
                "skills": ["data_analysis", "visualization"],
                "deadline": datetime.now() + timedelta(days=10)
            },
            estimated_effort=timedelta(hours=15),
            budget_range=(600.0, 1200.0),
            priority=6
        )
    ]
    
    # Test different auction mechanisms
    auction_types = [AuctionType.SEALED_BID, AuctionType.ENGLISH, AuctionType.VICKREY]
    
    print(f"\n🎯 Testing Different Auction Mechanisms:")
    print("-" * 40)
    
    results = {}
    
    for i, auction_type in enumerate(auction_types):
        task = tasks[i % len(tasks)]
        print(f"\n🔍 {auction_type.value.upper()} Auction for: {task.title}")
        
        result = await coordinator.conduct_task_auction(
            task, auction_type, auction_duration=timedelta(seconds=2)
        )
        
        results[auction_type.value] = result
        
        print(f"✅ Success: {result.success}")
        if result.success and result.winning_bid:
            print(f"🏆 Winner: {result.winning_bid.bidder_id}")
            print(f"💰 Winning bid: ${result.winning_bid.bid_amount:.2f}")
            print(f"📊 Bidders: {result.auction_statistics['total_bidders']}")
            print(f"⏱️  Duration: {result.auction_duration.total_seconds():.1f}s")
            
            # Special info for Vickrey auctions
            if auction_type == AuctionType.VICKREY and 'second_price_savings' in result.winning_bid.additional_terms:
                savings = result.winning_bid.additional_terms['second_price_savings']
                print(f"💡 Second-price savings: ${savings:.2f}")
        else:
            print(f"❌ Reason: {result.failure_reason}")
    
    # Test batch allocation
    print(f"\n📦 Testing Batch Task Allocation:")
    print("-" * 40)
    
    batch_results = await coordinator.batch_task_allocation(
        tasks, allocation_strategy="optimal"
    )
    
    successful_allocations = sum(1 for r in batch_results if r.success)
    total_value = sum(r.winning_bid.bid_amount for r in batch_results if r.success and r.winning_bid)
    
    print(f"✅ Allocated: {successful_allocations}/{len(tasks)} tasks")
    print(f"💰 Total value: ${total_value:.2f}")
    
    # Show overall statistics
    print(f"\n📈 Auction System Statistics:")
    stats = coordinator.get_auction_statistics()
    print(f"   - Total auctions: {stats['total_auctions']}")
    print(f"   - Success rate: {stats['success_rate']:.1%}")
    print(f"   - Average task value: ${stats['average_task_value']:.2f}")
    print(f"   - Average duration: {stats['average_auction_duration'].total_seconds():.1f}s")
    
    # Show agent performance
    print(f"\n👥 Agent Performance Summary:")
    agent_performance = coordinator.get_agent_performance_summary()
    for agent_id, performance in agent_performance.items():
        print(f"   {agent_id}:")
        print(f"      Wins: {performance['wins']}, Win rate: {performance['win_rate']:.1%}")
        print(f"      Load: {performance['current_load']}/{coordinator.agents[agent_id].capacity}")
    
    return {
        'coordinator': coordinator,
        'auction_results': results,
        'batch_results': batch_results,
        'statistics': stats
    }


if __name__ == "__main__":
    asyncio.run(demonstrate_auction_mechanisms())