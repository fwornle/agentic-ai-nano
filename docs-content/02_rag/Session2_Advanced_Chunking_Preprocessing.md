# Session 2: Advanced Chunking & Preprocessing

In Session 1, you implemented a working RAG system that splits documents into manageable chunks. But that's where many RAG implementations stop – and where they start to fail in production. When your chunker encounters a table and splits it down the middle, or breaks apart a code block that loses meaning without its function definition, you've hit the fundamental limitation of naive text splitting.

This session transforms your RAG system from simple text splitters into intelligent document understanding engines. You'll implement structure-aware chunking that preserves document hierarchy, extract rich metadata that enhances retrieval precision, and handle complex content types including tables, code blocks, and domain-specific formatting. The goal is to ensure that every chunk carries not just content, but context.

![RAG Problems Overview](images/RAG-overview-problems.png)
*Figure 1: Common problems with naive chunking approaches that advanced preprocessing solves.*

---

## Part 1: Document Structure Analysis - Understanding Content Before Chunking

### Content Type Detection

The first step in advanced chunking is understanding what you're working with. Different content types have different semantic boundaries and preservation requirements. A heading-paragraph relationship needs different treatment than a table with structured data, and code blocks require completely different handling than prose text.

Let's start with content type detection that goes beyond simple pattern matching:

```python

# Simple content type detection

from enum import Enum

class ContentType(Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph" 
    TABLE = "table"
    CODE = "code"
    LIST = "list"

def detect_simple_content_type(text_line):
    """Detect content type from a single line of text."""
    text = text_line.strip()
    
    # Check for markdown heading
    if text.startswith('#'):
        return ContentType.HEADING
    
    # Check for table (pipe-separated)
    if '|' in text and text.count('|') >= 2:
        return ContentType.TABLE
        
    # Check for code (starts with 4 spaces or tab)
    if text.startswith('    ') or text.startswith('\t'):
        return ContentType.CODE
        
    # Check for list item
    if text.startswith('- ') or text.startswith('* '):
        return ContentType.LIST
        
    return ContentType.PARAGRAPH
```

**Code Explanation:**

- **Lines 12-14**: Detects markdown headings by looking for the '#' symbol
- **Lines 16-18**: Identifies tables by counting pipe characters ('|') that separate columns
- **Lines 20-22**: Recognizes code blocks by indentation patterns
- **Lines 24-26**: Spots list items by bullet point markers

This classification enables our system to make intelligent decisions about how to process each type of content.

### Building Document Elements

Now that we can classify content types, we need to represent document structure in a way that preserves relationships between elements. This structured approach will enable our chunker to make intelligent decisions about where to split and how to maintain context:

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DocumentElement:
    """Represents a structured document element with metadata."""
    content: str
    element_type: ContentType
    level: int  # Hierarchy level (0=top, 1=section, 2=subsection)
    metadata: Dict[str, Any]
    position: int  # Position in document
    
    def get_hierarchy_context(self):
        """Get human-readable hierarchy information."""
        hierarchy_labels = {
            0: "Document Root",
            1: "Major Section", 
            2: "Subsection",
            3: "Minor Section"
        }
        return hierarchy_labels.get(self.level, f"Level {self.level}")
```

**Implementation Benefits:**

- **Structured representation**: Each element carries its content, type, and context
- **Hierarchy tracking**: Level information enables structure-aware processing
- **Rich metadata**: Position and additional context for enhanced chunking
- **Processing intelligence**: Different element types can receive specialized handling

With our document element structure defined, we can now implement the analyzer that transforms raw text into structured document understanding. This analyzer will be the foundation for all subsequent intelligent processing:

```python
class DocumentStructureAnalyzer:
    """Analyzes document structure and content types."""

    def __init__(self):
        self.heading_patterns = [
            r'^#{1,6}\s+(.+)$',      # Markdown headers
            r'^([A-Z][^a-z]*)\s*$',  # ALL CAPS headers
            r'^\d+\.\s+(.+)$',       # Numbered headers
        ]

    def analyze_structure(self, document_text: str) -> List[DocumentElement]:
        """Analyze document structure and create structured elements."""
        lines = document_text.split('\n')
        elements = []
        current_level = 0
        position = 0

        for i, line in enumerate(lines):
            if not line.strip():
                continue

            content_type = detect_simple_content_type(line)
            level = self._determine_level(line, current_level, content_type)
            
            element = DocumentElement(
                content=line.strip(),
                element_type=content_type,
                level=level,
                metadata={
                    "line_number": i + 1,
                    "char_count": len(line),
                    "word_count": len(line.split())
                },
                position=position
            )
            
            elements.append(element)
            position += 1
            current_level = level

        return elements
