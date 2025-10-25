#!/usr/bin/env python3
"""
Comments in Python

This module teaches you how to write comments in Python.

Comments are notes in your code that Python ignores. They're for humans to read,
not for the computer to execute. Good comments explain WHY you're doing something,
not just WHAT you're doing.

Types of comments:
1. Single-line comments: Start with #
2. Multi-line comments: Enclosed in triple quotes (three quote marks in a row)

Run this file with: python comments.py
"""

# This is a single-line comment
# Anything after the # symbol is ignored by Python
# Use these for short explanations or notes
print("There's a comment before this line, trust me.")

"""
This is a multi-line comment (also called a docstring when at the start of a file/function).

You can write multiple lines of text here.
It's useful for longer explanations.

Python will ignore all of this text when running the program.
"""

print("\n")
print("A few comments just happened, honest!")

# BEST PRACTICE TIP:
# - Use comments to explain WHY you wrote code a certain way
# - Don't comment on obvious things (like "x = 5  # set x to 5")
# - Update comments when you update code
# - Write comments as if explaining to a beginner
