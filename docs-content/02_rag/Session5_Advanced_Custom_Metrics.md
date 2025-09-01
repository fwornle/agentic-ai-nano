# ⚙️ Session 5: Advanced Custom Metrics

> **⚙️ IMPLEMENTER PATH - Advanced Custom Evaluation**  
> Prerequisites: Complete 🎯 Observer and 📝 Participant paths  
> Time Investment: 3-4 hours  
> Outcome: Build sophisticated domain-specific RAG evaluators  

## Learning Outcomes

By completing this section, you will master:  

- Domain-specific evaluation metric design and implementation  
- Advanced LLM-as-a-Judge evaluation systems  
- Sophisticated retrieval quality assessment techniques  
- Custom evaluation frameworks for specialized RAG applications  

## Prerequisites Validation

Before diving into advanced implementations, ensure mastery of:  

- Completed 🎯 [RAG Evaluation Essentials](Session5_RAG_Evaluation_Essentials.md)  
- Completed 📝 [RAGAS Implementation Practice](Session5_RAGAS_Implementation_Practice.md)  
- Working knowledge of statistical analysis and evaluation theory  
- Experience with production RAG system deployment  

## ⚙️ Advanced Custom Metrics Framework

### Domain-Specific Evaluation Architecture

Standard metrics like RAGAS provide excellent baseline evaluation, but production RAG systems often require specialized metrics that capture domain-specific quality dimensions. Let's build a sophisticated framework for custom evaluation:  

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field
import json
import re
from collections import defaultdict

@dataclass
class CustomEvaluationResult:
    """Comprehensive result structure for custom evaluations."""
    metric_name: str
    score: float
    confidence: float
    explanation: str
    component_scores: Dict[str, float] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AdvancedMetricFramework(ABC):
    """Abstract base for advanced custom evaluation metrics."""
    
    def __init__(self, name: str, llm_judge=None, domain_knowledge=None):
        self.name = name
        self.llm_judge = llm_judge
        self.domain_knowledge = domain_knowledge or {}
        self.evaluation_history = []
    
    @abstractmethod
    def evaluate(self, query: str, response: str, contexts: List[str], 
                **kwargs) -> CustomEvaluationResult:
        """Core evaluation method - must be implemented by subclasses."""
        pass
    
    def batch_evaluate(self, evaluation_data: List[Dict]) -> List[CustomEvaluationResult]:
        """Efficient batch evaluation with progress tracking."""
        results = []
        total_items = len(evaluation_data)
        
        for i, item in enumerate(evaluation_data):
            if i % 10 == 0:
                print(f"Custom evaluation progress: {i+1}/{total_items}")
            
            result = self.evaluate(
                item['query'], item['response'], 
                item.get('contexts', []), **item.get('kwargs', {})
            )
            results.append(result)
            
            # Store evaluation history for learning
            self.evaluation_history.append({
                'input': item,
                'result': result,
                'timestamp': time.time()
            })
        
        return results
