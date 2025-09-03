# 📝 Session 4: Query Expansion Practice

> **📝 PARTICIPANT PATH CONTENT**
> Prerequisites: Complete 🎯 Observer path and [📝 HyDE Implementation](Session4_HyDE_Implementation.md)
> Time Investment: 45-60 minutes
> Outcome: Multi-strategy query expansion system

## Learning Outcomes

After completing this practice guide, you will:

- Build intelligent query expansion systems  
- Implement multiple expansion strategies (semantic, contextual, domain-specific)  
- Create multi-query generation from different perspectives  
- Develop query decomposition for complex questions  

## Complete Query Expansion System

### Step 1: Intelligent Query Expander Setup

Build a comprehensive query expansion system with multiple strategies:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import wordnet
from collections import defaultdict

class IntelligentQueryExpander:
    """Advanced query expansion using multiple strategies."""

    def __init__(self, llm_model, domain_corpus: Optional[List[str]] = None):
        self.llm_model = llm_model
        self.domain_corpus = domain_corpus
```

**Query Expansion Libraries**: These imports provide statistical analysis, semantic relationships, and domain-specific term extraction capabilities.

```python
        # Initialize expansion strategies
        self.expansion_strategies = {
            'synonym': self._synonym_expansion,
            'semantic': self._semantic_expansion,
            'contextual': self._contextual_expansion,
            'domain_specific': self._domain_specific_expansion
        }

        # Domain-specific TF-IDF if corpus provided
        if domain_corpus:
            self.domain_tfidf = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            self.domain_tfidf.fit(domain_corpus)
```

**Strategy Framework**: Multiple expansion approaches ensure comprehensive coverage - from simple synonyms to complex semantic relationships and domain-specific terminology.

### Step 2: Core Expansion Workflow

Implement the main query expansion coordination system:

```python
def expand_query(self, query: str,
                strategies: List[str] = ['semantic', 'contextual'],
                max_expansions: int = 5) -> Dict[str, Any]:
    """Expand query using multiple strategies."""

    expansion_results = {}
    combined_expansions = set()

    # Apply each expansion strategy
    for strategy in strategies:
        if strategy in self.expansion_strategies:
            expansions = self.expansion_strategies[strategy](
                query, max_expansions
            )
            expansion_results[strategy] = expansions
            combined_expansions.update(expansions)
```

**Multi-Strategy Coordination**: Coordinating different expansion approaches allows leveraging the strengths of each method for comprehensive query enhancement.

```python
    # Create final expanded query
    expanded_query = self._create_expanded_query(
        query, list(combined_expansions)
    )

    return {
        'original_query': query,
        'expansions_by_strategy': expansion_results,
        'all_expansions': list(combined_expansions),
        'expanded_query': expanded_query,
        'expansion_count': len(combined_expansions)
    }
```

### Step 3: Semantic Expansion Using LLM

Generate semantically related terms using LLM understanding:

```python
def _semantic_expansion(self, query: str, max_expansions: int) -> List[str]:
    """Generate semantic expansions using LLM understanding."""

    semantic_prompt = f"""
    Given this query, generate {max_expansions} semantically related terms or phrases:

    Query: {query}

    Requirements:
    1. Include synonyms and related concepts
    2. Add domain-specific terminology if applicable
    3. Include both broader and narrower terms
    4. Focus on terms likely to appear in relevant documents

    Return only the expanded terms, one per line:
    """
```

**Semantic Expansion Strategy**: Using LLM understanding to generate related terms creates expansions that capture conceptual relationships beyond simple synonyms.

```python
    try:
        response = self.llm_model.predict(semantic_prompt)
        expansions = [
            term.strip()
            for term in response.strip().split('\n')
            if term.strip() and not term.strip().startswith(('-', '*', '•'))
        ]
        return expansions[:max_expansions]

    except Exception as e:
        print(f"Semantic expansion error: {e}")
        return []
```

**Response Processing**: Filtering and cleaning LLM output ensures we get high-quality expansion terms while removing formatting artifacts.

### Step 4: Contextual Query Reformulation

Create multiple ways to express the same information need:

```python
def _contextual_expansion(self, query: str, max_expansions: int) -> List[str]:
    """Generate contextual reformulations of the query."""

    reformulation_prompt = f"""
    Reformulate this query in {max_expansions} different ways that express the same information need:

    Original Query: {query}

    Create variations that:
    1. Use different phrasing and vocabulary
    2. Approach the question from different angles
    3. Include both specific and general formulations
    4. Maintain the original intent and meaning

    Reformulations:
    """
```

**Reformulation Strategy**: Creating multiple ways to express the same information need increases the likelihood of matching documents with different linguistic styles.

```python
    try:
        response = self.llm_model.predict(reformulation_prompt)
        reformulations = [
            reform.strip().rstrip('.')
            for reform in response.strip().split('\n')
            if reform.strip() and ('?' in reform or len(reform.split()) > 3)
        ]
        return reformulations[:max_expansions]

    except Exception as e:
        print(f"Contextual expansion error: {e}")
        return []
