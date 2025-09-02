# 📝 Session 2: Metadata Extraction Implementation

> **📝 PARTICIPANT PATH CONTENT**
> Prerequisites: Complete 🎯 Observer path and 📝 Hierarchical Chunking Practice
> Time Investment: 2-3 hours
> Outcome: Build rich metadata extraction systems

## Learning Outcomes

After completing this implementation guide, you will:

- Extract entities, keywords, and topics from document content
- Build domain-specific pattern recognition systems
- Implement difficulty assessment algorithms
- Create metadata-enhanced chunking pipelines

---

## Advanced Metadata Extractor Implementation

Raw text chunks, no matter how well structured, often lack the context needed for precise retrieval. A chunk about "memory optimization" might be talking about software memory management or human cognitive memory. Metadata extraction solves this by extracting entities, topics, technical terms, and other contextual information that makes content discoverable and meaningful.

### Data Structure & Initialization

First, let's define the data structure for our extracted metadata:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ExtractedMetadata:
    """Container for extracted metadata."""
    entities: List[str]
    keywords: List[str]
    topics: List[str]
    dates: List[str]
    numbers: List[float]
    technical_terms: List[str]
    difficulty_level: str
    content_summary: str
```

The ExtractedMetadata dataclass provides a structured container for all the different types of metadata we'll extract. This structured approach makes the metadata easy to work with and ensures consistent data types across the system.

### Pattern Definitions and Domain Knowledge

Now let's initialize the extractor with domain-specific patterns and knowledge:

```python
class MetadataExtractor:
    """Extracts rich metadata from document content."""

    def __init__(self):
        self.technical_patterns = [
            r'\b[A-Z]{2,}\b',                    # Acronyms
            r'\b\w+\(\)\b',                      # Function calls
            r'\b[a-zA-Z_]\w*\.[a-zA-Z_]\w*\b',   # Object notation
            r'\b\d+\.\d+\.\d+\b',                # Version numbers
        ]

        self.topic_keywords = {
            "technology": ["software", "computer", "digital", "algorithm", "data", "system"],
            "business": ["market", "customer", "revenue", "strategy", "company", "industry"],
            "legal": ["contract", "agreement", "clause", "statute", "regulation", "compliance"],
            "medical": ["patient", "treatment", "diagnosis", "medication", "therapy", "clinical"]
        }
```

The patterns and keywords define domain expertise that enables intelligent content analysis. Technical patterns capture programming constructs and technical terminology, while topic keywords enable automatic domain classification.

This knowledge base can be expanded for specific domains or applications.

## Main Extraction Orchestration

The main extraction method coordinates all the different extraction techniques:

### Comprehensive Metadata Extraction

```python
    def extract_enhanced_metadata(self, text: str) -> ExtractedMetadata:
        """Extract comprehensive metadata from text."""

        # Extract different types of information
        entities = self._extract_entities(text)
        keywords = self._extract_keywords(text)
        topics = self._infer_topics(text)
        dates = self._extract_dates(text)
        numbers = self._extract_numbers(text)
        technical_terms = self._extract_technical_terms(text)
        difficulty_level = self._assess_difficulty(text)
        content_summary = self._generate_summary(text)

        return ExtractedMetadata(
            entities=entities,
            keywords=keywords,
            topics=topics,
            dates=dates,
            numbers=numbers,
            technical_terms=technical_terms,
            difficulty_level=difficulty_level,
            content_summary=content_summary
        )
```

This orchestration method calls specialized extractors for each metadata type. The modular approach allows for easy testing and improvement of individual extraction techniques while maintaining a consistent interface.

## Entity Extraction with Pattern Matching

Entity extraction identifies names, terms, and concepts that are likely to be important:

### Multi-Heuristic Entity Detection

```python
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities using pattern matching."""
        entities = []

        # Extract capitalized words (potential proper nouns)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.extend(capitalized_words)

        # Extract quoted terms
        quoted_terms = re.findall(r'"([^"]*)"', text)
        entities.extend(quoted_terms)

        # Remove duplicates and filter by length
        entities = list(set([e for e in entities if 2 < len(e) < 50]))

        return entities[:10]  # Limit to top 10
```

Entity extraction combines multiple heuristics: capitalized words often represent proper nouns (names, places, technologies), while quoted terms typically indicate important concepts or technical terms.

The filtering removes noise (very short or very long matches) and limits results to prevent overwhelming the metadata.

### Advanced Pattern Recognition

```python
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terminology using patterns."""
        technical_terms = []

        for pattern in self.technical_patterns:
            matches = re.findall(pattern, text)
            technical_terms.extend(matches)

        # Remove duplicates and filter
        technical_terms = list(set([term for term in technical_terms if len(term) > 1]))

        return technical_terms[:8]  # Limit to top 8