```

This framework provides the foundation for building specialized evaluation metrics while maintaining consistency and extensibility.

### Advanced Citation Quality Evaluator

Let's implement a sophisticated citation quality metric that goes beyond simple pattern matching:  

```python
class AdvancedCitationQualityMetric(AdvancedMetricFramework):
    """Advanced evaluation of citation quality and source attribution."""
    
    def __init__(self, llm_judge, domain_knowledge=None):
        super().__init__("advanced_citation_quality", llm_judge, domain_knowledge)
        
        # Citation pattern recognition
        self.citation_patterns = {
            'explicit_reference': [r'\[Source: [^\]]+\]', r'\(Source: [^)]+\)', r'According to [^,.:;]+'],
            'implicit_reference': [r'studies show', r'research indicates', r'experts suggest'],
            'direct_quote': [r'"[^"]*"', r'\'[^\']*\''],
            'paraphrase_indicators': [r'as stated in', r'according to', r'research by']
        }
        
        # Quality assessment criteria
        self.quality_criteria = {
            'specificity': 0.25,    # How specific are the citations?
            'accuracy': 0.30,       # Do citations match source content?
            'relevance': 0.25,      # Are citations relevant to claims?
            'completeness': 0.20    # Are all claims properly attributed?
        }
    
    def evaluate(self, query: str, response: str, contexts: List[str], 
                **kwargs) -> CustomEvaluationResult:
        """Comprehensive citation quality evaluation."""
        
        # Extract citations and analyze patterns
        citation_analysis = self._analyze_citation_patterns(response)
        
        # Evaluate citation-context alignment
        alignment_score = self._evaluate_citation_alignment(response, contexts)
        
        # Assess citation specificity and quality
        specificity_score = self._assess_citation_specificity(citation_analysis)
        
        # Check claim-citation completeness
        completeness_score = self._evaluate_claim_coverage(response, citation_analysis)
        
        # Calculate weighted overall score
        component_scores = {
            'pattern_quality': citation_analysis['quality_score'],
            'context_alignment': alignment_score,
            'specificity': specificity_score,
            'completeness': completeness_score
        }
        
        overall_score = sum(
            component_scores[criterion] * weight 
            for criterion, weight in self.quality_criteria.items()
        )
        
        return CustomEvaluationResult(
            metric_name=self.name,
            score=overall_score,
            confidence=self._calculate_confidence(component_scores),
            explanation=self._generate_explanation(component_scores),
            component_scores=component_scores,
            evidence=citation_analysis['citations'],
            improvement_suggestions=self._generate_improvements(component_scores)
        )
```

This advanced evaluator provides nuanced assessment of citation quality beyond basic pattern matching.

### Citation Pattern Analysis Implementation

Let's implement sophisticated citation pattern recognition:  

```python
    def _analyze_citation_patterns(self, response: str) -> Dict[str, Any]:
        """Analyze citation patterns in response text."""
        
        citation_analysis = {
            'citations': [],
            'pattern_counts': defaultdict(int),
            'quality_indicators': [],
            'quality_score': 0.0
        }
        
        # Extract citations by pattern type
        for pattern_type, patterns in self.citation_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, response, re.IGNORECASE)
                for match in matches:
                    citation_analysis['citations'].append({
                        'text': match,
                        'type': pattern_type,
                        'position': response.lower().find(match.lower())
                    })
                citation_analysis['pattern_counts'][pattern_type] += len(matches)
        
        # Assess pattern quality
        total_citations = len(citation_analysis['citations'])
        if total_citations > 0:
            # Reward explicit over implicit references
            explicit_ratio = citation_analysis['pattern_counts']['explicit_reference'] / total_citations
            citation_analysis['quality_score'] = 0.4 + (explicit_ratio * 0.6)
            
            # Bonus for diverse citation types
            pattern_diversity = len([count for count in citation_analysis['pattern_counts'].values() if count > 0])
            diversity_bonus = min(pattern_diversity * 0.1, 0.2)
            citation_analysis['quality_score'] += diversity_bonus
        
        return citation_analysis
```

This analysis provides detailed insight into citation patterns and their quality characteristics.

### Context-Citation Alignment Assessment

Now let's implement sophisticated alignment checking between citations and source contexts:  

```python
    def _evaluate_citation_alignment(self, response: str, contexts: List[str]) -> float:
        """Evaluate how well citations align with available contexts."""
        
        if not contexts:
            return 0.0
        
        # Extract claims and their associated citations
        response_sentences = self._extract_sentences_with_citations(response)
        alignment_scores = []
        
        for sentence_data in response_sentences:
            sentence = sentence_data['text']
            has_citation = sentence_data['has_citation']
            
            # Find best matching context for this sentence
            best_match_score = 0.0
            
            for context in contexts:
                # Calculate semantic similarity (simplified with word overlap)
                sentence_words = set(sentence.lower().split())
                context_words = set(context.lower().split())
                
                overlap = len(sentence_words.intersection(context_words))
                similarity = overlap / max(len(sentence_words), 1)
                
                best_match_score = max(best_match_score, similarity)
            
            # Weight alignment by citation presence
            if has_citation and best_match_score > 0.3:
                alignment_scores.append(min(best_match_score * 1.2, 1.0))  # Bonus for cited claims
            elif not has_citation and best_match_score > 0.3:
                alignment_scores.append(best_match_score * 0.8)  # Penalty for uncited claims
            else:
                alignment_scores.append(best_match_score)
        
        return np.mean(alignment_scores) if alignment_scores else 0.0
