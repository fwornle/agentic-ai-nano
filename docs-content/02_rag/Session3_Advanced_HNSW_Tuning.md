# ⚙️ Session 3: Advanced HNSW Tuning

## Prerequisites

**⚙️ IMPLEMENTER PATH CONTENT**
Complete these guides before starting:  
1. 🎯 [Observer Path](Session3_Vector_Databases_Search_Optimization.md)  
2. 📝 [Production Implementation](Session3_Production_Implementation.md)  
3. 📝 [Performance Optimization](Session3_Performance_Optimization.md)  

This guide provides deep expertise in HNSW parameter tuning, custom implementations, and enterprise optimization strategies.

## Part 1: Deep HNSW Theory and Mathematics

### HNSW Algorithm Fundamentals

HNSW creates a multi-layered graph structure that enables logarithmic search complexity in high-dimensional spaces. Understanding the mathematical foundations is crucial for advanced optimization:

```python
import faiss
import numpy as np
from typing import List, Dict, Tuple, Optional
import math
import logging
from dataclasses import dataclass

@dataclass
class HNSWParameters:
    """Complete HNSW parameter specification."""
    M: int                          # Maximum connections per node
    ef_construction: int            # Dynamic candidate list size during build
    ef_search: int                 # Dynamic candidate list size during search
    ml: float                      # Level generation probability factor
    max_M: int                     # Maximum connections for level 0
    max_M_L: int                   # Maximum connections for upper levels
    seed: int = 42                 # Random seed for reproducibility

class HNSWMathematicalAnalyzer:
    """Mathematical analysis of HNSW parameters."""

    def __init__(self):
        self.ln2 = math.log(2.0)

    def calculate_expected_layers(self, M: int) -> float:
        """Calculate expected number of layers for given M."""
        # Formula: E[layers] = -ln(1-1/ln(2)) / ln(2) * ln(2) ≈ 1/ln(2)
        # This is independent of M, approximately 1.44 layers on average
        return 1 / self.ln2

    def calculate_memory_usage(self, n_vectors: int, dimension: int,
                              params: HNSWParameters) -> Dict[str, float]:
        """Calculate detailed memory usage breakdown."""

        # Vector storage (float32)
        vector_storage_bytes = n_vectors * dimension * 4

        # Graph connectivity storage
        # Level 0: max_M connections per node
        # Upper levels: max_M_L connections per node
        expected_layers = self.calculate_expected_layers(params.M)

        # Approximation: most nodes are at level 0
        level_0_connections = n_vectors * params.max_M * 4  # 4 bytes per int32 index

        # Upper level connections (geometric decay)
        upper_connections = 0
        for level in range(1, int(expected_layers * 3)):  # 3x expected for safety
            nodes_at_level = n_vectors * (0.5 ** level)
            connections = nodes_at_level * params.max_M_L * 4
            upper_connections += connections

        # Metadata and overhead (approximately 20% of graph storage)
        metadata_bytes = (level_0_connections + upper_connections) * 0.2

        total_bytes = vector_storage_bytes + level_0_connections + upper_connections + metadata_bytes

        return {
            'vector_storage_mb': vector_storage_bytes / (1024**2),
            'level_0_connections_mb': level_0_connections / (1024**2),
            'upper_connections_mb': upper_connections / (1024**2),
            'metadata_mb': metadata_bytes / (1024**2),
            'total_mb': total_bytes / (1024**2),
            'per_vector_bytes': total_bytes / n_vectors
        }

    def estimate_build_time(self, n_vectors: int, dimension: int,
                          params: HNSWParameters) -> Dict[str, float]:
        """Estimate index build time based on parameters."""

        # Simplified build time model based on empirical observations
        # Build time grows roughly as O(n * log(n) * ef_construction * dimension)

        complexity_factor = n_vectors * math.log(n_vectors) * params.ef_construction * dimension

        # Base time per complexity unit (microseconds) - hardware dependent
        base_time_per_unit = 1e-8  # Approximate for modern CPU

        estimated_seconds = complexity_factor * base_time_per_unit

        # Additional factors
        construction_overhead = estimated_seconds * 0.2  # 20% overhead
        total_time = estimated_seconds + construction_overhead

        return {
            'estimated_build_seconds': total_time,
            'estimated_build_minutes': total_time / 60,
            'complexity_factor': complexity_factor,
            'scalability_analysis': self._analyze_scalability(params)
        }

    def _analyze_scalability(self, params: HNSWParameters) -> Dict[str, str]:
        """Analyze parameter scalability characteristics."""

        analysis = {}

        # M parameter analysis
        if params.M < 8:
            analysis['M'] = 'Low connectivity - fast build, reduced accuracy'
        elif params.M > 48:
            analysis['M'] = 'High connectivity - slow build, high accuracy, memory intensive'
        else:
            analysis['M'] = 'Balanced connectivity - good speed/accuracy tradeoff'

        # ef_construction analysis
        if params.ef_construction < 100:
            analysis['ef_construction'] = 'Fast build - may produce suboptimal graph quality'
        elif params.ef_construction > 400:
            analysis['ef_construction'] = 'Slow build - high graph quality, diminishing returns'
        else:
            analysis['ef_construction'] = 'Balanced build quality - good quality/speed tradeoff'

        return analysis
```