```

This analyzer creates a structured representation of the document that preserves hierarchy and content relationships. Notice how we're not just splitting text – we're understanding it.

### Advanced Pattern Recognition

For enterprise applications, you often encounter domain-specific documents with specialized formatting conventions. Legal documents have section markers and citations, medical documents have dosages and medications, and technical documents have API references and version numbers. Generic pattern matching isn't sufficient:

```python
import re
from typing import List, Tuple

class AdvancedDocumentAnalyzer:
    """Enterprise-grade document analysis with domain-specific patterns."""
    
    def __init__(self):
        self.domain_patterns = {
            "legal": {
                "section_markers": [r"§\s*\d+", r"Article\s+[IVX]+", r"Section\s+\d+"],
                "citations": [r"\d+\s+U\.S\.C\.\s+§\s+\d+", r"\d+\s+F\.\d+d\s+\d+"]
            },
            "medical": {
                "dosages": [r"\d+\s*mg", r"\d+\s*ml", r"\d+\s*cc"],
                "medications": [r"[A-Z][a-z]+(?:in|ol|ide|ine)"]
            },
            "technical": {
                "apis": [r"[A-Z][a-zA-Z]+\.[a-zA-Z]+\(\)", r"HTTP[S]?\://"],
                "versions": [r"v?\d+\.\d+\.\d+", r"version\s+\d+"]
            }
        }
    
    def analyze_with_domain_knowledge(self, document_text: str, 
                                    domain: str = "general") -> Dict[str, Any]:
        """Analyze document with domain-specific intelligence."""
        analysis = {
            "domain": domain,
            "structure": self._analyze_structure(document_text),
            "complexity_score": self._calculate_complexity_score(document_text),
            "processing_strategy": "standard"
        }
        
        if domain in self.domain_patterns:
            domain_features = self._extract_domain_features(document_text, domain)
            analysis["domain_features"] = domain_features
            analysis["processing_strategy"] = self._recommend_strategy(domain_features)
            
        return analysis
```

This advanced analyzer adapts to different document domains and provides intelligent processing recommendations. The domain-specific patterns enable the system to recognize specialized content and adjust processing accordingly.

---

## Part 2: Hierarchical Chunking Implementation - Respecting Document Structure

The fundamental problem with naive chunking is that it treats all text equally. But documents have inherent structure: headings introduce topics, paragraphs develop those topics, and sections relate to each other hierarchically. Hierarchical chunking respects these natural boundaries, cutting along semantic divisions rather than arbitrary character counts.

This isn't just about better boundaries – it's about preserving the logical flow of information that makes chunks genuinely useful for retrieval.

### Simple Hierarchical Chunking

Here's a basic example of how hierarchical chunking works:

```python
def simple_hierarchical_chunk(elements: List[DocumentElement], 
                            max_chunk_size: int = 500) -> List[str]:
    """Create simple hierarchical chunks based on document structure."""
    chunks = []
    current_chunk = []
    current_size = 0
    
    for element in elements:
        element_size = len(element.content)
        
        # Start new chunk on major headings if current chunk has content
        if (element.element_type == ContentType.HEADING and 
            element.level <= 1 and current_chunk):
            
            # Save current chunk
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
        
        # Add element to current chunk if size permits
        if current_size + element_size <= max_chunk_size:
            current_chunk.append(element.content)
            current_size += element_size
        else:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [element.content]
            current_size = element_size
    
    # Save final chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks
```

**Key Benefits:**

- **Natural boundaries**: Uses document structure instead of arbitrary splits
- **Complete sections**: Keeps related content together
- **Size management**: Respects maximum chunk size while preserving structure

### Advanced Hierarchical Chunker

The simple approach demonstrates the concept, but production systems need more sophisticated handling of edge cases, overlap management, and metadata preservation. Our advanced chunker addresses these requirements:

```python
from langchain.schema import Document

