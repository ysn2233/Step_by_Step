#!/usr/bin/python
# -*- coding: utf-8 -*-

# originally from official python source code
# http://svn.python.org/view/*checkout*/python/trunk/Demo/parser/unparse.py

"Usage: instructor.py [-n|b|d] <path to source file>"
import sys
import ast
import cStringIO
import os
import json
import networkx
from unparse import Mode
from unparse import Colour
import Queue

Dict = {}

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

    def __init__(self, tree, mode=Mode.none, level=1):
        """Initialise instructor."""
        self.instructions = []
        self.buf = cStringIO.StringIO()
        self.tree = tree
        self.future_imports = []
        self.indents = 0
        self.no_newline = True
        self.variables = []
        self.func_name = " "
        self.no_direct_call = False
        self.import_module = False
        self.mode = mode
        self.dep_graph = networkx.DiGraph()
        self.dep_graph.add_node("header")
        self.call_seq = 1
        self.curr_buf = cStringIO.StringIO()
        self.buf_list = {"header": self.curr_buf}
        self.curr_def = "header"
        self.end_def = False
        self.func_list = []
        self.level = level

    def run(self):
        """Generate instructions."""
        self.dispatch(self.tree)
        self.newline()
        self.search()
        self.flush()
        return self.instructions

    def newline(self):
        """End current code/instruction block."""
        if self.no_newline:
            self.no_newline = False
            return
        self.write("\n")
        # code for function dependency
        if self.end_def:
            self.dep_graph.add_node("footer")
            self.call_seq = 1
            self.curr_buf = cStringIO.StringIO()
            self.buf_list["footer"] = self.curr_buf
            self.curr_def = "footer"
            self.end_def = False

    def indent(self):
        """Write appropriate indentation."""
        self.write("    " * self.indents)

    def write(self, text):
        "Append a piece of text to the current line."
        self.buf.write(text)
        self.curr_buf.write(text)

    def enter(self):
        "Print ':', and increase the indentation."
        self.write(":")
        self.indents += 1

    def leave(self):
        "Decrease the indentation level."
        self.indents -= 1

    def dispatch(self, tree):
        "Dispatcher function, dispatching tree type T to method _T."
        if isinstance(tree, ast.stmt):
            self.newline()
        if isinstance(tree, list):
            for t in tree:
                self.dispatch(t)
            return
        meth = getattr(self, "_" + tree.__class__.__name__)
        meth(tree)

    def dep_bfs(self, source):
        dist = {source:0}
        groups = [[source]]
        nodes = self.dep_graph.nodes()
        colour = dict(zip(nodes, [Colour.white] * len(nodes)))
        queue = Queue.Queue()
        queue.put(source)
        while not queue.empty():
            edges = self.dep_graph.edges(queue.get(), "weight")
            edges = sorted(edges, key=lambda t:t[2])
            for e in edges:
                if colour[e[1]] == Colour.white:
                    dist[e[1]] = dist[e[0]] + 1
                    if dist[e[1]] >= len(groups):
                        groups.append([e[1]])
                    else:
                        groups[dist[e[1]]].append(e[1])
                    colour[e[1]] = Colour.grey
                    queue.put(e[1])
            colour[e[1]] = Colour.black
        for g in groups[::-1]:
            self.func_list.extend(g)

    def dep_dfs(self, source):
        self.colour[source] = Colour.grey
        edges = self.dep_graph.edges(source, "weight")
        edges = sorted(edges, key=lambda t:t[2])
        for e in edges:
            if self.colour[e[1]] == Colour.white:
                self.dep_dfs(e[1])
        self.colour[source] = Colour.black
        self.func_list.append(source)

    def search(self):
        if (self.mode == Mode.none or
            not self.dep_graph.has_node("footer") or
            self.dep_graph.out_degree("footer") == 0):
            return

        self.func_list = ["header"]
        if self.mode == Mode.bfs:
            self.dep_bfs("footer")
        elif self.mode == Mode.dfs:
            nodes = self.dep_graph.nodes()
            self.colour = dict(zip(nodes, [Colour.white] * len(nodes)))
            self.dep_dfs("footer")
        else:
            assert False, "shouldn't get here"

    def flush(self):
        if not self.func_list:
            self.instructions.extend(self.buf.getvalue().split("\n")[:-1])
            return

        for func in self.func_list:
            if not self.buf_list.has_key(func):
                continue
            self.instructions.extend(self.buf_list[func].getvalue().split("\n")[:-1])


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
        self.indent()
        self.dispatch(tree.value)

    def _Import(self, t):
        if Dict.has_key('Import'):
            Dict['Import'] = Dict['Import'] + 1
        else:
            Dict['Import'] = 1

        self.import_module = True
        self.indent()
        self.write("Import the ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)

    def _ImportFrom(self, t):
        # A from __future__ import may affect unparsing, so record it.
        self.import_module = False
        if t.module and t.module == '__future__':
            self.future_imports.extend(n.name for n in t.names)

        self.indent()
        self.write("From the ")
        self.write("." * t.level)
        if t.module:
            self.write(t.module)
            self.write(" module")
        self.write(" import ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)

    def _Assign(self, t):
        Init = False
        if isinstance(t.targets[0], ast.Name):
            for target in t.targets:
                if not target.id in self.variables:
                    self.variables.append(target.id)
                    Init = True
        if Init:
            if Dict.has_key('Variable'):
                Dict['Variable'] = Dict['Variable'] + 1
            else:
                Dict['Variable'] = 1

            self.indent()
            self.write("Initialise a variable ")
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
            self.indent()
            self.write("Assign ")
            self.dispatch(t.value)
            self.write(" to variable ")
            for target in t.targets:
                self.dispatch(target)

    def _AugAssign(self, t):
        # Jack's implementation
        self.indent()
        self.write("The new value of ")
        self.dispatch(t.target)
        self.write(" is itself")
        # self.dispatch(t.target)
        self.write(" " + self.binop[t.op.__class__.__name__] + " ")
        self.dispatch(t.value)

    def _Return(self, t):
        self.indent()
        self.write("Return")
        if t.value:
            self.write(" ")
            self.dispatch(t.value)

    def _Break(self, t):
        if Dict.has_key('Break'):
            Dict['Break'] = Dict['Break'] + 1
        else:
            Dict['Break'] = 1

        self.indent()
        self.write("Break out of the current loop")

    def _Continue(self, t):
        if Dict.has_key('Continue'):
            Dict['Continue'] = Dict['Continue'] + 1
        else:
            Dict['Continue'] = 1

        self.indent()
        self.write("Skip the rest of the code inside the loop and continue on with the next iteration")

    def _Assert(self, t):
        if Dict.has_key('Assert'):
            Dict['Assert'] = Dict['Assert'] + 1
        else:
            Dict['Assert'] = 1

        self.indent()
        # self.write("Assert ")
        self.write("Check the condition of ")
        self.dispatch(t.test)
        self.write(" and if it is not ture, throw an exception ")
        if t.msg:
            # self.write(", ")
            self.write("with the message ")
            self.dispatch(t.msg)

    def _Print(self, t):
        if Dict.has_key('Print'):
            Dict['Print'] = Dict['Print'] + 1
        else:
            Dict['Print'] = 1

        self.no_direct_call = True
        self.indent()
        self.write("Print the result of ")
        do_comma = False
        for e in t.values:
            if do_comma: self.write(', ')
            else: do_comma = True
            self.dispatch(e)
        self.write(" to screen")
        self.no_direct_call = False

    def _ClassDef(self, t):
        if Dict.has_key('ClassDef'):
            Dict['ClassDef'] = Dict['ClassDef'] + 1
        else:
            Dict['ClassDef'] = 1

        self.indent()
        self.write("Define a class '" + t.name + "'")
        do_comma = False
        if t.bases:
            # self.write("(")
            if Dict.has_key('ClassDef_inherit'):
                Dict['ClassDef_inherit'] = Dict['ClassDef_inherit'] + 1
            else:
                Dict['ClassDef_inherit'] = 1

            self.write(", which inherits from ")
            for a in t.bases:
                if do_comma: self.write(", ")
                else: do_comma = True
                self.dispatch(a)
        # self.write(")")
        self.enter()
        self.dispatch(t.body)
        self.leave()

    def _FunctionDef(self, t):
        # code for function dependency
        if self.curr_def == "header":
            self.curr_buf = cStringIO.StringIO()
        else:
            self.buf_list["footer"] = None
        self.buf_list[t.name] = self.curr_buf
        self.curr_def = t.name

        if Dict.has_key('FunctionDef'):
            Dict['FunctionDef'] = Dict['FunctionDef'] + 1
        else:
            Dict['FunctionDef'] = 1

        self.func_name = t.name
        self.indent()
        self.write("Define a function '" + t.name + "'")
        if len(t.args.args) == 0:
            self.write(" without parameters")
        elif len(t.args.args) == 1:
            self.write(" with a parameter ")
        else:
            self.write(" with parameters ")
        self.dispatch(t.args)
        self.enter()
        if (self.level == 0):
            if (isinstance(t.body[0], ast.Expr)):
                if (isinstance(t.body[0].value, ast.Str)):
                    self.newline()
                self.indent()
                self.write(ast.get_docstring(t))
                self.newline()
        if (self.level == 1):
            self.dispatch(t.body)
        self.func_name = " "
        self.leave()

        # code for function dependency
        self.end_def = True

    def _For(self, t):
        if Dict.has_key('For'):
            Dict['For'] = Dict['For'] + 1
        else:
            Dict['For'] = 1

        self.indent()
        self.write("Iterate variable ")
        self.dispatch(t.target)
        self.write(" over ")
        self.dispatch(t.iter)
        self.write(", and do the following")
        self.enter()
        self.dispatch(t.body)
        self.leave()

    def _If(self, t):
        if Dict.has_key('If'):
            Dict['If'] = Dict['If'] + 1
        else:
            Dict['If'] = 1

        self.indent()
        self.write("If ")
        self.dispatch(t.test)
        self.write(", do the following")
        self.enter()
        self.dispatch(t.body)
        self.leave()
        # collapse nested ifs into equivalent elifs.
        while (t.orelse and len(t.orelse) == 1 and
               isinstance(t.orelse[0], ast.If)):
            t = t.orelse[0]
            self.newline()
            self.indent()
            self.write("Else if ")
            self.dispatch(t.test)
            self.write(", do the following")
            self.enter()
            self.dispatch(t.body)
            self.leave()
        # final else
        if t.orelse:
            self.newline()
            self.indent()
            self.write("Else, do the following")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

    def _While(self, t):
        if Dict.has_key('While'):
            Dict['While'] = Dict['While'] + 1
        else:
            Dict['While'] = 1

        self.indent()
        self.write("While ")
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
            print '='*30
            self.write("b" + repr(tree.s))
        elif isinstance(tree.s, unicode):
            print '-'*30
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
        self.write(repr_n)
        if repr_n.startswith("-"):
            self.write(")")

    def _List(self, t):
        if Dict.has_key('List'):
            Dict['List'] = Dict['List'] + 1
        else:
            Dict['List'] = 1

        self.write("list [")
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
        if Dict.has_key('Set'):
            Dict['Set'] = Dict['Set'] + 1
        else:
            Dict['Set'] = 1

        assert(t.elts) # should be at least one element
        self.write("set {")
        interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write("}")

    def _Dict(self, t):
        if Dict.has_key('Dict'):
            Dict['Dict'] = Dict['Dict'] + 1
        else:
            Dict['Dict'] = 1

        self.write("dictionary {")
        def write_pair(pair):
            (k, v) = pair
            self.dispatch(k)
            self.write(": ")
            self.dispatch(v)
        interleave(lambda: self.write(", "), write_pair, zip(t.keys, t.values))
        self.write("}")

    def _Tuple(self, t):
        if Dict.has_key('Tuple'):
            Dict['Tuple'] = Dict['Tuple'] + 1
        else:
            Dict['Tuple'] = 1

        self.write("tuple (")
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
        # self.write(" ")
        # If we're applying unary minus to a number, parenthesize the number.
        # This is necessary: -2147483648 is different from -(2147483648) on
        # a 32-bit machine (the first is an int, the second a long), and
        # -7j is different from -(7j).  (The first has real part 0.0, the second
        # has real part -0.0.)
        if isinstance(t.op, ast.Not):
            self.write(" ")
            self.dispatch(t.operand)
        elif isinstance(t.op, ast.USub) and isinstance(t.operand, ast.Num):
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

    boolops = {ast.And: "AND", ast.Or: "OR"}

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
        # if isinstance(t.value, ast.Num) and isinstance(t.value.n, int):
        #     self.write(" ")
        # self.write(".")
        # self.write(t.attr)

    def _Call(self, t):
        # code for function dependency
        if isinstance(t.func, ast.Name):
            if not self.dep_graph.has_edge(self.curr_def, t.func.id):
                self.dep_graph.add_edge(self.curr_def, t.func.id, weight=self.call_seq)
                self.call_seq += 1
        elif isinstance(t.func, ast.Attribute):
            if not self.dep_graph.has_edge(self.curr_def, t.func.attr):
                self.dep_graph.add_edge(self.curr_def, t.func.attr, weight=self.call_seq)
                self.call_seq += 1

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
        # handle cases of no arguments
        if len(t.args) + len(t.keywords) == 0:
            self.write(" without arguments")
        elif len(t.args) + len(t.keywords) == 1:
            self.write(" with an argument ")
        else:
            self.write(" with arguments ")
        for e in t.args:
            if comma: self.write(", ")
            else: comma = True
            self.dispatch(e)
        for e in t.keywords:
            if comma: self.write(", ")
            else: comma = True
            self.dispatch(e)

    def _Subscript(self, t):
        self.dispatch(t.value)
        self.write("[")
        self.dispatch(t.slice)
        self.write("]")

    def _Index(self, t):
        self.dispatch(t.value)

    def _Slice(self, t):
        # NOTE: no human readable instruction generated here
        if t.lower:
            self.dispatch(t.lower)
        self.write(":")
        if t.upper:
            self.dispatch(t.upper)
        if t.step:
            self.write(":")
            self.dispatch(t.step)

    def _ExtSlice(self, t):
        interleave(lambda: self.write(", "), self.dispatch, t.dims)

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
                self.write(" with default value ")
                self.dispatch(d)

    def _keyword(self, t):
        self.write(t.arg)
        self.write("=")
        self.dispatch(t.value)

    def _alias(self, t):
        self.write(t.name)
        if self.import_module:
            self.write(" module")
        if t.asname:
            self.write(" as " + t.asname)

def roundtrip(filename, output=sys.stdout, mode=Mode.none, level=0):
    with open(filename, "r") as pyfile:
        source = pyfile.read()
    tree = compile(source, filename, "exec", ast.PyCF_ONLY_AST)
    instructions = Unparser(tree, mode, level).run()
    for i in instructions:
        output.write(i)
        output.write("\n")

def main(args):
    if args[0] == '-n':
        roundtrip(args[1], mode=Mode.none, level=1)
    elif args[0] == '-b':
        roundtrip(args[1], mode=Mode.bfs, level=1)
    elif args[0] == '-d':
        roundtrip(args[1], mode=Mode.dfs, level=1)
    elif args[0] == '-h':
        roundtrip(args[1], mode=Mode.none, level=0)
        return 1
    else:
        roundtrip(args[0], mode=Mode.none, level=1)
    return 0


if __name__ == '__main__':
    ifstat = main(sys.argv[1:])
    if (ifstat==0):
        print('-------------------\n')
        for i in Dict:
            print i, Dict[i]
