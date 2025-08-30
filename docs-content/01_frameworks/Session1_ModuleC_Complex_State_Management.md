# Session 1 - Module C: Complex State Management

> **⚠️ ADVANCED OPTIONAL MODULE**  
> Prerequisites: Complete Session 1 core content first.

In distributed data processing systems, an agent must simultaneously track the state of thousands of concurrent ETL jobs, maintain consistency across multiple data centers, and preserve critical pipeline metadata through system restarts and rolling updates. When a data quality agent identifies anomalous patterns in streaming data, it needs to correlate this with pipeline state from the past 48 hours, current batch processing status, and ongoing ML training workflows - all while managing state within pod memory limits and ensuring GDPR compliance for data retention.

This module explores sophisticated state management patterns essential for production data processing systems. Whether you're building pipeline orchestrators that need to track job dependencies across multiple clusters, ML agents that maintain training state through infrastructure changes, or quality monitors that preserve anomaly detection patterns across system upgrades, these patterns form the foundation of robust cloud-native data systems.

The distinction between a prototype data pipeline and a production-ready data processing system lies in sophisticated state management. We'll examine patterns that enable agents to maintain consistency across distributed processing, handle graceful degradation under resource pressure, and preserve critical operational state - essential capabilities for systems that must operate reliably in high-throughput cloud environments processing petabyte-scale data.

---

## Part 1: Data Processing Memory Systems

### Advanced Memory Architecture

🗂️ **File**: `src/session1/conversation_memory.py` - Advanced memory management systems

In data processing contexts, memory management extends beyond simple conversation tracking. Consider a pipeline orchestration agent that must correlate current batch status with historical processing patterns, or a cost optimization system that needs to maintain resource utilization trends through cluster scaling events. The foundation is a structured memory system with priority levels aligned to data engineering criticality:

```python
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import sqlite3
from enum import Enum
import numpy as np
from sentence_transformers import SentenceTransformer

class DataProcessingMemoryPriority(Enum):
    LOW = 1        # Debug logs, temporary metrics, development queries
    MEDIUM = 2     # Processing history, performance trends, batch summaries
    HIGH = 3       # Pipeline state, resource allocations, data quality metrics
    CRITICAL = 4   # SLA commitments, compliance records, data lineage
```

The priority system aligns with data engineering operational impact levels, ensuring compliance and data lineage information is never discarded due to memory pressure.

```python
@dataclass
class DataProcessingMemory:
    id: str
    content: str
    timestamp: datetime
```

The `DataProcessingMemory` structure forms the core unit of the memory system, designed to handle cloud-native data processing requirements:

```python
    priority: DataProcessingMemoryPriority
    context_tags: List[str] = field(default_factory=list)  # ["kafka_topic", "airflow_dag", "s3_partition"]
    embedding: Optional[np.ndarray] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    related_memories: List[str] = field(default_factory=list)
    ttl_seconds: Optional[int] = None  # GDPR compliance for data retention
    cost_attribution: Optional[str] = None  # Track memory costs per data project
    data_lineage_refs: List[str] = field(default_factory=list)  # Data lineage tracking
    processing_stage: Optional[str] = None  # ingestion, transformation, validation, storage
```

Extended fields support data processing use cases: context_tags identify processing contexts (topics, DAGs, partitions), data_lineage_refs maintain data governance, processing_stage tracks pipeline position, and ttl_seconds handles regulatory data retention requirements.

```python
class HierarchicalDataProcessingMemoryAgent(BaseAgent):
    """Agent with hierarchical memory management for data processing systems"""
    
    def __init__(self, name: str, llm_client, memory_db_path: str = "data_agent_memory.db"):
        super().__init__(name, "Hierarchical data processing memory agent", llm_client)
        self.memory_db_path = memory_db_path
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.working_memory: List[DataProcessingMemory] = []
        self.working_memory_limit = 200  # Higher limit for data processing contexts
        self.data_lineage_graph = {}  # Track data relationships
        self._init_data_memory_database()
```

The agent initialization balances semantic search capabilities with Kubernetes resource constraints typical in cloud deployments, with higher limits to accommodate data processing context complexity.

### Semantic Memory Retrieval

The memory storage system combines semantic embeddings with operational metadata optimized for data processing contexts:

