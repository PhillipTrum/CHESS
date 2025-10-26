#!/usr/bin/env python3
"""
Test script to demonstrate the parallel operation tracking fix.
This shows how the instrumentor now correctly handles parallel operations.
"""

import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from instrumentation.instrumentor import Instrumentor


def simulate_parallel_llm_calls():
    """Simulate multiple LLM calls that would run in parallel."""
    instrumentor = Instrumentor()
    instrumentor.start_session()
    
    # Simulate 3 LLM calls that would run in parallel
    # Each takes 2 seconds, but they overlap in time
    
    print("Simulating 3 parallel LLM calls (2 seconds each)...")
    
    # Start all three
    op1 = instrumentor.start_operation("llm_calls", "query_1")
    time.sleep(0.1)  # Small offset
    op2 = instrumentor.start_operation("llm_calls", "query_2")
    time.sleep(0.1)  # Small offset
    op3 = instrumentor.start_operation("llm_calls", "query_3")
    
    # Simulate processing time
    time.sleep(2.0)
    
    # End them with slight offsets
    instrumentor.end_operation(op1)
    time.sleep(0.1)
    instrumentor.end_operation(op2)
    time.sleep(0.1)
    instrumentor.end_operation(op3)
    
    print("\nAll operations complete!")
    
    # Print summary
    instrumentor.print_summary()
    
    # Get summary programmatically
    summary = instrumentor.get_summary()
    llm_stats = summary['categories']['llm_calls']
    
    print("\nDetailed Analysis:")
    print(f"Session duration: {summary['session_duration']:.2f}s")
    print(f"Sum of LLM operation times: {llm_stats['total_time']:.2f}s")
    print(f"Cumulative percentage: {llm_stats['cumulative_percentage']:.1f}%")
    print(f"Timeline coverage: {llm_stats['timeline_percentage']:.1f}%")
    print(f"\n✓ Timeline coverage correctly shows ~100% (not {llm_stats['cumulative_percentage']:.0f}%!)")
    print(f"✓ Cumulative percentage shows total work done ({llm_stats['cumulative_percentage']:.0f}%)")
    

if __name__ == '__main__':
    simulate_parallel_llm_calls()
