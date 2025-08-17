# Production monitoring and observability system
from typing import Dict, Any, List, Callable, Optional
import time
import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Prometheus and structured logging imports
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
except ImportError:
    # Fallback if prometheus not available
    prometheus_client = None

try:
    import structlog
except ImportError:
    import logging as structlog


class RAGMonitoringSystem:
    """Comprehensive monitoring and observability for production RAG systems."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Prometheus metrics (if available)
        if prometheus_client:
            self._setup_prometheus_metrics()
        
        # Structured logging
        self.logger = structlog.get_logger()
        
        # Performance tracking
        self.performance_tracker = RAGPerformanceTracker()
        
        # Alert manager
        self.alert_manager = RAGAlertManager(config.get('alerting', {}))
        
        # Analytics dashboard
        self.analytics = RAGAnalytics(config.get('analytics', {}))
        
        # Health checker
        self.health_checker = RAGHealthChecker()
        
    def _setup_prometheus_metrics(self):
        """Set up Prometheus metrics for RAG system monitoring."""
        
        # Request metrics
        self.request_counter = Counter(
            'rag_requests_total',
            'Total number of RAG requests',
            ['method', 'endpoint', 'status']
        )
        
        self.request_duration = Histogram(
            'rag_request_duration_seconds',
            'RAG request duration in seconds',
            ['method', 'endpoint']
        )
        
        # System metrics
        self.active_connections = Gauge(
            'rag_active_connections',
            'Number of active connections',
            ['service']
        )
        
        self.queue_size = Gauge(
            'rag_queue_size',
            'Size of processing queues',
            ['queue_type']
        )
        
        # Quality metrics
        self.response_quality = Histogram(
            'rag_response_quality',
            'Response quality scores',
            ['query_type']
        )
        
        self.retrieval_accuracy = Histogram(
            'rag_retrieval_accuracy',
            'Retrieval accuracy scores',
            ['retrieval_method']
        )
        
        # Error metrics
        self.error_counter = Counter(
            'rag_errors_total',
            'Total number of errors',
            ['error_type', 'service']
        )
        
        # Start Prometheus metrics server
        metrics_port = self.config.get('metrics_port', 8000)
        try:
            start_http_server(metrics_port)
        except Exception as e:
            self.logger.warning(f"Failed to start Prometheus server: {e}")
    
    async def track_request(self, method: str, endpoint: str, 
                          request_func: Callable) -> Dict[str, Any]:
        """Track RAG request with comprehensive monitoring."""
        
        start_time = time.time()
        
        # Use Prometheus histogram timer if available
        timer_context = None
        if hasattr(self, 'request_duration'):
            timer_context = self.request_duration.labels(method=method, endpoint=endpoint).time()
            timer_context.__enter__()
        
        try:
            # Execute request
            result = await request_func()
            
            # Record successful request
            if hasattr(self, 'request_counter'):
                self.request_counter.labels(
                    method=method, endpoint=endpoint, status='success'
                ).inc()
            
            # Track quality metrics if available
            if 'quality_score' in result and hasattr(self, 'response_quality'):
                query_type = result.get('query_type', 'unknown')
                self.response_quality.labels(query_type=query_type).observe(
                    result['quality_score']
                )
            
            # Log structured request info
            self.logger.info(
                "RAG request completed",
                method=method,
                endpoint=endpoint,
                duration=time.time() - start_time,
                quality_score=result.get('quality_score'),
                sources_retrieved=result.get('sources_count', 0)
            )
            
            return result
            
        except Exception as e:
            # Record failed request
            if hasattr(self, 'request_counter'):
                self.request_counter.labels(
                    method=method, endpoint=endpoint, status='error'
                ).inc()
            
            # Record error
            error_type = type(e).__name__
            if hasattr(self, 'error_counter'):
                self.error_counter.labels(
                    error_type=error_type, service=endpoint
                ).inc()
            
            # Log error
            self.logger.error(
                "RAG request failed",
                method=method,
                endpoint=endpoint,
                error=str(e),
                duration=time.time() - start_time
            )
            
            # Check if alert should be triggered
            await self.alert_manager.check_error_threshold(endpoint, error_type)
            
            raise
            
        finally:
            if timer_context:
                timer_context.__exit__(None, None, None)
    
    def update_queue_metrics(self, queue_type: str, size: int):
        """Update queue size metrics."""
        if hasattr(self, 'queue_size'):
            self.queue_size.labels(queue_type=queue_type).set(size)
    
    def update_connection_metrics(self, service: str, connections: int):
        """Update active connections metrics."""
        if hasattr(self, 'active_connections'):
            self.active_connections.labels(service=service).set(connections)


class RAGPerformanceTracker:
    """Track performance metrics for RAG operations."""
    
    def __init__(self):
        self.performance_history = []
        self.current_metrics = {}
        
    def record_operation(self, operation: str, duration: float, 
                        success: bool, metadata: Dict = None):
        """Record a single operation performance."""
        
        performance_record = {
            'operation': operation,
            'duration': duration,
            'success': success,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        
        self.performance_history.append(performance_record)
        
        # Update current metrics
        if operation not in self.current_metrics:
            self.current_metrics[operation] = {
                'total_operations': 0,
                'successful_operations': 0,
                'total_duration': 0.0,
                'average_duration': 0.0,
                'success_rate': 0.0
            }
        
        metrics = self.current_metrics[operation]
        metrics['total_operations'] += 1
        if success:
            metrics['successful_operations'] += 1
        metrics['total_duration'] += duration
        metrics['average_duration'] = metrics['total_duration'] / metrics['total_operations']
        metrics['success_rate'] = metrics['successful_operations'] / metrics['total_operations']
    
    def get_performance_summary(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified time window."""
        
        cutoff_time = time.time() - (time_window_hours * 3600)
        recent_records = [
            record for record in self.performance_history
            if record['timestamp'] > cutoff_time
        ]
        
        if not recent_records:
            return {'error': 'No performance data in time window'}
        
        # Calculate aggregate metrics
        total_operations = len(recent_records)
        successful_operations = len([r for r in recent_records if r['success']])
        total_duration = sum(r['duration'] for r in recent_records)
        
        durations = [r['duration'] for r in recent_records]
        
        return {
            'time_window_hours': time_window_hours,
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'success_rate': successful_operations / total_operations,
            'average_duration': total_duration / total_operations,
            'median_duration': float(np.median(durations)),
            'p95_duration': float(np.percentile(durations, 95)),
            'p99_duration': float(np.percentile(durations, 99)),
            'operations_per_hour': total_operations / time_window_hours
        }


