# ⚙️ Session 3: Advanced Hybrid Search

## Prerequisites

**⚙️ IMPLEMENTER PATH CONTENT**  
Complete these guides before starting:  
1. 🎯 [Observer Path](Session3_Vector_Databases_Search_Optimization.md)  
2. 📝 [Production Implementation](Session3_Production_Implementation.md)  
3. 📝 [Performance Optimization](Session3_Performance_Optimization.md)  

This guide covers advanced hybrid search techniques, query enhancement strategies, and enterprise-grade fusion methods.

---

## Part 1: Advanced Query Enhancement

### Multi-Modal Query Processing

Advanced hybrid search goes beyond simple query expansion to include sophisticated query understanding and enhancement:

```python
import asyncio
from typing import List, Dict, Tuple, Optional, Union
import numpy as np
from dataclasses import dataclass
from enum import Enum
import logging
import time

class QueryType(Enum):
    """Classification of query types for specialized processing."""
    FACTUAL = "factual"
    CONCEPTUAL = "conceptual"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"
    AMBIGUOUS = "ambiguous"

@dataclass
class EnhancedQuery:
    """Enhanced query with multiple representations."""
    original: str
    query_type: QueryType
    intent: str
    semantic_variants: List[str]
    keyword_variants: List[str]
    hypothetical_answers: List[str]
    context_terms: List[str]
    confidence: float

class AdvancedQueryProcessor:
    """Advanced query processing with multi-modal enhancement."""
    
    def __init__(self, llm_client, embedding_model):
        self.llm_client = llm_client
        self.embedding_model = embedding_model
        self.query_type_classifier = self._build_classifier()
        
    async def process_query(self, query: str, context: Dict = None) -> EnhancedQuery:
        """Process query with comprehensive enhancement."""
        
        logging.info(f"Processing query: {query[:100]}...")
        start_time = time.time()
        
        # Parallel processing of different enhancement types
        tasks = [
            self._classify_query_type(query),
            self._extract_intent(query),
            self._generate_semantic_variants(query),
            self._generate_keyword_variants(query),
            self._generate_hypothetical_answers(query),
            self._extract_context_terms(query, context)
        ]
        
        results = await asyncio.gather(*tasks)
        
        query_type, intent, semantic_variants, keyword_variants, hypothetical_answers, context_terms = results
        
        # Calculate overall confidence
        confidence = self._calculate_enhancement_confidence(query, results)
        
        enhanced_query = EnhancedQuery(
            original=query,
            query_type=query_type,
            intent=intent,
            semantic_variants=semantic_variants,
            keyword_variants=keyword_variants,
            hypothetical_answers=hypothetical_answers,
            context_terms=context_terms,
            confidence=confidence
        )
        
        processing_time = time.time() - start_time
        logging.info(f"Query processing completed in {processing_time:.3f}s with {confidence:.2f} confidence")
        
        return enhanced_query
    
    async def _classify_query_type(self, query: str) -> QueryType:
        """Classify query type for specialized processing."""
        
        classification_prompt = f"""
        Analyze this search query and classify its type:
        
        Query: "{query}"
        
        Types:
        - FACTUAL: Seeking specific facts or data
        - CONCEPTUAL: Understanding concepts or theories  
        - COMPARATIVE: Comparing options or alternatives
        - PROCEDURAL: How-to or step-by-step information
        - AMBIGUOUS: Unclear intent or multiple interpretations
        
        Respond with just the type name.
        """
        
        try:
            response = await self.llm_client.agenerate([classification_prompt])
            classification = response.generations[0][0].text.strip().upper()
            
            # Map to enum
            for query_type in QueryType:
                if query_type.value.upper() == classification:
                    return query_type
                    
            return QueryType.AMBIGUOUS
            
        except Exception as e:
            logging.error(f"Query classification failed: {str(e)}")
            return QueryType.AMBIGUOUS
    
    async def _extract_intent(self, query: str) -> str:
        """Extract underlying user intent."""
        
        intent_prompt = f"""
        Analyze the user's intent behind this search query:
        
        Query: "{query}"
        
        Describe what the user is really trying to accomplish in one concise sentence.
        Focus on the underlying need, not just the literal query.
        """
        
        try:
            response = await self.llm_client.agenerate([intent_prompt])
            return response.generations[0][0].text.strip()
        except Exception as e:
            logging.error(f"Intent extraction failed: {str(e)}")
            return "Unknown intent"
    
    async def _generate_semantic_variants(self, query: str) -> List[str]:
        """Generate semantically similar query variants."""
        
        semantic_prompt = f"""
        Generate 3 alternative ways to express this search query using different vocabulary 
        but maintaining the same meaning:
        
        Original: "{query}"
        
        Variants:
        1.
        2. 
        3.
        """
        
        try:
            response = await self.llm_client.agenerate([semantic_prompt])
            variants_text = response.generations[0][0].text.strip()
            
            # Parse variants
            variants = []
            for line in variants_text.split('\n'):
                if line.strip() and any(line.strip().startswith(f"{i}.") for i in range(1, 10)):
                    variant = line.split('.', 1)[1].strip()
                    if variant and variant != query:
                        variants.append(variant)
            
            return variants[:3]
            
        except Exception as e:
            logging.error(f"Semantic variant generation failed: {str(e)}")
            return []
    
    async def _generate_keyword_variants(self, query: str) -> List[str]:
        """Generate keyword-focused query variants."""
        
        keyword_prompt = f"""
        For this query, generate 3 keyword-focused variations that include:
        - Technical terminology
        - Synonyms and related terms
        - Domain-specific language
        
        Original: "{query}"
        
        Keyword variants:
        1.
        2.
        3.
        """
        
        try:
            response = await self.llm_client.agenerate([keyword_prompt])
            variants_text = response.generations[0][0].text.strip()
            
            # Parse variants
            variants = []
            for line in variants_text.split('\n'):
                if line.strip() and any(line.strip().startswith(f"{i}.") for i in range(1, 10)):
                    variant = line.split('.', 1)[1].strip()
                    if variant and variant != query:
                        variants.append(variant)
            
            return variants[:3]
            
        except Exception as e:
            logging.error(f"Keyword variant generation failed: {str(e)}")
            return []
    
    async def _generate_hypothetical_answers(self, query: str) -> List[str]:
        """Generate hypothetical document content that would answer the query."""
        
        hyde_prompt = f"""
        Write 2 brief, informative paragraphs that would likely appear in documents 
        that answer this question. Use authoritative, factual language.
        
        Question: "{query}"
        
        Hypothetical answer 1:
        
        Hypothetical answer 2:
        """
        
        try:
            response = await self.llm_client.agenerate([hyde_prompt])
            content = response.generations[0][0].text.strip()
            
            # Split into separate answers
            answers = []
            current_answer = []
            
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('Hypothetical answer'):
                    if current_answer:
                        answers.append(' '.join(current_answer))
                    current_answer = []
                elif line and not line.startswith('Hypothetical'):
                    current_answer.append(line)
            
            # Add final answer
            if current_answer:
                answers.append(' '.join(current_answer))
            
            return answers[:2]
            
        except Exception as e:
            logging.error(f"Hypothetical answer generation failed: {str(e)}")
            return []
```

