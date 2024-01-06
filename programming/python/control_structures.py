#!/usr/bin/env python3

# A for loop
offices = ["Office A", "Office B", "Office C"]

for office in offices:
  print(office)

# A while loop
offices = ['Office A', 'Office B', 'Office C']
while offices:
  print(offices.pop(-1))

# An if-else statement
office_a_sales = 3
office_b_sales = 100
if office_b_sales > office_a_sales:
  print("Office B sales are greater than Office A sales")
elif office_a_sales > office_b_sales:
  print("Office A sales are greater than Office B sales")

