#!/bin/bash

# Script to verify the original and locked .th circuits using ABC and SAT solvers

# Check if enough arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <original_th_file> <locked_th_file>"
    exit 1
fi

# Paths to the input .th files
ORIGINAL_TH_FILE=$1
LOCKED_TH_FILE=$2

# Create a unique output directory based on the circuit name
OUTPUT_DIR=$(dirname "$LOCKED_TH_FILE")
mkdir -p "$OUTPUT_DIR"

# Path to the ABC binary
ABC_BINARY="/home/asahruri/work/threABC/bin/abc"

# Run ABC verification commands
echo "Running ABC verification commands..."
$ABC_BINARY -c "
tvr $ORIGINAL_TH_FILE $LOCKED_TH_FILE;
tvr -V 1 $ORIGINAL_TH_FILE $LOCKED_TH_FILE;
q;
"

# Check if the compTH files were generated in the current directory
if [ -f "compTH.opb" ]; then
    echo "Moving compTH.opb to ${OUTPUT_DIR}..."
    mv compTH.opb "$OUTPUT_DIR/"
else
    echo "Warning: compTH.opb not found. Skipping Minisat+ verification."
fi

if [ -f "compTH.dimacs" ]; then
    echo "Moving compTH.dimacs to ${OUTPUT_DIR}..."
    mv compTH.dimacs "$OUTPUT_DIR/"
else
    echo "Warning: compTH.dimacs not found. Skipping Minisat verification."
fi

# Run SAT solvers if the files are in the output directory
if [ -f "${OUTPUT_DIR}/compTH.opb" ]; then
    echo "Running Minisat+ verification..."
    /home/asahruri/work/threABC/bin/minisat+ "${OUTPUT_DIR}/compTH.opb"
fi

if [ -f "${OUTPUT_DIR}/compTH.dimacs" ]; then
    echo "Running Minisat verification..."
    /home/asahruri/work/threABC/bin/minisat "${OUTPUT_DIR}/compTH.dimacs"
fi

echo "Verification completed."