```

This alignment assessment ensures citations correspond to actual source content, detecting potential hallucinations.

## ⚙️ Advanced Retrieval Quality Metrics

### Multi-Dimensional Retrieval Assessment

Standard retrieval metrics focus on relevance, but production systems need comprehensive quality assessment. Let's build advanced retrieval evaluators:  

```python
class AdvancedRetrievalQualityMetric(AdvancedMetricFramework):
    """Comprehensive retrieval quality assessment beyond basic relevance."""
    
    def __init__(self, embedding_model, llm_judge=None):
        super().__init__("advanced_retrieval_quality", llm_judge)
        self.embedding_model = embedding_model
        
        # Multi-dimensional assessment criteria
        self.assessment_dimensions = {
            'semantic_relevance': 0.30,    # How semantically relevant to query
            'information_coverage': 0.25,   # How much needed info is covered
            'source_diversity': 0.20,       # Diversity of information sources
            'temporal_relevance': 0.15,     # Recency and temporal alignment
            'authority_quality': 0.10       # Source credibility and authority
        }
    
    def evaluate(self, query: str, response: str, contexts: List[str], 
                **kwargs) -> CustomEvaluationResult:
        """Multi-dimensional retrieval quality evaluation."""
        
        # Semantic relevance assessment
        semantic_score = self._calculate_semantic_relevance_advanced(query, contexts)
        
        # Information coverage analysis
        coverage_score = self._assess_information_coverage(query, contexts)
        
        # Source diversity evaluation
        diversity_score = self._evaluate_source_diversity(contexts)
        
        # Temporal relevance (if temporal info available)
        temporal_score = self._assess_temporal_relevance(
            query, contexts, kwargs.get('temporal_context')
        )
        
        # Authority assessment (if authority info available)
        authority_score = self._evaluate_source_authority(
            contexts, kwargs.get('source_metadata', {})
        )
        
        # Calculate weighted composite score
        component_scores = {
            'semantic_relevance': semantic_score,
            'information_coverage': coverage_score,
            'source_diversity': diversity_score,
            'temporal_relevance': temporal_score,
            'authority_quality': authority_score
        }
        
        overall_score = sum(
            component_scores[dim] * weight 
            for dim, weight in self.assessment_dimensions.items()
        )
        
        return CustomEvaluationResult(
            metric_name=self.name,
            score=overall_score,
            confidence=self._calculate_retrieval_confidence(component_scores),
            explanation=self._generate_retrieval_explanation(component_scores),
            component_scores=component_scores,
            improvement_suggestions=self._generate_retrieval_improvements(component_scores)
        )
```

This multi-dimensional approach captures the full spectrum of retrieval quality factors that impact RAG system performance.

### Advanced Semantic Relevance Calculation

Let's implement sophisticated semantic relevance that goes beyond simple similarity:  

```python
    def _calculate_semantic_relevance_advanced(self, query: str, contexts: List[str]) -> float:
        """Advanced semantic relevance with multiple similarity measures."""
        
        if not contexts:
            return 0.0
        
        # Get embeddings for query and all contexts
        query_embedding = self.embedding_model.encode([query])[0]
        context_embeddings = self.embedding_model.encode(contexts)
        
        relevance_scores = []
        
        for i, context_emb in enumerate(context_embeddings):
            # Cosine similarity
            cosine_sim = np.dot(query_embedding, context_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(context_emb)
            )
            
            # Keyword overlap bonus
            query_keywords = set(query.lower().split())
            context_keywords = set(contexts[i].lower().split())
            keyword_overlap = len(query_keywords.intersection(context_keywords))
            keyword_bonus = min(keyword_overlap * 0.05, 0.2)
            
            # Context length penalty (very short contexts are often low quality)
            length_penalty = 0.0
            if len(contexts[i].split()) < 20:
                length_penalty = 0.1
            
            # Composite relevance score
            composite_score = cosine_sim + keyword_bonus - length_penalty
            relevance_scores.append(max(0.0, min(1.0, composite_score)))
        
        # Return weighted average (top contexts weighted more heavily)
        sorted_scores = sorted(relevance_scores, reverse=True)
        weights = [0.4, 0.3, 0.2, 0.1] if len(sorted_scores) >= 4 else [1.0/len(sorted_scores)] * len(sorted_scores)
        
        weighted_relevance = sum(
            score * weight for score, weight in zip(sorted_scores[:4], weights)
        )
        
        return weighted_relevance