class HierarchicalChunker:
    """Creates intelligent chunks based on document hierarchy."""

    def __init__(self, max_chunk_size: int = 1000, overlap_ratio: float = 0.1):
        self.max_chunk_size = max_chunk_size
        self.overlap_ratio = overlap_ratio
        self.analyzer = DocumentStructureAnalyzer()

    def create_hierarchical_chunks(self, document: Document) -> List[Document]:
        """Create chunks that preserve document hierarchy."""
        # Analyze document structure
        elements = self.analyzer.analyze_structure(document.page_content)
        
        # Group elements into logical sections
        sections = self._group_elements_by_hierarchy(elements)
        
        # Create chunks from sections
        chunks = []
        for section in sections:
            section_chunks = self._chunk_section(section, document.metadata)
            chunks.extend(section_chunks)
        
        return chunks

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
            elif element.element_type == ContentType.HEADING and not current_section:
                current_section = [element]
                current_level = element.level
            else:
                current_section.append(element)

        # Add final section
        if current_section:
            sections.append(current_section)

        return sections

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
                # Create chunk from current elements
                chunk = self._create_chunk_from_elements(
                    current_chunk_elements, base_metadata, section_title
                )
                chunks.append(chunk)

                # Start new chunk with overlap for continuity
                overlap_elements = self._get_overlap_elements(current_chunk_elements)
                current_chunk_elements = overlap_elements + [element]
                current_size = sum(len(e.content) for e in current_chunk_elements)
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

This implementation provides intelligent section grouping, size management, and context preservation through overlap. Notice how we maintain rich metadata throughout the process – this metadata becomes crucial for retrieval quality and debugging.

### Enterprise Chunking Pipeline

For production deployments, you need more than just good chunking – you need quality assessment, optimization feedback loops, and the ability to adjust processing based on document characteristics:

```python
class EnterpriseChunkingPipeline:
    """Enterprise-grade chunking pipeline with quality assessment."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.chunker = HierarchicalChunker(
            max_chunk_size=config.get("max_chunk_size", 1000),
            overlap_ratio=config.get("overlap_ratio", 0.1)
        )
        self.quality_assessor = ChunkQualityAssessor()
        
    def process_document_with_quality_control(self, document: Document) -> Dict[str, Any]:
        """Process document with comprehensive quality assessment."""
        # Create initial chunks
        chunks = self.chunker.create_hierarchical_chunks(document)
        
        # Assess chunk quality
        quality_metrics = self.quality_assessor.assess_chunk_quality(chunks)
        
        # Apply quality-based optimization if needed
        if quality_metrics["overall_quality"] < self.config.get("min_quality_threshold", 0.7):
            chunks = self._optimize_chunks(chunks, quality_metrics)
            quality_metrics = self.quality_assessor.assess_chunk_quality(chunks)
        
        return {
            "chunks": chunks,
            "quality_metrics": quality_metrics,
            "processing_stats": {
                "original_length": len(document.page_content),
                "chunk_count": len(chunks),
                "avg_chunk_size": sum(len(c.page_content) for c in chunks) / len(chunks),
                "quality_score": quality_metrics["overall_quality"]
            }
        }
```

This enterprise pipeline includes quality control and optimization feedback loops. The quality threshold approach ensures you catch and fix problematic chunks before they affect retrieval quality.

---

## Part 3: Metadata Extraction & Enhancement - Making Content Discoverable

Raw text chunks, no matter how well structured, often lack the context needed for precise retrieval. A chunk about "memory optimization" might be talking about software memory management or human cognitive memory. Metadata extraction solves this by extracting entities, topics, technical terms, and other contextual information that makes content discoverable and meaningful.

### Simple Metadata Extraction

Here's a basic example of extracting useful metadata from document chunks:

```python
import re
from typing import List, Dict

def extract_simple_metadata(text: str) -> Dict[str, Any]:
    """Extract basic metadata from text content."""
    words = text.split()
    
    # Basic statistics
    metadata = {
        "word_count": len(words),
        "char_count": len(text),
        "sentence_count": len(text.split('.')),
    }
    
    # Extract capitalized words (potential entities)
    capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', text)
    metadata["potential_entities"] = list(set(capitalized_words))[:5]
    
    # Extract numbers and dates
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
    metadata["numbers"] = [float(n) for n in numbers[:5]]
    
    dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', text)
    metadata["dates"] = dates
    
    # Assess content difficulty
    long_words = [w for w in words if len(w) > 6]
    metadata["difficulty_level"] = "advanced" if len(long_words) / len(words) > 0.3 else "intermediate"
    
    return metadata
```