```python
    def _init_data_memory_database(self):
        """Initialize SQLite database with data processing schema"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
```

The initialization method establishes a database connection using SQLite, which provides ACID transactions and efficient querying for memory management without requiring external dependencies.

```python
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_processing_memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                priority INTEGER NOT NULL,
                context_tags TEXT,
                embedding BLOB,
                access_count INTEGER DEFAULT 0,
                last_accessed REAL,
                related_memories TEXT,
```

The core schema establishes essential fields for memory management: unique identifiers, content storage, temporal tracking, and priority systems. The embedding field stores vector representations for semantic search capabilities.

```python
                cluster_state TEXT,  -- K8s cluster at time of memory
                pipeline_context TEXT,  -- Active pipelines when memory was created
                cost_attribution TEXT,  -- Project/team for cost tracking
                gdpr_deletion_date REAL,  -- Automatic deletion for compliance
                data_lineage_refs TEXT,  -- Data lineage tracking
                processing_stage TEXT,  -- Pipeline stage context
                data_volume_gb REAL,  -- Volume of data processed
                schema_version TEXT,  -- Data schema version
                partition_info TEXT  -- Data partitioning information
            )
        ''')
        
        conn.commit()
        conn.close()
```

The schema includes data-specific fields for correlating memories with data lineage, processing stages, and schema evolution, essential for data governance and pipeline optimization.

### Memory Consolidation

For long-running data processing systems, memory consolidation prevents unbounded growth while preserving operational continuity:

```python
    def consolidate_data_processing_memories(self, time_window: timedelta = timedelta(hours=6)):
        """Consolidate similar data processing memories within processing time window"""
        cutoff_time = datetime.now() - time_window
        
        # Group memories by semantic similarity and data processing context
        memory_clusters = self._cluster_by_data_context(cutoff_time)
        
        for cluster in memory_clusters:
            if len(cluster) > 1:
                # Preserve compliance-critical and data lineage memories individually
                critical_memories = [m for m in cluster 
                                   if m.priority == DataProcessingMemoryPriority.CRITICAL]
                
                lineage_memories = [m for m in cluster 
                                  if m.data_lineage_refs]
                
                if critical_memories or lineage_memories:
                    continue  # Never consolidate compliance or lineage data
                
                # Consolidate operational data processing memories for efficiency
                consolidated = self._create_consolidated_data_memory(cluster)
                self._replace_memories(cluster, consolidated)
```

The consolidation process respects data governance requirements by never consolidating compliance-critical data or data lineage information, maintaining full audit trails for regulatory reporting and data governance.

### Data Lineage Integration

Advanced memory systems track data lineage to support governance and debugging:

```python
    def store_data_processing_memory_with_lineage(self, content: str, 
                                                 priority: DataProcessingMemoryPriority,
                                                 upstream_data: List[str] = None,
                                                 downstream_processes: List[str] = None,
                                                 schema_refs: List[str] = None):
        """Store memory with data lineage tracking"""
        memory_id = f"data_mem_{datetime.now().timestamp()}"
        
        # Generate semantic embedding for data processing context
        embedding = self.embedder.encode(content)
```

The memory storage process begins by generating a unique identifier using timestamp-based naming and creating a semantic embedding. This embedding enables similarity search and context-aware memory retrieval for data processing operations.

```python
        # Create memory with data lineage
        memory = DataProcessingMemory(
            id=memory_id,
            content=content,
            timestamp=datetime.now(),
            priority=priority,
            embedding=embedding,
            data_lineage_refs=upstream_data or [],
            context_tags=self._extract_data_context_tags(content)
        )
```

The DataProcessingMemory object encapsulates all memory attributes including lineage references that track data flow relationships. Context tags are automatically extracted to enable efficient filtering and categorization of data processing memories.

```python
        # Update data lineage graph
        if upstream_data:
            for upstream in upstream_data:
                if upstream not in self.data_lineage_graph:
                    self.data_lineage_graph[upstream] = {"downstream": []}
                self.data_lineage_graph[upstream]["downstream"].append(memory_id)
        
        self.working_memory.append(memory)
        
        # Persist to database with lineage
        self._persist_memory_with_lineage(memory, upstream_data, downstream_processes)
```

---

## Part 2: Persistent State Between Sessions

### Database-Backed State Management

