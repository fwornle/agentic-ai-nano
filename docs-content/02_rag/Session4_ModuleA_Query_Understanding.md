# Session 4 - Module A: Query Understanding

> **⚠️ ADVANCED OPTIONAL MODULE**  
> Prerequisites: Complete Session 4 core content first.

You've implemented HyDE, query expansion, and context optimization in Session 4. But when you deploy to real users in conversational interfaces, you discover new challenges: users say "it" without referencing what they mean, attach images expecting visual understanding, and express the same need in dramatically different ways depending on their expertise level.

This module teaches you to build query understanding systems that read between the lines of user intent. You'll implement intent classification that routes queries to specialized processing strategies, context-aware enhancement that maintains conversational memory, and multi-modal processing that handles images and documents alongside text. The goal is transforming ambiguous, incomplete user input into precise, complete information requests.

---

### Related Modules

- **Core Session:** [Session 4 - Query Enhancement & Context Augmentation](Session4_Query_Enhancement_Context_Augmentation.md)
- **Related Module:** [Session 3 Module A - Index Algorithms](Session3_ModuleA_Index_Algorithms.md)

### Code Files: `src/session4/`

- `comprehensive_enhancer.py` - Complete query processing pipeline
- `semantic_gap_analyzer.py` - Query intent detection
- `multi_query_generator.py` - Query expansion techniques
- `demo_query_enhancement.py` - Query understanding showcase

**Quick Start:** `cd src/session4 && python demo_query_enhancement.py`

---

## Advanced Query Understanding Patterns

### **Pattern 1: Intent Classification and Query Routing** - Understanding What Users Really Want

The fundamental challenge in query understanding is that identical questions can require completely different processing strategies depending on user intent. "How do I deploy?" could mean "show me the deployment checklist" (procedural), "what are my deployment options?" (comparative), or "why is my deployment failing?" (troubleshooting).

Intent classification routes queries to specialized processing pipelines that match the user's actual information need, not just their surface language.

First, we define the fundamental intent categories that represent different types of information needs:

```python
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re

class QueryIntent(Enum):
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    COMPARATIVE = "comparative"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    TROUBLESHOOTING = "troubleshooting"
    DEFINITIONAL = "definitional"
```

These intent categories represent the fundamental types of information needs that users express. Understanding intent is crucial because different query types require different retrieval and processing strategies. For example, a factual query like "What is the capital of France?" needs direct information retrieval, while a procedural query like "How do I deploy a RAG system?" requires step-by-step instructions.

Next, we'll define the comprehensive analysis result structure:

```python
@dataclass
class QueryAnalysis:
    intent: QueryIntent
    complexity_level: str
    domain: str
    entities: List[str]
    temporal_references: List[str]
    confidence: float
    processing_strategy: str
```

This analysis structure captures multiple dimensions of query understanding: intent classification, complexity assessment, domain identification, entity extraction, temporal context, confidence scoring, and processing recommendations.

Now let's implement the main analyzer class that orchestrates comprehensive query understanding:

```python
class AdvancedQueryAnalyzer:
    """Advanced query understanding with intent detection and routing."""
    
    def __init__(self, llm_model):
        self.llm_model = llm_model
        self.intent_patterns = self._initialize_intent_patterns()
        self.domain_classifiers = self._initialize_domain_classifiers()
```

The analyzer combines pattern-based recognition with LLM-powered analysis, providing both speed and sophistication in query understanding. This hybrid approach uses fast pattern matching for common query structures while leveraging LLM capabilities for complex or ambiguous queries that require deeper semantic understanding.

Let's implement the comprehensive analysis method that coordinates all aspects of query understanding:

```python
    def analyze_query_comprehensively(self, query: str) -> QueryAnalysis:
        """Perform comprehensive query analysis for optimal processing."""
        
        # Intent classification
        intent = self._classify_intent(query)
        
        # Complexity assessment
        complexity = self._assess_complexity(query)
        
        # Domain detection
        domain = self._detect_domain(query)
        
        # Entity extraction
        entities = self._extract_entities(query)
        
        # Temporal reference detection
        temporal_refs = self._detect_temporal_references(query)
```

This analysis pipeline systematically extracts different aspects of query understanding, building a comprehensive picture of the user's intent and information needs.

Next, we calculate confidence and recommend processing strategy:

```python
        # Confidence scoring
        confidence = self._calculate_confidence(query, intent, domain)
        
        # Processing strategy recommendation
        strategy = self._recommend_processing_strategy(intent, complexity, domain)
        
        return QueryAnalysis(
            intent=intent,
            complexity_level=complexity,
            domain=domain,
            entities=entities,
            temporal_references=temporal_refs,
            confidence=confidence,
            processing_strategy=strategy
        )
```

This multi-step analysis ensures that every aspect of the query is understood before retrieval begins, enabling optimal processing strategy selection.

