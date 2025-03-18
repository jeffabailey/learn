#!/usr/bin/env python3
import pandas as pd
import os

filename = "example.csv"

if not os.path.exists(filename):
    print(f"Error: {filename} not found")
    exit(1)

print(f"Chunking records for {filename}")
print("\n")
chunksize = 3
for chunk in pd.read_csv(filename, sep='|', chunksize=chunksize):
    print(chunk)