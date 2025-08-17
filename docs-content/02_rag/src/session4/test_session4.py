"""
Unit Tests for Session 4: Query Enhancement & Context Augmentation

Tests for all query enhancement components.
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock
import numpy as np

# Import components to test
from semantic_gap_analyzer import SemanticGapAnalyzer
from hyde_enhancer import HyDEQueryEnhancer
from query_expander import IntelligentQueryExpander
from multi_query_generator import MultiQueryGenerator
from context_optimizer import ContextWindowOptimizer
from prompt_engineer import RAGPromptEngineer, DynamicPromptAdapter
from comprehensive_enhancer import ComprehensiveQueryEnhancer
from config import Session4Config, get_development_config


class TestSemanticGapAnalyzer:
    """Test semantic gap analysis functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Mock embedding model
        self.mock_embedding_model = Mock()
        self.mock_embedding_model.encode.return_value = [
            np.array([1.0, 0.0, 0.0]),  # Query embedding
            np.array([0.8, 0.6, 0.0]),  # Doc 1 embedding
            np.array([0.0, 1.0, 0.0])   # Doc 2 embedding
        ]
        
        self.analyzer = SemanticGapAnalyzer(self.mock_embedding_model)
    
    def test_analyze_query_document_gap(self):
        """Test semantic gap analysis."""
        query = "test query"
        documents = ["document 1", "document 2"]
        
        result = self.analyzer.analyze_query_document_gap(query, documents)
        
        assert 'query' in result
        assert 'avg_similarity' in result
        assert 'max_similarity' in result
        assert 'min_similarity' in result
        assert 'gap_analysis' in result
        
        assert result['query'] == query
        assert isinstance(result['avg_similarity'], float)
        assert isinstance(result['max_similarity'], float)
        assert isinstance(result['min_similarity'], float)


class TestHyDEQueryEnhancer:
    """Test HyDE query enhancement functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Mock LLM model
        self.mock_llm = Mock()
        self.mock_llm.predict.return_value = "This is a hypothetical document about the query topic."
        
        # Mock embedding model
        self.mock_embedding_model = Mock()
        self.mock_embedding_model.encode.return_value = [
            np.array([1.0, 0.0, 0.0]),  # Query embedding
            np.array([0.8, 0.2, 0.0]),  # Hyde doc 1
            np.array([0.7, 0.3, 0.0])   # Hyde doc 2
        ]
        
        self.hyde_enhancer = HyDEQueryEnhancer(
            self.mock_llm, 
            self.mock_embedding_model
        )
    
    def test_enhance_query_with_hyde(self):
        """Test HyDE query enhancement."""
        query = "What is machine learning?"
        
        result = self.hyde_enhancer.enhance_query_with_hyde(
            query, num_hypotheticals=2
        )
        
        assert 'original_query' in result
        assert 'query_type' in result
        assert 'hypothetical_documents' in result
        assert 'enhanced_embedding' in result
        assert 'confidence_score' in result
        
        assert result['original_query'] == query
        assert len(result['hypothetical_documents']) == 2
        assert isinstance(result['confidence_score'], float)
    
    def test_classify_query_type(self):
        """Test query type classification."""
        self.mock_llm.predict.return_value = "factual"
        
        query_type = self.hyde_enhancer._classify_query_type("What is AI?")
        assert query_type == "factual"
    
    def test_factual_hyde_template(self):
        """Test factual HyDE template."""
        query = "What is AI?"
        template = self.hyde_enhancer._factual_hyde_template(query)
        
        assert query in template
        assert "detailed" in template.lower()
        assert "document" in template.lower()


class TestIntelligentQueryExpander:
    """Test query expansion functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_llm = Mock()
        self.mock_llm.predict.return_value = "artificial intelligence\nmachine learning\nneural networks"
        
        self.expander = IntelligentQueryExpander(self.mock_llm)
    
    def test_expand_query(self):
        """Test query expansion."""
        query = "AI algorithms"
        
        result = self.expander.expand_query(query, strategies=['semantic'])
        
        assert 'original_query' in result
        assert 'expansions_by_strategy' in result
        assert 'all_expansions' in result
        assert 'expanded_query' in result
        assert 'expansion_count' in result
        
        assert result['original_query'] == query
        assert 'semantic' in result['expansions_by_strategy']
    
    def test_semantic_expansion(self):
        """Test semantic expansion strategy."""
        query = "machine learning"
        
        expansions = self.expander._semantic_expansion(query, max_expansions=3)
        
        assert isinstance(expansions, list)
        assert len(expansions) <= 3
    
    def test_contextual_expansion(self):
        """Test contextual expansion strategy."""
        self.mock_llm.predict.return_value = "How do ML algorithms work?\nWhat is machine learning?"
        
        query = "machine learning"
        expansions = self.expander._contextual_expansion(query, max_expansions=2)
        
        assert isinstance(expansions, list)
        assert len(expansions) <= 2


