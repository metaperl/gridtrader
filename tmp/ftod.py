from decimal import Decimal
from sympy.core.numbers import Float

num = Float(2)
num = float(num)
parts = Decimal(num)
print(parts)


# TypeError: conversion from Float to Decimal is not supported
