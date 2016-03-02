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
