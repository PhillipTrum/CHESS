#!/usr/bin/env python3
"""
Visualization script for CHESS instrumentation metrics.

This script creates visualizations from the instrumentation metrics JSON file:
- Stacked timeline chart showing operation categories over time
- Pie chart showing percentage breakdown by category
- Bar chart showing operation counts by category
- Detailed statistics tables

Usage:
    python visualize_metrics.py <run_directory> [--output <output_dir>]
    python visualize_metrics.py --list  # List available runs
    
Examples:
    python visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00.192703
    python visualize_metrics.py --list --data-mode dev --setting CHESS_LOCAL_LLM
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.collections import PolyCollection
    import numpy as np
except ImportError:
    print("Error: matplotlib is required for visualization.")
    print("Install it with: pip install matplotlib")
    exit(1)


# Color scheme for operation categories
CATEGORY_COLORS = {
    "database_calls": "#3498db",      # Blue
    "llm_calls": "#e74c3c",           # Red
    "schema_operations": "#2ecc71",    # Green
    "vector_db_operations": "#9b59b6", # Purple
    "embedding_operations": "#f39c12", # Orange
    "minhash_lsh_operations": "#1abc9c" # Turquoise
}


def load_metrics(filepath: str) -> Dict[str, Any]:
    """Load metrics from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def find_instrumentation_file(run_directory: str) -> str:
    """
    Find the instrumentation metrics file in a run directory.
    
    Args:
        run_directory: Path to the run directory
        
    Returns:
        Path to the instrumentation metrics file
        
    Raises:
        FileNotFoundError: If no instrumentation file is found
    """
    instrumentation_file = os.path.join(run_directory, "-instrumentation.json")
    if os.path.exists(instrumentation_file):
        return instrumentation_file
    
    raise FileNotFoundError(
        f"No instrumentation metrics file found in: {run_directory}\n"
        f"Expected: {instrumentation_file}"
    )


def list_available_runs(results_root: str = "results", data_mode: str = None, setting: str = None):
    """
    List all available runs with instrumentation data.
    
    Args:
        results_root: Root directory for results
        data_mode: Filter by data mode (e.g., 'dev', 'test')
        setting: Filter by setting name
    """
    print("\n" + "="*80)
    print("AVAILABLE RUNS WITH INSTRUMENTATION DATA")
    print("="*80)
    
    results_path = Path(results_root)
    if not results_path.exists():
        print(f"\nResults directory not found: {results_root}")
        return
    
    runs_found = 0
    
    # Iterate through results structure: results/<data_mode>/<setting>/<dataset>/<run_timestamp>
    for mode_dir in sorted(results_path.iterdir()):
        if not mode_dir.is_dir():
            continue
        if data_mode and mode_dir.name != data_mode:
            continue
            
        for setting_dir in sorted(mode_dir.iterdir()):
            if not setting_dir.is_dir():
                continue
            if setting and setting_dir.name != setting:
                continue
                
            for dataset_dir in sorted(setting_dir.iterdir()):
                if not dataset_dir.is_dir():
                    continue
                    
                for run_dir in sorted(dataset_dir.iterdir(), reverse=True):
                    if not run_dir.is_dir():
                        continue
                    
                    # Check if instrumentation file exists
                    instrumentation_file = run_dir / "-instrumentation.json"
                    if instrumentation_file.exists():
                        runs_found += 1
                        
                        # Load basic info
                        try:
                            with open(instrumentation_file) as f:
                                data = json.load(f)
                            duration = data['summary']['session_duration']
                            ops_count = data['summary']['total_operations']
                            
                            print(f"\n[{runs_found}] {mode_dir.name}/{setting_dir.name}/{dataset_dir.name}")
                            print(f"    Run: {run_dir.name}")
                            print(f"    Duration: {duration:.2f}s | Operations: {ops_count}")
                            print(f"    Path: {run_dir}")
                        except Exception as e:
                            print(f"\n[{runs_found}] {mode_dir.name}/{setting_dir.name}/{dataset_dir.name}")
                            print(f"    Run: {run_dir.name}")
                            print(f"    Path: {run_dir}")
                            print(f"    Note: Could not read metrics: {e}")
    
    if runs_found == 0:
        print("\nNo runs with instrumentation data found.")
        if data_mode or setting:
            print("Try without filters or check your filter values.")
    else:
        print("\n" + "="*80)
        print(f"Total runs found: {runs_found}")
        print("="*80)
        print("\nTo visualize a run, use:")
        print("  python visualize_metrics.py <run_path>")
    print()


