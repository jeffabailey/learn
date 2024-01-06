#!/usr/bin/env python3
offices = [{'name': 'Office A', 'sales': 7},
          {'name': 'Office B', 'sales': 3},
          {'name': 'Office C', 'sales': 9}]

print("Get the office with the highest amount of sales")
print(max(offices, key=lambda x: x['sales']))
print("\n")

print("Get the office with the least amount of sales")
print(min(offices, key=lambda x: x['sales']))
