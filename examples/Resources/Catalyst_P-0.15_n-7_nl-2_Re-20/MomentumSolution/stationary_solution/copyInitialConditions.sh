#!/bin/bash

# This script gets the latest result of the steady simulation for the 
# fluid and places it as initial conditions for the multiregion case

# Receive the desired fields to update as inputs
#----------------------------------------------------------
# 1st input: Calculated steady file
inpField=$1
# 2nd input: File to update
modelField=$2

echo "Copying initial conditions from stationary case"

# Find latest result in case folder:
#----------------------------------------------------------
# Directory to search (current):
directory="."

# Find the largest numeric folder name
largest_number=-1
largest_folder=""

for folder in "$directory"/*; do
  if [[ -d "$folder" ]]; then
    # Extract the base name and check if it's a number
    folder_name=$(basename "$folder")
    if [[ "$folder_name" =~ ^[0-9]+$ ]]; then
      # Compare numbers
      if (( folder_name > largest_number )); then
        largest_number=$folder_name
        largest_folder=$folder
      fi
    fi
  fi
done

if [[ -n "$largest_folder" ]]; then
  echo "Steady solution result: $largest_folder"
else
  echo "Failed steady simulation."
fi

# Copy the results in 0 folder of the momentum case
#----------------------------------------------------------
if [[ -n "$largest_folder" ]]; then
    # Pimplefoam uses p/rho just as the output of the 
    # stationary case, we can just paste the files:
    cp -rf "$largest_folder/U" "../0/"
    cp -rf "$largest_folder/p" "../0/"
fi