def get_latest_run(results_root: str = "results", data_mode: str = None, 
                   setting: str = None, dataset: str = None) -> str:
    """
    Get the path to the latest run directory.
    
    Args:
        results_root: Root directory for results
        data_mode: Filter by data mode
        setting: Filter by setting name
        dataset: Filter by dataset name
        
    Returns:
        Path to the latest run directory
        
    Raises:
        FileNotFoundError: If no runs are found
    """
    results_path = Path(results_root)
    if not results_path.exists():
        raise FileNotFoundError(f"Results directory not found: {results_root}")
    
    latest_run = None
    latest_time = None
    
    for mode_dir in results_path.iterdir():
        if not mode_dir.is_dir():
            continue
        if data_mode and mode_dir.name != data_mode:
            continue
            
        for setting_dir in mode_dir.iterdir():
            if not setting_dir.is_dir():
                continue
            if setting and setting_dir.name != setting:
                continue
                
            for dataset_dir in setting_dir.iterdir():
                if not dataset_dir.is_dir():
                    continue
                if dataset and dataset_dir.name != dataset:
                    continue
                    
                for run_dir in dataset_dir.iterdir():
                    if not run_dir.is_dir():
                        continue
                    
                    # Check if instrumentation file exists
                    instrumentation_file = run_dir / "-instrumentation.json"
                    if not instrumentation_file.exists():
                        continue
                    
                    # Parse timestamp from directory name
                    try:
                        run_time = datetime.fromisoformat(run_dir.name)
                        if latest_time is None or run_time > latest_time:
                            latest_time = run_time
                            latest_run = str(run_dir)
                    except ValueError:
                        # If directory name is not a valid timestamp, skip
                        continue
    
    if latest_run is None:
        raise FileNotFoundError("No runs with instrumentation data found")
    
    return latest_run


