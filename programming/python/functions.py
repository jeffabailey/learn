#!/usr/bin/env python3
"""
Functions in Python

This module demonstrates how to create and use functions in Python.
Functions are reusable blocks of code that perform a specific task.

This example shows:
- How to define a function with the 'def' keyword
- How to accept parameters (inputs) to a function
- How to use try-except-finally for error handling
- How to work with file operations

Run this file with: python functions.py
"""


def file_check(file_name):
    """
    Check if a file exists and print its contents.

    This function attempts to open and read a file. If the file exists,
    it prints the file contents. If the file doesn't exist, it prints
    an error message.

    Parameters:
        file_name (str): The name of the file to check and read.
                        Example: "example.csv"

    Returns:
        None (this function prints output but doesn't return a value)

    Example:
        >>> file_check("example.csv")
        Found file, printing file

        [contents of example.csv]
    """
    try:
        # Try to open the file in read mode ("r")
        example_csv = open(file_name, "r")
        try:
            print("Found file, printing file")
            print("\n")
            # Read the entire file contents and print them
            print(example_csv.read())
        finally:
            # The 'finally' block always runs, even if there's an error
            # It's important to close files when we're done with them
            example_csv.close()
    except IOError:
        # If the file doesn't exist, Python raises an IOError
        # We catch it here and print a user-friendly message
        print('Error: File does not exist.')


# Call the function with the filename "example.csv"
# This executes the code inside the function
file_check("example.csv")
