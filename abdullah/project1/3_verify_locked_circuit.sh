#!/bin/bash

# Check if input folder is provided
if [ -z "$1" ]; then
    echo "Usage: ./verify_locked_circuit.sh <output_dir>"
    exit 1
fi

OUTPUT_DIR=$1

# Verify using ABC
/home/asahruri/work/threABC/bin/abc << EOF
rt $OUTPUT_DIR/$(basename $OUTPUT_DIR)_before_clp.th
t2m
w $OUTPUT_DIR/$(basename $OUTPUT_DIR)_before_clp.aig
rt $OUTPUT_DIR/$(basename $OUTPUT_DIR)_after_clp_locked.th
t2m
w $OUTPUT_DIR/$(basename $OUTPUT_DIR)_after_clp_locked.aig
cec $OUTPUT_DIR/$(basename $OUTPUT_DIR)_before_clp.aig $OUTPUT_DIR/$(basename $OUTPUT_DIR)_after_clp_locked.aig
q
EOF

# Verify using MiniSat+
/home/asahruri/work/threABC/bin/minisat+ $OUTPUT_DIR/compTH.opb

# Verify using MiniSat
/home/asahruri/work/threABC/bin/minisat $OUTPUT_DIR/compTH.dimacs

echo "Verification process completed."