🗂️ **File**: `src/session1/persistent_state.py` - Cross-session state persistence

Cloud-native data processing systems require state persistence across pod restarts, cluster maintenance, and infrastructure changes. This demands robust state management that can handle various failure scenarios:

```python
class DataProcessingPersistentStateManager:
    """Manages data processing agent state across cloud infrastructure changes"""
    
    def __init__(self, state_file: str = "data_agent_state.json", 
                 backup_to_s3: bool = True,
                 backup_interval: int = 180,  # 3-minute backup interval for data processing
                 state_partitioning: bool = True):
        self.state_file = state_file
        self.backup_to_s3 = backup_to_s3
        self.backup_interval = backup_interval
        self.state_partitioning = state_partitioning
        self.state: Dict[str, Any] = {}
        self.dirty = False
        self.s3_client = self._init_s3_client() if backup_to_s3 else None
        self.state_checksum = None  # Data integrity validation
        self._load_data_processing_state()
        self._start_backup_thread()
```

The state manager implements cloud-native persistence patterns essential for distributed data processing reliability:

```python
    def _load_data_processing_state(self):
        """Load data processing state with S3 fallback and integrity validation"""
        try:
            # Try local state file first (fastest)
            with open(self.state_file, 'r') as f:
                loaded_state = json.load(f)
                
            # Validate data integrity for data processing
            if self._validate_state_integrity(loaded_state):
                self.state = loaded_state
                self.state_checksum = self._calculate_checksum(loaded_state)
            else:
                raise ValueError("State integrity validation failed")
                
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            # Fallback to S3 backup
            if self.s3_client:
                try:
                    self.state = self._load_from_s3_with_validation()
                    print(f"Recovered data processing state from S3 backup")
                except:
                    # Initialize with safe data processing defaults
                    self.state = self._get_safe_data_processing_defaults()
            else:
                self.state = self._get_safe_data_processing_defaults()
```

### Data Processing State Migration

Cloud data systems must handle state migration across software updates and schema changes:

```python
    def migrate_data_processing_state(self, old_version: str, new_version: str):
        """Migrate data processing state between deployment versions"""
        migration_map = {
            ("1.0.0", "1.1.0"): self._migrate_add_data_lineage_tracking,
            ("1.1.0", "2.0.0"): self._migrate_add_schema_evolution_support,
            ("2.0.0", "2.1.0"): self._migrate_add_multi_region_data_processing,
            ("2.1.0", "2.2.0"): self._migrate_add_streaming_state_management
        }
```

The migration system uses a lookup table to map version pairs to specific migration functions. This pattern enables systematic state upgrades across deployment cycles, ensuring data processing agents can handle schema evolution gracefully without losing historical context.

```python
        migration_func = migration_map.get((old_version, new_version))
        if migration_func:
            self.state = migration_func(self.state)
            self.state["schema_version"] = new_version
            self.state["migration_timestamp"] = datetime.now().isoformat()
            self.dirty = True
```

When a migration path exists, the system applies the transformation function and updates metadata to track the migration event. The `dirty` flag ensures the migrated state will be persisted during the next save cycle.

```python
    def _migrate_add_data_lineage_tracking(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Add data lineage tracking to existing state"""
        state["data_lineage"] = {
            "upstream_dependencies": {},
            "downstream_consumers": {},
            "schema_evolution": {},
            "data_quality_metrics": {}
        }
        return state
```

The lineage tracking migration adds comprehensive data flow structures to the state. This enables data processing agents to understand how data moves through pipeline stages and track quality metrics across transformations.

```python
    def _backup_data_processing_state_to_s3(self):
        """Backup data processing state to S3 for disaster recovery"""
        if self.s3_client and self.dirty:
            # Create partitioned backup for large data processing states
            if self.state_partitioning:
                self._backup_partitioned_state()
```

The backup system checks for available S3 connectivity and dirty state flags before initiating backup operations. For large data processing states, partitioning strategies distribute the backup across multiple S3 objects to optimize storage and retrieval performance.

```python
            else:
                backup_key = f"data-agent-state/{datetime.utcnow().isoformat()}.json"
                self.s3_client.put_object(
                    Bucket=os.environ['DATA_PROCESSING_BACKUP_BUCKET'],
                    Key=backup_key,
                    Body=json.dumps(self.state, indent=2),
                    Metadata={
                        'data_processing_version': self.state.get('schema_version', '1.0.0'),
                        'checksum': self._calculate_checksum(self.state)
                    }
                )
```

