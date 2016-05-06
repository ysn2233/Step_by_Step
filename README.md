# How to choose instruction level?
Default is low-level line by line translation
λ:> python instructor.py -h sample_inputs/docstring.py
which can generate instruction in high level

# How to use dependency feature to re-organise output?

Take *instructor.py* for example:

Re-organise generated instructions in breadth-first order
```sh
λ:> python instructor.py -b sample_inputs/dependency.py
```

Re-organise generated instructions in depth-first order
```sh
λ> python instructor.py -d sample_inputs/dependency.py
```

Keep generated instructions in orignal order
```sh
λ> python instructor.py sample_inputs/dependency.py
```
Or
```sh
λ> python instructor.py -n sample_inputs/dependency.py
```

Note: The output of *main.py* and *unparse.py* can now be handled in a similar way.

# How to create and run a test case to cover a particular method in instructor.py?

1. define a new method named with the test_ prefix in the TestInstructor
class of test_instructor.py, which simplely calls the compare() method
provided by the class.

2. create a new python file with its basename the same as the method
name in unittest_inputs, and add the python code for generating
instructions into the file.

3. create a new text file with its basename the same as the method
name in unittest_outputs, and add the expected instructions for
comparison into the file.

4. run test_instructor.py or unittest_coverage.sh to compare the
generated and expected instructions line by line.

There is a demo case for testing _Import(self, t) given in the project
that you can refer to.

# Demo of dumping json to stdout
```sh
λ> python main.py sample_inputs/circle.py 
[
    {
        "code": "import turtle", 
        "instruction": "Import the turtle module"
    }, 
    {
        "code": "t = turtle.Turtle()", 
        "instruction": "Create and initialize variable 't' to return value of function 'Turtle' on object 'turtle' without parameter"
    }, 
    {
        "code": "for i in range(36):", 
        "instruction": "Iterate the variable i over the range from 0 to 36, and do the following:"
    }, 
    {
        "code": "    t.forward(10)", 
        "instruction": "    Call function 'forward' on object 't' with parameter of 10"
    }, 
    {
        "code": "    t.right(10)", 
        "instruction": "    Call function 'right' on object 't' with parameter of 10"
    }
]
```
