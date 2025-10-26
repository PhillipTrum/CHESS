# CHESS Instrumentation - Quick Reference

## 📍 Where Metrics Are Saved

```
results/<data_mode>/<setting>/<dataset>/<timestamp>/-instrumentation.json
```

Example:
```
results/dev/CHESS_LOCAL_LLM_IR_CG_UT/mini_dev_sqlite_10/2025-10-26T16:45:00.192703/-instrumentation.json
```

## 🔍 List Available Runs

```bash
# All runs
python src/instrumentation/visualize_metrics.py --list

# Filter by data mode
python src/instrumentation/visualize_metrics.py --list --data-mode dev

# Filter by setting
python src/instrumentation/visualize_metrics.py --list --setting CHESS_LOCAL_LLM
```

## 📊 Visualize Runs

```bash
# Latest run
python src/instrumentation/visualize_metrics.py --latest

# Latest with filters
python src/instrumentation/visualize_metrics.py --latest --data-mode dev --setting CHESS_LOCAL_LLM

# Specific run
python src/instrumentation/visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/2025-10-26T16:45:00

# Summary only (no plots)
python src/instrumentation/visualize_metrics.py --latest --no-plots

# Custom output directory
python src/instrumentation/visualize_metrics.py <run_dir> --output ./my_viz
```

## 📈 What Gets Generated

In the run directory (or custom output):
- `operation_timeline.png` - Timeline of all operations
- `category_breakdown.png` - Pie chart and bar chart
- `detailed_statistics.png` - Detailed stats tables

## 🎯 Operation Categories

1. **database_calls** - SQL query execution
2. **llm_calls** - LLM inference
3. **schema_operations** - Schema parsing/validation
4. **vector_db_operations** - Vector DB queries
5. **embedding_operations** - Text embedding generation
6. **minhash_lsh_operations** - LSH operations

## 📝 Quick Analysis

```bash
# See summary of latest run
python src/instrumentation/visualize_metrics.py --latest --no-plots

# Generate all visualizations
python src/instrumentation/visualize_metrics.py --latest
```

## 🔧 Common Commands

```bash
# After running CHESS, check what was created
python src/instrumentation/visualize_metrics.py --list --data-mode dev | tail -20

# Analyze the most recent run
python src/instrumentation/visualize_metrics.py --latest --data-mode dev

# Compare two runs (view separately)
python src/instrumentation/visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/RUN1 --output ./analysis/run1
python src/instrumentation/visualize_metrics.py results/dev/CHESS_LOCAL_LLM/dataset/RUN2 --output ./analysis/run2
```

## 📚 Files

- **QUICKSTART.md** - Step-by-step guide
- **README.md** - Complete documentation
- **INTEGRATION_NOTES.md** - Technical details
- **IMPLEMENTATION_SUMMARY.md** - Implementation overview

## 💡 Pro Tips

1. Use `--list` to find your runs
2. Use `--latest` for quick analysis
3. Use `--no-plots` for fast summary
4. Filters speed up finding specific runs
5. Metrics are saved automatically with each run

## 🚨 Troubleshooting

**Can't find metrics?**
```bash
python src/instrumentation/visualize_metrics.py --list
```

**Want latest run?**
```bash
python src/instrumentation/visualize_metrics.py --latest --data-mode dev
```

**Need help?**
```bash
python src/instrumentation/visualize_metrics.py --help
```