```

Technical term extraction uses specialized patterns to identify programming constructs, acronyms, function calls, and version numbers that might not be caught by general entity extraction.

## Topic Inference Through Keyword Analysis

### Frequency-Based Topic Classification

```python
    def _infer_topics(self, text: str) -> List[str]:
        """Infer topics from content using keyword analysis."""
        text_lower = text.lower()
        topic_scores = {}

        for topic, keywords in self.topic_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                topic_scores[topic] = score

        # Return topics sorted by relevance
        return sorted(topic_scores.keys(), key=lambda x: topic_scores[x], reverse=True)[:3]
```

Topic inference uses keyword frequency to classify content. Each domain gets a relevance score based on how many domain-specific keywords appear in the text.

This enables automatic tagging that helps with retrieval filtering ("show me all technology-related chunks") and content organization.

### Enhanced Keyword Extraction

```python
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        words = text.lower().split()

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]

        # Count word frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Return most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10] if freq > 1]
```

Keyword extraction identifies the most frequent meaningful words in the content, filtering out common stop words and emphasizing terms that appear multiple times.

## Difficulty Assessment Through Multiple Metrics

### Multi-Factor Difficulty Analysis

```python
    def _assess_difficulty(self, text: str) -> str:
        """Assess content difficulty level."""
        words = text.split()
        sentences = text.split('.')

        if not words or not sentences:
            return "unknown"

        # Calculate readability metrics
        avg_words_per_sentence = len(words) / len(sentences)
        long_words = len([w for w in words if len(w) > 6])
        long_word_ratio = long_words / len(words) if words else 0

        # Technical term density
        technical_terms = len(self._extract_technical_terms(text))
        technical_density = technical_terms / len(words) if words else 0
```

The difficulty assessment begins by calculating multiple readability indicators that contribute to content complexity.

### Difficulty Level Determination

```python
        # Determine difficulty
        if avg_words_per_sentence > 20 or long_word_ratio > 0.3 or technical_density > 0.1:
            return "advanced"
        elif avg_words_per_sentence > 15 or long_word_ratio > 0.2:
            return "intermediate"
        else:
            return "beginner"
