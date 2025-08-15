# Session 1 - Module B: Performance Optimization (35 minutes)

**Prerequisites**: [Session 1 Core Section Complete](Session1_Bare_Metal_Agents.md)  
**Target Audience**: Performance-focused developers  
**Cognitive Load**: 5 optimization concepts

---

## 🎯 Module Overview

This module focuses on optimizing bare metal agents for performance, memory efficiency, and speed. You'll learn memory management patterns, tool execution optimization, and response time improvement strategies essential for production agent systems.

### Learning Objectives
By the end of this module, you will:
- Implement efficient memory usage patterns and conversation history optimization
- Optimize tool execution speed through caching and parallel execution
- Design strategies for faster agent responses and improved user experience
- Build performance monitoring and analytics systems for continuous optimization

---

## Part 1: Memory Management (15 minutes)

### Efficient Memory Usage Patterns

🗂️ **File**: `src/session1/memory_optimized_agent.py` - Memory-efficient agent implementations

Memory management is crucial for long-running agent systems that need to maintain conversation context without memory leaks:

```python
from collections import deque
from typing import Dict, List, Any, Optional
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MemoryEntry:
    content: str
    timestamp: datetime
    importance_score: float
    size_bytes: int

class MemoryOptimizedAgent(BaseAgent):
    """Agent with intelligent memory management for long conversations"""
    
    def __init__(self, name: str, llm_client, max_memory_mb: float = 10.0):
        super().__init__(name, "Memory optimized agent", llm_client)
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.memory_entries: deque = deque(maxlen=1000)  # Hard limit
        self.importance_threshold = 0.5
        self.cleanup_interval = 100  # Clean up every N messages
        self.message_count = 0
```

### Conversation History Optimization

```python
def add_to_memory(self, content: str, importance_score: float = 0.5):
    """Add content to memory with intelligent sizing and cleanup"""
    
    # Calculate memory footprint
    content_size = sys.getsizeof(content)
    
    # Create memory entry
    entry = MemoryEntry(
        content=content,
        timestamp=datetime.now(),
        importance_score=importance_score,
        size_bytes=content_size
    )
    
    # Check if cleanup is needed
    self.message_count += 1
    if self.message_count % self.cleanup_interval == 0:
        self._cleanup_memory()
    
    # Add entry
    self.memory_entries.append(entry)
    
    # Force cleanup if memory limit exceeded
    if self._get_total_memory_usage() > self.max_memory_bytes:
        self._aggressive_cleanup()

def _cleanup_memory(self):
    """Intelligent memory cleanup based on importance and age"""
    
    if not self.memory_entries:
        return
    
    # Remove low-importance old entries
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    # Convert to list for easier manipulation
    entries_list = list(self.memory_entries)
    
    # Sort by importance and age (keep important recent items)
    entries_list.sort(key=lambda x: (x.importance_score, x.timestamp))
    
    # Keep top 70% of entries
    keep_count = int(len(entries_list) * 0.7)
    entries_to_keep = entries_list[-keep_count:]
    
    # Update deque
    self.memory_entries.clear()
    for entry in entries_to_keep:
        self.memory_entries.append(entry)
    
    self.logger.info(f"Memory cleanup: kept {len(entries_to_keep)} entries")

def _get_total_memory_usage(self) -> int:
    """Calculate total memory usage in bytes"""
    return sum(entry.size_bytes for entry in self.memory_entries)

def get_memory_stats(self) -> Dict[str, Any]:
    """Get comprehensive memory usage statistics"""
    total_entries = len(self.memory_entries)
    total_bytes = self._get_total_memory_usage()
    
    if total_entries > 0:
        avg_importance = sum(e.importance_score for e in self.memory_entries) / total_entries
        oldest_entry = min(self.memory_entries, key=lambda x: x.timestamp)
        newest_entry = max(self.memory_entries, key=lambda x: x.timestamp)
        
        return {
            "total_entries": total_entries,
            "total_memory_mb": total_bytes / (1024 * 1024),
            "avg_importance_score": avg_importance,
            "memory_utilization_pct": (total_bytes / self.max_memory_bytes) * 100,
            "oldest_entry_age_hours": (datetime.now() - oldest_entry.timestamp).total_seconds() / 3600,
            "memory_span_hours": (newest_entry.timestamp - oldest_entry.timestamp).total_seconds() / 3600
        }
    
    return {"total_entries": 0, "total_memory_mb": 0}
```

