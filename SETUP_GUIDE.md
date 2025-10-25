# CHESS Setup Guide - Local LLM Edition

## Overview

This guide covers the complete setup for running CHESS with a locally deployed LLM (Qwen 2.5 7B Instruct). CHESS has been configured to work with your local model running on port 39494, enabling privacy-preserving, cost-free SQL generation.

## Quick Start

### Prerequisites
- Local LLM server running on port 39494
- OpenAI API key (for preprocessing only) OR willingness to use local embeddings

### Setup Steps

1. **Verify Configuration**
   ```bash
   cd CHESS
   ./verify_setup.sh
   ```

2. **Add API Key** (edit `.env`)
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```
   *Note: Only needed for preprocessing. For 100% local setup, see "Local Embeddings" section.*

3. **Run Preprocessing** (one-time, ~$1 cost with OpenAI)
   ```bash
   sh run/run_preprocess.sh
   ```

4. **Start Local LLM Server**
   ```bash
   python3 ../launch_llmserver.py
   ```

5. **Run CHESS**
   ```bash
   sh run/run_main_local_llm.sh
   ```

---

## What Was Configured

### 1. Fixed Data Paths ✅

**Problem:** `.env` pointed to non-existent files  
**Solution:** Updated to correct MINIDEV paths

```bash
# Corrected paths in .env:
DATA_PATH="./data/dev/MINIDEV/mini_dev_sqlite.json"       # 500 questions
DB_ROOT_DIRECTORY="./data/dev/MINIDEV/dev_databases"      # 11 databases
DATA_TABLES_PATH="./data/dev/MINIDEV/dev_tables.json"
```

**Your Dataset:**
- 500 SQL questions across 11 databases
- Databases: california_schools, card_games, codebase_community, debit_card_specializing, european_football_2, financial, formula_1, student_club, superhero, thrombosis_prediction, toxicology

### 2. Local LLM Integration ✅

**Added** `qwen-local` engine to `src/llm/engine_configs.py`:
```python
"qwen-local": {
    "constructor": ChatOpenAI,
    "params": {
        "model": "qwen/qwen2.5-7b-instruct",
        "openai_api_key": "EMPTY",
        "openai_api_base": "http://127.0.0.1:39494/v1",
        "max_tokens": 1000,
        "temperature": 0,
    }
}
```

**Created** configuration file: `run/configs/CHESS_LOCAL_LLM_IR_CG_UT.yaml`
- Uses `qwen-local` for all agents (IR + CG + UT)
- 5 candidates per template
- 10 unit tests for validation

**Created** run script: `run/run_main_local_llm.sh`

### 3. Preprocessing Setup ✅

**What preprocessing does:**
- Creates LSH indexes for fast database value matching
- Creates vector databases using embeddings for schema retrieval
- One-time process, results cached in each database directory

**Current setup:** Uses OpenAI embeddings (`text-embedding-3-large`)
- Cost: ~$1 for 11 databases (one-time)
- Alternative: See "Local Embeddings" below for 100% free option

---

## Usage

### Using Your Local LLM

Simply use `qwen-local` as the engine in any YAML config:

```yaml
information_retriever:
  engine: 'qwen-local'
  
candidate_generator:
  engine: 'qwen-local'
  
unit_tester:
  engine: 'qwen-local'
```

### Hybrid Mode (Mix Local + Cloud)

Optimize costs by using local LLM for some tasks, cloud for others:

```yaml
information_retriever:
  engine: 'qwen-local'      # Free local processing

candidate_generator:
  engine: 'gpt-4o-mini'     # Cloud for complex generation
