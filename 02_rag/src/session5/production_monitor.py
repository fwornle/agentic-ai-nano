# Production monitoring system
import time
import numpy as np
from typing import Dict, List, Any
from collections import defaultdict

class RAGProductionMonitor:
    """Continuous monitoring system for production RAG deployments."""
    
    def __init__(self, evaluation_framework, alert_thresholds: Dict):
        self.evaluation_framework = evaluation_framework
        self.alert_thresholds = alert_thresholds
        
        # Monitoring components
        self.performance_tracker = PerformanceTracker()
        self.quality_monitor = QualityMonitor()
        self.anomaly_detector = AnomalyDetector()
        
        # Monitoring data storage
        self.monitoring_data = {
            'performance_metrics': [],
            'quality_samples': [],
            'alerts': [],
            'system_health': []
        }
    
    def monitor_rag_interaction(self, query: str, response: str,
                              contexts: List[str], metadata: Dict) -> Dict[str, Any]:
        """Monitor individual RAG interaction."""
        
        monitoring_result = {
            'timestamp': time.time(),
            'query': query,
            'response': response,
            'contexts': contexts,
            'metadata': metadata
        }
        
        # Performance monitoring
        performance_metrics = self.performance_tracker.track_performance(
            query, response, contexts, metadata
        )
        monitoring_result['performance'] = performance_metrics
        
        # Quality assessment
        quality_scores = self.quality_monitor.assess_quality(
            query, response, contexts
        )
        monitoring_result['quality'] = quality_scores
        
        # Anomaly detection
        anomaly_flags = self.anomaly_detector.detect_anomalies(
            performance_metrics, quality_scores
        )
        monitoring_result['anomalies'] = anomaly_flags
        
        # Store monitoring data
        self._store_monitoring_data(monitoring_result)
        
        # Check alert conditions
        alerts = self._check_alert_conditions(monitoring_result)
        if alerts:
            self._trigger_alerts(alerts)
        
        return monitoring_result
    
    def _store_monitoring_data(self, monitoring_result: Dict):
        """Store monitoring data for analysis."""
        
        # Store performance metrics
        if 'performance' in monitoring_result:
            self.monitoring_data['performance_metrics'].append({
                'timestamp': monitoring_result['timestamp'],
                'metrics': monitoring_result['performance']
            })
        
        # Store quality samples
        if 'quality' in monitoring_result:
            self.monitoring_data['quality_samples'].append({
                'timestamp': monitoring_result['timestamp'],
                'quality': monitoring_result['quality']
            })
        
        # Limit storage size (keep last 1000 entries)
        max_entries = 1000
        for key in ['performance_metrics', 'quality_samples']:
            if len(self.monitoring_data[key]) > max_entries:
                self.monitoring_data[key] = self.monitoring_data[key][-max_entries:]
    
    def _check_alert_conditions(self, monitoring_result: Dict) -> List[Dict]:
        """Check if any alert conditions are met."""
        
        alerts = []
        
        # Quality alerts
        if 'quality' in monitoring_result:
            quality_data = monitoring_result['quality']
            
            if 'overall_quality' in quality_data:
                overall_score = quality_data['overall_quality']
                min_threshold = self.alert_thresholds.get('min_quality_score', 0.6)
                
                if overall_score < min_threshold:
                    alerts.append({
                        'type': 'quality_degradation',
                        'severity': 'high' if overall_score < min_threshold * 0.8 else 'medium',
                        'message': f"Overall quality score {overall_score:.3f} below threshold {min_threshold}",
                        'timestamp': monitoring_result['timestamp'],
                        'data': quality_data
                    })
        
        # Performance alerts
        if 'performance' in monitoring_result:
            performance_data = monitoring_result['performance']
            
            if 'response_time' in performance_data:
                response_time = performance_data['response_time']
                max_threshold = self.alert_thresholds.get('max_response_time', 5.0)
                
                if response_time > max_threshold:
                    alerts.append({
                        'type': 'performance_degradation',
                        'severity': 'high' if response_time > max_threshold * 2 else 'medium',
                        'message': f"Response time {response_time:.2f}s exceeds threshold {max_threshold}s",
                        'timestamp': monitoring_result['timestamp'],
                        'data': performance_data
                    })
        
        # Anomaly alerts
        if 'anomalies' in monitoring_result:
            anomaly_flags = monitoring_result['anomalies']
            
            for anomaly in anomaly_flags:
                alerts.append({
                    'type': 'anomaly_detected',
                    'severity': anomaly.get('severity', 'medium'),
                    'message': f"Anomaly detected: {anomaly['description']}",
                    'timestamp': monitoring_result['timestamp'],
                    'data': anomaly
                })
        
        return alerts
    
    def _trigger_alerts(self, alerts: List[Dict]):
        """Trigger alerts through configured channels."""
        
        for alert in alerts:
            # Store alert
            self.monitoring_data['alerts'].append(alert)
            
            # Log alert (in production, would send to alerting system)
            print(f"ALERT [{alert['severity'].upper()}] {alert['type']}: {alert['message']}")
    
    def get_system_health_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate system health report for specified time window."""
        
        current_time = time.time()
        cutoff_time = current_time - (time_window_hours * 3600)
        
        # Filter data to time window
        recent_performance = [
            entry for entry in self.monitoring_data['performance_metrics']
            if entry['timestamp'] > cutoff_time
        ]
        
        recent_quality = [
            entry for entry in self.monitoring_data['quality_samples']
            if entry['timestamp'] > cutoff_time
        ]
        
        recent_alerts = [
            alert for alert in self.monitoring_data['alerts']
            if alert['timestamp'] > cutoff_time
        ]
        
        # Calculate health metrics
        health_report = {
            'time_window_hours': time_window_hours,
            'total_interactions': len(recent_performance),
            'alert_count': len(recent_alerts),
            'alert_breakdown': self._analyze_alerts(recent_alerts),
            'performance_summary': self._summarize_performance(recent_performance),
            'quality_summary': self._summarize_quality(recent_quality),
            'system_status': self._determine_system_status(recent_alerts, recent_performance, recent_quality)
        }
        
        return health_report
    
    def _analyze_alerts(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Analyze alert patterns."""
        
        if not alerts:
            return {'total': 0, 'by_type': {}, 'by_severity': {}}
        
        alert_analysis = {
            'total': len(alerts),
            'by_type': defaultdict(int),
            'by_severity': defaultdict(int)
        }
        
        for alert in alerts:
            alert_analysis['by_type'][alert['type']] += 1
            alert_analysis['by_severity'][alert['severity']] += 1
        
        return dict(alert_analysis)
    
    def _summarize_performance(self, performance_data: List[Dict]) -> Dict[str, Any]:
        """Summarize performance metrics."""
        
        if not performance_data:
            return {'message': 'No performance data available'}
        
        # Extract response times
        response_times = []
        for entry in performance_data:
            if 'response_time' in entry['metrics']:
                response_times.append(entry['metrics']['response_time'])
        
        if response_times:
            return {
                'total_requests': len(performance_data),
                'avg_response_time': np.mean(response_times),
                'median_response_time': np.median(response_times),
                'p95_response_time': np.percentile(response_times, 95),
                'p99_response_time': np.percentile(response_times, 99)
            }
        else:
            return {'message': 'No response time data available'}
    
    def _summarize_quality(self, quality_data: List[Dict]) -> Dict[str, Any]:
        """Summarize quality metrics."""
        
        if not quality_data:
            return {'message': 'No quality data available'}
        
        # Extract overall quality scores
        quality_scores = []
        for entry in quality_data:
            if 'overall_quality' in entry['quality']:
                quality_scores.append(entry['quality']['overall_quality'])
        
        if quality_scores:
            return {
                'total_samples': len(quality_data),
                'avg_quality_score': np.mean(quality_scores),
                'median_quality_score': np.median(quality_scores),
                'min_quality_score': np.min(quality_scores),
                'quality_distribution': {
                    'excellent': sum(1 for score in quality_scores if score >= 0.8),
                    'good': sum(1 for score in quality_scores if 0.6 <= score < 0.8),
                    'poor': sum(1 for score in quality_scores if score < 0.6)
                }
            }
        else:
            return {'message': 'No quality score data available'}
    
    def _determine_system_status(self, alerts: List[Dict], 
                               performance_data: List[Dict],
                               quality_data: List[Dict]) -> str:
        """Determine overall system status."""
        
        # Check for critical alerts
        critical_alerts = [alert for alert in alerts if alert['severity'] == 'critical']
        if critical_alerts:
            return 'CRITICAL'
        
        # Check for high severity alerts
        high_alerts = [alert for alert in alerts if alert['severity'] == 'high']
        if high_alerts:
            return 'WARNING'
        
        # Check quality trends
        if quality_data:
            recent_quality_scores = []
            for entry in quality_data[-10:]:  # Last 10 samples
                if 'overall_quality' in entry['quality']:
                    recent_quality_scores.append(entry['quality']['overall_quality'])
            
            if recent_quality_scores:
                avg_recent_quality = np.mean(recent_quality_scores)
                if avg_recent_quality < 0.6:
                    return 'WARNING'
        
        # Default to healthy if no issues detected
        return 'HEALTHY'