### Context Compression Strategies

```python
def get_compressed_context(self, max_context_size: int = 2000) -> str:
    """Get compressed conversation context for LLM calls"""
    
    # Sort entries by importance and recency
    sorted_entries = sorted(
        self.memory_entries,
        key=lambda x: (x.importance_score * 0.7 + self._recency_score(x) * 0.3),
        reverse=True
    )
    
    # Build context within size limit
    context_parts = []
    current_size = 0
    
    for entry in sorted_entries:
        if current_size + len(entry.content) > max_context_size:
            break
        
        context_parts.append(entry.content)
        current_size += len(entry.content)
    
    # Add summary if we had to truncate
    if len(context_parts) < len(sorted_entries):
        truncated_count = len(sorted_entries) - len(context_parts)
        summary = f"\n[... {truncated_count} earlier messages truncated for length ...]"
        context_parts.append(summary)
    
    return "\n".join(context_parts)

def _recency_score(self, entry: MemoryEntry) -> float:
    """Calculate recency score (1.0 = most recent, 0.0 = oldest)"""
    if not self.memory_entries:
        return 1.0
    
    oldest = min(self.memory_entries, key=lambda x: x.timestamp)
    newest = max(self.memory_entries, key=lambda x: x.timestamp)
    
    total_span = (newest.timestamp - oldest.timestamp).total_seconds()
    if total_span == 0:
        return 1.0
    
    entry_age = (newest.timestamp - entry.timestamp).total_seconds()
    return 1.0 - (entry_age / total_span)
```

---

## Part 2: Tool Execution Speed (10 minutes)

### Caching and Parallel Execution

🗂️ **File**: `src/session1/optimized_tools.py` - High-performance tool implementations

```python
import asyncio
from functools import lru_cache
from typing import Dict, List, Any, Callable
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class OptimizedToolAgent(BaseAgent):
    """Agent with high-performance tool execution"""
    
    def __init__(self, name: str, llm_client, tools: List[Tool]):
        super().__init__(name, "Optimized tool agent", llm_client)
        self.tools = {tool.name: tool for tool in tools}
        self.tool_cache = {}
        self.execution_stats = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
    def _cache_key(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Generate cache key for tool execution"""
        # Create deterministic hash of tool name and parameters
        param_str = str(sorted(params.items()))
        cache_input = f"{tool_name}:{param_str}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _is_cacheable(self, tool_name: str) -> bool:
        """Determine if tool results should be cached"""
        # Don't cache tools that have side effects or time-dependent results
        non_cacheable = {"web_search", "current_time", "random_generator", "file_write"}
        return tool_name not in non_cacheable
```

### Intelligent Tool Caching

