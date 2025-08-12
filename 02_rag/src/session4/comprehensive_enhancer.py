"""
Comprehensive Query Enhancement System

Integrates all query enhancement components into a unified pipeline.
"""

from typing import Dict, Any
from hyde_enhancer import HyDEQueryEnhancer
from query_expander import IntelligentQueryExpander
from multi_query_generator import MultiQueryGenerator
from context_optimizer import ContextWindowOptimizer
from prompt_engineer import RAGPromptEngineer, DynamicPromptAdapter


class ComprehensiveQueryEnhancer:
    """Complete query enhancement pipeline for RAG systems."""
    
    def __init__(self, llm_model, embedding_model, tokenizer):
        # Initialize components
        self.hyde_enhancer = HyDEQueryEnhancer(llm_model, embedding_model)
        self.query_expander = IntelligentQueryExpander(llm_model)
        self.multi_query_gen = MultiQueryGenerator(llm_model)
        self.context_optimizer = ContextWindowOptimizer(tokenizer)
        self.prompt_engineer = RAGPromptEngineer(llm_model)
        self.dynamic_adapter = DynamicPromptAdapter(llm_model)
        
    async def comprehensive_enhancement(self, query: str,
                                      vector_store,
                                      enhancement_config: Dict) -> Dict[str, Any]:
        """Run comprehensive query enhancement pipeline."""
        
        results = {'original_query': query}
        
        # Step 1: HyDE Enhancement
        if enhancement_config.get('use_hyde', True):
            hyde_result = self.hyde_enhancer.enhance_query_with_hyde(query)
            results['hyde_enhancement'] = hyde_result
        
        # Step 2: Query Expansion
        if enhancement_config.get('use_expansion', True):
            expansion_result = self.query_expander.expand_query(query)
            results['query_expansion'] = expansion_result
        
        # Step 3: Multi-Query Generation
        if enhancement_config.get('use_multi_query', True):
            multi_query_result = self.multi_query_gen.generate_multi_query_set(query)
            results['multi_query'] = multi_query_result
        
        # Step 4: Enhanced Retrieval
        enhanced_retrieval = await self._perform_enhanced_retrieval(
            results, vector_store, enhancement_config
        )
        results['enhanced_retrieval'] = enhanced_retrieval
        
        # Step 5: Context Optimization
        context_result = self.context_optimizer.optimize_context_window(
            query, enhanced_retrieval['combined_results']
        )
        results['optimized_context'] = context_result
        
        # Step 6: Dynamic Prompt Engineering
        prompt_result = self.dynamic_adapter.adapt_prompt_dynamically(
            query, context_result['optimized_context'], enhanced_retrieval
        )
        results['engineered_prompt'] = prompt_result
        
        return results

    async def _perform_enhanced_retrieval(self, enhancement_results: Dict,
                                        vector_store, config: Dict) -> Dict[str, Any]:
        """Perform retrieval using enhanced queries."""
        
        retrieval_results = {}
        all_results = []
        
        # Original query retrieval
        original_results = await vector_store.similarity_search(
            enhancement_results['original_query'], k=config.get('k', 10)
        )
        retrieval_results['original'] = original_results
        all_results.extend(original_results)
        
        # HyDE retrieval if available
        if 'hyde_enhancement' in enhancement_results:
            hyde_embedding = enhancement_results['hyde_enhancement']['enhanced_embedding']
            hyde_results = await vector_store.similarity_search_by_vector(
                hyde_embedding, k=config.get('k', 10)
            )
            retrieval_results['hyde'] = hyde_results
            all_results.extend(hyde_results)
        
        # Expanded query retrieval if available
        if 'query_expansion' in enhancement_results:
            expanded_query = enhancement_results['query_expansion']['expanded_query']
            expanded_results = await vector_store.similarity_search(
                expanded_query, k=config.get('k', 10)
            )
            retrieval_results['expanded'] = expanded_results
            all_results.extend(expanded_results)
        
        # Multi-query retrieval if available
        if 'multi_query' in enhancement_results:
            multi_results = []
            for variant in enhancement_results['multi_query']['query_variants'][:3]:  # Top 3
                variant_results = await vector_store.similarity_search(
                    variant, k=config.get('k', 5)
                )
                multi_results.extend(variant_results)
            retrieval_results['multi_query'] = multi_results
            all_results.extend(multi_results)
        
        # Deduplicate and rank combined results
        combined_results = self._deduplicate_and_rank_results(all_results)
        
        return {
            'individual_results': retrieval_results,
            'combined_results': combined_results,
            'total_unique_results': len(combined_results)
        }

    def _deduplicate_and_rank_results(self, all_results):
        """Deduplicate and rank combined retrieval results."""
        
        # Simple deduplication based on content hash
        seen_content = set()
        unique_results = []
        
        for result in all_results:
            content = result['document'].page_content
            content_hash = hash(content)
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
        
        # Sort by similarity score (assuming distance metric)
        unique_results.sort(key=lambda x: x.get('similarity_score', 1.0))
        
        return unique_results