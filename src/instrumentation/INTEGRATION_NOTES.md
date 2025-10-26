# Instrumentation Integration with CHESS Results Structure

## Summary of Changes

The instrumentation system has been updated to integrate with CHESS's existing results directory structure. Metrics are now saved per-run and the visualization script can browse and select runs.

## Key Changes

### 1. Metrics Storage Location

**Before:**
```
data/dev/instrumentation_metrics_20251026_164500.json
```

**After:**
```
results/dev/CHESS_LOCAL_LLM_IR_CG_UT/mini_dev_sqlite_10/2025-10-26T16:45:00.192703/
├── -instrumentation.json  ← NEW: Instrumentation metrics
├── -statistics.json       ← Existing: Evaluation statistics
├── -predictions.json      ← Existing: SQL predictions
├── -args.json             ← Existing: Run arguments
└── logs/                  ← Existing: Task execution logs
```

### 2. Modified Files

#### `src/main.py`
Changed metrics export to use the run manager's result directory:
```python
# Export to run-specific directory with standard filename
metrics_path = os.path.join(run_manager.result_directory, "-instrumentation.json")
instrumentor.export_to_json(metrics_path)
```

#### `src/instrumentation/visualize_metrics.py`
Complete redesign to work with run directories:

**New Features:**
- `--list` - Browse all available runs with instrumentation data
- `--latest` - Automatically select the most recent run
- `--data-mode`, `--setting`, `--dataset` - Filter runs
- `--results-root` - Customize results directory location
- Accepts run directory path instead of direct JSON file path

**New Functions:**
- `find_instrumentation_file()` - Locate -instrumentation.json in a run directory
- `list_available_runs()` - Display all runs with filtering
- `get_latest_run()` - Find the most recent run matching filters

### 3. Updated Documentation

All documentation updated to reflect the new workflow:
- `QUICKSTART.md` - Updated examples and workflows
- `README.md` - Updated usage instructions
- New section on browsing runs

## Usage Examples

### Basic Workflow

```bash
# 1. Run CHESS (metrics automatically saved to results directory)
python src/main.py --data_mode dev --data_path data/dev/test.json --config run/configs/config.yaml

# 2. List all runs
python src/instrumentation/visualize_metrics.py --list

# 3. Visualize latest run
python src/instrumentation/visualize_metrics.py --latest --data-mode dev

# 4. Visualize specific run
python src/instrumentation/visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00
```

### Advanced Usage

```bash
# List runs with filters
python src/instrumentation/visualize_metrics.py --list --data-mode dev --setting CHESS_LOCAL_LLM

# Visualize latest run matching filters
python src/instrumentation/visualize_metrics.py --latest --data-mode dev --setting CHESS_LOCAL_LLM --dataset mini_dev_sqlite_10

# Export visualizations to custom directory
python src/instrumentation/visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00 --output ./analysis

# Print summary only (no plots)
python src/instrumentation/visualize_metrics.py --latest --no-plots
```

## Benefits

1. **Consistency**: Instrumentation data lives with other run artifacts
2. **Organization**: All results for a run are in one directory
3. **Traceability**: Easy to correlate instrumentation with predictions/statistics
4. **Discovery**: Can browse and filter runs to find what you need
5. **Convenience**: `--latest` flag for quick analysis of most recent run

## File Structure Example

A complete run directory now contains:

```
results/dev/CHESS_LOCAL_LLM_IR_CG_UT/mini_dev_sqlite_10/2025-10-26T16:45:00.192703/
├── -args.json                  # Run configuration
├── -instrumentation.json       # Performance metrics (NEW)
├── -predictions.json           # Generated SQL queries
├── -statistics.json            # Evaluation results
├── -generate_candidate.json    # SQL candidates
├── operation_timeline.png      # Visualization (generated on demand)
├── category_breakdown.png      # Visualization (generated on demand)
├── detailed_statistics.png     # Visualization (generated on demand)
└── logs/
    ├── 123_database_a.json     # Individual task logs
    └── 456_database_b.json
```

## Backward Compatibility

The instrumentation system itself is backward compatible - existing code that manually uses the Instrumentor class still works. Only the main.py integration and visualization script have changed.

The example script (`example.py`) still works as before, creating metrics in its own directory.

## Migration Guide

If you have existing instrumentation metrics files:

1. **Old format** (direct JSON files): Can still be loaded by modifying the visualization script to accept direct file paths, or move them into a mock run directory structure.

2. **Recommended**: Just re-run CHESS to generate new metrics in the proper location.

## Testing

To verify the changes work:

```bash
# 1. Run CHESS on a small dataset
python src/main.py --data_mode dev --data_path data/dev/mini_test.json --config run/configs/your_config.yaml

# 2. Check that -instrumentation.json was created
ls results/dev/*/*/2025-*/-instrumentation.json

# 3. List the run
python src/instrumentation/visualize_metrics.py --list

# 4. Visualize it
python src/instrumentation/visualize_metrics.py --latest --data-mode dev
```

## Future Enhancements

Possible future improvements:
1. Compare multiple runs side-by-side
2. Export comparison reports
3. Web-based dashboard for browsing runs
4. Automatic anomaly detection
5. Integration with the statistics manager for combined analysis