The advanced query processor creates comprehensive query representations that enable more effective matching across different search modalities.

### Contextual Query Expansion

```python
class ContextualQueryExpander:
    """Context-aware query expansion with domain knowledge."""
    
    def __init__(self, domain_knowledge: Dict, user_profile: Dict = None):
        self.domain_knowledge = domain_knowledge
        self.user_profile = user_profile or {}
        self.expansion_cache = {}
        
    async def expand_with_context(self, enhanced_query: EnhancedQuery, 
                                 conversation_history: List[str] = None) -> Dict[str, List[str]]:
        """Expand query with contextual information."""
        
        # Create expansion context
        context = self._build_expansion_context(enhanced_query, conversation_history)
        
        # Different expansion strategies
        expansions = {
            'domain_specific': await self._domain_specific_expansion(enhanced_query, context),
            'conversational': await self._conversational_expansion(enhanced_query, conversation_history),
            'temporal': await self._temporal_expansion(enhanced_query, context),
            'personalized': await self._personalized_expansion(enhanced_query, self.user_profile)
        }
        
        # Filter and rank expansions
        filtered_expansions = self._filter_expansion_quality(expansions)
        
        return filtered_expansions
    
    def _build_expansion_context(self, enhanced_query: EnhancedQuery, 
                               conversation_history: List[str]) -> Dict:
        """Build comprehensive context for expansion."""
        
        context = {
            'query_type': enhanced_query.query_type,
            'intent': enhanced_query.intent,
            'domain_indicators': self._extract_domain_indicators(enhanced_query.original),
            'temporal_indicators': self._extract_temporal_indicators(enhanced_query.original),
            'complexity_level': self._assess_query_complexity(enhanced_query.original)
        }
        
        if conversation_history:
            context['conversation_topics'] = self._extract_conversation_topics(conversation_history)
            context['conversation_context'] = conversation_history[-3:]  # Last 3 exchanges
        
        return context
    
    async def _domain_specific_expansion(self, enhanced_query: EnhancedQuery, 
                                       context: Dict) -> List[str]:
        """Generate domain-specific expansions."""
        
        expansions = []
        
        # Check for domain matches
        domain_indicators = context.get('domain_indicators', [])
        
        for domain in domain_indicators:
            if domain in self.domain_knowledge:
                domain_info = self.domain_knowledge[domain]
                
                # Add related terminology
                related_terms = domain_info.get('related_terms', [])
                for term in related_terms:
                    if term.lower() not in enhanced_query.original.lower():
                        expansion = f"{enhanced_query.original} {term}"
                        expansions.append(expansion)
                
                # Add domain-specific synonyms
                synonyms = domain_info.get('synonyms', {})
                for word in enhanced_query.original.split():
                    if word.lower() in synonyms:
                        for synonym in synonyms[word.lower()]:
                            expansion = enhanced_query.original.replace(word, synonym)
                            expansions.append(expansion)
        
        return expansions[:5]  # Limit to top 5
    
    async def _conversational_expansion(self, enhanced_query: EnhancedQuery,
                                      conversation_history: List[str]) -> List[str]:
        """Generate expansions based on conversation context."""
        
        if not conversation_history:
            return []
        
        expansions = []
        
        # Extract key entities and topics from conversation
        conversation_text = ' '.join(conversation_history[-5:])  # Last 5 exchanges
        
        # Simple keyword extraction (in production, use NER)
        important_words = self._extract_important_words(conversation_text)
        
        # Add conversational context to query
        for word in important_words:
            if word.lower() not in enhanced_query.original.lower():
                expansion = f"{enhanced_query.original} {word}"
                expansions.append(expansion)
        
        # Add conversational connectives
        connective_expansions = [
            f"{enhanced_query.original} related to our discussion",
            f"building on our conversation about {enhanced_query.original}",
            f"more information about {enhanced_query.original}"
        ]
        
        expansions.extend(connective_expansions)
        
        return expansions[:5]
    
    async def _temporal_expansion(self, enhanced_query: EnhancedQuery, 
                                context: Dict) -> List[str]:
        """Generate time-aware expansions."""
        
        temporal_indicators = context.get('temporal_indicators', [])
        current_year = str(time.gmtime().tm_year)
        
        expansions = []
        
        # Add temporal context if missing
        if not temporal_indicators:
            expansions.extend([
                f"{enhanced_query.original} {current_year}",
                f"{enhanced_query.original} recent",
                f"{enhanced_query.original} latest",
                f"{enhanced_query.original} current"
            ])
        
        # Expand existing temporal references
        for indicator in temporal_indicators:
            if indicator.lower() in ['recent', 'latest', 'current']:
                expansions.append(f"{enhanced_query.original} {current_year}")
            elif indicator.isdigit() and len(indicator) == 4:  # Year
                # Add related years
                year = int(indicator)
                related_years = [str(year-1), str(year+1)]
                for related_year in related_years:
                    expansion = enhanced_query.original.replace(indicator, related_year)
                    expansions.append(expansion)
        
        return expansions[:3]
    
    def _extract_domain_indicators(self, query: str) -> List[str]:
        """Extract domain indicators from query."""
        
        # Domain keyword mapping
        domain_keywords = {
            'technology': ['API', 'software', 'programming', 'code', 'system', 'database'],
            'medicine': ['patient', 'diagnosis', 'treatment', 'medical', 'health'],
            'finance': ['investment', 'market', 'trading', 'financial', 'revenue'],
            'science': ['research', 'study', 'analysis', 'experiment', 'data']
        }
        
        detected_domains = []
        query_lower = query.lower()
        
        for domain, keywords in domain_keywords.items():
            if any(keyword.lower() in query_lower for keyword in keywords):
                detected_domains.append(domain)
        
        return detected_domains
    
    def _extract_important_words(self, text: str) -> List[str]:
        """Extract important words from conversation context."""
        
        # Simple implementation - in production, use TF-IDF or NER
        words = text.split()
        
        # Filter out common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        important_words = []
        for word in words:
            clean_word = word.strip('.,!?()').lower()
            if (len(clean_word) > 3 and 
                clean_word not in stopwords and 
                clean_word.isalpha()):
                important_words.append(clean_word)
        
        # Return most frequent words
        word_counts = {}
        for word in important_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:10]]
```