```

**Quality Filtering**: Ensuring reformulations are substantive questions rather than fragments improves the quality of query variations.

### Step 5: Domain-Specific Expansion

Use domain knowledge to enhance queries with specialized terminology:

```python
def _domain_specific_expansion(self, query: str, max_expansions: int) -> List[str]:
    """Generate domain-specific expansions using corpus knowledge."""

    if not hasattr(self, 'domain_tfidf'):
        return []

    # Transform query to TF-IDF vector
    query_vector = self.domain_tfidf.transform([query])

    # Get feature names and scores
    feature_names = self.domain_tfidf.get_feature_names_out()
    tfidf_scores = query_vector.toarray()[0]

    # Find highly relevant terms
    term_scores = list(zip(feature_names, tfidf_scores))
    term_scores.sort(key=lambda x: x[1], reverse=True)
```

**Domain Knowledge Integration**: Using TF-IDF analysis of domain-specific corpus to identify relevant specialized terms.

```python
    # Extract top domain terms not in original query
    query_terms = set(query.lower().split())
    domain_expansions = []

    for term, score in term_scores[:max_expansions * 3]:
        if score > 0 and term not in query_terms:
            domain_expansions.append(term)
            if len(domain_expansions) >= max_expansions:
                break

    return domain_expansions
```

### Step 6: Multi-Query Generation System

Generate comprehensive query sets from multiple perspectives:

```python
class MultiQueryGenerator:
    """Generate multiple query perspectives for comprehensive retrieval."""

    def __init__(self, llm_model):
        self.llm_model = llm_model

        self.query_perspectives = {
            'decomposition': self._decompose_complex_query,
            'specificity_levels': self._generate_specificity_variants,
            'temporal_variants': self._generate_temporal_variants,
            'perspective_shifts': self._generate_perspective_variants,
            'domain_focused': self._generate_domain_variants
        }
```

**Perspective Framework**: Multiple query generation approaches ensure comprehensive coverage by viewing the same information need from different angles and specificity levels.

```python
    def generate_multi_query_set(self, query: str,
                               perspectives: List[str] = None,
                               total_queries: int = 8) -> Dict[str, Any]:
        """Generate comprehensive query set from multiple perspectives."""

        if perspectives is None:
            perspectives = ['decomposition', 'specificity_levels', 'perspective_shifts']

        all_queries = {'original': query}
        generation_metadata = {}

        # Distribute query generation across perspectives
        queries_per_perspective = total_queries // len(perspectives)
        remaining_queries = total_queries % len(perspectives)
```

**Query Distribution Strategy**: Intelligently distributing query generation across different perspectives ensures balanced coverage of the information space.

```python
        for i, perspective in enumerate(perspectives):
            num_queries = queries_per_perspective
            if i < remaining_queries:
                num_queries += 1

            generated = self.query_perspectives[perspective](query, num_queries)
            all_queries[perspective] = generated

            generation_metadata[perspective] = {
                'count': len(generated),
                'method': perspective
            }

        # Flatten and deduplicate
        flattened_queries = self._flatten_and_deduplicate(all_queries)

        return {
            'original_query': query,
            'query_variants': flattened_queries,
            'queries_by_perspective': all_queries,
            'generation_metadata': generation_metadata,
            'total_variants': len(flattened_queries)
        }
```

### Step 7: Complex Query Decomposition

Break complex questions into manageable sub-questions:

```python
def _decompose_complex_query(self, query: str, num_queries: int) -> List[str]:
    """Decompose complex queries into simpler sub-questions."""

    decomposition_prompt = f"""
    Break down this complex query into {num_queries} simpler, focused sub-questions:

    Complex Query: {query}

    Requirements:
    1. Each sub-question should be independently searchable
    2. Sub-questions should cover different aspects of the main query
    3. Avoid redundancy between sub-questions
    4. Maintain logical flow and completeness

    Sub-questions:
    """
```

**Decomposition Strategy**: Breaking complex questions into focused sub-questions enables more precise retrieval and comprehensive coverage of multifaceted information needs.

```python
    try:
        response = self.llm_model.predict(decomposition_prompt)
        sub_questions = [
            q.strip().rstrip('?') + '?'
            for q in response.strip().split('\n')
            if q.strip() and ('?' in q or len(q.split()) > 3)
        ]

        # Ensure proper question formatting
        sub_questions = [
            q if q.endswith('?') else q + '?'
            for q in sub_questions
        ]

        return sub_questions[:num_queries]

    except Exception as e:
        print(f"Decomposition error: {e}")
        return []
```

### Step 8: Specificity Level Variants

Generate queries at different levels of granularity:

```python
def _generate_specificity_variants(self, query: str, num_queries: int) -> List[str]:
    """Generate queries at different levels of specificity."""

    specificity_prompt = f"""
    Generate {num_queries} variants of this query at different specificity levels:

    Original Query: {query}

    Create variants that range from:
    1. Very broad/general versions
    2. Medium specificity versions
    3. Very specific/detailed versions

    Each variant should maintain the core intent but adjust the scope:
    """
