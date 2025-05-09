#!/bin/sh

#  Create necessary files
mkdir -p /app/data
mkdir -p /app/data/parquet_data
mkdir -p /app/data/logs

python3 code/generateData.py

# Create the ordinal-based JSON file
ORDINAL=$(echo $HOSTNAME | rev | cut -d'-' -f1 | rev)

# Run your Python application
python3 code/main.py
