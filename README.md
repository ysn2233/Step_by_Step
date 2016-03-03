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

# Demo of unittest
Make sure your `dev` branch is up-to-date. `test_factors` and `test_leave`
methods in `test_unparser.py` have been implemented with comments, and can be
modified/extended to handle other test cases as well.

```sh
λ> git checkout dev     # switch to dev branch
λ> ./coverage.sh 
......
----------------------------------------------------------------------
Ran 6 tests in 0.001s

OK
Name          Stmts   Miss Branch BrPart     Cover
--------------------------------------------------
unparser.py     413    218    150     23    42.98%
```
You can then open `htmlcov/index.html` to see a nice web output.