```

This advanced calculation provides nuanced relevance assessment that considers multiple quality factors.

### Information Coverage Assessment

Let's implement sophisticated coverage analysis that determines if retrieved contexts contain sufficient information:  

```python
    def _assess_information_coverage(self, query: str, contexts: List[str]) -> float:
        """Assess how completely contexts cover information needs."""
        
        # Extract query intent and information needs
        information_needs = self._extract_information_needs(query)
        
        coverage_scores = []
        
        for need in information_needs:
            need_coverage = 0.0
            
            for context in contexts:
                # Check if this context addresses the information need
                context_relevance = self._calculate_need_context_relevance(need, context)
                need_coverage = max(need_coverage, context_relevance)
            
            coverage_scores.append(need_coverage)
        
        # Overall coverage is the average across all information needs
        return np.mean(coverage_scores) if coverage_scores else 0.0
    
    def _extract_information_needs(self, query: str) -> List[str]:
        """Extract distinct information needs from query."""
        
        # Simple information need extraction (in practice, use NLP)
        needs = []
        
        # Question word analysis
        question_patterns = {
            'what': 'definition/explanation',
            'how': 'process/method', 
            'why': 'reason/cause',
            'when': 'timing/sequence',
            'where': 'location/context',
            'who': 'person/entity'
        }
        
        query_lower = query.lower()
        for pattern, need_type in question_patterns.items():
            if pattern in query_lower:
                needs.append(need_type)
        
        # If no specific patterns, treat as general information need
        if not needs:
            needs.append('general_information')
        
        return needs
```

This coverage assessment ensures retrieved contexts collectively provide comprehensive information to answer the query.

## ⚙️ Domain-Specific Evaluation Systems

### Legal Document RAG Evaluator

Let's implement a specialized evaluator for legal document RAG systems that considers domain-specific quality requirements:  

```python
class LegalRAGEvaluator(AdvancedMetricFramework):
    """Specialized evaluator for legal document RAG systems."""
    
    def __init__(self, llm_judge, legal_knowledge_base=None):
        super().__init__("legal_rag_evaluator", llm_judge)
        self.legal_knowledge_base = legal_knowledge_base or {}
        
        # Legal-specific evaluation criteria
        self.legal_criteria = {
            'legal_accuracy': 0.35,      # Accuracy of legal information
            'citation_completeness': 0.25, # Complete legal citations
            'jurisdiction_awareness': 0.20, # Relevant to correct jurisdiction
            'precedent_relevance': 0.15,   # Relevant legal precedents
            'risk_disclosure': 0.05       # Appropriate disclaimers
        }
        
        # Legal citation patterns
        self.legal_citation_patterns = [
            r'\d+\s+\w+\s+\d+',  # Case citations (e.g., "123 F.3d 456")
            r'\d+\s+U\.S\.C\.\s+§\s+\d+',  # USC citations
            r'§\s*\d+[\.\d]*',   # Section references
        ]
    
    def evaluate(self, query: str, response: str, contexts: List[str], 
                **kwargs) -> CustomEvaluationResult:
        """Specialized legal RAG evaluation."""
        
        # Extract case context
        jurisdiction = kwargs.get('jurisdiction', 'federal')
        case_type = kwargs.get('case_type', 'general')
        
        # Legal accuracy assessment
        accuracy_score = self._assess_legal_accuracy(response, contexts)
        
        # Citation completeness check
        citation_score = self._evaluate_legal_citations(response)
        
        # Jurisdiction relevance
        jurisdiction_score = self._check_jurisdiction_relevance(
            response, contexts, jurisdiction
        )
        
        # Precedent analysis
        precedent_score = self._analyze_precedent_relevance(response, case_type)
        
        # Risk and disclaimer assessment
        risk_score = self._evaluate_risk_disclosure(response)
        
        # Composite scoring
        component_scores = {
            'legal_accuracy': accuracy_score,
            'citation_completeness': citation_score,
            'jurisdiction_awareness': jurisdiction_score,
            'precedent_relevance': precedent_score,
            'risk_disclosure': risk_score
        }
        
        overall_score = sum(
            component_scores[criterion] * weight
            for criterion, weight in self.legal_criteria.items()
        )
        
        return CustomEvaluationResult(
            metric_name=self.name,
            score=overall_score,
            confidence=self._calculate_legal_confidence(component_scores),
            explanation=self._generate_legal_explanation(component_scores),
            component_scores=component_scores,
            improvement_suggestions=self._generate_legal_improvements(component_scores)
        )
