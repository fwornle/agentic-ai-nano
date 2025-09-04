# Session 2 - Module A: Document Analytics

> **⚠️ ADVANCED OPTIONAL MODULE**
> Prerequisites: Complete Session 2 core content first.

You've implemented structure-aware chunking and metadata extraction in Session 2. But when you deploy to production, you discover that some documents process beautifully while others create fragmented, low-quality chunks that hurt retrieval performance. The difference isn't random – it's complexity.

A simple technical memo needs different processing than a complex legal contract with nested clauses and extensive cross-references. A medical research paper with detailed methodology sections requires different handling than a user manual with step-by-step procedures. This module teaches you to analyze document complexity automatically and adapt your processing strategy accordingly – the difference between generic document processing and enterprise-grade intelligence.

## Advanced Pattern 1: Document Complexity Scoring - Measuring What Matters

### Enterprise Complexity Analysis Framework

The key insight is that document complexity isn't just about length – it's about structural intricacy, semantic density, and processing difficulty. A 100-page contract with standardized clauses might be easier to process than a 10-page research paper with dense technical terminology and complex cross-references.

Our complexity framework evaluates documents across multiple dimensions to select optimal processing strategies:

```python
# Core imports for enterprise document analysis
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import re
```

We start with essential imports for our document analytics framework. NumPy provides efficient numerical operations for scoring calculations, while the typing module ensures type safety in our enterprise-grade system. The `dataclasses` decorator simplifies our data structure definitions, and `re` handles the complex pattern matching that powers domain-specific document analysis.

```python
@dataclass
class DocumentComplexityScore:
    """Comprehensive document complexity assessment."""
    structural_complexity: float
    semantic_complexity: float
    processing_difficulty: float
    overall_score: float
    recommendations: List[str]
    confidence_level: float
```

Our `DocumentComplexityScore` data class encapsulates the multi-dimensional complexity assessment results. Unlike simple difficulty measures, this separates structural complexity (document layout and organization), semantic complexity (terminology and concept density), and processing difficulty (computational requirements). The confidence level indicates how reliable our assessment is based on available patterns and document size.

```python
class EnterpriseComplexityAnalyzer:
    """Production-grade document complexity analysis."""

    def __init__(self):
        # Domain-specific complexity patterns
        self.complexity_patterns = {
            "legal": {
                "high_complexity": [r"whereas", r"heretofore", r"§\s*\d+", r"article\s+[IVX]+"],
                "structural_markers": [r"section\s+\d+", r"clause\s+\d+", r"paragraph\s+\([a-z]\)"],
                "citation_density": [r"\d+\s+U\.S\.C\.", r"\d+\s+F\.\d+d", r"Fed\.\s*R\.\s*Civ\.\s*P\."]
            },
```

The `EnterpriseComplexityAnalyzer` class initializes with domain-specific pattern recognition capabilities. Legal domain patterns capture formal legal language ("whereas", "heretofore"), statutory structure markers ("section 1", "clause A"), and legal citations (U.S.C., Federal Reporter formats). These patterns enable automatic detection of legal document complexity based on linguistic and structural indicators that legal professionals instinctively recognize.

```python
            "technical": {
                "code_blocks": [r"```[\s\S]*?```", r"(?:^|\n)    .*", r"`[^`]+`"],
                "api_references": [r"[A-Z][a-zA-Z]+\.[a-zA-Z]+\(\)", r"HTTP[S]?://"],
                "version_patterns": [r"v?\d+\.\d+\.\d+", r"version\s+\d+\.\d+"]
            },
            "medical": {
                "dosage_patterns": [r"\d+\s*mg", r"\d+\s*ml", r"\d+\s*units?"],
                "medical_terms": [r"[A-Z][a-z]+itis", r"[A-Z][a-z]+osis", r"[A-Z][a-z]+emia"],
                "procedure_codes": [r"CPT\s*\d+", r"ICD-\d+"]
            }
        }
```

Technical and medical domain patterns complete our complexity detection framework. Technical patterns identify code blocks (fenced and indented), API references (ClassName.method() patterns), and version strings. Medical patterns recognize dosage information (mg, ml, units), medical terminology suffixes (-itis, -osis, -emia), and procedure codes (CPT, ICD formats). This comprehensive pattern library enables domain-aware complexity assessment that adapts to document type automatically.
```

