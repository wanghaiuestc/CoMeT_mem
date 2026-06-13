#!/bin/bash

# ==============================================================================
# HotSpot Model Extraction & Verification Pipeline
# ==============================================================================

# 1. HotSpot Run Configuration
# Modify paths to your HotSpot binary, floorplan, and power trace as needed.
HOTSPOT_PATH="/Users/hwang/Documents/git_repos/hotspot_with_model_extract"
COMET_PATH="/Users/hwang/Documents/git_repos/CoMeT_mem"
WORK_PATH=$COMET_PATH"/benchmarks"
MODEL_PATH=$WORK_PATH"/model_extract"
HOTSPOT_BIN=$HOTSPOT_PATH"/hotspot"
# FLOORPLAN="./DDR_16core/cores.lcf"
POWER_TRACE=$WORK_PATH"/power_mem.trace"
CONFIG=$COMET_PATH"/config/hotspot/3D/stack_hotspot.config"
OUTPUT_TEMP=$WORK_PATH"/temperature_mem.trace"
OTHERS="-model_secondary 1 -model_type grid -all_transient_file all_transient_mem.init -steady_state_print_disable 1 -l 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,  -type 3D -sampling_intvl 0.001 -grid_layer_file /Users/hwang/Documents/git_repos/CoMeT_mem/config/hotspot/3D/stack.lcf -detailed_3D on"

# ==============================================================================

echo "--- Starting Model Extraction Pipeline ---"

# Step 1: Run HotSpot
echo "[1/3] Running HotSpot simulation..."
cd $WORK_PATH
$HOTSPOT_BIN \
    -c $CONFIG \
    -p $POWER_TRACE \
    -o $OUTPUT_TEMP \
    $OTHERS

# Step 2: Extract matrices
echo "[2/3] Processing matrix extraction..."
cd $MODEL_PATH
python3 model_extract.py transient

# Step 3: Run model verification reading from config
echo "[3/3] Performing model verification..."
python3 check_model.py --config $CONFIG --power_trace $POWER_TRACE --temp_trace $OUTPUT_TEMP

echo "--- Model Extraction and Verification Complete ---"
