# Session 9 - Module A: Test Solutions

**Question 1:** Byzantine Fault Tolerance Node Requirements  

**Explanation**: Byzantine Fault Tolerance requires 3f + 1 nodes to tolerate f Byzantine faults. This is a fundamental mathematical requirement in distributed systems. With 3f + 1 nodes, even if f nodes behave maliciously (Byzantine faults), there are still 2f + 1 honest nodes remaining. Since honest nodes always outnumber Byzantine nodes, consensus can be achieved. The formula ensures that any two quorums of 2f + 1 nodes will overlap in at least f + 1 honest nodes, maintaining consistency.

**Question 2:** Vickrey Auction Strategy-Proof Property  

**Explanation**: Vickrey auctions are strategy-proof because winners pay the second-highest bid, not their own bid. This payment rule removes the incentive to bid anything other than one's true valuation. If you bid higher than your true value and win, you risk paying more than the item is worth to you. If you bid lower and lose, you might miss out on profitable opportunities. The second-price mechanism makes truthful bidding the dominant strategy.

**Question 3:** Shapley Value in Cooperative Game Theory  

**Explanation**: The Shapley value represents each player's fair share based on their marginal contribution to all possible coalitions. It's calculated by averaging a player's marginal contribution across all possible orderings of coalition formation. The Shapley value satisfies important fairness axioms: efficiency (the sum equals total value), symmetry (identical players get identical payoffs), dummy (non-contributors get zero), and additivity (values add linearly across games).

**Question 4:** pBFT Prepare Phase Purpose  

**Explanation**: The prepare phase is the first phase of the three-phase pBFT protocol where the primary broadcasts a PREPARE message containing the client request to all backup nodes. The goal is to collect PREPARE responses from 2f+1 nodes (including the primary) to ensure that enough honest nodes have received and agreed to process the request. This phase establishes agreement on the request ordering and content before moving to the commit phase.

**Question 5:** Optimal Bidding Strategy in Vickrey Auctions  

**Explanation**: Truthful bidding (bidding exactly your true valuation) is the dominant strategy in Vickrey auctions. Since you pay the second-highest bid when you win, not your own bid, there's no advantage to bidding higher or lower than your true value. Bidding higher doesn't change what you pay but increases the risk of winning when it's unprofitable. Bidding lower might cause you to lose profitable opportunities without any benefit.

**Question 6:** Core Allocation Characterization  

**Explanation**: The core of a cooperative game consists of all allocations where no coalition can improve their total payoff by leaving the grand coalition and forming their own group. An allocation is in the core if, for every possible subset of players, the sum of their allocations is at least as large as the value they could generate independently. This stability concept ensures that all players prefer to stay in the grand coalition rather than break away.

**Question 7:** View Change Mechanism Importance  

**Explanation**: The view change mechanism is critical for maintaining liveness in Byzantine consensus when the primary node fails or behaves maliciously. If the current primary stops responding or sends inconsistent messages, backup nodes can initiate a view change to elect a new primary. This prevents the system from becoming stuck and ensures progress can continue despite primary failures. The mechanism requires 2f+1 nodes to agree on the view change, maintaining Byzantine fault tolerance during leadership transitions.

---

## 🧭 Navigation

**Back to Test:** [Session 9 Test Questions →](Session9_*.md#multiple-choice-test)

---
