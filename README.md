This module tries to parse an input source program into an AST and
understand its semantics if necessary.

# Question:
1. How to run a python script line by line (or with exact control), and
   check its variable values without polluting the global namespace?

## Easy
```python
for i in range(5):          # loop over elements of range(5)
    print i                 # print i to screen
```

## Hard - Evaluation of `range(foo)` can only happen at runtime
```python
# ############################################################################# 
# Example 1
# ############################################################################# 
foo = input("Please enter a number:")
for i in range(foo)
    print i

# ############################################################################# 
# Example 2
# ############################################################################# 
def range(x):
    print "BLAH"

for i in range(5):
    print i
```
