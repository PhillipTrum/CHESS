import time
import json
from datetime import datetime
from threading import Lock
from typing import Dict, List, Any, Optional
from collections import defaultdict
from contextlib import contextmanager


class Instrumentor:
    """
    A singleton class to track and aggregate time spent on different categories of operations.
    
    Operation categories:
    - database_calls: Time spent executing SQL queries against the database
    - llm_calls: Time spent on LLM inference and generation
    - schema_operations: Time spent on schema-related operations (parsing, validation, etc.)
    - vector_db_operations: Time spent querying vector databases
    - embedding_operations: Time spent generating embeddings
    - minhash_lsh_operations: Time spent on MinHash LSH operations
    """
    
    _instance = None
    _lock = Lock()
    
    # Define operation categories
    CATEGORIES = {
        "database_calls",
        "llm_calls",
        "schema_operations",
        "vector_db_operations",
        "embedding_operations",
        "minhash_lsh_operations"
    }
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Instrumentor, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        with self._lock:
            if not self._initialized:
                # Track individual operation timings with metadata
                self.operations: List[Dict[str, Any]] = []
                
                # Track currently active operations (for nested timing)
                self.active_operations: Dict[str, Dict[str, Any]] = {}
                
                # Aggregate statistics per category
                self.aggregates: Dict[str, Dict[str, Any]] = {
                    category: {
                        "total_time": 0.0,
                        "count": 0,
                        "min_time": float('inf'),
                        "max_time": 0.0
                    }
                    for category in self.CATEGORIES
                }
                
                # Global start time for relative timestamps
                self.start_time: Optional[float] = None
                
                self._initialized = True
    
    def reset(self):
        """Reset all tracked metrics."""
        with self._lock:
            self.operations = []
            self.active_operations = {}
            self.aggregates = {
                category: {
                    "total_time": 0.0,
                    "count": 0,
                    "min_time": float('inf'),
                    "max_time": 0.0
                }
                for category in self.CATEGORIES
            }
            self.start_time = None
    
    def start_session(self):
        """Start a new instrumentation session."""
        self.reset()
        self.start_time = time.time()
    
    def start_operation(self, category: str, operation_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start tracking an operation.
        
        Args:
            category: The category of the operation (must be one of CATEGORIES)
            operation_name: A descriptive name for this specific operation
            metadata: Optional additional metadata to store with the operation
            
        Returns:
            operation_id: A unique identifier for this operation
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Must be one of {self.CATEGORIES}")
        
        if self.start_time is None:
            self.start_session()
        
        operation_id = f"{category}_{operation_name}_{time.time()}"
        
        with self._lock:
            self.active_operations[operation_id] = {
                "category": category,
                "operation_name": operation_name,
                "start_time": time.time(),
                "metadata": metadata or {}
            }
        
        return operation_id
    
    def end_operation(self, operation_id: str):
        """
        End tracking an operation and record its metrics.
        
        Args:
            operation_id: The identifier returned by start_operation
        """
        end_time = time.time()
        
        with self._lock:
            if operation_id not in self.active_operations:
                # Operation might have already been ended or never started
                return
            
            op_info = self.active_operations.pop(operation_id)
            start_time = op_info["start_time"]
            duration = end_time - start_time
            category = op_info["category"]
            
            # Record the operation
            operation_record = {
                "category": category,
                "operation_name": op_info["operation_name"],
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
                "relative_start": start_time - self.start_time if self.start_time else 0,
                "relative_end": end_time - self.start_time if self.start_time else duration,
                "metadata": op_info["metadata"]
            }
            self.operations.append(operation_record)
            
            # Update aggregates
            agg = self.aggregates[category]
            agg["total_time"] += duration
            agg["count"] += 1
            agg["min_time"] = min(agg["min_time"], duration)
            agg["max_time"] = max(agg["max_time"], duration)
    
    @contextmanager
    def track_operation(self, category: str, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for tracking an operation.
        
        Usage:
            with instrumentor.track_operation("database_calls", "execute_query", {"query": sql}):
                # perform operation
                pass
        """
        operation_id = self.start_operation(category, operation_name, metadata)
        try:
            yield operation_id
        finally:
            self.end_operation(operation_id)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all tracked operations.
        
        Returns:
            Dictionary containing aggregate statistics per category
        """
        with self._lock:
            summary = {
                "session_duration": time.time() - self.start_time if self.start_time else 0,
                "total_operations": len(self.operations),
                "categories": {}
            }
            
            for category in self.CATEGORIES:
                agg = self.aggregates[category]
                if agg["count"] > 0:
                    cumulative_percentage = round((agg["total_time"] / summary["session_duration"] * 100), 2) if summary["session_duration"] > 0 else 0
                    timeline_percentage = self._calculate_timeline_coverage(category, summary["session_duration"])
                    
                    summary["categories"][category] = {
                        "total_time": round(agg["total_time"], 3),
                        "count": agg["count"],
                        "average_time": round(agg["total_time"] / agg["count"], 3),
                        "min_time": round(agg["min_time"], 3),
                        "max_time": round(agg["max_time"], 3),
                        "cumulative_percentage": cumulative_percentage,  # Can exceed 100% with parallel operations
                        "timeline_percentage": timeline_percentage  # Actual wall-clock coverage, never exceeds 100%
                    }
                else:
                    summary["categories"][category] = {
                        "total_time": 0,
                        "count": 0,
                        "average_time": 0,
                        "min_time": 0,
                        "max_time": 0,
                        "cumulative_percentage": 0,
                        "timeline_percentage": 0
                    }
            
            return summary
    
    def _calculate_timeline_coverage(self, category: str, session_duration: float) -> float:
        """
        Calculate what percentage of the session timeline had this category active.
        Accounts for overlapping operations within the same category.
        
        Args:
            category: The category to calculate coverage for
            session_duration: Total duration of the session
            
        Returns:
            Percentage of timeline where this category had at least one active operation
        """
        if session_duration <= 0:
            return 0.0
        
        # Get all operations for this category
        category_ops = [op for op in self.operations if op["category"] == category]
        if not category_ops:
            return 0.0
        
        # Merge overlapping time intervals
        intervals = [(op["relative_start"], op["relative_end"]) for op in category_ops]
        intervals.sort()
        
        merged = []
        for start, end in intervals:
            if merged and start <= merged[-1][1]:
                # Overlapping interval, merge it
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                # Non-overlapping interval
                merged.append((start, end))
        
        # Calculate total coverage
        total_coverage = sum(end - start for start, end in merged)
        
        return round((total_coverage / session_duration * 100), 2)
    
    def get_timeline_data(self) -> List[Dict[str, Any]]:
        """
        Get timeline data suitable for creating stacked timeline visualizations.
        
        Returns:
            List of operation records sorted by start time
        """
        with self._lock:
            # Sort operations by relative start time
            sorted_operations = sorted(self.operations, key=lambda x: x["relative_start"])
            
            # Format for visualization
            timeline_data = []
            for op in sorted_operations:
                timeline_data.append({
                    "category": op["category"],
                    "operation_name": op["operation_name"],
                    "start": round(op["relative_start"], 3),
                    "end": round(op["relative_end"], 3),
                    "duration": round(op["duration"], 3),
                    "metadata": op["metadata"]
                })
            
            return timeline_data
    
    def get_stacked_timeline(self, time_resolution: float = 0.1) -> Dict[str, Any]:
        """
        Get timeline data in a format suitable for stacked area charts.
        
        Args:
            time_resolution: Time interval (in seconds) for each data point
            
        Returns:
            Dictionary with time points and category values
        """
        with self._lock:
            if not self.operations or self.start_time is None:
                return {"time_points": [], "categories": {cat: [] for cat in self.CATEGORIES}}
            
            session_duration = time.time() - self.start_time
            num_points = int(session_duration / time_resolution) + 1
            time_points = [i * time_resolution for i in range(num_points)]
            
            # Initialize category data
            category_data = {cat: [0] * num_points for cat in self.CATEGORIES}
            
            # For each operation, mark the time intervals it was active
            for op in self.operations:
                category = op["category"]
                start_idx = int(op["relative_start"] / time_resolution)
                end_idx = int(op["relative_end"] / time_resolution)
                
                for i in range(start_idx, min(end_idx + 1, num_points)):
                    category_data[category][i] = 1  # Mark as active
            
            return {
                "time_points": time_points,
                "categories": category_data
            }
    
    def export_to_json(self, filepath: str):
        """
        Export all metrics to a JSON file.
        
        Args:
            filepath: Path where to save the JSON file
        """
        data = {
            "session_info": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
                "duration": time.time() - self.start_time if self.start_time else 0
            },
            "summary": self.get_summary(),
            "timeline": self.get_timeline_data(),
            "operations": self.operations
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_category_breakdown(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get operations grouped by category.
        
        Returns:
            Dictionary mapping categories to lists of their operations
        """
        with self._lock:
            breakdown = {cat: [] for cat in self.CATEGORIES}
            
            for op in self.operations:
                category = op["category"]
                breakdown[category].append({
                    "operation_name": op["operation_name"],
                    "duration": round(op["duration"], 3),
                    "start": round(op["relative_start"], 3),
                    "metadata": op["metadata"]
                })
            
            return breakdown
    
    def print_summary(self):
        """Print a formatted summary of metrics."""
        summary = self.get_summary()
        
        print("\n" + "="*80)
        print("INSTRUMENTATION SUMMARY")
        print("="*80)
        print(f"Session Duration: {summary['session_duration']:.2f}s")
        print(f"Total Operations: {summary['total_operations']}")
        print("\nCategory Breakdown:")
        print("-"*80)
        
        for category, stats in summary["categories"].items():
            if stats["count"] > 0:
                print(f"\n{category.replace('_', ' ').title()}:")
                print(f"  Total Time:       {stats['total_time']:.3f}s")
                print(f"  Timeline Coverage: {stats['timeline_percentage']:.1f}% (wall-clock)")
                print(f"  Cumulative Time:  {stats['cumulative_percentage']:.1f}% (can exceed 100% with parallel ops)")
                print(f"  Call Count:       {stats['count']}")
                print(f"  Average Time:     {stats['average_time']:.3f}s")
                print(f"  Min/Max Time:     {stats['min_time']:.3f}s / {stats['max_time']:.3f}s")
        
        print("="*80)
        print("\nNote: 'Cumulative Time' is the sum of all operation durations.")
        print("      It can exceed 100% when operations run in parallel.")
        print("      'Timeline Coverage' shows actual wall-clock time coverage.")
        print("="*80 + "\n")
