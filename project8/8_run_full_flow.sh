#!/bin/bash

# Paths to tools
ABC_BINARY="/home/asahruri/work/threABC/bin/abc"
MINISAT_BINARY="/home/asahruri/work/threABC/bin/minisat"
MINISAT_PLUS_BINARY="/home/asahruri/work/threABC/bin/minisat+"
LOCKING_SCRIPT="2_add_logic_locking.py"  # Path to your logic locking Python script
FORMATTING_SCRIPT="7_run_format_circuit.py"  # Path to your formatting Python script

# Define the range of NUM_KEYS values to sweep
NUM_KEYS_VALUES=(2 4 8 16)  # Adjust this array as needed for different key values

# Loop through each benchmark directory in benchmarks/
for BENCHMARK_FOLDER in benchmarks/*; do
    # Check if the directory exists and contains .blif or .bench files
    if [[ -d "$BENCHMARK_FOLDER" && ($(ls -A $BENCHMARK_FOLDER/*.blif 2>/dev/null || ls -A $BENCHMARK_FOLDER/*.bench 2>/dev/null)) ]]; then
        # Get benchmark folder name
        BENCHMARK_NAME=$(basename $BENCHMARK_FOLDER)

        # Loop through each NUM_KEYS value
        for NUM_KEYS in "${NUM_KEYS_VALUES[@]}"; do
            # Generate output CSV filename and output folder name
            OUTPUT_CSV="sat_out_${BENCHMARK_NAME}_${NUM_KEYS}.csv"
            RUN_FOLDER="${BENCHMARK_NAME}_${NUM_KEYS}_runs"

            # Create a main folder for all run directories if it doesn't exist
            mkdir -p $RUN_FOLDER

            # CSV header
            echo "Circuit,Conflicts,Decisions,CPU Time,Result" > $OUTPUT_CSV

            # Loop through each .blif and .bench file in the current benchmark directory
            for circuit_path in $BENCHMARK_FOLDER/*.{blif,bench}; do
                # Check if the file exists (skip if there are no matching files)
                [[ -e $circuit_path ]] || continue

                # Extract circuit name
                circuit_name=$(basename $circuit_path .blif)
                circuit_name=$(basename $circuit_name .bench)
                run_dir="run_${circuit_name}_${NUM_KEYS}"

                # Create a run directory if it doesn't exist
                mkdir -p $run_dir

                # Run ABC synthesis flow and generate .th files
                echo "Running ABC synthesis flow for $circuit_name with NUM_KEYS=$NUM_KEYS..."
                $ABC_BINARY -c "
                    r $circuit_path;
                    tl_syn;
                    wt ${run_dir}/${circuit_name}_before_clp.th;
                    mt -B 100;
                    pt;
                    wt ${run_dir}/${circuit_name}_after_clp.th;
                    q;
                "

                # Check if .th files were created
                if [[ ! -f ${run_dir}/${circuit_name}_before_clp.th || ! -f ${run_dir}/${circuit_name}_after_clp.th ]]; then
                    echo "Error: .th files not found for $circuit_name. Skipping to next circuit."
                    rm -rf $run_dir  # Delete the run directory if processing fails
                    continue
                fi

                # Run the logic locking script
                echo "Running logic locking for $circuit_name with NUM_KEYS=$NUM_KEYS..."
                python3 $LOCKING_SCRIPT ${run_dir}/${circuit_name}_after_clp.th $NUM_KEYS

                # Run the formatting script on the after_clp and after_clp_locked .th files
                echo "Formatting .th files for $circuit_name..."
                python3 $FORMATTING_SCRIPT ${run_dir}/${circuit_name}_after_clp.th
                python3 $FORMATTING_SCRIPT ${run_dir}/${circuit_name}_after_clp_locked.th

                # Run verification using abc with formatted .th files
                echo "Running ABC verification for $circuit_name with NUM_KEYS=$NUM_KEYS..."
                $ABC_BINARY -c "
                    tvr ${run_dir}/${circuit_name}_after_clp_formatted.th ${run_dir}/${circuit_name}_after_clp_locked_formatted.th;
                    tvr -V 1 ${run_dir}/${circuit_name}_after_clp_formatted.th ${run_dir}/${circuit_name}_after_clp_locked_formatted.th;
                    q;
                "

                # Move generated compTH files into the run directory if they exist
                if [[ -f compTH.opb ]]; then
                    mv compTH.opb ${run_dir}/
                fi
                if [[ -f compTH.dimacs ]]; then
                    mv compTH.dimacs ${run_dir}/
                fi

                # Run external SAT solvers and capture the output
                echo "Verifying with Minisat and Minisat+ for $circuit_name..."
                for solver_output in "${run_dir}/compTH.opb" "${run_dir}/compTH.dimacs"; do
                    if [[ -f $solver_output ]]; then
                        if [[ $solver_output == *.opb ]]; then
                            $MINISAT_PLUS_BINARY $solver_output > ${solver_output}_output.txt
                            output_file="${solver_output}_output.txt"
                        else
                            $MINISAT_BINARY $solver_output > ${solver_output}_output.txt
                            output_file="${solver_output}_output.txt"
                        fi

                        # Parse output and append to CSV
                        if [[ -f $output_file ]]; then
                            conflicts=$(grep -oP 'conflicts\s*:\s*\K\d+' $output_file || echo "N/A")
                            decisions=$(grep -oP 'decisions\s*:\s*\K\d+' $output_file || echo "N/A")
                            cpu_time=$(grep -oP 'CPU time\s*:\s*\K[\d.]+' $output_file || echo "N/A")
                            result=$(grep -q 'UNSATISFIABLE' $output_file && echo "UNSATISFIABLE" || (grep -q 'SATISFIABLE' $output_file && echo "SATISFIABLE" || echo "UNKNOWN"))

                            echo "$circuit_name,$conflicts,$decisions,$cpu_time,$result" >> $OUTPUT_CSV
                        fi
                    else
                        echo "Warning: $solver_output not found. Skipping verification."
                    fi
                done

                # Delete compTH files to save space
                rm -f ${run_dir}/compTH.opb ${run_dir}/compTH.dimacs ${run_dir}/*.txt

                # Move the run directory into the main run folder
                mv $run_dir $RUN_FOLDER/

                # Delete the run directory after moving it
                rm -rf $RUN_FOLDER/$run_dir

                echo "Verification completed for $circuit_name with NUM_KEYS=$NUM_KEYS."
            done

            echo "All circuits in $BENCHMARK_NAME processed with NUM_KEYS=$NUM_KEYS. Results stored in $OUTPUT_CSV."
        done
    else
        echo "No .blif or .bench files found in $BENCHMARK_FOLDER. Skipping."
    fi
done

echo "All benchmark directories processed for all NUM_KEYS."

