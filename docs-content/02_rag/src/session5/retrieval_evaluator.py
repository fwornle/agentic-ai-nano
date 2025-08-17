# Specialized evaluator for retrieval quality
import numpy as np
from typing import List, Dict, Any, Optional

class RetrievalEvaluator:
    """Specialized evaluator for retrieval quality."""
    
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        
    def evaluate_retrieval_quality(self, query: str, retrieved_contexts: List[str],
                                 ground_truth_contexts: List[str] = None) -> Dict[str, float]:
        """Comprehensive retrieval quality evaluation."""
        
        metrics = {}
        
        # Semantic relevance of retrieved contexts
        metrics['semantic_relevance'] = self._calculate_semantic_relevance(
            query, retrieved_contexts
        )
        
        # Diversity of retrieved contexts
        metrics['context_diversity'] = self._calculate_context_diversity(
            retrieved_contexts
        )
        
        # Coverage of information needs
        metrics['information_coverage'] = self._assess_information_coverage(
            query, retrieved_contexts
        )
        
        # If ground truth available, calculate precision/recall
        if ground_truth_contexts:
            precision_recall = self._calculate_precision_recall(
                retrieved_contexts, ground_truth_contexts
            )
            metrics.update(precision_recall)
        
        return metrics
    
    def _calculate_semantic_relevance(self, query: str, 
                                    contexts: List[str]) -> float:
        """Calculate average semantic relevance of contexts to query."""
        
        if not contexts:
            return 0.0
        
        query_embedding = self.embedding_model.encode([query])[0]
        context_embeddings = self.embedding_model.encode(contexts)
        
        # Calculate similarities
        similarities = []
        for ctx_emb in context_embeddings:
            similarity = np.dot(query_embedding, ctx_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(ctx_emb)
            )
            similarities.append(similarity)
        
        return float(np.mean(similarities))
    
    def _calculate_context_diversity(self, contexts: List[str]) -> float:
        """Calculate diversity among retrieved contexts."""
        
        if len(contexts) < 2:
            return 1.0  # Single context is maximally diverse
        
        context_embeddings = self.embedding_model.encode(contexts)
        
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(context_embeddings)):
            for j in range(i+1, len(context_embeddings)):
                similarity = np.dot(context_embeddings[i], context_embeddings[j]) / (
                    np.linalg.norm(context_embeddings[i]) * np.linalg.norm(context_embeddings[j])
                )
                similarities.append(similarity)
        
        # Diversity is inverse of average similarity
        avg_similarity = np.mean(similarities)
        diversity = 1.0 - avg_similarity
        
        return max(0.0, diversity)
    
    def _assess_information_coverage(self, query: str, contexts: List[str]) -> float:
        """Assess how well contexts cover the information need."""
        
        if not contexts:
            return 0.0
        
        # Simple coverage assessment based on keyword overlap
        query_words = set(query.lower().split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        query_keywords = query_words - stop_words
        
        if not query_keywords:
            return 0.5  # Neutral score if no meaningful keywords
        
        covered_keywords = set()
        for context in contexts:
            context_words = set(context.lower().split())
            covered_keywords.update(query_keywords.intersection(context_words))
        
        coverage = len(covered_keywords) / len(query_keywords)
        return min(1.0, coverage)
    
    def _calculate_precision_recall(self, retrieved: List[str], 
                                  ground_truth: List[str]) -> Dict[str, float]:
        """Calculate precision and recall against ground truth."""
        
        if not retrieved or not ground_truth:
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
        
        # Simple string matching for relevance (in practice, use semantic similarity)
        retrieved_set = set(retrieved)
        ground_truth_set = set(ground_truth)
        
        # Find overlapping contexts (simplified)
        relevant_retrieved = len(retrieved_set.intersection(ground_truth_set))
        
        precision = relevant_retrieved / len(retrieved) if retrieved else 0.0
        recall = relevant_retrieved / len(ground_truth) if ground_truth else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def evaluate_ranking_quality(self, query: str, ranked_contexts: List[str], 
                               relevance_scores: List[float] = None) -> Dict[str, float]:
        """Evaluate the quality of context ranking."""
        
        metrics = {}
        
        # If relevance scores provided, calculate ranking metrics
        if relevance_scores and len(relevance_scores) == len(ranked_contexts):
            metrics['ndcg_5'] = self._calculate_ndcg(relevance_scores, k=5)
            metrics['ndcg_10'] = self._calculate_ndcg(relevance_scores, k=10)
            metrics['mrr'] = self._calculate_mrr(relevance_scores)
        
        # Position-based diversity
        if len(ranked_contexts) >= 2:
            metrics['position_diversity'] = self._calculate_position_diversity(ranked_contexts)
        
        return metrics
    
    def _calculate_ndcg(self, relevance_scores: List[float], k: int = 5) -> float:
        """Calculate Normalized Discounted Cumulative Gain."""
        
        k = min(k, len(relevance_scores))
        if k == 0:
            return 0.0
        
        # DCG calculation
        dcg = relevance_scores[0] if k > 0 else 0.0
        for i in range(1, k):
            dcg += relevance_scores[i] / np.log2(i + 1)
        
        # Ideal DCG (IDCG)
        ideal_relevance = sorted(relevance_scores[:k], reverse=True)
        idcg = ideal_relevance[0] if k > 0 else 0.0
        for i in range(1, k):
            idcg += ideal_relevance[i] / np.log2(i + 1)
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def _calculate_mrr(self, relevance_scores: List[float], threshold: float = 0.5) -> float:
        """Calculate Mean Reciprocal Rank."""
        
        for i, score in enumerate(relevance_scores):
            if score >= threshold:
                return 1.0 / (i + 1)
        
        return 0.0
    
    def _calculate_position_diversity(self, contexts: List[str]) -> float:
        """Calculate diversity based on position in ranking."""
        
        if len(contexts) < 2:
            return 1.0
        
        # Simple lexical diversity between consecutive contexts
        diversities = []
        for i in range(len(contexts) - 1):
            ctx1_words = set(contexts[i].lower().split())
            ctx2_words = set(contexts[i + 1].lower().split())
            
            intersection = len(ctx1_words.intersection(ctx2_words))
            union = len(ctx1_words.union(ctx2_words))
            
            diversity = 1.0 - (intersection / union if union > 0 else 0.0)
            diversities.append(diversity)
        
        return np.mean(diversities)
