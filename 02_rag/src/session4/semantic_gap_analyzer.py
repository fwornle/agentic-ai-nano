"""
Semantic Gap Analyzer

Analyzes and demonstrates semantic gaps in retrieval systems.
"""

from typing import List, Dict
import numpy as np


class SemanticGapAnalyzer:
    """Analyze and demonstrate semantic gaps in retrieval."""
    
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
    
    def analyze_query_document_gap(self, query: str, documents: List[str]) -> Dict:
        """Analyze semantic gaps between queries and documents."""
        
        # Embed query and documents
        query_embedding = self.embedding_model.encode([query])
        doc_embeddings = self.embedding_model.encode(documents)
        
        # Calculate similarities
        similarities = []
        for doc_emb in doc_embeddings:
            similarity = np.dot(query_embedding[0], doc_emb) / (
                np.linalg.norm(query_embedding[0]) * np.linalg.norm(doc_emb)
            )
            similarities.append(similarity)
        
        return {
            'query': query,
            'avg_similarity': np.mean(similarities),
            'max_similarity': np.max(similarities),
            'min_similarity': np.min(similarities),
            'gap_analysis': self._analyze_gap(query, documents, similarities)
        }
    
    def _analyze_gap(self, query: str, documents: List[str], similarities: List[float]) -> Dict:
        """Analyze the semantic gap characteristics."""
        
        # Simple gap analysis - can be enhanced with more sophisticated metrics
        gap_size = 1.0 - np.mean(similarities)
        consistency = 1.0 - np.std(similarities)
        
        return {
            'gap_size': gap_size,
            'consistency': consistency,
            'problematic_docs': [
                {'doc_idx': i, 'similarity': sim} 
                for i, sim in enumerate(similarities) 
                if sim < 0.5
            ]
        }