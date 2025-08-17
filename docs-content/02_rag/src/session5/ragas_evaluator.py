# RAGAS integration for standardized evaluation
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    context_relevancy,
    answer_correctness,
    answer_similarity
)
from datasets import Dataset
from typing import List, Dict, Any, Optional

class RAGASEvaluator:
    """RAGAS-based evaluation system."""
    
    def __init__(self, llm_model, embedding_model):
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        
        # Configure RAGAS metrics
        self.metrics = [
            faithfulness,           # Factual consistency
            answer_relevancy,       # Answer relevance to question
            context_precision,      # Precision of retrieved context
            context_recall,         # Recall of retrieved context
            context_relevancy,      # Relevance of context to question
            answer_correctness,     # Correctness compared to ground truth
            answer_similarity       # Semantic similarity to ground truth
        ]
        
        # Initialize with models
        for metric in self.metrics:
            if hasattr(metric, 'init'):
                metric.init(self.llm_model, self.embedding_model)
    
    def evaluate_with_ragas(self, rag_results: List[Dict],
                           include_ground_truth: bool = True) -> Dict[str, Any]:
        """Evaluate using RAGAS framework."""
        
        # Prepare dataset in RAGAS format
        dataset_dict = self._prepare_ragas_dataset(rag_results, include_ground_truth)
        dataset = Dataset.from_dict(dataset_dict)
        
        # Select metrics based on available data
        selected_metrics = self._select_metrics(include_ground_truth)
        
        print(f"Running RAGAS evaluation with {len(selected_metrics)} metrics...")
        
        # Run evaluation
        ragas_results = evaluate(
            dataset=dataset,
            metrics=selected_metrics
        )
        
        return {
            'ragas_scores': ragas_results,
            'metric_descriptions': self._get_metric_descriptions(),
            'dataset_size': len(rag_results),
            'evaluation_summary': self._summarize_ragas_results(ragas_results)
        }
    
    def _prepare_ragas_dataset(self, rag_results: List[Dict], 
                              include_ground_truth: bool) -> Dict[str, List]:
        """Prepare dataset in RAGAS format."""
        
        dataset_dict = {
            'question': [],
            'answer': [],
            'contexts': [],
            'ground_truths': [] if include_ground_truth else None
        }
        
        for result in rag_results:
            dataset_dict['question'].append(result['query'])
            dataset_dict['answer'].append(result['generated_answer'])
            
            # Format contexts as list of strings
            contexts = []
            if 'retrieved_contexts' in result:
                contexts = [
                    ctx if isinstance(ctx, str) else ctx['content']
                    for ctx in result['retrieved_contexts']
                ]
            dataset_dict['contexts'].append(contexts)
            
            # Add ground truth if available
            if include_ground_truth and 'ground_truth' in result:
                if dataset_dict['ground_truths'] is not None:
                    # Ground truth should be a list
                    gt = result['ground_truth']
                    if isinstance(gt, str):
                        gt = [gt]
                    dataset_dict['ground_truths'].append(gt)
        
        # Remove ground_truths if not using
        if not include_ground_truth:
            del dataset_dict['ground_truths']
        
        return dataset_dict
    
    def _select_metrics(self, include_ground_truth: bool) -> List:
        """Select appropriate metrics based on available data."""
        if include_ground_truth:
            return self.metrics
        else:
            # Return metrics that don't require ground truth
            return [
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
                context_relevancy
            ]
    
    def _get_metric_descriptions(self) -> Dict[str, str]:
        """Get descriptions of RAGAS metrics."""
        return {
            'faithfulness': 'Measures factual consistency of the answer with given context',
            'answer_relevancy': 'Measures how relevant the answer is to the question',
            'context_precision': 'Measures precision of retrieved context',
            'context_recall': 'Measures recall of retrieved context',
            'context_relevancy': 'Measures relevance of context to the question',
            'answer_correctness': 'Measures correctness of answer compared to ground truth',
            'answer_similarity': 'Measures semantic similarity to ground truth'
        }
    
    def _summarize_ragas_results(self, ragas_results) -> Dict[str, Any]:
        """Summarize RAGAS evaluation results."""
        # Placeholder implementation
        return {
            'summary': 'RAGAS evaluation completed',
            'overall_score': 0.0,
            'metric_breakdown': {}
        }