Contextual expansion leverages domain knowledge, conversation history, and temporal awareness to create more targeted search queries.

---

## Part 2: Advanced Fusion Algorithms

### Weighted Reciprocal Rank Fusion

Standard RRF treats all search methods equally, but advanced fusion can weight different approaches based on query characteristics and historical performance:

```python
class AdvancedFusionEngine:
    """Advanced fusion with dynamic weighting and quality estimation."""
    
    def __init__(self):
        self.fusion_history = []
        self.method_performance = {
            'semantic': {'avg_precision': 0.7, 'avg_recall': 0.8},
            'lexical': {'avg_precision': 0.6, 'avg_recall': 0.9},
            'hyde': {'avg_precision': 0.8, 'avg_recall': 0.6}
        }
        
    def advanced_fusion(self, search_results: Dict[str, List[Dict]], 
                       enhanced_query: EnhancedQuery,
                       fusion_strategy: str = "adaptive") -> List[Dict]:
        """Advanced fusion with dynamic weighting."""
        
        # Calculate dynamic weights based on query characteristics
        weights = self._calculate_dynamic_weights(enhanced_query, search_results)
        
        if fusion_strategy == "adaptive":
            return self._adaptive_weighted_rrf(search_results, weights)
        elif fusion_strategy == "cascade":
            return self._cascade_fusion(search_results, weights)
        elif fusion_strategy == "ensemble":
            return self._ensemble_fusion(search_results, weights)
        else:
            return self._weighted_rrf(search_results, weights)
    
    def _calculate_dynamic_weights(self, enhanced_query: EnhancedQuery, 
                                 search_results: Dict[str, List[Dict]]) -> Dict[str, float]:
        """Calculate dynamic weights based on query and result characteristics."""
        
        weights = {}
        
        # Base weights from query type
        base_weights = self._get_base_weights_for_query_type(enhanced_query.query_type)
        
        # Adjust weights based on result quality indicators
        for method, results in search_results.items():
            if method in base_weights:
                quality_multiplier = self._assess_result_quality(results, enhanced_query)
                weights[method] = base_weights[method] * quality_multiplier
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {method: weight / total_weight for method, weight in weights.items()}
        
        return weights
    
    def _get_base_weights_for_query_type(self, query_type: QueryType) -> Dict[str, float]:
        """Get base fusion weights based on query type."""
        
        weight_mappings = {
            QueryType.FACTUAL: {
                'semantic': 0.4,
                'lexical': 0.5,
                'hyde': 0.1
            },
            QueryType.CONCEPTUAL: {
                'semantic': 0.6,
                'lexical': 0.2,
                'hyde': 0.2
            },
            QueryType.COMPARATIVE: {
                'semantic': 0.5,
                'lexical': 0.3,
                'hyde': 0.2
            },
            QueryType.PROCEDURAL: {
                'semantic': 0.3,
                'lexical': 0.6,
                'hyde': 0.1
            },
            QueryType.AMBIGUOUS: {
                'semantic': 0.4,
                'lexical': 0.4,
                'hyde': 0.2
            }
        }
        
        return weight_mappings.get(query_type, {
            'semantic': 0.4,
            'lexical': 0.4,
            'hyde': 0.2
        })
    
    def _assess_result_quality(self, results: List[Dict], enhanced_query: EnhancedQuery) -> float:
        """Assess quality of search results for weighting adjustment."""
        
        if not results:
            return 0.1
        
        quality_indicators = []
        
        # Score distribution analysis
        if len(results) > 1:
            scores = [r.get('score', 0) for r in results]
            if max(scores) > 0:
                # Good separation between top and bottom results
                score_range = max(scores) - min(scores)
                score_separation = score_range / max(scores)
                quality_indicators.append(score_separation)
        
        # Result diversity (simple heuristic)
        content_similarities = []
        for i in range(min(3, len(results))):
            for j in range(i+1, min(3, len(results))):
                content1 = results[i].get('content', '')
                content2 = results[j].get('content', '')
                
                # Simple word overlap as diversity measure
                words1 = set(content1.lower().split())
                words2 = set(content2.lower().split())
                
                if words1 and words2:
                    overlap = len(words1.intersection(words2)) / len(words1.union(words2))
                    content_similarities.append(1 - overlap)  # Diversity = 1 - similarity
        
        if content_similarities:
            diversity_score = np.mean(content_similarities)
            quality_indicators.append(diversity_score)
        
        # Overall quality score
        if quality_indicators:
            return min(2.0, max(0.5, np.mean(quality_indicators)))  # Clamp between 0.5 and 2.0
        else:
            return 1.0
    
    def _adaptive_weighted_rrf(self, search_results: Dict[str, List[Dict]], 
                             weights: Dict[str, float], k: int = 60) -> List[Dict]:
        """Adaptive weighted RRF with quality-based weight adjustment."""
        
        doc_scores = {}
        
        for method, results in search_results.items():
            method_weight = weights.get(method, 0)
            
            if method_weight > 0:
                for rank, result in enumerate(results):
                    doc_id = self._get_document_id(result)
                    rrf_score = method_weight / (k + rank + 1)
                    
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = {
                            'document': result,
                            'total_score': 0,
                            'method_scores': {},
                            'method_ranks': {}
                        }
                    
                    doc_scores[doc_id]['total_score'] += rrf_score
                    doc_scores[doc_id]['method_scores'][method] = rrf_score
                    doc_scores[doc_id]['method_ranks'][method] = rank + 1
        
        # Sort by total score
        ranked_results = sorted(
            doc_scores.values(), 
            key=lambda x: x['total_score'], 
            reverse=True
        )
        
        # Add fusion metadata
        for result in ranked_results:
            result['fusion_metadata'] = {
                'fusion_method': 'adaptive_weighted_rrf',
                'weights_used': weights,
                'contributing_methods': list(result['method_scores'].keys()),
                'confidence': min(1.0, result['total_score'] * 2)  # Approximate confidence
            }
        
        return ranked_results
    
    def _cascade_fusion(self, search_results: Dict[str, List[Dict]], 
                       weights: Dict[str, float]) -> List[Dict]:
        """Cascade fusion - use higher-weight methods to filter results from lower-weight methods."""
        
        # Sort methods by weight
        sorted_methods = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_methods:
            return []
        
        # Start with highest-weight method
        primary_method, _ = sorted_methods[0]
        primary_results = search_results.get(primary_method, [])
        
        # Get document IDs from primary method
        primary_doc_ids = set(self._get_document_id(r) for r in primary_results)
        
        # Add results from secondary methods that aren't in primary
        cascade_results = list(primary_results)
        
        for method, weight in sorted_methods[1:]:
            secondary_results = search_results.get(method, [])
            
            for result in secondary_results:
                doc_id = self._get_document_id(result)
                
                # Add if not already in results and passes weight threshold
                if (doc_id not in primary_doc_ids and 
                    weight > 0.1 and  # Minimum weight threshold
                    len(cascade_results) < 20):  # Limit total results
                    
                    result['cascade_source'] = method
                    result['cascade_weight'] = weight
                    cascade_results.append(result)
                    primary_doc_ids.add(doc_id)
        
        return cascade_results
    
    def _ensemble_fusion(self, search_results: Dict[str, List[Dict]], 
                        weights: Dict[str, float]) -> List[Dict]:
        """Ensemble fusion with voting and confidence estimation."""
        
        # Collect all unique documents
        all_docs = {}
        
        for method, results in search_results.items():
            method_weight = weights.get(method, 0)
            
            for rank, result in enumerate(results[:10]):  # Top 10 from each method
                doc_id = self._get_document_id(result)
                
                if doc_id not in all_docs:
                    all_docs[doc_id] = {
                        'document': result,
                        'votes': [],
                        'total_weight': 0,
                        'methods': []
                    }
                
                # Add vote with weight and rank information
                vote_strength = method_weight * (1 / (rank + 1))  # Higher rank = stronger vote
                all_docs[doc_id]['votes'].append({
                    'method': method,
                    'rank': rank + 1,
                    'weight': method_weight,
                    'strength': vote_strength
                })
                all_docs[doc_id]['total_weight'] += vote_strength
                all_docs[doc_id]['methods'].append(method)
        
        # Calculate ensemble scores
        ensemble_results = []
        
        for doc_id, doc_info in all_docs.items():
            # Ensemble score based on weighted votes
            ensemble_score = doc_info['total_weight']
            
            # Confidence based on number of methods agreeing
            confidence = len(set(doc_info['methods'])) / len(search_results)
            
            # Consistency bonus for documents that appear in multiple methods
            consistency_bonus = 1 + (confidence - 1) * 0.2
            ensemble_score *= consistency_bonus
            
            result_entry = {
                'document': doc_info['document'],
                'ensemble_score': ensemble_score,
                'confidence': confidence,
                'voting_methods': list(set(doc_info['methods'])),
                'vote_details': doc_info['votes']
            }
            
            ensemble_results.append(result_entry)
        
        # Sort by ensemble score
        ensemble_results.sort(key=lambda x: x['ensemble_score'], reverse=True)
        
        return ensemble_results
    
    def _get_document_id(self, result: Dict) -> str:
        """Extract consistent document ID from result."""
        return result.get('id', result.get('document_id', hash(str(result.get('content', '')))))
```

