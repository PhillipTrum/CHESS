# CHESS Instrumentation - Quick Start Guide

## 🚀 Quick Start

### 1. Run CHESS with Automatic Instrumentation

The instrumentation is already integrated - just run CHESS normally:

```bash
cd /mnt/scratch/ptrummer/CHESS

# Run with your normal configuration
python src/main.py \
    --data_mode dev \
    --data_path data/dev/your_data.json \
    --config run/configs/your_config.yaml
```

**What happens:**
- ✓ Instrumentation automatically tracks all operations
- ✓ Metrics are saved to `results/<data_mode>/<setting>/<dataset>/<timestamp>/-instrumentation.json`
- ✓ Summary is printed to console at the end

### 2. List Available Runs

See all runs with instrumentation data:

```bash
# List all runs
python src/instrumentation/visualize_metrics.py --list

# Filter by data mode and setting
python src/instrumentation/visualize_metrics.py --list --data-mode dev --setting CHESS_LOCAL_LLM
```

**Output example:**
```
AVAILABLE RUNS WITH INSTRUMENTATION DATA
================================================================================

[1] dev/CHESS_LOCAL_LLM_IR_CG_UT/mini_dev_sqlite_10
    Run: 2025-10-26T16:45:00.192703
    Duration: 120.45s | Operations: 150
    Path: results/dev/CHESS_LOCAL_LLM_IR_CG_UT/mini_dev_sqlite_10/2025-10-26T16:45:00.192703

[2] dev/CHESS_LOCAL_LLM_IR_CG_UT/mini_dev_sqlite_10
    Run: 2025-10-26T14:30:00.123456
    Duration: 98.23s | Operations: 142
    Path: results/dev/CHESS_LOCAL_LLM_IR_CG_UT/mini_dev_sqlite_10/2025-10-26T14:30:00.123456
```

### 3. Visualize a Specific Run

Generate visual reports from any run:

```bash
# Using full path
python src/instrumentation/visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00.192703

# Or using the latest run
python src/instrumentation/visualize_metrics.py --latest --data-mode dev --setting CHESS_LOCAL_LLM
```

**Output files (saved in the run directory):**
- `operation_timeline.png` - Timeline showing when each operation occurred
- `category_breakdown.png` - Pie chart and bar chart of time/count distribution
- `detailed_statistics.png` - Detailed comparison of all categories

### 4. Analyze the Results

The instrumentation file is in the run directory:

```
results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00.192703/
├── -instrumentation.json  ← Instrumentation metrics
├── -statistics.json       ← Evaluation statistics
├── -predictions.json      ← SQL predictions
├── -args.json             ← Run arguments
└── logs/                  ← Individual task logs
```

Open `-instrumentation.json` to see:

```json
{
  "summary": {
    "categories": {
      "llm_calls": {
        "total_time": 60.2,
        "percentage": 49.9
      },
      "database_calls": {
        "total_time": 45.3,
        "percentage": 37.6
      }
      // ...
    }
  }
}
```

**Key metrics to check:**
- `percentage` - Which category takes most time?
- `count` - How many operations in each category?
- `average_time` - Are some operations unusually slow?
- `max_time` - Any outliers to investigate?

## 📊 Understanding the Output

### Console Summary

At the end of CHESS execution, you'll see:

```
================================================================================
INSTRUMENTATION SUMMARY
================================================================================
Session Duration: 120.45s
Total Operations: 150

Category Breakdown:
--------------------------------------------------------------------------------

Llm Calls:
  Total Time:    60.182s (49.9%)  ← 50% of time spent on LLM
  Call Count:    30                ← 30 LLM calls made
  Average Time:  2.006s            ← ~2s per call
  Min/Max Time:  0.512s / 8.123s  ← Fastest/slowest call
```

### What Each Category Means

- **database_calls**: SQL query execution (SELECT, INSERT, etc.)
- **llm_calls**: Time waiting for LLM responses
- **schema_operations**: Parsing SQL, validating schema structure
- **vector_db_operations**: Similarity searches in vector database
- **embedding_operations**: Converting text to embeddings
- **minhash_lsh_operations**: Finding similar database values

