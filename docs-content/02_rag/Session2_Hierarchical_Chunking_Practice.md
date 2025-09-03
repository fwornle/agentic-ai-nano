# 📝 Session 2: Hierarchical Chunking Practice

> **📝 PARTICIPANT PATH CONTENT**
> Prerequisites: Complete 🎯 Observer path concepts
> Time Investment: 2-3 hours
> Outcome: Build structure-aware chunking systems

## Learning Outcomes

After completing this implementation guide, you will:

- Build hierarchical chunkers that respect document structure  
- Implement intelligent overlap management for context preservation  
- Create section-aware grouping algorithms  
- Handle edge cases in document structure analysis  

---

## Advanced Hierarchical Chunker Implementation

The simple approach demonstrates the concept, but production systems need more sophisticated handling of edge cases, overlap management, and metadata preservation. Our advanced chunker addresses these requirements.

### Hierarchical Chunker - Core Initialization

Let's start with the chunker's initialization and main entry point:

```python
from langchain.schema import Document

class HierarchicalChunker:
    """Creates intelligent chunks based on document hierarchy."""

    def __init__(self, max_chunk_size: int = 1000, overlap_ratio: float = 0.1):
        self.max_chunk_size = max_chunk_size
        self.overlap_ratio = overlap_ratio
        self.analyzer = DocumentStructureAnalyzer()
```

The hierarchical chunker initializes with configurable parameters for chunk size and overlap. The overlap_ratio (typically 0.1 = 10%) ensures continuity between chunks by including some content from the previous chunk in the next one.

This prevents context loss at chunk boundaries, which is crucial for maintaining semantic coherence.

### Three-Step Chunking Process

```python
    def create_hierarchical_chunks(self, document: Document) -> List[Document]:
        """Create chunks that preserve document hierarchy."""
        # Step 1: Analyze document structure
        elements = self.analyzer.analyze_structure(document.page_content)

        # Step 2: Group elements into logical sections
        sections = self._group_elements_by_hierarchy(elements)

        # Step 3: Create chunks from sections
        chunks = []
        for section in sections:
            section_chunks = self._chunk_section(section, document.metadata)
            chunks.extend(section_chunks)

        return chunks
```

This main method orchestrates the three-step chunking process: analyze structure, group by hierarchy, and create chunks. Notice how we preserve the original document metadata throughout the process.

This ensures each chunk maintains its provenance and context information.

## Section Grouping Logic

The heart of hierarchical chunking is understanding document structure:

### Hierarchical Section Grouping

```python
    def _group_elements_by_hierarchy(self, elements: List[DocumentElement]) -> List[List[DocumentElement]]:
        """Group elements into hierarchical sections."""
        sections = []
        current_section = []
        current_level = -1

        for element in elements:
            # Start new section on same or higher level heading
            if (element.element_type == ContentType.HEADING and
                element.level <= current_level and current_section):

                sections.append(current_section)
                current_section = [element]
                current_level = element.level
```

This logic implements the core hierarchical principle: start a new section when you encounter a heading at the same level or higher (closer to root) than the current section.

This respects document hierarchy - a new "## Introduction" section should close any previous "### Details" subsection.

### Edge Case Handling

```python
            elif element.element_type == ContentType.HEADING and not current_section:
                # First heading initializes first section
                current_section = [element]
                current_level = element.level
            else:
                # Add element to current section
                current_section.append(element)

        # Add final section
        if current_section:
            sections.append(current_section)

        return sections
```

The grouping logic handles edge cases: the first heading initializes the first section, and we ensure the final section isn't lost. This creates logical document sections that can be processed independently while maintaining their internal structure.

## Intelligent Section Chunking

Once sections are identified, we chunk them with size management and overlap:

### Section Chunking with Size Management

```python
    def _chunk_section(self, section: List[DocumentElement],
                      base_metadata: Dict) -> List[Document]:
        """Create chunks from a document section with intelligent overlap."""
        chunks = []
        current_chunk_elements = []
        current_size = 0

        section_title = self._extract_section_title(section)

        for element in section:
            element_size = len(element.content)

            # Check if adding this element would exceed size limit
            if current_size + element_size > self.max_chunk_size and current_chunk_elements:
```

This method balances structure preservation with size constraints. We track both the elements and their cumulative size, making decisions based on content boundaries rather than arbitrary character counts.

The section title extraction provides context for each chunk.

### Intelligent Overlap Management

```python
                # Create chunk from current elements
                chunk = self._create_chunk_from_elements(
                    current_chunk_elements, base_metadata, section_title
                )
                chunks.append(chunk)

                # Start new chunk with overlap for continuity
                overlap_elements = self._get_overlap_elements(current_chunk_elements)
                current_chunk_elements = overlap_elements + [element]
                current_size = sum(len(e.content) for e in current_chunk_elements)
```

When a size limit is reached, we create a chunk and start the next one with intelligent overlap. The overlap elements typically include the last few sentences or the section heading, ensuring context continuity.

This prevents information loss at chunk boundaries.

### Element Accumulation Logic