The complexity patterns dictionary is the heart of our domain-aware analysis. Each domain has specific linguistic and structural markers that indicate complexity. Legal documents use archaic terminology like "whereas" and formal section references. Technical documents contain code blocks and API references. Medical documents include dosage information and standardized terminology patterns. These regex patterns allow us to automatically detect domain-specific complexity indicators that human reviewers would recognize instinctively.

```python
        # Structural complexity weights
        self.structure_weights = {
            "table_density": 3.0,
            "list_density": 1.5,
            "heading_hierarchy": 2.0,
            "code_block_density": 2.5,
            "citation_density": 2.0
        }
```

These weights reflect the relative processing difficulty of different structural elements. Tables are weighted highest (3.0) because they require specialized parsing and maintain relationships between cells. Code blocks (2.5) need syntax preservation and special handling. The weights are calibrated based on real-world processing experience - a document with many tables will require more sophisticated chunking than one with simple lists.

```python
    def analyze_enterprise_complexity(self, document_text: str,
                                    domain: str = "general") -> DocumentComplexityScore:
        """Comprehensive enterprise document complexity analysis."""

        # Multi-dimensional complexity assessment
        structural_score = self._analyze_structural_complexity(document_text, domain)
        semantic_score = self._analyze_semantic_complexity(document_text, domain)
        processing_score = self._assess_processing_difficulty(document_text, domain)

        # Calculate weighted overall score
        overall_score = (structural_score * 0.4 +
                        semantic_score * 0.3 +
                        processing_score * 0.3)

        # Generate actionable recommendations
        recommendations = self._generate_processing_recommendations(
            structural_score, semantic_score, processing_score, domain
        )

        # Calculate confidence based on pattern matches
        confidence = self._calculate_confidence_level(document_text, domain)

        return DocumentComplexityScore(
            structural_complexity=structural_score,
            semantic_complexity=semantic_score,
            processing_difficulty=processing_score,
            overall_score=overall_score,
            recommendations=recommendations,
            confidence_level=confidence
        )

    def _analyze_structural_complexity(self, text: str, domain: str) -> float:
        """Analyze document structural complexity with domain awareness."""
        complexity_score = 0.0
        text_length = len(text)

        if text_length == 0:
            return 0.0

        # Base structural elements
        table_count = text.count('|')
        code_blocks = len(re.findall(r'```[\s\S]*?```', text))
        lists = len(re.findall(r'^\s*[-*+]\s+', text, re.MULTILINE))
        headings = len(re.findall(r'^#+\s+', text, re.MULTILINE))

        # Calculate density scores
        table_density = (table_count / text_length) * 1000
        code_density = (code_blocks / text_length) * 1000
        list_density = (lists / text_length) * 1000
        heading_density = (headings / text_length) * 1000

        # Apply domain-specific weights
        complexity_score += table_density * self.structure_weights["table_density"]
        complexity_score += code_density * self.structure_weights["code_block_density"]
        complexity_score += list_density * self.structure_weights["list_density"]
        complexity_score += heading_density * self.structure_weights["heading_hierarchy"]

        # Domain-specific structural patterns
        if domain in self.complexity_patterns:
            domain_patterns = self.complexity_patterns[domain]
            for pattern_type, patterns in domain_patterns.items():
                pattern_matches = sum(len(re.findall(pattern, text, re.IGNORECASE))
                                    for pattern in patterns)
                pattern_density = (pattern_matches / text_length) * 1000
                complexity_score += pattern_density * 1.5

        # Normalize to 0-1 scale
        return min(complexity_score / 100, 1.0)

    def _analyze_semantic_complexity(self, text: str, domain: str) -> float:
        """Analyze semantic complexity including terminology and concepts."""
        words = text.split()

        if not words:
            return 0.0

        # Vocabulary complexity metrics
        unique_words = set(words)
        vocabulary_richness = len(unique_words) / len(words)

        # Technical terminology density
        technical_terms = self._count_technical_terms(text, domain)
        technical_density = technical_terms / len(words)

        # Sentence complexity
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = len(words) / len(sentences) if sentences else 0

        # Readability approximation (simplified)
        long_words = len([w for w in words if len(w) > 6])
        long_word_ratio = long_words / len(words)

        # Calculate semantic complexity score
        complexity_factors = [
            vocabulary_richness * 0.3,
            min(technical_density * 10, 1.0) * 0.3,
            min(avg_sentence_length / 25, 1.0) * 0.2,
            long_word_ratio * 0.2
        ]

        return sum(complexity_factors)

    def _assess_processing_difficulty(self, text: str, domain: str) -> float:
        """Assess computational and processing difficulty."""
        # Document size factor
        size_complexity = min(len(text) / 10000, 1.0) * 0.3

        # Mixed content complexity
        has_tables = '|' in text and text.count('|') > 5
        has_code = '```' in text or text.count('    ') > 10
        has_images = any(ext in text.lower() for ext in ['.jpg', '.png', '.gif', '.pdf'])

        mixed_content_score = sum([has_tables, has_code, has_images]) / 3 * 0.4

        # Cross-reference complexity
        cross_refs = len(re.findall(r'see\s+(?:section|chapter|page)\s+\d+', text, re.IGNORECASE))
        cross_ref_complexity = min(cross_refs / 10, 1.0) * 0.3

        return size_complexity + mixed_content_score + cross_ref_complexity

    def _count_technical_terms(self, text: str, domain: str) -> int:
        """Count domain-specific technical terms."""
        technical_count = 0

        # General technical patterns
        acronyms = len(re.findall(r'\b[A-Z]{2,}\b', text))
        technical_count += acronyms

        # Domain-specific terms
        if domain in self.complexity_patterns:
            for pattern_list in self.complexity_patterns[domain].values():
                for pattern in pattern_list:
                    technical_count += len(re.findall(pattern, text, re.IGNORECASE))

        return technical_count

    def _generate_processing_recommendations(self, structural: float, semantic: float,
                                           processing: float, domain: str) -> List[str]:
        """Generate actionable processing recommendations."""
        recommendations = []

        # Structural recommendations
        if structural > 0.7:
            recommendations.append("Use specialized structural processing for complex document layout")
            recommendations.append("Implement table-aware chunking for structured content")
        elif structural > 0.4:
            recommendations.append("Apply hierarchical chunking to preserve document structure")

        # Semantic recommendations
        if semantic > 0.7:
            recommendations.append("Enable advanced metadata extraction for technical terminology")
            recommendations.append("Use domain-specific preprocessing patterns")
        elif semantic > 0.4:
            recommendations.append("Apply enhanced keyword and entity extraction")

        # Processing recommendations
        if processing > 0.7:
            recommendations.append("Allocate additional computational resources for processing")
            recommendations.append("Consider batch processing with quality checkpoints")

        # Domain-specific recommendations
        if domain == "legal":
            recommendations.append("Preserve citation relationships and statutory references")
        elif domain == "medical":
            recommendations.append("Validate dosage information and maintain treatment correlations")
        elif domain == "technical":
            recommendations.append("Keep code blocks intact and preserve API documentation structure")

        return recommendations

    def _calculate_confidence_level(self, text: str, domain: str) -> float:
        """Calculate confidence in complexity assessment."""
        # Base confidence on document size and pattern matches
        size_confidence = min(len(text) / 1000, 1.0) * 0.5

        # Pattern match confidence
        pattern_matches = 0
        if domain in self.complexity_patterns:
            for pattern_list in self.complexity_patterns[domain].values():
                for pattern in pattern_list:
                    if re.search(pattern, text, re.IGNORECASE):
                        pattern_matches += 1

        pattern_confidence = min(pattern_matches / 5, 1.0) * 0.5

        return size_confidence + pattern_confidence
