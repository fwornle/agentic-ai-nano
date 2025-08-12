# LLM-as-a-Judge evaluation system
import numpy as np
from typing import List, Dict, Any, Optional

class LLMJudgeEvaluator:
    """Use LLM as a judge for RAG response evaluation."""
    
    def __init__(self, judge_llm, temperature: float = 0.1):
        self.judge_llm = judge_llm
        self.temperature = temperature
        
        # Evaluation prompts for different aspects
        self.evaluation_prompts = {
            'relevance': self._relevance_evaluation_prompt,
            'accuracy': self._accuracy_evaluation_prompt,
            'completeness': self._completeness_evaluation_prompt,
            'coherence': self._coherence_evaluation_prompt,
            'helpfulness': self._helpfulness_evaluation_prompt
        }
    
    def evaluate_response_quality(self, query: str, response: str,
                                contexts: List[str],
                                aspects: List[str] = None) -> Dict[str, Any]:
        """Evaluate response quality using LLM judge."""
        
        if aspects is None:
            aspects = ['relevance', 'accuracy', 'completeness', 'coherence']
        
        evaluation_results = {}
        detailed_feedback = {}
        
        for aspect in aspects:
            if aspect in self.evaluation_prompts:
                score, feedback = self._evaluate_aspect(
                    aspect, query, response, contexts
                )
                evaluation_results[aspect] = score
                detailed_feedback[aspect] = feedback
        
        # Calculate overall score
        overall_score = np.mean(list(evaluation_results.values()))
        
        return {
            'aspect_scores': evaluation_results,
            'overall_score': overall_score,
            'detailed_feedback': detailed_feedback,
            'evaluation_summary': self._generate_evaluation_summary(
                evaluation_results, detailed_feedback
            )
        }
    
    def _evaluate_aspect(self, aspect: str, query: str, response: str,
                        contexts: List[str]) -> tuple[float, str]:
        """Evaluate a specific aspect of the response."""
        
        prompt_generator = self.evaluation_prompts[aspect]
        evaluation_prompt = prompt_generator(query, response, contexts)
        
        try:
            # Get evaluation from LLM judge
            judge_response = self.judge_llm.predict(evaluation_prompt)
            
            # Parse score and feedback
            score, feedback = self._parse_judge_response(judge_response)
            
            return score, feedback
            
        except Exception as e:
            print(f"Error evaluating {aspect}: {e}")
            return 0.5, f"Error in {aspect} evaluation: {str(e)}"
    
    def _parse_judge_response(self, response: str) -> tuple[float, str]:
        """Parse LLM judge response to extract score and feedback."""
        
        lines = response.strip().split('\n')
        score = 3.0  # Default middle score
        feedback = response
        
        for line in lines:
            line = line.strip()
            if line.startswith('SCORE:'):
                try:
                    score_text = line.replace('SCORE:', '').strip()
                    score = float(score_text)
                    # Convert 1-5 scale to 0-1 scale
                    score = (score - 1) / 4.0
                except:
                    pass
            elif line.startswith('REASONING:'):
                # Extract reasoning as feedback
                reasoning_start = response.find('REASONING:')
                if reasoning_start != -1:
                    feedback = response[reasoning_start:].strip()
        
        return max(0.0, min(1.0, score)), feedback
    
    def _relevance_evaluation_prompt(self, query: str, response: str, 
                                   contexts: List[str]) -> str:
        """Generate prompt for relevance evaluation."""
        
        return f"""You are an expert evaluator assessing the relevance of AI-generated responses.

TASK: Evaluate how well the response addresses the given query.

QUERY: {query}

RESPONSE: {response}

EVALUATION CRITERIA:
1. Direct Address: Does the response directly answer what was asked?
2. Scope Alignment: Is the response appropriately scoped to the query?
3. Focus: Does the response stay focused on the main question?
4. Completeness: Does it address all parts of multi-part questions?

SCORING SCALE:
5 - Excellent: Response perfectly addresses the query with complete relevance
4 - Good: Response addresses the query well with minor irrelevant content
3 - Average: Response partially addresses the query but has some irrelevant parts
2 - Poor: Response marginally addresses the query with significant irrelevant content  
1 - Very Poor: Response barely addresses or completely misses the query

Provide your evaluation in this format:
SCORE: [1-5]
REASONING: [Detailed explanation of your scoring decision]
SUGGESTIONS: [How the response could be improved]
"""
    
    def _accuracy_evaluation_prompt(self, query: str, response: str,
                                  contexts: List[str]) -> str:
        """Generate prompt for accuracy evaluation."""
        
        contexts_text = '\n\n'.join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(contexts[:3])])
        
        return f"""You are an expert fact-checker evaluating the accuracy of AI responses.

TASK: Evaluate the factual accuracy of the response based on the provided contexts.

QUERY: {query}

RESPONSE: {response}

AVAILABLE CONTEXTS:
{contexts_text}

EVALUATION CRITERIA:
1. Factual Correctness: Are the facts stated in the response accurate?
2. Source Consistency: Does the response align with the provided contexts?
3. No Hallucinations: Does the response avoid making up information not in the contexts?
4. Proper Attribution: Are claims properly supported by the available information?

SCORING SCALE:
5 - Excellent: All information is accurate and well-supported by contexts
4 - Good: Mostly accurate with minor unsupported details
3 - Average: Generally accurate but contains some questionable claims
2 - Poor: Contains several inaccuracies or unsupported claims
1 - Very Poor: Contains significant inaccuracies or fabricated information

Provide your evaluation in this format:
SCORE: [1-5]
REASONING: [Detailed explanation focusing on specific factual claims]
INACCURACIES: [List any factual errors or unsupported claims]
SUGGESTIONS: [How accuracy could be improved]
"""
    
    def _completeness_evaluation_prompt(self, query: str, response: str,
                                      contexts: List[str]) -> str:
        """Generate prompt for completeness evaluation."""
        
        return f"""You are an expert evaluator assessing the completeness of AI-generated responses.

TASK: Evaluate how completely the response addresses all aspects of the query.

QUERY: {query}

RESPONSE: {response}

EVALUATION CRITERIA:
1. Coverage: Are all aspects of the question addressed?
2. Depth: Is sufficient detail provided for each aspect?
3. Thoroughness: Are important sub-questions or implications covered?
4. Balance: Is appropriate attention given to different parts of multi-part questions?

SCORING SCALE:
5 - Excellent: Response comprehensively addresses all aspects with appropriate depth
4 - Good: Response covers most aspects well but may miss minor details
3 - Average: Response addresses main aspects but lacks depth or misses some parts
2 - Poor: Response addresses some aspects but leaves significant gaps
1 - Very Poor: Response fails to address most aspects of the question

Provide your evaluation in this format:
SCORE: [1-5]
REASONING: [Detailed explanation of coverage and depth]
MISSING: [What aspects are not adequately addressed]
SUGGESTIONS: [How completeness could be improved]
"""
    
    def _coherence_evaluation_prompt(self, query: str, response: str,
                                   contexts: List[str]) -> str:
        """Generate prompt for coherence evaluation."""
        
        return f"""You are an expert evaluator assessing the coherence of AI-generated responses.

TASK: Evaluate the logical structure and flow of the response.

QUERY: {query}

RESPONSE: {response}

EVALUATION CRITERIA:
1. Logical Flow: Do ideas flow logically from one to the next?
2. Internal Consistency: Are there any contradictions within the response?
3. Clear Structure: Is the response well-organized and easy to follow?
4. Transitions: Are connections between different points clear?

SCORING SCALE:
5 - Excellent: Response is perfectly coherent with clear logical flow
4 - Good: Response is coherent with minor organizational issues
3 - Average: Response is mostly coherent but has some confusing parts
2 - Poor: Response has significant coherence issues or contradictions
1 - Very Poor: Response is incoherent or contradictory

Provide your evaluation in this format:
SCORE: [1-5]
REASONING: [Detailed explanation of coherence assessment]
ISSUES: [Any coherence problems identified]
SUGGESTIONS: [How coherence could be improved]
"""
    
    def _helpfulness_evaluation_prompt(self, query: str, response: str,
                                     contexts: List[str]) -> str:
        """Generate prompt for helpfulness evaluation."""
        
        return f"""You are an expert evaluator assessing the helpfulness of AI-generated responses.

TASK: Evaluate how helpful the response would be to someone with this query.

QUERY: {query}

RESPONSE: {response}

EVALUATION CRITERIA:
1. Practical Value: Does the response provide actionable or useful information?
2. Clarity: Is the response clear and understandable?
3. Appropriate Detail: Is the level of detail appropriate for the question?
4. User Intent: Does the response address the likely intent behind the query?

SCORING SCALE:
5 - Excellent: Response is extremely helpful and addresses user needs perfectly
4 - Good: Response is helpful with minor limitations
3 - Average: Response provides some help but could be more useful
2 - Poor: Response provides limited help or is confusing
1 - Very Poor: Response is unhelpful or potentially misleading

Provide your evaluation in this format:
SCORE: [1-5]
REASONING: [Detailed explanation of helpfulness assessment]
STRENGTHS: [What makes the response helpful]
WEAKNESSES: [How the response could be more helpful]
"""
    
    def _generate_evaluation_summary(self, scores: Dict[str, float], 
                                   feedback: Dict[str, str]) -> str:
        """Generate a summary of the evaluation results."""
        
        overall_score = np.mean(list(scores.values()))
        
        # Determine overall assessment
        if overall_score >= 0.8:
            assessment = "Excellent"
        elif overall_score >= 0.6:
            assessment = "Good"
        elif overall_score >= 0.4:
            assessment = "Average"
        elif overall_score >= 0.2:
            assessment = "Poor"
        else:
            assessment = "Very Poor"
        
        # Identify strengths and weaknesses
        strengths = [aspect for aspect, score in scores.items() if score >= 0.7]
        weaknesses = [aspect for aspect, score in scores.items() if score < 0.5]
        
        summary = f"Overall Assessment: {assessment} (Score: {overall_score:.2f})\n\n"
        
        if strengths:
            summary += f"Strengths: {', '.join(strengths)}\n"
        
        if weaknesses:
            summary += f"Areas for Improvement: {', '.join(weaknesses)}\n"
        
        return summary