```

**Specificity Adjustment**: Creating query variants at different granularity levels ensures retrieval of both overview information and detailed specifics.

```python
    try:
        response = self.llm_model.predict(specificity_prompt)
        variants = [
            variant.strip()
            for variant in response.strip().split('\n')
            if variant.strip() and len(variant.split()) > 2
        ]

        return variants[:num_queries]

    except Exception as e:
        print(f"Specificity variant error: {e}")
        return []
```

### Step 9: Enhanced Query Assembly

Create final expanded queries that combine all enhancement techniques:

```python
def _create_expanded_query(self, original_query: str,
                          expansions: List[str]) -> str:
    """Create final expanded query combining original and expansions."""

    # Remove duplicates and very similar terms
    filtered_expansions = self._filter_similar_terms(
        original_query, expansions
    )

    # Limit expansion count to prevent query bloat
    max_expansions = 8
    if len(filtered_expansions) > max_expansions:
        filtered_expansions = filtered_expansions[:max_expansions]

    # Create expanded query with OR logic
    if filtered_expansions:
        expansion_text = ' OR '.join(f'"{term}"' for term in filtered_expansions)
        expanded_query = f"{original_query} OR ({expansion_text})"
    else:
        expanded_query = original_query

    return expanded_query
```

**Query Assembly**: Intelligent combination of original query and expansions creates enhanced search queries while preventing query bloat.

### Step 10: Similarity Filtering

Remove redundant or overly similar expansion terms:

```python
def _filter_similar_terms(self, original_query: str,
                         expansions: List[str]) -> List[str]:
    """Filter out terms too similar to original query or each other."""

    original_words = set(original_query.lower().split())
    filtered_expansions = []

    for expansion in expansions:
        expansion_words = set(expansion.lower().split())

        # Skip if too much overlap with original
        overlap_ratio = len(expansion_words & original_words) / len(expansion_words)
        if overlap_ratio > 0.7:
            continue

        # Skip if too similar to already selected expansions
        is_too_similar = False
        for selected in filtered_expansions:
            selected_words = set(selected.lower().split())
            similarity = len(expansion_words & selected_words) / len(expansion_words | selected_words)
            if similarity > 0.6:
                is_too_similar = True
                break

        if not is_too_similar:
            filtered_expansions.append(expansion)

    return filtered_expansions
```

**Similarity Control**: Preventing redundant expansions ensures query enhancement adds value without creating noise.

## Testing Your Query Expansion System

Test the complete expansion system with various query types:

```python
# Initialize the expansion system
expander = IntelligentQueryExpander(llm_model, domain_corpus)
multi_gen = MultiQueryGenerator(llm_model)

# Test semantic expansion
semantic_result = expander.expand_query(
    "How to optimize database performance?",
    strategies=['semantic', 'contextual']
)

# Test multi-query generation
multi_result = multi_gen.generate_multi_query_set(
    "What are the best practices for microservices architecture?",
    perspectives=['decomposition', 'specificity_levels'],
    total_queries=6
)

print("Expansion Results:")
print(f"Original: {semantic_result['original_query']}")
print(f"Expanded: {semantic_result['expanded_query']}")
print(f"Expansion count: {semantic_result['expansion_count']}")

print("\nMulti-Query Results:")
print(f"Total variants: {multi_result['total_variants']}")
print("Query variants:", multi_result['query_variants'][:3])
```

## Integration with Search Systems

Connect your expansion system to vector search:

```python
def search_with_expansion(self, query: str, vector_store,
                         expansion_strategies: List[str] = ['semantic'],
                         top_k: int = 10):
    """Perform enhanced search using query expansion."""

    # Generate expanded query
    expansion_result = self.expander.expand_query(
        query, strategies=expansion_strategies
    )

    # Search with both original and expanded queries
    original_results = vector_store.similarity_search(query, k=top_k)
    expanded_results = vector_store.similarity_search(
        expansion_result['expanded_query'], k=top_k
    )

    # Generate multiple query variants
    multi_results = self.multi_gen.generate_multi_query_set(query)
    variant_results = []

    for variant in multi_results['query_variants'][:3]:
        variant_results.extend(
            vector_store.similarity_search(variant, k=top_k//3)
        )

    return {
        'original_results': original_results,
        'expanded_results': expanded_results,
        'variant_results': variant_results,
        'expansion_metadata': expansion_result,
        'multi_query_metadata': multi_results
    }
```

**Comprehensive Search**: Combining multiple expansion strategies with variant generation provides maximum retrieval coverage.

---

## Practice Exercises

1. **Custom Strategies**: Implement domain-specific expansion strategies  
2. **Performance Comparison**: Compare expansion results with baseline search  
3. **Query Complexity**: Test with increasingly complex multi-part questions  
4. **Expansion Quality**: Develop metrics to assess expansion effectiveness  

---

**Next:** [Session 5 - RAG Evaluation & Quality Assessment →](Session5_RAG_Evaluation_Quality_Assessment.md)

---