```python
async def execute_tool_cached(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute tool with intelligent caching"""
    
    start_time = time.time()
    
    # Check cache first
    if self._is_cacheable(tool_name):
        cache_key = self._cache_key(tool_name, params)
        if cache_key in self.tool_cache:
            cached_result = self.tool_cache[cache_key]
            # Check if cache entry is still valid (within 1 hour)
            if time.time() - cached_result["timestamp"] < 3600:
                execution_time = time.time() - start_time
                self._update_stats(tool_name, execution_time, True)
                return cached_result["result"]
    
    # Execute tool
    if tool_name not in self.tools:
        raise ValueError(f"Tool {tool_name} not available")
    
    tool = self.tools[tool_name]
    result = await tool.execute(params)
    
    # Cache result if appropriate
    if self._is_cacheable(tool_name):
        self.tool_cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
    
    # Update performance stats
    execution_time = time.time() - start_time
    self._update_stats(tool_name, execution_time, False)
    
    return result

def _update_stats(self, tool_name: str, execution_time: float, cache_hit: bool):
    """Update tool execution statistics"""
    if tool_name not in self.execution_stats:
        self.execution_stats[tool_name] = {
            "total_calls": 0,
            "cache_hits": 0,
            "total_time": 0.0,
            "avg_time": 0.0
        }
    
    stats = self.execution_stats[tool_name]
    stats["total_calls"] += 1
    stats["total_time"] += execution_time
    stats["avg_time"] = stats["total_time"] / stats["total_calls"]
    
    if cache_hit:
        stats["cache_hits"] += 1
```

### Parallel Tool Execution

```python
async def execute_tools_parallel(self, tool_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Execute multiple tools in parallel for better performance"""
    
    async def execute_single_tool(request):
        tool_name = request["tool"]
        params = request.get("params", {})
        try:
            result = await self.execute_tool_cached(tool_name, params)
            return {"success": True, "result": result, "tool": tool_name}
        except Exception as e:
            return {"success": False, "error": str(e), "tool": tool_name}
    
    # Execute all tool requests concurrently
    tasks = [execute_single_tool(request) for request in tool_requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any exceptions
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            processed_results.append({
                "success": False,
                "error": str(result),
                "tool": "unknown"
            })
        else:
            processed_results.append(result)
    
    return processed_results

def get_performance_stats(self) -> Dict[str, Any]:
    """Get comprehensive performance statistics"""
    total_calls = sum(stats["total_calls"] for stats in self.execution_stats.values())
    total_cache_hits = sum(stats["cache_hits"] for stats in self.execution_stats.values())
    
    cache_hit_rate = (total_cache_hits / total_calls * 100) if total_calls > 0 else 0
    
    return {
        "total_tool_calls": total_calls,
        "total_cache_hits": total_cache_hits,
        "cache_hit_rate_pct": cache_hit_rate,
        "tool_stats": dict(self.execution_stats),
        "cache_size": len(self.tool_cache),
        "thread_pool_size": self.thread_pool._max_workers
    }
```

---

## Part 3: Response Time Optimization (10 minutes)

### Faster Agent Responses

🗂️ **File**: `src/session1/fast_response_agent.py` - Speed-optimized agent implementations

```python
import asyncio
from typing import Optional, Dict, Any
import time

class FastResponseAgent(BaseAgent):
    """Agent optimized for minimal response latency"""
    
    def __init__(self, name: str, llm_client):
        super().__init__(name, "Fast response agent", llm_client)
        self.response_cache = {}
        self.precomputed_responses = {}
        self.response_times = []
        self.target_response_time = 2.0  # seconds
        
    async def process_message_fast(self, message: str) -> Dict[str, Any]:
        """Process message with speed optimizations"""
        start_time = time.time()
        
        # Check for exact match in cache
        if message in self.response_cache:
            response = self.response_cache[message]
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            return {
                "response": response,
                "response_time": response_time,
                "cache_hit": True
            }
        
        # Check for similar message (fuzzy matching)
        similar_response = self._find_similar_response(message)
        if similar_response:
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            return {
                "response": similar_response,
                "response_time": response_time,
                "cache_hit": "fuzzy"
            }
        
        # Generate new response with timeout
        try:
            response = await asyncio.wait_for(
                self._generate_response_with_context(message),
                timeout=self.target_response_time
            )
        except asyncio.TimeoutError:
            response = self._get_fallback_response(message)
        
        # Cache the response
        self.response_cache[message] = response
        
        response_time = time.time() - start_time
        self.response_times.append(response_time)
        
        return {
            "response": response,
            "response_time": response_time,
            "cache_hit": False
        }
    
    def _find_similar_response(self, message: str) -> Optional[str]:
        """Find cached response for similar message using fuzzy matching"""
        message_words = set(message.lower().split())
        
        best_match = None
        best_similarity = 0.0
        
        for cached_message, cached_response in self.response_cache.items():
            cached_words = set(cached_message.lower().split())
            
            # Calculate Jaccard similarity
            intersection = message_words & cached_words
            union = message_words | cached_words
            
            if union:
                similarity = len(intersection) / len(union)
                if similarity > 0.7 and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = cached_response
        
        return best_match
    
    def _get_fallback_response(self, message: str) -> str:
        """Generate quick fallback response when main processing times out"""
        fallback_responses = [
            "I'm processing your request. Could you please rephrase or simplify your question?",
            "I understand you're asking about this topic. Let me provide a brief response while I gather more details.",
            "That's an interesting question. Here's what I can tell you immediately..."
        ]
        
        # Select fallback based on message characteristics
        if "?" in message:
            return fallback_responses[0]
        elif len(message.split()) > 20:
            return fallback_responses[1]
        else:
            return fallback_responses[2]
```

