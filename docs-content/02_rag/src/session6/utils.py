# Utility functions for Session 6 GraphRAG
import json
import time
import logging
import hashlib
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import networkx as nx
from functools import wraps


def setup_logging(level: str = "INFO", format_string: str = None):
    """Setup logging configuration."""
    
    format_string = format_string or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("graphrag.log")
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger("neo4j").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


def timer(func):
    """Decorator to measure function execution time."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger = logging.getLogger(func.__module__)
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        
        return result
    
    return wrapper


def cache_result(ttl: int = 3600):
    """Decorator to cache function results."""
    
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = hashlib.md5(
                json.dumps([str(args), str(kwargs)], sort_keys=True).encode()
            ).hexdigest()
            
            current_time = time.time()
            
            # Check if result is cached and not expired
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl:
                    return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            
            return result
        
        return wrapper
    
    return decorator


class GraphMetrics:
    """Utility class for calculating graph metrics."""
    
    @staticmethod
    def calculate_graph_statistics(graph: nx.Graph) -> Dict[str, Any]:
        """Calculate comprehensive graph statistics."""
        
        if graph.number_of_nodes() == 0:
            return {'empty_graph': True}
        
        stats = {
            'basic_metrics': {
                'node_count': graph.number_of_nodes(),
                'edge_count': graph.number_of_edges(),
                'density': nx.density(graph),
                'is_connected': nx.is_connected(graph) if isinstance(graph, nx.Graph) else nx.is_weakly_connected(graph)
            }
        }
        
        # Centrality measures
        try:
            if graph.number_of_nodes() < 1000:  # Only for smaller graphs due to computation cost
                stats['centrality'] = {
                    'degree_centrality': nx.degree_centrality(graph),
                    'betweenness_centrality': nx.betweenness_centrality(graph),
                    'closeness_centrality': nx.closeness_centrality(graph)
                }
                
                if isinstance(graph, nx.DiGraph):
                    stats['centrality']['pagerank'] = nx.pagerank(graph)
                
        except Exception as e:
            logging.warning(f"Could not calculate centrality measures: {e}")
        
        # Community detection (for undirected graphs)
        try:
            if isinstance(graph, nx.Graph) and graph.number_of_nodes() > 5:
                communities = nx.community.greedy_modularity_communities(graph)
                stats['community'] = {
                    'num_communities': len(communities),
                    'modularity': nx.community.modularity(graph, communities)
                }
        except Exception as e:
            logging.warning(f"Could not calculate community metrics: {e}")
        
        return stats
    
    @staticmethod
    def find_important_nodes(graph: nx.Graph, top_k: int = 10) -> Dict[str, List]:
        """Find the most important nodes by various centrality measures."""
        
        important_nodes = {}
        
        try:
            # Degree centrality
            degree_centrality = nx.degree_centrality(graph)
            important_nodes['degree'] = sorted(
                degree_centrality.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:top_k]
            
            # Betweenness centrality
            betweenness_centrality = nx.betweenness_centrality(graph)
            important_nodes['betweenness'] = sorted(
                betweenness_centrality.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:top_k]
            
            # PageRank (for directed graphs)
            if isinstance(graph, nx.DiGraph):
                pagerank = nx.pagerank(graph)
                important_nodes['pagerank'] = sorted(
                    pagerank.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:top_k]
                
        except Exception as e:
            logging.warning(f"Could not find important nodes: {e}")
        
        return important_nodes


class TextProcessor:
    """Utility class for text processing operations."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        
        if not text:
            return ""
        
        import re
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,!?;:()]+', '', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from collections import Counter
            
            # Download required NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords')
            
            # Tokenize and filter
            tokens = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            
            # Filter tokens
            keywords = [
                token for token in tokens 
                if token.isalnum() and len(token) > 2 and token not in stop_words
            ]
            
            # Count frequency and return top keywords
            word_freq = Counter(keywords)
            return [word for word, _ in word_freq.most_common(max_keywords)]
            
        except ImportError:
            logging.warning("NLTK not available, using simple keyword extraction")
            # Fallback to simple extraction
            import re
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            return list(set(words))[:max_keywords]
    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except ImportError:
            # Fallback to simple Jaccard similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """Ensure directory exists, create if necessary."""
        
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def save_json(data: Dict[str, Any], filepath: Union[str, Path]) -> None:
        """Save data to JSON file."""
        
        filepath = Path(filepath)
        FileUtils.ensure_directory(filepath.parent)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    @staticmethod
    def load_json(filepath: Union[str, Path]) -> Dict[str, Any]:
        """Load data from JSON file."""
        
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def find_files(directory: Union[str, Path], 
                   patterns: List[str], 
                   exclude_patterns: List[str] = None) -> List[Path]:
        """Find files matching patterns."""
        
        directory = Path(directory)
        exclude_patterns = exclude_patterns or []
        
        found_files = []
        
        for pattern in patterns:
            # Use glob to find matching files
            matches = directory.rglob(pattern)
            
            for match in matches:
                # Check exclude patterns
                should_exclude = False
                for exclude_pattern in exclude_patterns:
                    if exclude_pattern.replace('*', '') in str(match):
                        should_exclude = True
                        break
                
                if not should_exclude and match.is_file():
                    found_files.append(match)
        
        return sorted(list(set(found_files)))


