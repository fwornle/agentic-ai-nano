"""Hybrid search implementation combining semantic and lexical retrieval."""

import re
import hashlib
from collections import Counter
from typing import List, Dict, Tuple, Set
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


class HybridSearchEngine:
    """Advanced hybrid search combining semantic and lexical retrieval."""
    
    def __init__(self, vector_store, documents: List[str]):
        self.vector_store = vector_store
        self.documents = documents
        
        # Initialize TF-IDF for lexical search
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams
            lowercase=True,
            token_pattern=r'\b[a-zA-Z]\w{2,}\b'  # Words with 3+ chars
        )
        
        # Fit TF-IDF on document corpus
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
        print(f"Built TF-IDF index for {len(documents)} documents")
    
    def _compute_bm25_scores(self, query: str, k1: float = 1.2, 
                           b: float = 0.75) -> np.ndarray:
        """Compute BM25 scores using optimized algorithm for RAG workloads.
        
        BM25 Formula: IDF * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))
        
        Where:
        - tf: Term frequency in document
        - df: Document frequency (documents containing term)  
        - dl: Document length
        - avgdl: Average document length
        - k1: Term frequency saturation parameter (1.2 optimal for most corpora)
        - b: Document length normalization (0.75 optimal for mixed-length documents)
        """
        
        # Tokenize query using same preprocessing as corpus
        query_tokens = self.tfidf_vectorizer.build_analyzer()(query.lower())
        
        # Pre-compute document statistics for efficiency
        doc_lengths = np.array([len(doc.split()) for doc in self.documents])
        avg_doc_length = np.mean(doc_lengths)
        
        # Initialize score accumulator
        scores = np.zeros(len(self.documents))
        
        # Process each query term
        for token in query_tokens:
            if token in self.tfidf_vectorizer.vocabulary_:
                # Retrieve term statistics from pre-built TF-IDF matrix
                term_idx = self.tfidf_vectorizer.vocabulary_[token]
                tf_scores = self.tfidf_matrix[:, term_idx].toarray().flatten()
                
                # Convert normalized TF-IDF back to raw term frequencies
                # This approximation works well when TF-IDF was built with sublinear_tf=False
                tf = tf_scores * len(self.documents)
                
                # Calculate document frequency and inverse document frequency
                df = np.sum(tf > 0)  # Number of documents containing this term
                if df > 0:
                    # BM25 IDF formula (with +0.5 smoothing to prevent negative values)
                    idf = np.log((len(self.documents) - df + 0.5) / (df + 0.5))
                    
                    # BM25 term frequency component with saturation
                    numerator = tf * (k1 + 1)
                    denominator = tf + k1 * (1 - b + b * doc_lengths / avg_doc_length)
                    
                    # Combine IDF and normalized TF for final BM25 score
                    scores += idf * (numerator / denominator)
        
        return scores
    
    def hybrid_search(self, query: str, top_k: int = 10, 
                     semantic_weight: float = 0.7,
                     lexical_weight: float = 0.3,
                     rerank: bool = True) -> List[Dict]:
        """Perform hybrid search with multiple fusion strategies."""
        
        # Step 1: Semantic search
        semantic_results = self.vector_store.similarity_search_with_scores(
            query, k=min(top_k * 3, 50)  # Retrieve more for reranking
        )
        
        # Step 2: Lexical search (BM25)
        lexical_scores = self._compute_bm25_scores(query)
        
        # Step 3: Combine scores using Reciprocal Rank Fusion (RRF)
        combined_results = self._reciprocal_rank_fusion(
            semantic_results, lexical_scores, k=60
        )
        
        # Step 4: Optional reranking
        if rerank:
            combined_results = self._cross_encoder_rerank(
                query, combined_results
            )
        
        return combined_results[:top_k]
    
    def _reciprocal_rank_fusion(self, semantic_results: List[Tuple], 
                               lexical_scores: np.ndarray, 
                               k: int = 60) -> List[Dict]:
        """Implement Reciprocal Rank Fusion for score combination."""
        
        # Create document score dictionary
        doc_scores = {}
        
        # Add semantic scores (convert similarity to rank)
        for rank, (doc, similarity_score) in enumerate(semantic_results):
            doc_id = doc.metadata.get('chunk_id', rank)
            doc_scores[doc_id] = {
                'document': doc,
                'semantic_rrf': 1 / (k + rank + 1),
                'semantic_score': similarity_score
            }
        
        # Add lexical scores (BM25 rankings)
        lexical_rankings = np.argsort(-lexical_scores)  # Descending order
        for rank, doc_idx in enumerate(lexical_rankings[:len(semantic_results)]):
            doc_id = doc_idx  # Assuming document index as ID
            
            if doc_id in doc_scores:
                doc_scores[doc_id]['lexical_rrf'] = 1 / (k + rank + 1)
                doc_scores[doc_id]['lexical_score'] = lexical_scores[doc_idx]
            else:
                # Create entry for lexical-only results
                doc_scores[doc_id] = {
                    'document': self.documents[doc_idx],
                    'semantic_rrf': 0,
                    'lexical_rrf': 1 / (k + rank + 1),
                    'semantic_score': 0,
                    'lexical_score': lexical_scores[doc_idx]
                }
        
        # Calculate final RRF scores
        for doc_id in doc_scores:
            semantic_rrf = doc_scores[doc_id].get('semantic_rrf', 0)
            lexical_rrf = doc_scores[doc_id].get('lexical_rrf', 0)
            doc_scores[doc_id]['final_score'] = semantic_rrf + lexical_rrf
        
        # Sort by final score
        sorted_results = sorted(
            doc_scores.values(),
            key=lambda x: x['final_score'],
            reverse=True
        )
        
        return sorted_results
    
    def _cross_encoder_rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Placeholder for cross-encoder reranking."""
        # This would integrate with the AdvancedReranker class
        return documents