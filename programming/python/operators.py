#!/usr/bin/env python3
class color:
   BOLD = '\033[1;37;48m'
   CYAN = '\033[1;36;48m'
   YELLOW = '\033[1;33;48m'
   BOLD_YELLOW = BOLD + YELLOW
   BOLD_CYAN = BOLD + CYAN
   END = '\033[1;37;0m'

print(color.BOLD_CYAN + "Arithmetic Operators" + color.END)
print("\n")

addition = 1 + 1
print(f"1 + 1 = {addition}")
print("\n")

subtraction = 2 - 1
print(f"2 - 1 = {subtraction}")
print("\n")

multiplication = 3 * 3
print(f"3 * 3 = {multiplication}")
print("\n")

division = 10 / 5
print(f"10 / 5 = {division}")
print("\n")

modulus = 6 % 3
print(f"6 % 3 = {modulus} ")
print("\n")

exponentiation = 2 ** 3
print(f"2 ** 3 = {exponentiation}")
print("\n")

print(color.BOLD_YELLOW + "Assignment Operators" + color.END)
print("\n")

equals = 1
print(f"1 = {equals}")

equals += 1
print(f"1 += {equals}")

minus_equals = 2
minus_equals -= 1
print(f"2 -= {minus_equals}")

multiply_and = 5
multiply_and *= 5
print(f"5 *= {multiply_and}")

divide_and = 5
divide_and /= 5
print(f"5 /= {divide_and}")

modulus_and = 6
modulus_and %= 3
print(f"6 %= {modulus_and}")

exponent_and = 2
exponent_and **= 3
print(f"2 **= {exponent_and}")

y = 7
floor_division = 78125.0
floor_division//=y
print(f"78125.0 //= {floor_division}")