```

Confidence calculation helps you trust the complexity assessment. Size confidence increases with document length up to 1000 characters - very short documents might not contain enough patterns for reliable analysis. Pattern match confidence increases as we find more domain-specific indicators, capping at 5 matches to prevent over-confidence from pattern-heavy documents. Together, these measures give you a 0-1 confidence score indicating how reliable the complexity assessment is.

### Enterprise Implementation Example

The complexity analysis becomes powerful when integrated into automated processing pipelines. Instead of applying one-size-fits-all processing, you can dynamically adapt your approach based on document characteristics:

```python
class ProductionComplexityPipeline:
    """Production pipeline with complexity-based processing selection."""

    def __init__(self):
        self.complexity_analyzer = EnterpriseComplexityAnalyzer()
        self.processing_strategies = {
            "simple": {"max_chunk_size": 500, "overlap": 0.05},
            "standard": {"max_chunk_size": 1000, "overlap": 0.1},
            "complex": {"max_chunk_size": 1500, "overlap": 0.15},
            "enterprise": {"max_chunk_size": 2000, "overlap": 0.2}
        }

    def process_with_adaptive_strategy(self, document: str, domain: str = "general") -> Dict[str, Any]:
        """Process document with complexity-adaptive strategy."""
        # Analyze complexity
        complexity_score = self.complexity_analyzer.analyze_enterprise_complexity(document, domain)

        # Select processing strategy
        if complexity_score.overall_score < 0.3:
            strategy = "simple"
        elif complexity_score.overall_score < 0.6:
            strategy = "standard"
        elif complexity_score.overall_score < 0.8:
            strategy = "complex"
        else:
            strategy = "enterprise"

        # Apply selected strategy
        strategy_config = self.processing_strategies[strategy]

        return {
            "complexity_analysis": complexity_score,
            "selected_strategy": strategy,
            "processing_config": strategy_config,
            "recommendations": complexity_score.recommendations,
            "confidence": complexity_score.confidence_level
        }
