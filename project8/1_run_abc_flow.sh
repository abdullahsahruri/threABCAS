#!/bin/bash

# Check if the benchmark file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_benchmark_file>"
    exit 1
fi

BENCHMARK_PATH="$1"
BENCHMARK_NAME=$(basename "$BENCHMARK_PATH" .blif)

# Create a unique run directory
RUN_DIR="run_$BENCHMARK_NAME"
mkdir -p "$RUN_DIR"

echo "Running ABC synthesis flow for $BENCHMARK_PATH..."

# Run ABC commands
/home/asahruri/work/threABC/bin/abc <<EOF
source abc.rc;
r $BENCHMARK_PATH;
tl_syn;
wt $RUN_DIR/${BENCHMARK_NAME}_before_clp.th;
mt -B 100;
pt;
wt $RUN_DIR/${BENCHMARK_NAME}_after_clp.th;
tvr $RUN_DIR/${BENCHMARK_NAME}_before_clp.th $RUN_DIR/${BENCHMARK_NAME}_after_clp.th > $RUN_DIR/compTH.opb;
tvr -V 1 $RUN_DIR/${BENCHMARK_NAME}_before_clp.th $RUN_DIR/${BENCHMARK_NAME}_after_clp.th > $RUN_DIR/compTH.dimacs;
q;
EOF

# Verify that the .th files were generated
if [ ! -f "$RUN_DIR/${BENCHMARK_NAME}_before_clp.th" ]; then
    echo "Error: $RUN_DIR/${BENCHMARK_NAME}_before_clp.th not found. ABC synthesis may have failed."
    exit 1
fi

if [ ! -f "$RUN_DIR/${BENCHMARK_NAME}_after_clp.th" ]; then
    echo "Error: $RUN_DIR/${BENCHMARK_NAME}_after_clp.th not found. ABC synthesis may have failed."
    exit 1
fi

# Verify that compTH files were generated
if [ ! -f "$RUN_DIR/compTH.opb" ] || [ ! -f "$RUN_DIR/compTH.dimacs" ]; then
    echo "Warning: One or both compTH files were not generated in $RUN_DIR."
    exit 1
fi

echo "ABC synthesis and file generation completed successfully. Output saved in $RUN_DIR."

