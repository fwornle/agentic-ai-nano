# Session 2 - Module B: Test Solutions

---

**Question 1:** What components are included in the complete Kubernetes manifest package?  

### Answer: B) Deployment, service, configmap, ingress, HPA, and PDB

**Explanation:** The complete Kubernetes manifest package includes six essential components: deployment (for pod management), service (for network exposure), configmap (for configuration), ingress (for external routing), HPA (Horizontal Pod Autoscaler for scaling), and PDB (Pod Disruption Budget for resilience during maintenance).

---

**Question 2:** What is the systematic approach followed in the deployment process?  

### Answer: B) Manifest generation, cloud provisioning, Kubernetes deployment, monitoring, auto-scaling

**Explanation:** The deployment follows a systematic five-step approach: first generating Kubernetes manifests, then provisioning cloud resources, deploying to Kubernetes, setting up monitoring and alerting, and finally configuring auto-scaling. This ensures comprehensive production readiness.

---

**Question 3:** What happens when a deployment fails according to the error handling strategy?  

### Answer: B) Automatic rollback is initiated to maintain system stability

**Explanation:** The deployment system includes robust error handling that automatically initiates rollback procedures when failures occur. This prevents partial deployments from affecting production services and maintains system stability by reverting to the previous known-good state.

---

**Question 4:** What information is returned upon successful deployment?  

### Answer: B) Deployment ID, status, cloud resources, endpoints, and health check URLs

**Explanation:** Successful deployments return comprehensive information including deployment_id (for tracking), status, cloud_resources (infrastructure details), kubernetes_deployment (cluster info), monitoring and scaling configurations, service endpoints, and health check URLs for operational management.

---

**Question 5:** What is the purpose of Pod Disruption Budgets (PDB) in the deployment architecture?  

### Answer: B) Ensure production resilience during maintenance operations

**Explanation:** Pod Disruption Budgets (PDB) are a Kubernetes feature that ensures a minimum number of pods remain available during voluntary disruptions like cluster maintenance, node upgrades, or scaling operations. This maintains service availability and production resilience.

---

### Return to Module

---

**Next:** [Session 3 - LangGraph Multi-Agent Workflows →](Session3_LangGraph_Multi_Agent_Workflows.md)

---