Now let's examine the intent classification method that combines pattern matching with LLM analysis:

```python
    def _classify_intent(self, query: str) -> QueryIntent:
        """Classify query intent using pattern matching and ML."""
        
        # Pattern-based classification
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query.lower()):
                    return intent
```

Pattern-based classification provides fast intent detection for common query structures and keywords. This approach uses regular expressions to identify linguistic patterns that strongly indicate specific intent types, enabling rapid classification without expensive LLM calls for straightforward queries.

For more complex queries, we fallback to LLM-powered analysis:

```python
        # Fallback to LLM classification
        intent_prompt = f"""
        Classify the intent of this query into one of these categories:
        - factual: Seeking specific facts or information
        - procedural: Asking how to do something
        - comparative: Comparing options or alternatives
        - analytical: Requiring analysis or interpretation
        - creative: Open-ended or creative requests
        - troubleshooting: Problem-solving or debugging
        - definitional: Asking for definitions or explanations
        
        Query: {query}
        
        Return only the category name:
        """
```

The LLM prompt provides clear category definitions and examples for accurate intent classification. By explicitly defining each category and providing the query context, we guide the LLM to make consistent classification decisions that align with our processing capabilities.

Finally, we handle the LLM response with error handling:

```python
        try:
            response = self.llm_model.predict(intent_prompt).strip().lower()
            return QueryIntent(response)
        except:
            return QueryIntent.FACTUAL  # Default fallback
```

Intent classification combines fast pattern matching for common query types with sophisticated LLM analysis for complex cases. This hybrid approach provides both speed and accuracy in understanding user intent.

### **Pattern 2: Context-Aware Query Enhancement** - Remembering the Conversation

The second major challenge emerges in conversational interfaces: users don't repeat context from earlier in the conversation. They say "How do I fix it?" expecting the system to remember that they were discussing database connection errors three messages ago. Or they ask "What about the Python version?" without specifying which Python deployment or configuration they're referencing.

Context-aware enhancement transforms incomplete, reference-heavy queries into complete, self-contained information requests by maintaining conversational memory and resolving implicit references.

```python
class ContextAwareQueryEnhancer:
    """Enhance queries based on user context and conversation history."""
    
    def __init__(self, llm_model):
        self.llm_model = llm_model
        self.conversation_history = {}
        self.user_profiles = {}
```

The context-aware enhancer maintains conversation history and user profiles to provide personalized and contextually relevant query processing. This is essential for conversational RAG systems where users build upon previous interactions and expect the system to remember context from earlier in the session.

Let's implement the main enhancement method that coordinates context integration:

```python
    def enhance_with_context(self, query: str, user_id: str, 
                           session_id: str) -> Dict[str, Any]:
        """Enhance query using conversation context and user profile."""
        
        # Retrieve conversation context
        context = self._get_conversation_context(user_id, session_id)
        
        # Get user profile
        profile = self._get_user_profile(user_id)
        
        # Resolve pronouns and references
        resolved_query = self._resolve_references(query, context)
        
        # Add implicit context
        enriched_query = self._add_implicit_context(resolved_query, profile, context)
```

The enhancement process systematically builds context by retrieving conversation history, user preferences, and resolving ambiguous references.

Finally, we generate query variants and compile the complete enhancement result:

```python
        # Generate query variants
        variants = self._generate_contextual_variants(enriched_query, context)
        
        return {
            "original_query": query,
            "resolved_query": resolved_query,
            "enriched_query": enriched_query,
            "variants": variants,
            "context_used": context,
            "profile_factors": profile
        }
```

This enhancement pipeline transforms ambiguous queries into clear, contextually complete queries that can be processed more effectively by retrieval systems.

Now let's examine the reference resolution process that handles pronouns and implicit references:

```python
    def _resolve_references(self, query: str, context: Dict) -> str:
        """Resolve pronouns and references using conversation context."""
        
        if not context.get("recent_entities"):
            return query
            
        reference_prompt = f"""
        Given this conversation context and current query, resolve any pronouns or references:
        
        Recent entities mentioned: {context.get("recent_entities", [])}
        Previous topics: {context.get("recent_topics", [])}
        
        Current query: {query}
        
        Return the query with references resolved:
        """
```

The reference resolution prompt provides conversation context to help resolve ambiguous references.

We process the LLM response with error handling:

```python
        try:
            return self.llm_model.predict(reference_prompt).strip()
        except:
            return query
```

### **Pattern 3: Multi-Modal Query Processing** - Beyond Text-Only Interaction

The third frontier in query understanding is handling rich media interactions. Users increasingly expect to upload screenshots of error messages, attach configuration files, or reference diagrams when asking questions. A user might upload an architecture diagram and ask "How do I implement this pattern?" expecting the system to understand both the visual content and the technical implementation question.