**Metadata Benefits:**

- **Enhanced searchability**: Additional context for retrieval matching
- **Content understanding**: Insight into chunk characteristics
- **Quality assessment**: Metrics for evaluating chunk usefulness

### Advanced Metadata Extractor

The simple approach gives you basic insights, but production systems need more sophisticated extraction that can handle technical content, domain-specific terminology, and complex relationships within text:

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

        # Determine difficulty
        if avg_words_per_sentence > 20 or long_word_ratio > 0.3 or technical_density > 0.1:
            return "advanced"
        elif avg_words_per_sentence > 15 or long_word_ratio > 0.2:
            return "intermediate"
        else:
            return "beginner"
```

### Metadata-Enhanced Chunking Integration

The real power emerges when you combine hierarchical chunking with metadata extraction. This creates chunks that are both structurally coherent and contextually rich – the foundation of high-precision retrieval:

```python
class MetadataEnhancedChunker:
    """Chunker that enriches chunks with extracted metadata."""

    def __init__(self, max_chunk_size: int = 1000):
        self.hierarchical_chunker = HierarchicalChunker(max_chunk_size=max_chunk_size)
        self.metadata_extractor = MetadataExtractor()

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

---

## Part 4: Multi-Modal & Quality Assessment - Handling the Complex Stuff

Real documents aren't just paragraphs and headings. They contain tables with structured data, code blocks with syntactic relationships, lists with hierarchical information, and images with contextual relevance. Naive chunking destroys these structures. Advanced preprocessing preserves them.

### Table-Aware Processing

Tables are particularly challenging because they encode relationships between data points that are completely lost when split by arbitrary text boundaries. A table about quarterly revenue broken in half becomes meaningless – you need specialized handling:

```python
def process_simple_table(table_text: str) -> Dict[str, Any]:
    """Process table content while preserving structure."""
    lines = table_text.strip().split('\n')
    table_lines = [line for line in lines if '|' in line]
    
    if not table_lines:
        return {"error": "No table structure found"}
    
    # Extract headers from first row
    header_row = table_lines[0]
    headers = [cell.strip() for cell in header_row.split('|') if cell.strip()]
    
    # Count data rows (excluding header and separator)
    data_rows = len(table_lines) - 2 if len(table_lines) > 2 else 0
    
    # Create enhanced description
    description = f"Table with {data_rows} rows and {len(headers)} columns"
    if headers:
        description += f" containing data about: {', '.join(headers)}"
    
    return {
        "enhanced_content": f"{description}\n\n{table_text}",
        "metadata": {
            "content_type": "table",
            "row_count": data_rows,
            "column_count": len(headers),
            "headers": headers
        }
    }
```

**Table Processing Benefits:**

- **Structure preservation**: Tables remain intact and meaningful
- **Enhanced searchability**: Descriptive text makes tables discoverable
- **Metadata enrichment**: Table characteristics available for retrieval

### Basic Quality Assessment

Quality assessment is essential because not all chunks are created equal. Some preserve meaning well, others lose crucial context. You need metrics to identify and fix problematic chunks before they affect retrieval performance:

```python
def assess_basic_quality(chunks: List[str]) -> Dict[str, float]:
    """Assess basic quality metrics for chunks."""
    if not chunks:
        return {"error": "No chunks to assess"}
    
    # Calculate size consistency
    chunk_sizes = [len(chunk) for chunk in chunks]
    avg_size = sum(chunk_sizes) / len(chunk_sizes)
    size_variance = sum((size - avg_size) ** 2 for size in chunk_sizes) / len(chunk_sizes)
    size_consistency = 1.0 / (1.0 + size_variance / (avg_size ** 2))
    
    # Calculate information density
    densities = []
    for chunk in chunks:
        words = chunk.split()
        unique_words = set(words)
        if words:
            density = len(unique_words) / len(words)
            densities.append(density)
    
    avg_density = sum(densities) / len(densities) if densities else 0
    
    return {
        "size_consistency": size_consistency,
        "avg_information_density": avg_density,
        "chunk_count": len(chunks),
        "avg_chunk_size": avg_size
    }
```

