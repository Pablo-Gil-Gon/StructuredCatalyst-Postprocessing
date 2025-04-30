#!/bin/bash

# This script gets the latest result of the steady simulation for the 
# fluid and places it as initial conditions for the multiregion case

# Receive the desired fields to update as inputs
#----------------------------------------------------------
# 1st input: Calculated steady file
inpField=$1
# 2nd input: File to update
modelField=$2

echo "Updating initial condition for field $modelField"

# Find latest result in case folder:
#----------------------------------------------------------
# Directory to search (current):
directory="MomentumSolution"

# Find the largest numeric folder name
largest_number=-1
largest_folder=""

for folder in "$directory"/*; do
  if [[ -d "$folder" ]]; then
    # Extract the base name and check if it's a number
    folder_name=$(basename "$folder")
    if [[ "$folder_name" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
      # Compare numbers
      if (( $(echo "$folder_name > $largest_number" | bc -l) )); then
        largest_number=$folder_name
        largest_folder=$folder
      fi
    fi
  fi
done

if [[ -n "$largest_folder" ]]; then
  echo "Momentum solution result: $largest_folder"
else
  echo "Failed steady simulation."
fi

# Copy the results in 0 folder of the main case
#----------------------------------------------------------
if [[ -n "$largest_folder" ]]; then
    TARGET_STR="internalField"
    input_file="$largest_folder/$inpField"
    reference_file="$directory/modelInitialConditions/$modelField"
    output_file="0/FluidRegion/$modelField"
    #output_file="0/$modelField"

    # Find the first line in the input file with the target content:
    startline=$(grep -n "$TARGET_STR" "$input_file" | head -n 1 | cut -d: -f1)

    # Find the first non-empty line after the startline
    nextline=$(awk -v start="$startline" 'NR > start && NF { print; exit }' $input_file)
    echo "Number of points: $nextline"

    endline=$(expr $startline + 2 + $nextline + 2)

    # Locate line in the reference file where i want to place the extracted lines:
    targetOutputLine=$(grep -n "$TARGET_STR" "$reference_file" | head -n 1 | cut -d: -f1)

    # Paste the header and the rest of the lines up to the initial internalField 
    # from the main case initial file to the temporary file:
    temp_file=$(mktemp)
    sed -n "1,$(expr $targetOutputLine - 1)p" "$reference_file" > "$temp_file"

    # Paste the lines with the new initial condition in the temporary file:
    sed -n "${startline},${endline}p" "$input_file" >> "$temp_file"

    # Paste the rest of the lines from the reference file:
    sed -n "$(expr $targetOutputLine + 1),\$p" "$reference_file" >> "$temp_file"

    # Replace the initial condition file with the temp file:
    cp -rf "$temp_file" "$output_file"

    # Clean up temporary files
    rm -f "$temp_file"

fi