#!/bin/bash

# Check if input file is provided
if [ -z "$1" ]; then
    echo "Usage: ./run_abc_flow.sh <path_to_circuit>"
    exit 1
fi

INPUT_CIRCUIT=$1
OUTPUT_DIR="run_abc"
mkdir -p $OUTPUT_DIR

# Run ABC commands
/home/asahruri/work/threABC/bin/abc << EOF
r $INPUT_CIRCUIT
tl_syn
wt $OUTPUT_DIR/$(basename $INPUT_CIRCUIT .blif)_before_clp.th
mt -B 100
pt
wt $OUTPUT_DIR/$(basename $INPUT_CIRCUIT .blif)_after_clp.th
tvr $OUTPUT_DIR/$(basename $INPUT_CIRCUIT .blif)_before_clp.th $OUTPUT_DIR/$(basename $INPUT_CIRCUIT .blif)_after_clp.th > $OUTPUT_DIR/compTH.opb
tvr -V 1 $OUTPUT_DIR/$(basename $INPUT_CIRCUIT .blif)_before_clp.th $OUTPUT_DIR/$(basename $INPUT_CIRCUIT .blif)_after_clp.th > $OUTPUT_DIR/compTH.dimacs
q
EOF

echo "ABC synthesis and file generation completed."

