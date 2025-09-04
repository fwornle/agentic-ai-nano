# 📝 Session 4: Context Optimization Methods

> **📝 PARTICIPANT PATH CONTENT**
> Prerequisites: Complete 🎯 Observer path and previous 📝 Participant files
> Time Investment: 45-60 minutes
> Outcome: Context window optimization system

## Learning Outcomes

After completing this optimization guide, you will:

- Build context window optimization systems  
- Implement relevance-based content selection  
- Create hierarchical summarization strategies  
- Develop semantic compression techniques  

## Context Window Optimization Framework

### The Token Budget Challenge

LLMs have finite context windows, and production systems need to maximize information density within those constraints. Poor context optimization wastes precious tokens on redundant information while missing critical details that could improve generation quality.

### Step 1: Context Window Optimizer Setup

Build the foundation for intelligent context assembly:

```python
class ContextWindowOptimizer:
    """Optimize context assembly for maximum information density."""

    def __init__(self, llm_tokenizer, max_context_tokens: int = 4000):
        self.tokenizer = llm_tokenizer
        self.max_context_tokens = max_context_tokens

        # Context optimization strategies
        self.optimization_strategies = {
            'relevance_ranking': self._relevance_based_selection,
            'diversity_clustering': self._diversity_based_selection,
            'hierarchical_summary': self._hierarchical_summarization,
            'semantic_compression': self._semantic_compression
        }
```

**Token Management**: Setting up tokenizer and context limits enables precise control over the information density within LLM context windows.

```python
    def optimize_context_window(self, query: str,
                               retrieved_chunks: List[Dict],
                               strategy: str = 'relevance_ranking') -> Dict[str, Any]:
        """Optimize context window using specified strategy."""

        # Calculate available token budget
        query_tokens = len(self.tokenizer.encode(query))
        available_tokens = self.max_context_tokens - query_tokens - 200  # Buffer

        # Apply optimization strategy
        optimized_context = self.optimization_strategies[strategy](
            query, retrieved_chunks, available_tokens
        )

        return {
            'optimized_context': optimized_context['context'],
            'selected_chunks': optimized_context['chunks'],
            'context_tokens': optimized_context['token_count'],
            'efficiency_score': optimized_context['efficiency'],
            'strategy_used': strategy,
            'original_chunk_count': len(retrieved_chunks)
        }
```

**Strategy Selection**: Multiple optimization approaches allow choosing the best method based on the specific characteristics of retrieved content and query requirements.

### Step 2: Relevance-Based Context Selection

Implement the core relevance-based selection strategy:

```python
def _relevance_based_selection(self, query: str, chunks: List[Dict],
                             token_budget: int) -> Dict[str, Any]:
    """Select chunks based on relevance scores and token efficiency."""

    # Calculate relevance scores and token costs
    chunk_analysis = []
    for i, chunk in enumerate(chunks):
        content = chunk['document'].page_content
        tokens = len(self.tokenizer.encode(content))
        relevance = 1 - chunk.get('similarity_score', 0.5)  # Convert distance to similarity

        # Calculate efficiency: relevance per token
        efficiency = relevance / tokens if tokens > 0 else 0
```

**Efficiency Calculation**: Computing relevance-per-token ratios enables optimal selection of chunks that provide maximum information value within token constraints.

```python
        chunk_analysis.append({
            'index': i,
            'content': content,
            'tokens': tokens,
            'relevance': relevance,
            'efficiency': efficiency,
            'metadata': chunk.get('metadata', {})
        })

    # Sort by efficiency (relevance per token)
    chunk_analysis.sort(key=lambda x: x['efficiency'], reverse=True)
```

**Efficiency Ranking**: Sorting chunks by efficiency ensures the most valuable content per token is prioritized for inclusion in the context window.

```python
    # Select chunks within token budget
    selected_chunks = []
    total_tokens = 0

    for chunk_data in chunk_analysis:
        if total_tokens + chunk_data['tokens'] <= token_budget:
            selected_chunks.append(chunk_data)
            total_tokens += chunk_data['tokens']
        else:
            break
```

**Budget Management**: Greedy selection based on efficiency ensures optimal use of available tokens while staying within limits.