The mathematical analyzer provides theoretical foundations for parameter selection. The memory and build time calculations enable informed capacity planning.

### Advanced Parameter Selection Strategies

```python
class AdvancedHNSWOptimizer:
    """Advanced HNSW parameter optimization using empirical testing."""

    def __init__(self, test_vectors: np.ndarray, ground_truth_queries: List[Tuple]):
        self.test_vectors = test_vectors
        self.ground_truth_queries = ground_truth_queries  # List of (query_vector, expected_results)
        self.optimization_history = []

    def parameter_sweep(self, parameter_ranges: Dict) -> Dict:
        """Systematic parameter sweep with quality measurement."""

        results = []

        # Generate parameter combinations
        m_values = parameter_ranges.get('M', [16, 32, 48])
        ef_construction_values = parameter_ranges.get('ef_construction', [100, 200, 400])
        ef_search_values = parameter_ranges.get('ef_search', [50, 100, 200])

        total_combinations = len(m_values) * len(ef_construction_values) * len(ef_search_values)
        logging.info(f"Starting parameter sweep: {total_combinations} combinations")

        combination_count = 0

        for M in m_values:
            for ef_construction in ef_construction_values:
                for ef_search in ef_search_values:
                    combination_count += 1

                    params = HNSWParameters(
                        M=M,
                        ef_construction=ef_construction,
                        ef_search=ef_search,
                        ml=1/math.log(2.0),
                        max_M=M,
                        max_M_L=M
                    )

                    # Test this parameter combination
                    result = self._test_parameter_combination(params)
                    result['combination_id'] = combination_count
                    result['parameters'] = params

                    results.append(result)

                    if combination_count % 10 == 0:
                        logging.info(f"Completed {combination_count}/{total_combinations} combinations")

        # Analyze results
        analysis = self._analyze_sweep_results(results)

        return {
            'results': results,
            'analysis': analysis,
            'best_parameters': analysis['pareto_optimal'][0] if analysis['pareto_optimal'] else None
        }

    def _test_parameter_combination(self, params: HNSWParameters) -> Dict:
        """Test single parameter combination."""

        start_time = time.time()

        # Build index
        dimension = self.test_vectors.shape[1]
        index = faiss.IndexHNSWFlat(dimension, params.M)
        index.hnsw.efConstruction = params.ef_construction
        index.add(self.test_vectors)

        build_time = time.time() - start_time

        # Test search performance
        index.hnsw.efSearch = params.ef_search

        search_times = []
        recalls = []

        for query_vector, expected_results in self.ground_truth_queries[:100]:  # Test first 100 queries
            # Measure search time
            search_start = time.time()
            distances, indices = index.search(query_vector.reshape(1, -1), len(expected_results))
            search_time = time.time() - search_start
            search_times.append(search_time * 1000)  # Convert to ms

            # Calculate recall
            found_results = set(indices[0])
            expected_set = set(expected_results)
            recall = len(found_results.intersection(expected_set)) / len(expected_set)
            recalls.append(recall)

        # Calculate memory usage
        memory_analysis = HNSWMathematicalAnalyzer().calculate_memory_usage(
            len(self.test_vectors), dimension, params
        )

        return {
            'build_time_seconds': build_time,
            'avg_search_time_ms': np.mean(search_times),
            'p95_search_time_ms': np.percentile(search_times, 95),
            'avg_recall': np.mean(recalls),
            'memory_usage_mb': memory_analysis['total_mb'],
            'parameters': {
                'M': params.M,
                'ef_construction': params.ef_construction,
                'ef_search': params.ef_search
            }
        }

    def _analyze_sweep_results(self, results: List[Dict]) -> Dict:
        """Analyze parameter sweep results for optimal configurations."""

        # Sort by different criteria
        by_recall = sorted(results, key=lambda x: x['avg_recall'], reverse=True)
        by_speed = sorted(results, key=lambda x: x['avg_search_time_ms'])
        by_memory = sorted(results, key=lambda x: x['memory_usage_mb'])

        # Find Pareto optimal solutions (non-dominated configurations)
        pareto_optimal = []

        for result in results:
            is_pareto = True

            for other in results:
                if (other['avg_recall'] >= result['avg_recall'] and
                    other['avg_search_time_ms'] <= result['avg_search_time_ms'] and
                    other['memory_usage_mb'] <= result['memory_usage_mb'] and
                    (other['avg_recall'] > result['avg_recall'] or
                     other['avg_search_time_ms'] < result['avg_search_time_ms'] or
                     other['memory_usage_mb'] < result['memory_usage_mb'])):
                    is_pareto = False
                    break

            if is_pareto:
                pareto_optimal.append(result)

        # Sort Pareto optimal by balanced score
        for result in pareto_optimal:
            # Normalize metrics and create balanced score
            recall_score = result['avg_recall']
            speed_score = 1.0 / (1.0 + result['avg_search_time_ms'] / 100)  # Normalize around 100ms
            memory_score = 1.0 / (1.0 + result['memory_usage_mb'] / 1000)   # Normalize around 1GB

            result['balanced_score'] = (recall_score * 0.5 + speed_score * 0.3 + memory_score * 0.2)

        pareto_optimal.sort(key=lambda x: x['balanced_score'], reverse=True)

        return {
            'total_configurations': len(results),
            'best_recall': by_recall[0],
            'fastest_search': by_speed[0],
            'lowest_memory': by_memory[0],
            'pareto_optimal': pareto_optimal,
            'parameter_correlations': self._calculate_parameter_correlations(results)
        }

    def _calculate_parameter_correlations(self, results: List[Dict]) -> Dict:
        """Calculate correlations between parameters and performance metrics."""

        # Extract parameter and metric vectors
        M_values = [r['parameters']['M'] for r in results]
        ef_construction_values = [r['parameters']['ef_construction'] for r in results]
        ef_search_values = [r['parameters']['ef_search'] for r in results]

        recalls = [r['avg_recall'] for r in results]
        search_times = [r['avg_search_time_ms'] for r in results]
        memory_usage = [r['memory_usage_mb'] for r in results]

        # Calculate correlation coefficients (simplified Pearson)
        correlations = {}

        # M parameter correlations
        correlations['M_vs_recall'] = np.corrcoef(M_values, recalls)[0, 1]
        correlations['M_vs_search_time'] = np.corrcoef(M_values, search_times)[0, 1]
        correlations['M_vs_memory'] = np.corrcoef(M_values, memory_usage)[0, 1]

        # ef_construction correlations
        correlations['ef_construction_vs_recall'] = np.corrcoef(ef_construction_values, recalls)[0, 1]
        correlations['ef_construction_vs_build_time'] = np.corrcoef(
            ef_construction_values, [r['build_time_seconds'] for r in results]
        )[0, 1]

        # ef_search correlations
        correlations['ef_search_vs_recall'] = np.corrcoef(ef_search_values, recalls)[0, 1]
        correlations['ef_search_vs_search_time'] = np.corrcoef(ef_search_values, search_times)[0, 1]

        return correlations
```