### Data Processing State Validation

Comprehensive validation ensures data processing state integrity:

```python
    def _validate_state_integrity(self, state: Dict[str, Any]) -> bool:
        """Validate data processing state integrity"""
        required_fields = [
            'schema_version', 'pipeline_states', 'data_quality_metrics',
            'resource_allocations', 'processing_history'
        ]
        
        # Check required fields
        if not all(field in state for field in required_fields):
            return False
            
        # Validate pipeline states
        if 'pipeline_states' in state:
            for pipeline_id, pipeline_state in state['pipeline_states'].items():
                if not self._validate_pipeline_state(pipeline_state):
                    return False
        
        # Validate data quality metrics
        if 'data_quality_metrics' in state:
            if not self._validate_quality_metrics(state['data_quality_metrics']):
                return False
                
        return True
```

---

## Part 3: Context Window Management

### Sliding Window with Priority Retention

🗂️ **File**: `src/session1/context_management.py` - Optimized context window handling

In data processing systems handling high-volume data streams, intelligent context management directly impacts API costs and processing latency:

```python
class DataProcessingContextManager:
    """Manages context window for cost-optimized data processing operations"""
    
    def __init__(self, max_tokens: int = 12288, cost_budget: float = 200.0):  # Higher limits for data processing
        self.max_tokens = max_tokens
        self.cost_budget = cost_budget  # Daily budget in USD
        self.current_cost = 0.0
        self.context_window = []
        self.token_count = 0
        self.cost_per_token = 0.00002  # GPT-4 pricing
        self.data_context_priority_weights = {
            "data_quality_alert": 1.0,
            "pipeline_failure": 0.95,
            "schema_change": 0.9,
            "performance_degradation": 0.85,
            "batch_completion": 0.7,
            "routine_processing": 0.3
        }
```

The cost awareness ensures data processing operations stay within budget constraints while prioritizing critical data engineering events:

```python
    def add_data_processing_context(self, content: str, 
                                  priority: DataProcessingMemoryPriority, 
                                  source: str = "unknown", 
                                  data_context_type: str = "routine_processing",
                                  estimated_cost: float = 0.0):
        """Add data processing content with cost and priority tracking"""
        tokens = self._estimate_tokens(content)
        
        # Check cost constraints
        if self.current_cost + estimated_cost > self.cost_budget:
            self._apply_data_processing_cost_optimization()
        
        context_entry = {
            "content": content,
            "priority": priority,
            "source": source,  # "airflow_dag", "kafka_stream", "spark_job"
            "data_context_type": data_context_type,
            "timestamp": datetime.now(),
            "tokens": tokens,
            "estimated_cost": estimated_cost,
            "processing_metadata": self._extract_data_processing_metadata(source),
            "priority_weight": self.data_context_priority_weights.get(data_context_type, 0.5)
        }
        
        self.context_window.append(context_entry)
        self.token_count += tokens
        self.current_cost += estimated_cost
```

### Dynamic Context Pruning

The pruning strategy optimizes for both data processing priority and cost efficiency:

```python
    def prune_data_processing_context(self):
        """Prune context with data processing priority and cost optimization"""
        # Sort by data context priority, then operational priority, then cost-efficiency
        sorted_context = sorted(
            self.context_window,
            key=lambda x: (
                x["priority_weight"],  # Data context importance
                x["priority"].value,   # Operational priority
                -x["estimated_cost"]   # Cost efficiency (negative for ascending cost)
            ),
            reverse=True
        )
        
        # Rebuild context keeping high-value, cost-effective items
        new_context = []
        new_token_count = 0
        new_cost = 0.0
        
        for entry in sorted_context:
            token_cost = new_token_count + entry["tokens"]
            budget_cost = new_cost + entry["estimated_cost"]
            
            if (token_cost <= self.max_tokens and 
                budget_cost <= self.cost_budget):
                new_context.append(entry)
                new_token_count += entry["tokens"]
                new_cost += entry["estimated_cost"]
            elif entry["priority"] == DataProcessingMemoryPriority.CRITICAL:
                # Force include critical data processing events
                self._make_room_for_critical_data_processing(new_context, entry)
            elif entry["data_context_type"] == "data_quality_alert":
                # Always preserve data quality alerts
                self._make_room_for_data_quality_alert(new_context, entry)
        
        self.context_window = new_context
        self.token_count = new_token_count
        self.current_cost = new_cost
```

