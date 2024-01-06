#!/usr/bin/env python3
class Office:
    def __init__(self, name, location, sales):
        self.name = name
        self.location = location
        self.sales = sales

office = Office("Office A", "Portland, Oregon", 7)

print("Office Object Properties:")
print("\n")
print(f"Name: {office.name}")
print(f"Location: {office.location}")
print(f"Sales: {office.sales}")