The advanced optimizer uses systematic parameter sweeping with Pareto optimality analysis to find the best parameter configurations for specific use cases.

## Part 2: Custom HNSW Implementation Strategies

### Enterprise HNSW Wrapper

```python
class EnterpriseHNSWIndex:
    """Enterprise-grade HNSW with advanced features."""

    def __init__(self, dimension: int, config: Dict):
        self.dimension = dimension
        self.config = config
        self.index = None
        self.metadata_store = {}
        self.performance_tracker = {
            'build_time': 0,
            'search_count': 0,
            'total_search_time': 0,
            'parameter_adjustments': 0
        }

        # Advanced configuration
        self.adaptive_parameters = config.get('adaptive_parameters', True)
        self.quality_threshold = config.get('quality_threshold', 0.90)
        self.latency_threshold_ms = config.get('latency_threshold_ms', 100)

    def build_with_optimization(self, vectors: np.ndarray,
                               external_ids: List[str],
                               metadata: List[Dict] = None) -> Dict:
        """Build index with automatic parameter optimization."""

        logging.info(f"Building enterprise HNSW index for {len(vectors)} vectors")
        start_time = time.time()

        # Initial parameter selection based on dataset characteristics
        optimal_params = self._select_initial_parameters(vectors)

        # Build index with selected parameters
        self.index = faiss.IndexHNSWFlat(self.dimension, optimal_params.M)
        self.index.hnsw.efConstruction = optimal_params.ef_construction
        self.index.add(vectors)

        # Set initial search parameters
        self.index.hnsw.efSearch = optimal_params.ef_search

        # Store metadata
        if metadata:
            for i, (ext_id, meta) in enumerate(zip(external_ids, metadata)):
                self.metadata_store[ext_id] = {
                    'internal_id': i,
                    'metadata': meta,
                    'added_at': time.time()
                }

        build_time = time.time() - start_time
        self.performance_tracker['build_time'] = build_time

        # Validate index quality with sample queries
        quality_metrics = self._validate_index_quality(vectors[:1000])  # Sample validation

        build_report = {
            'build_time_seconds': build_time,
            'parameters_used': optimal_params.__dict__,
            'quality_metrics': quality_metrics,
            'memory_usage_mb': self._estimate_memory_usage(),
            'vectors_indexed': len(vectors)
        }

        logging.info(f"Index build completed in {build_time:.2f}s with {quality_metrics['avg_recall']:.3f} recall")

        return build_report

    def _select_initial_parameters(self, vectors: np.ndarray) -> HNSWParameters:
        """Select optimal parameters based on dataset characteristics."""

        n_vectors, dimension = vectors.shape

        # Dataset-based parameter selection
        if n_vectors < 10000:
            # Small dataset - prioritize accuracy
            M = 48
            ef_construction = 400
            ef_search = 200
        elif n_vectors < 100000:
            # Medium dataset - balanced approach
            M = 32
            ef_construction = 200
            ef_search = 128
        else:
            # Large dataset - prioritize speed and memory
            M = 16
            ef_construction = 128
            ef_search = 100

        # Adjust based on dimension
        if dimension > 1000:
            # High-dimensional data needs more connectivity
            M = min(64, M * 2)
            ef_construction = min(512, ef_construction * 1.5)

        return HNSWParameters(
            M=M,
            ef_construction=int(ef_construction),
            ef_search=int(ef_search),
            ml=1/math.log(2.0),
            max_M=M,
            max_M_L=M
        )

    def adaptive_search(self, query_vector: np.ndarray, top_k: int = 10,
                       quality_target: float = None) -> Dict:
        """Search with automatic parameter adaptation."""

        start_time = time.time()

        # Use quality target or default
        target_quality = quality_target or self.quality_threshold

        # Start with current ef_search
        current_ef = self.index.hnsw.efSearch
        max_ef = min(500, current_ef * 4)  # Don't go crazy with ef_search

        best_result = None
        best_quality = 0

        # Progressive ef_search increase if quality is insufficient
        for ef_search in [current_ef, current_ef * 2, max_ef]:
            self.index.hnsw.efSearch = ef_search

            # Perform search
            distances, indices = self.index.search(query_vector.reshape(1, -1), top_k * 2)

            # Estimate quality based on distance distribution
            quality_score = self._estimate_result_quality(distances[0])

            result = {
                'indices': indices[0][:top_k],
                'distances': distances[0][:top_k],
                'ef_search_used': ef_search,
                'quality_score': quality_score,
                'search_time_ms': (time.time() - start_time) * 1000
            }

            # Check if we've met quality target or time threshold
            if (quality_score >= target_quality or
                result['search_time_ms'] > self.latency_threshold_ms):
                best_result = result
                break

            best_result = result
            best_quality = quality_score

        # Update performance tracking
        self.performance_tracker['search_count'] += 1
        self.performance_tracker['total_search_time'] += best_result['search_time_ms']

        # Adaptive parameter adjustment
        if self.adaptive_parameters:
            self._adjust_parameters_based_on_performance(best_result)

        return best_result

    def _estimate_result_quality(self, distances: np.ndarray) -> float:
        """Estimate search result quality based on distance distribution."""

        if len(distances) < 2:
            return 1.0

        # Quality heuristic: good results have clear separation between top matches
        # and lower matches (large distance ratio)

        sorted_distances = np.sort(distances)

        # Calculate distance ratios
        ratios = []
        for i in range(1, min(5, len(sorted_distances))):  # Look at top 5 results
            if sorted_distances[i-1] > 0:
                ratio = sorted_distances[i] / sorted_distances[i-1]
                ratios.append(ratio)

        if not ratios:
            return 0.5

        # Higher ratios indicate better separation -> higher quality
        avg_ratio = np.mean(ratios)

        # Normalize to 0-1 scale (empirically determined)
        quality_score = min(1.0, max(0.0, (avg_ratio - 1.0) / 2.0))

        return quality_score

    def _adjust_parameters_based_on_performance(self, search_result: Dict):
        """Adjust ef_search based on recent performance."""

        # Get recent performance statistics
        if self.performance_tracker['search_count'] < 10:
            return  # Need more data

        avg_search_time = (self.performance_tracker['total_search_time'] /
                          self.performance_tracker['search_count'])

        current_ef = self.index.hnsw.efSearch

        # Adjustment logic
        if avg_search_time > self.latency_threshold_ms and current_ef > 32:
            # Searches are too slow - reduce ef_search
            new_ef = max(32, int(current_ef * 0.8))
            self.index.hnsw.efSearch = new_ef
            self.performance_tracker['parameter_adjustments'] += 1
            logging.info(f"Reduced ef_search from {current_ef} to {new_ef} due to high latency")

        elif (avg_search_time < self.latency_threshold_ms * 0.5 and
              search_result['quality_score'] < self.quality_threshold and
              current_ef < 256):
            # We have latency headroom and need better quality
            new_ef = min(256, int(current_ef * 1.25))
            self.index.hnsw.efSearch = new_ef
            self.performance_tracker['parameter_adjustments'] += 1
            logging.info(f"Increased ef_search from {current_ef} to {new_ef} for better quality")

        # Reset running averages periodically
        if self.performance_tracker['search_count'] % 1000 == 0:
            self.performance_tracker['total_search_time'] *= 0.1  # Keep 10% for trend
            self.performance_tracker['search_count'] = int(
                self.performance_tracker['search_count'] * 0.1
            )
```