```python
            else:
                current_chunk_elements.append(element)
                current_size += element_size

        # Create final chunk
        if current_chunk_elements:
            chunk = self._create_chunk_from_elements(
                current_chunk_elements, base_metadata, section_title
            )
            chunks.append(chunk)

        return chunks
```

The method handles the accumulation case (element fits in current chunk) and ensures the final chunk is created. This systematic approach ensures no content is lost while respecting both structural and size constraints.

## Rich Chunk Creation with Metadata

The final step creates chunks with comprehensive metadata for enhanced retrieval:

### Content Assembly with Formatting

```python
    def _create_chunk_from_elements(self, elements: List[DocumentElement],
                                  base_metadata: Dict, section_title: str) -> Document:
        """Create a document chunk with rich metadata."""
        # Combine element content with proper formatting
        content_parts = []
        for element in elements:
            if element.element_type == ContentType.HEADING:
                content_parts.append(f"\n{element.content}\n")
            else:
                content_parts.append(element.content)

        content = "\n".join(content_parts).strip()
```

Content assembly preserves formatting by treating headings specially - they get extra spacing to maintain their visual prominence. This formatting preservation helps both human readers and embedding models understand the content structure.

### Enhanced Metadata Creation

```python
        # Build enhanced metadata
        content_types = [e.element_type.value for e in elements]
        hierarchy_levels = [e.level for e in elements]

        enhanced_metadata = {
            **base_metadata,
            "section_title": section_title,
            "chunk_type": "hierarchical",
            "content_types": list(set(content_types)),
            "hierarchy_levels": hierarchy_levels,
            "element_count": len(elements),
            "has_heading": ContentType.HEADING.value in content_types,
            "has_table": ContentType.TABLE.value in content_types,
            "has_code": ContentType.CODE.value in content_types,
            "min_hierarchy_level": min(hierarchy_levels),
            "max_hierarchy_level": max(hierarchy_levels)
        }

        return Document(page_content=content, metadata=enhanced_metadata)
```

The metadata enhancement provides multiple search dimensions: content types enable filtering ("find chunks with code"), hierarchy levels support structure-aware retrieval, and boolean flags enable quick filtering.

This rich metadata transforms simple text chunks into searchable, contextual knowledge units.

## Supporting Helper Methods

### Section Title Extraction

```python
    def _extract_section_title(self, section: List[DocumentElement]) -> str:
        """Extract title from section elements."""
        for element in section:
            if element.element_type == ContentType.HEADING:
                return element.content.strip('#').strip()
        return "Untitled Section"
```

Section title extraction identifies the main heading within a section to provide context.

### Overlap Element Selection

```python
    def _get_overlap_elements(self, elements: List[DocumentElement]) -> List[DocumentElement]:
        """Get elements for chunk overlap."""
        if not elements:
            return []

        # Calculate overlap size
        total_size = sum(len(e.content) for e in elements)
        overlap_size = int(total_size * self.overlap_ratio)

        # Select last elements that fit in overlap
        overlap_elements = []
        current_size = 0

        for element in reversed(elements):
            element_size = len(element.content)
            if current_size + element_size <= overlap_size:
                overlap_elements.insert(0, element)
                current_size += element_size
            else:
                break

        return overlap_elements
```

Overlap element selection ensures the next chunk begins with some context from the previous chunk, maintaining semantic continuity while respecting the configured overlap ratio.

---

## 📝 Practice Exercises

### Exercise 1: Basic Hierarchical Chunker

Implement a simplified hierarchical chunker and test it on a structured document:

```python
# Test with sample document
sample_doc = """
# Machine Learning Guide

Machine learning is a subset of artificial intelligence.

## Supervised Learning

Supervised learning uses labeled training data to make predictions.

### Classification

Classification algorithms predict discrete categories.

#### Decision Trees

Decision trees split data based on feature values.

#### Random Forest

Random forest combines multiple decision trees.

### Regression

Regression algorithms predict continuous values.

## Unsupervised Learning

Unsupervised learning finds patterns without labels.
"""

# Test your implementation
chunker = HierarchicalChunker(max_chunk_size=300)
chunks = chunker.create_hierarchical_chunks(Document(page_content=sample_doc))

print(f"Created {len(chunks)} chunks:")
for i, chunk in enumerate(chunks):
    print(f"\nChunk {i+1}:")
    print(f"Size: {len(chunk.page_content)} characters")
    print(f"Content types: {chunk.metadata.get('content_types', [])}")
    print(f"Section title: {chunk.metadata.get('section_title', 'N/A')}")
    print(f"Preview: {chunk.page_content[:100]}...")
```

### Exercise 2: Overlap Testing

Create chunks with different overlap ratios and analyze the continuity:

```python
# Test different overlap ratios
overlap_ratios = [0.0, 0.1, 0.2, 0.3]

for ratio in overlap_ratios:
    chunker = HierarchicalChunker(max_chunk_size=200, overlap_ratio=ratio)
    chunks = chunker.create_hierarchical_chunks(Document(page_content=sample_doc))

    print(f"\nOverlap ratio: {ratio}")
    print(f"Number of chunks: {len(chunks)}")

    # Analyze overlap between adjacent chunks
    for i in range(len(chunks) - 1):
        chunk1_words = set(chunks[i].page_content.split())
        chunk2_words = set(chunks[i + 1].page_content.split())
        overlap = len(chunk1_words & chunk2_words)
        total = len(chunk1_words | chunk2_words)
        overlap_percentage = (overlap / total) * 100 if total > 0 else 0
        print(f"  Chunks {i+1}-{i+2} overlap: {overlap_percentage:.1f}%")
```