```

This specialized evaluator ensures legal RAG systems meet the stringent requirements of legal information systems.

### Medical RAG Evaluator

Let's create a specialized evaluator for medical/healthcare RAG systems:  

```python
class MedicalRAGEvaluator(AdvancedMetricFramework):
    """Specialized evaluator for medical/healthcare RAG systems."""
    
    def __init__(self, llm_judge, medical_knowledge_base=None):
        super().__init__("medical_rag_evaluator", llm_judge)
        self.medical_knowledge_base = medical_knowledge_base or {}
        
        # Medical-specific evaluation criteria
        self.medical_criteria = {
            'clinical_accuracy': 0.40,     # Clinical accuracy and safety
            'evidence_quality': 0.25,      # Quality of cited evidence
            'contraindication_awareness': 0.20, # Awareness of risks/contraindications
            'professional_tone': 0.10,     # Appropriate professional language
            'disclaimer_presence': 0.05    # Medical disclaimers present
        }
        
        # Medical terminology and patterns
        self.medical_patterns = {
            'drug_names': r'[A-Z][a-z]+(?:ine|ol|ide|ium|ate)\b',
            'dosages': r'\d+\s*(?:mg|mcg|g|ml|cc)\b',
            'conditions': r'(?:syndrome|disease|disorder|condition)\b',
            'procedures': r'(?:surgery|procedure|therapy|treatment)\b'
        }
        
        # Safety-critical terms that require careful handling
        self.safety_terms = [
            'contraindicated', 'adverse', 'side effect', 'warning', 
            'caution', 'risk', 'dangerous', 'toxic', 'lethal'
        ]
    
    def evaluate(self, query: str, response: str, contexts: List[str], 
                **kwargs) -> CustomEvaluationResult:
        """Specialized medical RAG evaluation."""
        
        # Clinical accuracy assessment
        accuracy_score = self._assess_clinical_accuracy(response, contexts)
        
        # Evidence quality evaluation
        evidence_score = self._evaluate_medical_evidence(response, contexts)
        
        # Contraindication and safety assessment
        safety_score = self._assess_safety_awareness(response)
        
        # Professional tone evaluation
        tone_score = self._evaluate_professional_tone(response)
        
        # Disclaimer presence check
        disclaimer_score = self._check_medical_disclaimers(response)
        
        # Composite medical scoring
        component_scores = {
            'clinical_accuracy': accuracy_score,
            'evidence_quality': evidence_score,
            'contraindication_awareness': safety_score,
            'professional_tone': tone_score,
            'disclaimer_presence': disclaimer_score
        }
        
        overall_score = sum(
            component_scores[criterion] * weight
            for criterion, weight in self.medical_criteria.items()
        )
        
        return CustomEvaluationResult(
            metric_name=self.name,
            score=overall_score,
            confidence=self._calculate_medical_confidence(component_scores),
            explanation=self._generate_medical_explanation(component_scores),
            component_scores=component_scores,
            improvement_suggestions=self._generate_medical_improvements(component_scores),
            metadata={'safety_flags': self._identify_safety_flags(response)}
        )
