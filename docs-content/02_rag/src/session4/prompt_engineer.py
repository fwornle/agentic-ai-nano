"""
Advanced Prompt Engineering for RAG Systems

Implements context-aware prompt templates and dynamic prompt adaptation.
"""

from typing import List, Dict, Any


class RAGPromptEngineer:
    """Advanced prompt engineering specifically for RAG systems."""
    
    def __init__(self, llm_model):
        self.llm_model = llm_model
        
        # Domain-specific prompt templates
        self.prompt_templates = {
            'factual_qa': self._factual_qa_template,
            'analytical': self._analytical_template,
            'procedural': self._procedural_template,
            'comparative': self._comparative_template,
            'creative': self._creative_template,
            'technical': self._technical_template
        }
        
        # Prompt optimization techniques
        self.optimization_techniques = {
            'chain_of_thought': self._add_chain_of_thought,
            'source_weighting': self._add_source_weighting,
            'confidence_calibration': self._add_confidence_calibration,
            'multi_step_reasoning': self._add_multi_step_reasoning
        }
    
    def engineer_rag_prompt(self, query: str, context: str,
                           query_type: str = 'factual_qa',
                           optimizations: List[str] = ['confidence_calibration']) -> Dict[str, Any]:
        """Engineer optimized RAG prompt with specified techniques."""
        
        # Start with base template
        base_prompt = self.prompt_templates[query_type](query, context)
        
        # Apply optimization techniques
        optimized_prompt = base_prompt
        optimization_metadata = {}
        
        for technique in optimizations:
            if technique in self.optimization_techniques:
                result = self.optimization_techniques[technique](
                    optimized_prompt, query, context
                )
                optimized_prompt = result['prompt']
                optimization_metadata[technique] = result['metadata']
        
        return {
            'base_prompt': base_prompt,
            'optimized_prompt': optimized_prompt,
            'optimizations_applied': optimizations,
            'optimization_metadata': optimization_metadata,
            'query_type': query_type
        }

    def _factual_qa_template(self, query: str, context: str) -> str:
        """Optimized template for factual question answering."""
        
        return f"""You are an expert information analyst. Use the provided context to answer the user's question accurately and comprehensively.

CONTEXT INFORMATION:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Base your answer strictly on the provided context
2. If the context doesn't contain sufficient information, clearly state this limitation
3. Cite specific sources when making claims
4. Provide direct quotes when appropriate
5. Distinguish between facts and interpretations
6. If there are contradictions in the sources, acknowledge and explain them

ANSWER STRUCTURE:
- Start with a direct answer to the question
- Provide supporting details from the context
- Include relevant quotes with source attribution
- Note any limitations or uncertainties

ANSWER:"""

    def _analytical_template(self, query: str, context: str) -> str:
        """Template for analytical queries requiring interpretation."""
        
        return f"""You are an expert analyst. Analyze the provided context to answer the user's analytical question.

CONTEXT INFORMATION:
{context}

ANALYTICAL QUESTION: {query}

INSTRUCTIONS:
1. Analyze the information provided in the context
2. Present multiple perspectives where relevant
3. Draw connections between different pieces of information
4. Provide evidence-based reasoning
5. Distinguish between facts and your analysis
6. Note any limitations in the available data

ANALYSIS STRUCTURE:
- Summary of key findings from context
- Detailed analytical response
- Supporting evidence with source citations
- Limitations and uncertainties
- Conclusions based on available evidence

ANALYSIS:"""

    def _procedural_template(self, query: str, context: str) -> str:
        """Template for procedural/how-to queries."""
        
        return f"""You are an expert instructor. Use the provided context to answer the procedural question clearly and comprehensively.

CONTEXT INFORMATION:
{context}

PROCEDURAL QUESTION: {query}

INSTRUCTIONS:
1. Extract step-by-step information from the context
2. Organize steps in logical order
3. Include prerequisites and requirements
4. Note any warnings or important considerations
5. Provide clear, actionable guidance
6. Cite sources for each major step

RESPONSE STRUCTURE:
- Prerequisites and requirements
- Step-by-step instructions
- Important notes and warnings
- Expected outcomes
- Troubleshooting tips (if available in context)

PROCEDURAL RESPONSE:"""

    def _comparative_template(self, query: str, context: str) -> str:
        """Template for comparative analysis queries."""
        
        return f"""You are an expert comparator. Use the provided context to conduct a thorough comparison.

CONTEXT INFORMATION:
{context}

COMPARISON QUESTION: {query}

INSTRUCTIONS:
1. Identify the items/concepts being compared
2. Extract comparison criteria from the context
3. Present similarities and differences systematically
4. Use evidence from the context to support comparisons
5. Note any missing information that limits comparison
6. Provide balanced analysis

COMPARISON STRUCTURE:
- Items being compared
- Comparison criteria
- Similarities
- Differences
- Strengths and weaknesses of each
- Summary and conclusions

COMPARISON:"""

    def _creative_template(self, query: str, context: str) -> str:
        """Template for creative or open-ended queries."""
        
        return f"""You are a creative expert. Use the provided context as inspiration to address the creative question.

CONTEXT INFORMATION:
{context}

CREATIVE QUESTION: {query}

INSTRUCTIONS:
1. Use the context as a foundation for creative thinking
2. Build upon the information provided
3. Generate novel ideas and perspectives
4. Connect disparate concepts from the context
5. Maintain relevance to the original question
6. Clearly indicate what comes from context vs. creative extension

CREATIVE RESPONSE:"""

    def _technical_template(self, query: str, context: str) -> str:
        """Template for technical queries."""
        
        return f"""You are a technical expert. Use the provided context to answer the technical question with precision.

CONTEXT INFORMATION:
{context}

TECHNICAL QUESTION: {query}

INSTRUCTIONS:
1. Focus on technical accuracy and precision
2. Use appropriate technical terminology
3. Provide detailed explanations of technical concepts
4. Include relevant technical specifications or parameters
5. Note any technical limitations or constraints
6. Cite technical sources appropriately

TECHNICAL RESPONSE:"""

    def _add_chain_of_thought(self, base_prompt: str, query: str, 
                            context: str) -> Dict[str, Any]:
        """Add chain-of-thought reasoning to prompt."""
        
        cot_enhancement = """
REASONING PROCESS:
Before providing your final answer, work through your reasoning step-by-step:

1. INFORMATION EXTRACTION: What key information from the context relates to the question?
2. RELEVANCE ASSESSMENT: How does each piece of information address the question?
3. SYNTHESIS: How do you combine the information to form a comprehensive answer?
4. CONFIDENCE EVALUATION: How confident are you in your answer based on the available evidence?

Let me work through this systematically:

STEP 1 - Information Extraction:
[Identify and list key relevant information from context]

STEP 2 - Relevance Assessment:
[Evaluate how each piece of information addresses the question]

STEP 3 - Synthesis:
[Combine information into a coherent answer]

STEP 4 - Confidence Evaluation:
[Assess confidence level and note any limitations]

FINAL ANSWER:
"""
        
        enhanced_prompt = base_prompt + cot_enhancement
        
        return {
            'prompt': enhanced_prompt,
            'metadata': {
                'technique': 'chain_of_thought',
                'added_tokens': len(cot_enhancement.split()),
                'reasoning_steps': 4
            }
        }

    def _add_confidence_calibration(self, base_prompt: str, query: str,
                                  context: str) -> Dict[str, Any]:
        """Add confidence calibration to improve answer reliability."""
        
        confidence_enhancement = """
CONFIDENCE ASSESSMENT:
For your final answer, provide a confidence assessment:

1. EVIDENCE STRENGTH: Rate the strength of evidence (Strong/Medium/Weak)
   - Strong: Multiple reliable sources with consistent information
   - Medium: Some sources with mostly consistent information
   - Weak: Limited or inconsistent source information

2. COMPLETENESS: Rate answer completeness (Complete/Partial/Incomplete)
   - Complete: Context fully addresses the question
   - Partial: Context addresses some aspects but missing key information
   - Incomplete: Context has minimal relevant information

3. CONFIDENCE SCORE: Provide an overall confidence score (0-100%)
   - 90-100%: Highly confident, strong evidence base
   - 70-89%: Confident, adequate evidence base
   - 50-69%: Moderately confident, limited evidence
   - Below 50%: Low confidence, insufficient evidence

Include this assessment at the end of your response:

CONFIDENCE ASSESSMENT:
- Evidence Strength: [Strong/Medium/Weak]
- Completeness: [Complete/Partial/Incomplete] 
- Confidence Score: [0-100%]
- Key Limitations: [List any significant limitations or uncertainties]
"""
        
        enhanced_prompt = base_prompt + confidence_enhancement
        
        return {
            'prompt': enhanced_prompt,
            'metadata': {
                'technique': 'confidence_calibration',
                'added_tokens': len(confidence_enhancement.split()),
                'assessment_dimensions': 3
            }
        }

    def _add_source_weighting(self, base_prompt: str, query: str,
                            context: str) -> Dict[str, Any]:
        """Add source weighting instructions."""
        
        source_enhancement = """
SOURCE WEIGHTING:
When using information from multiple sources, consider:
1. Source credibility and authority
2. Recency and relevance of information
3. Consistency across sources
4. Specific expertise related to the query

Weight your response accordingly and explicitly note when drawing from higher-quality sources.
"""
        
        enhanced_prompt = base_prompt + source_enhancement
        
        return {
            'prompt': enhanced_prompt,
            'metadata': {
                'technique': 'source_weighting',
                'added_tokens': len(source_enhancement.split())
            }
        }

    def _add_multi_step_reasoning(self, base_prompt: str, query: str,
                                context: str) -> Dict[str, Any]:
        """Add multi-step reasoning structure."""
        
        reasoning_enhancement = """
MULTI-STEP REASONING:
Structure your response using these reasoning steps:

1. PROBLEM BREAKDOWN: Break the question into component parts
2. EVIDENCE GATHERING: Identify relevant information for each part
3. LOGICAL CONNECTIONS: Connect evidence to reach conclusions
4. SYNTHESIS: Combine findings into a comprehensive answer
5. VALIDATION: Check reasoning for consistency and completeness
"""
        
        enhanced_prompt = base_prompt + reasoning_enhancement
        
        return {
            'prompt': enhanced_prompt,
            'metadata': {
                'technique': 'multi_step_reasoning',
                'added_tokens': len(reasoning_enhancement.split()),
                'reasoning_steps': 5
            }
        }


