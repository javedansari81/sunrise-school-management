"""
Performance monitoring utilities for tracking API response times and database query performance
"""

import time
import logging
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager

# Configure performance logger
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)

# Create handler if it doesn't exist
if not perf_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - PERF - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    perf_logger.addHandler(handler)

class PerformanceMonitor:
    """Performance monitoring utility class"""
    
    @staticmethod
    def log_timing(operation: str, duration_ms: float, details: Optional[Dict[str, Any]] = None):
        """Log timing information for an operation"""
        details_str = ""
        if details:
            details_str = " | " + " | ".join([f"{k}: {v}" for k, v in details.items()])
        
        # Color coding based on performance
        if duration_ms < 100:
            emoji = "🟢"  # Fast
        elif duration_ms < 500:
            emoji = "🟡"  # Moderate
        elif duration_ms < 1000:
            emoji = "🟠"  # Slow
        else:
            emoji = "🔴"  # Very slow
            
        perf_logger.info(f"{emoji} {operation}: {duration_ms:.2f}ms{details_str}")
    
    @staticmethod
    @contextmanager
    def timer(operation: str, details: Optional[Dict[str, Any]] = None):
        """Context manager for timing operations"""
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            PerformanceMonitor.log_timing(operation, duration_ms, details)
    
    @staticmethod
    def timing_decorator(operation: str):
        """Decorator for timing function execution"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    PerformanceMonitor.log_timing(f"{operation} ({func.__name__})", duration_ms)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    PerformanceMonitor.log_timing(f"{operation} ({func.__name__})", duration_ms)
            
            # Return appropriate wrapper based on function type
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator

# Convenience functions
def log_timing(operation: str, duration_ms: float, **details):
    """Convenience function for logging timing"""
    PerformanceMonitor.log_timing(operation, duration_ms, details)

def timer(operation: str, **details):
    """Convenience function for timing context manager"""
    return PerformanceMonitor.timer(operation, details)

def timing_decorator(operation: str):
    """Convenience function for timing decorator"""
    return PerformanceMonitor.timing_decorator(operation)

# Database query performance tracking
class DatabasePerformanceTracker:
    """Track database query performance"""
    
    def __init__(self):
        self.query_stats = {}
    
    def track_query(self, query_name: str, duration_ms: float, row_count: Optional[int] = None):
        """Track a database query performance"""
        if query_name not in self.query_stats:
            self.query_stats[query_name] = {
                "count": 0,
                "total_time_ms": 0,
                "avg_time_ms": 0,
                "min_time_ms": float('inf'),
                "max_time_ms": 0,
                "total_rows": 0
            }
        
        stats = self.query_stats[query_name]
        stats["count"] += 1
        stats["total_time_ms"] += duration_ms
        stats["avg_time_ms"] = stats["total_time_ms"] / stats["count"]
        stats["min_time_ms"] = min(stats["min_time_ms"], duration_ms)
        stats["max_time_ms"] = max(stats["max_time_ms"], duration_ms)
        
        if row_count is not None:
            stats["total_rows"] += row_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return self.query_stats.copy()
    
    def reset_stats(self):
        """Reset query statistics"""
        self.query_stats.clear()

# Global database performance tracker
db_perf_tracker = DatabasePerformanceTracker()

# Configuration endpoint specific monitoring
class ConfigurationPerformanceMonitor:
    """Specialized monitoring for configuration endpoint"""
    
    @staticmethod
    def log_cache_performance(cache_hit: bool, total_time_ms: float, record_count: int):
        """Log configuration cache performance"""
        cache_status = "HIT" if cache_hit else "MISS"
        emoji = "⚡" if cache_hit else "🔄"
        
        details = {
            "cache": cache_status,
            "records": record_count,
            "avg_per_record": f"{total_time_ms / record_count:.2f}ms" if record_count > 0 else "0ms"
        }
        
        PerformanceMonitor.log_timing(f"{emoji} Configuration Load", total_time_ms, details)
    
    @staticmethod
    def log_compression_performance(original_size: int, compressed_size: int, compression_time_ms: float):
        """Log response compression performance"""
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        details = {
            "original": f"{original_size:,} bytes",
            "compressed": f"{compressed_size:,} bytes",
            "ratio": f"{compression_ratio:.1f}%",
            "compression_time": f"{compression_time_ms:.2f}ms"
        }
        
        PerformanceMonitor.log_timing("📦 Response Compression", compression_time_ms, details)

# Export main components
__all__ = [
    'PerformanceMonitor',
    'DatabasePerformanceTracker',
    'ConfigurationPerformanceMonitor',
    'log_timing',
    'timer',
    'timing_decorator',
    'db_perf_tracker'
]
