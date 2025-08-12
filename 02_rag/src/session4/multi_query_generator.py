"""
Multi-Query Generation System

Generates multiple query perspectives for comprehensive retrieval coverage.
"""

from typing import List, Dict, Any


class MultiQueryGenerator:
    """Generate multiple query perspectives for comprehensive retrieval."""
    
    def __init__(self, llm_model):
        self.llm_model = llm_model
        
        self.query_perspectives = {
            'decomposition': self._decompose_complex_query,
            'specificity_levels': self._generate_specificity_variants,
            'temporal_variants': self._generate_temporal_variants,
            'perspective_shifts': self._generate_perspective_variants,
            'domain_focused': self._generate_domain_variants
        }
    
    def generate_multi_query_set(self, query: str, 
                               perspectives: List[str] = None,
                               total_queries: int = 8) -> Dict[str, Any]:
        """Generate comprehensive query set from multiple perspectives."""
        
        if perspectives is None:
            perspectives = ['decomposition', 'specificity_levels', 'perspective_shifts']
        
        all_queries = {'original': query}
        generation_metadata = {}
        
        # Distribute query generation across perspectives
        queries_per_perspective = total_queries // len(perspectives)
        remaining_queries = total_queries % len(perspectives)
        
        for i, perspective in enumerate(perspectives):
            num_queries = queries_per_perspective
            if i < remaining_queries:
                num_queries += 1
                
            generated = self.query_perspectives[perspective](query, num_queries)
            all_queries[perspective] = generated
            generation_metadata[perspective] = {
                'count': len(generated),
                'method': perspective
            }
        
        # Flatten and deduplicate
        flattened_queries = self._flatten_and_deduplicate(all_queries)
        
        return {
            'original_query': query,
            'query_variants': flattened_queries,
            'queries_by_perspective': all_queries,
            'generation_metadata': generation_metadata,
            'total_variants': len(flattened_queries)
        }

    def _decompose_complex_query(self, query: str, num_queries: int) -> List[str]:
        """Decompose complex queries into simpler sub-questions."""
        
        decomposition_prompt = f"""
        Break down this complex query into {num_queries} simpler, focused sub-questions that together would fully answer the original question:
        
        Complex Query: {query}
        
        Requirements:
        1. Each sub-question should be independently searchable
        2. Sub-questions should cover different aspects of the main query
        3. Avoid redundancy between sub-questions
        4. Maintain logical flow and completeness
        
        Sub-questions:
        """
        
        try:
            response = self.llm_model.predict(decomposition_prompt)
            sub_questions = [
                q.strip().rstrip('?') + '?'
                for q in response.strip().split('\n')
                if q.strip() and ('?' in q or len(q.split()) > 3)
            ]
            
            # Ensure we have question marks
            sub_questions = [
                q if q.endswith('?') else q + '?'
                for q in sub_questions
            ]
            
            return sub_questions[:num_queries]
            
        except Exception as e:
            print(f"Decomposition error: {e}")
            return []

    def _generate_specificity_variants(self, query: str, num_queries: int) -> List[str]:
        """Generate queries at different levels of specificity."""
        
        specificity_prompt = f"""
        Generate {num_queries} variants of this query at different levels of specificity:
        
        Original Query: {query}
        
        Create variants that range from:
        1. Very broad/general versions
        2. Medium specificity versions  
        3. Very specific/detailed versions
        
        Each variant should maintain the core intent but adjust the scope:
        """
        
        try:
            response = self.llm_model.predict(specificity_prompt)
            variants = [
                variant.strip()
                for variant in response.strip().split('\n')
                if variant.strip() and len(variant.split()) > 2
            ]
            
            return variants[:num_queries]
            
        except Exception as e:
            print(f"Specificity variant error: {e}")
            return []

    def _generate_temporal_variants(self, query: str, num_queries: int) -> List[str]:
        """Generate temporal variations of the query."""
        
        temporal_prompt = f"""
        Generate {num_queries} temporal variants of this query:
        
        Original Query: {query}
        
        Create variants that focus on different time perspectives:
        1. Historical context versions
        2. Current state versions
        3. Future trend versions
        4. Evolution over time versions
        
        Temporal variants:
        """
        
        try:
            response = self.llm_model.predict(temporal_prompt)
            variants = [
                variant.strip()
                for variant in response.strip().split('\n')
                if variant.strip() and len(variant.split()) > 2
            ]
            
            return variants[:num_queries]
            
        except Exception as e:
            print(f"Temporal variant error: {e}")
            return []

    def _generate_perspective_variants(self, query: str, num_queries: int) -> List[str]:
        """Generate queries from different perspectives or viewpoints."""
        
        perspective_prompt = f"""
        Generate {num_queries} variants of this query from different perspectives:
        
        Original Query: {query}
        
        Create variants that approach the topic from different angles:
        1. Technical/expert perspective
        2. Beginner/layperson perspective  
        3. Business/practical perspective
        4. Academic/research perspective
        
        Perspective variants:
        """
        
        try:
            response = self.llm_model.predict(perspective_prompt)
            variants = [
                variant.strip()
                for variant in response.strip().split('\n')
                if variant.strip() and len(variant.split()) > 2
            ]
            
            return variants[:num_queries]
            
        except Exception as e:
            print(f"Perspective variant error: {e}")
            return []

    def _generate_domain_variants(self, query: str, num_queries: int) -> List[str]:
        """Generate domain-specific variants of the query."""
        
        domain_prompt = f"""
        Generate {num_queries} domain-specific variants of this query:
        
        Original Query: {query}
        
        Create variants that focus on different domain aspects:
        1. Technical implementation details
        2. Business/commercial applications
        3. Academic/theoretical aspects
        4. Practical use cases
        
        Domain variants:
        """
        
        try:
            response = self.llm_model.predict(domain_prompt)
            variants = [
                variant.strip()
                for variant in response.strip().split('\n')
                if variant.strip() and len(variant.split()) > 2
            ]
            
            return variants[:num_queries]
            
        except Exception as e:
            print(f"Domain variant error: {e}")
            return []

    def _flatten_and_deduplicate(self, all_queries: Dict[str, Any]) -> List[str]:
        """Flatten query dictionary and remove duplicates."""
        
        flattened = []
        seen = set()
        
        for key, queries in all_queries.items():
            if key == 'original':
                if isinstance(queries, str):
                    queries = [queries]
            
            if isinstance(queries, list):
                for query in queries:
                    query_lower = query.lower().strip()
                    if query_lower not in seen:
                        seen.add(query_lower)
                        flattened.append(query)
        
        return flattened