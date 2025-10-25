#!/usr/bin/env python3
"""
Variables and Data Types in Python

This module demonstrates how to create and use variables in Python, including:
- String variables (text)
- Integer variables (whole numbers)
- Float variables (decimal numbers)
- Boolean variables (True/False)

When you run this file, it will show examples of each data type with their values
and Python's built-in type() function to see what type each variable is.

Run this file with: python variables.py
"""


class color:
   """Helper class for adding formatting to console output.

   BOLD_UNDERLINE makes text bold and underlined
   END resets formatting back to normal
   """
   BOLD_UNDERLINE = '\033[1m\033[4m'
   END = '\033[0m'

print(color.BOLD_UNDERLINE + 'Assign a string value to a variable' + color.END)
print("\n")
# A string is text enclosed in quotes (either "double" or 'single' quotes work)
office_name = "Office A"
print(office_name)  # This will output: Office A
print("\n")
print("----------------------------------------------")

print(color.BOLD_UNDERLINE + 'Assign a multiple line string value to a variable' + color.END)
print("\n")
# Triple quotes (""" or ''') let you create strings that span multiple lines
office_name = """Office A\n
Office B
"""
print(office_name)  # This will output both lines
print("\n")
print("----------------------------------------------")

print(color.BOLD_UNDERLINE + 'Assign an integer value to a variable' + color.END)
print("\n")
# An integer (int) is a whole number without a decimal point
office_sales = 7
# The type() function tells us what type of data a variable contains
office_sales_type = type(office_sales)
print(f"office_sales is type: {office_sales_type}")  # Will show: <class 'int'>
print("\n")
print("----------------------------------------------")


print(color.BOLD_UNDERLINE + 'Assign a floating point value to a variable' + color.END)
print("\n")
# A float is a number with a decimal point
office_score = 7.5
office_score_type = type(office_score)
print(f"office_score is type: {office_score_type}")  # Will show: <class 'float'>
print("\n")
print("----------------------------------------------")

print(color.BOLD_UNDERLINE + 'Assign a boolean value to a variable' + color.END)
print("\n")
# A boolean (bool) can only be True or False (note: capital T and F are required)
office_is_active = bool(True)
office_is_active_type = type(office_is_active)
print(f"office_is_active is type: {office_is_active_type}")  # Will show: <class 'bool'>
print("\n")
print("----------------------------------------------")

"""
Interesting tidbits

Python employs a concept called name mangling for private variables.
"""