The enterprise wrapper provides adaptive parameter tuning, quality monitoring, and comprehensive performance tracking for production environments.

## Part 3: Multi-Index and Distributed HNSW Strategies

### Hierarchical Index Architecture

```python
class HierarchicalHNSWSystem:
    """Multi-level HNSW system for ultra-large datasets."""

    def __init__(self, dimension: int, cluster_size: int = 100000):
        self.dimension = dimension
        self.cluster_size = cluster_size
        self.cluster_indexes = {}  # Cluster ID -> HNSW index
        self.cluster_centroids = None  # Cluster centroid vectors
        self.centroid_index = None    # HNSW index for centroids
        self.document_to_cluster = {}  # Document ID -> Cluster ID

    def build_hierarchical_index(self, vectors: np.ndarray,
                               document_ids: List[str],
                               cluster_method: str = 'kmeans') -> Dict:
        """Build hierarchical index with clustering."""

        logging.info(f"Building hierarchical HNSW for {len(vectors)} vectors")
        start_time = time.time()

        # Step 1: Cluster the vectors
        cluster_labels, centroids = self._cluster_vectors(vectors, cluster_method)
        self.cluster_centroids = centroids

        # Step 2: Build centroid index for cluster selection
        self.centroid_index = faiss.IndexHNSWFlat(self.dimension, 32)
        self.centroid_index.hnsw.efConstruction = 200
        self.centroid_index.add(centroids.astype(np.float32))

        # Step 3: Build individual cluster indexes
        cluster_build_times = {}

        for cluster_id in range(len(centroids)):
            cluster_mask = cluster_labels == cluster_id
            cluster_vectors = vectors[cluster_mask]
            cluster_doc_ids = [document_ids[i] for i in np.where(cluster_mask)[0]]

            if len(cluster_vectors) > 10:  # Skip tiny clusters
                # Build HNSW for this cluster
                cluster_index = faiss.IndexHNSWFlat(self.dimension, 16)
                cluster_index.hnsw.efConstruction = 100

                cluster_start = time.time()
                cluster_index.add(cluster_vectors.astype(np.float32))
                cluster_build_time = time.time() - cluster_start

                self.cluster_indexes[cluster_id] = {
                    'index': cluster_index,
                    'document_ids': cluster_doc_ids,
                    'size': len(cluster_vectors)
                }

                cluster_build_times[cluster_id] = cluster_build_time

                # Update document-to-cluster mapping
                for doc_id in cluster_doc_ids:
                    self.document_to_cluster[doc_id] = cluster_id

        total_build_time = time.time() - start_time

        return {
            'total_build_time': total_build_time,
            'num_clusters': len(self.cluster_indexes),
            'cluster_sizes': [info['size'] for info in self.cluster_indexes.values()],
            'avg_cluster_build_time': np.mean(list(cluster_build_times.values())),
            'centroid_index_size': len(centroids)
        }

    def _cluster_vectors(self, vectors: np.ndarray,
                        method: str) -> Tuple[np.ndarray, np.ndarray]:
        """Cluster vectors using specified method."""

        n_clusters = max(1, len(vectors) // self.cluster_size)

        if method == 'kmeans':
            # Use FAISS k-means for efficiency
            kmeans = faiss.Kmeans(self.dimension, n_clusters, niter=20)
            kmeans.train(vectors.astype(np.float32))

            # Get cluster assignments
            distances, labels = kmeans.index.search(vectors.astype(np.float32), 1)
            cluster_labels = labels.flatten()
            centroids = kmeans.centroids

        elif method == 'hierarchical_kmeans':
            # Hierarchical clustering for better quality
            cluster_labels, centroids = self._hierarchical_kmeans(vectors, n_clusters)

        else:
            raise ValueError(f"Unknown clustering method: {method}")

        return cluster_labels, centroids

    def hierarchical_search(self, query_vector: np.ndarray,
                          top_k: int = 10,
                          num_clusters_to_search: int = 3) -> List[Dict]:
        """Perform hierarchical search across clusters."""

        start_time = time.time()

        # Step 1: Find most relevant clusters
        self.centroid_index.hnsw.efSearch = min(num_clusters_to_search * 2, 50)
        centroid_distances, centroid_indices = self.centroid_index.search(
            query_vector.reshape(1, -1),
            num_clusters_to_search
        )

        cluster_search_time = time.time() - start_time

        # Step 2: Search within selected clusters
        all_results = []

        for i, cluster_id in enumerate(centroid_indices[0]):
            if cluster_id in self.cluster_indexes:
                cluster_info = self.cluster_indexes[cluster_id]
                cluster_index = cluster_info['index']

                # Search within cluster
                cluster_index.hnsw.efSearch = top_k * 2
                distances, indices = cluster_index.search(
                    query_vector.reshape(1, -1),
                    min(top_k * 2, cluster_info['size'])
                )

                # Add cluster context to results
                for j, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx != -1:
                        all_results.append({
                            'document_id': cluster_info['document_ids'][idx],
                            'distance': float(distance),
                            'cluster_id': cluster_id,
                            'cluster_distance': float(centroid_distances[0][i]),
                            'within_cluster_rank': j + 1
                        })

        # Step 3: Global ranking of results
        all_results.sort(key=lambda x: x['distance'])
        final_results = all_results[:top_k]

        total_search_time = time.time() - start_time

        # Add search metadata
        for result in final_results:
            result['total_search_time_ms'] = total_search_time * 1000
            result['cluster_search_time_ms'] = cluster_search_time * 1000

        return final_results

    def get_cluster_statistics(self) -> Dict:
        """Get comprehensive cluster statistics."""

        cluster_sizes = [info['size'] for info in self.cluster_indexes.values()]

        return {
            'total_clusters': len(self.cluster_indexes),
            'total_documents': sum(cluster_sizes),
            'avg_cluster_size': np.mean(cluster_sizes),
            'median_cluster_size': np.median(cluster_sizes),
            'min_cluster_size': min(cluster_sizes) if cluster_sizes else 0,
            'max_cluster_size': max(cluster_sizes) if cluster_sizes else 0,
            'cluster_size_std': np.std(cluster_sizes),
            'memory_usage_estimate_mb': self._estimate_total_memory_usage()
        }

    def _estimate_total_memory_usage(self) -> float:
        """Estimate total memory usage across all indexes."""

        total_mb = 0

        # Centroid index
        if self.centroid_index:
            total_mb += len(self.cluster_centroids) * self.dimension * 4 / (1024**2)

        # Cluster indexes
        for cluster_info in self.cluster_indexes.values():
            cluster_size = cluster_info['size']
            # Approximate HNSW memory usage
            total_mb += cluster_size * (self.dimension * 4 + 16 * 4) / (1024**2)

        return total_mb
```