class RAGAlertManager:
    """Alert manager for RAG system monitoring."""
    
    def __init__(self, alert_config: Dict[str, Any]):
        self.config = alert_config
        self.alert_thresholds = {
            'error_rate': alert_config.get('error_rate_threshold', 0.05),  # 5%
            'response_time_p95': alert_config.get('response_time_threshold', 2.0),  # 2 seconds
            'queue_size': alert_config.get('queue_size_threshold', 1000),
            'disk_usage': alert_config.get('disk_usage_threshold', 0.85),  # 85%
            'memory_usage': alert_config.get('memory_usage_threshold', 0.80)  # 80%
        }
        
        self.error_counts = {}
        self.alert_cooldowns = {}
        self.logger = logging.getLogger(__name__)
    
    async def check_error_threshold(self, service: str, error_type: str):
        """Check if error threshold is exceeded and trigger alert if needed."""
        
        current_time = time.time()
        
        # Track error count
        error_key = f"{service}:{error_type}"
        if error_key not in self.error_counts:
            self.error_counts[error_key] = []
        
        self.error_counts[error_key].append(current_time)
        
        # Clean old error records (keep last hour)
        cutoff_time = current_time - 3600
        self.error_counts[error_key] = [
            t for t in self.error_counts[error_key] if t > cutoff_time
        ]
        
        # Calculate error rate
        error_count = len(self.error_counts[error_key])
        error_rate = error_count / 100  # Assuming 100 requests per hour as baseline
        
        # Check threshold
        if error_rate > self.alert_thresholds['error_rate']:
            await self._trigger_alert(
                'high_error_rate',
                f"High error rate for {service}:{error_type}",
                {'error_rate': error_rate, 'threshold': self.alert_thresholds['error_rate']}
            )
    
    async def check_performance_threshold(self, metric: str, value: float, 
                                        service: str = 'unknown'):
        """Check if performance threshold is exceeded."""
        
        if metric in self.alert_thresholds and value > self.alert_thresholds[metric]:
            await self._trigger_alert(
                f'high_{metric}',
                f"High {metric} for {service}",
                {'value': value, 'threshold': self.alert_thresholds[metric]}
            )
    
    async def _trigger_alert(self, alert_type: str, message: str, 
                           details: Dict[str, Any]):
        """Trigger an alert with cooldown protection."""
        
        current_time = time.time()
        cooldown_period = self.config.get('alert_cooldown', 300)  # 5 minutes
        
        # Check cooldown
        if alert_type in self.alert_cooldowns:
            if current_time - self.alert_cooldowns[alert_type] < cooldown_period:
                return  # Skip alert due to cooldown
        
        # Log alert
        self.logger.warning(
            f"ALERT: {alert_type} - {message}",
            extra={'alert_details': details}
        )
        
        # Send alert notifications
        await self._send_alert_notifications(alert_type, message, details)
        
        # Update cooldown
        self.alert_cooldowns[alert_type] = current_time
    
    async def _send_alert_notifications(self, alert_type: str, message: str, 
                                      details: Dict[str, Any]):
        """Send alert notifications to configured channels."""
        
        # Email notifications
        if self.config.get('email_alerts'):
            await self._send_email_alert(alert_type, message, details)
        
        # Slack notifications
        if self.config.get('slack_webhook'):
            await self._send_slack_alert(alert_type, message, details)
        
        # PagerDuty for critical alerts
        if alert_type in self.config.get('critical_alerts', []):
            await self._send_pagerduty_alert(alert_type, message, details)
    
    async def _send_email_alert(self, alert_type: str, message: str, details: Dict):
        """Send email alert - placeholder implementation."""
        self.logger.info(f"Email alert would be sent: {alert_type} - {message}")
    
    async def _send_slack_alert(self, alert_type: str, message: str, details: Dict):
        """Send Slack alert - placeholder implementation."""
        self.logger.info(f"Slack alert would be sent: {alert_type} - {message}")
    
    async def _send_pagerduty_alert(self, alert_type: str, message: str, details: Dict):
        """Send PagerDuty alert - placeholder implementation."""
        self.logger.info(f"PagerDuty alert would be sent: {alert_type} - {message}")


