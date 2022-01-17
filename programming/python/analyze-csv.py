#!/usr/bin/env python3
import pandas as pd
filename = "example.csv"
chunksize = 3
for chunk in pd.read_csv(filename, chunksize=chunksize):
    print(chunk)