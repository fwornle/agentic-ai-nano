# Session 3 Module B - Test Solutions

## Enterprise State Management - Answer Key

**Question 1:** Correct Answer: c) PostgresSaver with primary and backup clusters

**Explanation**: The production environment configuration uses PostgreSQL with cluster redundancy:
```python
if self.environment == "production":
    return {
        "primary": PostgresSaver.from_conn_string(
            "postgresql://user:pass@prod-cluster:5432/langgraph_state"
        ),
        "backup": PostgresSaver.from_conn_string(
            "postgresql://user:pass@backup-cluster:5432/langgraph_state"
        ),
        "type": "postgres_cluster"
    }
```

PostgreSQL provides ACID compliance, enterprise-grade reliability, and backup cluster support for high availability production deployments.

**Question 2:** Correct Answer: b) Error rate > 30%, integrity issues, or execution > 30 minutes

**Explanation**: The automatic recovery system triggers on multiple conditions:
```python
recovery_actions =
---

## 🧭 Navigation

**Previous:** [Session 2 - LangChain Foundations ←](Session2_LangChain_Foundations.md)
**Next:** [Session 4 - CrewAI Team Orchestration →](Session4_CrewAI_Team_Orchestration.md)
---
