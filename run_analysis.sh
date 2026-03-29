#!/bin/bash
#
# run_analysis.sh - Launch IoT-23 intrusion detection on ASAX (Alabama Supercomputer)
# Course: Linux Team Project - Alabama A&M University
#
# Usage:
#   sbatch run_analysis.sh
#   OR
#   bash run_analysis.sh
#

#SBATCH --job-name=iot23_detection
#SBATCH --output=iot23_output_%j.log
#SBATCH --error=iot23_error_%j.log
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

echo "============================================"
echo "  IoT-23 Intrusion Detection Analysis"
echo "  Alabama A&M University - Linux Project"
echo "============================================"
echo ""
echo "Date: $(date)"
echo "Hostname: $(hostname)"
echo "Working directory: $(pwd)"
echo ""

# ---- Load required modules on ASAX ----
echo "Loading software modules..."
module load python/3.9 2>/dev/null || module load python3 2>/dev/null || echo "No module system found, using system Python"

# Check Python version
echo "Python version: $(python3 --version 2>&1)"
echo ""

# ---- Install required packages (user-level) ----
echo "Installing required Python packages..."
pip3 install --user pandas numpy scikit-learn matplotlib seaborn kaggle 2>&1 | tail -1
echo ""

# ---- Download and prepare dataset if needed ----
DATASET="iot23_combined.csv"
if [ ! -f "$DATASET" ]; then
    echo "Dataset not found. Downloading from Kaggle..."
    echo ""

    if [ -z "$KAGGLE_API_TOKEN" ]; then
        echo "ERROR: KAGGLE_API_TOKEN is not set."
        echo "Run:  export KAGGLE_API_TOKEN=your_token_here"
        echo "Then re-run this script."
        exit 1
    fi

    kaggle datasets download -d srifqi/iot-23-cleaned-data
    unzip -o iot-23-cleaned-data.zip

    echo "Combining CSV files..."
    python3 -c "
import pandas as pd, glob
files = sorted(glob.glob('CTU-*.csv'))
dfs = [pd.read_csv(f, sep='|') for f in files]
combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('iot23_combined.csv', index=False)
print(f'Combined {len(files)} files: {combined.shape[0]:,} rows')
"

    # Clean up individual files
    rm -f CTU-*.csv iot-23-cleaned-data.zip
    echo ""
fi

echo "Dataset: $DATASET ($(du -h $DATASET | cut -f1))"
echo ""

# ---- Run the analysis ----
echo "Starting analysis..."
echo "--------------------------------------------"
python3 iot_intrusion_detection.py "$DATASET"
EXIT_CODE=$?
echo "--------------------------------------------"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "Analysis completed successfully!"
    echo ""
    echo "Output files in results/:"
    ls -lh results/ 2>/dev/null
else
    echo "Analysis failed with exit code $EXIT_CODE"
fi

echo ""
echo "Finished: $(date)"