def plot_timeline(metrics: Dict[str, Any], output_path: str):
    """Create a stacked timeline visualization."""
    timeline = metrics['timeline']
    if not timeline:
        print("No timeline data available.")
        return
    
    # Sort timeline by start time
    timeline = sorted(timeline, key=lambda x: x['start'])
    
    # Prepare data for plotting
    categories = set(op['category'] for op in timeline)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Track y-position for each category
    category_y_pos = {cat: i for i, cat in enumerate(sorted(categories))}
    
    # Plot each operation as a horizontal bar
    for op in timeline:
        category = op['category']
        start = op['start']
        duration = op['duration']
        y_pos = category_y_pos[category]
        
        color = CATEGORY_COLORS.get(category, '#95a5a6')
        ax.barh(y_pos, duration, left=start, height=0.8, 
                color=color, alpha=0.7, edgecolor='white', linewidth=0.5)
    
    # Customize plot
    ax.set_yticks(range(len(category_y_pos)))
    ax.set_yticklabels([cat.replace('_', ' ').title() for cat in sorted(categories)])
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('Operation Category', fontsize=12)
    ax.set_title('CHESS Operation Timeline', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add legend
    legend_patches = [mpatches.Patch(color=CATEGORY_COLORS.get(cat, '#95a5a6'), 
                                     label=cat.replace('_', ' ').title()) 
                     for cat in sorted(categories)]
    ax.legend(handles=legend_patches, loc='upper right', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Timeline plot saved to: {output_path}")
    plt.close()


def plot_category_breakdown(metrics: Dict[str, Any], output_dir: str):
    """Create pie chart and bar chart showing category breakdown."""
    summary = metrics['summary']
    categories_data = summary['categories']
    
    # Filter out categories with no data
    active_categories = {k: v for k, v in categories_data.items() if v['count'] > 0}
    
    if not active_categories:
        print("No category data available.")
        return
    
    # Prepare data
    labels = [cat.replace('_', ' ').title() for cat in active_categories.keys()]
    times = [data['total_time'] for data in active_categories.values()]
    counts = [data['count'] for data in active_categories.values()]
    colors = [CATEGORY_COLORS.get(cat, '#95a5a6') for cat in active_categories.keys()]
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Pie chart - Time distribution
    wedges, texts, autotexts = ax1.pie(times, labels=labels, colors=colors,
                                        autopct='%1.1f%%', startangle=90,
                                        textprops={'fontsize': 10})
    ax1.set_title('Time Distribution by Category', fontsize=14, fontweight='bold')
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # Bar chart - Operation counts
    x_pos = np.arange(len(labels))
    bars = ax2.bar(x_pos, counts, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax2.set_xlabel('Category', fontsize=12)
    ax2.set_ylabel('Number of Operations', fontsize=12)
    ax2.set_title('Operation Counts by Category', fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(labels, rotation=45, ha='right')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add count labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'category_breakdown.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Category breakdown saved to: {output_path}")
    plt.close()


def plot_detailed_statistics(metrics: Dict[str, Any], output_dir: str):
    """Create detailed statistics visualization."""
    summary = metrics['summary']
    categories_data = summary['categories']
    
    # Filter out categories with no data
    active_categories = {k: v for k, v in categories_data.items() if v['count'] > 0}
    
    if not active_categories:
        print("No category data available.")
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    labels = [cat.replace('_', ' ').title() for cat in active_categories.keys()]
    colors = [CATEGORY_COLORS.get(cat, '#95a5a6') for cat in active_categories.keys()]
    
    # 1. Total Time
    times = [data['total_time'] for data in active_categories.values()]
    bars1 = ax1.barh(labels, times, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Total Time (seconds)', fontsize=12)
    ax1.set_title('Total Time by Category', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    for i, bar in enumerate(bars1):
        width = bar.get_width()
        ax1.text(width, bar.get_y() + bar.get_height()/2., 
                f'{width:.2f}s',
                ha='left', va='center', fontsize=9, fontweight='bold', 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    # 2. Average Time
    avg_times = [data['average_time'] for data in active_categories.values()]
    bars2 = ax2.barh(labels, avg_times, color=colors, alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Average Time (seconds)', fontsize=12)
    ax2.set_title('Average Time per Operation', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    for i, bar in enumerate(bars2):
        width = bar.get_width()
        ax2.text(width, bar.get_y() + bar.get_height()/2., 
                f'{width:.3f}s',
                ha='left', va='center', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    # 3. Min/Max Times
    min_times = [data['min_time'] for data in active_categories.values()]
    max_times = [data['max_time'] for data in active_categories.values()]
    x = np.arange(len(labels))
    width = 0.35
    bars3a = ax3.bar(x - width/2, min_times, width, label='Min', 
                     color=colors, alpha=0.5, edgecolor='black')
    bars3b = ax3.bar(x + width/2, max_times, width, label='Max', 
                     color=colors, alpha=0.9, edgecolor='black')
    ax3.set_ylabel('Time (seconds)', fontsize=12)
    ax3.set_title('Min/Max Operation Times', fontsize=14, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(labels, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 4. Statistics Table
    ax4.axis('tight')
    ax4.axis('off')
    
    table_data = []
    for cat, data in active_categories.items():
        table_data.append([
            cat.replace('_', ' ').title(),
            f"{data['total_time']:.2f}s",
            data['count'],
            f"{data['average_time']:.3f}s",
            f"{data['percentage']:.1f}%"
        ])
    
    table = ax4.table(cellText=table_data,
                     colLabels=['Category', 'Total Time', 'Count', 'Avg Time', '%'],
                     cellLoc='left',
                     loc='center',
                     colWidths=[0.3, 0.15, 0.1, 0.15, 0.1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header
    for i in range(5):
        table[(0, i)].set_facecolor('#34495e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Color rows by category
    for i, cat in enumerate(active_categories.keys()):
        color = CATEGORY_COLORS.get(cat, '#95a5a6')
        for j in range(5):
            table[(i+1, j)].set_facecolor(color)
            table[(i+1, j)].set_alpha(0.3)
    
    ax4.set_title('Detailed Statistics', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'detailed_statistics.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Detailed statistics saved to: {output_path}")
    plt.close()


def print_text_summary(metrics: Dict[str, Any]):
    """Print a text summary of the metrics."""
    summary = metrics['summary']
    session_info = metrics.get('session_info', {})
    
    print("\n" + "="*80)
    print("INSTRUMENTATION SUMMARY")
    print("="*80)
    
    if 'start_time' in session_info:
        print(f"Session Start: {session_info['start_time']}")
    print(f"Session Duration: {summary['session_duration']:.2f}s")
    print(f"Total Operations: {summary['total_operations']}")
    
    print("\nCategory Breakdown:")
    print("-"*80)
    
    for category, stats in sorted(summary['categories'].items()):
        if stats['count'] > 0:
            print(f"\n{category.replace('_', ' ').title()}:")
            print(f"  Total Time:    {stats['total_time']:.3f}s ({stats['percentage']:.1f}%)")
            print(f"  Call Count:    {stats['count']}")
            print(f"  Average Time:  {stats['average_time']:.3f}s")
            print(f"  Min/Max Time:  {stats['min_time']:.3f}s / {stats['max_time']:.3f}s")
    
    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize CHESS instrumentation metrics from a run directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Visualize a specific run
  python visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00

  # List all available runs
  python visualize_metrics.py --list
  
  # List runs filtered by data mode and setting
  python visualize_metrics.py --list --data-mode dev --setting CHESS_LOCAL_LLM
  
  # Visualize latest run with filters
  python visualize_metrics.py --latest --data-mode dev --setting CHESS_LOCAL_LLM
  
  # Custom output directory
  python visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00 --output ./viz
        """
    )
    parser.add_argument('run_directory', nargs='?', 
                       help='Path to the run directory (contains -instrumentation.json)')
    parser.add_argument('--output', '-o', 
                       help='Output directory for visualizations (default: same as run directory)')
    parser.add_argument('--no-plots', action='store_true', 
                       help='Skip generating plots, only print summary')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List all available runs with instrumentation data')
    parser.add_argument('--latest', action='store_true',
                       help='Use the latest run (can be combined with filters)')
    parser.add_argument('--data-mode', 
                       help='Filter by data mode (e.g., dev, test)')
    parser.add_argument('--setting',
                       help='Filter by setting name (e.g., CHESS_LOCAL_LLM)')
    parser.add_argument('--dataset',
                       help='Filter by dataset name')
    parser.add_argument('--results-root', default='results',
                       help='Root directory for results (default: results)')
    
    args = parser.parse_args()
    
    # Handle --list mode
    if args.list:
        list_available_runs(args.results_root, args.data_mode, args.setting)
        return
    
    # Handle --latest mode
    if args.latest:
        try:
            run_directory = get_latest_run(
                args.results_root, 
                args.data_mode, 
                args.setting, 
                args.dataset
            )
            print(f"Using latest run: {run_directory}\n")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("\nUse --list to see available runs")
            exit(1)
    elif args.run_directory:
        run_directory = args.run_directory
    else:
        parser.print_help()
        print("\nError: Please specify a run directory, use --latest, or use --list")
        exit(1)
    
    # Find instrumentation file in the run directory
    try:
        metrics_file = find_instrumentation_file(run_directory)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nUse --list to see available runs with instrumentation data")
        exit(1)
    
    # Load metrics
    print(f"Loading metrics from: {metrics_file}")
    try:
        metrics = load_metrics(metrics_file)
    except Exception as e:
        print(f"Error loading metrics file: {e}")
        exit(1)
    
    # Print text summary
    print_text_summary(metrics)
    
    if args.no_plots:
        return
    
    # Determine output directory
    if args.output:
        output_dir = args.output
    else:
        output_dir = run_directory
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate visualizations
    print(f"\nGenerating visualizations in: {output_dir}")
    print("-" * 80)
    
    timeline_path = os.path.join(output_dir, 'operation_timeline.png')
    plot_timeline(metrics, timeline_path)
    
    plot_category_breakdown(metrics, output_dir)
    
    plot_detailed_statistics(metrics, output_dir)
    
    print("-" * 80)
    print(f"\n✓ All visualizations generated successfully!")
    print(f"  Output directory: {output_dir}")
    print(f"  Run directory: {run_directory}")


if __name__ == '__main__':
    main()
