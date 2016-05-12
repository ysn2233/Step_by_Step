from __future__ import print_function

def func3():
    return 3

def func5():
    return 5

def func2():
    return 2

def func1():
    return func2() + func3()

def func6():
    return 6

def func4():
    return func5() + func6()

print (func1())
print (func4())
