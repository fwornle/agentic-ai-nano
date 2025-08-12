# Ensemble RAG system with multiple models and strategies
from typing import Dict, Any, List, Callable
import asyncio
import time
import numpy as np


class EnsembleRAGSystem:
    """Ensemble RAG system combining multiple models and strategies."""
    
    def __init__(self, rag_systems: Dict[str, Any], ensemble_config: Dict):
        self.rag_systems = rag_systems
        self.ensemble_config = ensemble_config
        
        # Ensemble strategies
        self.ensemble_methods = {
            'voting': self._voting_ensemble,
            'weighted_average': self._weighted_average_ensemble,
            'learned_combination': self._learned_combination_ensemble,
            'cascading': self._cascading_ensemble,
            'adaptive_selection': self._adaptive_selection_ensemble
        }
        
        # Performance tracking for adaptive weighting
        self.system_performance = {name: {'correct': 0, 'total': 0} for name in rag_systems.keys()}
        
    async def ensemble_generate(self, query: str, 
                              ensemble_config: Dict = None) -> Dict[str, Any]:
        """Generate response using ensemble of RAG systems."""
        
        config = ensemble_config or self.ensemble_config
        ensemble_method = config.get('method', 'weighted_average')
        
        print(f"Ensemble RAG generation using {ensemble_method}...")
        
        # Generate responses from all systems
        system_responses = await self._generate_all_system_responses(query, config)
        
        # Apply ensemble method
        ensemble_response = await self.ensemble_methods[ensemble_method](
            query, system_responses, config
        )
        
        # Calculate ensemble confidence
        ensemble_confidence = self._calculate_ensemble_confidence(
            system_responses, ensemble_response
        )
        
        return {
            'query': query,
            'system_responses': system_responses,
            'ensemble_response': ensemble_response,
            'ensemble_confidence': ensemble_confidence,
            'ensemble_metadata': {
                'method': ensemble_method,
                'systems_used': len(system_responses),
                'systems_agreed': self._count_system_agreement(system_responses),
                'confidence_variance': self._calculate_confidence_variance(system_responses)
            }
        }
    
    async def _generate_all_system_responses(self, query: str, 
                                           config: Dict) -> Dict[str, Dict]:
        """Generate responses from all RAG systems."""
        
        system_responses = {}
        
        # Generate responses concurrently for efficiency
        tasks = []
        for system_name, rag_system in self.rag_systems.items():
            task = self._generate_single_system_response(system_name, rag_system, query)
            tasks.append((system_name, task))
        
        # Collect results
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for (system_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                system_responses[system_name] = {
                    'success': False,
                    'error': str(result),
                    'response': '',
                    'confidence': 0.0
                }
            else:
                system_responses[system_name] = result
        
        return system_responses
    
    async def _generate_single_system_response(self, system_name: str, 
                                             rag_system: Any, query: str) -> Dict[str, Any]:
        """Generate response from a single RAG system."""
        
        try:
            start_time = time.time()
            
            # Generate response from the system
            if hasattr(rag_system, 'generate_response'):
                response = await rag_system.generate_response(query)
            else:
                # Fallback for different system interfaces
                response = await rag_system.query(query)
            
            response_time = time.time() - start_time
            
            # Extract confidence if available
            confidence = self._extract_confidence(response)
            
            return {
                'success': True,
                'response': self._extract_response_text(response),
                'confidence': confidence,
                'response_time': response_time,
                'sources': self._extract_sources(response),
                'system_name': system_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': '',
                'confidence': 0.0,
                'system_name': system_name
            }
    
    async def _weighted_average_ensemble(self, query: str, 
                                       system_responses: Dict[str, Dict],
                                       config: Dict) -> Dict[str, Any]:
        """Combine responses using weighted averaging based on system performance."""
        
        # Calculate dynamic weights based on performance and confidence
        system_weights = self._calculate_dynamic_weights(system_responses, config)
        
        # Extract responses and confidences
        responses = []
        confidences = []
        weights = []
        
        for system_name, response_data in system_responses.items():
            if response_data.get('success', False):
                responses.append(response_data['response'])
                confidences.append(response_data.get('confidence', 0.5))
                weights.append(system_weights.get(system_name, 0.1))
        
        if not responses:
            return {
                'response': "No successful responses from ensemble systems.",
                'method': 'weighted_average',
                'success': False
            }
        
        # Generate ensemble response through weighted synthesis
        synthesis_prompt = f"""
        Synthesize these responses into a comprehensive answer, giving more weight to higher-confidence responses:
        
        Query: {query}
        
        Responses with weights and confidences:
        {self._format_weighted_responses(responses, weights, confidences)}
        
        Create a synthesized response that:
        1. Incorporates the most reliable information (higher weights/confidence)
        2. Resolves any contradictions by favoring more confident responses
        3. Combines complementary information from different sources
        4. Maintains accuracy and coherence
        
        Synthesized Response:
        """
        
        try:
            ensemble_response = await self._async_llm_predict(
                synthesis_prompt, temperature=0.2
            )
            
            # Calculate overall confidence as weighted average
            overall_confidence = sum(c * w for c, w in zip(confidences, weights)) / sum(weights)
            
            return {
                'response': ensemble_response,
                'method': 'weighted_average',
                'success': True,
                'confidence': overall_confidence,
                'system_weights': system_weights,
                'component_responses': len(responses)
            }
            
        except Exception as e:
            print(f"Ensemble synthesis error: {e}")
            # Fallback to highest confidence response
            best_idx = max(range(len(confidences)), key=lambda i: confidences[i])
            return {
                'response': responses[best_idx],
                'method': 'weighted_average_fallback',
                'success': True,
                'confidence': confidences[best_idx],
                'fallback_reason': str(e)
            }
    
    async def _voting_ensemble(self, query: str, system_responses: Dict[str, Dict],
                             config: Dict) -> Dict[str, Any]:
        """Simple voting ensemble method."""
        
        successful_responses = [
            resp for resp in system_responses.values() 
            if resp.get('success', False)
        ]
        
        if not successful_responses:
            return {
                'response': "No successful responses from ensemble systems.",
                'method': 'voting',
                'success': False
            }
        
        # Simple majority vote based on highest confidence
        best_response = max(successful_responses, key=lambda x: x.get('confidence', 0))
        
        return {
            'response': best_response['response'],
            'method': 'voting',
            'success': True,
            'confidence': best_response['confidence'],
            'votes': len(successful_responses)
        }
    
    def _calculate_dynamic_weights(self, system_responses: Dict[str, Dict], 
                                 config: Dict) -> Dict[str, float]:
        """Calculate dynamic weights for each system based on performance and confidence."""
        
        weights = {}
        total_weight = 0
        
        for system_name, response_data in system_responses.items():
            if not response_data.get('success', False):
                weights[system_name] = 0.0
                continue
            
            # Base weight from historical performance
            performance_data = self.system_performance.get(system_name, {'correct': 1, 'total': 2})
            performance_ratio = performance_data['correct'] / max(performance_data['total'], 1)
            
            # Current confidence
            current_confidence = response_data.get('confidence', 0.5)
            
            # Response time factor (faster is better, but cap the benefit)
            response_time = response_data.get('response_time', 1.0)
            time_factor = min(2.0, 1.0 / max(response_time, 0.1))
            
            # Combined weight
            weight = performance_ratio * current_confidence * time_factor
            weights[system_name] = weight
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            for system_name in weights:
                weights[system_name] /= total_weight
        else:
            # Equal weights if no valid responses
            equal_weight = 1.0 / len(system_responses)
            weights = {name: equal_weight for name in system_responses.keys()}
        
        return weights
    
    def _format_weighted_responses(self, responses: List[str], weights: List[float], 
                                 confidences: List[float]) -> str:
        """Format responses with their weights and confidences for synthesis."""
        
        formatted = []
        for i, (response, weight, confidence) in enumerate(zip(responses, weights, confidences)):
            formatted.append(
                f"Response {i+1} (Weight: {weight:.2f}, Confidence: {confidence:.2f}):\n{response}\n"
            )
        
        return "\n".join(formatted)
    
    def _calculate_ensemble_confidence(self, system_responses: Dict[str, Dict], 
                                     ensemble_response: Dict[str, Any]) -> float:
        """Calculate confidence for the ensemble response."""
        
        successful_responses = [
            resp for resp in system_responses.values() 
            if resp.get('success', False)
        ]
        
        if not successful_responses:
            return 0.0
        
        # Average confidence of successful systems
        avg_confidence = sum(resp.get('confidence', 0) for resp in successful_responses) / len(successful_responses)
        
        # Boost confidence if multiple systems agree
        agreement_bonus = min(0.1 * len(successful_responses), 0.3)
        
        return min(avg_confidence + agreement_bonus, 1.0)
    
    def _count_system_agreement(self, system_responses: Dict[str, Dict]) -> int:
        """Count how many systems provided successful responses."""
        return len([resp for resp in system_responses.values() if resp.get('success', False)])
    
    def _calculate_confidence_variance(self, system_responses: Dict[str, Dict]) -> float:
        """Calculate variance in confidence scores across systems."""
        
        confidences = [
            resp.get('confidence', 0) for resp in system_responses.values() 
            if resp.get('success', False)
        ]
        
        if len(confidences) < 2:
            return 0.0
        
        return float(np.var(confidences))
    
    def _extract_confidence(self, response) -> float:
        """Extract confidence score from response."""
        if isinstance(response, dict) and 'confidence' in response:
            return response['confidence']
        return 0.7  # Default confidence
    
    def _extract_response_text(self, response) -> str:
        """Extract response text from response object."""
        if isinstance(response, dict):
            return response.get('response', response.get('text', str(response)))
        return str(response)
    
    def _extract_sources(self, response) -> List[str]:
        """Extract sources from response object."""
        if isinstance(response, dict) and 'sources' in response:
            return response['sources']
        return []
    
    # Placeholder methods for other ensemble strategies
    async def _learned_combination_ensemble(self, query: str, system_responses: Dict[str, Dict],
                                          config: Dict) -> Dict[str, Any]:
        """Learned combination ensemble method."""
        # Would use a trained model to combine responses
        return await self._weighted_average_ensemble(query, system_responses, config)
    
    async def _cascading_ensemble(self, query: str, system_responses: Dict[str, Dict],
                                config: Dict) -> Dict[str, Any]:
        """Cascading ensemble method."""
        # Would use systems in order, stopping when confidence threshold is met
        return await self._voting_ensemble(query, system_responses, config)
    
    async def _adaptive_selection_ensemble(self, query: str, system_responses: Dict[str, Dict],
                                         config: Dict) -> Dict[str, Any]:
        """Adaptive selection ensemble method."""
        # Would adaptively select the best system based on query characteristics
        return await self._weighted_average_ensemble(query, system_responses, config)
    
    async def _async_llm_predict(self, prompt: str, temperature: float = 0.1):
        """Async LLM prediction - placeholder implementation."""
        # In a real implementation, this would call your LLM
        return "Synthesized ensemble response based on multiple systems"