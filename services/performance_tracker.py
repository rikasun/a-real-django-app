from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics
import json
from pathlib import Path

class PerformanceTracker:
    """
    Tracks and analyzes cleanup performance metrics over time.
    Helps identify optimal cleanup schedules and resource usage patterns.
    """
    
    def __init__(self, metrics_file: str = "cleanup_metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_history: List[Dict] = []
        self._load_metrics()

    def _load_metrics(self) -> None:
        """Load historical metrics from file"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                self.metrics_history = json.load(f)

    def _save_metrics(self) -> None:
        """Save metrics to file"""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, default=str)

    def record_cleanup_metrics(self, metrics: Dict) -> None:
        """
        Record metrics from a cleanup operation.
        
        Args:
            metrics: Dict containing:
                - duration_seconds: float
                - records_processed: int
                - cpu_usage: float
                - memory_usage: float
                - timestamp: datetime
                - success: bool
        """
        self.metrics_history.append({
            **metrics,
            'timestamp': datetime.now().isoformat()
        })
        self._save_metrics()

    def analyze_performance_trends(self, days: int = 30) -> Dict:
        """
        Analyze performance trends over the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict containing:
                - optimal_times: List of best performing time slots
                - peak_usage_periods: List of high resource usage periods
                - efficiency_score: Float indicating overall efficiency
                - recommendations: List of suggested improvements
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m['timestamp']) > cutoff
        ]

        if not recent_metrics:
            return {
                'optimal_times': [],
                'peak_usage_periods': [],
                'efficiency_score': 0,
                'recommendations': ['Insufficient data for analysis']
            }

        # Analyze cleanup durations by hour
        hourly_performance = self._analyze_hourly_performance(recent_metrics)
        
        # Find optimal times (lowest average duration and resource usage)
        optimal_times = self._find_optimal_times(hourly_performance)
        
        # Identify peak usage periods
        peak_periods = self._identify_peak_periods(recent_metrics)
        
        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score(recent_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            hourly_performance,
            peak_periods,
            efficiency_score
        )

        return {
            'optimal_times': optimal_times,
            'peak_usage_periods': peak_periods,
            'efficiency_score': efficiency_score,
            'recommendations': recommendations
        }

    def _analyze_hourly_performance(self, metrics: List[Dict]) -> Dict[int, Dict]:
        """Analyze performance metrics grouped by hour"""
        hourly_stats = {}
        
        for metric in metrics:
            hour = datetime.fromisoformat(metric['timestamp']).hour
            if hour not in hourly_stats:
                hourly_stats[hour] = {
                    'durations': [],
                    'cpu_usage': [],
                    'memory_usage': [],
                    'success_rate': []
                }
                
            stats = hourly_stats[hour]
            stats['durations'].append(metric['duration_seconds'])
            stats['cpu_usage'].append(metric['cpu_usage'])
            stats['memory_usage'].append(metric['memory_usage'])
            stats['success_rate'].append(1 if metric['success'] else 0)
            
        # Calculate averages
        for hour, stats in hourly_stats.items():
            hourly_stats[hour] = {
                'avg_duration': statistics.mean(stats['durations']),
                'avg_cpu': statistics.mean(stats['cpu_usage']),
                'avg_memory': statistics.mean(stats['memory_usage']),
                'success_rate': statistics.mean(stats['success_rate']) * 100
            }
            
        return hourly_stats

    def _find_optimal_times(self, hourly_performance: Dict) -> List[Dict]:
        """Identify optimal time slots for cleanup operations"""
        # Score each hour based on performance metrics
        hour_scores = []
        for hour, stats in hourly_performance.items():
            score = (
                (1 / stats['avg_duration']) * 0.4 +  # Lower duration is better
                (1 / stats['avg_cpu']) * 0.3 +      # Lower CPU usage is better
                (1 / stats['avg_memory']) * 0.2 +   # Lower memory usage is better
                (stats['success_rate'] / 100) * 0.1  # Higher success rate is better
            )
            hour_scores.append({
                'hour': hour,
                'score': score,
                'stats': stats
            })
        
        # Sort by score and return top 3
        return sorted(hour_scores, key=lambda x: x['score'], reverse=True)[:3]

    def _identify_peak_periods(self, metrics: List[Dict]) -> List[Dict]:
        """Identify periods of high resource usage"""
        peak_periods = []
        
        # Group consecutive high-usage periods
        current_peak = None
        for metric in sorted(metrics, key=lambda x: x['timestamp']):
            if metric['cpu_usage'] > 80 or metric['memory_usage'] > 80:
                if not current_peak:
                    current_peak = {
                        'start': metric['timestamp'],
                        'end': metric['timestamp'],
                        'max_cpu': metric['cpu_usage'],
                        'max_memory': metric['memory_usage']
                    }
                else:
                    current_peak['end'] = metric['timestamp']
                    current_peak['max_cpu'] = max(current_peak['max_cpu'], metric['cpu_usage'])
                    current_peak['max_memory'] = max(current_peak['max_memory'], metric['memory_usage'])
            elif current_peak:
                peak_periods.append(current_peak)
                current_peak = None
                
        return peak_periods

    def _calculate_efficiency_score(self, metrics: List[Dict]) -> float:
        """Calculate overall efficiency score (0-100)"""
        if not metrics:
            return 0
            
        scores = []
        for metric in metrics:
            # Weight different factors
            duration_score = min(1.0, 300 / metric['duration_seconds'])  # Normalize to 5 minutes
            resource_score = 1 - ((metric['cpu_usage'] + metric['memory_usage']) / 200)  # Average of CPU and memory
            success_score = 1.0 if metric['success'] else 0.0
            
            # Combined score
            score = (
                duration_score * 0.4 +
                resource_score * 0.4 +
                success_score * 0.2
            ) * 100
            
            scores.append(score)
            
        return statistics.mean(scores)

    def _generate_recommendations(self, 
                               hourly_performance: Dict,
                               peak_periods: List[Dict],
                               efficiency_score: float) -> List[str]:
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        # Analyze patterns and generate recommendations
        if efficiency_score < 70:
            recommendations.append("Consider reducing batch size to improve performance")
            
        if len(peak_periods) > 5:
            recommendations.append("High resource usage detected - consider spreading cleanup operations")
            
        # Find worst performing hours
        worst_hours = sorted(
            hourly_performance.items(),
            key=lambda x: x[1]['success_rate']
        )[:3]
        
        if worst_hours[0][1]['success_rate'] < 80:
            recommendations.append(
                f"Avoid scheduling cleanups during hour {worst_hours[0][0]} "
                f"(success rate: {worst_hours[0][1]['success_rate']:.1f}%)"
            )
            
        return recommendations 