```python
    # Assemble context
    context_parts = []
    for chunk_data in selected_chunks:
        source = chunk_data['metadata'].get('source', 'Unknown')
        context_parts.append(f"[Source: {source}]\n{chunk_data['content']}")

    final_context = '\n\n'.join(context_parts)

    return {
        'context': final_context,
        'chunks': selected_chunks,
        'token_count': total_tokens,
        'efficiency': np.mean([c['efficiency'] for c in selected_chunks])
    }
```

### Step 3: Diversity-Based Selection

Implement selection that balances relevance with information diversity:

```python
def _diversity_based_selection(self, query: str, chunks: List[Dict],
                              token_budget: int) -> Dict[str, Any]:
    """Select chunks balancing relevance and diversity."""

    # Get embeddings for all chunks
    chunk_texts = [chunk['document'].page_content for chunk in chunks]
    chunk_embeddings = self.embedding_model.encode(chunk_texts)

    # Calculate diversity scores using clustering
    diversity_scores = self._calculate_diversity_scores(chunk_embeddings)

    selected_chunks = []
    total_tokens = 0
    used_indices = set()
```

**Diversity Strategy**: Balancing relevance with information diversity ensures comprehensive coverage while avoiding redundant content.

```python
    while total_tokens < token_budget and len(used_indices) < len(chunks):
        best_score = -1
        best_idx = -1

        for i, chunk in enumerate(chunks):
            if i in used_indices:
                continue

            content = chunk['document'].page_content
            tokens = len(self.tokenizer.encode(content))

            if total_tokens + tokens > token_budget:
                continue

            relevance = 1 - chunk.get('similarity_score', 0.5)
            diversity = diversity_scores[i]

            # Combined score balancing relevance and diversity
            combined_score = 0.7 * relevance + 0.3 * diversity

            if combined_score > best_score:
                best_score = combined_score
                best_idx = i

        if best_idx == -1:
            break

        # Add selected chunk
        selected_chunk = chunks[best_idx]
        content = selected_chunk['document'].page_content
        tokens = len(self.tokenizer.encode(content))

        selected_chunks.append({
            'content': content,
            'tokens': tokens,
            'relevance': 1 - selected_chunk.get('similarity_score', 0.5),
            'diversity': diversity_scores[best_idx],
            'metadata': selected_chunk.get('metadata', {})
        })

        total_tokens += tokens
        used_indices.add(best_idx)
```

**Selection Algorithm**: Iteratively selecting chunks that optimize the combination of relevance and diversity scores.

### Step 4: Hierarchical Summarization

Implement intelligent summarization when content exceeds budget:

```python
def _hierarchical_summarization(self, query: str, chunks: List[Dict],
                              token_budget: int) -> Dict[str, Any]:
    """Create hierarchical summaries when context exceeds budget."""

    # Group chunks by source/topic
    chunk_groups = self._group_chunks_by_source(chunks)

    summarized_chunks = []
    total_tokens = 0
```

**Grouping Strategy**: Organizing chunks by source or topic enables intelligent summarization that preserves information coherence while reducing token usage.

```python
    for group_key, group_chunks in chunk_groups.items():
        # Calculate total tokens for this group
        group_content = '\n'.join([
            chunk['document'].page_content for chunk in group_chunks
        ])
        group_tokens = len(self.tokenizer.encode(group_content))

        if group_tokens > token_budget // 4:  # Group too large, summarize
            summary = self._summarize_chunk_group(query, group_chunks)
            summary_tokens = len(self.tokenizer.encode(summary))
```

**Adaptive Summarization**: Groups exceeding 25% of token budget are summarized to maintain information while fitting constraints.

```python
            if total_tokens + summary_tokens <= token_budget:
                summarized_chunks.append({
                    'content': summary,
                    'tokens': summary_tokens,
                    'type': 'summary',
                    'source_count': len(group_chunks),
                    'group_key': group_key
                })
                total_tokens += summary_tokens
```

**Summary Integration**: Summarized content is tracked with metadata indicating its condensed nature and original source count.

```python
        else:
            # Use original chunks if they fit
            for chunk in group_chunks:
                content = chunk['document'].page_content
                chunk_tokens = len(self.tokenizer.encode(content))

                if total_tokens + chunk_tokens <= token_budget:
                    summarized_chunks.append({
                        'content': content,
                        'tokens': chunk_tokens,
                        'type': 'original',
                        'group_key': group_key,
                        'metadata': chunk.get('metadata', {})
                    })
                    total_tokens += chunk_tokens
```

**Original Content Preservation**: Smaller groups remain intact to preserve detailed information when token budget allows.