### Cost-Aware Context Strategies

Advanced cost optimization for high-throughput data processing:

```python
    def _apply_data_processing_cost_optimization(self):
        """Apply data processing specific cost optimization strategies"""
        strategies = [
            self._use_efficient_model_for_routine_data_processing,
            self._batch_similar_data_processing_requests,
            self._cache_frequent_data_processing_patterns,
            self._compress_repetitive_data_processing_context,
            self._aggregate_similar_data_quality_events,
            self._summarize_batch_processing_logs
        ]
        
        for strategy in strategies:
            if strategy():
                break  # Applied successfully
                
    def _extract_data_processing_metadata(self, source: str) -> Dict[str, Any]:
        """Extract relevant metadata for data processing context"""
        metadata = {
            "source_type": self._classify_data_source(source),
            "processing_stage": self._infer_processing_stage(source),
            "data_volume_indicator": self._estimate_data_volume_from_source(source),
            "criticality_level": self._assess_source_criticality(source)
        }
        
        return metadata
```

---

## Part 4: Multi-Tenant Memory Management

### Tenant Isolation and Resource Allocation

For multi-tenant data processing systems, memory management must respect isolation boundaries and data governance:

```python
class MultiTenantDataProcessingMemoryManager:
    """Memory management with tenant isolation for SaaS data processing platforms"""
    
    def __init__(self, total_memory_mb: int = 4096):  # Higher limit for data processing
        self.total_memory_mb = total_memory_mb
        self.tenant_quotas = {}  # tenant_id -> allocated memory
        self.tenant_usage = {}   # tenant_id -> current usage
        self.tenant_data_contexts = {}  # tenant_id -> data processing contexts
        self.global_priority_reserve = total_memory_mb * 0.15  # 15% reserve for critical data processing
        self.compliance_reserve = total_memory_mb * 0.05  # 5% for compliance and audit
```

The tenant system ensures fair resource allocation while maintaining system stability and data governance:

```python
    def allocate_tenant_data_processing_memory(self, tenant_id: str, quota_mb: int, 
                                             data_retention_days: int = 90,
                                             compliance_tier: str = "standard"):
        """Allocate memory quota for data processing tenant"""
        available = self.total_memory_mb - self.global_priority_reserve - self.compliance_reserve
        allocated = sum(self.tenant_quotas.values())
        
        if allocated + quota_mb > available:
            raise ResourceError(f"Cannot allocate {quota_mb}MB for data processing tenant {tenant_id}")
```

Tenant allocation begins by calculating available memory after reserving space for global priorities and compliance requirements. This ensures that high-priority data processing operations and regulatory compliance data retention always have guaranteed resources.

```python
        self.tenant_quotas[tenant_id] = quota_mb
        self.tenant_usage[tenant_id] = 0
        self.tenant_data_contexts[tenant_id] = {
            "data_retention_days": data_retention_days,
            "compliance_tier": compliance_tier,
            "processing_contexts": [],
            "data_lineage_entries": [],
            "quality_metrics": {}
        }
```

Once allocation succeeds, the system initializes tenant-specific tracking structures. The data context includes retention policies, compliance classifications, and containers for processing history and quality metrics - essential for data governance in multi-tenant data processing environments.

```python
    def store_tenant_data_processing_memory(self, tenant_id: str, 
                                          memory: DataProcessingMemory,
                                          data_classification: str = "internal"):
        """Store data processing memory with tenant quota enforcement and data governance"""
        estimated_size = self._estimate_data_processing_memory_size(memory)
        current_usage = self.tenant_usage.get(tenant_id, 0)
        quota = self.tenant_quotas.get(tenant_id, 0)
```

Memory storage starts with size estimation and quota validation. This upfront check prevents memory allocation failures that could disrupt data processing pipelines, while providing predictable resource management for multi-tenant data environments.

```python
        # Apply data classification policies
        if data_classification == "sensitive":
            memory.ttl_seconds = min(memory.ttl_seconds or 7776000, 7776000)  # Max 90 days for sensitive data
        elif data_classification == "public":
            memory.ttl_seconds = memory.ttl_seconds or 31536000  # 1 year default for public data
```

