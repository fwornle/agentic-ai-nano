# Session 4 Module B - Test Solutions

## Enterprise Team Patterns - Answer Key

**Question 1:** Correct Answer: b) Knowledge base (1.2 weight) and databases (1.3 weight)  

**Explanation**: The source weighting system prioritizes trusted enterprise data sources:
```python
source_weights = {
    "knowledge_base": 1.2,  # Higher weight for internal sources
    "web": 1.0,
    "documents": 1.1,
    "databases": 1.3
}
```

This weighting ensures that internal documentation and database content receive priority over external web sources, maintaining enterprise data quality standards.

**Question 2:** Correct Answer: d) ENTERPRISE_LEAD  

**Explanation**: The delegation rules define strategic planning as an enterprise-level responsibility:
```python
DelegationRule(
    from_authority=DelegationAuthority.ENTERPRISE_LEAD,
    to_authority=DelegationAuthority.DEPARTMENT_MANAGE,
    task_types=

---

## 🧭 Navigation

**Back to Test:** [Session 4 Test Questions →](Session4_CrewAI_Team_Orchestration.md#multiple-choice-test-session-4)

---