class PerformanceTracker:
    """Track performance metrics for RAG interactions."""
    
    def __init__(self):
        self.start_time = None
    
    def track_performance(self, query: str, response: str, 
                         contexts: List[str], metadata: Dict) -> Dict[str, Any]:
        """Track performance metrics for a RAG interaction."""
        
        # Extract timing information from metadata if available
        response_time = metadata.get('response_time', 0.0)
        retrieval_time = metadata.get('retrieval_time', 0.0)
        generation_time = metadata.get('generation_time', 0.0)
        
        # Calculate additional metrics
        context_count = len(contexts)
        response_length = len(response.split())
        query_length = len(query.split())
        
        return {
            'response_time': response_time,
            'retrieval_time': retrieval_time,
            'generation_time': generation_time,
            'context_count': context_count,
            'response_length': response_length,
            'query_length': query_length,
            'throughput': 1.0 / max(response_time, 0.001)  # Requests per second
        }


class QualityMonitor:
    """Real-time quality monitoring for RAG responses."""
    
    def __init__(self, llm_judge=None):
        self.llm_judge = llm_judge
        
        # Quality assessment strategies
        self.quality_assessments = {
            'response_length': self._assess_response_length,
            'context_utilization': self._assess_context_utilization,
            'factual_consistency': self._assess_factual_consistency,
            'relevance_score': self._assess_relevance,
            'citation_quality': self._assess_citation_quality
        }
        
        # Quality baselines (would be learned from data)
        self.quality_baselines = {
            'response_length': {'min': 50, 'max': 500, 'optimal': 200},
            'context_utilization': {'min': 0.3, 'optimal': 0.7},
            'relevance_score': {'min': 0.6, 'optimal': 0.8},
            'citation_quality': {'min': 0.4, 'optimal': 0.7}
        }
    
    def assess_quality(self, query: str, response: str, 
                      contexts: List[str]) -> Dict[str, Any]:
        """Assess quality of RAG response."""
        
        quality_scores = {}
        quality_flags = []
        
        # Run all quality assessments
        for assessment_name, assessment_func in self.quality_assessments.items():
            try:
                score = assessment_func(query, response, contexts)
                quality_scores[assessment_name] = score
                
                # Check against baselines
                baseline = self.quality_baselines.get(assessment_name)
                if baseline and 'min' in baseline:
                    if score < baseline['min']:
                        quality_flags.append({
                            'type': 'quality_below_threshold',
                            'assessment': assessment_name,
                            'score': score,
                            'threshold': baseline['min']
                        })
                        
            except Exception as e:
                print(f"Quality assessment error for {assessment_name}: {e}")
                quality_scores[assessment_name] = None
        
        # Calculate overall quality score
        valid_scores = [score for score in quality_scores.values() if score is not None]
        overall_quality = np.mean(valid_scores) if valid_scores else 0.0
        
        return {
            'individual_scores': quality_scores,
            'overall_quality': overall_quality,
            'quality_flags': quality_flags,
            'assessment_timestamp': time.time()
        }
    
    def _assess_response_length(self, query: str, response: str, 
                              contexts: List[str]) -> float:
        """Assess if response length is appropriate."""
        
        response_length = len(response.split())
        baseline = self.quality_baselines['response_length']
        
        if response_length < baseline['min']:
            return response_length / baseline['min']  # Penalize too short
        elif response_length > baseline['max']:
            return baseline['max'] / response_length  # Penalize too long
        else:
            # Optimal range - score based on proximity to optimal
            distance_from_optimal = abs(response_length - baseline['optimal'])
            max_distance = max(baseline['optimal'] - baseline['min'], 
                             baseline['max'] - baseline['optimal'])
            return 1.0 - (distance_from_optimal / max_distance)
    
    def _assess_context_utilization(self, query: str, response: str,
                                  contexts: List[str]) -> float:
        """Assess how well the response utilizes provided contexts."""
        
        if not contexts:
            return 0.0
        
        # Simple word overlap assessment
        response_words = set(response.lower().split())
        
        utilization_scores = []
        for context in contexts:
            context_words = set(context.lower().split())
            overlap = len(response_words.intersection(context_words))
            context_utilization = overlap / len(context_words) if context_words else 0
            utilization_scores.append(context_utilization)
        
        # Return average utilization across all contexts
        return np.mean(utilization_scores) if utilization_scores else 0.0
    
    def _assess_factual_consistency(self, query: str, response: str,
                                  contexts: List[str]) -> float:
        """Assess factual consistency (placeholder implementation)."""
        # Placeholder - would use more sophisticated fact-checking
        return 0.8
    
    def _assess_relevance(self, query: str, response: str,
                        contexts: List[str]) -> float:
        """Assess response relevance to query (placeholder implementation)."""
        # Placeholder - would use semantic similarity
        return 0.75
    
    def _assess_citation_quality(self, query: str, response: str,
                               contexts: List[str]) -> float:
        """Assess citation quality (placeholder implementation)."""
        # Placeholder - would check for proper citations
        return 0.6