class PerformanceMonitor:
    """Utility class for monitoring performance metrics."""
    
    def __init__(self):
        self.metrics = {
            'function_calls': {},
            'execution_times': {},
            'memory_usage': {},
            'error_counts': {}
        }
    
    def record_function_call(self, function_name: str, execution_time: float):
        """Record function call metrics."""
        
        if function_name not in self.metrics['function_calls']:
            self.metrics['function_calls'][function_name] = 0
            self.metrics['execution_times'][function_name] = []
        
        self.metrics['function_calls'][function_name] += 1
        self.metrics['execution_times'][function_name].append(execution_time)
    
    def record_error(self, error_type: str):
        """Record error occurrence."""
        
        if error_type not in self.metrics['error_counts']:
            self.metrics['error_counts'][error_type] = 0
        
        self.metrics['error_counts'][error_type] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        
        summary = {
            'total_function_calls': sum(self.metrics['function_calls'].values()),
            'total_errors': sum(self.metrics['error_counts'].values()),
            'function_stats': {}
        }
        
        for func_name, call_count in self.metrics['function_calls'].items():
            execution_times = self.metrics['execution_times'][func_name]
            
            summary['function_stats'][func_name] = {
                'call_count': call_count,
                'avg_execution_time': sum(execution_times) / len(execution_times),
                'min_execution_time': min(execution_times),
                'max_execution_time': max(execution_times),
                'total_execution_time': sum(execution_times)
            }
        
        return summary


class ValidationUtils:
    """Utility class for data validation."""
    
    @staticmethod
    def validate_entity(entity_data: Dict[str, Any]) -> bool:
        """Validate entity data structure."""
        
        required_fields = ['canonical', 'type', 'confidence']
        
        for field in required_fields:
            if field not in entity_data:
                return False
        
        # Validate confidence score
        confidence = entity_data.get('confidence', 0)
        if not (0.0 <= confidence <= 1.0):
            return False
        
        return True
    
    @staticmethod
    def validate_relationship(relationship_data: Dict[str, Any]) -> bool:
        """Validate relationship data structure."""
        
        required_fields = ['subject', 'predicate', 'object']
        
        for field in required_fields:
            if field not in relationship_data:
                return False
            
            if not relationship_data[field]:
                return False
        
        # Validate confidence if present
        if 'confidence' in relationship_data:
            confidence = relationship_data['confidence']
            if not (0.0 <= confidence <= 1.0):
                return False
        
        return True
    
    @staticmethod
    def validate_graph_config(config: Dict[str, Any]) -> List[str]:
        """Validate graph configuration and return list of issues."""
        
        issues = []
        
        # Check required fields
        required_fields = ['neo4j_uri', 'llm_model', 'embedding_model']
        for field in required_fields:
            if field not in config or not config[field]:
                issues.append(f"Missing required field: {field}")
        
        # Validate thresholds
        threshold_fields = ['entity_confidence_threshold', 'similarity_threshold']
        for field in threshold_fields:
            if field in config:
                value = config[field]
                if not (0.0 <= value <= 1.0):
                    issues.append(f"Invalid threshold value for {field}: {value}")
        
        return issues


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return performance_monitor