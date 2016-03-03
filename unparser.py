#!/usr/bin/python
# -*- coding: utf-8 -*-

# originally from official python source code
# http://svn.python.org/view/*checkout*/python/trunk/Demo/parser/unparse.py

"Usage: unparse.py <path to source file>"
import sys
import ast
import cStringIO
import os

VARS = []
# Large float and imaginary literals get turned into infinities in the AST.
# We unparse those infinities to INFSTR.
INFSTR = "1e" + repr(sys.float_info.max_10_exp + 1)

def interleave(inter, f, seq):
    """Call f on each item in seq, calling inter() in between.
    """
    seq = iter(seq)
    try:
        f(next(seq))
    except StopIteration:
        pass
    else:
        for x in seq:
            inter()
            f(x)

class Unparser:
    """Methods in this class recursively traverse an AST and
    output source code for the abstract syntax; original formatting
    is disregarded. """

    # member varibale (some flags to handle different cases)
    func_name = " "
    no_direct_call = False

    ###################

    def __init__(self, tree, file = sys.stdout):
        """Unparser(tree, file=sys.stdout) -> None.
         Print the source for tree to file."""
        self.f = file
        self.future_imports = []
        self._indent = 0
        self.first_line = True
        self.dispatch(tree)
        self.f.write("")
        self.newline()
        self.f.flush()

    def fill(self, text = ""):
        "Indent a piece of text, according to the current indentation level"
        if not self.first_line:
            self.f.write("\n")
        self.f.write("    "*self._indent + text)
        self.first_line = False

    def newline(self):
        """BY WL: write a newline to screen"""
        self.f.write("\n")

    def indent(self):
        """BY WL: write appropriate indentation"""
        self.f.write("    " * self._indent)

    def write(self, text):
        "Append a piece of text to the current line."
        self.f.write(text)

    def enter(self):
        "Print ':', and increase the indentation."
        self.write(":")
        self._indent += 1

    def leave(self):
        "Decrease the indentation level."
        self._indent -= 1

    def dispatch(self, tree):
        "Dispatcher function, dispatching tree type T to method _T."
        if isinstance(tree, list):
            for t in tree:
                self.dispatch(t)
            return
        meth = getattr(self, "_"+tree.__class__.__name__)
        meth(tree)


    ############### Unparsing methods ######################
    # There should be one method per concrete grammar type #
    # Constructors should be grouped by sum type. Ideally, #
    # this would follow the order in the grammar, but      #
    # currently doesn't.                                   #
    ########################################################

    def _Module(self, tree):
        for stmt in tree.body:
            self.dispatch(stmt)

    # stmt

    def _Expr(self, tree):
        self.fill()
        self.dispatch(tree.value)

    def _Import(self, t):
        self.fill("Import the ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)
        self.write(" module")

    def _ImportFrom(self, t):
        # A from __future__ import may affect unparsing, so record it.
        if t.module and t.module == '__future__':
            self.future_imports.extend(n.name for n in t.names)

        self.fill("from ")
        self.write("." * t.level)
        if t.module:
            self.write(t.module)
        self.write(" import ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)

    def _Assign(self, t):
        # self.fill()
        # for target in t.targets:
        #     self.dispatch(target)
        #     self.write(" = ")
        # self.dispatch(t.value)

        Init = False
        if isinstance(t.targets[0], ast.Name):
            for target in t.targets:
                if not target.id in VARS:
                    VARS.append(target.id)
                    Init = True
        if Init:
            self.fill("Create and initialize variable ")
            for target in t.targets:
                self.write("\'")
                self.dispatch(target)
                self.write("\'")
            self.write(" to ")
            if isinstance(t.value, ast.Call):
                self.no_direct_call = True
            self.dispatch(t.value)
            self.no_direct_call = False

        else:
            self.fill("Assign ")
            self.dispatch(t.value)
            self.write(" to variable ")
            for target in t.targets:
                self.dispatch(target)

    def _AugAssign(self, t):

        '''
        self.fill()
        self.dispatch(t.target)
        self.write(" "+self.binop[t.op.__class__.__name__]+"= ")
        self.dispatch(t.value)
        '''
        # Jack's implementation
        self.fill()
        self.write("The new value of ")
        self.dispatch(t.target)
        self.write(" is itself")
        #self.dispatch(t.target)
        self.write(" "+self.binop[t.op.__class__.__name__]+' ')
        self.dispatch(t.value)

    def _Return(self, t):
        self.fill("Return")
        if t.value:
            self.write(" ")
            self.dispatch(t.value)

    def _Break(self, t):
        self.fill("Break")

    def _Continue(self, t):
        self.fill("Continue")

    def _Assert(self, t):
        self.fill("Assert ")
        self.dispatch(t.test)
        if t.msg:
            self.write(", ")
            self.dispatch(t.msg)

    def _Print(self, t):
        # self.fill("print ")
        # do_comma = False
        # if t.dest:
        #     self.write(">>")
        #     self.dispatch(t.dest)
        #     do_comma = True
        # for e in t.values:
        #     if do_comma:self.write(", ")
        #     else:do_comma=True
        #     self.dispatch(e)
        # if not t.nl:
        #     self.write(",")
        self.no_direct_call = True
        self.fill("Print the result of ")
        do_comma = False
        for e in t.values:
            if do_comma: self.write(', ')
            else: do_comma = True
            self.dispatch(e)
        self.write(" to screen")
        self.no_direct_call = False

    def _ClassDef(self, t):
        self.write("\n")
        self.fill("class "+t.name)
        if t.bases:
            self.write("(")
            for a in t.bases:
                self.dispatch(a)
                self.write(", ")
            self.write(")")
        self.enter()
        self.dispatch(t.body)
        self.leave()

    def _FunctionDef(self, t):
        '''call
        self.write("\n")
        for deco in t.decorator_list:
            self.fill("@")
            self.dispatch(deco)
        self.fill("def "+t.name + "(")
        self.dispatch(t.args)
        self.write(")")
        self.enter()
        self.dispatch(t.body)
        self.leave()
        '''
        # Jack's implementation
        self.func_name = t.name
        self.fill("Define a function called '" + t.name + "'")
        self.fill("Set the input arguments to (")
        self.dispatch(t.args)
        self.write(")")
        self.enter()
        self.dispatch(t.body)
        self.func_name = " "
        self.leave()

    def _For(self, t):
        # self.fill("for ")
        # self.dispatch(t.target)
        # self.write(" in ")
        # self.dispatch(t.iter)
        # self.enter()
        # self.dispatch(t.body)
        # self.leave()
        # if t.orelse:
        #     self.fill("else")
        #     self.enter()
        #     self.dispatch(t.orelse)
        #     self.leave()

        self.fill("Iterate the variable ")
        self.dispatch(t.target)
        self.write(" over ")
        self.dispatch(t.iter)
        self.write(", and do the following")
        self.enter()
        self.dispatch(t.body)
        self.leave()

    def _If(self, t):
        self.fill("If ")
        self.dispatch(t.test)
        self.write(", do the following")
        self.enter()
        self.dispatch(t.body)
        self.leave()
        # collapse nested ifs into equivalent elifs.
        while (t.orelse and len(t.orelse) == 1 and
               isinstance(t.orelse[0], ast.If)):
            t = t.orelse[0]
            self.fill("Else if ")
            self.dispatch(t.test)
            self.write(", do the following")
            self.enter()
            self.dispatch(t.body)
            self.leave()
        # final else
        if t.orelse:
            self.fill("Else, do the following")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

    def _While(self, t):
        '''
        self.fill("while ")
        self.dispatch(t.test)
        self.enter()
        self.dispatch(t.body)
        self.leave()
        if t.orelse:
            self.fill("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()
        '''
        # Jack's implementation

        self.fill("While ")
        self.dispatch(t.test)
        self.write(", do the following")
        self.enter()
        self.dispatch(t.body)
        self.leave()

    # expr
    def _Str(self, tree):
        # if from __future__ import unicode_literals is in effect,
        # then we want to output string literals using a 'b' prefix
        # and unicode literals with no prefix.
        if "unicode_literals" not in self.future_imports:
            self.write(repr(tree.s))
        elif isinstance(tree.s, str):
            self.write("b" + repr(tree.s))
        elif isinstance(tree.s, unicode):
            self.write(repr(tree.s).lstrip("u"))
        else:
            assert False, "shouldn't get here"

    def _Name(self, t):
        self.write(t.id)

    def _Repr(self, t):
        self.write("`")
        self.dispatch(t.value)
        self.write("`")

    def _Num(self, t):
        repr_n = repr(t.n)
        # Parenthesize negative numbers, to avoid turning (-1)**2 into -1**2.
        if repr_n.startswith("-"):
            self.write("(")
        # Substitute overflowing decimal literal for AST infinities.
        self.write(repr_n.replace("inf", INFSTR))
        if repr_n.startswith("-"):
            self.write(")")

    def _List(self, t):
        self.write("[")
        interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write("]")

    def _IfExp(self, t):
        self.write("(")
        self.dispatch(t.body)
        self.write(" if ")
        self.dispatch(t.test)
        self.write(" else ")
        self.dispatch(t.orelse)
        self.write(")")

    def _Set(self, t):
        assert(t.elts) # should be at least one element
        self.write("{")
        interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write("}")

    def _Dict(self, t):
        self.write("{")
        def write_pair(pair):
            (k, v) = pair
            self.dispatch(k)
            self.write(": ")
            self.dispatch(v)
        interleave(lambda: self.write(", "), write_pair, zip(t.keys, t.values))
        self.write("}")

    def _Tuple(self, t):
        self.write("(")
        if len(t.elts) == 1:
            (elt,) = t.elts
            self.dispatch(elt)
            self.write(",")
        else:
            interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write(")")

    unop = {"Invert":"~", "Not": "not", "UAdd":"+", "USub":"-"}

    def _UnaryOp(self, t):
        self.write("(")
        self.write(self.unop[t.op.__class__.__name__])
        self.write(" ")
        # If we're applying unary minus to a number, parenthesize the number.
        # This is necessary: -2147483648 is different from -(2147483648) on
        # a 32-bit machine (the first is an int, the second a long), and
        # -7j is different from -(7j).  (The first has real part 0.0, the second
        # has real part -0.0.)
        if isinstance(t.op, ast.USub) and isinstance(t.operand, ast.Num):
            self.write("(")
            self.dispatch(t.operand)
            self.write(")")
        else:
            self.dispatch(t.operand)
        self.write(")")

    binop = {"Add":"plus", "Sub":"minus", "Mult":"times", "Div":"over", "Mod":"modulo",
             "LShift":"shifts left by", "RShift":"shifts right by",
             "BitOr":"bitwise OR", "BitAnd":"bitwise AND", "BitXor":"bitwise XOR",
             "FloorDiv":"floor over", "Pow": "to the power of"}

    def _BinOp(self, t):
        self.write("(")
        self.dispatch(t.left)
        self.write(" " + self.binop[t.op.__class__.__name__] + " ")
        self.dispatch(t.right)
        self.write(")")

    cmpops = {"Eq":"is equal to", "NotEq":"is not equal to",
              "Lt":"is less than", "LtE":"is less than or equal to",
              "Gt":"is greater than", "GtE":"is greater than or equal to",
              "Is":"is", "IsNot":"is not", "In":"is in", "NotIn":"is not in"}

    def _Compare(self, t):
        self.write("(")
        self.dispatch(t.left)
        for o, e in zip(t.ops, t.comparators):
            self.write(" " + self.cmpops[o.__class__.__name__] + " ")
            self.dispatch(e)
        self.write(")")

    boolops = {ast.And: 'AND', ast.Or: 'OR'}

    def _BoolOp(self, t):
        self.write("(")
        s = " %s " % self.boolops[t.op.__class__]
        interleave(lambda: self.write(s), self.dispatch, t.values)
        self.write(")")

    def _Attribute(self,t):
        self.write("\'" + t.attr + "\'")
        self.write(" on object \'")
        self.dispatch(t.value)
        self.write("\'")
        # self.dispatch(t.value)
        # Special case: 3.__abs__() is a syntax error, so if t.value
        # is an integer literal then we need to either parenthesize
        # it or add an extra space to get 3 .__abs__().
        if isinstance(t.value, ast.Num) and isinstance(t.value.n, int):
            self.write(" ")
        #self.write(".")
        #self.write(t.attr)

    def _Call(self, t):
        # special requirement on range([start], stop[, step])
        if isinstance(t.func, ast.Name) and t.func.id == "range":
            cnt = 0
            for e in t.args:
                cnt += 1
            if cnt == 1:
                self.write("the range from 0 to ")
                self.dispatch(t.args[0])
            elif cnt == 2:
                self.write("the range from ")
                self.dispatch(t.args[0])
                self.write(" to ")
                self.dispatch(t.args[1])
            else:
                self.write("the range from ")
                self.dispatch(t.args[0])
                self.write(" to ")
                self.dispatch(t.args[1])
                self.write(" with the step of ")
                self.dispatch(t.args[2])
            return
        # special requirement on range([start], stop[, step])sub
        if (self.no_direct_call == True):
            self.write ("return value of function ")
            # self.no_direct_call = False;
        else:
            self.write("Call function ")
        if isinstance(t.func, ast.Name):
            self.write("'")
        self.dispatch(t.func)
        if isinstance(t.func, ast.Name):
            self.write("'")
        if isinstance(t.func, ast.Name) and t.func.id == self.func_name:
            self.write(" recursively")
        comma = False
        # handle cases of no parameters
        if not t.args:
            self.write(" without parameters")
        else:
            self.write(" with parameters of ")
        for e in t.args:
            if comma: self.write(", ")
            else: comma = True
            self.dispatch(e)
        for e in t.keywords:
            if comma: self.write(", ")
            else: comma = True
            self.dispatch(e)
        if t.starargs:
            if comma: self.write(", ")
            else: comma = True
            self.write("*")
            self.dispatch(t.starargs)
        if t.kwargs:
            if comma: self.write(", ")
            else: comma = True
            self.write("**")
            self.dispatch(t.kwargs)

    def _Subscript(self, t):
        self.dispatch(t.value)
        self.write("[")
        self.dispatch(t.slice)
        self.write("]")

    def _Index(self, t):
        self.dispatch(t.value)

    def _Slice(self, t):
        if t.lower:
            self.dispatch(t.lower)
        self.write(":")
        if t.upper:
            self.dispatch(t.upper)
        if t.step:
            self.write(":")
            self.dispatch(t.step)

    def _ExtSlice(self, t):
        interleave(lambda: self.write(', '), self.dispatch, t.dims)

    # others
    def _arguments(self, t):
        first = True
        # normal arguments
        defaults = [None] * (len(t.args) - len(t.defaults)) + t.defaults
        for a,d in zip(t.args, defaults):
            if first:first = False
            else: self.write(", ")
            self.dispatch(a),
            if d:
                self.write("=")
                self.dispatch(d)

        # varargs
        if t.vararg:
            if first:first = False
            else: self.write(", ")
            self.write("*")
            self.write(t.vararg)

        # kwargs
        if t.kwarg:
            if first:first = False
            else: self.write(", ")
            self.write("**"+t.kwarg)

    def _keyword(self, t):
        self.write(t.arg)
        self.write("=")
        self.dispatch(t.value)

    def _alias(self, t):
        self.write(t.name)
        if t.asname:
            self.write(" as "+t.asname)

def roundtrip(filename, output=sys.stdout):
    with open(filename, "r") as pyfile:
        source = pyfile.read()
    tree = compile(source, filename, "exec", ast.PyCF_ONLY_AST)
    Unparser(tree, output)

def testdir(a):
    try:
        names = [n for n in os.listdir(a) if n.endswith('.py')]
    except OSError:
        sys.stderr.write("Directory not readable: %s" % a)
    else:
        for n in names:
            fullname = os.path.join(a, n)
            if os.path.isfile(fullname):
                output = cStringIO.StringIO()
                print 'Testing %s' % fullname
                try:
                    roundtrip(fullname, output)
                except Exception as e:
                    print '  Failed to compile, exception is %s' % repr(e)
            elif os.path.isdir(fullname):
                testdir(fullname)

def main(args):
    if args[0] == '--testdir':
        for a in args[1:]:
            testdir(a)
    else:
        for a in args:
            roundtrip(a)

if __name__=='__main__':
    main(sys.argv[1:])
