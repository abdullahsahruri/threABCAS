#!/usr/bin/env python3

import sys
import os

def format_th_file(th_file):
    if not os.path.exists(th_file):
        print(f"Error: {th_file} not found.")
        sys.exit(1)

    formatted_th_file = th_file.replace('.th', '_formatted.th')

    # Initialize storage for different sections
    header = "Threshold logic gate list written by NZ"
    model_line = ""
    input_line = ""
    output_line = ""
    threshold_lines = []

    # Process the file and categorize lines
    with open(th_file, 'r') as infile:
        for line in infile:
            stripped_line = line.strip()
            if stripped_line.startswith(".model"):
                model_line = stripped_line
            elif stripped_line.startswith(".input"):
                input_line = stripped_line
            elif stripped_line.startswith(".output"):
                output_line = stripped_line
            elif stripped_line.startswith(".threshold"):
                # Append .threshold lines as-is to the threshold_lines list
                threshold_lines.append(stripped_line)
                # The following line contains weights and threshold, so read and add it too
                weights_line = next(infile).strip()
                threshold_lines.append(weights_line)

    # Write the formatted content to a new file
    with open(formatted_th_file, 'w') as outfile:
        outfile.write(header + '\n')
        outfile.write(model_line + '\n')
        outfile.write(input_line + '\n')
        outfile.write(output_line + '\n')
        outfile.write("\n".join(threshold_lines) + '\n')

    print(f"Formatted .th file created: {formatted_th_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python format_th_file.py <path_to_th_file>")
        sys.exit(1)

    th_file = sys.argv[1]
    format_th_file(th_file)

