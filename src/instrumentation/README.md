# CHESS Instrumentation

This instrumentation system tracks and aggregates time spent on different categories of operations in the CHESS text-to-SQL framework.

## Operation Categories

The instrumentor tracks the following operation categories:

1. **database_calls**: Time spent executing SQL queries against the database
2. **llm_calls**: Time spent on LLM inference and generation
3. **schema_operations**: Time spent on schema-related operations (parsing, validation, etc.)
4. **vector_db_operations**: Time spent querying vector databases
5. **embedding_operations**: Time spent generating embeddings
6. **minhash_lsh_operations**: Time spent on MinHash LSH operations

## Usage

### Automatic Tracking

The instrumentor is automatically initialized in `main.py` and tracks all operations throughout the pipeline execution. After the pipeline completes, metrics are automatically saved to the run-specific results directory:

```
results/<data_mode>/<setting>/<dataset>/<timestamp>/-instrumentation.json
```

For example:
```
results/dev/CHESS_LOCAL_LLM_IR_CG_UT/mini_dev_sqlite_10/2025-10-26T16:45:00.192703/-instrumentation.json
```

### Viewing Results

List all available runs:
```bash
python src/instrumentation/visualize_metrics.py --list

# Filter by data mode and setting
python src/instrumentation/visualize_metrics.py --list --data-mode dev --setting CHESS_LOCAL_LLM
```

Visualize a specific run:
```bash
# By full path
python src/instrumentation/visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00

# Or use the latest run
python src/instrumentation/visualize_metrics.py --latest --data-mode dev
```

### Manual Instrumentation

To manually instrument custom code:

```python
from instrumentation.instrumentor import Instrumentor

# Get the singleton instance
instrumentor = Instrumentor()

# Option 1: Using context manager (recommended)
with instrumentor.track_operation("database_calls", "my_custom_query", {"metadata": "value"}):
    # perform operation
    execute_my_query()

# Option 2: Manual start/stop
operation_id = instrumentor.start_operation("llm_calls", "custom_llm_call")
# perform operation
instrumentor.end_operation(operation_id)
```

## Output Metrics

The instrumentor exports metrics in JSON format with the following structure:

```json
{
  "session_info": {
    "start_time": "2025-10-26T12:00:00",
    "duration": 120.5
  },
  "summary": {
    "session_duration": 120.5,
    "total_operations": 150,
    "categories": {
      "database_calls": {
        "total_time": 45.3,
        "count": 50,
        "average_time": 0.906,
        "min_time": 0.001,
        "max_time": 5.2,
        "percentage": 37.6
      },
      "llm_calls": {
        "total_time": 60.2,
        "count": 30,
        "average_time": 2.007,
        "min_time": 0.5,
        "max_time": 8.1,
        "percentage": 49.9
      }
      // ... other categories
    }
  },
  "timeline": [
    {
      "category": "database_calls",
      "operation_name": "execute_sql",
      "start": 0.123,
      "end": 0.456,
      "duration": 0.333,
      "metadata": {"fetch": "all"}
    }
    // ... more operations
  ]
}
```

## Visualization

### Listing Available Runs

```bash
# List all runs with instrumentation data
python src/instrumentation/visualize_metrics.py --list

# Filter by data mode
python src/instrumentation/visualize_metrics.py --list --data-mode dev

# Filter by setting
python src/instrumentation/visualize_metrics.py --list --setting CHESS_LOCAL_LLM_IR_CG_UT
```

### Creating Timeline Plots

```bash
# Visualize a specific run
python src/instrumentation/visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00

# Visualize the latest run
python src/instrumentation/visualize_metrics.py --latest --data-mode dev --setting CHESS_LOCAL_LLM

# Custom output directory
python src/instrumentation/visualize_metrics.py <run_directory> --output ./my_analysis

# Print summary only (no plots)
python src/instrumentation/visualize_metrics.py --latest --no-plots
```

This will generate (in the run directory or custom output directory):
- A stacked timeline chart showing concurrent operations
- A pie chart showing the percentage breakdown by category
- A bar chart showing operation counts by category

### Custom Visualization

You can also create custom visualizations using the exported JSON data:

```python
import json
from pathlib import Path
import matplotlib.pyplot as plt

# Load metrics from a run directory
run_dir = Path("results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00")
with open(run_dir / "-instrumentation.json") as f:
    metrics = json.load(f)

# Access timeline data
timeline = metrics['timeline']

# Access summary statistics
summary = metrics['summary']
```

## API Reference

### Instrumentor Methods

- `start_session()`: Initialize a new instrumentation session
- `reset()`: Reset all tracked metrics
- `start_operation(category, operation_name, metadata=None)`: Start tracking an operation
- `end_operation(operation_id)`: Stop tracking an operation
- `track_operation(category, operation_name, metadata=None)`: Context manager for tracking
- `get_summary()`: Get aggregate statistics for all categories
- `get_timeline_data()`: Get chronological list of all operations
- `get_stacked_timeline(time_resolution=0.1)`: Get timeline data for stacked area charts
- `get_category_breakdown()`: Get operations grouped by category
- `export_to_json(filepath)`: Export all metrics to JSON
- `print_summary()`: Print formatted summary to console

## Integration with Agents

The instrumentor automatically tracks operations performed by all agents:

- **Information Retriever (IR) Agent**: Tracks embedding and vector DB operations
- **Schema Selector (SS) Agent**: Tracks schema operations
- **Candidate Generator (CG) Agent**: Tracks LLM calls
- **Unit Tester (UT) Agent**: Tracks database and LLM operations

## Performance Considerations

The instrumentor uses thread-safe operations and has minimal overhead:
- Uses a single Lock for thread safety
- Context managers ensure proper cleanup even on exceptions
- Metadata is optional and can be omitted for better performance

## Example Output

```
================================================================================
INSTRUMENTATION SUMMARY
================================================================================
Session Duration: 120.45s
Total Operations: 150

Category Breakdown:
--------------------------------------------------------------------------------

Database Calls:
  Total Time:    45.321s (37.6%)
  Call Count:    50
  Average Time:  0.906s
  Min/Max Time:  0.001s / 5.234s

Llm Calls:
  Total Time:    60.182s (49.9%)
  Call Count:    30
  Average Time:  2.006s
  Min/Max Time:  0.512s / 8.123s

Embedding Operations:
  Total Time:    8.456s (7.0%)
  Call Count:    12
  Average Time:  0.705s
  Min/Max Time:  0.234s / 1.456s

Vector Db Operations:
  Total Time:    4.234s (3.5%)
  Call Count:    15
  Average Time:  0.282s
  Min/Max Time:  0.123s / 0.678s

Schema Operations:
  Total Time:    1.876s (1.6%)
  Call Count:    28
  Average Time:  0.067s
  Min/Max Time:  0.012s / 0.234s

Minhash Lsh Operations:
  Total Time:    0.381s (0.3%)
  Call Count:    15
  Average Time:  0.025s
  Min/Max Time:  0.008s / 0.056s
================================================================================
```
