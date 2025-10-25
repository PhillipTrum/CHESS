#!/bin/bash
# Run script for CHESS using local LLM (qwen-local)
# Make sure your local LLM server is running on port 39494 before executing this script

source .env
data_mode=$DATA_MODE # Options: 'dev', 'train' 
data_path=$DATA_PATH # UPDATE THIS WITH THE PATH TO THE TARGET DATASET

config="./run/configs/CHESS_LOCAL_LLM_IR_CG_UT.yaml"

num_workers=1 # Number of workers to use for parallel processing, set to 1 for no parallel processing

echo "================================================================"
echo "Running CHESS with Local LLM (qwen-local)"
echo "Config: $config"
echo "Data Mode: $data_mode"
echo "Data Path: $data_path"
echo "================================================================"
echo ""
echo "Make sure your local LLM server is running on port 39494!"
echo "If not, run: python3 launch_llmserver.py"
echo ""
echo "================================================================"

python3 -u ./src/main.py --data_mode ${data_mode} --data_path ${data_path} --config "$config" \
        --num_workers ${num_workers} --pick_final_sql true 
