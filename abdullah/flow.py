#!/usr/bin/env python3

import sys
import subprocess
import os

ABC_PATH = "/home/asahruri/work/threABC/bin/abc"
MINISAT_PATH = "/home/asahruri/work/threABC/bin/minisat"
MINISAT_PLUS_PATH = "/home/asahruri/work/threABC/bin/minisat+"

def run_abc_commands(commands, abc_binary=ABC_PATH, output_dir="."):
    try:
        process = subprocess.Popen(abc_binary, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate("\n".join(commands) + "\n")
        
        if process.returncode != 0:
            print("Error executing ABC commands:")
            print(stderr)
            sys.exit(1)
        else:
            print(stdout)
    except FileNotFoundError:
        print(f"Error: {abc_binary} not found.")
        sys.exit(1)

def run_minisat_command(command, minisat_path):
    try:
        command_list = command.split()  # Split the command into a list
        command_list[0] = minisat_path  # Replace the first item with the path to the binary

        # Check if the input file exists
        input_file = command_list[1]  # Assuming the input file is the second item in the list
        if not os.path.exists(input_file):
            print(f"Error: The input file {input_file} does not exist.")
            sys.exit(1)

        # Print the command for debugging
        print(f"Running command: {' '.join(command_list)}")

        process = subprocess.run(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        if process.returncode != 0:
            print(f"Error executing {minisat_path} command:")
            print("STDOUT:", process.stdout)
            print("STDERR:", process.stderr)
            sys.exit(1)
        else:
            print(process.stdout)
    except FileNotFoundError:
        print(f"Error: {minisat_path} not found.")
        sys.exit(1)

def create_output_directory(base_name="run"):
    run_number = 1
    while os.path.exists(f"{base_name}_{run_number}"):
        run_number += 1
    output_dir = f"{base_name}_{run_number}"
    os.makedirs(output_dir)
    return output_dir

def main(circuit_path):
    circuit_name = os.path.splitext(os.path.basename(circuit_path))[0]
    circuit_extension = os.path.splitext(circuit_path)[1].lower()
    output_dir = create_output_directory()

    if circuit_extension not in ['.blif', '.bench']:
        print("Error: The script only supports .blif and .bench files.")
        sys.exit(1)

    # AIG Collapse Flow (only for .blif)
    if circuit_extension == '.blif':
        abc_aig_commands = [
            f"r {circuit_path}",
            "aig_syn",
            "mt -B 100",
            "pt",
            "q"
        ]
        print("\nRunning AIG Collapse Flow...")
        run_abc_commands(abc_aig_commands)

    # TLC Collapse Flow
    abc_tlc_commands = [
        f"r {circuit_path}",
        "tl_syn",
        f"wt {os.path.join(output_dir, f'{circuit_name}_before_clp.th')}",
        "mt -B 100",
        "pt",
        f"wt {os.path.join(output_dir, f'{circuit_name}_after_clp.th')}",
        f"tvr {os.path.join(output_dir, f'{circuit_name}_before_clp.th')} {os.path.join(output_dir, f'{circuit_name}_after_clp.th')} > {os.path.join(output_dir, 'compTH.opb')}",
        f"tvr -V 1 {os.path.join(output_dir, f'{circuit_name}_before_clp.th')} {os.path.join(output_dir, f'{circuit_name}_after_clp.th')} > {os.path.join(output_dir, 'compTH.dimacs')}",
        "q"
    ]
    print("\nRunning TLC Collapse Flow...")
    run_abc_commands(abc_tlc_commands)

    # Run MiniSat+ for PB verification
    run_minisat_command(f"{MINISAT_PLUS_PATH} {os.path.join(output_dir, 'compTH.opb')}", MINISAT_PLUS_PATH)

    # Run MiniSat for CNF verification
    run_minisat_command(f"{MINISAT_PATH} {os.path.join(output_dir, 'compTH.dimacs')}", MINISAT_PATH)

    # Verify Equivalence Using TL-to-MUX Translation
    abc_mux_commands = [
        f"rt {os.path.join(output_dir, f'{circuit_name}_before_clp.th')}",
        "t2m",
        f"w {os.path.join(output_dir, f'{circuit_name}_before_clp.aig')}",
        f"rt {os.path.join(output_dir, f'{circuit_name}_after_clp.th')}",
        "t2m",
        f"w {os.path.join(output_dir, f'{circuit_name}_after_clp.aig')}",
        f"cec {os.path.join(output_dir, f'{circuit_name}_before_clp.aig')} {os.path.join(output_dir, f'{circuit_name}_after_clp.aig')}",
        "q"
    ]
    print("\nVerifying Equivalence Using TL-to-MUX Translation...")
    run_abc_commands(abc_mux_commands)

    # Check Output Satisfiability Using PB-Based Method with PG Encoding
    abc_pg_commands = [
        f"r {circuit_path}",
        "pg_and",
        "q"
    ]
    print("\nChecking Output Satisfiability Using PB-Based Method with PG Encoding...")
    run_abc_commands(abc_pg_commands)
    run_minisat_command(f"{MINISAT_PLUS_PATH} {os.path.join(output_dir, 'no_pg.opb')}", MINISAT_PLUS_PATH)
    run_minisat_command(f"{MINISAT_PLUS_PATH} {os.path.join(output_dir, 'pg.opb')}", MINISAT_PLUS_PATH)

    print(f"All output files have been saved to {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_flow.py <path_to_circuit>")
        sys.exit(1)

    circuit_path = sys.argv[1]
    main(circuit_path)

