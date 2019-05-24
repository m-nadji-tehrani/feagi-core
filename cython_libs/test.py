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
a = (3, 5)
c = max(a)
'''

mycode3 = ''' 
a = np.array([3,5])
c = a.max()
'''

# timeit statement
print(timeit.timeit(setup=mysetup,
              stmt=mycode,
              number=1000000))


print(timeit.timeit(setup=mysetup,
              stmt=mycode2,
              number=1000000))

print(timeit.timeit(setup=mysetup,
              stmt=mycode3,
              number=1000000))
