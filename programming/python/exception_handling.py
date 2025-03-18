#!/usr/bin/env python
def read_file(file_name):
    example_csv = None
    try:
        example_csv = open(file_name, "r")
    except IOError:
        print("Error: File does not exist.")
    return example_csv

example_csv = read_file("example_missing.csv")
