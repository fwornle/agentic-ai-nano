"""
HyDE (Hypothetical Document Embeddings) Query Enhancer

Implements HyDE for semantic gap bridging through hypothetical document generation.
"""

from typing import List, Dict, Any, Optional
import numpy as np


class HyDEQueryEnhancer:
    """Hypothetical Document Embeddings for query enhancement."""
    
    def __init__(self, llm_model, embedding_model, temperature: float = 0.7):
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.temperature = temperature
        
        # Different HyDE templates for various query types
        self.hyde_templates = {
            'factual': self._factual_hyde_template,
            'procedural': self._procedural_hyde_template,
            'analytical': self._analytical_hyde_template,
            'creative': self._creative_hyde_template
        }
        
    def enhance_query_with_hyde(self, query: str, 
                               query_type: str = 'factual',
                               num_hypotheticals: int = 3) -> Dict[str, Any]:
        """Generate hypothetical documents for query enhancement."""
        
        print(f"Generating HyDE for query: {query[:100]}...")
        
        # Step 1: Classify query type if not provided
        if query_type == 'auto':
            query_type = self._classify_query_type(query)
        
        # Step 2: Generate hypothetical documents
        hypothetical_docs = self._generate_hypothetical_documents(
            query, query_type, num_hypotheticals
        )
        
        # Step 3: Create enhanced embeddings
        enhanced_embeddings = self._create_enhanced_embeddings(
            query, hypothetical_docs
        )
        
        # Step 4: Return comprehensive enhancement data
        return {
            'original_query': query,
            'query_type': query_type,
            'hypothetical_documents': hypothetical_docs,
            'enhanced_embedding': enhanced_embeddings['combined'],
            'original_embedding': enhanced_embeddings['original'],
            'hyde_embeddings': enhanced_embeddings['hyde_embeddings'],
            'confidence_score': self._calculate_enhancement_confidence(
                enhanced_embeddings
            )
        }

    def _classify_query_type(self, query: str) -> str:
        """Classify query type for appropriate HyDE template selection."""
        
        classification_prompt = f"""
        Classify the following query into one of these categories:
        1. factual - Questions seeking specific facts or information
        2. procedural - Questions asking how to do something or step-by-step processes
        3. analytical - Questions requiring analysis, comparison, or interpretation
        4. creative - Questions requiring creative or open-ended responses
        
        Query: {query}
        
        Return only the category name:
        """
        
        try:
            response = self.llm_model.predict(classification_prompt).strip().lower()
            if response in self.hyde_templates:
                return response
        except Exception as e:
            print(f"Classification error: {e}")
        
        # Default to factual
        return 'factual'

    def _factual_hyde_template(self, query: str) -> str:
        """Template for factual query types."""
        return f"""
        Write a detailed, informative document that comprehensively answers this question: {query}
        
        The document should:
        - Provide specific facts and data points
        - Include relevant context and background information
        - Use authoritative tone and precise language
        - Cover multiple aspects of the topic
        - Include examples where relevant
        
        Document:
        """
    
    def _procedural_hyde_template(self, query: str) -> str:
        """Template for procedural query types.""" 
        return f"""
        Write a detailed how-to guide that explains: {query}
        
        The guide should:
        - Provide step-by-step instructions
        - Include prerequisite requirements
        - Mention common pitfalls and how to avoid them
        - Explain the reasoning behind each step
        - Include tips for success
        
        Guide:
        """
    
    def _analytical_hyde_template(self, query: str) -> str:
        """Template for analytical query types."""
        return f"""
        Write an analytical document that thoroughly examines: {query}
        
        The analysis should:
        - Present multiple perspectives or approaches
        - Compare and contrast different options
        - Discuss pros and cons
        - Provide evidence-based reasoning
        - Draw insightful conclusions
        
        Analysis:
        """

    def _creative_hyde_template(self, query: str) -> str:
        """Template for creative query types."""
        return f"""
        Write a creative and comprehensive response that addresses: {query}
        
        The response should:
        - Explore multiple creative angles
        - Include innovative ideas and approaches
        - Provide inspirational content
        - Use engaging language and examples
        - Encourage further exploration
        
        Response:
        """

    def _generate_hypothetical_documents(self, query: str, 
                                       query_type: str, 
                                       num_docs: int) -> List[Dict]:
        """Generate multiple hypothetical documents with variations."""
        
        base_template = self.hyde_templates[query_type]
        hypothetical_docs = []
        
        for i in range(num_docs):
            # Add variation to temperature for diversity
            varied_temperature = self.temperature + (i * 0.1)
            varied_temperature = min(varied_temperature, 1.0)
            
            try:
                # Generate hypothetical document
                prompt = base_template(query)
                
                # Use varied temperature for diversity
                doc_text = self.llm_model.predict(
                    prompt, 
                    temperature=varied_temperature
                )
                
                hypothetical_docs.append({
                    'document': doc_text.strip(),
                    'temperature': varied_temperature,
                    'variation': i + 1,
                    'word_count': len(doc_text.split()),
                    'quality_score': self._assess_document_quality(doc_text, query)
                })
                
                print(f"Generated hypothetical document {i+1}/{num_docs}")
                
            except Exception as e:
                print(f"Error generating document {i+1}: {e}")
                continue
        
        # Sort by quality score
        hypothetical_docs.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return hypothetical_docs

    def _create_enhanced_embeddings(self, query: str, 
                                  hypothetical_docs: List[Dict]) -> Dict:
        """Create enhanced embeddings combining query and hypothetical docs."""
        
        # Original query embedding
        original_embedding = self.embedding_model.encode([query])[0]
        
        # Hypothetical document embeddings
        hyde_texts = [doc['document'] for doc in hypothetical_docs]
        hyde_embeddings = self.embedding_model.encode(hyde_texts)
        
        # Combine embeddings using weighted average
        weights = self._calculate_document_weights(hypothetical_docs)
        
        # Weighted combination
        weighted_hyde = np.average(hyde_embeddings, axis=0, weights=weights)
        
        # Combine original query with weighted hypotheticals
        # Give more weight to original query to preserve intent
        combined_embedding = (0.3 * original_embedding + 
                            0.7 * weighted_hyde)
        
        # Normalize the combined embedding
        combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)
        
        return {
            'original': original_embedding,
            'hyde_embeddings': hyde_embeddings,
            'weighted_hyde': weighted_hyde,
            'combined': combined_embedding,
            'weights': weights
        }
    
    def _calculate_document_weights(self, hypothetical_docs: List[Dict]) -> List[float]:
        """Calculate weights for hypothetical documents based on quality."""
        
        quality_scores = [doc['quality_score'] for doc in hypothetical_docs]
        
        # Softmax normalization for weights
        exp_scores = np.exp(np.array(quality_scores))
        weights = exp_scores / np.sum(exp_scores)
        
        return weights.tolist()

    def _assess_document_quality(self, doc_text: str, query: str) -> float:
        """Assess the quality of a generated hypothetical document."""
        
        # Simple heuristic-based quality assessment
        # Can be enhanced with more sophisticated methods
        
        # Length factor (not too short, not too long)
        word_count = len(doc_text.split())
        length_score = min(1.0, word_count / 200) * (1 - max(0, (word_count - 500) / 1000))
        
        # Keyword relevance (simple overlap check)
        query_words = set(query.lower().split())
        doc_words = set(doc_text.lower().split())
        relevance_score = len(query_words.intersection(doc_words)) / len(query_words)
        
        # Combine scores
        quality_score = 0.6 * length_score + 0.4 * relevance_score
        
        return min(1.0, max(0.0, quality_score))

    def _calculate_enhancement_confidence(self, enhanced_embeddings: Dict) -> float:
        """Calculate confidence score for the enhancement."""
        
        # Compare original vs enhanced embedding diversity
        original = enhanced_embeddings['original']
        combined = enhanced_embeddings['combined']
        
        # Cosine similarity between original and enhanced
        similarity = np.dot(original, combined) / (
            np.linalg.norm(original) * np.linalg.norm(combined)
        )
        
        # Confidence based on how much enhancement changed the embedding
        # while maintaining reasonable similarity
        enhancement_strength = 1 - similarity
        confidence = min(1.0, enhancement_strength * 2)  # Scale appropriately
        
        return confidence