The hierarchical system enables handling of ultra-large datasets by intelligent clustering and multi-level search strategies.

## Part 4: Advanced Optimization Techniques

### Dynamic Index Optimization

```python
class DynamicHNSWOptimizer:
    """Real-time HNSW optimization based on query patterns."""

    def __init__(self, index_system, optimization_interval: int = 1000):
        self.index_system = index_system
        self.optimization_interval = optimization_interval
        self.query_history = deque(maxlen=optimization_interval * 2)
        self.optimization_history = []

        # Performance tracking
        self.performance_metrics = {
            'avg_latency_ms': 0,
            'p95_latency_ms': 0,
            'avg_recall': 0,
            'queries_processed': 0
        }

    def record_query_performance(self, query_vector: np.ndarray,
                               search_results: List[Dict],
                               search_time_ms: float,
                               estimated_recall: float = None):
        """Record query performance for optimization analysis."""

        query_record = {
            'timestamp': time.time(),
            'query_vector': query_vector,
            'search_time_ms': search_time_ms,
            'num_results': len(search_results),
            'estimated_recall': estimated_recall,
            'result_distances': [r.get('distance', 0) for r in search_results[:5]]
        }

        self.query_history.append(query_record)
        self.performance_metrics['queries_processed'] += 1

        # Update running averages
        self._update_performance_metrics(search_time_ms, estimated_recall)

        # Check if optimization is needed
        if len(self.query_history) >= self.optimization_interval:
            if self._should_optimize():
                self._perform_optimization()

    def _update_performance_metrics(self, search_time_ms: float,
                                  estimated_recall: float = None):
        """Update running performance metrics."""

        # Update latency metrics
        recent_queries = list(self.query_history)[-100:]  # Last 100 queries
        if recent_queries:
            latencies = [q['search_time_ms'] for q in recent_queries]
            self.performance_metrics['avg_latency_ms'] = np.mean(latencies)
            self.performance_metrics['p95_latency_ms'] = np.percentile(latencies, 95)

            if estimated_recall is not None:
                recalls = [q['estimated_recall'] for q in recent_queries
                          if q['estimated_recall'] is not None]
                if recalls:
                    self.performance_metrics['avg_recall'] = np.mean(recalls)

    def _should_optimize(self) -> bool:
        """Determine if optimization is warranted."""

        # Optimization triggers
        conditions = [
            self.performance_metrics['p95_latency_ms'] > 200,  # High latency
            self.performance_metrics['avg_recall'] < 0.85,    # Low recall
            len(self.optimization_history) == 0,              # Never optimized
            # Periodically optimize regardless
            self.performance_metrics['queries_processed'] % (self.optimization_interval * 10) == 0
        ]

        return any(conditions)

    def _perform_optimization(self):
        """Perform intelligent optimization based on query patterns."""

        logging.info("Starting dynamic HNSW optimization")
        optimization_start = time.time()

        # Analyze query patterns
        query_analysis = self._analyze_query_patterns()

        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(query_analysis)

        # Apply optimizations
        applied_optimizations = []

        for rec in recommendations:
            if rec['type'] == 'ef_search_adjustment':
                old_ef = self.index_system.index.hnsw.efSearch
                new_ef = rec['new_value']
                self.index_system.index.hnsw.efSearch = new_ef

                applied_optimizations.append({
                    'type': 'ef_search',
                    'old_value': old_ef,
                    'new_value': new_ef,
                    'reason': rec['reason']
                })

            elif rec['type'] == 'cluster_rebalancing':
                # For hierarchical systems, trigger cluster rebalancing
                if hasattr(self.index_system, 'rebalance_clusters'):
                    self.index_system.rebalance_clusters()
                    applied_optimizations.append({
                        'type': 'cluster_rebalancing',
                        'reason': rec['reason']
                    })

        # Record optimization
        optimization_record = {
            'timestamp': time.time(),
            'optimization_time_seconds': time.time() - optimization_start,
            'query_analysis': query_analysis,
            'applied_optimizations': applied_optimizations,
            'performance_before': dict(self.performance_metrics)
        }

        self.optimization_history.append(optimization_record)

        # Reset query history to measure optimization impact
        self.query_history.clear()

        logging.info(f"Optimization completed: {len(applied_optimizations)} changes applied")

    def _analyze_query_patterns(self) -> Dict:
        """Analyze recent query patterns for optimization insights."""

        recent_queries = list(self.query_history)

        if not recent_queries:
            return {}

        # Latency analysis
        latencies = [q['search_time_ms'] for q in recent_queries]
        latency_analysis = {
            'mean': np.mean(latencies),
            'std': np.std(latencies),
            'p95': np.percentile(latencies, 95),
            'trend': self._calculate_latency_trend(latencies)
        }

        # Recall analysis
        recalls = [q['estimated_recall'] for q in recent_queries
                  if q['estimated_recall'] is not None]

        recall_analysis = {
            'mean': np.mean(recalls) if recalls else None,
            'std': np.std(recalls) if recalls else None,
            'samples': len(recalls)
        }

        # Query similarity analysis
        query_vectors = np.array([q['query_vector'] for q in recent_queries[-100:]])
        similarity_analysis = self._analyze_query_similarity(query_vectors)

        return {
            'latency': latency_analysis,
            'recall': recall_analysis,
            'query_similarity': similarity_analysis,
            'total_queries_analyzed': len(recent_queries)
        }

    def _generate_optimization_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate optimization recommendations based on analysis."""

        recommendations = []

        # Latency-based recommendations
        if analysis.get('latency', {}).get('p95', 0) > 200:
            current_ef = self.index_system.index.hnsw.efSearch
            new_ef = max(32, int(current_ef * 0.8))

            recommendations.append({
                'type': 'ef_search_adjustment',
                'new_value': new_ef,
                'reason': f'High P95 latency ({analysis["latency"]["p95"]:.1f}ms) - reducing ef_search',
                'expected_impact': 'Faster searches, slightly lower recall'
            })

        # Recall-based recommendations
        if analysis.get('recall', {}).get('mean', 1.0) < 0.85:
            current_ef = self.index_system.index.hnsw.efSearch
            new_ef = min(256, int(current_ef * 1.25))

            recommendations.append({
                'type': 'ef_search_adjustment',
                'new_value': new_ef,
                'reason': f'Low recall ({analysis["recall"]["mean"]:.3f}) - increasing ef_search',
                'expected_impact': 'Better recall, slower searches'
            })

        # Query pattern recommendations
        if analysis.get('query_similarity', {}).get('avg_similarity', 0) > 0.8:
            recommendations.append({
                'type': 'cluster_rebalancing',
                'reason': 'High query similarity detected - may benefit from specialized clusters',
                'expected_impact': 'Better cache locality and specialized optimization'
            })

        return recommendations

    def _calculate_latency_trend(self, latencies: List[float]) -> str:
        """Calculate latency trend over time."""

        if len(latencies) < 10:
            return 'insufficient_data'

        # Simple linear trend calculation
        x = np.arange(len(latencies))
        slope, _ = np.polyfit(x, latencies, 1)

        if slope > 1:
            return 'increasing'
        elif slope < -1:
            return 'decreasing'
        else:
            return 'stable'

    def _analyze_query_similarity(self, query_vectors: np.ndarray) -> Dict:
        """Analyze similarity patterns in recent queries."""

        if len(query_vectors) < 2:
            return {'avg_similarity': 0, 'similarity_std': 0}

        # Calculate pairwise similarities for a sample
        sample_size = min(50, len(query_vectors))
        sample_indices = np.random.choice(len(query_vectors), sample_size, replace=False)
        sample_vectors = query_vectors[sample_indices]

        similarities = []
        for i in range(len(sample_vectors)):
            for j in range(i+1, len(sample_vectors)):
                # Cosine similarity
                sim = np.dot(sample_vectors[i], sample_vectors[j]) / (
                    np.linalg.norm(sample_vectors[i]) * np.linalg.norm(sample_vectors[j])
                )
                similarities.append(sim)

        return {
            'avg_similarity': np.mean(similarities) if similarities else 0,
            'similarity_std': np.std(similarities) if similarities else 0,
            'sample_size': sample_size
        }
```

