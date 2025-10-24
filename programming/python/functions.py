#!/usr/bin/env python3

def file_check(fn):
  try:
      example_csv = open(fn, "r")
      try:
          print("Found file, printing file")
          print("\n")
          print(example_csv.read())
      finally:
          example_csv.close()
  except IOError:
      print('Error: File does not exist.')

file_check("example.csv")