### Complete Processing Pipeline

Now we bring everything together into a comprehensive processing pipeline that analyzes document characteristics, chooses appropriate strategies, and applies quality controls:

```python
class AdvancedProcessingPipeline:
    """Complete advanced document processing pipeline."""

    def __init__(self, max_chunk_size: int = 1000, enable_quality_assessment: bool = True):
        self.max_chunk_size = max_chunk_size
        self.enable_quality_assessment = enable_quality_assessment
        
        # Initialize processors
        self.metadata_chunker = MetadataEnhancedChunker(max_chunk_size=max_chunk_size)
        self.quality_assessor = ChunkQualityAssessor() if enable_quality_assessment else None

    def process_document(self, document: Document) -> Dict[str, Any]:
        """Process document using the most appropriate strategy."""
        
        # Analyze document characteristics
        doc_analysis = self._analyze_document_complexity(document)
        
        # Choose processing strategy
        if doc_analysis["has_tables"]:
            print("Detected tables - using table-aware processing...")
            processed_chunks = self._process_with_table_awareness(document)
        else:
            print("Using standard hierarchical processing...")
            processed_chunks = self.metadata_chunker.create_enhanced_chunks(document)
        
        # Assess quality if enabled
        quality_metrics = {}
        if self.enable_quality_assessment and self.quality_assessor:
            quality_metrics = self.quality_assessor.assess_chunk_quality(processed_chunks)
        
        # Add processing metadata
        for chunk in processed_chunks:
            chunk.metadata.update({
                "processing_strategy": doc_analysis["recommended_strategy"],
                "document_complexity": doc_analysis["complexity_score"],
                "processing_pipeline": "advanced_v2"
            })
        
        return {
            "chunks": processed_chunks,
            "document_analysis": doc_analysis,
            "quality_metrics": quality_metrics,
            "processing_stats": {
                "chunk_count": len(processed_chunks),
                "total_processed_chars": sum(len(c.page_content) for c in processed_chunks),
                "avg_chunk_size": sum(len(c.page_content) for c in processed_chunks) / len(processed_chunks)
            }
        }

    def _analyze_document_complexity(self, document: Document) -> Dict[str, Any]:
        """Analyze document to determine optimal processing strategy."""
        content = document.page_content

        # Detect various content types
        has_tables = "|" in content and content.count("|") > 5
        has_code = "```" in content or content.count("    ") > 3
        has_lists = content.count("- ") > 3 or content.count("* ") > 3
        has_headings = content.count("#") > 2
        
        # Calculate complexity score
        complexity_score = 0
        if has_tables: complexity_score += 3
        if has_code: complexity_score += 2
        if has_lists: complexity_score += 1
        if has_headings: complexity_score += 2

        # Determine strategy
        if has_tables:
            strategy = "table_aware"
        elif complexity_score > 4:
            strategy = "hierarchical"
        else:
            strategy = "standard"

        return {
            "has_tables": has_tables,
            "has_code": has_code,
            "has_lists": has_lists,
            "has_headings": has_headings,
            "complexity_score": complexity_score,
            "recommended_strategy": strategy
        }