class DynamicPromptAdapter:
    """Adapt prompts based on context quality and query characteristics."""
    
    def __init__(self, llm_model):
        self.llm_model = llm_model
        
    def adapt_prompt_dynamically(self, query: str, context: str,
                                retrieval_metadata: Dict) -> Dict[str, Any]:
        """Dynamically adapt prompt based on context and query analysis."""
        
        # Analyze context quality
        context_analysis = self._analyze_context_quality(context, query)
        
        # Analyze query characteristics
        query_analysis = self._analyze_query_characteristics(query)
        
        # Choose optimal prompt strategy
        prompt_strategy = self._select_prompt_strategy(
            context_analysis, query_analysis, retrieval_metadata
        )
        
        # Generate adapted prompt
        adapted_prompt = self._generate_adapted_prompt(
            query, context, prompt_strategy
        )
        
        return {
            'adapted_prompt': adapted_prompt,
            'context_analysis': context_analysis,
            'query_analysis': query_analysis,
            'strategy': prompt_strategy,
            'adaptation_reasoning': self._explain_adaptation_reasoning(
                context_analysis, query_analysis, prompt_strategy
            )
        }

    def _analyze_context_quality(self, context: str, query: str) -> Dict[str, Any]:
        """Analyze the quality and characteristics of retrieved context."""
        
        # Basic metrics
        context_length = len(context.split())
        context_diversity = self._calculate_context_diversity(context)
        
        # Source analysis
        source_count = context.count('[Source:')
        source_diversity = self._analyze_source_diversity(context)
        
        # Relevance assessment using LLM
        relevance_score = self._assess_context_relevance(context, query)
        
        # Information density
        information_density = self._calculate_information_density(context)
        
        # Quality classification
        quality_level = self._classify_context_quality(
            context_length, context_diversity, source_count, 
            relevance_score, information_density
        )
        
        return {
            'length': context_length,
            'diversity_score': context_diversity,
            'source_count': source_count,
            'source_diversity': source_diversity,
            'relevance_score': relevance_score,
            'information_density': information_density,
            'quality_level': quality_level  # High/Medium/Low
        }
    
    def _assess_context_relevance(self, context: str, query: str) -> float:
        """Use LLM to assess context relevance to query."""
        
        relevance_prompt = f"""
        Rate the relevance of this context to the given query on a scale of 0.0 to 1.0:
        
        Query: {query}
        
        Context: {context[:1000]}...
        
        Consider:
        1. How directly the context addresses the query
        2. The completeness of information provided
        3. The accuracy and reliability of information
        
        Return only a number between 0.0 and 1.0:
        """
        
        try:
            response = self.llm_model.predict(relevance_prompt).strip()
            relevance_score = float(response)
            return max(0.0, min(1.0, relevance_score))
        except:
            return 0.5  # Default score if assessment fails

    def _analyze_query_characteristics(self, query: str) -> Dict[str, Any]:
        """Analyze characteristics of the input query."""
        
        # Basic characteristics
        query_length = len(query.split())
        question_marks = query.count('?')
        
        # Complexity indicators
        complexity_indicators = ['how', 'why', 'what', 'when', 'where', 'compare', 'analyze']
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in query.lower())
        
        return {
            'length': query_length,
            'complexity_score': complexity_score,
            'has_questions': question_marks > 0,
            'estimated_complexity': 'high' if complexity_score > 2 else 'medium' if complexity_score > 0 else 'low'
        }

    def _calculate_context_diversity(self, context: str) -> float:
        """Calculate diversity score of context content."""
        # Simple diversity measure based on unique words
        words = context.lower().split()
        unique_words = set(words)
        return len(unique_words) / len(words) if words else 0

    def _analyze_source_diversity(self, context: str) -> float:
        """Analyze diversity of sources in context."""
        # Extract source indicators
        import re
        sources = re.findall(r'\[Source: ([^\]]+)\]', context)
        unique_sources = set(sources)
        return len(unique_sources) / max(1, len(sources))

    def _calculate_information_density(self, context: str) -> float:
        """Calculate information density of context."""
        # Simple heuristic: ratio of content words to total words
        content_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with']
        words = context.lower().split()
        non_stopwords = [w for w in words if w not in content_words]
        return len(non_stopwords) / max(1, len(words))

    def _classify_context_quality(self, length: int, diversity: float, source_count: int,
                                 relevance: float, density: float) -> str:
        """Classify overall context quality."""
        
        # Simple scoring system
        score = 0
        
        # Length factor
        if length > 200:
            score += 1
        
        # Diversity factor
        if diversity > 0.3:
            score += 1
            
        # Source factor
        if source_count > 1:
            score += 1
            
        # Relevance factor
        if relevance > 0.7:
            score += 2
        elif relevance > 0.4:
            score += 1
            
        # Density factor
        if density > 0.6:
            score += 1
        
        if score >= 4:
            return 'high'
        elif score >= 2:
            return 'medium'
        else:
            return 'low'

    def _select_prompt_strategy(self, context_analysis: Dict, query_analysis: Dict,
                               retrieval_metadata: Dict) -> Dict[str, Any]:
        """Select optimal prompt strategy based on analysis."""
        
        strategy = {
            'template': 'factual_qa',  # default
            'optimizations': []
        }
        
        # Adjust based on context quality
        if context_analysis['quality_level'] == 'high':
            strategy['optimizations'].append('chain_of_thought')
        
        if context_analysis['source_count'] > 1:
            strategy['optimizations'].append('source_weighting')
        
        # Always include confidence calibration
        strategy['optimizations'].append('confidence_calibration')
        
        # Adjust based on query complexity
        if query_analysis['estimated_complexity'] == 'high':
            strategy['optimizations'].append('multi_step_reasoning')
        
        return strategy

    def _generate_adapted_prompt(self, query: str, context: str,
                               strategy: Dict) -> str:
        """Generate adapted prompt using selected strategy."""
        
        # Use RAGPromptEngineer to create the prompt
        prompt_engineer = RAGPromptEngineer(self.llm_model)
        
        result = prompt_engineer.engineer_rag_prompt(
            query=query,
            context=context,
            query_type=strategy['template'],
            optimizations=strategy['optimizations']
        )
        
        return result['optimized_prompt']

    def _explain_adaptation_reasoning(self, context_analysis: Dict,
                                    query_analysis: Dict, strategy: Dict) -> str:
        """Explain the reasoning behind prompt adaptation choices."""
        
        reasoning_parts = []
        
        # Context quality reasoning
        reasoning_parts.append(f"Context quality: {context_analysis['quality_level']} "
                             f"(relevance: {context_analysis['relevance_score']:.2f})")
        
        # Query complexity reasoning  
        reasoning_parts.append(f"Query complexity: {query_analysis['estimated_complexity']}")
        
        # Strategy reasoning
        reasoning_parts.append(f"Selected optimizations: {', '.join(strategy['optimizations'])}")
        
        return '; '.join(reasoning_parts)