class TestMultiQueryGenerator:
    """Test multi-query generation functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_llm = Mock()
        self.mock_llm.predict.return_value = "What is ML?\nHow does ML work?\nWhy use ML?"
        
        self.multi_gen = MultiQueryGenerator(self.mock_llm)
    
    def test_generate_multi_query_set(self):
        """Test multi-query generation."""
        query = "How to optimize machine learning?"
        
        result = self.multi_gen.generate_multi_query_set(query, total_queries=4)
        
        assert 'original_query' in result
        assert 'query_variants' in result
        assert 'queries_by_perspective' in result
        assert 'generation_metadata' in result
        assert 'total_variants' in result
        
        assert result['original_query'] == query
        assert isinstance(result['query_variants'], list)
    
    def test_decompose_complex_query(self):
        """Test query decomposition."""
        query = "How to build and deploy ML models?"
        
        sub_questions = self.multi_gen._decompose_complex_query(query, num_queries=3)
        
        assert isinstance(sub_questions, list)
        assert len(sub_questions) <= 3
    
    def test_generate_specificity_variants(self):
        """Test specificity variant generation."""
        query = "machine learning"
        
        variants = self.multi_gen._generate_specificity_variants(query, num_queries=3)
        
        assert isinstance(variants, list)
        assert len(variants) <= 3


class TestContextWindowOptimizer:
    """Test context window optimization functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Mock tokenizer
        self.mock_tokenizer = Mock()
        self.mock_tokenizer.encode.return_value = ["token"] * 10  # 10 tokens per text
        
        self.optimizer = ContextWindowOptimizer(
            self.mock_tokenizer, 
            max_context_tokens=100
        )
    
    def test_optimize_context_window(self):
        """Test context window optimization."""
        query = "test query"
        chunks = [
            {
                'document': Mock(page_content="test content 1"),
                'similarity_score': 0.1,
                'metadata': {'source': 'doc1.pdf'}
            },
            {
                'document': Mock(page_content="test content 2"),
                'similarity_score': 0.2,
                'metadata': {'source': 'doc2.pdf'}
            }
        ]
        
        result = self.optimizer.optimize_context_window(query, chunks)
        
        assert 'optimized_context' in result
        assert 'selected_chunks' in result
        assert 'context_tokens' in result
        assert 'efficiency_score' in result
        assert 'strategy_used' in result
        assert 'original_chunk_count' in result
        
        assert result['original_chunk_count'] == 2
        assert isinstance(result['optimized_context'], str)
    
    def test_relevance_based_selection(self):
        """Test relevance-based chunk selection."""
        query = "test query"
        chunks = [
            {
                'document': Mock(page_content="relevant content"),
                'similarity_score': 0.1,
                'metadata': {'source': 'doc1.pdf'}
            }
        ]
        
        result = self.optimizer._relevance_based_selection(query, chunks, token_budget=50)
        
        assert 'context' in result
        assert 'chunks' in result
        assert 'token_count' in result
        assert 'efficiency' in result


