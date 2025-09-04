# Session 8 - Module B: Test Solutions

## Enterprise Scaling & Architecture - Answer Key

**Question 1:** Custom Resource Definitions (CRDs)  

**Explanation**: Custom Resource Definitions (CRDs) allow you to create new resource types in Kubernetes beyond the built-in ones like Pods and Services. In our agent platform, CRDs enable us to define AgnoAgent resources with specific fields for agent configuration, scaling policies, and business logic that Kubernetes operators can then manage automatically.

**Question 2:** ResourceQuota Purpose  

**Explanation**: ResourceQuota objects are Kubernetes' way of implementing resource governance in multi-tenant environments. They set hard limits on CPU, memory, storage, and object counts per namespace, ensuring fair resource distribution and preventing any tenant from monopolizing cluster resources or causing denial-of-service to other tenants.

```yaml
"hard": {
    "requests.cpu": "10",
    "requests.memory": "20Gi",
    "limits.cpu": "20",
    "limits.memory": "40Gi"
}
```

**Question 3:** Canary Traffic Distribution  

**Explanation**: The canary deployment configuration implements a conservative 90/10 traffic split by default. This allows gradual rollout of new agent versions while minimizing risk. The small 10% canary traffic provides real user feedback while maintaining service stability for the majority of requests through the proven stable version.

```yaml
"route":

---

## 🧭 Navigation

**Back to Test:** [Session 8 Test Questions →](Session8_Agno_Production_Ready_Agents.md#multiple-choice-test-session-8)

---