```

This medical evaluator ensures healthcare RAG systems meet the critical safety and accuracy standards required in medical applications.

## ⚙️ Advanced LLM-as-a-Judge Systems

### Multi-Perspective Evaluation Framework

Let's implement a sophisticated LLM-as-a-Judge system that uses multiple evaluation perspectives for robust assessment:  

```python
class MultiPerspectiveLLMJudge:
    """Advanced LLM evaluation using multiple judge perspectives."""
    
    def __init__(self, llm_models, perspective_configs):
        self.llm_models = llm_models  # Multiple LLM models for diversity
        self.perspective_configs = perspective_configs
        self.evaluation_history = []
    
    def evaluate_from_multiple_perspectives(self, query: str, response: str, 
                                          contexts: List[str]) -> Dict[str, Any]:
        """Evaluate response from multiple expert perspectives."""
        
        perspective_results = {}
        
        for perspective_name, config in self.perspective_configs.items():
            print(f"Evaluating from {perspective_name} perspective...")
            
            # Select appropriate LLM for this perspective
            llm_model = self._select_model_for_perspective(perspective_name)
            
            # Generate perspective-specific evaluation
            perspective_result = self._evaluate_single_perspective(
                query, response, contexts, perspective_name, config, llm_model
            )
            
            perspective_results[perspective_name] = perspective_result
        
        # Aggregate perspectives into final assessment
        final_assessment = self._aggregate_perspective_results(perspective_results)
        
        # Store evaluation history
        self.evaluation_history.append({
            'query': query,
            'response': response,
            'perspective_results': perspective_results,
            'final_assessment': final_assessment,
            'timestamp': time.time()
        })
        
        return final_assessment
```

This multi-perspective approach reduces bias and provides more robust evaluation by considering different expert viewpoints.

### Advanced Evaluation Prompt Engineering

Let's implement sophisticated prompt engineering for reliable LLM-as-a-Judge evaluation:  

```python
    def _create_advanced_evaluation_prompt(self, query: str, response: str, 
                                         contexts: List[str], perspective: str, 
                                         config: Dict) -> str:
        """Create sophisticated evaluation prompt with multiple quality dimensions."""
        
        context_text = '\n\n'.join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(contexts[:3])])
        
        evaluation_prompt = f"""You are an expert {perspective} evaluator assessing AI-generated responses.

EVALUATION TASK: Assess the quality of this response across multiple dimensions.

QUERY: {query}

RESPONSE: {response}

AVAILABLE CONTEXTS:
{context_text}

EVALUATION FRAMEWORK:
Please evaluate the response on each dimension using the 1-5 scale:
5 - Excellent: Exceeds expectations across all criteria
4 - Good: Meets expectations with minor areas for improvement  
3 - Satisfactory: Adequate performance with some notable gaps
2 - Poor: Below expectations with significant issues
1 - Very Poor: Fails to meet basic requirements

DIMENSIONS TO EVALUATE:
"""
        
        # Add dimension-specific criteria
        for dimension, criteria in config['dimensions'].items():
            evaluation_prompt += f"""
{dimension.upper()}:
{criteria['description']}
Specific criteria: {', '.join(criteria['criteria'])}
"""
        
        evaluation_prompt += f"""

RESPONSE FORMAT:
For each dimension, provide:
- SCORE: [1-5]
- EVIDENCE: [Specific examples from the response supporting your score]
- IMPROVEMENT: [Specific suggestions for improvement]

Then provide:
- OVERALL_SCORE: [Average of dimension scores]
- SUMMARY: [2-3 sentence overall assessment]
- KEY_STRENGTHS: [Main strengths of the response]
- KEY_WEAKNESSES: [Main areas needing improvement]

Begin your evaluation:
"""
        
        return evaluation_prompt