class TestRAGPromptEngineer:
    """Test prompt engineering functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_llm = Mock()
        self.prompt_engineer = RAGPromptEngineer(self.mock_llm)
    
    def test_engineer_rag_prompt(self):
        """Test RAG prompt engineering."""
        query = "What is AI?"
        context = "AI is artificial intelligence that simulates human thinking."
        
        result = self.prompt_engineer.engineer_rag_prompt(
            query, context, 
            query_type='factual_qa',
            optimizations=['confidence_calibration']
        )
        
        assert 'base_prompt' in result
        assert 'optimized_prompt' in result
        assert 'optimizations_applied' in result
        assert 'optimization_metadata' in result
        assert 'query_type' in result
        
        assert query in result['optimized_prompt']
        assert context in result['optimized_prompt']
    
    def test_factual_qa_template(self):
        """Test factual QA template."""
        query = "What is machine learning?"
        context = "ML is a subset of AI."
        
        prompt = self.prompt_engineer._factual_qa_template(query, context)
        
        assert query in prompt
        assert context in prompt
        assert "expert" in prompt.lower()
    
    def test_add_confidence_calibration(self):
        """Test confidence calibration enhancement."""
        base_prompt = "Answer the question."
        query = "test query"
        context = "test context"
        
        result = self.prompt_engineer._add_confidence_calibration(
            base_prompt, query, context
        )
        
        assert 'prompt' in result
        assert 'metadata' in result
        assert "CONFIDENCE" in result['prompt']
        assert result['metadata']['technique'] == 'confidence_calibration'


class TestDynamicPromptAdapter:
    """Test dynamic prompt adaptation functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_llm = Mock()
        self.mock_llm.predict.return_value = "0.8"  # Mock relevance score
        
        self.adapter = DynamicPromptAdapter(self.mock_llm)
    
    def test_adapt_prompt_dynamically(self):
        """Test dynamic prompt adaptation."""
        query = "What is AI?"
        context = "AI is artificial intelligence."
        metadata = {'source_count': 2}
        
        result = self.adapter.adapt_prompt_dynamically(query, context, metadata)
        
        assert 'adapted_prompt' in result
        assert 'context_analysis' in result
        assert 'query_analysis' in result
        assert 'strategy' in result
        assert 'adaptation_reasoning' in result
    
    def test_analyze_context_quality(self):
        """Test context quality analysis."""
        context = "[Source: doc1.pdf]\nThis is test content about AI and machine learning."
        query = "What is AI?"
        
        analysis = self.adapter._analyze_context_quality(context, query)
        
        assert 'length' in analysis
        assert 'diversity_score' in analysis
        assert 'source_count' in analysis
        assert 'relevance_score' in analysis
        assert 'quality_level' in analysis
        
        assert analysis['source_count'] == 1
        assert analysis['quality_level'] in ['high', 'medium', 'low']


class TestSession4Config:
    """Test configuration management."""
    
    def test_default_config_creation(self):
        """Test default configuration creation."""
        config = Session4Config()
        
        assert config.hyde_config is not None
        assert config.expansion_config is not None
        assert config.multi_query_config is not None
        assert config.context_config is not None
        assert config.prompt_config is not None
        assert config.enhancement_pipeline is not None
    
    def test_development_config(self):
        """Test development configuration."""
        config = get_development_config()
        
        # Development config should have reduced resource usage
        assert config.hyde_config.num_hypotheticals == 2
        assert config.expansion_config.max_expansions == 3
        assert config.multi_query_config.total_queries == 4
        assert config.context_config.max_context_tokens == 2000
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Session4Config()
        
        # Valid configuration should pass validation
        assert config.validate_config() == True
        
        # Invalid configuration should fail validation
        config.context_config.max_context_tokens = -1
        assert config.validate_config() == False
    
    def test_get_enhancement_config(self):
        """Test enhancement configuration generation."""
        config = Session4Config()
        enhancement_config = config.get_enhancement_config()
        
        assert 'use_hyde' in enhancement_config
        assert 'use_expansion' in enhancement_config
        assert 'use_multi_query' in enhancement_config
        assert 'k' in enhancement_config
        assert 'hyde_config' in enhancement_config
        assert 'expansion_config' in enhancement_config


# Integration test for the comprehensive enhancer
class TestComprehensiveQueryEnhancer:
    """Test comprehensive query enhancement integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Mock components
        self.mock_llm = Mock()
        self.mock_embedding_model = Mock()
        self.mock_tokenizer = Mock()
        
        self.mock_llm.predict.return_value = "Test response"
        self.mock_embedding_model.encode.return_value = [np.array([1.0, 0.0, 0.0])]
        self.mock_tokenizer.encode.return_value = ["token"] * 5
        
        self.enhancer = ComprehensiveQueryEnhancer(
            self.mock_llm,
            self.mock_embedding_model, 
            self.mock_tokenizer
        )
    
    @pytest.mark.asyncio
    async def test_comprehensive_enhancement_initialization(self):
        """Test comprehensive enhancer initialization."""
        assert self.enhancer.hyde_enhancer is not None
        assert self.enhancer.query_expander is not None
        assert self.enhancer.multi_query_gen is not None
        assert self.enhancer.context_optimizer is not None
        assert self.enhancer.prompt_engineer is not None
        assert self.enhancer.dynamic_adapter is not None


# Utility function to run async tests
def run_async_test(async_func):
    """Helper to run async test functions."""
    return asyncio.run(async_func())


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])