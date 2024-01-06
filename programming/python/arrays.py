#!/usr/bin/env python3
offices = ["Office A","Office B", "Office C"]

print(f"We have an office array: {offices}")
print("\n")

print("Accessing array item 0")
x = offices
print(f"Found {x}")
print("\n")

print("Update an array value")
offices[0] = "Office Z"
print(f"Updated Office A to {offices[0]}")
print("\n")

print("Get the length of an array")
x = len(offices)
print(f"{x} offices exist in the array")

print("\n")
print("Loop a sorted array")
for x in sorted(offices):
 print(x)
print("\n")

print("Add an array element named Office Y")
offices.append("Office Y")
print(offices)
print("\n")

print("Remove an array element")
offices.pop(1)
print(offices)
print("\n")

print("Delete an array element")
offices.remove("Office C")
print(offices)
print("\n")