Advanced fusion algorithms provide sophisticated result combination strategies that adapt to query characteristics and result quality.

---

## Part 3: Cross-Encoder Reranking Integration

### Production Cross-Encoder Pipeline

Cross-encoders provide superior accuracy by jointly processing query-document pairs, but require careful integration due to computational costs:

```python
from transformers import AutoTokenizer, AutoModel
import torch
from torch.nn.functional import softmax

class ProductionCrossEncoderReranker:
    """Production-ready cross-encoder reranking with optimization."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", 
                 batch_size: int = 16, max_length: int = 512):
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_length = max_length
        
        # Load model and tokenizer
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        
        # Performance tracking
        self.reranking_stats = {
            'total_queries': 0,
            'total_documents_reranked': 0,
            'avg_reranking_time': 0,
            'batch_processing_times': []
        }
        
    async def rerank_results(self, query: str, candidate_results: List[Dict], 
                           top_k: int = 10, confidence_threshold: float = 0.5) -> List[Dict]:
        """Rerank search results using cross-encoder."""
        
        if not candidate_results:
            return []
        
        start_time = time.time()
        
        # Limit candidates for computational efficiency
        candidates_to_rerank = candidate_results[:min(100, len(candidate_results))]
        
        # Batch processing for efficiency
        reranked_results = await self._batch_rerank(query, candidates_to_rerank)
        
        # Filter by confidence threshold
        filtered_results = [
            result for result in reranked_results 
            if result.get('rerank_confidence', 0) >= confidence_threshold
        ]
        
        # Return top-k results
        final_results = filtered_results[:top_k]
        
        # Update statistics
        reranking_time = time.time() - start_time
        self._update_stats(len(candidates_to_rerank), reranking_time)
        
        logging.info(f"Reranked {len(candidates_to_rerank)} documents in {reranking_time:.3f}s, "
                    f"returned {len(final_results)} results above confidence threshold")
        
        return final_results
    
    async def _batch_rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """Perform batch reranking for efficiency."""
        
        reranked_candidates = []
        
        # Process in batches
        for i in range(0, len(candidates), self.batch_size):
            batch = candidates[i:i + self.batch_size]
            batch_start = time.time()
            
            # Prepare batch data
            query_doc_pairs = []
            for candidate in batch:
                doc_content = self._extract_document_content(candidate)
                query_doc_pairs.append((query, doc_content))
            
            # Get reranking scores
            scores = await self._get_batch_scores(query_doc_pairs)
            
            # Update candidates with scores
            for j, candidate in enumerate(batch):
                candidate['rerank_score'] = float(scores[j])
                candidate['rerank_confidence'] = self._convert_score_to_confidence(scores[j])
                candidate['rerank_batch'] = i // self.batch_size
                reranked_candidates.append(candidate)
            
            batch_time = time.time() - batch_start
            self.reranking_stats['batch_processing_times'].append(batch_time)
        
        # Sort by reranking score
        reranked_candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return reranked_candidates
    
    async def _get_batch_scores(self, query_doc_pairs: List[Tuple[str, str]]) -> List[float]:
        """Get cross-encoder scores for a batch of query-document pairs."""
        
        # Tokenize all pairs
        inputs = []
        for query, doc in query_doc_pairs:
            # Truncate document if necessary
            doc_truncated = doc[:self.max_length - len(query) - 10]  # Leave room for special tokens
            inputs.append(f"{query} [SEP] {doc_truncated}")
        
        # Tokenize batch
        tokenized = self.tokenizer(
            inputs,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        ).to(self.device)
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**tokenized)
            # Assuming the model outputs logits for relevance classification
            logits = outputs.logits if hasattr(outputs, 'logits') else outputs.last_hidden_state.mean(dim=1)
            
            # Convert to relevance scores
            if logits.dim() > 1 and logits.size(1) > 1:
                # Multi-class output - use softmax
                probabilities = softmax(logits, dim=-1)
                scores = probabilities[:, -1]  # Assume last class is "relevant"
            else:
                # Single output - use sigmoid
                scores = torch.sigmoid(logits.squeeze())
        
        return scores.cpu().tolist()
    
    def _extract_document_content(self, candidate: Dict) -> str:
        """Extract text content from candidate document."""
        
        # Try different content fields
        content_fields = ['content', 'text', 'document', 'body', 'title', 'snippet']
        
        for field in content_fields:
            if field in candidate and candidate[field]:
                content = candidate[field]
                if isinstance(content, str):
                    return content
                elif isinstance(content, dict):
                    # Handle nested content
                    return str(content)
        
        # Fallback to string representation
        return str(candidate)[:1000]  # Limit length
    
    def _convert_score_to_confidence(self, score: float) -> float:
        """Convert raw cross-encoder score to interpretable confidence."""
        
        # Assuming score is between 0 and 1 (sigmoid output)
        # Apply calibration based on empirical observations
        
        if score < 0.3:
            return score * 0.5  # Low confidence
        elif score < 0.7:
            return 0.15 + (score - 0.3) * 1.75  # Moderate confidence  
        else:
            return 0.85 + (score - 0.7) * 0.5  # High confidence
    
    def _update_stats(self, num_documents: int, reranking_time: float):
        """Update reranking statistics."""
        
        self.reranking_stats['total_queries'] += 1
        self.reranking_stats['total_documents_reranked'] += num_documents
        
        # Update running average
        total_time = self.reranking_stats['avg_reranking_time'] * (self.reranking_stats['total_queries'] - 1)
        self.reranking_stats['avg_reranking_time'] = (total_time + reranking_time) / self.reranking_stats['total_queries']
    
    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics."""
        
        stats = dict(self.reranking_stats)
        
        if stats['batch_processing_times']:
            batch_times = stats['batch_processing_times']
            stats['batch_stats'] = {
                'avg_batch_time': np.mean(batch_times),
                'p95_batch_time': np.percentile(batch_times, 95),
                'total_batches': len(batch_times)
            }
        
        if stats['total_documents_reranked'] > 0:
            stats['avg_documents_per_query'] = stats['total_documents_reranked'] / stats['total_queries']
            stats['documents_per_second'] = stats['total_documents_reranked'] / sum(batch_times) if batch_times else 0
        
        return stats
```

