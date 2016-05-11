#!/usr/bin/python
# -*- coding: utf-8 -*-

# originally from official python source code
# http://svn.python.org/view/*checkout*/python/trunk/Demo/parser/unparse.py

"Usage: instructor.py [-n|d] [-l|h] <path to source file>"
import sys
import ast
import cStringIO
import os
import networkx
import enum
from unparse import Mode
from unparse import Colour
from unparse import Level
import re

class Option(enum.Enum):
    both = 0
    instr = 1
    statis = 2

def interleave(inter, f, seq):
    "Call f on each item in seq, calling inter() in between."
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
    is disregarded."""

    def __init__(self, tree, mode=Mode.normal, level=Level.low):
        "Initialise instructor."
        self.instructions = []
        self.statistics = {}
        self.tree = tree
        self.future_imports = []
        self.indents = 0
        self.no_newline = True
        self.variables = []
        self.func_name = ""
        self.direct_call = True
        self.import_module = False
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
        self.level = level
        self.docs_list = {}
        self.mod_list = {}
        self.mod_map = {}
        self.func_map = {}
        self.var_list = {}
        self.from_mod = ""
        self.stat_execs = {}
        self.def_calls = {}
        self.other_calls = 0

    def run(self):
        "Generate instructions."
        self.imp_mod("built_in")
        self.dispatch(self.tree)
        self.newline()
        self.search()
        self.flush()
        self.collect()
        return self.instructions, self.statistics

    def newline(self):
        "End current code/instruction block."
        self.direct_call = True
        if self.no_newline:
            self.no_newline = False
            return
        self.write("\n")

        # code for function dependency
        if not self.curr_vert:
            if not self.comp_stat:
                self.curr_vert = "_stat_" + str(self.stat_seq) + "_"
                self.dep_graph.add_node(self.curr_vert)
                self.buf_list[self.curr_vert] = self.curr_buf
                self.curr_buf = cStringIO.StringIO()
                self.stat_list.append(self.curr_vert)
                for i in range(len(self.call_list)):
                    self.dep_graph.add_edge(self.curr_vert, self.call_list[i], weight=i)
                self.out_list.append(self.curr_vert)
                self.curr_vert = ""
                self.call_list = []
                self.stat_seq += 1
        else:
            if not self.func_def:
                self.dep_graph.add_node(self.curr_vert)
                if self.level == Level.high:
                    self.buf_list[self.curr_vert] = cStringIO.StringIO()
                    self.buf_list[self.curr_vert].write(self.curr_buf.getvalue().split("\n")[0] + "\n")
                    self.buf_list[self.curr_vert].write(self.docs_list[self.curr_vert])
                    self.curr_buf = cStringIO.StringIO()
                else:
                    self.buf_list[self.curr_vert] = self.curr_buf
                    self.curr_buf = cStringIO.StringIO()
                for i in range(len(self.call_list)):
                    self.dep_graph.add_edge(self.curr_vert, self.call_list[i], weight=i)
                self.out_list.append(self.curr_vert)
                self.curr_vert = ""
                self.call_list = []

    def indent(self):
        "Write appropriate indentation."
        self.write("    " * self.indents)

    def write(self, text):
        "Append a piece of text to the current line."
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

        # if top level is a function call
        if isinstance(tree, ast.Call):
            pass
        elif (not isinstance(tree, ast.Expr) or
              not isinstance(tree.value, ast.Call)):
            self.direct_call = False

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
        edges.sort(key=lambda t:t[2])
        for e in edges:
            if self.colour[e[1]] == Colour.white:
                self.dep_dfs(e[1])
        self.colour[source] = Colour.black
        self.out_list.append(source)

    def search(self):
        if (self.mode == Mode.depend):
            self.out_list = []
            nodes = self.dep_graph.nodes()
            self.colour = dict(zip(nodes, [Colour.white] * len(nodes)))
            for s in self.stat_list:
                self.dep_dfs(s)

    def flush(self):
        for vert in self.out_list:
            if not self.buf_list.has_key(vert):
                continue
            self.instructions.extend(self.buf_list[vert].getvalue().split("\n")[:-1])

    def match(self, call, sign):
        if call[0] != sign[0] or call[1] != sign[1]:
            return False
        for kwarg in call[2:]:
            if kwarg not in sign[2:]:
                return False
        return True

    def get_tml(self, mod, call):
        if not self.mod_map.has_key(mod):
            return ""
        mod = self.mod_map[mod]
        if mod == "built_in":
            for sign in self.func_map:
                if self.match(call, sign):
                    mod = self.func_map[sign][0]
                    sign = self.func_map[sign][1]
                    self.mod_list[mod][sign][1] += 1
                    return self.mod_list[mod][sign][0]
        for sign in self.mod_list[mod]:
            if self.match(call, sign):
                self.mod_list[mod][sign][1] += 1
                return self.mod_list[mod][sign][0]
        return ""

    def resolve(self, line):
        fields = re.split(r"\s{2,}", line)
        if len(fields) < 2:
            return (), ""
        tml_split = fields[1].split("|")
        tml_args = re.findall(r"\[(arg[0-9]+)\]", tml_split[0])
        tml_args.sort()
        for i in range(len(tml_args)):
            if tml_args[i] != "arg" + str(i + 1):
                return (), ""
        tml_kwargs = []
        for seg in tml_split[1:]:
            kwargs = re.findall(r"\[(\w+)\]", seg)
            if len(kwargs) != 1:
                return (), ""
            tml_kwargs.extend(kwargs)
        return (fields[0], len(tml_args)) + tuple(tml_kwargs), fields[1]

    def imp_mod(self, mod, alias=""):
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(curr_dir, 'modules', mod + ".mod")
        if not os.path.exists(filename):
            return
        with open(filename, "r") as file:
            self.mod_list[mod] = {}
            if alias:
                self.mod_map[alias] = mod
            else:
                self.mod_map[mod] = mod
            line_cnt = 0
            for line in file:
                line_cnt += 1
                line = line.strip()
                if not line or line[0] == "#":
                    continue
                func_sign, func_tml = self.resolve(line)
                assert func_sign and func_tml, \
                       "Module file error: \"" + filename + "\", " + str(line_cnt)
                self.mod_list[mod][func_sign] = [func_tml, 0]

    def imp_func(self, mod, func, alias=""):
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(curr_dir, 'modules', mod + ".mod")
        if not os.path.exists(filename):
            return
        with open(filename, "r") as file:
            if not self.mod_list.has_key(mod):
                self.mod_list[mod] = {}
            line_cnt = 0
            for line in file:
                line_cnt += 1
                line = line.strip()
                if not line or line[0] == "#":
                    continue
                func_sign, func_tml = self.resolve(line)
                assert func_sign and func_tml, \
                       "Module file error: \"" + filename + "\", " + str(line_cnt)
                if func_sign[0] != func:
                    continue
                self.mod_list[mod][func_sign] = [func_tml, 0]
                if alias:
                    self.func_map[(alias,) + func_sign[1:]] = (mod, func_sign)
                else:
                    self.func_map[func_sign] = (mod, func_sign)

    def collect(self):
        self.statistics["stat_execs"] = {}
        self.statistics["stat_execs"]["_total_"] = 0
        for e in self.stat_execs:
            if self.stat_execs[e] > 0:
                self.statistics["stat_execs"][e] = self.stat_execs[e]
                self.statistics["stat_execs"]["_total_"] += self.stat_execs[e]

        self.statistics["func_calls"] = {}
        for m in self.mod_list:
            self.statistics["func_calls"][m] = {}
            self.statistics["func_calls"][m]["_total_"] = 0
            for s in self.mod_list[m]:
                if self.mod_list[m][s][1] > 0:
                    if not self.statistics["func_calls"][m].has_key(s[0]):
                        self.statistics["func_calls"][m][s[0]] = 0
                    self.statistics["func_calls"][m][s[0]] += self.mod_list[m][s][1]
                    self.statistics["func_calls"][m]["_total_"] += self.mod_list[m][s][1]
        self.statistics["func_calls"]["defined"] = {}
        self.statistics["func_calls"]["defined"]["_total_"] = 0
        for d in self.def_calls:
            if self.def_calls[d] > 0:
                self.statistics["func_calls"]["defined"][d] = self.def_calls[d]
                self.statistics["func_calls"]["defined"]["_total_"] += self.def_calls[d]
        self.statistics["func_calls"]["other"] = {}
        self.statistics["func_calls"]["other"]["_total_"] = self.other_calls


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
        self.import_module = True
        self.indent()
        self.write("Import ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)

    def _ImportFrom(self, t):
        # A from __future__ import may affect unparsing, so record it.
        if t.module and t.module == '__future__':
            self.future_imports.extend(n.name for n in t.names)

        self.import_module = False
        self.indent()
        self.write("From ")
        self.write("." * t.level)
        if t.module:
            self.write("module '" + t.module + "'")
            self.from_mod = t.module
        self.write(" import ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)
        self.from_mod = ""

    def _Assign(self, t):
        init = False
        if isinstance(t.targets[0], ast.Name):
            for target in t.targets:
                if not target.id in self.variables:
                    self.variables.append(target.id)
                    init = True
        elif isinstance(t.targets[0], ast.Tuple):
            for target in t.targets[0].elts:
                if not target.id in self.variables:
                    self.variables.append(target.id)
                    init = True

        if init:
            self.stat_execs["var_init"] = len(self.variables)
            self.indent()
            self.write("Initialise ")
            if isinstance(t.targets[0], ast.Name):
                if len(t.targets) == 1:
                    self.write("a variable ")
                else:
                    self.write("variables ")
                comma = False
                for target in t.targets:
                    if comma: self.write(", ")
                    else: comma = True
                    self.dispatch(target)
            else:
                for target in t.targets:
                    self.dispatch(t.targets)
            self.write(" to ")
            self.dispatch(t.value)
        else:
            self.indent()
            self.write("Assign ")
            self.dispatch(t.value)
            self.write(" to ")
            if isinstance(t.targets[0], ast.Name):
                if len(t.targets) == 1:
                    self.write("variable ")
                else:
                    self.write("variables ")
                comma = False
                for target in t.targets:
                    if comma: self.write(", ")
                    else: comma = True
                    self.dispatch(target)
            else:
                for target in t.targets:
                    self.dispatch(target)

        # code for function templates
        if (isinstance(t.value, ast.Name) and
            self.var_list.has_key(t.value.id)):
            if isinstance (t.targets[0], ast.Name):
                for target in t.targets:
                    self.var_list[target.id] = self.var_list[t.value.id]
            elif isinstance(t.targets[0], ast.Tuple):
                for target in t.targets[0].elts:
                    self.var_list[target.id] = self.var_list[t.value.id]

        # code for function templates
        if (isinstance(t.value, ast.Call) and
            isinstance(t.value.func, ast.Name)):
            if isinstance(t.targets[0], ast.Name):
                for target in t.targets:
                    self.var_list[target.id] = "built_in"
            elif isinstance(t.targets[0], ast.Tuple):
                for target in t.targets[0].elts:
                    self.var_list[target.id] = "built_in"

        # code for function templates
        if (isinstance(t.value, ast.Call) and
            isinstance(t.value.func, ast.Attribute) and
            isinstance(t.value.func.value, ast.Name) and
            self.mod_list.has_key(t.value.func.value.id)):
            if isinstance(t.targets[0], ast.Name):
                for target in t.targets:
                    self.var_list[target.id] = t.value.func.value.id
            elif isinstance(t.targets[0], ast.Tuple):
                for target in t.targets[0].elts:
                    self.var_list[target.id] = t.value.func.value.id

        # code for function templates
        if isinstance(t.value, ast.Tuple):
            for (value, target) in zip(t.value.elts, t.targets[0].elts):
                if (isinstance(value, ast.Name) and
                    self.var_list.has_key(value.id)):
                    self.var_list[target.id] = self.var_list[value.id]
                if (isinstance(value, ast.Call) and
                    isinstance(t.value.func, ast.Name)):
                    self.var_list[target.id] = "built_in"
                if (isinstance(value, ast.Call) and
                    isinstance(t.value.func, ast.Attribute) and
                    isinstance(t.value.func.value, ast.Name) and
                    self.mod_list.has_key(value.func.value.id)):
                    self.var_list[target.id] = value.func.value.id

    def _AugAssign(self, t):
        self.indent()
        self.write("The new value of ")
        self.dispatch(t.target)
        self.write(" is itself")
        self.write(" " + self.binop[t.op.__class__.__name__] + " ")
        self.dispatch(t.value)

    def _Return(self, t):
        self.indent()
        self.write("Return")
        if t.value:
            self.write(" ")
            self.dispatch(t.value)

    def _Break(self, t):
        self.indent()
        self.write("Break out of the current loop")

    def _Continue(self, t):
        self.indent()
        self.write("Skip the rest code inside the loop and continue with next iteration")

    def _Assert(self, t):
        self.indent()
        self.write("Check the condition of ")
        self.dispatch(t.test)
        self.write(" and if it is not ture, throw an exception ")
        if t.msg:
            self.write("with the message ")
            self.dispatch(t.msg)

    def _Print(self, t):
        self.indent()
        self.write("Print ")
        do_comma = False
        for e in t.values:
            if do_comma: self.write(", ")
            else: do_comma = True
            self.dispatch(e)
        self.write(" to the screen")

    def _ClassDef(self, t):
        # code for function dependency
        self.enter_comp()

        if not self.stat_execs.has_key("class_def"):
            self.stat_execs["class_def"] = 1
        else:
            self.stat_execs["class_def"] += 1

        self.indent()
        self.write("Define a class '" + t.name + "'")
        if t.bases:
            self.write(", which inherits from ")
            do_comma = False
            for a in t.bases:
                if do_comma: self.write(", ")
                else: do_comma = True
                self.dispatch(a)
        self.enter()
        self.dispatch(t.body)
        self.leave()

        # code for function dependency
        self.leave_comp()

    def _FunctionDef(self, t):
        # code for function dependency
        self.enter_def(t.name)

        if not self.stat_execs.has_key("func_def"):
            self.stat_execs["func_def"] = 1
        else:
            self.stat_execs["func_def"] += 1

        self.func_name = t.name
        self.def_calls[t.name] = 0
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
        if (isinstance(t.body[0], ast.Expr) and
            isinstance(t.body[0].value, ast.Str)):
            doc_str = ""
            first_line = True
            for line in ast.get_docstring(t).strip().split("\n"):
                doc_str += "    " * self.indents
                if first_line:
                    doc_str += "   "
                    first_line = False
                doc_str += line.strip()
                doc_str += "\n"
            self.docs_list[t.name] = doc_str
            self.dispatch(t.body[1:])
        else:
            self.dispatch(t.body)
        self.func_name = ""
        self.leave()

        # code for function dependency
        self.leave_def()

    def _For(self, t):
        # code for function dependency
        self.enter_comp()

        if not self.stat_execs.has_key("for_loop"):
            self.stat_execs["for_loop"] = 1
        else:
            self.stat_execs["for_loop"] += 1

        self.indent()
        self.write("Iterate variable ")
        self.dispatch(t.target)
        self.write(" over ")
        self.dispatch(t.iter)
        self.write(", and do the following")
        self.enter()
        self.dispatch(t.body)
        self.leave()

        # code for function dependency
        self.leave_comp()

    def _If(self, t):
        # code for function dependency
        self.enter_comp()

        if not self.stat_execs.has_key("if_else_stat"):
            self.stat_execs["if_else_stat"] = 1
        else:
            self.stat_execs["if_else_stat"] += 1

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
            self.write("Otherwise, if ")
            self.dispatch(t.test)
            self.write(", do the following")
            self.enter()
            self.dispatch(t.body)
            self.leave()
        # final else
        if t.orelse:
            self.newline()
            self.indent()
            self.write("Otherwise, do the following")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

        # code for function dependency
        self.leave_comp()

    def _While(self, t):
        # code for function dependency
        self.enter_comp()

        if not self.stat_execs.has_key("while_loop"):
            self.stat_execs["while_loop"] = 1
        else:
            self.stat_execs["while_loop"] += 1

        self.indent()
        self.write("While ")
        self.dispatch(t.test)
        self.write(", do the following")
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
        self.write("string ")
        if "unicode_literals" not in self.future_imports:
            self.write(repr(tree.s))
        elif isinstance(tree.s, str):
            self.write("b" + repr(tree.s))
        elif isinstance(tree.s, unicode):
            self.write(repr(tree.s).lstrip("u"))
        else:
            assert False, "shouldn't get here"

    def _Name(self, t):
        self.write("'")
        self.write(t.id)
        self.write("'")

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
        assert(t.elts) # should be at least one element
        self.write("set {")
        interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write("}")

    def _Dict(self, t):
        self.write("dictionary {")
        def write_pair(pair):
            (k, v) = pair
            self.dispatch(k)
            self.write(": ")
            self.dispatch(v)
        interleave(lambda: self.write(", "), write_pair, zip(t.keys, t.values))
        self.write("}")

    def _Tuple(self, t):
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
        self.write("'" + t.attr + "'")
        self.write(" on object ")
        self.dispatch(t.value)

    def _Call(self, t):
        # code for function dependency
        if isinstance(t.func, ast.Name):
            if t.func.id not in self.call_list:
                self.call_list.append(t.func.id)
        elif isinstance(t.func, ast.Attribute):
            if t.func.attr not in self.call_list:
                self.call_list.append(t.func.attr)

        # code for function templates
        func_tml = ""
        if isinstance(t.func, ast.Name):
            func_call = (t.func.id, len(t.args)) + tuple(k.arg for k in t.keywords)
            func_tml = self.get_tml("built_in", func_call)
        elif (isinstance(t.func, ast.Attribute) and
              isinstance(t.func.value, ast.Name)):
            if self.var_list.has_key(t.func.value.id):
                ref_mod = self.var_list[t.func.value.id]
            else:
                ref_mod = t.func.value.id
            func_call = (t.func.attr, len(t.args)) + tuple(k.arg for k in t.keywords)
            func_tml = self.get_tml(ref_mod, func_call)

        # code for function templates
        if func_tml:
            if (isinstance(t.func, ast.Attribute) and
                isinstance(t.func.value, ast.Name)):
                func_tml = func_tml.replace("[obj]", "'" + t.func.value.id + "'")
            tml_split = func_tml.split("|")
            tml_args = re.findall(r"\[(arg[0-9]+)\]", tml_split[0])
            for arg in tml_args:
                seg_split = tml_split[0].split("[" + arg + "]")
                self.write(seg_split[0])
                tml_split[0] = seg_split[1]
                self.dispatch(t.args[int(arg[3:]) - 1])
            self.write(tml_split[0])
            for seg in tml_split[1:]:
                res = re.search(r"\[(\w+)\]", seg)
                for e in t.keywords:
                    if e.arg == res.group(1):
                        seg_split = seg.split("[" + e.arg + "]")
                        self.write(seg_split[0])
                        self.dispatch(e.value)
                        self.write(seg_split[1])
        else:
            if self.direct_call:
                self.write("Call function ")
            else:
                self.write("return value of function ")
            if isinstance(t.func, ast.Name) and self.def_calls.has_key(t.func.id):
                self.def_calls[t.func.id] += 1
            else:
                self.other_calls += 1
            self.dispatch(t.func)
            if isinstance(t.func, ast.Name) and t.func.id == self.func_name:
                self.write(" recursively")
            # handle cases of no arguments
            if len(t.args) + len(t.keywords) == 0:
                self.write(" without arguments")
            elif len(t.args) + len(t.keywords) == 1:
                self.write(" with an argument ")
            else:
                self.write(" with arguments ")
            comma = False
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
        for a, d in zip(t.args, defaults):
            if first: first = False
            else: self.write(", ")
            self.dispatch(a)
            if d:
                self.write(" defaulted to ")
                self.dispatch(d)

    def _keyword(self, t):
        self.write("'" + t.arg + "'")
        self.write(" set to ")
        self.dispatch(t.value)

    def _alias(self, t):
        if self.import_module:
            self.write("module '" + t.name + "'")
            if t.asname:
                self.write(" as '" + t.asname + "'")
                self.imp_mod(t.name, t.asname)
            else:
                self.imp_mod(t.name)
        else:
            self.write("'" + t.name + "'")
            if t.asname:
                self.write(" as '" + t.asname + "'")
                self.imp_func(self.from_mod, t.name, t.asname)
            else:
                self.imp_func(self.from_mod, t.name)

def roundtrip(filename, output=sys.stdout, option=Option.both, mode=Mode.normal, level=Level.low):
    assert os.path.exists(filename), "File doesn't exist: \"" + filename + "\""
    with open(filename, "r") as pyfile:
        source = pyfile.read()
    tree = compile(source, filename, "exec", ast.PyCF_ONLY_AST)

    instructions, statistics = Unparser(tree, mode, level).run()
    if option != Option.statis:
        for i in instructions:
            output.write(i + "\n")

    if option != Option.instr:
        output.write("-" * 50 + "\n")

        output.write("stat_execs: " + str(statistics["stat_execs"]["_total_"]) + "\n")
        for e in statistics["stat_execs"]:
            if e == "_total_":
                continue
            output.write(" " * 4 + e + ": " + str(statistics["stat_execs"][e]) + "\n")

        output.write("-" * 50 + "\n")

        total = 0
        for m in statistics["func_calls"]:
            total += statistics["func_calls"][m]["_total_"]
        output.write("func_calls: " + str(total) + "\n")

        for m in statistics["func_calls"]:
            if m == "built_in" or m == "defined" or m == "other":
                continue
            output.write(" " * 4 + m + ": " + str(statistics["func_calls"][m]["_total_"]) + "\n")
            for f in statistics["func_calls"][m]:
                if f == "_total_":
                    continue
                output.write(" " * 8 + f + ": " + str(statistics["func_calls"][m][f]) + "\n")

        for m in ["built_in", "defined", "other"]:
            output.write(" " * 4 + m + ": "+ str(statistics["func_calls"][m]["_total_"]) + "\n")
            for f in statistics["func_calls"][m]:
                if f == "_total_":
                    continue
                output.write(" " * 8 + f + ": " + str(statistics["func_calls"][m][f]) + "\n")

        output.write("-" * 50 + "\n")

def main(argv):
    if len(argv) < 1:
        print __doc__
        return

    md = Mode.depend
    lv = Level.low
    for i in range(len(argv) - 1):
        if argv[i] == "-n":
            md = Mode.normal
        elif argv[i] == "-d":
            md = Mode.depend
        elif argv[i] == "-l":
            lv = Level.low
        elif argv[i] == "-h":
            lv = Level.high
    roundtrip(argv[-1], mode=md, level=lv)

if __name__ == '__main__':
    main(sys.argv[1:])
