#!/usr/bin/env python3

import sys

def read_th_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def find_highest_node(lines):
    highest_node = 0
    for line in lines:
        if line.startswith(".threshold") or line.startswith(".input") or line.startswith(".output"):
            parts = line.split()
            for part in parts[1:]:
                if part.isdigit():
                    highest_node = max(highest_node, int(part))
    return highest_node

def lock_tlg(lines, highest_node, num_keys):
    modified_lines = []
    key_count = 0
    inputs_declared = False

    for line in lines:
        if line.startswith(".input") and not inputs_declared:
            # Add key inputs to the input declaration line
            key_inputs = [str(highest_node + i + 1) for i in range(num_keys)]
            modified_lines.append(line.strip() + " " + " ".join(key_inputs) + "\n")
            inputs_declared = True
        elif line.startswith(".threshold"):
            # Modify gate definitions to include key inputs
            parts = line.split()
            if len(parts) > 2:
                # Add key input nodes before the output node
                for i in range(num_keys):
                    key_input = str(highest_node + key_count + 1)
                    parts.insert(-1, key_input)
                    key_count += 1
                modified_lines.append(" ".join(parts) + "\n")

                # Read the weights and threshold line and append weights for the key inputs
                weights_line = next(lines).strip().split()
                weights = list(map(int, weights_line[:-1]))
                threshold = int(weights_line[-1])

                # Add weights for the key inputs
                weights.extend([1] * num_keys)  # Add weights of 1 for each new key input

                modified_weights_line = " ".join(map(str, weights)) + f" {threshold}\n"
                modified_lines.append(modified_weights_line)
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)

    return modified_lines

def write_th_file(modified_lines, output_path):
    with open(output_path, 'w') as file:
        file.writelines(modified_lines)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python lock_tlg.py <input_file> <number_of_keys>")
        sys.exit(1)

    input_file = sys.argv[1]
    num_keys = int(sys.argv[2])
    output_file = "locked_circuit.th"

    lines = read_th_file(input_file)
    highest_node = find_highest_node(lines)
    modified_lines = lock_tlg(lines, highest_node, num_keys)
    write_th_file(modified_lines, output_file)
    print(f"Locked .th file with {num_keys} keys written to {output_file}")