```

The return structure provides complete transparency into the adaptive processing decision. You get the full complexity analysis, the selected strategy with configuration parameters, specific processing recommendations, and confidence levels. This enables both automated processing and human oversight - operators can see why a particular strategy was chosen and adjust thresholds based on domain-specific requirements.

## Advanced Pattern 2: Multi-Domain Quality Assessment - Beyond Basic Metrics

### Enterprise Quality Framework

Complexity scoring tells you how hard a document is to process, but quality assessment tells you how well you actually processed it. This distinction is crucial – a document might be simple to process but result in poor-quality chunks due to inappropriate boundary decisions or missing context.

Enterprise quality assessment goes beyond basic metrics like chunk size consistency to evaluate semantic coherence, information completeness, and domain-specific quality criteria:

```python
class EnterpriseQualityFramework:
    """Comprehensive quality assessment for enterprise document processing."""

    def __init__(self):
        self.quality_dimensions = {
            "coherence": 0.25,      # Topic consistency
            "completeness": 0.25,   # Information preservation
            "accessibility": 0.20,  # Readability and structure
            "accuracy": 0.15,       # Factual correctness
            "efficiency": 0.15      # Processing optimization
        }

        self.domain_quality_criteria = {
            "legal": {
                "citation_preservation": 0.3,
                "clause_integrity": 0.3,
                "terminology_accuracy": 0.4
            },
            "medical": {
                "dosage_accuracy": 0.4,
                "procedure_completeness": 0.3,
                "terminology_precision": 0.3
            },
            "technical": {
                "code_integrity": 0.4,
                "api_documentation": 0.3,
                "version_consistency": 0.3
            }
        }

    def assess_enterprise_quality(self, chunks: List[Document],
                                domain: str = "general") -> Dict[str, Any]:
        """Comprehensive enterprise quality assessment."""

        # Base quality metrics
        base_quality = self._assess_base_quality(chunks)

        # Domain-specific quality metrics
        domain_quality = self._assess_domain_quality(chunks, domain)

        # Processing efficiency metrics
        efficiency_metrics = self._assess_processing_efficiency(chunks)

        # Calculate weighted overall score
        overall_score = self._calculate_weighted_score(
            base_quality, domain_quality, efficiency_metrics
        )

        # Generate quality improvement recommendations
        recommendations = self._generate_quality_recommendations(
            base_quality, domain_quality, efficiency_metrics, domain
        )

        return {
            "overall_quality": overall_score,
            "base_quality": base_quality,
            "domain_quality": domain_quality,
            "efficiency_metrics": efficiency_metrics,
            "recommendations": recommendations,
            "quality_grade": self._assign_quality_grade(overall_score)
        }

    def _assess_base_quality(self, chunks: List[Document]) -> Dict[str, float]:
        """Assess fundamental quality metrics."""
        if not chunks:
            return {"coherence": 0, "completeness": 0, "accessibility": 0}

        # Coherence assessment
        coherence = self._measure_semantic_coherence(chunks)

        # Completeness assessment
        completeness = self._measure_information_completeness(chunks)

        # Accessibility assessment
        accessibility = self._measure_content_accessibility(chunks)

        return {
            "coherence": coherence,
            "completeness": completeness,
            "accessibility": accessibility
        }

    def _measure_semantic_coherence(self, chunks: List[Document]) -> float:
        """Advanced semantic coherence measurement."""
        if len(chunks) < 2:
            return 1.0

        coherence_scores = []

        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]

            # Topic overlap analysis
            current_topics = set(current_chunk.metadata.get("topics", []))
            next_topics = set(next_chunk.metadata.get("topics", []))

            if current_topics and next_topics:
                topic_overlap = len(current_topics & next_topics) / len(current_topics | next_topics)
            else:
                topic_overlap = 0

            # Entity continuity analysis
            current_entities = set(current_chunk.metadata.get("entities", []))
            next_entities = set(next_chunk.metadata.get("entities", []))

            if current_entities and next_entities:
                entity_overlap = len(current_entities & next_entities) / len(current_entities | next_entities)
            else:
                entity_overlap = 0

            # Combined coherence score
            chunk_coherence = (topic_overlap * 0.6 + entity_overlap * 0.4)
            coherence_scores.append(chunk_coherence)

        return np.mean(coherence_scores) if coherence_scores else 0.0

    def _assess_domain_quality(self, chunks: List[Document], domain: str) -> Dict[str, float]:
        """Domain-specific quality assessment."""
        if domain not in self.domain_quality_criteria:
            return {}

        criteria = self.domain_quality_criteria[domain]
        domain_scores = {}

        for criterion, weight in criteria.items():
            if criterion == "citation_preservation" and domain == "legal":
                domain_scores[criterion] = self._assess_citation_preservation(chunks)
            elif criterion == "dosage_accuracy" and domain == "medical":
                domain_scores[criterion] = self._assess_dosage_accuracy(chunks)
            elif criterion == "code_integrity" and domain == "technical":
                domain_scores[criterion] = self._assess_code_integrity(chunks)
            # Add more domain-specific assessments as needed

        return domain_scores

    def _assess_processing_efficiency(self, chunks: List[Document]) -> Dict[str, float]:
        """Assess processing efficiency metrics."""
        if not chunks:
            return {"size_consistency": 0, "metadata_richness": 0, "processing_speed": 0}

        # Size consistency
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        avg_size = np.mean(chunk_sizes)
        size_variance = np.var(chunk_sizes)
        size_consistency = 1.0 / (1.0 + size_variance / (avg_size ** 2)) if avg_size > 0 else 0

        # Metadata richness
        expected_metadata = ["topics", "entities", "keywords", "difficulty_level"]
        metadata_scores = []

        for chunk in chunks:
            present_metadata = sum(1 for field in expected_metadata
                                 if field in chunk.metadata and chunk.metadata[field])
            richness = present_metadata / len(expected_metadata)
            metadata_scores.append(richness)

        metadata_richness = np.mean(metadata_scores) if metadata_scores else 0

        return {
            "size_consistency": size_consistency,
            "metadata_richness": metadata_richness,
            "chunk_count": len(chunks),
            "avg_chunk_size": avg_size
        }