## 🎯 Common Use Cases

### Find Performance Bottlenecks

Look at the `percentage` values - categories with high percentages are bottlenecks.

```bash
# View summary only (no plots)
python src/instrumentation/visualize_metrics.py --latest --no-plots
```

### Compare Different Runs

List and compare different runs:

```bash
# List all runs for a specific setting
python src/instrumentation/visualize_metrics.py --list --setting CHESS_LOCAL_LLM

# Visualize specific runs
python src/instrumentation/visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T120000
python src/instrumentation/visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T130000
```

### Export Visualizations to Custom Location

```bash
# Export to a custom directory
python src/instrumentation/visualize_metrics.py \
  results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00 \
  --output ./analysis/run1
```

### Analyze Timeline

Use the timeline visualization to see:
- Are operations happening in parallel or sequentially?
- Are there idle periods?
- Which agent is taking the most time?

### Export Data for Further Analysis

The JSON format is easy to parse in Python:

```python
import json
import pandas as pd
from pathlib import Path

# Load metrics from a run directory
run_dir = Path("results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00")
with open(run_dir / "-instrumentation.json") as f:
    data = json.load(f)

# Convert to DataFrame for analysis
df = pd.DataFrame(data['timeline'])

# Analyze by category
print(df.groupby('category')['duration'].describe())

# Find slowest operations
print(df.nlargest(10, 'duration'))
```

## 🔧 Troubleshooting

### No metrics file generated?

Check:
1. Did CHESS complete successfully?
2. Do you have write permissions in the results directory?
3. Check console for error messages
4. Look for `-instrumentation.json` in the run directory

### Can't find your run?

```bash
# List all available runs
python src/instrumentation/visualize_metrics.py --list

# Use filters to narrow down
python src/instrumentation/visualize_metrics.py --list --data-mode dev
```

### Visualization script fails?

Install matplotlib if needed:
```bash
pip install matplotlib
```

### Want to add custom instrumentation?

```python
from instrumentation.instrumentor import Instrumentor

instrumentor = Instrumentor()

# Wrap any code block
with instrumentor.track_operation("database_calls", "my_custom_query"):
    my_database_operation()
```

## 📚 More Information

- Full documentation: `src/instrumentation/README.md`
- Implementation details: `src/instrumentation/IMPLEMENTATION_SUMMARY.md`
- Example code: `src/instrumentation/example.py`

## 🎨 Customization

### Change Output Directory

Modify `main.py`:

```python
# Instead of:
output_dir = os.path.dirname(args.data_path)

# Use:
output_dir = "/path/to/custom/metrics/directory"
```

### Add Metadata to Operations

```python
with instrumentor.track_operation(
    "llm_calls", 
    "generate_sql",
    metadata={"model": "gpt-4", "temperature": 0.7}
):
    call_llm()
```

Metadata appears in the JSON output for detailed analysis.

## 💡 Tips

1. **Use --list often**: Quickly see all available runs
2. **Use --latest**: Analyze the most recent run without typing full path
3. **Check for outliers**: Use min/max times to find unusual operations
4. **Focus optimization**: Optimize categories with highest time percentages first
5. **Track changes**: Compare metrics before and after optimizations

## Example Workflow

```bash
# 1. Run CHESS
python src/main.py --data_mode dev --data_path data/dev/test.json --config run/configs/default.yaml

# 2. List available runs to confirm it completed
python src/instrumentation/visualize_metrics.py --list --data-mode dev

# 3. Quick check of results
python src/instrumentation/visualize_metrics.py --latest --data-mode dev --no-plots

# 4. Generate full visualizations
python src/instrumentation/visualize_metrics.py --latest --data-mode dev

# 5. Review the plots in the run directory
# results/dev/<setting>/<dataset>/<timestamp>/*.png

# 6. Make optimizations based on findings

# 7. Run again and compare!
python src/main.py --data_mode dev --data_path data/dev/test.json --config run/configs/optimized.yaml
```

---

**Ready to start?** Just run CHESS as normal - instrumentation is already active! 🎉
