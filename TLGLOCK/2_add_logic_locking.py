#!/usr/bin/env python3

import sys
import os
import random

def add_logic_locking(th_file, num_keys=4):
    if not os.path.exists(th_file):
        print(f"Error: {th_file} not found.")
        sys.exit(1)

    locked_th_file = th_file.replace('.th', '_locked.th')
    key_vectors = {}
    all_nodes = set()
    key_nodes = set()  # Collect key nodes for adding to .input line

    # Variables to store header lines
    model_line = ""
    input_line = ""
    output_line = ""

    # First pass to find the highest node in the circuit and collect header info
    with open(th_file, 'r') as infile:
        for line in infile:
            if line.startswith(".model"):
                model_line = line.strip()
            elif line.startswith(".input"):
                input_line = line.strip()
                all_nodes.update(int(node) for node in input_line.split()[1:] if node.isdigit())
            elif line.startswith(".output"):
                output_line = line.strip()
            elif line.startswith(".threshold"):
                tokens = line.strip().split()
                all_nodes.update(int(node) for node in tokens[1:] if node.isdigit())
            else:
                # Update set with other numeric nodes in the file
                tokens = line.strip().split()
                all_nodes.update(int(token) for token in tokens if token.isdigit())

    max_node = max(all_nodes)

    # Store original input nodes for later use
    original_input_nodes = input_line.split()[1:]

    with open(th_file, 'r') as infile, open(locked_th_file, 'w') as outfile:
        # Write the initial custom header line
        outfile.write("Threshold logic gate list written by NZ\n")

        # Write the header lines in order: .model, .input, .output
        if model_line:
            outfile.write(model_line + '\n')
        if input_line:
            outfile.write(input_line + '\n')
        if output_line:
            outfile.write(output_line + '\n')

        for line in infile:
            if line.startswith(".input") or line.startswith(".output") or line.startswith(".model"):
                continue  # Skip header lines that have already been written
            elif line.startswith(".threshold"):
                # Process .threshold lines
                tokens = line.strip().split()
                input_nodes = tokens[1:-1]  # Extract input nodes (all except the last token)
                output_node = tokens[-1]  # The last token is the output node

                # Remove duplicate output nodes from the input list
                input_nodes = [node for node in input_nodes if node != output_node]

                # Write the modified .threshold line with new key nodes added
                for i in range(num_keys):
                    key_node = max_node + i + 1
                    if key_node not in input_nodes:
                        input_nodes.append(str(key_node))
                        all_nodes.add(key_node)
                        key_nodes.add(key_node)

                # Update the maximum node number
                max_node += num_keys

                outfile.write(f"{tokens[0]} {' '.join(input_nodes)} {output_node}\n")

                # Read the second line (weights and threshold)
                weights_line = infile.readline().strip().split()
                weights = [int(w) for w in weights_line[:-1]]  # All but the last are weights
                threshold = int(weights_line[-1])  # The last is the threshold

                # Generate random weights for key inputs
                key_weights = []
                W_sum = sum(weights)
                if abs(W_sum) < 1:
                    W_sum = 10  # Default value to ensure a valid range
                for _ in range(num_keys):
                    lower_bound = -max(1, abs(W_sum) // 2)
                    upper_bound = max(1, abs(W_sum) // 2)
                    key_weight = random.randint(lower_bound, upper_bound)
                    while key_weight == 0:
                        key_weight = random.randint(lower_bound, upper_bound)
                    key_weights.append(key_weight)

                weights.extend(key_weights)
                key_vector = [random.randint(0, 1) for _ in range(num_keys)]
                key_vectors[output_node] = key_vector

                # Write the modified weights and threshold line
                outfile.write(' '.join(map(str, weights)) + f" {threshold}\n")
            else:
                outfile.write(line)

        # Create a new .input line with all key nodes included at the end of the file
        all_input_nodes = sorted(set(original_input_nodes + list(key_nodes)), key=int)
        outfile.write("\n.input " + " ".join(map(str, all_input_nodes)) + "\n")

    # Print the vector of keys and node numbers
    print(f"Logic locking applied. Locked .th file generated: {locked_th_file}")
    print("Node numbers of the key inputs added:")
    print(", ".join(map(str, key_nodes)))
    print("Key vectors required to unlock the circuit:")
    for output_node, key_vector in key_vectors.items():
        print(f"Output {output_node}: {key_vector}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 2_add_logic_locking.py <path_to_th_file> [num_keys]")
        sys.exit(1)

    th_file = sys.argv[1]
    num_keys = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    add_logic_locking(th_file, num_keys)