```

### Verification Script

Run anytime to check setup status:
```bash
./verify_setup.sh
```

Shows:
- ✓ Path correctness
- ✓ Dataset statistics (500 questions, 11 databases)
- ✓ API key status
- ✓ Preprocessing completion for each database

---

## 100% Local Setup (No API Costs)

To avoid OpenAI entirely, use local embeddings for preprocessing:

### Steps:

1. **Install sentence-transformers**
   ```bash
   pip install sentence-transformers
   ```

2. **Modify** `src/database_utils/db_catalog/preprocess.py`
   
   Replace:
   ```python
   from langchain_openai import OpenAIEmbeddings
   EMBEDDING_FUNCTION = OpenAIEmbeddings(model="text-embedding-3-large")
   ```
   
   With:
   ```python
   from langchain_huggingface import HuggingFaceEmbeddings
   EMBEDDING_FUNCTION = HuggingFaceEmbeddings(
       model_name="sentence-transformers/all-MiniLM-L6-v2",
       model_kwargs={'device': 'cpu'},  # or 'cuda' for GPU
       encode_kwargs={'normalize_embeddings': True}
   )
   ```

3. **Modify** `src/workflow/agents/information_retriever/tool_kit/retrieve_entity.py`
   
   In `__init__` method (line ~34), replace:
   ```python
   self.embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
   ```
   
   With:
   ```python
   from langchain_huggingface import HuggingFaceEmbeddings
   self.embedding_function = HuggingFaceEmbeddings(
       model_name="sentence-transformers/all-MiniLM-L6-v2",
       model_kwargs={'device': 'cpu'},
       encode_kwargs={'normalize_embeddings': True}
   )
   ```

4. **Run preprocessing** (no API key needed)
   ```bash
   sh run/run_preprocess.sh
   ```

**Local Embedding Models:**
- `all-MiniLM-L6-v2`: Fast, 384 dims, 23MB (recommended for CPU)
- `all-mpnet-base-v2`: Better quality, 768 dims, 420MB (GPU recommended)
- `BAAI/bge-large-en-v1.5`: Best quality, 1024 dims, 1.3GB (GPU required)

---

## Configuration Files

### Main Configurations

- **`run/configs/CHESS_LOCAL_LLM_IR_CG_UT.yaml`** - Local LLM with IR+CG+UT agents
- **`run/configs/CHESS_IR_CG_UT.yaml`** - Original config with GPT-4o-mini
- **`run/configs/CHESS_IR_SS_CG.yaml`** - With Schema Selector (for large DBs)

### Run Scripts

- **`run/run_main_local_llm.sh`** - Run with local LLM
- **`run/run_main_ir_cg_ut.sh`** - IR + CG + UT agents
- **`run/run_main_ir_ss_cg.sh`** - IR + SS + CG agents (no unit testing)
- **`run/run_preprocess.sh`** - Preprocessing databases

### Difference Between Configs

**IR_CG_UT (Information Retriever + Candidate Generator + Unit Tester):**
- Validates SQL with LLM-generated unit tests
- Generates 10-20 candidates per question
- Best for correctness validation

**IR_SS_CG (Information Retriever + Schema Selector + Candidate Generator):**
- Prunes large schemas before generation
- Reduces token usage by ~5x
- Best for very large databases

---

## Troubleshooting

### Connection to Local LLM Failed
```bash
# Check if server is running
curl http://127.0.0.1:39494/v1/models

# Verify port in engine_configs.py matches launch_llmserver.py
```

### Preprocessing Fails
```bash
# Check OpenAI API key is set
echo $OPENAI_API_KEY

# Or switch to local embeddings (see above)
```

### Path Not Found Errors
```bash
# Verify paths are correct
./verify_setup.sh

# Should show MINIDEV paths, not dev paths
```

### Import Errors
```bash
# Install missing dependencies
pip install -r requirements.txt

# For local embeddings:
pip install sentence-transformers
```

---

## Advanced Usage

### Adding Other Local Models

Edit `src/llm/engine_configs.py`:

```python
"my-local-model": {
    "constructor": ChatOpenAI,
    "params": {
        "model": "model-name",
        "openai_api_key": "EMPTY",
        "openai_api_base": "http://127.0.0.1:PORT/v1",
        "max_tokens": 1000,
        "temperature": 0,
    }
}
```

Then use `'my-local-model'` in YAML configs.

### Custom Configurations

Create new YAML config by copying existing one:
```bash
cp run/configs/CHESS_LOCAL_LLM_IR_CG_UT.yaml run/configs/my_config.yaml
# Edit my_config.yaml
# Update run script to use: config="./run/configs/my_config.yaml"
```

### Performance Tuning

Adjust in YAML configs:
- `sampling_count`: Number of candidates (lower = faster)
- `unit_test_count`: Number of tests (lower = faster)
- `temperature`: 0=deterministic, higher=creative
- `top_k`: Vector search results (lower = faster)

---

## Files Structure

```
CHESS/
├── .env                          # Configuration (UPDATED)
├── verify_setup.sh              # Setup verification script
├── test_local_llm.py            # Test local LLM integration
├── run/
│   ├── run_preprocess.sh        # Preprocessing script
│   ├── run_main_local_llm.sh   # Run with local LLM (NEW)
│   └── configs/
│       └── CHESS_LOCAL_LLM_IR_CG_UT.yaml  # Local LLM config (NEW)
├── src/
│   ├── llm/
│   │   ├── engine_configs.py    # Added qwen-local (MODIFIED)
│   │   └── models.py
│   └── database_utils/
│       └── db_catalog/
│           └── preprocess.py    # Uses OpenAI embeddings
└── data/dev/MINIDEV/            # Your dataset (500 questions, 11 DBs)
```

---

## Summary

**What was done:**
1. ✅ Fixed incorrect paths in `.env` to point to MINIDEV dataset
2. ✅ Added `qwen-local` engine configuration for your local LLM
3. ✅ Created YAML config using local LLM for all agents
4. ✅ Created run script for easy execution
5. ✅ Verified dataset exists (500 questions, 11 databases)
6. ✅ Documented local embeddings option for 100% offline setup

**Current status:**
- Paths: ✅ Corrected
- Local LLM: ✅ Configured
- Dataset: ✅ Ready (500 questions)
- Preprocessing: ⏳ Pending (add API key OR use local embeddings)

**Next step:**
Add OpenAI API key to `.env` and run `sh run/run_preprocess.sh`  
OR  
Configure local embeddings (see "100% Local Setup" section) for zero-cost setup.

---

For questions or issues, check the troubleshooting section or run `./verify_setup.sh` to diagnose problems.
