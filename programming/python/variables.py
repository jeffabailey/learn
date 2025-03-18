#!/usr/bin/env python3
class color:
   BOLD_UNDERLINE = '\033[1m\033[4m'
   END = '\033[0m'

print(color.BOLD_UNDERLINE + 'Assign a string value to a variable' + color.END)
print("\n")
office_name = "Office A"
print(office_name)
print("\n")
print("----------------------------------------------")

print(color.BOLD_UNDERLINE + 'Assign a multiple line string value to a variable' + color.END)
print("\n")
office_name = """Office A\n
Office B
"""
print(office_name)
print("\n")
print("----------------------------------------------")

print("yo")

print(color.BOLD_UNDERLINE + 'Assign an integer value to a variable' + color.END)
print("\n")
office_sales = 7
office_sales_type = type(office_sales)
print(f"office_sales is type: {office_sales_type}")
print("\n")
print("----------------------------------------------")


print(color.BOLD_UNDERLINE + 'Assign a floating point value to a variable' + color.END)
print("\n")
office_score = 7.5
office_score_type = type(office_score)
print(f"office_score is type: {office_score_type}")
print("\n")
print("----------------------------------------------")

print(color.BOLD_UNDERLINE + 'Assign an boolean value to a variable' + color.END)
print("\n")
office_is_active = bool(True)
office_is_active_type = type(office_is_active)
print(f"office_is_active is type: {office_is_active_type}")
print("\n")
print("----------------------------------------------")

"""
Interesting tidbits

Python employs a concept called name mangling for private variables.abs
"""
