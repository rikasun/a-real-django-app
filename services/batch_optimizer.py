from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BatchMetrics:
    batch_size: int
    duration: float
    success: bool
    cpu_usage: float
    memory_usage: float
    records_per_second: float

class BatchOptimizer:
    """
    Optimizes batch size for cleanup operations based on system performance.
    Automatically adjusts batch size to maintain optimal throughput while avoiding system overload.
    """
    
    def __init__(self, 
                 min_batch_size: int = 100,
                 max_batch_size: int = 10000,
                 target_duration: float = 300,  # 5 minutes
                 max_memory_threshold: float = 80.0):
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        self.target_duration = target_duration
        self.max_memory_threshold = max_memory_threshold
        self.performance_history: List[BatchMetrics] = []
        self.current_batch_size = 1000  # Default starting point

    def record_batch_performance(self, metrics: Dict) -> None:
        """Record performance metrics for a batch operation"""
        batch_metrics = BatchMetrics(
            batch_size=metrics['batch_size'],
            duration=metrics['duration_seconds'],
            success=metrics['success'],
            cpu_usage=metrics['cpu_usage'],
            memory_usage=metrics['memory_usage'],
            records_per_second=metrics['records_processed'] / metrics['duration_seconds']
        )
        self.performance_history.append(batch_metrics)
        
        # Keep only recent history
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]

    def get_optimal_batch_size(self, current_memory_usage: float) -> int:
        """
        Calculate optimal batch size based on recent performance history
        and current system conditions
        """
        if not self.performance_history:
            return self.current_batch_size

        # Get recent successful operations
        recent_metrics = [
            m for m in self.performance_history[-10:]
            if m.success
        ]

        if not recent_metrics:
            return self.min_batch_size

        # Calculate performance metrics
        avg_duration = statistics.mean(m.duration for m in recent_metrics)
        avg_records_per_second = statistics.mean(m.records_per_second for m in recent_metrics)
        
        # Adjust batch size based on performance targets
        if avg_duration > self.target_duration * 1.2:  # Too slow
            new_batch_size = int(self.current_batch_size * 0.8)  # Reduce by 20%
        elif avg_duration < self.target_duration * 0.8:  # Too fast
            new_batch_size = int(self.current_batch_size * 1.2)  # Increase by 20%
        else:
            new_batch_size = self.current_batch_size

        # Apply memory usage constraints
        if current_memory_usage > self.max_memory_threshold:
            new_batch_size = int(self.current_batch_size * 0.7)  # Reduce more aggressively
            logger.warning(f"High memory usage ({current_memory_usage}%), reducing batch size")

        # Apply bounds
        new_batch_size = max(self.min_batch_size, min(self.max_batch_size, new_batch_size))
        
        if new_batch_size != self.current_batch_size:
            logger.info(
                f"Adjusting batch size from {self.current_batch_size} to {new_batch_size} "
                f"(avg duration: {avg_duration:.1f}s, memory: {current_memory_usage:.1f}%)"
            )
            self.current_batch_size = new_batch_size

        return new_batch_size

    def analyze_batch_performance(self) -> Dict:
        """Analyze batch size performance patterns"""
        if not self.performance_history:
            return {
                "optimal_batch_size": self.current_batch_size,
                "recommendations": ["Insufficient performance data"]
            }

        successful_ops = [m for m in self.performance_history if m.success]
        if not successful_ops:
            return {
                "optimal_batch_size": self.min_batch_size,
                "recommendations": ["No successful operations recorded"]
            }

        # Group by batch size
        batch_stats = {}
        for metric in successful_ops:
            if metric.batch_size not in batch_stats:
                batch_stats[metric.batch_size] = []
            batch_stats[metric.batch_size].append(metric)

        # Calculate efficiency for each batch size
        batch_efficiency = {}
        for batch_size, metrics in batch_stats.items():
            avg_duration = statistics.mean(m.duration for m in metrics)
            avg_records_per_second = statistics.mean(m.records_per_second for m in metrics)
            avg_memory = statistics.mean(m.memory_usage for m in metrics)
            
            # Calculate efficiency score
            efficiency_score = (
                avg_records_per_second * 0.5 +  # Prioritize throughput
                (1 - avg_memory/100) * 0.3 +    # Lower memory usage is better
                (self.target_duration/avg_duration) * 0.2  # Closer to target duration is better
            )
            
            batch_efficiency[batch_size] = {
                "efficiency_score": efficiency_score,
                "avg_duration": avg_duration,
                "avg_records_per_second": avg_records_per_second,
                "avg_memory_usage": avg_memory
            }

        # Find optimal batch size
        optimal_batch_size = max(
            batch_efficiency.items(),
            key=lambda x: x[1]["efficiency_score"]
        )[0]

        # Generate recommendations
        recommendations = []
        if optimal_batch_size != self.current_batch_size:
            recommendations.append(
                f"Consider changing batch size to {optimal_batch_size} "
                f"for optimal performance"
            )

        return {
            "optimal_batch_size": optimal_batch_size,
            "batch_efficiency": batch_efficiency,
            "recommendations": recommendations
        } 