### Step 5: Chunk Group Summarization

Implement intelligent group summarization:

```python
def _summarize_chunk_group(self, query: str, group_chunks: List[Dict]) -> str:
    """Summarize a group of related chunks."""

    group_content = '\n---\n'.join([
        chunk['document'].page_content for chunk in group_chunks
    ])

    summarization_prompt = f"""
    Summarize the following related content sections in the context of this query: {query}

    Content sections:
    {group_content[:2000]}  # Limit input to prevent prompt bloat

    Create a comprehensive summary that:
    1. Preserves key information relevant to the query
    2. Maintains important details and examples
    3. Removes redundancy and verbose explanations
    4. Keeps technical accuracy intact

    Summary:
    """
```

**Summarization Strategy**: Query-aware summarization ensures summaries focus on information most relevant to the user's needs.

```python
    try:
        summary = self.llm_model.predict(summarization_prompt)
        return summary.strip()
    except Exception as e:
        print(f"Summarization error: {e}")
        # Fallback: truncate original content
        return group_content[:500] + "..."
```

### Step 6: Source-Based Chunk Grouping

Group related chunks for coherent summarization:

```python
def _group_chunks_by_source(self, chunks: List[Dict]) -> Dict[str, List[Dict]]:
    """Group chunks by source for coherent processing."""

    groups = defaultdict(list)

    for chunk in chunks:
        # Extract source identifier
        source = chunk.get('metadata', {}).get('source', 'unknown')

        # Create semantic groups if no source available
        if source == 'unknown':
            # Use first few words as grouping key
            content = chunk['document'].page_content
            group_key = ' '.join(content.split()[:5])
            groups[group_key].append(chunk)
        else:
            groups[source].append(chunk)

    return dict(groups)
```

**Grouping Logic**: Intelligent grouping by source or semantic similarity enables coherent summarization and content organization.

### Step 7: Semantic Compression

Implement advanced semantic compression techniques:

```python
def _semantic_compression(self, query: str, chunks: List[Dict],
                         token_budget: int) -> Dict[str, Any]:
    """Apply semantic compression to maximize information density."""

    compressed_chunks = []
    total_tokens = 0

    for chunk in chunks:
        content = chunk['document'].page_content
        original_tokens = len(self.tokenizer.encode(content))

        # Skip if chunk is already efficient
        if original_tokens <= 100:
            if total_tokens + original_tokens <= token_budget:
                compressed_chunks.append({
                    'content': content,
                    'tokens': original_tokens,
                    'compression_ratio': 1.0,
                    'type': 'original'
                })
                total_tokens += original_tokens
            continue
```

**Efficiency Threshold**: Small chunks bypass compression to avoid unnecessary processing overhead.

```python
        # Compress larger chunks
        compressed_content = self._compress_chunk_content(content, query)
        compressed_tokens = len(self.tokenizer.encode(compressed_content))

        if total_tokens + compressed_tokens <= token_budget:
            compression_ratio = original_tokens / compressed_tokens

            compressed_chunks.append({
                'content': compressed_content,
                'tokens': compressed_tokens,
                'compression_ratio': compression_ratio,
                'type': 'compressed'
            })
            total_tokens += compressed_tokens
```

**Compression Processing**: Larger chunks undergo semantic compression to reduce token usage while preserving meaning.

### Step 8: Content Compression Implementation

Create the core content compression method:

```python
def _compress_chunk_content(self, content: str, query: str) -> str:
    """Compress content while preserving query-relevant information."""

    compression_prompt = f"""
    Compress the following content while preserving information relevant to: {query}

    Original content:
    {content}

    Requirements:
    1. Remove verbose explanations and redundant phrases
    2. Preserve key facts, data, and technical details
    3. Maintain logical flow and context
    4. Keep examples that illustrate important points
    5. Reduce word count by approximately 30-50%

    Compressed content:
    """
```

**Compression Strategy**: Query-aware compression focuses on preserving information most relevant to the user's needs while reducing verbosity.

```python
    try:
        compressed = self.llm_model.predict(compression_prompt)
        return compressed.strip()
    except Exception as e:
        print(f"Compression error: {e}")
        # Fallback: simple truncation
        words = content.split()
        truncated_length = int(len(words) * 0.7)
        return ' '.join(words[:truncated_length])
```

**Error Handling**: Robust fallback to simple truncation ensures system reliability even when compression fails.

