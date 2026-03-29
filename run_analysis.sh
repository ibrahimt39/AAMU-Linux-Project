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
pip3 install --user pandas numpy scikit-learn matplotlib seaborn 2>&1 | tail -1
echo ""

# ---- Verify dataset exists ----
DATASET="iot23_dataset.csv"
if [ ! -f "$DATASET" ]; then
    echo "ERROR: Dataset file '$DATASET' not found in $(pwd)"
    echo ""
    echo "Please download the IoT-23 dataset and place it here."
    echo "Source: https://www.kaggle.com/datasets/arbazkhan971/iot23-dataset"
    echo ""
    echo "If using Kaggle CLI:"
    echo "  pip3 install --user kaggle"
    echo "  kaggle datasets download -d arbazkhan971/iot23-dataset"
    echo "  unzip iot23-dataset.zip"
    exit 1
fi

echo "Dataset found: $DATASET ($(du -h $DATASET | cut -f1))"
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
