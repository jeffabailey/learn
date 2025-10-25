#!/usr/bin/env python3
"""
Operators in Python

This module demonstrates the different types of operators in Python:

1. Arithmetic Operators - For mathematical calculations (+, -, *, /, %, **, //)
2. Assignment Operators - For assigning and updating values (=, +=, -=, *=, etc.)

Operators are symbols that perform operations on variables and values.
They're the building blocks for doing calculations and manipulating data.

Run this file with: python operators.py
"""


class color:
   """Helper class for adding color formatting to console output."""
   BOLD = '\033[1;37;48m'
   CYAN = '\033[1;36;48m'
   YELLOW = '\033[1;33;48m'
   BOLD_YELLOW = BOLD + YELLOW
   BOLD_CYAN = BOLD + CYAN
   END = '\033[1;37;0m'

print(color.BOLD_CYAN + "Arithmetic Operators" + color.END)
print("\n")

# Addition: adds two numbers together
addition = 1 + 1
print(f"1 + 1 = {addition}")  # Will output: 2
print("\n")

# Subtraction: subtracts the second number from the first
subtraction = 2 - 1
print(f"2 - 1 = {subtraction}")  # Will output: 1
print("\n")

# Multiplication: multiplies two numbers
multiplication = 3 * 3
print(f"3 * 3 = {multiplication}")  # Will output: 9
print("\n")

# Division: divides the first number by the second (always returns a float)
division = 10 / 5
print(f"10 / 5 = {division}")  # Will output: 2.0 (note the decimal)
print("\n")

# Modulus: returns the remainder after division
# Think of it as "what's left over" after dividing
modulus = 6 % 3
print(f"6 % 3 = {modulus} ")  # Will output: 0 (6 divides evenly by 3)
print("\n")

# Exponentiation: raises first number to the power of the second
# 2 ** 3 means "2 to the power of 3" or "2 × 2 × 2"
exponentiation = 2 ** 3
print(f"2 ** 3 = {exponentiation}")  # Will output: 8
print("\n")

print(color.BOLD_YELLOW + "Assignment Operators" + color.END)
print("\n")

# = assigns a value to a variable
equals = 1
print(f"1 = {equals}")

# += adds to the current value
# 'equals += 1' is shorthand for 'equals = equals + 1'
equals += 1
print(f"1 += {equals}")  # Will output: 2 (1 + 1)

# -= subtracts from the current value
minus_equals = 2
minus_equals -= 1  # Same as: minus_equals = minus_equals - 1
print(f"2 -= {minus_equals}")  # Will output: 1

# *= multiplies the current value
multiply_and = 5
multiply_and *= 5  # Same as: multiply_and = multiply_and * 5
print(f"5 *= {multiply_and}")  # Will output: 25

# /= divides the current value
divide_and = 5
divide_and /= 5  # Same as: divide_and = divide_and / 5
print(f"5 /= {divide_and}")  # Will output: 1.0

# %= gets the modulus (remainder) of the current value
modulus_and = 6
modulus_and %= 3  # Same as: modulus_and = modulus_and % 3
print(f"6 %= {modulus_and}")  # Will output: 0

# **= raises current value to a power
exponent_and = 2
exponent_and **= 3  # Same as: exponent_and = exponent_and ** 3
print(f"2 **= {exponent_and}")  # Will output: 8

# //= floor division (divides and rounds down to nearest integer)
y = 7
floor_division = 78125.0
floor_division //= y  # Same as: floor_division = floor_division // y
print(f"78125.0 //= {floor_division}")  # Will output: 11160.0

