#!/usr/bin/env python3
"""
Lambda Functions in Python

This module demonstrates lambda functions - small anonymous (unnamed) functions.

Lambda functions are useful for simple operations that you need to use just once,
especially with functions like max(), min(), sorted(), etc.

Think of lambda as a shortcut for writing a simple function. Instead of:
    def get_sales(x):
        return x['sales']

You can write:
    lambda x: x['sales']

Run this file with: python lambdas.py
"""

# Create a list of dictionaries (each dictionary represents an office)
# A dictionary is a collection of key-value pairs (like name: "Office A")
offices = [{'name': 'Office A', 'sales': 7},
          {'name': 'Office B', 'sales': 3},
          {'name': 'Office C', 'sales': 9}]

# ========== FINDING MAXIMUM ==========
print("Get the office with the highest amount of sales")
# max() finds the largest item in a list
# The 'key' parameter tells max() how to compare items
# 'lambda x: x['sales']' means: "for each office (x), look at its 'sales' value"
highest_sales_office = max(offices, key=lambda x: x['sales'])
print(highest_sales_office)  # Will output: {'name': 'Office C', 'sales': 9}
print("\n")

# ========== FINDING MINIMUM ==========
print("Get the office with the least amount of sales")
# min() finds the smallest item in a list
# The lambda function extracts the 'sales' value for comparison
# This will find the office with the lowest sales number
lowest_sales_office = min(offices, key=lambda x: x['sales'])
print(lowest_sales_office)  # Will output: {'name': 'Office B', 'sales': 3}
