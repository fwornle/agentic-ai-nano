import time
from typing import List, Dict
from interactive_rag import InteractiveRAG

class RAGEvaluator:
    """Basic evaluation metrics for RAG system."""
    
    def __init__(self, rag_system: InteractiveRAG):
        self.rag_system = rag_system
    
    def evaluate_response_time(self, questions: List[str]) -> Dict[str, float]:
        """Evaluate average response time."""
        times = []
        
        for question in questions:
            start_time = time.time()
            self.rag_system.rag_system.query(question)
            end_time = time.time()
            
            times.append(end_time - start_time)
        
        return {
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times)
        }
    
    def evaluate_retrieval_quality(self, test_questions: List[str]) -> Dict[str, float]:
        """Evaluate retrieval quality metrics."""
        total_confidence = 0
        total_sources = 0
        
        for question in test_questions:
            result = self.rag_system.rag_system.query(question)
            total_confidence += result["confidence"]
            total_sources += result["num_sources"]
        
        return {
            "average_confidence": total_confidence / len(test_questions),
            "average_sources_per_query": total_sources / len(test_questions)
        }

# Sample test questions
TEST_QUESTIONS = [
    "What is artificial intelligence?",
    "How does machine learning work?",
    "What are neural networks?",
    "What is natural language processing?",
    "How is AI used in healthcare?"
]

def run_evaluation():
    """Run basic RAG system evaluation."""
    rag = InteractiveRAG()
    
    # Load sample documents
    sample_sources = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning"
    ]
    rag.load_and_index_documents(sample_sources)
    
    # Run evaluation
    evaluator = RAGEvaluator(rag)
    
    print("Running RAG Performance Evaluation...")
    print("-" * 40)
    
    # Response time evaluation
    time_metrics = evaluator.evaluate_response_time(TEST_QUESTIONS)
    print(f"Average Response Time: {time_metrics['average_time']:.2f}s")
    print(f"Min Response Time: {time_metrics['min_time']:.2f}s")
    print(f"Max Response Time: {time_metrics['max_time']:.2f}s")
    
    # Quality evaluation
    quality_metrics = evaluator.evaluate_retrieval_quality(TEST_QUESTIONS)
    print(f"Average Confidence: {quality_metrics['average_confidence']:.3f}")
    print(f"Average Sources per Query: {quality_metrics['average_sources_per_query']:.1f}")

if __name__ == "__main__":
    run_evaluation()