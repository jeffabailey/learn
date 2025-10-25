#!/usr/bin/env python3
"""
Classes and Objects in Python

This module demonstrates object-oriented programming (OOP) in Python.
Classes are blueprints for creating objects. Objects are instances of classes
that have properties (data) and methods (functions).

Think of a class like a cookie cutter - it defines the shape.
Objects are the actual cookies made from that cutter - each cookie
can have different decorations (properties) but follows the same basic shape.

Run this file with: python classes_and_objects.py
"""


class Office:
    """
    Represents an office location with its properties.

    This class demonstrates the basics of object-oriented programming by
    creating a simple Office object with name, location, and sales properties.

    Attributes:
        name (str): The name of the office (e.g., "Office A")
        location (str): The physical location (e.g., "Portland, Oregon")
        sales (int): The number of sales for this office

    Example:
        >>> office = Office("Office A", "Portland, Oregon", 7)
        >>> print(office.name)
        Office A
    """

    def __init__(self, name, location, sales):
        """
        Initialize a new Office object.

        __init__ is a special method (called a constructor) that runs
        automatically when you create a new Office object. It sets up
        the initial properties of the object.

        Parameters:
            name (str): The office name
            location (str): Where the office is located
            sales (int): Number of sales

        Returns:
            None (constructors don't return values)
        """
        # 'self' refers to the specific object being created
        # These lines save the parameters as properties of this object
        self.name = name
        self.location = location
        self.sales = sales


# Create a new Office object called 'office'
# This calls __init__ automatically with the values we provide
office = Office("Office A", "Portland, Oregon", 7)

print("Office Object Properties:")
print("\n")
# Access the properties using dot notation: object.property
print(f"Name: {office.name}")  # Gets the 'name' property
print(f"Location: {office.location}")  # Gets the 'location' property
print(f"Sales: {office.sales}")  # Gets the 'sales' property
