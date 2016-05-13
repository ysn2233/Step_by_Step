# How to generate re-organised output?

Take `reorganiser.py` for example:

Generate re-organised source code:
```sh
λ> python reorganiser.py -d sample_inputs/dependency.py
```
Or
```sh
λ> python reorganiser.py sample_inputs/dependency.py
```

Generate original source code:
```sh
λ> python reorganiser.py -n sample_inputs/dependency.py
```

Note: The output of `main.py` can now be handled in a similar way.



# How to generate high/low level output?

Take `processor.py` for example:

Generate high level instructions:
```sh
λ> python processor.py -h sample_inputs/draw_house.py
```

Generate low level instructions:
```sh
λ> python processor.py -l sample_inputs/draw_house.py
```
Or
```sh
λ> python processor.py sample_inputs/draw_house.py
```

Note: The output of `main.py` can now be handled in a similar way.



# How to generate instructional and statistical output?

Take `processor.py` for example:

Generate both instructions and statistics:
```sh
λ> python processor.py -b sample_inputs/draw_house.py
```
Or
```sh
λ> python processor.py sample_inputs/draw_house.py
```

Generate instructions only:
```sh
λ> python processor.py -i sample_inputs/draw_house.py
```

Generate statistics only:
```sh
λ> python processor.py -s sample_inputs/draw_house.py
```

Note: The output of `main.py` can now be handled in a similar way.



# How to create and run a test case to cover a particular method in `processor.py`?

1. define a new method named with the _**test\_**_ prefix in the
_**TestProcessor**_ class of `test_processor.py`, which simplely calls
the _**compare()**_ method provided by the class.

2. create a new python file with its basename the same as the method
name in `unittest_inputs`, and add the python code for generating
instructions into the file.

3. create a new text file with its basename the same as the method
name in `unittest_outputs`, and add the expected instructions for
comparison into the file.

4. run `test_processor.py` or `unittest_coverage.sh` to compare the
generated and expected instructions line by line.

There is a demo case for testing _**\_Import(self, t)**_ given in the
project that you can refer to.



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
        "instruction": "Create and initialize variable 't' to return
        value of function 'Turtle' on object 'turtle' without parameter"
    },
    {
        "code": "for i in range(36):",
        "instruction": "Iterate the variable i over the range from 0
        to 36, and do the following:"
    },
    {
        "code": "    t.forward(10)",
        "instruction": "    Call function 'forward' on object 't' with
        parameter of 10"
    },
    {
        "code": "    t.right(10)",
        "instruction": "    Call function 'right' on object 't' with
        parameter of 10"
    }
]
```