The dynamic optimizer continuously adapts HNSW parameters based on real-time performance analysis and query patterns.

## Key Advanced HNSW Principles

### Deep Optimization Insights

**Mathematical Foundations:**  
- HNSW creates logarithmic search complexity through hierarchical graph structure  
- Parameter selection requires balancing connectivity, build time, and memory usage  
- Pareto optimality analysis reveals optimal configurations for different use cases  

**Enterprise Implementation:**  
- Adaptive parameter tuning responds to real-time performance requirements  
- Hierarchical clustering enables ultra-large dataset handling  
- Quality estimation guides automatic optimization decisions  

**Production Optimization:**  
- Dynamic optimization adapts to changing query patterns  
- Multi-level indexes provide scalability beyond single-node limitations  
- Comprehensive performance tracking enables data-driven optimization  

## Implementation Recommendations

1. **Parameter Selection**: Use systematic parameter sweeps with quality measurement  
2. **Adaptive Systems**: Implement real-time parameter adjustment based on performance  
3. **Scalability**: Consider hierarchical approaches for datasets >1M vectors  
4. **Monitoring**: Track both performance metrics and parameter effectiveness  
5. **Quality Assurance**: Validate optimizations with ground-truth testing
---

## Navigation

**Previous:** [Session 2 - Implementation →](Session2_*.md)  
**Next:** [Session 4 - Team Orchestration →](Session4_*.md)

---
