# importing the required module
import timeit

# code snippet to be executed only once
mysetup = "import numpy as np"

# code snippet whose execution time is to be measured
mycode = ''' 
a = 5
b = 3
c = max(a,b)
'''
mycode2 = ''' 
a = 5
b = 3
if a > 3:
    a = 3
'''

mycode3 = '''
a = 5
b = 8
if a > 3:
    a = 3
'''


# timeit statement
print(timeit.timeit(setup=mysetup,
              stmt=mycode,
              number=10000000))

print(timeit.timeit(setup=mysetup,
              stmt=mycode2,
              number=10000000))

print(timeit.timeit(setup=mysetup,
              stmt=mycode3,
              number=10000000))