The production cross-encoder pipeline provides sophisticated reranking with batch processing, confidence calibration, and comprehensive performance monitoring.

---

## Part 4: Multi-Stage Search Architecture

### Enterprise Multi-Stage Pipeline

```python
class EnterpriseSearchPipeline:
    """Complete enterprise search pipeline with multiple stages."""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Initialize components
        self.query_processor = AdvancedQueryProcessor(
            config['llm_client'], 
            config['embedding_model']
        )
        self.query_expander = ContextualQueryExpander(
            config['domain_knowledge'],
            config.get('user_profile')
        )
        self.vector_store = config['vector_store']
        self.hybrid_engine = config['hybrid_search_engine']
        self.fusion_engine = AdvancedFusionEngine()
        self.cross_encoder = ProductionCrossEncoderReranker(
            config.get('cross_encoder_model', 'cross-encoder/ms-marco-MiniLM-L-6-v2')
        )
        
        # Pipeline configuration
        self.enable_query_enhancement = config.get('enable_query_enhancement', True)
        self.enable_cross_encoder = config.get('enable_cross_encoder', True)
        self.fusion_strategy = config.get('fusion_strategy', 'adaptive')
        self.max_candidates_for_reranking = config.get('max_candidates_for_reranking', 50)
        
        # Performance tracking
        self.pipeline_stats = {
            'total_queries': 0,
            'stage_times': {
                'query_processing': [],
                'expansion': [],
                'search': [],
                'fusion': [],
                'reranking': [],
                'total': []
            }
        }
    
    async def search(self, query: str, top_k: int = 10, 
                    context: Dict = None, 
                    conversation_history: List[str] = None) -> Dict:
        """Complete enterprise search with all stages."""
        
        pipeline_start = time.time()
        stage_times = {}
        
        logging.info(f"Starting enterprise search pipeline for: {query[:100]}...")
        
        try:
            # Stage 1: Query Processing and Enhancement
            if self.enable_query_enhancement:
                stage_start = time.time()
                enhanced_query = await self.query_processor.process_query(query, context)
                query_expansions = await self.query_expander.expand_with_context(
                    enhanced_query, conversation_history
                )
                stage_times['query_processing'] = time.time() - stage_start
            else:
                enhanced_query = EnhancedQuery(
                    original=query,
                    query_type=QueryType.AMBIGUOUS,
                    intent="Direct search",
                    semantic_variants=[],
                    keyword_variants=[],
                    hypothetical_answers=[],
                    context_terms=[],
                    confidence=0.8
                )
                query_expansions = {}
                stage_times['query_processing'] = 0
            
            # Stage 2: Multi-Method Search
            stage_start = time.time()
            search_results = await self._execute_multi_method_search(
                enhanced_query, query_expansions, top_k
            )
            stage_times['search'] = time.time() - stage_start
            
            # Stage 3: Advanced Fusion
            stage_start = time.time()
            fused_results = self.fusion_engine.advanced_fusion(
                search_results, enhanced_query, self.fusion_strategy
            )
            stage_times['fusion'] = time.time() - stage_start
            
            # Stage 4: Cross-Encoder Reranking (Optional)
            if self.enable_cross_encoder and fused_results:
                stage_start = time.time()
                candidates_for_reranking = fused_results[:self.max_candidates_for_reranking]
                
                # Convert fusion results to reranker format
                candidates = []
                for result in candidates_for_reranking:
                    candidates.append({
                        'content': result.get('document', {}).get('content', ''),
                        'metadata': result.get('document', {}).get('metadata', {}),
                        'fusion_score': result.get('total_score', 0)
                    })
                
                reranked_results = await self.cross_encoder.rerank_results(
                    query, candidates, top_k
                )
                stage_times['reranking'] = time.time() - stage_start
            else:
                reranked_results = fused_results[:top_k]
                stage_times['reranking'] = 0
            
            # Compile final response
            total_time = time.time() - pipeline_start
            stage_times['total'] = total_time
            
            # Update statistics
            self._update_pipeline_stats(stage_times)
            
            response = {
                'results': reranked_results,
                'query_analysis': {
                    'enhanced_query': enhanced_query,
                    'expansions': query_expansions,
                    'processing_confidence': enhanced_query.confidence
                },
                'search_metadata': {
                    'methods_used': list(search_results.keys()),
                    'fusion_strategy': self.fusion_strategy,
                    'cross_encoder_enabled': self.enable_cross_encoder,
                    'total_candidates_considered': sum(len(results) for results in search_results.values())
                },
                'performance': {
                    'stage_times_ms': {k: v * 1000 for k, v in stage_times.items()},
                    'total_time_ms': total_time * 1000
                }
            }
            
            logging.info(f"Enterprise search completed in {total_time:.3f}s, "
                        f"returned {len(reranked_results)} results")
            
            return response
            
        except Exception as e:
            logging.error(f"Enterprise search pipeline failed: {str(e)}")
            raise
    
    async def _execute_multi_method_search(self, enhanced_query: EnhancedQuery, 
                                         query_expansions: Dict,
                                         top_k: int) -> Dict[str, List[Dict]]:
        """Execute search using multiple methods."""
        
        search_tasks = []
        search_methods = {}
        
        # Primary semantic search
        search_methods['semantic_primary'] = self.vector_store.similarity_search_cached(
            enhanced_query.original, k=top_k * 2
        )
        
        # Semantic variants search
        for i, variant in enumerate(enhanced_query.semantic_variants[:2]):  # Limit variants
            method_name = f'semantic_variant_{i+1}'
            search_methods[method_name] = self.vector_store.similarity_search_cached(
                variant, k=top_k
            )
        
        # HyDE search (if hypothetical answers exist)
        for i, hyde_answer in enumerate(enhanced_query.hypothetical_answers[:2]):
            method_name = f'hyde_{i+1}'
            search_methods[method_name] = self.vector_store.similarity_search_cached(
                hyde_answer, k=top_k
            )
        
        # Keyword/BM25 search through hybrid engine
        search_methods['lexical'] = self.hybrid_engine.bm25_search(
            enhanced_query.original, top_k=top_k * 2
        )
        
        # Domain-specific expansions
        domain_expansions = query_expansions.get('domain_specific', [])
        for i, expansion in enumerate(domain_expansions[:2]):  # Limit expansions
            method_name = f'domain_expansion_{i+1}'
            search_methods[method_name] = self.vector_store.similarity_search_cached(
                expansion, k=top_k
            )
        
        # Execute all searches concurrently
        search_results = {}
        for method_name, search_coroutine in search_methods.items():
            try:
                if asyncio.iscoroutine(search_coroutine):
                    result = await search_coroutine
                else:
                    result = search_coroutine
                search_results[method_name] = result
            except Exception as e:
                logging.error(f"Search method {method_name} failed: {str(e)}")
                search_results[method_name] = []
        
        return search_results
    
    def _update_pipeline_stats(self, stage_times: Dict):
        """Update pipeline performance statistics."""
        
        self.pipeline_stats['total_queries'] += 1
        
        for stage, time_taken in stage_times.items():
            self.pipeline_stats['stage_times'][stage].append(time_taken)
    
    def get_pipeline_performance(self) -> Dict:
        """Get comprehensive pipeline performance metrics."""
        
        performance = {
            'total_queries_processed': self.pipeline_stats['total_queries'],
            'stage_performance': {}
        }
        
        for stage, times in self.pipeline_stats['stage_times'].items():
            if times:
                performance['stage_performance'][stage] = {
                    'avg_time_ms': np.mean(times) * 1000,
                    'p95_time_ms': np.percentile(times, 95) * 1000,
                    'total_calls': len(times)
                }
        
        # Component-specific performance
        performance['component_stats'] = {
            'cross_encoder': self.cross_encoder.get_performance_stats(),
            'fusion_engine': {
                'fusion_history_count': len(self.fusion_engine.fusion_history)
            }
        }
        
        return performance
```