class RAGAnalytics:
    """Advanced analytics for RAG system performance and usage."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analytics_data = {}
        
        # Time series storage for metrics
        self.metrics_store = MetricsTimeSeriesStore()
        
        # Query pattern analyzer
        self.query_analyzer = QueryPatternAnalyzer()
        
        # Performance predictor
        self.performance_predictor = PerformancePredictor()
        
    async def analyze_system_performance(self, time_window: str = '1h') -> Dict[str, Any]:
        """Analyze comprehensive system performance over time window."""
        
        # Get metrics for time window
        metrics = await self.metrics_store.get_metrics_window(time_window)
        
        # Calculate performance indicators
        performance_analysis = {
            'request_volume': self._analyze_request_volume(metrics),
            'response_times': self._analyze_response_times(metrics),
            'quality_trends': self._analyze_quality_trends(metrics),
            'error_patterns': self._analyze_error_patterns(metrics),
            'resource_usage': self._analyze_resource_usage(metrics),
            'user_satisfaction': self._analyze_user_satisfaction(metrics)
        }
        
        # Identify performance issues
        performance_issues = self._identify_performance_issues(performance_analysis)
        
        # Generate recommendations
        recommendations = self._generate_performance_recommendations(
            performance_analysis, performance_issues
        )
        
        return {
            'analysis_period': time_window,
            'performance_analysis': performance_analysis,
            'identified_issues': performance_issues,
            'recommendations': recommendations,
            'overall_health_score': self._calculate_health_score(performance_analysis)
        }
    
    def _analyze_request_volume(self, metrics: Dict[str, List]) -> Dict[str, Any]:
        """Analyze request volume patterns and trends."""
        
        request_counts = metrics.get('request_counts', [])
        
        if not request_counts:
            return {'error': 'No request data available'}
        
        # Calculate volume statistics
        total_requests = sum(request_counts)
        avg_requests_per_minute = total_requests / len(request_counts)
        peak_requests = max(request_counts)
        
        # Identify trends
        trend = 'stable'
        if len(request_counts) > 10:
            recent_avg = np.mean(request_counts[-10:])
            earlier_avg = np.mean(request_counts[:10])
            
            if recent_avg > earlier_avg * 1.2:
                trend = 'increasing'
            elif recent_avg < earlier_avg * 0.8:
                trend = 'decreasing'
        
        return {
            'total_requests': total_requests,
            'average_per_minute': avg_requests_per_minute,
            'peak_requests': peak_requests,
            'trend': trend,
            'volume_distribution': {
                'p50': float(np.percentile(request_counts, 50)),
                'p95': float(np.percentile(request_counts, 95)),
                'p99': float(np.percentile(request_counts, 99))
            }
        }
    
    def _analyze_response_times(self, metrics: Dict[str, List]) -> Dict[str, Any]:
        """Analyze response time patterns."""
        
        response_times = metrics.get('response_times', [])
        
        if not response_times:
            return {'error': 'No response time data available'}
        
        return {
            'average': float(np.mean(response_times)),
            'median': float(np.median(response_times)),
            'p95': float(np.percentile(response_times, 95)),
            'p99': float(np.percentile(response_times, 99)),
            'min': float(np.min(response_times)),
            'max': float(np.max(response_times)),
            'std_dev': float(np.std(response_times))
        }
    
    def _analyze_quality_trends(self, metrics: Dict[str, List]) -> Dict[str, Any]:
        """Analyze response quality trends."""
        
        quality_scores = metrics.get('quality_scores', [])
        
        if not quality_scores:
            return {'error': 'No quality score data available'}
        
        return {
            'average_score': float(np.mean(quality_scores)),
            'median_score': float(np.median(quality_scores)),
            'quality_distribution': {
                'excellent': len([s for s in quality_scores if s >= 0.9]) / len(quality_scores),
                'good': len([s for s in quality_scores if 0.7 <= s < 0.9]) / len(quality_scores),
                'fair': len([s for s in quality_scores if 0.5 <= s < 0.7]) / len(quality_scores),
                'poor': len([s for s in quality_scores if s < 0.5]) / len(quality_scores)
            }
        }
    
    def _analyze_error_patterns(self, metrics: Dict[str, List]) -> Dict[str, Any]:
        """Analyze error patterns and frequencies."""
        
        error_counts = metrics.get('error_counts', [])
        total_requests = sum(metrics.get('request_counts', [1]))
        
        total_errors = sum(error_counts) if error_counts else 0
        error_rate = total_errors / max(total_requests, 1)
        
        return {
            'total_errors': total_errors,
            'error_rate': error_rate,
            'errors_trend': self._calculate_trend(error_counts) if error_counts else 'stable'
        }
    
    def _analyze_resource_usage(self, metrics: Dict[str, List]) -> Dict[str, Any]:
        """Analyze system resource usage."""
        
        cpu_usage = metrics.get('cpu_usage', [50])  # Default values
        memory_usage = metrics.get('memory_usage', [40])
        
        return {
            'cpu_utilization': float(np.mean(cpu_usage)),
            'memory_utilization': float(np.mean(memory_usage)),
            'cpu_peak': float(np.max(cpu_usage)),
            'memory_peak': float(np.max(memory_usage))
        }
    
    def _analyze_user_satisfaction(self, metrics: Dict[str, List]) -> Dict[str, Any]:
        """Analyze user satisfaction metrics."""
        
        # Combine quality scores and response times for satisfaction estimate
        quality_scores = metrics.get('quality_scores', [0.7])
        response_times = metrics.get('response_times', [1.0])
        
        # Simple satisfaction model
        avg_quality = np.mean(quality_scores)
        avg_response_time = np.mean(response_times)
        
        # Satisfaction decreases with higher response times
        time_penalty = max(0, (avg_response_time - 1.0) * 0.2)
        satisfaction_score = max(0, avg_quality - time_penalty)
        
        return {
            'satisfaction_score': float(satisfaction_score),
            'quality_component': float(avg_quality),
            'response_time_component': float(avg_response_time),
            'satisfaction_category': self._categorize_satisfaction(satisfaction_score)
        }
    
    def _categorize_satisfaction(self, score: float) -> str:
        """Categorize satisfaction score."""
        if score >= 0.8:
            return 'excellent'
        elif score >= 0.6:
            return 'good'
        elif score >= 0.4:
            return 'fair'
        else:
            return 'poor'
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from time series values."""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend
        recent_avg = np.mean(values[-len(values)//2:])
        earlier_avg = np.mean(values[:len(values)//2])
        
        if recent_avg > earlier_avg * 1.1:
            return 'increasing'
        elif recent_avg < earlier_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _identify_performance_issues(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance issues from analysis."""
        
        issues = []
        
        # High response times
        if analysis['response_times'].get('p95', 0) > 2.0:
            issues.append({
                'type': 'high_response_time',
                'severity': 'high',
                'description': f"P95 response time is {analysis['response_times']['p95']:.2f}s",
                'threshold': 2.0
            })
        
        # Low quality scores
        if analysis['quality_trends'].get('average_score', 1.0) < 0.7:
            issues.append({
                'type': 'low_quality',
                'severity': 'medium',
                'description': f"Average quality score is {analysis['quality_trends']['average_score']:.2f}",
                'threshold': 0.7
            })
        
        # High error rate
        if analysis['error_patterns'].get('error_rate', 0) > 0.05:
            issues.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'description': f"Error rate is {analysis['error_patterns']['error_rate']:.1%}",
                'threshold': 0.05
            })
        
        return issues
    
    def _generate_performance_recommendations(self, analysis: Dict[str, Any],
                                           issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actionable performance recommendations."""
        
        recommendations = []
        
        # High response time recommendations
        if analysis['response_times'].get('p95', 0) > 2.0:
            recommendations.append({
                'type': 'performance',
                'priority': 'high',
                'issue': 'High response times detected',
                'recommendation': 'Consider scaling retrieval services or optimizing vector search indices',
                'expected_impact': 'Reduce P95 response time by 30-50%'
            })
        
        # Quality issues recommendations
        if analysis['quality_trends'].get('average_score', 1.0) < 0.7:
            recommendations.append({
                'type': 'quality',
                'priority': 'medium',
                'issue': 'Response quality below target',
                'recommendation': 'Review and update document chunking strategy, consider reranking implementation',
                'expected_impact': 'Improve average quality score by 15-25%'
            })
        
        # Resource usage recommendations
        if analysis['resource_usage'].get('cpu_utilization', 0) > 0.8:
            recommendations.append({
                'type': 'scaling',
                'priority': 'high',
                'issue': 'High CPU utilization detected',
                'recommendation': 'Enable auto-scaling or add more service instances',
                'expected_impact': 'Reduce CPU utilization to 60-70% range'
            })
        
        return recommendations
    
    def _calculate_health_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall system health score."""
        
        # Weight different components
        weights = {
            'response_times': 0.3,
            'quality_trends': 0.25,
            'error_patterns': 0.25,
            'resource_usage': 0.2
        }
        
        # Calculate component scores (0-1)
        component_scores = {}
        
        # Response time score (lower is better)
        p95_time = analysis['response_times'].get('p95', 2.0)
        component_scores['response_times'] = max(0, 1 - (p95_time - 0.5) / 2.0)
        
        # Quality score
        component_scores['quality_trends'] = analysis['quality_trends'].get('average_score', 0.7)
        
        # Error rate score (lower is better)
        error_rate = analysis['error_patterns'].get('error_rate', 0.05)
        component_scores['error_patterns'] = max(0, 1 - (error_rate / 0.1))
        
        # Resource usage score (lower is better)
        cpu_usage = analysis['resource_usage'].get('cpu_utilization', 50) / 100
        component_scores['resource_usage'] = max(0, 1 - cpu_usage)
        
        # Calculate weighted average
        health_score = sum(
            component_scores[component] * weights[component]
            for component in weights.keys()
        )
        
        return min(1.0, max(0.0, health_score))


# Supporting classes
class MetricsTimeSeriesStore:
    """Store time series metrics data."""
    
    async def get_metrics_window(self, time_window: str) -> Dict[str, List]:
        """Get metrics for specified time window."""
        
        # Simulate metrics data
        import random
        
        # Generate sample data points
        num_points = 60 if '1h' in time_window else 24
        
        return {
            'request_counts': [random.randint(50, 200) for _ in range(num_points)],
            'response_times': [random.uniform(0.2, 3.0) for _ in range(num_points)],
            'quality_scores': [random.uniform(0.6, 0.95) for _ in range(num_points)],
            'error_counts': [random.randint(0, 10) for _ in range(num_points)],
            'cpu_usage': [random.uniform(30, 85) for _ in range(num_points)],
            'memory_usage': [random.uniform(25, 75) for _ in range(num_points)]
        }


class QueryPatternAnalyzer:
    """Analyze query patterns and usage."""
    pass


class PerformancePredictor:
    """Predict system performance trends."""
    pass


class RAGHealthChecker:
    """Comprehensive health checking for RAG system components."""
    
    def __init__(self):
        self.health_checks = {
            'database_connectivity': self._check_database_health,
            'vector_store_health': self._check_vector_store_health,
            'llm_service_health': self._check_llm_service_health,
            'embedding_service_health': self._check_embedding_service_health,
            'queue_health': self._check_queue_health,
            'disk_space': self._check_disk_space,
            'memory_usage': self._check_memory_usage
        }
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all system components."""
        
        health_results = {}
        overall_healthy = True
        
        # Run all health checks
        for check_name, check_func in self.health_checks.items():
            try:
                health_result = await check_func()
                health_results[check_name] = health_result
                
                if not health_result['healthy']:
                    overall_healthy = False
                    
            except Exception as e:
                health_results[check_name] = {
                    'healthy': False,
                    'error': str(e),
                    'check_failed': True
                }
                overall_healthy = False
        
        # Calculate health score
        healthy_checks = len([r for r in health_results.values() if r.get('healthy', False)])
        health_score = healthy_checks / len(health_results)
        
        return {
            'overall_healthy': overall_healthy,
            'health_score': health_score,
            'component_health': health_results,
            'critical_issues': [
                name for name, result in health_results.items()
                if not result.get('healthy', False) and result.get('critical', False)
            ],
            'timestamp': time.time()
        }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        
        try:
            start_time = time.time()
            
            # Test database connection
            # This would connect to your actual database
            connection_time = time.time() - start_time
            
            return {
                'healthy': connection_time < 1.0,
                'response_time': connection_time,
                'performance_grade': 'excellent' if connection_time < 0.1 else 
                                   'good' if connection_time < 0.5 else 
                                   'fair' if connection_time < 1.0 else 'poor',
                'critical': connection_time > 5.0
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'critical': True
            }
    
    async def _check_vector_store_health(self) -> Dict[str, Any]:
        """Check vector store health and performance."""
        
        try:
            start_time = time.time()
            
            # Test basic connectivity
            # This would be implemented based on your vector store
            # Example: test_query = await vector_store.similarity_search("test", k=1)
            
            response_time = time.time() - start_time
            
            # Check performance thresholds
            healthy = response_time < 1.0  # 1 second threshold
            
            return {
                'healthy': healthy,
                'response_time': response_time,
                'performance_grade': 'excellent' if response_time < 0.1 else 
                                   'good' if response_time < 0.5 else 
                                   'fair' if response_time < 1.0 else 'poor',
                'critical': response_time > 5.0
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'critical': True
            }
    
    # Placeholder implementations for other health checks
    async def _check_llm_service_health(self):
        return {'healthy': True, 'response_time': 0.5}
    
    async def _check_embedding_service_health(self):
        return {'healthy': True, 'response_time': 0.3}
    
    async def _check_queue_health(self):
        return {'healthy': True, 'queue_size': 10}
    
    async def _check_disk_space(self):
        return {'healthy': True, 'disk_usage_percent': 65}
    
    async def _check_memory_usage(self):
        return {'healthy': True, 'memory_usage_percent': 70}