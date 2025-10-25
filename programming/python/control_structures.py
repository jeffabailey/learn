#!/usr/bin/env python3
"""
Control Structures in Python

This module demonstrates Python's control structures that let you control
the flow of your program:

1. for loops - Repeat code for each item in a collection
2. while loops - Repeat code while a condition is True
3. if-elif-else statements - Make decisions in your code

Control structures are fundamental to programming - they let you write
code that makes decisions and repeats tasks automatically.

Run this file with: python control_structures.py
"""

# ========== FOR LOOP ==========
# A for loop iterates (goes through) each item in a list
offices = ["Office A", "Office B", "Office C"]

# 'for office in offices' means: "for each item in the offices list,
# temporarily call it 'office' and run the indented code below"
for office in offices:
  print(office)  # This will print each office name, one per line

print()  # Empty line for spacing

# ========== WHILE LOOP ==========
# A while loop repeats as long as a condition is True
offices = ['Office A', 'Office B', 'Office C']

# This loop continues while the offices list is not empty
# In Python, an empty list is considered False, a non-empty list is True
while offices:
  # pop(-1) removes and returns the last item from the list
  # The list gets shorter each time, until it's empty and the loop stops
  print(offices.pop(-1))

print()  # Empty line for spacing

# ========== IF-ELIF-ELSE STATEMENT ==========
# These statements let your program make decisions based on conditions
office_a_sales = 3
office_b_sales = 100

# 'if' checks the first condition
if office_b_sales > office_a_sales:
  print("Office B sales are greater than Office A sales")
# 'elif' (else-if) checks another condition if the first was False
elif office_a_sales > office_b_sales:
  print("Office A sales are greater than Office B sales")
# You can add 'else' to run code if none of the conditions are True
# (Not used here because we're only interested in one being greater than the other)

