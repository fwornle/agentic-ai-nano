"""
State Management System - Session 8
Advanced state management for workflow persistence and recovery.
"""

import asyncio
import json
import pickle
import sqlite3
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StateType(Enum):
    """Types of state storage."""
    MEMORY = "memory"           # In-memory storage (fast, non-persistent)
    SQLITE = "sqlite"           # SQLite database (persistent, good for single instance)
    REDIS = "redis"             # Redis (distributed, cache-like)
    FILE = "file"               # File-based (simple persistence)


class StateStatus(Enum):
    """Status of state entries."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"
    EXPIRED = "expired"


@dataclass
class StateEntry:
    """Individual state entry with metadata."""
    id: str
    workflow_id: str
    execution_id: str
    step_id: Optional[str] = None
    
    # State data
    state_data: Dict[str, Any] = field(default_factory=dict)
    checkpoint_data: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    status: StateStatus = StateStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Versioning
    version: int = 1
    parent_version: Optional[str] = None
    
    # Tags and labels
    tags: Set[str] = field(default_factory=set)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class StateSnapshot:
    """Complete state snapshot for backup/restore."""
    snapshot_id: str
    workflow_id: str
    execution_id: str
    timestamp: datetime
    
    # Complete state
    workflow_state: Dict[str, Any]
    step_states: Dict[str, Dict[str, Any]]
    variables: Dict[str, Any]
    metadata: Dict[str, Any]
    
    # Snapshot metadata
    description: str = ""
    automatic: bool = True  # True if auto-generated, False if manual


class InMemoryStateStore:
    """High-performance in-memory state store."""
    
    def __init__(self):
        self.states: Dict[str, StateEntry] = {}
        self.indices: Dict[str, Set[str]] = {
            'workflow_id': {},
            'execution_id': {},
            'status': {}
        }
        self.lock = threading.RLock()
    
    async def store_state(self, entry: StateEntry) -> bool:
        """Store state entry."""
        with self.lock:
            entry.updated_at = datetime.now()
            self.states[entry.id] = entry
            
            # Update indices
            self._update_indices(entry)
            
            return True
    
    async def get_state(self, state_id: str) -> Optional[StateEntry]:
        """Get state entry by ID."""
        with self.lock:
            entry = self.states.get(state_id)
            if entry and entry.expires_at and datetime.now() > entry.expires_at:
                # Entry expired
                await self.delete_state(state_id)
                return None
            return entry
    
    async def get_states_by_workflow(self, workflow_id: str) -> List[StateEntry]:
        """Get all states for a workflow."""
        with self.lock:
            workflow_states = []
            for entry in self.states.values():
                if entry.workflow_id == workflow_id:
                    if not entry.expires_at or datetime.now() <= entry.expires_at:
                        workflow_states.append(entry)
            return workflow_states
    
    async def get_states_by_execution(self, execution_id: str) -> List[StateEntry]:
        """Get all states for an execution."""
        with self.lock:
            execution_states = []
            for entry in self.states.values():
                if entry.execution_id == execution_id:
                    if not entry.expires_at or datetime.now() <= entry.expires_at:
                        execution_states.append(entry)
            return execution_states
    
    async def update_state(self, state_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing state entry."""
        with self.lock:
            if state_id not in self.states:
                return False
            
            entry = self.states[state_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(entry, key):
                    setattr(entry, key, value)
                elif key == 'state_data':
                    entry.state_data.update(value)
                elif key == 'checkpoint_data':
                    entry.checkpoint_data.update(value)
            
            entry.updated_at = datetime.now()
            entry.version += 1
            
            self._update_indices(entry)
            return True
    
    async def delete_state(self, state_id: str) -> bool:
        """Delete state entry."""
        with self.lock:
            if state_id in self.states:
                entry = self.states[state_id]
                self._remove_from_indices(entry)
                del self.states[state_id]
                return True
            return False
    
    async def cleanup_expired_states(self) -> int:
        """Clean up expired state entries."""
        with self.lock:
            expired_ids = []
            now = datetime.now()
            
            for state_id, entry in self.states.items():
                if entry.expires_at and now > entry.expires_at:
                    expired_ids.append(state_id)
            
            for state_id in expired_ids:
                await self.delete_state(state_id)
            
            return len(expired_ids)
    
    def _update_indices(self, entry: StateEntry):
        """Update search indices."""
        # Workflow ID index
        if entry.workflow_id not in self.indices['workflow_id']:
            self.indices['workflow_id'][entry.workflow_id] = set()
        self.indices['workflow_id'][entry.workflow_id].add(entry.id)
        
        # Execution ID index
        if entry.execution_id not in self.indices['execution_id']:
            self.indices['execution_id'][entry.execution_id] = set()
        self.indices['execution_id'][entry.execution_id].add(entry.id)
        
        # Status index
        status_key = entry.status.value
        if status_key not in self.indices['status']:
            self.indices['status'][status_key] = set()
        self.indices['status'][status_key].add(entry.id)
    
    def _remove_from_indices(self, entry: StateEntry):
        """Remove entry from indices."""
        for index_type, indices in self.indices.items():
            for key, id_set in indices.items():
                id_set.discard(entry.id)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get state store statistics."""
        with self.lock:
            status_counts = {}
            for status_key, id_set in self.indices['status'].items():
                status_counts[status_key] = len(id_set)
            
            return {
                "total_states": len(self.states),
                "status_breakdown": status_counts,
                "workflow_count": len(self.indices['workflow_id']),
                "execution_count": len(self.indices['execution_id'])
            }


class SQLiteStateStore:
    """SQLite-based persistent state store."""
    
    def __init__(self, db_path: str = "workflow_state.db"):
        self.db_path = db_path
        self.lock = threading.RLock()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS workflow_states (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    execution_id TEXT NOT NULL,
                    step_id TEXT,
                    state_data TEXT,
                    checkpoint_data TEXT,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    expires_at TEXT,
                    version INTEGER,
                    parent_version TEXT,
                    tags TEXT,
                    labels TEXT
                )
            ''')
            
            # Create indices
            conn.execute('CREATE INDEX IF NOT EXISTS idx_workflow_id ON workflow_states(workflow_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_execution_id ON workflow_states(execution_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON workflow_states(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON workflow_states(created_at)')
            
            conn.commit()
    
    async def store_state(self, entry: StateEntry) -> bool:
        """Store state entry in SQLite."""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO workflow_states 
                        (id, workflow_id, execution_id, step_id, state_data, checkpoint_data,
                         status, created_at, updated_at, expires_at, version, parent_version, tags, labels)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        entry.id,
                        entry.workflow_id,
                        entry.execution_id,
                        entry.step_id,
                        json.dumps(entry.state_data),
                        json.dumps(entry.checkpoint_data),
                        entry.status.value,
                        entry.created_at.isoformat(),
                        entry.updated_at.isoformat(),
                        entry.expires_at.isoformat() if entry.expires_at else None,
                        entry.version,
                        entry.parent_version,
                        json.dumps(list(entry.tags)),
                        json.dumps(entry.labels)
                    ))
                    conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to store state {entry.id}: {str(e)}")
                return False
    
    async def get_state(self, state_id: str) -> Optional[StateEntry]:
        """Get state entry by ID."""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.execute('SELECT * FROM workflow_states WHERE id = ?', (state_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        return self._row_to_entry(row)
                return None
            except Exception as e:
                logger.error(f"Failed to get state {state_id}: {str(e)}")
                return None
    
    async def get_states_by_workflow(self, workflow_id: str) -> List[StateEntry]:
        """Get all states for a workflow."""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.execute(
                        'SELECT * FROM workflow_states WHERE workflow_id = ? ORDER BY created_at',
                        (workflow_id,)
                    )
                    rows = cursor.fetchall()
                    
                    return [self._row_to_entry(row) for row in rows]
            except Exception as e:
                logger.error(f"Failed to get states for workflow {workflow_id}: {str(e)}")
                return []
    
    async def cleanup_expired_states(self) -> int:
        """Clean up expired state entries."""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        'DELETE FROM workflow_states WHERE expires_at < ?',
                        (datetime.now().isoformat(),)
                    )
                    deleted_count = cursor.rowcount
                    conn.commit()
                    return deleted_count
            except Exception as e:
                logger.error(f"Failed to cleanup expired states: {str(e)}")
                return 0
    
    def _row_to_entry(self, row: sqlite3.Row) -> StateEntry:
        """Convert database row to StateEntry."""
        return StateEntry(
            id=row['id'],
            workflow_id=row['workflow_id'],
            execution_id=row['execution_id'],
            step_id=row['step_id'],
            state_data=json.loads(row['state_data']) if row['state_data'] else {},
            checkpoint_data=json.loads(row['checkpoint_data']) if row['checkpoint_data'] else {},
            status=StateStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
            version=row['version'],
            parent_version=row['parent_version'],
            tags=set(json.loads(row['tags'])) if row['tags'] else set(),
            labels=json.loads(row['labels']) if row['labels'] else {}
        )


class WorkflowStateManager:
    """High-level workflow state management system."""
    
    def __init__(self, store_type: StateType = StateType.MEMORY, **kwargs):
        if store_type == StateType.MEMORY:
            self.store = InMemoryStateStore()
        elif store_type == StateType.SQLITE:
            db_path = kwargs.get('db_path', 'workflow_state.db')
            self.store = SQLiteStateStore(db_path)
        else:
            raise ValueError(f"Unsupported store type: {store_type}")
        
        self.snapshots: Dict[str, StateSnapshot] = {}
        self.auto_checkpoint_interval = kwargs.get('auto_checkpoint_interval', 300)  # 5 minutes
        self.auto_cleanup_interval = kwargs.get('auto_cleanup_interval', 3600)  # 1 hour
        self.default_ttl = kwargs.get('default_ttl', 24 * 3600)  # 24 hours
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        # Note: In a real implementation, these would be proper background tasks
        # For this demo, we'll implement them as callable methods
        pass
    
    async def create_checkpoint(self, workflow_id: str, execution_id: str, 
                               step_id: Optional[str] = None,
                               data: Dict[str, Any] = None,
                               ttl_seconds: Optional[int] = None) -> str:
        """Create a state checkpoint."""
        checkpoint_id = str(uuid.uuid4())
        
        expires_at = None
        if ttl_seconds or self.default_ttl:
            ttl = ttl_seconds or self.default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        entry = StateEntry(
            id=checkpoint_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            step_id=step_id,
            checkpoint_data=data or {},
            expires_at=expires_at,
            status=StateStatus.ACTIVE
        )
        
        success = await self.store.store_state(entry)
        if success:
            logger.info(f"Created checkpoint {checkpoint_id} for execution {execution_id}")
            return checkpoint_id
        else:
            raise RuntimeError(f"Failed to create checkpoint for execution {execution_id}")
    
    async def update_state(self, workflow_id: str, execution_id: str,
                          step_id: Optional[str] = None,
                          state_data: Dict[str, Any] = None,
                          variables: Dict[str, Any] = None) -> str:
        """Update workflow state."""
        # Try to find existing state entry
        execution_states = await self.store.get_states_by_execution(execution_id)
        
        existing_entry = None
        for state in execution_states:
            if state.step_id == step_id:
                existing_entry = state
                break
        
        if existing_entry:
            # Update existing entry
            updates = {}
            if state_data:
                updates['state_data'] = state_data
            if variables:
                if 'state_data' not in updates:
                    updates['state_data'] = existing_entry.state_data.copy()
                updates['state_data']['variables'] = variables
            
            success = await self.store.update_state(existing_entry.id, updates)
            if success:
                return existing_entry.id
        else:
            # Create new entry
            state_id = str(uuid.uuid4())
            full_state_data = state_data or {}
            if variables:
                full_state_data['variables'] = variables
            
            entry = StateEntry(
                id=state_id,
                workflow_id=workflow_id,
                execution_id=execution_id,
                step_id=step_id,
                state_data=full_state_data,
                status=StateStatus.ACTIVE,
                expires_at=datetime.now() + timedelta(seconds=self.default_ttl)
            )
            
            success = await self.store.store_state(entry)
            if success:
                return state_id
        
        raise RuntimeError("Failed to update workflow state")
    
    async def get_workflow_state(self, workflow_id: str) -> Dict[str, Any]:
        """Get complete workflow state."""
        states = await self.store.get_states_by_workflow(workflow_id)
        
        workflow_state = {
            "workflow_id": workflow_id,
            "executions": {},
            "checkpoints": [],
            "total_states": len(states)
        }
        
        for state in states:
            exec_id = state.execution_id
            
            if exec_id not in workflow_state["executions"]:
                workflow_state["executions"][exec_id] = {
                    "execution_id": exec_id,
                    "steps": {},
                    "checkpoints": [],
                    "status": state.status.value,
                    "created_at": state.created_at.isoformat(),
                    "updated_at": state.updated_at.isoformat()
                }
            
            execution_state = workflow_state["executions"][exec_id]
            
            if state.step_id:
                execution_state["steps"][state.step_id] = {
                    "state_data": state.state_data,
                    "status": state.status.value,
                    "version": state.version
                }
            
            if state.checkpoint_data:
                execution_state["checkpoints"].append({
                    "checkpoint_id": state.id,
                    "data": state.checkpoint_data,
                    "timestamp": state.created_at.isoformat()
                })
        
        return workflow_state
    
    async def restore_from_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Restore state from a checkpoint."""
        checkpoint = await self.store.get_state(checkpoint_id)
        
        if not checkpoint:
            logger.warning(f"Checkpoint {checkpoint_id} not found")
            return None
        
        if checkpoint.status != StateStatus.ACTIVE:
            logger.warning(f"Checkpoint {checkpoint_id} is not active (status: {checkpoint.status})")
            return None
        
        return {
            "checkpoint_id": checkpoint_id,
            "workflow_id": checkpoint.workflow_id,
            "execution_id": checkpoint.execution_id,
            "step_id": checkpoint.step_id,
            "restored_data": checkpoint.checkpoint_data,
            "checkpoint_timestamp": checkpoint.created_at.isoformat()
        }
    
    async def create_snapshot(self, workflow_id: str, execution_id: str, 
                             description: str = "") -> str:
        """Create a complete state snapshot."""
        snapshot_id = str(uuid.uuid4())
        
        # Get all states for the execution
        states = await self.store.get_states_by_execution(execution_id)
        
        workflow_state = {}
        step_states = {}
        variables = {}
        
        for state in states:
            if state.step_id:
                step_states[state.step_id] = state.state_data
                if 'variables' in state.state_data:
                    variables.update(state.state_data['variables'])
            else:
                workflow_state.update(state.state_data)
        
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            timestamp=datetime.now(),
            workflow_state=workflow_state,
            step_states=step_states,
            variables=variables,
            metadata={"total_states": len(states)},
            description=description,
            automatic=not description  # Manual if description provided
        )
        
        self.snapshots[snapshot_id] = snapshot
        logger.info(f"Created snapshot {snapshot_id} for execution {execution_id}")
        
        return snapshot_id
    
    async def restore_from_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Restore complete state from snapshot."""
        if snapshot_id not in self.snapshots:
            logger.warning(f"Snapshot {snapshot_id} not found")
            return None
        
        snapshot = self.snapshots[snapshot_id]
        
        return {
            "snapshot_id": snapshot_id,
            "workflow_id": snapshot.workflow_id,
            "execution_id": snapshot.execution_id,
            "workflow_state": snapshot.workflow_state,
            "step_states": snapshot.step_states,
            "variables": snapshot.variables,
            "snapshot_timestamp": snapshot.timestamp.isoformat(),
            "metadata": snapshot.metadata
        }
    
    async def cleanup_workflow_states(self, workflow_id: str, 
                                     keep_latest: int = 5) -> Dict[str, int]:
        """Clean up old states for a workflow, keeping the latest N."""
        states = await self.store.get_states_by_workflow(workflow_id)
        
        # Group by execution
        execution_groups = {}
        for state in states:
            exec_id = state.execution_id
            if exec_id not in execution_groups:
                execution_groups[exec_id] = []
            execution_groups[exec_id].append(state)
        
        deleted_count = 0
        archived_count = 0
        
        for exec_id, exec_states in execution_groups.items():
            # Sort by creation time (newest first)
            exec_states.sort(key=lambda s: s.created_at, reverse=True)
            
            # Keep the latest N, archive or delete the rest
            if len(exec_states) > keep_latest:
                to_cleanup = exec_states[keep_latest:]
                
                for state in to_cleanup:
                    if state.status == StateStatus.COMPLETED:
                        # Archive completed states
                        await self.store.update_state(state.id, {'status': StateStatus.ARCHIVED})
                        archived_count += 1
                    else:
                        # Delete other old states
                        await self.store.delete_state(state.id)
                        deleted_count += 1
        
        return {
            "deleted_states": deleted_count,
            "archived_states": archived_count,
            "total_cleaned": deleted_count + archived_count
        }
    
    async def get_state_statistics(self) -> Dict[str, Any]:
        """Get comprehensive state management statistics."""
        store_stats = await self.store.get_statistics()
        
        return {
            "store_statistics": store_stats,
            "snapshots": {
                "total_snapshots": len(self.snapshots),
                "automatic_snapshots": len([s for s in self.snapshots.values() if s.automatic]),
                "manual_snapshots": len([s for s in self.snapshots.values() if not s.automatic])
            },
            "configuration": {
                "auto_checkpoint_interval": self.auto_checkpoint_interval,
                "auto_cleanup_interval": self.auto_cleanup_interval,
                "default_ttl": self.default_ttl
            }
        }