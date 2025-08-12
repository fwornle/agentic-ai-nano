"""Cross-encoder reranking implementation."""

from sentence_transformers import CrossEncoder
from typing import List, Dict


class AdvancedReranker:
    """Cross-encoder based reranking for improved precision."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.cross_encoder = CrossEncoder(model_name)
        self.model_name = model_name
        print(f"Loaded cross-encoder model: {model_name}")
    
    def rerank_results(self, query: str, documents: List[Dict], 
                      top_k: int = 10) -> List[Dict]:
        """Rerank documents using cross-encoder scores."""
        
        if not documents:
            return []
        
        # Prepare query-document pairs
        pairs = []
        for doc_data in documents:
            doc_text = self._extract_text(doc_data)
            pairs.append([query, doc_text])
        
        # Get cross-encoder scores
        ce_scores = self.cross_encoder.predict(pairs)
        
        # Update documents with reranking scores
        for i, doc_data in enumerate(documents):
            doc_data['rerank_score'] = float(ce_scores[i])
            doc_data['original_rank'] = i + 1
        
        # Sort by cross-encoder scores
        reranked = sorted(
            documents,
            key=lambda x: x['rerank_score'],
            reverse=True
        )
        
        return reranked[:top_k]
    
    def _extract_text(self, doc_data: Dict) -> str:
        """Extract text content from document data."""
        if 'document' in doc_data:
            # Handle document object
            doc = doc_data['document']
            if hasattr(doc, 'page_content'):
                return doc.page_content
            elif hasattr(doc, 'content'):
                return doc.content
        elif 'content' in doc_data:
            return doc_data['content']
        elif 'text' in doc_data:
            return doc_data['text']
        else:
            return str(doc_data)