#!/usr/bin/env python3

import sys
import os

def add_logic_locking(th_file, num_keys=4):
    if not os.path.exists(th_file):
        print(f"Error: {th_file} not found.")
        sys.exit(1)

    locked_th_file = th_file.replace('.th', '_locked.th')
    with open(th_file, 'r') as infile, open(locked_th_file, 'w') as outfile:
        for line in infile:
            if line.startswith(".threshold"):
                # Add key logic after reading a threshold line
                tokens = line.split()
                max_node = max([int(x) for x in tokens if x.isdigit()])
                for i in range(num_keys):
                    key_node = max_node + i + 1
                    tokens.append(str(key_node))
                    tokens.append('1')  # Assign a weight for the key
                tokens.append(str(int(tokens[-1]) + 1))  # Adjust threshold
                outfile.write(' '.join(tokens) + '\n')
            else:
                outfile.write(line)

    print(f"Logic locking applied. Locked .th file generated: {locked_th_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_logic_locking.py <path_to_th_file> [num_keys]")
        sys.exit(1)

    th_file = sys.argv[1]
    num_keys = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    add_logic_locking(th_file, num_keys)

