#!/bin/bash

# Check if the run folder is provided
if [ -z "$1" ]; then
  echo "Usage: ./3_verify_locked_circuit.sh <run_folder>"
  exit 1
fi

RUN_FOLDER=$1

echo "Verifying the locked circuit using Minisat and Minisat+..."
/home/asahruri/work/threABC/bin/minisat "$RUN_FOLDER/compTH.dimacs"
/home/asahruri/work/threABC/bin/minisat+ "$RUN_FOLDER/compTH.opb"

echo "Verification completed."