Multi-modal query processing analyzes images, documents, and other media to extract meaningful context that can be integrated with text-based retrieval, enabling comprehensive understanding of complex user interactions.

```python
class MultiModalQueryProcessor:
    """Process queries that may reference images, documents, or other media."""
    
    def __init__(self, vision_model, llm_model):
        self.vision_model = vision_model
        self.llm_model = llm_model
```

The multi-modal processor combines vision models for image analysis with language models for text processing, enabling comprehensive understanding of complex queries. This capability is increasingly important as users interact with RAG systems through rich media interfaces that support images, documents, and other file types alongside text.

Let's implement the main processing method that handles various attachment types:

```python
    def process_multimodal_query(self, query: str, attachments: List[Dict]) -> Dict[str, Any]:
        """Process query with image, document, or other attachments."""
        
        processed_attachments = []
        
        for attachment in attachments:
            if attachment["type"] == "image":
                description = self._analyze_image(attachment["data"])
                processed_attachments.append({
                    "type": "image",
                    "description": description,
                    "original": attachment
                })
            elif attachment["type"] == "document":
                summary = self._summarize_document(attachment["data"])
                processed_attachments.append({
                    "type": "document",
                    "summary": summary,
                    "original": attachment
                })
```

This processing loop extracts meaningful information from each attachment type using specialized models. For images, vision models generate descriptive text that can be integrated into text-based retrieval. For documents, summarization techniques extract key information while preserving important context.

Next, we integrate the attachment context with the original query:

```python
        # Enhance query with attachment context
        enhanced_query = self._integrate_attachment_context(query, processed_attachments)
        
        return {
            "enhanced_query": enhanced_query,
            "processed_attachments": processed_attachments,
            "multimodal_strategy": self._determine_multimodal_strategy(query, attachments)
        }
```

This processing pipeline extracts meaningful information from each attachment type and integrates it with the text query to create a comprehensive search context.

Now let's examine the image analysis and context integration methods:

```python
    def _analyze_image(self, image_data: bytes) -> str:
        """Analyze image content for query enhancement."""
        # Implement vision model analysis
        description = self.vision_model.describe_image(image_data)
        return description
    
    def _integrate_attachment_context(self, query: str, attachments: List[Dict]) -> str:
        """Integrate attachment descriptions into query."""
        
        if not attachments:
            return query
            
        context_parts = []
        for attachment in attachments:
            if attachment["type"] == "image":
                context_parts.append(f"Image content: {attachment['description']}")
            elif attachment["type"] == "document":
                context_parts.append(f"Document content: {attachment['summary']}")
```

The integration method builds contextual descriptions from each attachment type. Rather than treating attachments as separate entities, we weave their content into the query context to create a unified search target that leverages both textual and multi-modal information.

Finally, we combine the original query with the attachment context:

```python
        enhanced_query = f"{query}\n\nReferenced content:\n" + "\n".join(context_parts)
        return enhanced_query
```

Multi-modal query processing enables RAG systems to handle rich user interactions that include visual content, documents, and other media types. By extracting descriptive information from these attachments and integrating it with the text query, the system can provide more comprehensive and relevant responses.

---

## Multiple Choice Test - Module A

**Question 1:** What is the primary benefit of intent classification in query processing?  
A) Reduces processing time
B) Enables specialized processing strategies tailored to query types
C) Reduces memory usage
D) Simplifies implementation  

**Question 2:** Why is context-aware query enhancement important?  
A) It reduces computational costs
B) It resolves ambiguities and adds implicit context from conversation history
C) It speeds up retrieval
D) It reduces storage requirements  

**Question 3:** How does multi-modal query processing improve RAG systems?  
A) It reduces complexity
B) It enables processing of queries with images, documents, and other media types
C) It reduces memory usage
D) It simplifies deployment  

**Question 4:** What is the value of reference resolution in conversational RAG?  
A) It improves speed
B) It resolves pronouns and references using conversation context for clarity
C) It reduces costs
D) It simplifies architecture  

**Question 5:** Why should query complexity assessment guide processing strategy?  
A) It reduces infrastructure costs
B) It allows allocation of appropriate computational resources and techniques
C) It speeds up all queries
D) It reduces memory usage  

[**🗂️ View Test Solutions →**](Session4_ModuleA_Test_Solutions.md)

## Navigation

**Previous:** [Session 4 - Query Enhancement & Context Augmentation](Session4_Query_Enhancement_Context_Augmentation.md)

### Related Modules

- **Core Session:** [Session 4 - Query Enhancement & Context Augmentation](Session4_Query_Enhancement_Context_Augmentation.md)
- **Related Module:** [Session 3 Module A - Index Algorithms](Session3_ModuleA_Index_Algorithms.md)

**Next:** [Session 5 - RAG Evaluation & Quality Assessment](Session5_RAG_Evaluation_Quality_Assessment.md)

---