```

Difficulty assessment combines multiple readability indicators: sentence length (complex ideas often need longer sentences), vocabulary complexity (longer words typically indicate more advanced concepts), and technical density (specialized terminology suggests expert content).

This classification helps users find content appropriate to their level and enables difficulty-based filtering.

## Supporting Extraction Methods

### Date and Number Extraction

```python
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # YYYY/MM/DD
            r'\b[A-Za-z]+ \d{1,2}, \d{4}\b'      # Month DD, YYYY
        ]

        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)

        return list(set(dates))[:5]  # Limit to 5 unique dates

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values from text."""
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, text)

        try:
            numeric_values = [float(n) for n in numbers]
            return numeric_values[:10]  # Limit to first 10
        except ValueError:
            return []
```

Date and number extraction identify structured data within text that can be valuable for filtering and analysis.

### Content Summary Generation

```python
    def _generate_summary(self, text: str) -> str:
        """Generate a brief content summary."""
        sentences = text.split('.')

        if not sentences:
            return "No content available"

        # Take first sentence as summary, truncate if too long
        first_sentence = sentences[0].strip()

        if len(first_sentence) > 150:
            words = first_sentence.split()
            truncated = ' '.join(words[:20])
            return f"{truncated}..." if len(words) > 20 else first_sentence

        return first_sentence
```

Summary generation creates a brief description of the content, typically using the first sentence or a truncated version for long content.

---

## Metadata-Enhanced Chunking Integration

The real power emerges when you combine hierarchical chunking with metadata extraction. This creates chunks that are both structurally coherent and contextually rich – the foundation of high-precision retrieval.

### MetadataEnhancedChunker - Initialization and Core Processing

```python
class MetadataEnhancedChunker:
    """Chunker that enriches chunks with extracted metadata."""

    def __init__(self, max_chunk_size: int = 1000):
        self.hierarchical_chunker = HierarchicalChunker(max_chunk_size=max_chunk_size)
        self.metadata_extractor = MetadataExtractor()
```

The MetadataEnhancedChunker combines hierarchical chunking with metadata extraction, creating a two-stage process that first respects document structure, then enriches each chunk with contextual information.

### Two-Stage Enhancement Process

```python
    def create_enhanced_chunks(self, document: Document) -> List[Document]:
        """Create chunks with rich metadata."""
        # First, create hierarchical chunks
        chunks = self.hierarchical_chunker.create_hierarchical_chunks(document)

        # Enhance each chunk with extracted metadata
        enhanced_chunks = []
        for chunk in chunks:
            enhanced_chunk = self._enhance_chunk_metadata(chunk)
            enhanced_chunks.append(enhanced_chunk)

        return enhanced_chunks
```

This two-stage approach ensures optimal chunking boundaries (via hierarchical chunking) before adding metadata enrichment. The separation of concerns makes the system modular - you can swap chunking strategies or metadata extraction techniques independently.

### Metadata Integration and Enhancement

```python
    def _enhance_chunk_metadata(self, chunk: Document) -> Document:
        """Enhance chunk with extracted metadata."""
        # Extract metadata from chunk content
        extracted_metadata = self.metadata_extractor.extract_enhanced_metadata(chunk.page_content)

        # Merge extracted metadata with existing metadata
        enhanced_metadata = {
            **chunk.metadata,
            "entities": extracted_metadata.entities,
            "keywords": extracted_metadata.keywords,
            "topics": extracted_metadata.topics,
            "technical_terms": extracted_metadata.technical_terms,
            "difficulty_level": extracted_metadata.difficulty_level,
            "content_summary": extracted_metadata.content_summary,
            "enhanced_at": datetime.now().isoformat()
        }
```

Metadata merging preserves existing chunk metadata (section titles, hierarchy levels) while adding extracted information. The timestamp tracks when enhancement occurred, enabling cache invalidation and processing pipeline monitoring.

### Searchable Content Creation

```python
        # Create searchable content that includes metadata
        searchable_content = self._create_searchable_content(chunk.page_content, extracted_metadata)

        return Document(page_content=searchable_content, metadata=enhanced_metadata)

    def _create_searchable_content(self, original_content: str, metadata: ExtractedMetadata) -> str:
        """Create enhanced searchable content."""
        metadata_text_parts = []

        if metadata.keywords:
            metadata_text_parts.append(f"Keywords: {', '.join(metadata.keywords)}")

        if metadata.topics:
            metadata_text_parts.append(f"Topics: {', '.join(metadata.topics)}")

        if metadata.entities:
            metadata_text_parts.append(f"Entities: {', '.join(metadata.entities[:5])}")

        metadata_text = "\n".join(metadata_text_parts)

        # Combine original content with metadata
        if metadata_text:
            return f"{original_content}\n\n--- Metadata ---\n{metadata_text}"
        else:
            return original_content
```

The searchable content enhancement embeds metadata directly into the chunk text, making it discoverable during vector similarity search. This approach enables queries like "find database optimization" to match chunks containing those keywords even if they weren't in the original text but were inferred from context.

---

## 📝 Practice Exercises

### Exercise 1: Basic Metadata Extraction

Implement and test basic metadata extraction on sample content:

```python
# Test content with various elements
test_content = """
Machine Learning Optimization Guide

This comprehensive guide covers advanced optimization techniques for machine learning algorithms.
Published on January 15, 2024, this document includes performance benchmarks and API references.

Key concepts include gradient descent, learning rates (typically 0.001 to 0.1), and regularization.
The TensorFlow 2.8.0 library provides optimizers like Adam() and SGD().

