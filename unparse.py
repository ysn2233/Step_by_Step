"Usage: unparse.py [-n|d] <path to source file>"
import sys
import ast
import cStringIO
import os
import networkx
import enum

class Mode(enum.Enum):
    normal = 0
    depend = 1

class Colour(enum.Enum):
    white = 0
    grey  = 1
    black = 2

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

    def __init__(self, tree, mode=Mode.normal):
        """Initialise unparser."""
        self.instructions = []
        self.buf = cStringIO.StringIO()
        self.tree = tree
        self.future_imports = []
        self.indents = 0
        self.no_newline = True
        self.mode = mode
        self.dep_graph = networkx.DiGraph()
        self.curr_vert = ""
        self.curr_buf = cStringIO.StringIO()
        self.buf_list = {}
        self.stat_list = []
        self.call_list = []
        self.out_list = []
        self.stat_seq = 1
        self.comp_stat = False
        self.func_def = False

    def run(self):
        """Generate code lines."""
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
        if self.curr_vert == "":
            if not self.comp_stat:
                self.curr_vert = "_stat_" + str(self.stat_seq) + "_"
                self.dep_graph.add_node(self.curr_vert)
                self.buf_list[self.curr_vert] = self.curr_buf
                self.curr_buf = cStringIO.StringIO()
                self.stat_list.append(self.curr_vert)
                for i in range(0, len(self.call_list)):
                    self.dep_graph.add_edge(self.curr_vert, self.call_list[i], weight=i)
                self.curr_vert = ""
                self.call_list = []
                self.stat_seq += 1
        else:
            if not self.func_def:
                self.dep_graph.add_node(self.curr_vert)
                self.buf_list[self.curr_vert] = self.curr_buf
                self.curr_buf = cStringIO.StringIO()
                for i in range(0, len(self.call_list)):
                    self.dep_graph.add_edge(self.curr_vert, self.call_list[i], weight=i)
                self.curr_vert = ""
                self.call_list = []

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

    def enter_comp(self):
        if self.indents == 0:
            self.comp_stat = True

    def leave_comp(self):
        if self.indents == 0:
            self.comp_stat = False

    def enter_def(self, name):
        if self.indents == 0:
            self.curr_vert = name
            self.func_def = True

    def leave_def(self):
        if self.indents == 0:
            self.func_def = False

    def dep_dfs(self, source):
        self.colour[source] = Colour.grey
        edges = self.dep_graph.edges(source, "weight")
        edges = sorted(edges, key=lambda t:t[2])
        for e in edges:
            if self.colour[e[1]] == Colour.white:
                self.dep_dfs(e[1])
        self.colour[source] = Colour.black
        self.out_list.append(source)

    def search(self):
        if (self.mode == Mode.depend):
            nodes = self.dep_graph.nodes()
            self.colour = dict(zip(nodes, [Colour.white] * len(nodes)))
            for s in self.stat_list:
                self.dep_dfs(s)

    def flush(self):
        if not self.out_list:
            self.instructions.extend(self.buf.getvalue().split("\n")[:-1])
            return

        for func in self.out_list:
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
        self.indent()
        self.write("import ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)

    def _ImportFrom(self, t):
        # A from __future__ import may affect unparsing, so record it.
        if t.module and t.module == '__future__':
            self.future_imports.extend(n.name for n in t.names)

        self.indent()
        self.write("from ")
        self.write("." * t.level)
        if t.module:
            self.write(t.module)
        self.write(" import ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)

    def _Assign(self, t):
        self.indent()
        for target in t.targets:
            self.dispatch(target)
            self.write(" = ")
        self.dispatch(t.value)

    def _AugAssign(self, t):
        self.indent()
        self.dispatch(t.target)
        self.write(" " + self.binop[t.op.__class__.__name__] + "= ")
        self.dispatch(t.value)

    def _Return(self, t):
        self.indent()
        self.write("return")
        if t.value:
            self.write(" ")
            self.dispatch(t.value)

    def _Pass(self, t):
        self.indent()
        self.write("pass")

    def _Break(self, t):
        self.indent()
        self.write("break")

    def _Continue(self, t):
        self.indent()
        self.write("continue")

    def _Delete(self, t):
        self.indent()
        self.write("del ")
        interleave(lambda: self.write(", "), self.dispatch, t.targets)

    def _Assert(self, t):
        self.indent()
        self.write("assert ")
        self.dispatch(t.test)
        if t.msg:
            self.write(", ")
            self.dispatch(t.msg)

    def _Exec(self, t):
        self.indent()
        self.write("exec ")
        self.dispatch(t.body)
        if t.globals:
            self.write(" in ")
            self.dispatch(t.globals)
        if t.locals:
            self.write(", ")
            self.dispatch(t.locals)

    def _Print(self, t):
        self.indent()
        self.write("print ")
        do_comma = False
        if t.dest:
            self.write(">>")
            self.dispatch(t.dest)
            do_comma = True
        for e in t.values:
            if do_comma: self.write(", ")
            else: do_comma = True
            self.dispatch(e)
        if not t.nl:
            self.write(",")

    def _Global(self, t):
        self.indent()
        self.write("global ")
        interleave(lambda: self.write(", "), self.write, t.names)

    def _Yield(self, t):
        self.write("(")
        self.write("yield")
        if t.value:
            self.write(" ")
            self.dispatch(t.value)
        self.write(")")

    def _Raise(self, t):
        self.indent()
        self.write("raise ")
        if t.type:
            self.dispatch(t.type)
        if t.inst:
            self.write(", ")
            self.dispatch(t.inst)
        if t.tback:
            self.write(", ")
            self.dispatch(t.tback)

    def _TryExcept(self, t):
        # code for function dependency
        self.enter_comp()

        self.indent()
        self.write("try")
        self.enter()
        self.dispatch(t.body)
        self.leave()

        for ex in t.handlers:
            self.dispatch(ex)
        if t.orelse:
            self.newline()
            self.indent()
            self.write("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

        # code for function dependency
        self.leave_comp()

    def _TryFinally(self, t):
        # code for function dependency
        self.enter_comp()

        if len(t.body) == 1 and isinstance(t.body[0], ast.TryExcept):
            # try-except-finally
            self.no_newline = True
            self.dispatch(t.body)
        else:
            self.indent()
            self.write("try")
            self.enter()
            self.dispatch(t.body)
            self.leave()

        self.newline()
        self.indent()
        self.write("finally")
        self.enter()
        self.dispatch(t.finalbody)
        self.leave()

        # code for function dependency
        self.leave_comp()

    def _ExceptHandler(self, t):
        # code for function dependency
        self.enter_comp()

        self.newline()
        self.indent()
        self.write("except")
        if t.type:
            self.write(" ")
            self.dispatch(t.type)
        if t.name:
            self.write(" as ")
            self.dispatch(t.name)
        self.enter()
        self.dispatch(t.body)
        self.leave()

        # code for function dependency
        self.leave_comp()

    def _ClassDef(self, t):
        # code for function dependency
        self.enter_comp()

        for deco in t.decorator_list:
            self.indent()
            self.write("@")
            self.dispatch(deco)
            self.newline()
        self.indent()
        self.write("class " + t.name)
        if t.bases:
            self.write("(")
            for a in t.bases:
                self.dispatch(a)
                self.write(", ")
            self.write(")")
        self.enter()
        self.dispatch(t.body)
        self.leave()

        # code for function dependency
        self.leave_comp()

    def _FunctionDef(self, t):
        # code for function dependency
        self.enter_def(t.name)

        for deco in t.decorator_list:
            self.indent()
            self.write("@")
            self.dispatch(deco)
            self.newline()
        self.indent()
        self.write("def " + t.name + "(")
        self.dispatch(t.args)
        self.write(")")
        self.enter()
        self.dispatch(t.body)
        self.leave()

        # code for function dependency
        self.leave_def()

    def _For(self, t):
        # code for function dependency
        self.enter_comp()

        self.indent()
        self.write("for ")
        self.dispatch(t.target)
        self.write(" in ")
        self.dispatch(t.iter)
        self.enter()
        self.dispatch(t.body)
        self.leave()
        if t.orelse:
            self.newline()
            self.indent()
            self.write("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

        # code for function dependency
        self.leave_comp()

    def _If(self, t):
        # code for function dependency
        self.enter_comp()

        self.indent()
        self.write("if ")
        self.dispatch(t.test)
        self.enter()
        self.dispatch(t.body)
        self.leave()
        # collapse nested ifs into equivalent elifs.
        while (t.orelse and len(t.orelse) == 1 and
               isinstance(t.orelse[0], ast.If)):
            t = t.orelse[0]
            self.newline()
            self.indent()
            self.write("elif ")
            self.dispatch(t.test)
            self.enter()
            self.dispatch(t.body)
            self.leave()
        # final else
        if t.orelse:
            self.newline()
            self.indent()
            self.write("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

        # code for function dependency
        self.leave_comp()

    def _While(self, t):
        # code for function dependency
        self.enter_comp()

        self.indent()
        self.write("while ")
        self.dispatch(t.test)
        self.enter()
        self.dispatch(t.body)
        self.leave()
        if t.orelse:
            self.newline()
            self.indent()
            self.write("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

        # code for function dependency
        self.leave_comp()

    def _With(self, t):
        # code for function dependency
        self.enter_comp()

        self.indent()
        self.write("with ")
        self.dispatch(t.context_expr)
        if t.optional_vars:
            self.write(" as ")
            self.dispatch(t.optional_vars)
        self.enter()
        self.dispatch(t.body)
        self.leave()

        # code for function dependency
        self.leave_comp()

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

    def _ListComp(self, t):
        self.write("[")
        self.dispatch(t.elt)
        for gen in t.generators:
            self.dispatch(gen)
        self.write("]")

    def _GeneratorExp(self, t):
        self.write("(")
        self.dispatch(t.elt)
        for gen in t.generators:
            self.dispatch(gen)
        self.write(")")

    def _SetComp(self, t):
        self.write("{")
        self.dispatch(t.elt)
        for gen in t.generators:
            self.dispatch(gen)
        self.write("}")

    def _DictComp(self, t):
        self.write("{")
        self.dispatch(t.key)
        self.write(": ")
        self.dispatch(t.value)
        for gen in t.generators:
            self.dispatch(gen)
        self.write("}")

    def _comprehension(self, t):
        self.write(" for ")
        self.dispatch(t.target)
        self.write(" in ")
        self.dispatch(t.iter)
        for if_clause in t.ifs:
            self.write(" if ")
            self.dispatch(if_clause)

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

    unop = {"Invert":"~", "Not":"not", "UAdd":"+", "USub":"-"}
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

    binop = { "Add":"+", "Sub":"-", "Mult":"*", "Div":"/", "Mod":"%",
                    "LShift":"<<", "RShift":">>", "BitOr":"|", "BitXor":"^", "BitAnd":"&",
                    "FloorDiv":"//", "Pow": "**"}
    def _BinOp(self, t):
        self.write("(")
        self.dispatch(t.left)
        self.write(" " + self.binop[t.op.__class__.__name__] + " ")
        self.dispatch(t.right)
        self.write(")")

    cmpops = {"Eq":"==", "NotEq":"!=", "Lt":"<", "LtE":"<=", "Gt":">", "GtE":">=",
                        "Is":"is", "IsNot":"is not", "In":"in", "NotIn":"not in"}
    def _Compare(self, t):
        self.write("(")
        self.dispatch(t.left)
        for o, e in zip(t.ops, t.comparators):
            self.write(" " + self.cmpops[o.__class__.__name__] + " ")
            self.dispatch(e)
        self.write(")")

    boolops = {ast.And: "and", ast.Or: "or"}
    def _BoolOp(self, t):
        self.write("(")
        s = " %s " % self.boolops[t.op.__class__]
        interleave(lambda: self.write(s), self.dispatch, t.values)
        self.write(")")

    def _Attribute(self,t):
        self.dispatch(t.value)
        # Special case: 3.__abs__() is a syntax error, so if t.value
        # is an integer literal then we need to either parenthesize
        # it or add an extra space to get 3 .__abs__().
        if isinstance(t.value, ast.Num) and isinstance(t.value.n, int):
            self.write(" ")
        self.write(".")
        self.write(t.attr)

    def _Call(self, t):
        # code for function dependency
        if isinstance(t.func, ast.Name):
            if t.func.id not in self.call_list:
                self.call_list.append(t.func.id)
        elif isinstance(t.func, ast.Attribute):
            if t.func.attr not in self.call_list:
                self.call_list.append(t.func.attr)

        self.dispatch(t.func)
        self.write("(")
        comma = False
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
        self.write(")")

    def _Subscript(self, t):
        self.dispatch(t.value)
        self.write("[")
        self.dispatch(t.slice)
        self.write("]")

    # slice
    def _Ellipsis(self, t):
        self.write("...")

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

    def _Lambda(self, t):
        self.write("(")
        self.write("lambda ")
        self.dispatch(t.args)
        self.write(": ")
        self.dispatch(t.body)
        self.write(")")

    def _alias(self, t):
        self.write(t.name)
        if t.asname:
            self.write(" as " + t.asname)

def roundtrip(filename, output=sys.stdout, mode=Mode.normal):
    with open(filename, "r") as pyfile:
        source = pyfile.read()
    tree = compile(source, filename, "exec", ast.PyCF_ONLY_AST)
    instructions = Unparser(tree, mode).run()
    for i in instructions:
        output.write(i)
        output.write("\n")

def main(args):
    if args[0] == '-n':
        roundtrip(args[1], mode=Mode.normal)
    elif args[0] == '-d':
        roundtrip(args[1], mode=Mode.depend)
    else:
        roundtrip(args[0])

if __name__ == '__main__':
    main(sys.argv[1:])
