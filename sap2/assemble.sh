#!/bin/bash

# # Check if correct number of arguments is passed
# if [ "$#" -ne 4 ] || [ "$1" != "--path" ] || [ "$3" != "--output" ]; then
#     echo "Usage: $0 --path <input_file> --output <output_file>"
# fi

# Assign input arguments
INPUT_FILE="$2"
OUTPUT_FILE="$4"

# Run Python script with hardcoded instruction set map
python3 -m assembler.assembler --path "$INPUT_FILE" --output "$OUTPUT_FILE" --instruction_set_map "instruction_set_map.txt"