```

### Enterprise Quality Control

The final component is comprehensive quality assessment that evaluates chunks across multiple dimensions. This enables automated quality control and optimization feedback:

```python
class ChunkQualityAssessor:
    """Comprehensive chunk quality assessment."""

    def assess_chunk_quality(self, chunks: List[Document]) -> Dict[str, float]:
        """Multi-dimensional quality assessment."""
        if not chunks:
            return {metric: 0.0 for metric in ["coherence", "density", "consistency", "overall"]}

        # Calculate individual metrics
        coherence = self._calculate_coherence_score(chunks)
        density = self._calculate_information_density(chunks)
        consistency = self._calculate_size_consistency(chunks)
        metadata_richness = self._calculate_metadata_richness(chunks)

        overall_quality = (coherence + density + consistency + metadata_richness) / 4

        return {
            "coherence_score": coherence,
            "information_density": density,
            "size_consistency": consistency,
            "metadata_richness": metadata_richness,
            "overall_quality": overall_quality
        }

    def _calculate_coherence_score(self, chunks: List[Document]) -> float:
        """Calculate topic coherence between adjacent chunks."""
        if len(chunks) < 2:
            return 1.0

        coherence_scores = []
        for i in range(len(chunks) - 1):
            current_topics = set(chunks[i].metadata.get("topics", []))
            next_topics = set(chunks[i + 1].metadata.get("topics", []))
            
            if current_topics and next_topics:
                overlap = len(current_topics & next_topics)
                union = len(current_topics | next_topics)
                score = overlap / union if union > 0 else 0
                coherence_scores.append(score)

        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0

    def _calculate_information_density(self, chunks: List[Document]) -> float:
        """Calculate average information density across chunks."""
        densities = []
        
        for chunk in chunks:
            words = chunk.page_content.split()
            unique_words = set(words)
            
            if words:
                density = len(unique_words) / len(words)
                densities.append(density)
        
        return sum(densities) / len(densities) if densities else 0.0

    def _calculate_metadata_richness(self, chunks: List[Document]) -> float:
        """Assess metadata completeness across chunks."""
        expected_fields = ["topics", "entities", "keywords", "difficulty_level"]
        
        richness_scores = []
        for chunk in chunks:
            present_fields = sum(1 for field in expected_fields 
                               if field in chunk.metadata and chunk.metadata[field])
            score = present_fields / len(expected_fields)
            richness_scores.append(score)
        
        return sum(richness_scores) / len(richness_scores) if richness_scores else 0.0
```

---

## Optional Deep Dive Modules

**⚠️ OPTIONAL CONTENT - Choose based on your goals:**

- **[Module A: Advanced Document Analytics](Session2_ModuleA_Document_Analytics.md)** - Specialized techniques and optimization patterns
- **[Module B: Enterprise Content Processing](Session2_ModuleB_Enterprise_Processing.md)** - Production deployment and scaling strategies

---

## 📝 Multiple Choice Test - Session 2

Test your understanding of advanced chunking and preprocessing concepts:

**Question 1:** What is the primary benefit of detecting content types (headings, tables, code) during document analysis?  
A) Reduces processing time
B) Enables structure-aware chunking that preserves meaning
C) Reduces storage requirements
D) Improves embedding quality  

**Question 2:** In hierarchical chunking, why is it important to track element hierarchy levels?  
A) To reduce memory usage
B) To simplify the codebase
C) To improve processing speed
D) To preserve document structure and create meaningful chunk boundaries  

**Question 3:** What is the main advantage of extracting entities, keywords, and topics during preprocessing?  
A) Reduces chunk size
B) Enables more precise retrieval through enriched context
C) Simplifies the chunking process
D) Improves computational efficiency  

**Question 4:** Why do tables require specialized processing in RAG systems?  
A) Tables use different encoding formats
B) Tables contain more text than paragraphs
C) Tables are always larger than the chunk size
D) Tables have structured relationships that are lost in naive chunking  

**Question 5:** When processing documents with images, what is the best practice for RAG systems?  
A) Store images as binary data in chunks
B) Create separate chunks for each image
C) Replace image references with descriptive text
D) Ignore images completely  

**Question 6:** Which metric is most important for measuring chunk coherence in hierarchical chunking?  
A) Topic consistency between related chunks
B) Number of chunks created
C) Average chunk size
D) Processing speed  

**Question 7:** What is the optimal overlap ratio for hierarchical chunks?  
A) 100% - complete duplication
B) 0% - no overlap needed
C) 10-20% - balanced context and efficiency
D) 50% - maximum context preservation  

**Question 8:** Why should the advanced processing pipeline analyze document complexity before choosing a processing strategy?  
A) To select the most appropriate processing approach for the content type
B) To set the embedding model parameters
C) To reduce computational costs
D) To determine the number of chunks to create  

[**🗂️ View Test Solutions →**](Session2_Test_Solutions.md)

---

## 🧭 Navigation

**Previous:** [Session 1 - Basic RAG Implementation](Session1_Basic_RAG_Implementation.md)

### Optional Deep Dive Modules

- **[Module A: Advanced Document Analytics](Session2_ModuleA_Document_Analytics.md)** - Deep analytics for document structure analysis
- **[Module B: Enterprise Content Processing](Session2_ModuleB_Enterprise_Processing.md)** - Enterprise-scale content processing strategies

**Next:** [Session 3 - Vector Databases & Search Optimization →](Session3_Vector_Databases_Search_Optimization.md)
