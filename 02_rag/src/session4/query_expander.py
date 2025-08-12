"""
Intelligent Query Expansion System

Implements multi-strategy query expansion using semantic, contextual, 
and domain-specific techniques.
"""

from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import wordnet
from collections import defaultdict


class IntelligentQueryExpander:
    """Advanced query expansion using multiple strategies."""
    
    def __init__(self, llm_model, domain_corpus: Optional[List[str]] = None):
        self.llm_model = llm_model
        self.domain_corpus = domain_corpus
        
        # Initialize expansion strategies
        self.expansion_strategies = {
            'synonym': self._synonym_expansion,
            'semantic': self._semantic_expansion, 
            'contextual': self._contextual_expansion,
            'domain_specific': self._domain_specific_expansion
        }
        
        # Domain-specific TF-IDF if corpus provided
        if domain_corpus:
            self.domain_tfidf = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            self.domain_tfidf.fit(domain_corpus)
    
    def expand_query(self, query: str, 
                    strategies: List[str] = ['semantic', 'contextual'],
                    max_expansions: int = 5) -> Dict[str, Any]:
        """Expand query using multiple strategies."""
        
        expansion_results = {}
        combined_expansions = set()
        
        # Apply each expansion strategy
        for strategy in strategies:
            if strategy in self.expansion_strategies:
                expansions = self.expansion_strategies[strategy](
                    query, max_expansions
                )
                expansion_results[strategy] = expansions
                combined_expansions.update(expansions)
        
        # Create final expanded query
        expanded_query = self._create_expanded_query(
            query, list(combined_expansions)
        )
        
        return {
            'original_query': query,
            'expansions_by_strategy': expansion_results,
            'all_expansions': list(combined_expansions),
            'expanded_query': expanded_query,
            'expansion_count': len(combined_expansions)
        }

    def _semantic_expansion(self, query: str, max_expansions: int) -> List[str]:
        """Generate semantic expansions using LLM understanding."""
        
        semantic_prompt = f"""
        Given this query, generate {max_expansions} semantically related terms or phrases that would help find relevant information:
        
        Query: {query}
        
        Requirements:
        1. Include synonyms and related concepts
        2. Add domain-specific terminology if applicable
        3. Include both broader and narrower terms
        4. Focus on terms likely to appear in relevant documents
        
        Return only the expanded terms, one per line:
        """
        
        try:
            response = self.llm_model.predict(semantic_prompt)
            expansions = [
                term.strip() 
                for term in response.strip().split('\n')
                if term.strip() and not term.strip().startswith(('-', '*', '•'))
            ]
            return expansions[:max_expansions]
            
        except Exception as e:
            print(f"Semantic expansion error: {e}")
            return []

    def _contextual_expansion(self, query: str, max_expansions: int) -> List[str]:
        """Generate contextual reformulations of the query."""
        
        reformulation_prompt = f"""
        Reformulate this query in {max_expansions} different ways that express the same information need:
        
        Original Query: {query}
        
        Create variations that:
        1. Use different phrasing and vocabulary
        2. Approach the question from different angles
        3. Include both specific and general formulations
        4. Maintain the original intent and meaning
        
        Reformulations:
        """
        
        try:
            response = self.llm_model.predict(reformulation_prompt)
            reformulations = [
                reform.strip().rstrip('.')
                for reform in response.strip().split('\n')
                if reform.strip() and ('?' in reform or len(reform.split()) > 3)
            ]
            return reformulations[:max_expansions]
            
        except Exception as e:
            print(f"Contextual expansion error: {e}")
            return []

    def _synonym_expansion(self, query: str, max_expansions: int) -> List[str]:
        """Generate synonym-based expansions using WordNet."""
        
        try:
            # Download required NLTK data if not present
            import nltk
            try:
                nltk.data.find('corpora/wordnet')
            except LookupError:
                nltk.download('wordnet', quiet=True)
            
            from nltk.corpus import wordnet
            
            query_words = query.lower().split()
            synonyms = set()
            
            for word in query_words:
                # Get synsets for each word
                for synset in wordnet.synsets(word):
                    # Get all lemma names for each synset
                    for lemma in synset.lemmas():
                        synonym = lemma.name().replace('_', ' ')
                        if synonym.lower() != word.lower():
                            synonyms.add(synonym)
            
            return list(synonyms)[:max_expansions]
            
        except Exception as e:
            print(f"Synonym expansion error: {e}")
            return []

    def _domain_specific_expansion(self, query: str, max_expansions: int) -> List[str]:
        """Generate domain-specific expansions using corpus analysis."""
        
        if not hasattr(self, 'domain_tfidf'):
            return []
        
        try:
            # Transform query using domain TF-IDF
            query_tfidf = self.domain_tfidf.transform([query])
            
            # Get feature names (terms)
            feature_names = self.domain_tfidf.get_feature_names_out()
            
            # Find most relevant terms
            scores = query_tfidf.toarray()[0]
            term_scores = list(zip(feature_names, scores))
            
            # Sort by relevance and filter non-zero scores
            relevant_terms = [
                term for term, score in sorted(term_scores, key=lambda x: x[1], reverse=True)
                if score > 0
            ]
            
            return relevant_terms[:max_expansions]
            
        except Exception as e:
            print(f"Domain expansion error: {e}")
            return []

    def _create_expanded_query(self, original_query: str, expansions: List[str]) -> str:
        """Create final expanded query combining original and expansions."""
        
        if not expansions:
            return original_query
        
        # Simple approach: combine original with top expansions
        # Can be enhanced with more sophisticated query construction
        expansion_terms = ' '.join(expansions[:3])  # Use top 3 expansions
        expanded_query = f"{original_query} {expansion_terms}"
        
        return expanded_query