```

This advanced prompt engineering ensures comprehensive, structured evaluation that provides actionable feedback.

## Practice Implementation Exercises

### Exercise 1: Domain-Specific Evaluator

1. Choose a specialized domain (e.g., financial, technical, educational)  
2. Define 5 domain-specific evaluation criteria with weights  
3. Implement complete custom evaluator class  
4. Test on domain-specific RAG outputs and document results  

### Exercise 2: Multi-Dimensional Retrieval Assessment

1. Implement comprehensive retrieval evaluator with 4+ dimensions  
2. Include semantic, coverage, diversity, and quality assessments  
3. Test against different retrieval strategies  
4. Create performance comparison dashboard  

### Exercise 3: Advanced LLM-as-a-Judge System

1. Design 3 different expert perspectives for evaluation  
2. Implement multi-perspective evaluation framework  
3. Compare single vs. multi-perspective evaluation reliability  
4. Document bias reduction and accuracy improvements  

## Integration and Deployment Patterns

### Custom Metrics Integration

```python
class CustomMetricsEvaluationPipeline:
    """Integration pipeline for custom evaluation metrics."""
    
    def __init__(self):
        self.registered_metrics = {}
        self.evaluation_configs = {}
    
    def register_custom_metric(self, metric_name: str, metric_instance):
        """Register custom evaluation metric."""
        self.registered_metrics[metric_name] = metric_instance
        
    def create_evaluation_config(self, config_name: str, metrics_config: Dict):
        """Create evaluation configuration using custom metrics."""
        self.evaluation_configs[config_name] = metrics_config
        
    def run_custom_evaluation_suite(self, evaluation_data: List[Dict], 
                                   config_name: str) -> Dict[str, Any]:
        """Run comprehensive evaluation using custom metrics."""
        
        if config_name not in self.evaluation_configs:
            raise ValueError(f"Configuration '{config_name}' not found")
        
        config = self.evaluation_configs[config_name]
        results = {
            'config_name': config_name,
            'metric_results': {},
            'aggregate_scores': {},
            'recommendations': []
        }
        
        # Run each configured metric
        for metric_name, metric_config in config.items():
            if metric_name in self.registered_metrics:
                metric_instance = self.registered_metrics[metric_name]
                
                # Run metric evaluation
                metric_results = metric_instance.batch_evaluate(evaluation_data)
                results['metric_results'][metric_name] = metric_results
                
                # Calculate aggregate scores
                scores = [r.score for r in metric_results if r.score is not None]
                if scores:
                    results['aggregate_scores'][metric_name] = {
                        'mean': np.mean(scores),
                        'std': np.std(scores),
                        'min': min(scores),
                        'max': max(scores)
                    }
        
        return results
```

This integration pattern enables seamless deployment of custom metrics in production evaluation pipelines.

## Learning Path Summary

**⚙️ Implementer Path Mastery**: You've built sophisticated custom evaluation metrics, domain-specific evaluators, and advanced LLM-as-a-Judge systems. You can now create specialized evaluation frameworks that capture the unique quality requirements of your RAG applications.

**Advanced Capabilities Achieved:**  

- Domain-specific evaluation metric design and implementation  
- Multi-dimensional retrieval quality assessment  
- Specialized evaluators for legal, medical, and other critical domains  
- Advanced LLM-as-a-Judge systems with multiple perspectives  
- Custom metric integration and deployment patterns  

**Next Advanced Topic:**  

- **⚙️ Implementer Path**: [Enterprise Monitoring Systems →](Session5_Enterprise_Monitoring_Systems.md) - Production-scale monitoring and alerting infrastructure  

---

## Navigation

[← Previous: Automated Testing Practice](Session5_Automated_Testing_Practice.md) | [Module Overview](Session5_RAG_Evaluation_Quality_Assessment.md) | [Next: Enterprise Monitoring →](Session5_Enterprise_Monitoring_Systems.md)