```

Metadata richness evaluates whether the processing pipeline successfully extracted expected metadata fields like topics, entities, keywords, and difficulty levels. Rich metadata enables better filtering, routing, and context understanding during retrieval. The richness score averages metadata completeness across all chunks, helping identify documents where metadata extraction failed or performed poorly.

## Advanced Pattern 3: Real-Time Quality Monitoring - Continuous Intelligence

Quality assessment is most valuable when it's continuous, not just a one-time check. In production, you need real-time monitoring that can detect when document processing quality degrades and automatically trigger corrective actions. This pattern transforms quality assessment from batch analysis into operational intelligence:

```python
class ProductionQualityMonitor:
    """Real-time quality monitoring for production RAG systems."""

    def __init__(self, quality_thresholds: Dict[str, float] = None):
        self.quality_framework = EnterpriseQualityFramework()
        self.thresholds = quality_thresholds or {
            "overall_quality": 0.7,
            "coherence": 0.6,
            "completeness": 0.7,
            "domain_quality": 0.8
        }
        self.quality_history = []
        self.alerts = []

    def monitor_processing_quality(self, chunks: List[Document],
                                 document_id: str, domain: str = "general") -> Dict[str, Any]:
        """Real-time quality monitoring with alerting."""

        # Assess quality
        quality_assessment = self.quality_framework.assess_enterprise_quality(chunks, domain)

        # Check against thresholds
        quality_alerts = self._check_quality_thresholds(quality_assessment, document_id)

        # Store quality history
        quality_record = {
            "document_id": document_id,
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "quality_scores": quality_assessment,
            "alerts": quality_alerts
        }
        self.quality_history.append(quality_record)

        # Generate quality report
        quality_report = self._generate_quality_report(quality_assessment, quality_alerts)

        return {
            "quality_assessment": quality_assessment,
            "quality_alerts": quality_alerts,
            "quality_report": quality_report,
            "processing_recommendation": self._get_processing_recommendation(quality_assessment)
        }

    def _check_quality_thresholds(self, assessment: Dict[str, Any],
                                document_id: str) -> List[Dict[str, Any]]:
        """Check quality scores against thresholds and generate alerts."""
        alerts = []

        for metric, threshold in self.thresholds.items():
            if metric in assessment and assessment[metric] < threshold:
                alert = {
                    "document_id": document_id,
                    "metric": metric,
                    "actual_score": assessment[metric],
                    "threshold": threshold,
                    "severity": "high" if assessment[metric] < threshold * 0.8 else "medium",
                    "timestamp": datetime.now().isoformat()
                }
                alerts.append(alert)
                self.alerts.append(alert)

        return alerts

    def get_quality_analytics(self, lookback_hours: int = 24) -> Dict[str, Any]:
        """Generate quality analytics for specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)

        recent_records = [
            record for record in self.quality_history
            if datetime.fromisoformat(record["timestamp"]) > cutoff_time
        ]

        if not recent_records:
            return {"message": "No quality data available for specified period"}

        # Calculate aggregate metrics
        quality_trends = self._analyze_quality_trends(recent_records)
        alert_summary = self._summarize_alerts(lookback_hours)

        return {
            "period_summary": {
                "documents_processed": len(recent_records),
                "avg_quality_score": quality_trends["avg_overall_quality"],
                "quality_trend": quality_trends["trend_direction"],
                "alert_count": len(alert_summary)
            },
            "quality_trends": quality_trends,
            "alert_summary": alert_summary,
            "recommendations": self._generate_system_recommendations(recent_records)
        }
```

Quality analytics provide operational intelligence for production RAG systems. The 24-hour default lookback period captures recent performance without overwhelming operators with historical data. Trend analysis identifies whether quality is improving, stable, or degrading over time, while alert summaries highlight recurring problems that need systematic fixes rather than individual document attention. System recommendations translate analytics into actionable configuration changes or process improvements.

---

## 📝 Multiple Choice Test - Session 2

**Question 1:** What is the primary benefit of document complexity scoring in enterprise RAG systems?  
A) Reduces processing time for all documents  
B) Enables optimal processing strategy selection based on document characteristics  
C) Eliminates the need for human document review  
D) Automatically fixes document formatting issues  

**Question 2:** Which approach provides the most comprehensive chunk quality assessment?  
A) Word count and character length only  
B) Balance of coherence, information density, and completeness  
C) Processing speed and memory usage  
D) File size and format compatibility  

**Question 3:** Why is domain-specific document processing crucial for enterprise applications?  
A) It reduces computational requirements  
B) It preserves domain-specific structure and terminology for better retrieval  
C) It standardizes all documents to a common format  
D) It eliminates the need for manual preprocessing  

**Question 4:** How should information density be measured in enterprise quality frameworks?  
A) Total word count divided by paragraph count  
B) Ratio of unique words to total words  
C) Number of technical terms per sentence  
D) Average sentence length in characters  

**Question 5:** What is the most effective method for measuring semantic coherence between chunks?  
A) Word overlap and shared vocabulary analysis  
B) Semantic similarity and topic consistency evaluation  
C) File format and structure comparison  
D) Processing time and resource utilization  

[View Solutions →](Session2_Test_Solutions.md)

---

## 🧭 Navigation

**Previous:** [Session 1 - Foundations →](Session1_RAG_Essentials.md)  
**Next:** [Session 3 - Advanced Patterns →](Session3_Performance_Optimization.md)

---