For enterprise deployment, consider Docker containers and Kubernetes orchestration.
Contact sales@mlcompany.com for licensing information.
"""

# Extract metadata
extractor = MetadataExtractor()
metadata = extractor.extract_enhanced_metadata(test_content)

print(f"Entities: {metadata.entities}")
print(f"Technical terms: {metadata.technical_terms}")
print(f"Topics: {metadata.topics}")
print(f"Difficulty: {metadata.difficulty_level}")
print(f"Dates: {metadata.dates}")
print(f"Numbers: {metadata.numbers}")
```

### Exercise 2: Domain-Specific Pattern Testing

Create custom patterns for your specific domain:

```python
# Extend MetadataExtractor for legal domain
class LegalMetadataExtractor(MetadataExtractor):
    def __init__(self):
        super().__init__()
        self.legal_patterns = [
            r'§\s*\d+[\w\d]*',           # Section references
            r'Article\s+[IVX]+',         # Article references
            r'\d+\s+U\.S\.C\.\s+§\s+\d+', # USC citations
            r'Case\s+No\.\s+[\d-]+',     # Case numbers
        ]

    def _extract_legal_references(self, text: str) -> List[str]:
        """Extract legal-specific references."""
        references = []
        for pattern in self.legal_patterns:
            matches = re.findall(pattern, text)
            references.extend(matches)
        return list(set(references))

# Test with legal document
legal_text = """
Pursuant to Section 1983 and Article IV of the Constitution,
the defendant violated 42 U.S.C. § 1983 in Case No. 2023-CV-1234.
"""

legal_extractor = LegalMetadataExtractor()
legal_refs = legal_extractor._extract_legal_references(legal_text)
print(f"Legal references: {legal_refs}")
```

### Exercise 3: Quality Assessment Integration

Build metadata quality validation:

```python
def assess_metadata_quality(metadata: ExtractedMetadata) -> Dict[str, float]:
    """Assess quality of extracted metadata."""
    quality_scores = {}

    # Entity richness (0-1 scale)
    entity_score = min(len(metadata.entities) / 5, 1.0)
    quality_scores['entity_richness'] = entity_score

    # Topic coverage (0-1 scale)
    topic_score = min(len(metadata.topics) / 3, 1.0)
    quality_scores['topic_coverage'] = topic_score

    # Technical depth (0-1 scale)
    tech_score = min(len(metadata.technical_terms) / 5, 1.0)
    quality_scores['technical_depth'] = tech_score

    # Overall completeness
    completeness = (entity_score + topic_score + tech_score) / 3
    quality_scores['overall_completeness'] = completeness

    return quality_scores

# Test quality assessment
sample_metadata = extractor.extract_enhanced_metadata(test_content)
quality = assess_metadata_quality(sample_metadata)

print("Metadata Quality Assessment:")
for metric, score in quality.items():
    print(f"  {metric}: {score:.2f}")
```

---

## Advanced Optimization Techniques

### Cached Pattern Compilation

Optimize performance by pre-compiling regex patterns:

```python
import re

class OptimizedMetadataExtractor(MetadataExtractor):
    def __init__(self):
        super().__init__()
        # Pre-compile patterns for better performance
        self.compiled_patterns = {
            'technical': [re.compile(pattern) for pattern in self.technical_patterns],
            'entities': re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'),
            'dates': re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'),
            'numbers': re.compile(r'\b\d+(?:\.\d+)?\b')
        }

    def _extract_entities_optimized(self, text: str) -> List[str]:
        """Optimized entity extraction with compiled patterns."""
        matches = self.compiled_patterns['entities'].findall(text)
        return list(set([e for e in matches if 2 < len(e) < 50]))[:10]
```

### Batch Processing

Process multiple chunks efficiently:

```python
def extract_metadata_batch(self, texts: List[str]) -> List[ExtractedMetadata]:
    """Extract metadata from multiple texts efficiently."""
    results = []

    # Pre-process all texts
    processed_texts = [(text, text.lower(), text.split()) for text in texts]

    for original_text, lower_text, words in processed_texts:
        # Use pre-processed data to avoid redundant operations
        metadata = self._extract_from_processed(original_text, lower_text, words)
        results.append(metadata)

    return results
```

### Configurable Domain Adaptation

Make domain patterns configurable:

```python
class ConfigurableMetadataExtractor(MetadataExtractor):
    def __init__(self, domain_config: Dict[str, Any] = None):
        super().__init__()
        if domain_config:
            self.topic_keywords.update(domain_config.get('topic_keywords', {}))
            self.technical_patterns.extend(domain_config.get('technical_patterns', []))
            self.custom_extractors = domain_config.get('custom_extractors', {})

    def add_custom_extractor(self, name: str, extractor_func):
        """Add custom extraction function."""
        self.custom_extractors[name] = extractor_func

    def extract_with_custom(self, text: str) -> Dict[str, Any]:
        """Extract metadata including custom extractors."""
        base_metadata = self.extract_enhanced_metadata(text)

        custom_results = {}
        for name, extractor in self.custom_extractors.items():
            custom_results[name] = extractor(text)

        return {
            'base_metadata': base_metadata,
            'custom_metadata': custom_results
        }
```

---

## Troubleshooting Common Issues

### Issue 1: Poor Entity Detection

**Problem**: Missing important entities or extracting irrelevant terms.
**Solution**: Refine patterns and add domain-specific rules:

```python
def _extract_entities_refined(self, text: str) -> List[str]:
    """Enhanced entity extraction with filtering."""
    entities = []

    # Standard capitalized words
    capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)

    # Filter out common false positives
    false_positives = {'The', 'This', 'That', 'These', 'Those', 'First', 'Second', 'Last'}
    filtered = [e for e in capitalized if e not in false_positives]

    entities.extend(filtered)

    # Add domain-specific entity patterns
    # Example: Product names, company names, etc.

    return list(set(entities))[:10]
```

### Issue 2: Inaccurate Topic Classification

**Problem**: Content classified under wrong topics or missing topics.
**Solution**: Improve keyword sets and add contextual analysis:

```python
def _infer_topics_enhanced(self, text: str) -> List[str]:
    """Enhanced topic inference with context."""
    text_lower = text.lower()
    topic_scores = {}

    # Standard keyword matching
    for topic, keywords in self.topic_keywords.items():
        score = sum(text_lower.count(keyword) for keyword in keywords)

        # Add context weighting
        for keyword in keywords:
            # Higher score if keyword appears in important positions
            if keyword in text_lower[:100]:  # Beginning of text
                score += 0.5
            if keyword in text.lower().split('\n')[0]:  # First line
                score += 0.3

        if score > 0:
            topic_scores[topic] = score

    return sorted(topic_scores.keys(), key=lambda x: topic_scores[x], reverse=True)[:3]
```

### Issue 3: Inconsistent Difficulty Assessment

**Problem**: Similar content receives different difficulty ratings.
**Solution**: Standardize metrics and add validation:

```python
def _assess_difficulty_standardized(self, text: str) -> str:
    """Standardized difficulty assessment."""
    if len(text.strip()) < 50:
        return "unknown"

    words = text.split()
    sentences = [s.strip() for s in text.split('.') if s.strip()]

    # Normalize metrics
    avg_sentence_length = len(words) / max(len(sentences), 1)
    long_word_ratio = len([w for w in words if len(w) > 6]) / max(len(words), 1)

    # Technical complexity
    tech_indicators = len(re.findall(r'\b[A-Z]{2,}\b|\b\w+\(\)|\b\d+\.\d+\.\d+\b', text))
    tech_ratio = tech_indicators / max(len(words), 1)

    # Calculate composite score (0-10 scale)
    complexity_score = (
        (avg_sentence_length / 25) * 3 +      # Sentence complexity (0-3)
        (long_word_ratio * 10) * 4 +          # Vocabulary complexity (0-4)
        (tech_ratio * 100) * 3                # Technical complexity (0-3)
    )

    if complexity_score >= 6:
        return "advanced"
    elif complexity_score >= 3:
        return "intermediate"
    else:
        return "beginner"
```

---

## Key Implementation Tips

### Best Practices

1. **Pattern Testing**: Validate patterns against representative content samples
2. **Domain Adaptation**: Customize extractors for specific content domains
3. **Quality Validation**: Implement quality checks for extracted metadata
4. **Performance Monitoring**: Track extraction accuracy and processing time

### Performance Optimization

1. **Pattern Compilation**: Pre-compile regex patterns for repeated use
2. **Batch Processing**: Process multiple documents together efficiently
3. **Caching**: Cache extraction results for repeated content
4. **Lazy Loading**: Extract metadata on-demand rather than upfront

### Quality Assurance

1. **Validation Rules**: Implement checks for extracted metadata quality
2. **Human Review**: Sample and review extraction results regularly
3. **Feedback Integration**: Use retrieval performance to improve extraction
4. **Domain Testing**: Test across different content types and domains
---

## 🧭 Navigation

**Previous:** [Session 1 - Basic RAG Implementation ←](Session1_Basic_RAG_Implementation.md)
**Next:** [Session 3 - Vector Databases & Search Optimization →](Session3_Vector_Databases_Search_Optimization.md)
---