Data classification policies automatically enforce retention limits based on sensitivity levels. Sensitive data is capped at 90 days to meet compliance requirements, while public data defaults to longer retention for analytics purposes.

```python
        if current_usage + estimated_size > quota:
            # Apply tenant-specific data processing memory pruning
            self._prune_tenant_data_processing_memory(tenant_id, estimated_size)
        
        # Store with data governance metadata
        self._store_data_processing_memory_with_governance(tenant_id, memory, data_classification)
        self.tenant_usage[tenant_id] += estimated_size
```

When quota limits are exceeded, tenant-specific pruning removes lower-priority memories to make space. The governance-aware storage process includes metadata tracking for audit trails and compliance reporting.

```python
        # Update tenant data context
        self.tenant_data_contexts[tenant_id]["processing_contexts"].append({
            "memory_id": memory.id,
            "timestamp": memory.timestamp,
            "processing_stage": memory.processing_stage,
            "data_classification": data_classification
        })
```

### Data Processing Memory Analytics

Advanced analytics for multi-tenant data processing memory usage:

```python
    def get_tenant_data_processing_analytics(self, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for tenant data processing memory usage"""
        if tenant_id not in self.tenant_quotas:
            return {"error": "Tenant not found"}
        
        tenant_context = self.tenant_data_contexts[tenant_id]
        usage = self.tenant_usage[tenant_id]
        quota = self.tenant_quotas[tenant_id]
        
        # Calculate processing stage distribution
        stage_distribution = {}
        for context in tenant_context["processing_contexts"]:
            stage = context.get("processing_stage", "unknown")
            stage_distribution[stage] = stage_distribution.get(stage, 0) + 1
        
        # Calculate data classification distribution
        classification_distribution = {}
        for context in tenant_context["processing_contexts"]:
            classification = context.get("data_classification", "internal")
            classification_distribution[classification] = classification_distribution.get(classification, 0) + 1
        
        return {
            "tenant_id": tenant_id,
            "memory_usage_mb": usage,
            "memory_quota_mb": quota,
            "utilization_percentage": (usage / quota * 100) if quota > 0 else 0,
            "processing_stage_distribution": stage_distribution,
            "data_classification_distribution": classification_distribution,
            "total_processing_contexts": len(tenant_context["processing_contexts"]),
            "data_lineage_entries": len(tenant_context["data_lineage_entries"]),
            "compliance_tier": tenant_context["compliance_tier"],
            "data_retention_days": tenant_context["data_retention_days"]
        }
```

---

## Multiple Choice Test - Session 1 Module C

Test your understanding of data processing state management:

**Question 1:** In data processing systems, why are compliance and data lineage memories never consolidated?  
A) To reduce API costs  
B) To maintain full audit trails for regulatory reporting and data governance  
C) To improve query speed  
D) To simplify the codebase  

**Question 2:** What is the purpose of cost tracking in data processing context window management?  
A) To impress stakeholders  
B) To ensure data processing operations stay within API budget constraints  
C) To improve processing speed  
D) To reduce token count  

**Question 3:** How does the data processing state manager handle pod restart scenarios?  
A) Loses all data processing state  
B) Only keeps local files  
C) Falls back to S3 backup with integrity validation and safe defaults  
D) Crashes the data processing system  

**Question 4:** Why is semantic embedding useful in data processing memory systems?  
A) To compress data  
B) To correlate related processing jobs, pipeline states, and operational patterns  
C) To reduce latency  
D) To encrypt data  

**Question 5:** What determines memory priority in multi-tenant data processing systems?  
A) Data size  
B) Processing time  
C) Data processing criticality, compliance requirements, and data governance policies  
D) User preference  

## Solutions

[Click here for solutions](Session1_ModuleC_Test_Solutions.md)

---

## Navigation

- [← Previous: Session 1 Module B - Performance Optimization](Session1_ModuleB_Performance_Optimization.md)
- [↑ Return to Session 1: Bare Metal Agents](Session1_Bare_Metal_Agents.md)
- [→ Next: Session 1 Module D - Coding Assistant Case Study](Session1_ModuleD_Coding_Assistant_Case_Study.md)