### Exercise 3: Section Boundary Analysis

Test how the chunker handles different heading hierarchies:

```python
# Document with complex hierarchy
complex_doc = """
# Chapter 1: Introduction

This is the introduction to our topic.

## Section 1.1: Background

Background information here.

### Subsection 1.1.1: History

Historical context.

### Subsection 1.1.2: Evolution

How things evolved.

## Section 1.2: Current State

Current situation analysis.

# Chapter 2: Methods

New chapter begins here.

## Section 2.1: Methodology

Our approach to the problem.
"""

# Analyze section boundaries
chunker = HierarchicalChunker(max_chunk_size=400)
elements = chunker.analyzer.analyze_structure(complex_doc)

print("Document structure analysis:")
for element in elements:
    if element.element_type == ContentType.HEADING:
        indent = "  " * element.level
        print(f"{indent}Level {element.level}: {element.content}")
```

---

## Troubleshooting Common Issues

### Issue 1: Chunks Too Small

**Problem**: Chunks contain only single elements or very little content.
**Solution**: Adjust `max_chunk_size` or modify section grouping logic:

```python
# Add minimum chunk size constraint
def _chunk_section(self, section, base_metadata, min_chunk_size=150):
    # ... existing code ...

    # Only create chunk if minimum size is met
    if current_size >= min_chunk_size or not chunks:
        chunk = self._create_chunk_from_elements(...)
        chunks.append(chunk)
```

### Issue 2: Overlap Too Large

**Problem**: Overlap creates excessive duplication between chunks.
**Solution**: Implement smart overlap that prioritizes important content:

```python
def _get_smart_overlap_elements(self, elements):
    """Get overlap elements prioritizing headings and key content."""
    overlap_elements = []

    # Always include section heading if present
    for element in elements:
        if element.element_type == ContentType.HEADING:
            overlap_elements.append(element)
            break

    # Add last few sentences up to overlap limit
    # ... implementation details ...

    return overlap_elements
```

### Issue 3: Metadata Inconsistency

**Problem**: Chunk metadata varies inconsistently across similar content.
**Solution**: Standardize metadata extraction with validation:

```python
def _validate_chunk_metadata(self, metadata):
    """Ensure metadata consistency."""
    required_fields = ["section_title", "content_types", "chunk_type"]

    for field in required_fields:
        if field not in metadata:
            metadata[field] = self._get_default_value(field)

    return metadata
```

---

## Advanced Optimization Techniques

### Dynamic Chunk Sizing

Adapt chunk size based on content complexity:

```python
def _calculate_adaptive_chunk_size(self, section):
    """Calculate optimal chunk size for section."""
    base_size = self.max_chunk_size

    # Increase size for code-heavy sections
    code_elements = sum(1 for e in section if e.element_type == ContentType.CODE)
    if code_elements > 2:
        return base_size * 1.3

    # Decrease size for list-heavy sections
    list_elements = sum(1 for e in section if e.element_type == ContentType.LIST)
    if list_elements > 5:
        return base_size * 0.8

    return base_size
```

### Quality-Based Chunk Validation

Validate chunk quality during creation:

```python
def _validate_chunk_quality(self, chunk):
    """Validate chunk meets quality standards."""
    content = chunk.page_content
    words = content.split()

    # Check minimum information content
    if len(words) < 20:
        return False, "Chunk too short"

    # Check for incomplete sentences
    if not content.strip().endswith(('.', '!', '?', ':')):
        return False, "Chunk ends mid-sentence"

    # Check for balanced content types
    metadata = chunk.metadata
    if len(metadata.get('content_types', [])) == 0:
        return False, "No content type detected"

    return True, "Quality check passed"
```

---

## Key Implementation Tips

### Best Practices

1. **Size Management**: Balance structure preservation with practical limits  
2. **Overlap Strategy**: Use 10-15% overlap for optimal context preservation  
3. **Metadata Richness**: Include comprehensive metadata for retrieval enhancement  
4. **Edge Case Handling**: Test with various document structures and formats  

### Performance Optimization

1. **Lazy Loading**: Process elements on-demand for large documents  
2. **Caching**: Cache structure analysis results for repeated processing  
3. **Parallel Processing**: Process independent sections concurrently  
4. **Memory Management**: Clear intermediate data structures regularly  

### Testing Strategy

1. **Unit Tests**: Test individual methods with controlled inputs  
2. **Integration Tests**: Test full pipeline with realistic documents  
3. **Edge Case Tests**: Handle malformed documents and unusual structures  
4. **Performance Tests**: Measure processing time and memory usage  
---

**Next:** [Session 3 - Vector Databases & Search Optimization →](Session3_Vector_Databases_Search_Optimization.md)

---