The enterprise pipeline orchestrates all advanced search components into a cohesive, production-ready system with comprehensive monitoring and optimization.

---

## Key Advanced Hybrid Search Principles

### Master-Level Insights

**Query Enhancement Mastery:**  
- Multi-modal query processing creates comprehensive search representations  
- Contextual expansion leverages domain knowledge and conversation history  
- Query type classification enables specialized processing strategies  

**Advanced Fusion Techniques:**  
- Dynamic weighting adapts to query characteristics and result quality  
- Cascade and ensemble fusion provide sophisticated combination strategies  
- Quality assessment guides automatic weight adjustment  

**Cross-Encoder Integration:**  
- Batch processing optimizes computational efficiency  
- Confidence calibration enables intelligent filtering  
- Production deployment requires careful resource management  

**Enterprise Architecture:**  
- Multi-stage pipelines enable comprehensive search optimization  
- Performance monitoring across all stages enables bottleneck identification  
- Configurable components support different deployment requirements  

## Production Implementation Guidelines

1. **Query Processing**: Implement parallel enhancement strategies for efficiency  
2. **Fusion Strategy**: Choose fusion method based on query characteristics and performance requirements  
3. **Cross-Encoder Usage**: Balance accuracy improvements against computational costs  
4. **Monitoring**: Track performance at every pipeline stage for optimization opportunities  
5. **Scalability**: Design for concurrent query processing and horizontal scaling  

The advanced hybrid search techniques in this guide enable state-of-the-art retrieval performance while maintaining production-grade reliability and efficiency.

---

## Navigation

[← Advanced HNSW Tuning](Session3_Advanced_HNSW_Tuning.md) | [Back to Observer Path](Session3_Vector_Databases_Search_Optimization.md)