#!/usr/bin/env python
"""
Exception Handling in Python

This module demonstrates how to handle errors (exceptions) in Python.

When something goes wrong in your program (like trying to open a file that
doesn't exist), Python "raises an exception". Without proper handling, this
stops your program. Exception handling lets you catch these errors and
respond gracefully.

Key concepts:
- try: Code that might cause an error
- except: Code to run if an error occurs
- Prevents your program from crashing

Run this file with: python exception_handling.py
"""


def read_file(file_name):
    """
    Attempt to open and return a file handle.

    This function demonstrates exception handling by trying to open a file.
    If the file doesn't exist, instead of crashing, it catches the error
    and prints a user-friendly message.

    Parameters:
        file_name (str): The name of the file to open
                        Example: "example.csv"

    Returns:
        file object or None: The opened file if successful, None if file doesn't exist

    Example:
        >>> file_handle = read_file("example.csv")
        >>> if file_handle:
        ...     print("File opened successfully!")
        ... else:
        ...     print("File could not be opened")
    """
    csv_file = None  # Initialize to None (represents "no value")

    try:
        # Try to open the file - this might raise an IOError
        csv_file = open(file_name, "r")
    except IOError:
        # If an IOError occurs (file doesn't exist), this block runs
        # Instead of crashing, we print a helpful message
        print("Error: File does not exist.")

    # Return the file object (or None if there was an error)
    return csv_file


# Try to open a file that doesn't exist
# This will trigger the exception handling in read_file()
result_file = read_file("example_missing.csv")
# You should see: "Error: File does not exist." printed to the console