### Performance Monitoring

```python
def get_response_time_stats(self) -> Dict[str, Any]:
    """Get detailed response time analytics"""
    if not self.response_times:
        return {"no_data": True}
    
    sorted_times = sorted(self.response_times)
    n = len(sorted_times)
    
    return {
        "total_responses": n,
        "avg_response_time": sum(sorted_times) / n,
        "min_response_time": min(sorted_times),
        "max_response_time": max(sorted_times),
        "p50_response_time": sorted_times[n // 2],
        "p90_response_time": sorted_times[int(n * 0.9)],
        "p95_response_time": sorted_times[int(n * 0.95)],
        "responses_under_target": sum(1 for t in sorted_times if t < self.target_response_time),
        "target_achievement_rate": sum(1 for t in sorted_times if t < self.target_response_time) / n * 100,
        "cache_entries": len(self.response_cache)
    }

async def optimize_performance(self):
    """Automatically optimize agent performance based on metrics"""
    stats = self.get_response_time_stats()
    
    if stats.get("no_data"):
        return
    
    # Adjust target response time based on performance
    if stats["target_achievement_rate"] > 90:
        # Performing well, can be more ambitious
        self.target_response_time *= 0.9
    elif stats["target_achievement_rate"] < 50:
        # Struggling, be more lenient
        self.target_response_time *= 1.2
    
    # Clean cache if it's getting too large
    if len(self.response_cache) > 1000:
        # Keep only most recent 500 entries
        items = list(self.response_cache.items())
        self.response_cache = dict(items[-500:])
    
    self.logger.info(f"Performance optimization: target time {self.target_response_time:.2f}s, cache size {len(self.response_cache)}")
```

---

## 🎯 Module Summary

You've now mastered performance optimization for bare metal agents:

✅ **Memory Management**: Implemented efficient memory usage and conversation history optimization  
✅ **Tool Execution Speed**: Built caching and parallel execution systems for faster tool usage  
✅ **Response Time Optimization**: Created strategies for faster agent responses with fallback mechanisms  
✅ **Performance Monitoring**: Designed analytics systems for continuous performance improvement

### Next Steps
- **Continue to Module C**: [Complex State Management](Session1_ModuleC_Complex_State_Management.md) for advanced memory systems
- **Return to Core**: [Session 1 Main](Session1_Bare_Metal_Agents.md)
- **Advance to Session 2**: [LangChain Foundations](Session2_LangChain_Foundations.md)

---

**🗂️ Source Files for Module B:**
- `src/session1/memory_optimized_agent.py` - Memory-efficient agent implementations
- `src/session1/optimized_tools.py` - High-performance tool execution
- `src/session1/fast_response_agent.py` - Speed-optimized response generation