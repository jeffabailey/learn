#!/usr/bin/env python3
"""
Arrays (Lists) in Python

This module demonstrates how to work with lists in Python.
In Python, we call them "lists" but they're similar to arrays in other languages.

Lists are ordered collections that can hold multiple items. They're one of the
most useful data structures in Python.

Topics covered:
- Creating lists
- Accessing items by index
- Modifying list items
- Getting list length
- Sorting and iterating
- Adding and removing items

Run this file with: python arrays.py
"""

# Create a list of office names
# Lists are created using square brackets []
offices = ["Office A", "Office B", "Office C"]

print(f"We have an office array: {offices}")
print("\n")

# ========== ACCESSING ITEMS ==========
print("Accessing array item 0")
# Lists use zero-based indexing (first item is at index 0)
first_office = offices[0]
print(f"Found {first_office}")  # Will output: Office A
print("\n")

# ========== UPDATING ITEMS ==========
print("Update an array value")
# Change the value at index 0
offices[0] = "Office Z"
print(f"Updated Office A to {offices[0]}")  # Will output: Office Z
print("\n")

# ========== GETTING LENGTH ==========
print("Get the length of an array")
# len() returns how many items are in the list
office_count = len(offices)
print(f"{office_count} offices exist in the array")  # Will output: 3
print("\n")

# ========== SORTING AND LOOPING ==========
print("Loop a sorted array")
# sorted() returns a sorted copy of the list (doesn't modify original)
# The for loop goes through each item in the sorted list
for office_name in sorted(offices):
 print(office_name)  # Prints each office name in alphabetical order
print("\n")

# ========== ADDING ITEMS ==========
print("Add an array element named Office Y")
# append() adds an item to the end of the list
offices.append("Office Y")
print(offices)  # The list now has 4 items
print("\n")

# ========== REMOVING ITEMS ==========
print("Remove an array element")
# pop(index) removes and returns the item at the specified index
# pop(1) removes the second item (index 1)
offices.pop(1)
print(offices)
print("\n")

print("Delete an array element")
# remove() deletes the first occurrence of a specific value
# This searches for "Office C" and removes it
offices.remove("Office C")
print(offices)
print("\n")