### Step 9: Optimization Strategy Selection

Implement intelligent strategy selection based on content characteristics:

```python
def select_optimization_strategy(self, query: str, chunks: List[Dict]) -> str:
    """Select optimal strategy based on content characteristics."""

    total_chunks = len(chunks)
    total_tokens = sum(len(self.tokenizer.encode(chunk['document'].page_content))
                      for chunk in chunks)
    avg_chunk_size = total_tokens / total_chunks if total_chunks > 0 else 0

    # Calculate content diversity
    chunk_sources = set(chunk.get('metadata', {}).get('source', 'unknown')
                       for chunk in chunks)
    source_diversity = len(chunk_sources) / total_chunks if total_chunks > 0 else 0
```

**Content Analysis**: Analyzing chunk count, token distribution, and source diversity guides optimal strategy selection.

```python
    # Strategy selection logic
    if total_tokens <= self.max_context_tokens * 0.8:
        return 'relevance_ranking'  # Simple case, use relevance

    elif source_diversity > 0.5:
        return 'hierarchical_summary'  # High diversity, use summarization

    elif avg_chunk_size > 500:
        return 'semantic_compression'  # Large chunks, compress

    else:
        return 'diversity_clustering'  # Complex case, balance diversity
```

**Selection Logic**: Rule-based strategy selection based on content characteristics ensures optimal optimization approach.

## Testing Your Context Optimization System

Test the complete optimization system with different scenarios:

```python
# Test the context optimization system
optimizer = ContextWindowOptimizer(tokenizer, max_context_tokens=4000)

# Test with high-token content
large_chunks = [create_large_chunk() for _ in range(10)]
relevance_result = optimizer.optimize_context_window(
    "How to implement authentication?",
    large_chunks,
    strategy='relevance_ranking'
)

# Test with diverse sources
diverse_chunks = [create_diverse_chunk(source=f"source_{i}") for i in range(15)]
summary_result = optimizer.optimize_context_window(
    "What are microservices best practices?",
    diverse_chunks,
    strategy='hierarchical_summary'
)

print("Optimization Results:")
print(f"Relevance strategy tokens: {relevance_result['context_tokens']}")
print(f"Summary strategy tokens: {summary_result['context_tokens']}")
print(f"Efficiency scores: {relevance_result['efficiency_score']:.3f}, {summary_result['efficiency_score']:.3f}")
```

## Integration with RAG Pipeline

Connect your optimization system to the complete RAG pipeline:

```python
def enhanced_rag_pipeline(self, query: str, vector_store):
    """Complete RAG pipeline with query enhancement and context optimization."""

    # Step 1: Enhanced query generation
    hyde_result = self.hyde_enhancer.enhance_query_with_hyde(query)
    expansion_result = self.query_expander.expand_query(query)

    # Step 2: Multi-strategy retrieval
    hyde_results = vector_store.similarity_search_by_vector(
        hyde_result['enhanced_embedding'], k=20
    )

    expanded_results = vector_store.similarity_search(
        expansion_result['expanded_query'], k=20
    )

    # Combine and deduplicate results
    all_results = self._combine_and_rank_results(
        hyde_results, expanded_results, query
    )

    # Step 3: Context optimization
    optimized_context = self.context_optimizer.optimize_context_window(
        query, all_results
    )

    # Step 4: Generate response with optimized context
    response = self._generate_response(
        query, optimized_context['optimized_context']
    )

    return {
        'response': response,
        'context_tokens': optimized_context['context_tokens'],
        'optimization_strategy': optimized_context['strategy_used'],
        'source_count': optimized_context['original_chunk_count'],
        'selected_count': len(optimized_context['selected_chunks'])
    }
```

**Pipeline Integration**: Complete RAG pipeline combining query enhancement, retrieval, context optimization, and response generation.

## Practice Exercises

1. **Strategy Comparison**: Compare different optimization strategies on the same content  
2. **Token Efficiency**: Measure information retention vs. token reduction ratios  
3. **Quality Assessment**: Evaluate response quality with different optimization approaches  
4. **Performance Testing**: Benchmark optimization speed and memory usage

---

## 🧭 Navigation

**Previous:** [Session 3 - Advanced Patterns →](Session3_Performance_Optimization.md)  
**Next:** [Session 5 - Type-Safe Development →](Session5_RAG_Evaluation_Quality_Assessment.md)

---
