#!/usr/bin/env python3
"""
Example demonstrating the Instrumentor class usage.

This script shows how to use the instrumentor to track operations
and generate visualization-ready metrics.
"""

import time
import random
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from instrumentation.instrumentor import Instrumentor


def simulate_database_call(query_type: str, duration: float):
    """Simulate a database operation."""
    time.sleep(duration)


def simulate_llm_call(model: str, duration: float):
    """Simulate an LLM inference call."""
    time.sleep(duration)


def simulate_embedding_operation(num_texts: int, duration: float):
    """Simulate generating embeddings."""
    time.sleep(duration)


def simulate_vector_db_query(query: str, duration: float):
    """Simulate a vector database query."""
    time.sleep(duration)


def simulate_schema_operation(operation: str, duration: float):
    """Simulate a schema operation."""
    time.sleep(duration)


def simulate_lsh_operation(keyword: str, duration: float):
    """Simulate a MinHash LSH operation."""
    time.sleep(duration)


def main():
    print("="*80)
    print("CHESS Instrumentor Example")
    print("="*80)
    print("\nThis example simulates various operations to demonstrate the instrumentor.\n")
    
    # Initialize instrumentor and start session
    instrumentor = Instrumentor()
    instrumentor.start_session()
    
    print("Running simulated operations...")
    print("-"*80)
    
    # Simulate a typical CHESS workflow
    
    # 1. Information Retrieval Phase
    print("\n[1] Information Retrieval Phase")
    
    # Schema operations
    with instrumentor.track_operation("schema_operations", "parse_database_schema"):
        simulate_schema_operation("parse", random.uniform(0.01, 0.05))
    
    # Embedding operations
    for i in range(3):
        with instrumentor.track_operation("embedding_operations", "embed_keywords", {"batch": i+1}):
            simulate_embedding_operation(10, random.uniform(0.1, 0.3))
    
    # Vector DB queries
    for i in range(5):
        with instrumentor.track_operation("vector_db_operations", "similarity_search", {"query_id": i+1}):
            simulate_vector_db_query(f"query_{i}", random.uniform(0.05, 0.15))
    
    # LSH operations
    for i in range(4):
        with instrumentor.track_operation("minhash_lsh_operations", "find_similar_values", {"keyword_id": i+1}):
            simulate_lsh_operation(f"keyword_{i}", random.uniform(0.01, 0.05))
    
    # 2. Schema Selection Phase
    print("[2] Schema Selection Phase")
    
    # Database queries to check columns
    for i in range(8):
        with instrumentor.track_operation("database_calls", "get_table_columns", {"table_id": i+1}):
            simulate_database_call("SELECT", random.uniform(0.01, 0.05))
    
    # Schema filtering operations
    for i in range(5):
        with instrumentor.track_operation("schema_operations", "filter_columns", {"iteration": i+1}):
            simulate_schema_operation("filter", random.uniform(0.02, 0.08))
    
    # 3. Candidate Generation Phase
    print("[3] Candidate Generation Phase")
    
    # LLM calls for SQL generation
    for i in range(6):
        with instrumentor.track_operation("llm_calls", "generate_sql_candidate", {"candidate": i+1}):
            simulate_llm_call("gpt-4", random.uniform(0.5, 2.0))
    
    # Database calls to validate candidates
    for i in range(6):
        with instrumentor.track_operation("database_calls", "execute_candidate", {"candidate": i+1}):
            simulate_database_call("EXECUTE", random.uniform(0.05, 0.3))
    
    # Schema validation
    for i in range(3):
        with instrumentor.track_operation("schema_operations", "validate_sql_schema", {"sql_id": i+1}):
            simulate_schema_operation("validate", random.uniform(0.01, 0.03))
    
    # 4. Revision Phase
    print("[4] Revision Phase")
    
    # LLM calls for revisions
    for i in range(3):
        with instrumentor.track_operation("llm_calls", "revise_sql", {"revision": i+1}):
            simulate_llm_call("gpt-4", random.uniform(0.8, 1.5))
    
    # Database validation
    for i in range(3):
        with instrumentor.track_operation("database_calls", "execute_revised", {"revision": i+1}):
            simulate_database_call("EXECUTE", random.uniform(0.05, 0.2))
    
    # 5. Unit Testing Phase
    print("[5] Unit Testing Phase")
    
    # Generate unit tests
    for i in range(4):
        with instrumentor.track_operation("llm_calls", "generate_unit_test", {"test": i+1}):
            simulate_llm_call("gpt-4", random.uniform(0.3, 0.8))
    
    # Execute unit tests
    for i in range(4):
        with instrumentor.track_operation("database_calls", "execute_unit_test", {"test": i+1}):
            simulate_database_call("EXECUTE", random.uniform(0.02, 0.1))
    
    # Evaluate results
    with instrumentor.track_operation("llm_calls", "evaluate_results"):
        simulate_llm_call("gpt-4", random.uniform(0.5, 1.0))
    
    print("\n" + "-"*80)
    print("Simulation complete!")
    
    # Print summary
    instrumentor.print_summary()
    
    # Export metrics
    output_path = os.path.join(os.path.dirname(__file__), 'example_metrics.json')
    instrumentor.export_to_json(output_path)
    print(f"\n✓ Metrics exported to: {output_path}")
    
    # Show how to access specific data
    print("\n" + "="*80)
    print("Example: Accessing Specific Metrics")
    print("="*80)
    
    summary = instrumentor.get_summary()
    print(f"\nTotal LLM call time: {summary['categories']['llm_calls']['total_time']:.2f}s")
    print(f"Total database call time: {summary['categories']['database_calls']['total_time']:.2f}s")
    print(f"Percentage spent on LLM: {summary['categories']['llm_calls']['percentage']:.1f}%")
    
    timeline = instrumentor.get_timeline_data()
    print(f"\nTotal number of tracked operations: {len(timeline)}")
    print(f"First operation: {timeline[0]['operation_name']} ({timeline[0]['category']})")
    print(f"Last operation: {timeline[-1]['operation_name']} ({timeline[-1]['category']})")
    
    # Get category breakdown
    breakdown = instrumentor.get_category_breakdown()
    print(f"\nNumber of LLM calls: {len(breakdown['llm_calls'])}")
    print(f"Number of database calls: {len(breakdown['database_calls'])}")
    
    print("\n" + "="*80)
    print("To visualize these metrics, run:")
    print(f"  python visualize_metrics.py {output_path}")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
