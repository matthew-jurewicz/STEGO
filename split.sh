#!/bin/bash

# Set the source directory and target directories
src_dir="geotiff_tiles"
train_dir="geotiff_tiles/imgs/train"
val_dir="geotiff_tiles/imgs/val"

# Create the target directories if they do not exist
mkdir -p "${train_dir}"
mkdir -p "${val_dir}"

# Calculate the number of files in the source directory
num_files=$(find "${src_dir}" -type f | wc -l)

# Calculate the index at which to split the files (75% for training, 25% for validation)
split_index=$(echo "0.75 * ${num_files}" | bc -l | awk '{print int($1+0.5)}')

# Loop through the files in the source directory and move them to the appropriate target directories
counter=0
for file in "${src_dir}"/*; do
  if [ $counter -lt $split_index ]; then
    mv "${file}" "${train_dir}"
  else
    mv "${file}" "${val_dir}"
  fi
  counter=$((counter+1))
done
