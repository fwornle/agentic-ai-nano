"""
Context Window Optimization System

Optimizes context assembly for maximum information density and relevance.
"""

from typing import List, Dict, Any
import numpy as np


class ContextWindowOptimizer:
    """Optimize context assembly for maximum information density."""
    
    def __init__(self, llm_tokenizer, max_context_tokens: int = 4000):
        self.tokenizer = llm_tokenizer
        self.max_context_tokens = max_context_tokens
        
        # Context optimization strategies
        self.optimization_strategies = {
            'relevance_ranking': self._relevance_based_selection,
            'diversity_clustering': self._diversity_based_selection,
            'hierarchical_summary': self._hierarchical_summarization,
            'semantic_compression': self._semantic_compression
        }
    
    def optimize_context_window(self, query: str, 
                               retrieved_chunks: List[Dict],
                               strategy: str = 'relevance_ranking') -> Dict[str, Any]:
        """Optimize context window using specified strategy."""
        
        # Calculate available token budget
        query_tokens = len(self.tokenizer.encode(query))
        available_tokens = self.max_context_tokens - query_tokens - 200  # Buffer
        
        # Apply optimization strategy
        optimized_context = self.optimization_strategies[strategy](
            query, retrieved_chunks, available_tokens
        )
        
        return {
            'optimized_context': optimized_context['context'],
            'selected_chunks': optimized_context['chunks'],
            'context_tokens': optimized_context['token_count'],
            'efficiency_score': optimized_context['efficiency'],
            'strategy_used': strategy,
            'original_chunk_count': len(retrieved_chunks)
        }

    def _relevance_based_selection(self, query: str, chunks: List[Dict], 
                                 token_budget: int) -> Dict[str, Any]:
        """Select chunks based on relevance scores and token efficiency."""
        
        # Calculate relevance scores and token costs
        chunk_analysis = []
        for i, chunk in enumerate(chunks):
            content = chunk['document'].page_content
            tokens = len(self.tokenizer.encode(content))
            relevance = 1 - chunk.get('similarity_score', 0.5)  # Convert distance to similarity
            
            # Calculate efficiency: relevance per token
            efficiency = relevance / tokens if tokens > 0 else 0
            
            chunk_analysis.append({
                'index': i,
                'content': content,
                'tokens': tokens,
                'relevance': relevance,
                'efficiency': efficiency,
                'metadata': chunk.get('metadata', {})
            })
        
        # Sort by efficiency (relevance per token)
        chunk_analysis.sort(key=lambda x: x['efficiency'], reverse=True)
        
        # Select chunks within token budget
        selected_chunks = []
        total_tokens = 0
        
        for chunk_data in chunk_analysis:
            if total_tokens + chunk_data['tokens'] <= token_budget:
                selected_chunks.append(chunk_data)
                total_tokens += chunk_data['tokens']
            else:
                break
        
        # Assemble context
        context_parts = []
        for chunk_data in selected_chunks:
            source = chunk_data['metadata'].get('source', 'Unknown')
            context_parts.append(f"[Source: {source}]\n{chunk_data['content']}")
        
        final_context = '\n\n'.join(context_parts)
        
        return {
            'context': final_context,
            'chunks': selected_chunks,
            'token_count': total_tokens,
            'efficiency': np.mean([c['efficiency'] for c in selected_chunks])
        }

    def _diversity_based_selection(self, query: str, chunks: List[Dict],
                                 token_budget: int) -> Dict[str, Any]:
        """Select chunks based on diversity and relevance balance."""
        
        # This would implement diversity-based selection
        # For now, fallback to relevance-based selection
        return self._relevance_based_selection(query, chunks, token_budget)

    def _hierarchical_summarization(self, query: str, chunks: List[Dict],
                                  token_budget: int) -> Dict[str, Any]:
        """Create hierarchical summaries when context exceeds budget."""
        
        # Group chunks by source/topic
        chunk_groups = self._group_chunks_by_source(chunks)
        
        summarized_chunks = []
        total_tokens = 0
        
        for group_key, group_chunks in chunk_groups.items():
            # Calculate total tokens for this group
            group_content = '\n'.join([
                chunk['document'].page_content for chunk in group_chunks
            ])
            group_tokens = len(self.tokenizer.encode(group_content))
            
            if group_tokens > token_budget // 4:  # Group too large, summarize
                summary = self._summarize_chunk_group(query, group_chunks)
                summary_tokens = len(self.tokenizer.encode(summary))
                
                if total_tokens + summary_tokens <= token_budget:
                    summarized_chunks.append({
                        'content': summary,
                        'tokens': summary_tokens,
                        'type': 'summary',
                        'source_count': len(group_chunks),
                        'group_key': group_key
                    })
                    total_tokens += summary_tokens
            else:
                # Use original chunks if they fit
                for chunk in group_chunks:
                    content = chunk['document'].page_content
                    chunk_tokens = len(self.tokenizer.encode(content))
                    
                    if total_tokens + chunk_tokens <= token_budget:
                        summarized_chunks.append({
                            'content': content,
                            'tokens': chunk_tokens,
                            'type': 'original',
                            'group_key': group_key,
                            'metadata': chunk.get('metadata', {})
                        })
                        total_tokens += chunk_tokens
        
        # Assemble final context
        context_parts = []
        for chunk in summarized_chunks:
            if chunk['type'] == 'summary':
                context_parts.append(f"[Summary from {chunk['source_count']} sources]\n{chunk['content']}")
            else:
                source = chunk['metadata'].get('source', chunk['group_key'])
                context_parts.append(f"[Source: {source}]\n{chunk['content']}")
        
        final_context = '\n\n'.join(context_parts)
        
        return {
            'context': final_context,
            'chunks': summarized_chunks,
            'token_count': total_tokens,
            'efficiency': total_tokens / token_budget
        }

    def _semantic_compression(self, query: str, chunks: List[Dict],
                            token_budget: int) -> Dict[str, Any]:
        """Compress context using semantic understanding."""
        
        # This would implement semantic compression
        # For now, fallback to relevance-based selection
        return self._relevance_based_selection(query, chunks, token_budget)

    def _group_chunks_by_source(self, chunks: List[Dict]) -> Dict[str, List[Dict]]:
        """Group chunks by their source document."""
        
        groups = {}
        for chunk in chunks:
            source = chunk.get('metadata', {}).get('source', 'unknown')
            if source not in groups:
                groups[source] = []
            groups[source].append(chunk)
        
        return groups

    def _summarize_chunk_group(self, query: str, group_chunks: List[Dict]) -> str:
        """Summarize a group of chunks related to the query."""
        
        # Simple summarization - concatenate key sentences
        # In a real implementation, this would use an LLM for summarization
        
        combined_content = '\n'.join([
            chunk['document'].page_content for chunk in group_chunks
        ])
        
        # Simple extractive summarization - take first sentence from each chunk
        sentences = []
        for chunk in group_chunks:
            content = chunk['document'].page_content
            first_sentence = content.split('.')[0] + '.'
            sentences.append(first_sentence)
        
        summary = ' '.join(sentences)
        return summary[:500]  # Limit summary length