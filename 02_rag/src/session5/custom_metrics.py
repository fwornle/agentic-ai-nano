# Custom evaluation metrics
import numpy as np
from typing import List, Dict, Any, Optional

class CustomRAGMetrics:
    """Custom evaluation metrics for specialized RAG applications."""
    
    def __init__(self, llm_judge, domain_knowledge: Optional[Dict] = None):
        self.llm_judge = llm_judge
        self.domain_knowledge = domain_knowledge or {}
        
    def evaluate_answer_completeness(self, query: str, answer: str, 
                                   contexts: List[str]) -> float:
        """Evaluate how completely the answer addresses the query."""
        
        completeness_prompt = f"""
        Evaluate how completely this answer addresses the given question based on the provided contexts.
        
        Question: {query}
        
        Answer: {answer}
        
        Available Contexts: {' '.join(contexts[:3])}
        
        Rate completeness on a scale of 0.0 to 1.0:
        - 1.0: Answer fully and comprehensively addresses all aspects of the question
        - 0.7: Answer addresses most important aspects but misses some details
        - 0.4: Answer partially addresses the question but lacks important information
        - 0.1: Answer barely addresses the question or contains mostly irrelevant information
        - 0.0: Answer completely fails to address the question
        
        Consider:
        1. Does the answer cover all aspects of the question?
        2. Are important details included?
        3. Is the scope of the answer appropriate?
        4. Does the answer use information from the contexts effectively?
        
        Return only a number between 0.0 and 1.0:
        """
        
        try:
            response = self.llm_judge.predict(completeness_prompt).strip()
            score = float(response)
            return max(0.0, min(1.0, score))
        except:
            return 0.5
    
    def evaluate_citation_quality(self, answer: str, contexts: List[str]) -> float:
        """Evaluate quality of citations and source attribution."""
        
        # Count citations in answer
        citation_patterns = ['[Source:', '(Source:', 'According to', 'As stated in']
        citation_count = sum(
            answer.lower().count(pattern.lower()) for pattern in citation_patterns
        )
        
        # Check if citations match available contexts
        valid_citations = 0
        for context in contexts:
            # Simple check if context information appears in answer
            context_words = set(context.lower().split())
            answer_words = set(answer.lower().split())
            overlap = len(context_words.intersection(answer_words))
            
            if overlap > 5:  # Threshold for meaningful overlap
                valid_citations += 1
        
        # Calculate citation quality score
        if len(contexts) == 0:
            return 0.0
        
        citation_coverage = valid_citations / len(contexts)
        citation_frequency = min(citation_count / 3, 1.0)  # Normalize to max 1
        
        # Weighted average
        citation_quality = 0.7 * citation_coverage + 0.3 * citation_frequency
        
        return citation_quality
    
    def evaluate_domain_accuracy(self, answer: str, query: str) -> float:
        """Evaluate domain-specific accuracy using domain knowledge."""
        
        if not self.domain_knowledge:
            return 0.5  # Neutral score if no domain knowledge available
        
        # Simple domain-specific validation
        domain_terms = self.domain_knowledge.get('key_terms', [])
        domain_facts = self.domain_knowledge.get('facts', {})
        
        # Check for presence of relevant domain terms
        answer_lower = answer.lower()
        relevant_terms = sum(1 for term in domain_terms if term.lower() in answer_lower)
        term_score = min(relevant_terms / max(len(domain_terms), 1), 1.0)
        
        # Check factual accuracy against domain knowledge
        fact_score = 1.0  # Default to high if no conflicts found
        for fact_key, fact_value in domain_facts.items():
            if fact_key.lower() in answer_lower:
                # Simple check - in practice, this would be more sophisticated
                if str(fact_value).lower() not in answer_lower:
                    fact_score -= 0.2
        
        fact_score = max(0.0, fact_score)
        
        # Weighted combination
        domain_accuracy = 0.6 * fact_score + 0.4 * term_score
        
        return domain_accuracy
    
    def evaluate_answer_coherence(self, answer: str) -> float:
        """Evaluate internal coherence and logical flow of answer."""
        
        # Simple coherence checks
        sentences = answer.split('.')
        if len(sentences) < 2:
            return 0.8  # Short answers are generally coherent
        
        coherence_score = 1.0
        
        # Check for contradictions (simple keyword-based)
        contradiction_pairs = [
            ('yes', 'no'), ('true', 'false'), ('always', 'never'),
            ('increase', 'decrease'), ('high', 'low')
        ]
        
        answer_lower = answer.lower()
        for word1, word2 in contradiction_pairs:
            if word1 in answer_lower and word2 in answer_lower:
                # Check if they're in different contexts (simple distance check)
                pos1 = answer_lower.find(word1)
                pos2 = answer_lower.find(word2)
                if abs(pos1 - pos2) < 50:  # Close proximity suggests potential contradiction
                    coherence_score -= 0.1
        
        # Check for logical flow indicators
        flow_indicators = ['however', 'therefore', 'moreover', 'furthermore', 'consequently']
        flow_count = sum(1 for indicator in flow_indicators if indicator in answer_lower)
        flow_bonus = min(flow_count * 0.05, 0.2)
        coherence_score += flow_bonus
        
        return max(0.0, min(1.0, coherence_score))
    
    def evaluate_answer_depth(self, query: str, answer: str) -> float:
        """Evaluate the depth and thoroughness of the answer."""
        
        # Analyze query complexity to determine expected depth
        query_lower = query.lower()
        complexity_indicators = ['why', 'how', 'explain', 'describe', 'analyze', 'compare']
        is_complex = any(indicator in query_lower for indicator in complexity_indicators)
        
        # Measure answer characteristics
        word_count = len(answer.split())
        sentence_count = len(answer.split('.'))
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Depth indicators
        depth_indicators = ['because', 'due to', 'result in', 'leads to', 'caused by', 'example']
        depth_count = sum(1 for indicator in depth_indicators if indicator in answer.lower())
        
        # Calculate depth score based on query complexity
        if is_complex:
            # Complex queries expect more detailed answers
            length_score = min(word_count / 150, 1.0)  # Optimal around 150 words
            detail_score = min(depth_count / 3, 1.0)    # Expect multiple explanations
        else:
            # Simple queries prefer concise but complete answers
            length_score = min(word_count / 75, 1.0)    # Optimal around 75 words
            detail_score = min(depth_count / 1, 1.0)    # At least one explanation
        
        # Penalize extremely short or long sentences
        sentence_balance = 1.0
        if avg_sentence_length < 8:
            sentence_balance -= 0.1  # Too choppy
        elif avg_sentence_length > 25:
            sentence_balance -= 0.1  # Too complex
        
        depth_score = 0.5 * length_score + 0.3 * detail_score + 0.2 * sentence_balance
        
        return max(0.0, min(1.0, depth_score))