class AnomalyDetector:
    """Detect anomalies in RAG system behavior."""
    
    def __init__(self):
        self.baseline_metrics = {}
        self.anomaly_thresholds = {
            'response_time': {'z_score': 3.0, 'percentile': 95},
            'quality_score': {'z_score': 2.5, 'percentile': 5}
        }
    
    def detect_anomalies(self, performance_metrics: Dict, 
                        quality_metrics: Dict) -> List[Dict]:
        """Detect anomalies in performance and quality metrics."""
        
        anomalies = []
        
        # Check performance anomalies
        if 'response_time' in performance_metrics:
            response_time = performance_metrics['response_time']
            
            # Simple threshold-based detection
            if response_time > 10.0:  # 10 seconds threshold
                anomalies.append({
                    'type': 'performance_anomaly',
                    'metric': 'response_time',
                    'value': response_time,
                    'severity': 'high',
                    'description': f'Response time {response_time:.2f}s exceeds normal range'
                })
        
        # Check quality anomalies
        if 'overall_quality' in quality_metrics:
            quality_score = quality_metrics['overall_quality']
            
            # Simple threshold-based detection
            if quality_score < 0.3:  # Very low quality threshold
                anomalies.append({
                    'type': 'quality_anomaly',
                    'metric': 'overall_quality',
                    'value': quality_score,
                    'severity': 'high',
                    'description': f'Quality score {quality_score:.3f} is unusually low'
                })
        
        return anomalies
