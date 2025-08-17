#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

def test_imports():
    """Test that all modules can be imported successfully."""
    
    print("Testing module imports...")
    
    try:
        # Test core framework imports
        from evaluation_framework import RAGEvaluationFramework, RAGEvaluationResult
        print("✅ evaluation_framework - OK")
        
        from custom_metrics import CustomRAGMetrics
        print("✅ custom_metrics - OK")
        
        from retrieval_evaluator import RetrievalEvaluator
        print("✅ retrieval_evaluator - OK")
        
        from llm_judge_evaluator import LLMJudgeEvaluator
        print("✅ llm_judge_evaluator - OK")
        
        from benchmark_system import AutomatedRAGBenchmark
        print("✅ benchmark_system - OK")
        
        from ab_testing import RAGABTestFramework, RAGMultiArmedBandit
        print("✅ ab_testing - OK")
        
        from production_monitor import RAGProductionMonitor
        print("✅ production_monitor - OK")
        
        from alerting_system import RAGAlertingSystem
        print("✅ alerting_system - OK")
        
        try:
            from evaluation_ecosystem import RAGEvaluationEcosystem
            print("✅ evaluation_ecosystem - OK")
        except ImportError as e:
            if "ragas" in str(e).lower():
                print("⚠️  evaluation_ecosystem - PARTIAL (missing ragas dependency)")
            else:
                raise
        
        from config import get_config, EvaluationConfig
        print("✅ config - OK")
        
        # Note: ragas_evaluator requires external dependencies
        try:
            from ragas_evaluator import RAGASEvaluator
            print("✅ ragas_evaluator - OK")
        except ImportError as e:
            print("⚠️  ragas_evaluator - SKIP (missing dependencies: ragas, datasets)")
        
        print("\n✅ All core imports successful!")
        
        # Test configuration
        config = get_config('development')
        print(f"✅ Configuration loaded: {config.llm_judge_model}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality with mock components."""
    
    print("\nTesting basic functionality...")
    
    try:
        from evaluation_framework import RAGEvaluationFramework
        from config import get_config
        
        # Mock components
        class MockLLM:
            def predict(self, prompt):
                return "Mock response"
        
        class MockEmbedding:
            def encode(self, texts):
                import random
                return [[random.random() for _ in range(10)] for _ in texts]
        
        # Test framework initialization
        framework = RAGEvaluationFramework(
            llm_judge=MockLLM(),
            embedding_model=MockEmbedding()
        )
        
        print("✅ Framework initialization - OK")
        
        # Test configuration
        config = get_config('development')
        print(f"✅ Configuration: min_quality_score = {config.min_quality_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("RAG Evaluation Framework - Import Test")
    print("=" * 50)
    
    imports_ok = test_imports()
    functionality_ok = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if imports_ok and functionality_ok:
        print("✅ All tests passed! The framework is ready to use.")
        print("\nNext steps:")
        print("1. Run: python demo_evaluation_system.py")
        print("2. Install optional dependencies: pip install ragas datasets")
        print("3. Configure your LLM and embedding models")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Ensure you're in the session5 directory")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check Python version (requires 3.8+)")
