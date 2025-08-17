# Alerting system for RAG monitoring
import time
from typing import Dict, List, Any

class RAGAlertingSystem:
    """Alerting system for RAG quality degradation and anomalies."""
    
    def __init__(self, alert_config: Dict):
        self.alert_config = alert_config
        self.alert_history = []
        self.active_alerts = {}
        
        # Alert severity levels
        self.severity_levels = {
            'low': {'threshold_multiplier': 1.2, 'cooldown': 300},
            'medium': {'threshold_multiplier': 1.5, 'cooldown': 180}, 
            'high': {'threshold_multiplier': 2.0, 'cooldown': 60},
            'critical': {'threshold_multiplier': 3.0, 'cooldown': 0}
        }
    
    def evaluate_alert_conditions(self, monitoring_data: Dict) -> List[Dict]:
        """Evaluate if any alert conditions are met."""
        
        alerts_to_trigger = []
        current_time = time.time()
        
        # Check quality degradation alerts
        quality_alerts = self._check_quality_alerts(monitoring_data)
        alerts_to_trigger.extend(quality_alerts)
        
        # Check performance alerts
        performance_alerts = self._check_performance_alerts(monitoring_data)
        alerts_to_trigger.extend(performance_alerts)
        
        # Check anomaly alerts
        anomaly_alerts = self._check_anomaly_alerts(monitoring_data)
        alerts_to_trigger.extend(anomaly_alerts)
        
        # Filter out alerts in cooldown
        filtered_alerts = []
        for alert in alerts_to_trigger:
            alert_key = f"{alert['type']}_{alert['metric']}"
            
            if alert_key in self.active_alerts:
                last_triggered = self.active_alerts[alert_key]['last_triggered']
                cooldown = self.severity_levels[alert['severity']]['cooldown']
                
                if current_time - last_triggered < cooldown:
                    continue  # Skip alert in cooldown
            
            filtered_alerts.append(alert)
            
            # Update active alerts
            self.active_alerts[alert_key] = {
                'alert': alert,
                'last_triggered': current_time,
                'trigger_count': self.active_alerts.get(alert_key, {}).get('trigger_count', 0) + 1
            }
        
        return filtered_alerts
    
    def _check_quality_alerts(self, monitoring_data: Dict) -> List[Dict]:
        """Check for quality degradation alerts."""
        
        alerts = []
        
        if 'quality' in monitoring_data:
            quality_data = monitoring_data['quality']
            
            # Overall quality threshold
            if 'overall_quality' in quality_data:
                overall_score = quality_data['overall_quality']
                
                if overall_score < self.alert_config.get('min_quality_score', 0.6):
                    alerts.append({
                        'type': 'quality_degradation',
                        'metric': 'overall_quality',
                        'severity': self._determine_severity('quality', overall_score),
                        'current_value': overall_score,
                        'threshold': self.alert_config.get('min_quality_score', 0.6),
                        'message': f"Overall quality score {overall_score:.3f} below threshold",
                        'timestamp': time.time()
                    })
            
            # Individual quality metric alerts
            individual_scores = quality_data.get('individual_scores', {})
            for metric, score in individual_scores.items():
                if score is not None:
                    threshold_key = f'min_{metric}_score'
                    if threshold_key in self.alert_config:
                        if score < self.alert_config[threshold_key]:
                            alerts.append({
                                'type': 'quality_metric_low',
                                'metric': metric,
                                'severity': self._determine_severity(metric, score),
                                'current_value': score,
                                'threshold': self.alert_config[threshold_key],
                                'message': f"{metric} score {score:.3f} below threshold",
                                'timestamp': time.time()
                            })
        
        return alerts
    
    def _check_performance_alerts(self, monitoring_data: Dict) -> List[Dict]:
        """Check for performance degradation alerts."""
        
        alerts = []
        
        if 'performance' in monitoring_data:
            performance_data = monitoring_data['performance']
            
            # Response time alerts
            if 'response_time' in performance_data:
                response_time = performance_data['response_time']
                max_threshold = self.alert_config.get('max_response_time', 5.0)
                
                if response_time > max_threshold:
                    alerts.append({
                        'type': 'performance_degradation',
                        'metric': 'response_time',
                        'severity': self._determine_severity('response_time', response_time),
                        'current_value': response_time,
                        'threshold': max_threshold,
                        'message': f"Response time {response_time:.2f}s exceeds threshold",
                        'timestamp': time.time()
                    })
            
            # Throughput alerts
            if 'throughput' in performance_data:
                throughput = performance_data['throughput']
                min_threshold = self.alert_config.get('min_throughput', 0.1)
                
                if throughput < min_threshold:
                    alerts.append({
                        'type': 'throughput_low',
                        'metric': 'throughput',
                        'severity': self._determine_severity('throughput', throughput),
                        'current_value': throughput,
                        'threshold': min_threshold,
                        'message': f"Throughput {throughput:.3f} req/s below threshold",
                        'timestamp': time.time()
                    })
        
        return alerts
    
    def _check_anomaly_alerts(self, monitoring_data: Dict) -> List[Dict]:
        """Check for anomaly detection alerts."""
        
        alerts = []
        
        if 'anomalies' in monitoring_data:
            anomaly_flags = monitoring_data['anomalies']
            
            for anomaly in anomaly_flags:
                alerts.append({
                    'type': 'anomaly_detected',
                    'metric': anomaly.get('metric', 'unknown'),
                    'severity': anomaly.get('severity', 'medium'),
                    'current_value': anomaly.get('value', 'N/A'),
                    'threshold': 'dynamic',
                    'message': f"Anomaly detected: {anomaly.get('description', 'Unknown anomaly')}",
                    'timestamp': time.time(),
                    'anomaly_data': anomaly
                })
        
        return alerts
    
    def _determine_severity(self, metric_name: str, current_value: float) -> str:
        """Determine alert severity based on metric value."""
        
        # Get threshold for metric
        threshold_key = f'min_{metric_name}_score' if 'quality' in metric_name else f'max_{metric_name}'
        threshold = self.alert_config.get(threshold_key, 0.5)
        
        # Calculate deviation from threshold
        if 'quality' in metric_name or metric_name == 'throughput':
            # Lower is worse for these metrics
            deviation_ratio = threshold / max(current_value, 0.001)
        else:
            # Higher is worse for these metrics (e.g., response_time)
            deviation_ratio = current_value / max(threshold, 0.001)
        
        # Determine severity based on deviation
        if deviation_ratio >= self.severity_levels['critical']['threshold_multiplier']:
            return 'critical'
        elif deviation_ratio >= self.severity_levels['high']['threshold_multiplier']:
            return 'high'
        elif deviation_ratio >= self.severity_levels['medium']['threshold_multiplier']:
            return 'medium'
        else:
            return 'low'
    
    def send_alert(self, alert: Dict, channels: List[str] = None) -> bool:
        """Send alert through configured channels."""
        
        if channels is None:
            channels = self.alert_config.get('default_channels', ['console'])
        
        alert_sent = False
        
        for channel in channels:
            try:
                if channel == 'console':
                    self._send_console_alert(alert)
                    alert_sent = True
                elif channel == 'email':
                    self._send_email_alert(alert)
                    alert_sent = True
                elif channel == 'slack':
                    self._send_slack_alert(alert)
                    alert_sent = True
                elif channel == 'webhook':
                    self._send_webhook_alert(alert)
                    alert_sent = True
                else:
                    print(f"Unknown alert channel: {channel}")
            
            except Exception as e:
                print(f"Error sending alert via {channel}: {e}")
        
        # Store alert in history
        if alert_sent:
            self.alert_history.append({
                'alert': alert,
                'channels': channels,
                'sent_at': time.time()
            })
        
        return alert_sent
    
    def _send_console_alert(self, alert: Dict):
        """Send alert to console."""
        
        severity_colors = {
            'low': '\033[93m',      # Yellow
            'medium': '\033[91m',   # Orange
            'high': '\033[91m',     # Red
            'critical': '\033[95m'  # Magenta
        }
        
        reset_color = '\033[0m'
        
        color = severity_colors.get(alert['severity'], '')
        
        print(f"{color}🚨 ALERT [{alert['severity'].upper()}] {alert['type']}: {alert['message']}{reset_color}")
        print(f"   Metric: {alert['metric']} = {alert['current_value']}")
        print(f"   Threshold: {alert['threshold']}")
        print(f"   Time: {time.ctime(alert['timestamp'])}")
    
    def _send_email_alert(self, alert: Dict):
        """Send alert via email (placeholder implementation)."""
        
        # In production, would use actual email service
        print(f"[EMAIL ALERT] {alert['severity'].upper()}: {alert['message']}")
    
    def _send_slack_alert(self, alert: Dict):
        """Send alert via Slack (placeholder implementation)."""
        
        # In production, would use Slack API
        severity_emojis = {
            'low': '⚠️',
            'medium': '🔥',
            'high': '🚨',
            'critical': '💥'
        }
        
        emoji = severity_emojis.get(alert['severity'], '⚠️')
        
        print(f"[SLACK ALERT] {emoji} {alert['severity'].upper()}: {alert['message']}")
    
    def _send_webhook_alert(self, alert: Dict):
        """Send alert via webhook (placeholder implementation)."""
        
        # In production, would make HTTP POST to webhook URL
        print(f"[WEBHOOK ALERT] {alert['severity'].upper()}: {alert['message']}")
    
    def get_alert_summary(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get summary of alerts in specified time window."""
        
        current_time = time.time()
        cutoff_time = current_time - (time_window_hours * 3600)
        
        recent_alerts = [
            alert_record for alert_record in self.alert_history
            if alert_record['sent_at'] > cutoff_time
        ]
        
        if not recent_alerts:
            return {
                'time_window_hours': time_window_hours,
                'total_alerts': 0,
                'message': 'No alerts in specified time window'
            }
        
        # Analyze alert patterns
        alert_summary = {
            'time_window_hours': time_window_hours,
            'total_alerts': len(recent_alerts),
            'by_severity': {},
            'by_type': {},
            'by_metric': {},
            'most_common_issues': []
        }
        
        # Count alerts by category
        for alert_record in recent_alerts:
            alert = alert_record['alert']
            
            # By severity
            severity = alert['severity']
            alert_summary['by_severity'][severity] = alert_summary['by_severity'].get(severity, 0) + 1
            
            # By type
            alert_type = alert['type']
            alert_summary['by_type'][alert_type] = alert_summary['by_type'].get(alert_type, 0) + 1
            
            # By metric
            metric = alert['metric']
            alert_summary['by_metric'][metric] = alert_summary['by_metric'].get(metric, 0) + 1
        
        # Identify most common issues
        most_common_types = sorted(alert_summary['by_type'].items(), key=lambda x: x[1], reverse=True)
        alert_summary['most_common_issues'] = most_common_types[:3]
        
        return alert_summary
    
    def clear_active_alerts(self, alert_types: List[str] = None):
        """Clear active alerts (remove from cooldown)."""
        
        if alert_types is None:
            # Clear all active alerts
            cleared_count = len(self.active_alerts)
            self.active_alerts = {}
            print(f"Cleared {cleared_count} active alerts")
        else:
            # Clear specific alert types
            cleared_count = 0
            for alert_type in alert_types:
                keys_to_remove = [key for key in self.active_alerts.keys() if key.startswith(alert_type)]
                for key in keys_to_remove:
                    del self.active_alerts[key]
                    cleared_count += 1
            print(f"Cleared {cleared_count} active alerts of types: {alert_types}")
    
    def update_alert_config(self, new_config: Dict):
        """Update alert configuration."""
        
        self.alert_config.update(new_config)
        print(f"Alert configuration updated with {len(new_config)} new/updated settings")
    
    def test_alerting_channels(self, channels: List[str] = None) -> Dict[str, bool]:
        """Test alerting channels with a test message."""
        
        if channels is None:
            channels = self.alert_config.get('default_channels', ['console'])
        
        test_alert = {
            'type': 'test_alert',
            'metric': 'test_metric',
            'severity': 'low',
            'current_value': 'test_value',
            'threshold': 'test_threshold',
            'message': 'This is a test alert to verify alerting channels',
            'timestamp': time.time()
        }
        
        results = {}
        
        for channel in channels:
            try:
                if channel == 'console':
                    self._send_console_alert(test_alert)
                    results[channel] = True
                elif channel == 'email':
                    self._send_email_alert(test_alert)
                    results[channel] = True
                elif channel == 'slack':
                    self._send_slack_alert(test_alert)
                    results[channel] = True
                elif channel == 'webhook':
                    self._send_webhook_alert(test_alert)
                    results[channel] = True
                else:
                    results[channel] = False
                    
            except Exception as e:
                print(f"Test failed for channel {channel}: {e}")
                results[channel] = False
        
        return results
