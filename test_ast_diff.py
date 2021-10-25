import ast
import unittest

import ast_diff


class TestAstDiff(unittest.TestCase):
    def _test_differ(self, code1, code2, diff=None):
        if diff is None:
            self.assertIsNotNone(ast_diff.ast_diff(ast.parse(code1), ast.parse(code2)))
        else:
            self.assertEqual(ast_diff.ast_diff(ast.parse(code1), ast.parse(code2)), diff)

    def _test_same(self, code1, code2):
        self.assertIsNone(ast_diff.ast_diff(ast.parse(code1), ast.parse(code2)))

    def test_empty(self):
        self._test_same("", "")
        self._test_same(" ", "")
        self._test_same("", " ")
        self._test_same(" ", " ")
        self._test_same("#", "")
        self._test_same("", "#")
        self._test_same("#", "#")

    def test_global(self):
        self._test_same("global a", "global a")
        self._test_differ("global a", "global b",
                          ((1, 0), (1, 0), "ast.Global.names differ"))

    @unittest.skipUnless(ast_diff.py3, "ast.NonLocal is added in py3")
    def test_nonlocal(self):
        self._test_same("nonlocal a", "nonlocal a")
        self._test_differ("nonlocal a", "nonlocal b",
                          ((1, 0), (1, 0), "ast.Nonlocal.names differ"))

    def test_num(self):
        if ast_diff.py38:
            num_value = "ast.Constant.value"
        else:
            num_value = "ast.Num.n"
        self._test_same("0", "0")
        self._test_differ("0", "1",
                          ((1, 0), (1, 0), "%s differ 0 1" % num_value))

    def test_str(self):
        if ast_diff.py38:
            str_value = "ast.Constant.value"
        else:
            str_value = "ast.Str.s"
        self._test_same("'a'", "'a'")
        self._test_differ("'a'", "'b'",
                          ((1, 0), (1, 0), "%s differ a b" % str_value))

    @unittest.skipUnless(ast_diff.py3, "ast.JoinedStr is added in py3")
    def test_joinedstr(self):
        self._test_same("f'{a}'", "f'{a}'")
        self._test_differ("f'{3.14:10.10}'", "f'{3.14}'",
                          ((1, 0), (1, 0), "ast.FormattedValue.format_spec differ"))
        self._test_differ("f'{3.14!r:10.10}'", "f'{3.14!a:10.10}'",
                          ((1, 0), (1, 0), "ast.FormattedValue.conversion differ"))
        if ast_diff.py38:
            self._test_differ("'{a}'", "f'{a}'",
                              ((1, 0), (1, 0), "different type Constant JoinedStr"))
        else:
            self._test_differ("'{a}'", "f'{a}'",
                              ((1, 0), (1, 0), "different type Str JoinedStr"))
        self._test_differ("f'_{a}'", "f'{a}'",
                          ((1, 0), (1, 0), "length of ast.JoinedStr.values differ"))
        self._test_differ("f'{a}_'", "f'{a}'",
                          ((1, 0), (1, 0), "length of ast.JoinedStr.values differ"))
        self._test_differ("f'{a}'", "f'{a}{b}'",
                          ((1, 0), (1, 0), "length of ast.JoinedStr.values differ"))
        self._test_differ("f'{a}'", "f'{b}'",
                          ((1, 3), (1, 3), "ast.Name.id differ a b"))
        if ast_diff.py38:
            self._test_same("f'{a=}'", "f'{a=}'")
            self._test_differ("f'{a=}'", "f'{b=}'",
                              ((1, 0), (1, 0), "ast.Constant.value differ a= b="))

    @unittest.skipUnless(ast_diff.py3, "ast.Bytes is added in py3")
    def test_bytes(self):
        if ast_diff.py38:
            bytes_value = "ast.Constant.value"
        else:
            bytes_value = "ast.Bytes.s"
        self._test_same("b'a'", "b'a'")
        self._test_differ("b'a'", "b'b'",
                          ((1, 0), (1, 0), "%s differ b'a' b'b'" % bytes_value))

    def test_pass(self):
        self._test_same("pass", "pass")

    @unittest.skipUnless(ast_diff.py3, "ast.NameConst is added in py3")
    def test_nameconst(self):
        if ast_diff.py38:
            value = "ast.Constant.value"
        else:
            value = "ast.NameConstant.value"
        self._test_same("True", "True")
        self._test_differ("True", "False",
                          ((1, 0), (1, 0), "%s differ True False" % value))

    def test_module(self):
        self._test_same("pass", "pass")
        self._test_differ("pass\npass", "pass",
                          ((2, 0), None, "different type Pass NoneType"))
        self._test_differ("pass", "pass\npass",
                          (None, (2, 0), "different type NoneType Pass"))

    def test_expression(self):
        if ast_diff.py38:
            str_value = num_value = "ast.Constant.value"
        else:
            str_value = "ast.Str.s"
            num_value = "ast.Num.n"
        self._test_same("1", "1")
        self._test_differ("1", "2", ((1, 0), (1, 0), "%s differ 1 2" % num_value))
        self._test_same("'s'", "'s'")
        self._test_same("'s'", '"s"')
        self._test_same("'s'", '"""s"""')
        self._test_differ("'s'", "'t'", ((1, 0), (1, 0), "%s differ s t" % str_value))
        if ast_diff.py38:
            self._test_differ("1", "'s'", ((1, 0), (1, 0), "ast.Constant.value differ 1 s"))
        else:
            self._test_differ("1", "'s'", ((1, 0), (1, 0), "different type Num Str"))

    def test_assign(self):
        if ast_diff.py38:
            num_value = "ast.Constant.value"
        else:
            num_value = "ast.Num.n"
        self._test_same("a = 1", "a = 1")
        self._test_differ("a = 1", "b = 1", ((1, 0), (1, 0), "ast.Name.id differ a b"))
        self._test_differ("a = 1", "a = 2", ((1, 4), (1, 4), "%s differ 1 2" % num_value))
        self._test_same("a += 1", "a += 1")
        self._test_differ("a += 1", "a -= 1", ((1, 0), (1, 0), "ast.AugAssign.op differ Add Sub"))

    @unittest.skipUnless(ast_diff.py3, "ast.AnnAssign is added in py3")
    def test_annassign(self):
        self._test_same("a: x", "a: x")
        self._test_differ("a: x", "b: x",
                          ((1, 0), (1, 0), "ast.Name.id differ a b"))
        self._test_differ("a: x", "a: y",
                          ((1, 3), (1, 3), "ast.Name.id differ x y"))

    def test_call(self):
        self._test_same("int()", "int()")
        self._test_same("int(1)", "int(1)")
        self._test_differ("int()", "int(1)", ((1, 0), (1, 0), "length of ast.Call.args differ"))
        self._test_same("int(*[1])", "int(*[1])")
        if ast_diff.py3:
            self._test_differ("int()", "int(*[1])",
                              ((1, 0), (1, 0), "length of ast.Call.args differ"))
        else:
            self._test_differ("int()", "int(*[1])", ((1, 0), (1, 0), "ast.Call.starargs differ"))
        self._test_differ("int()", "float()", ((1, 0), (1, 0), "ast.Name.id differ int float"))
        self._test_same("func(a=1)", "func(a=1)")
        self._test_differ("func(a=1)", "func(a=1, b=1)",
                          ((1, 0), (1, 0), "length of ast.Call.keywords differ"))
        self._test_differ("func(a=1)", "func(b=1)", ((1, 0), (1, 0), "ast.Call.keywords differ"))

    def test_compare(self):
        if ast_diff.py38:
            num_value = "ast.Constant.value"
        else:
            num_value = "ast.Num.n"
        self._test_same("1 == 1", "1 == 1")
        self._test_same("1 != 1", "1 != 1")
        self._test_same("1 > 1", "1 > 1")
        self._test_same("1 < 1", "1 < 1")
        self._test_same("1 >= 1", "1 >= 1")
        self._test_same("1 <= 1", "1 <= 1")
        self._test_differ("1 == 1", "1 != 1", ((1, 0), (1, 0), "ast.Compare.ops differ"))
        self._test_differ("1 == 1", "2 == 1", ((1, 0), (1, 0), "%s differ 1 2" % num_value))
        self._test_differ("1 == 1", "1 == 2", ((1, 5), (1, 5), "%s differ 1 2" % num_value))

    def test_if(self):
        self._test_same("if t:\n    pass",
                        "if t:\n    pass")
        self._test_differ("if t:\n    pass",
                          "if f:\n    pass",
                          ((1, 3), (1, 3), "ast.Name.id differ t f"))
        self._test_differ("if t:\n    pass\n    pass",
                          "if t:\n    pass",
                          ((1, 0), (1, 0), "length of ast.If.body differ"))
        self._test_same("if t:\n    pass\nelse:\n    pass",
                        "if t:\n    pass\nelse:\n    pass")
        self._test_differ("if t:\n    pass",
                          "if t:\n    pass\nelse:\n    pass",
                          ((1, 0), (1, 0), "length of ast.If.orelse differ"))
        self._test_differ("if t:\n    pass\nelse:\n    pass\n    pass",
                          "if t:\n    pass\nelse:\n    pass",
                          ((1, 0), (1, 0), "length of ast.If.orelse differ"))

    def test_ifexp(self):
        self._test_same("1 if t else 0", "1 if t else 0")
        self._test_differ("1 if t else 0", "1 if f else 0",
                          ((1, 5), (1, 5), "ast.Name.id differ t f"))

    def test_while(self):
        self._test_same("while t:\n    pass",
                        "while t:\n    pass")
        self._test_same("while t:\n    continue",
                        "while t:\n    continue")
        self._test_same("while t:\n    break",
                        "while t:\n    break")
        self._test_differ("while t:\n    pass",
                          "while f:\n    pass",
                          ((1, 6), (1, 6), "ast.Name.id differ t f"))
        self._test_differ("while t:\n    pass\n    pass",
                          "while t:\n    pass",
                          ((1, 0), (1, 0), "length of ast.While.body differ"))
        self._test_same("while t:\n    pass\nelse:\n    pass",
                        "while t:\n    pass\nelse:\n    pass")
        self._test_differ("while t:\n    pass\nelse:\n    pass",
                          "while t:\n    pass",
                          ((1, 0), (1, 0), "length of ast.While.orelse differ"))
        self._test_differ("while t:\n    pass\nelse:\n    pass\n    pass",
                          "while t:\n    pass\nelse:\n    pass",
                          ((1, 0), (1, 0), "length of ast.While.orelse differ"))

    def test_for(self):
        self._test_same("for i in itr:\n    pass",
                        "for i in itr:\n    pass")
        self._test_differ("for i in itr:\n    pass\n    pass",
                          "for i in itr:\n    pass",
                          ((1, 0), (1, 0), "length of ast.For.body differ"))
        self._test_same("for i in itr:\n    pass\nelse:\n    pass",
                        "for i in itr:\n    pass\nelse:\n    pass")
        self._test_differ("for i in itr:\n    pass",
                          "for i in itr:\n    pass\nelse:\n    pass",
                          ((1, 0), (1, 0), "length of ast.For.orelse differ"))
        self._test_differ("for i in itr:\n    pass\nelse:\n    pass\n    pass",
                          "for i in itr:\n    pass\nelse:\n    pass",
                          ((1, 0), (1, 0), "length of ast.For.orelse differ"))
        self._test_differ("for i in itr1:\n    pass",
                          "for i in itr2:\n    pass",
                          ((1, 9), (1, 9), "ast.Name.id differ itr1 itr2"))

    @unittest.skipUnless(ast_diff.py3, "ast.AsyncFor is added in py3")
    def test_asyncfor(self):
        self._test_same("async for i in itr:\n    pass",
                        "async for i in itr:\n    pass")
        self._test_differ("async for i in itr:\n    pass\n    pass",
                          "async for i in itr:\n    pass",
                          ((1, 0), (1, 0), "length of ast.AsyncFor.body differ"))
        self._test_same("async for i in itr:\n    pass\nelse:\n    pass",
                        "async for i in itr:\n    pass\nelse:\n    pass")
        self._test_differ("async for i in itr:\n    pass",
                          "async for i in itr:\n    pass\nelse:\n    pass",
                          ((1, 0), (1, 0), "length of ast.AsyncFor.orelse differ"))
        self._test_differ("async for i in itr:\n    pass\nelse:\n    pass\n    pass",
                          "async for i in itr:\n    pass\nelse:\n    pass",
                          ((1, 0), (1, 0), "length of ast.AsyncFor.orelse differ"))
        self._test_differ("async for i in itr1:\n    pass",
                          "async for i in itr2:\n    pass",
                          ((1, 15), (1, 15), "ast.Name.id differ itr1 itr2"))

    def test_operator(self):
        self._test_same("1 + 1", "1 + 1")
        self._test_differ("1 + 1", "1 - 1",
                          ((1, 0), (1, 0), "ast.BinOp.op differ Add Sub"))

    def test_boolean_operator(self):
        self._test_same("True and True", "True and True")
        self._test_differ("True and True", "True or True",
                          ((1, 0), (1, 0), "ast.BoolOp.op differ And Or"))

    def test_subscript(self):
        if ast_diff.py38:
            str_value = num_value = "ast.Constant.value"
        else:
            str_value = "ast.Str.s"
            num_value = "ast.Num.n"
        self._test_same("a[0]", "a[0]")
        self._test_differ("a[0]", "b[0]", ((1, 0), (1, 0), "ast.Name.id differ a b"))
        self._test_differ("a[0]", "a[1]", ((1, 2), (1, 2), "%s differ 0 1" % num_value))
        if ast_diff.py39:
            self._test_differ("a[0]", "a[:]",
                              ((1, 0), (1, 0),
                               "type of ast.Subscript.slice differ Constant Slice"))
        else:
            self._test_differ("a[0]", "a[:]",
                              ((1, 0), (1, 0), "type of ast.Subscript.slice differ Index Slice"))
        self._test_same("a[:]", "a[:]")
        self._test_differ("a[:]", "a[0:]", ((1, 0), (1, 0), "ast.Subscript.slice.lower differ"))
        self._test_differ("a[:]", "a[:0]", ((1, 0), (1, 0), "ast.Subscript.slice.upper differ"))
        self._test_differ("a[:]", "a[::1]", ((1, 0), (1, 0), "ast.Subscript.slice.step differ"))
        self._test_same("a['x']", "a['x']")
        self._test_differ("a['x']", "a['y']", ((1, 2), (1, 2), "%s differ x y" % str_value))
        if ast_diff.py38:
            self._test_differ("a[0]", "a['x']",
                              ((1, 2), (1, 2), "ast.Constant.value differ 0 x"))
        else:
            self._test_differ("a[0]", "a['x']",
                              ((1, 2), (1, 2), "different type Num Str"))
        self._test_same("a[x]", "a[x]")
        self._test_differ("a[x]", "a[y]", ((1, 2), (1, 2), "ast.Name.id differ x y"))
        if ast_diff.py39:
            self._test_differ("a[0]", "a[x]",
                              ((1, 0), (1, 0), "type of ast.Subscript.slice differ Constant Name"))
        elif ast_diff.py38:
            self._test_differ("a[0]", "a[x]",
                              ((1, 2), (1, 2), "different type Constant Name"))
        else:
            self._test_differ("a[0]", "a[x]",
                              ((1, 2), (1, 2), "different type Num Name"))

    def test_delete(self):
        self._test_same("del a[0]", "del a[0]")
        self._test_same("del a[:]", "del a[:]")

    def test_import(self):
        self._test_same("import m", "import m")
        self._test_differ("import m", "import m, n",
                          ((1, 0), (1, 0), "length of ast.Import.names differ"))
        self._test_differ("import m", "import n",
                          ((1, 0), (1, 0), "ast.alias.name differ m n"))
        self._test_differ("import m as a", "import n as a",
                          ((1, 0), (1, 0), "ast.alias.name differ m n"))
        self._test_same("import m as a", "import m as a")
        self._test_differ("import m as a", "import m as b",
                          ((1, 0), (1, 0), "ast.alias.asname differ a b"))

    def test_importfrom(self):
        self._test_same("from m import a", "from m import a")
        self._test_differ("from m import a", "from n import a",
                          ((1, 0), (1, 0), "ast.ImportFrom.module differ m n"))
        self._test_differ("from m import a", "from m import a,b",
                          ((1, 0), (1, 0), "length of ast.ImportFrom.names differ"))
        self._test_differ("from m import a", "from m import b",
                          ((1, 0), (1, 0), "ast.alias.name differ a b"))
        self._test_same("from m import a as b", "from m import a as b")
        self._test_differ("from m import a as b", "from m import a as c",
                          ((1, 0), (1, 0), "ast.alias.asname differ b c"))

    def test_dict(self):
        self._test_same("{}", "{}")
        self._test_same("{k: v}", "{k: v}")
        self._test_differ("{k1: v}", "{k2: v}",
                          ((1, 1), (1, 1), "ast.Name.id differ k1 k2"))
        self._test_differ("{k: v1}", "{k: v2}",
                          ((1, 4), (1, 4), "ast.Name.id differ v1 v2"))

    def test_list(self):
        self._test_same("[]", "[]")
        self._test_same("[a]", "[a]")
        self._test_differ("[a]", "[a,b]",
                          ((1, 0), (1, 0), "length of ast.List.elts differ"))
        self._test_differ("[a]", "[b]",
                          ((1, 1), (1, 1), "ast.Name.id differ a b"))

    def test_set(self):
        self._test_same("{a}", "{a}")
        self._test_differ("{a}", "{a, b}",
                          ((1, 0), (1, 0), "length of ast.Set.elts differ"))
        self._test_differ("{a}", "{b}",
                          ((1, 1), (1, 1), "ast.Name.id differ a b"))

    def test_tuple(self):
        self._test_same("()", "()")
        if ast_diff.py38:
            col = 0
        else:
            col = 1
        self._test_differ("()", "(a,)",
                          ((1, 0), (1, col), "length of ast.Tuple.elts differ"))
        self._test_differ("(a,)", "(b,)",
                          ((1, 1), (1, 1), "ast.Name.id differ a b"))

    def test_raise(self):
        self._test_same("raise", "raise")
        if ast_diff.py3:
            self._test_differ("raise a", "raise",
                              ((1, 0), (1, 0), "ast.Raise.exc differ"))
        else:
            self._test_differ("raise a", "raise",
                              ((1, 0), (1, 0), "ast.Raise.type differ"))
        self._test_same("raise a", "raise a")
        self._test_differ("raise a", "raise b",
                          ((1, 6), (1, 6), "ast.Name.id differ a b"))

    @unittest.skipUnless(ast_diff.py3, "raise from syntax is added in py3")
    def test_raise_from(self):
        self._test_same("raise a from x", "raise a from x")
        self._test_differ("raise a from x", "raise a",
                          ((1, 0), (1, 0), "ast.Raise.cause differ"))
        self._test_differ("raise a from x", "raise a",
                          ((1, 0), (1, 0), "ast.Raise.cause differ"))

    def test_return(self):
        self._test_same("return", "return")
        self._test_differ("return a", "return",
                          ((1, 0), (1, 0), "ast.Return.value differ"))
        self._test_same("return a", "return a")
        self._test_differ("return a", "return b",
                          ((1, 7), (1, 7), "ast.Name.id differ a b"))

    def test_with(self):
        if ast_diff.py3:
            col = 0
        else:
            col = 5
        self._test_same("with a:\n    pass", "with a:\n    pass")
        if ast_diff.py3:
            self._test_differ("with a:\n    pass", "with a, b:\n    pass",
                              ((1, 0), (1, 0), "length of ast.With.items differ"))
        else:
            self._test_differ("with a:\n    pass", "with a, b:\n    pass",
                              (((2, 4), (1, 8), "different type Pass With")))
        self._test_same("with a as x:\n    pass", "with a as x:\n    pass")
        if ast_diff.py3:
            self._test_differ("with a as x:\n    pass", "with a:\n    pass",
                              ((1, 0), (1, 0), "ast.With.items[0].optional_vars differ"))
        else:
            self._test_differ("with a as x:\n    pass", "with a:\n    pass",
                              ((1, 5), (1, 5), "ast.With.optional_vars differ"))
        self._test_differ("with a:\n    pass", "with b:\n    pass",
                          ((1, 5), (1, 5), "ast.Name.id differ a b"))
        self._test_differ("with a as x:\n    pass", "with a as y:\n    pass",
                          ((1, 10), (1, 10), "ast.Name.id differ x y"))
        self._test_differ("with a:\n    pass\n    pass",
                          "with a:\n    pass",
                          ((1, col), (1, col), "length of ast.With.body differ"))

    @unittest.skipUnless(ast_diff.py3, "ast.AsyncWith is added in py3")
    def test_asyncwith(self):
        self._test_same("async with a:\n    pass", "async with a:\n    pass")
        self._test_differ("async with a:\n    pass", "async with a, b:\n    pass",
                          ((1, 0), (1, 0), "length of ast.AsyncWith.items differ"))
        self._test_same("async with a as x:\n    pass", "async with a as x:\n    pass")
        self._test_differ("async with a as x:\n    pass", "async with a:\n    pass",
                          ((1, 0), (1, 0), "ast.AsyncWith.items[0].optional_vars differ"))
        self._test_differ("async with a:\n    pass", "async with b:\n    pass",
                          ((1, 11), (1, 11), "ast.Name.id differ a b"))
        self._test_differ("async with a as x:\n    pass", "async with a as y:\n    pass",
                          ((1, 16), (1, 16), "ast.Name.id differ x y"))
        self._test_differ("async with a:\n    pass\n    pass",
                          "async with a:\n    pass",
                          ((1, 0), (1, 0), "length of ast.AsyncWith.body differ"))

    def test_assert(self):
        self._test_same("assert x", "assert x")
        self._test_differ("assert x", "assert y",
                          ((1, 7), (1, 7), "ast.Name.id differ x y"))
        self._test_differ("assert x, m1", "assert x, m2",
                          ((1, 10), (1, 10), "ast.Name.id differ m1 m2"))

    @unittest.skipIf(ast_diff.py3, "ast.Print is removed in py3")
    def test_print(self):
        self._test_same("print a", "print a")
        self._test_same("print a,b", "print a,b")
        self._test_differ("print a", "print b",
                          ((1, 6), (1, 6), "ast.Name.id differ a b"))

    @unittest.skipIf(ast_diff.py3, "ast.Exec is removed in py3")
    def test_exec(self):
        self._test_same("exec 'a'", "exec 'a'")
        self._test_differ("exec 'a'", "exec 'b'",
                          ((1, 5), (1, 5), "ast.Str.s differ a b"))
        self._test_differ("exec 'a' in {}", "exec 'a'",
                          ((1, 0), (1, 0), "ast.Exec.globals differ"))
        self._test_differ("exec 'a' in {}, {}", "exec 'a' in {}",
                          ((1, 0), (1, 0), "ast.Exec.locals differ"))

    @unittest.skipIf(ast_diff.py3, "ast.Repr is removed in py3")
    def test_repr(self):
        self._test_same("`x`", "`x`")
        self._test_differ("`x`", "`y`",
                          ((1, 1), (1, 1), "ast.Name.id differ x y"))

    def test_in(self):
        self._test_same("a in x", "a in x")
        self._test_differ("a in x", "b in x",
                          ((1, 0), (1, 0), "ast.Name.id differ a b"))
        self._test_differ("a in x", "a in y",
                          ((1, 5), (1, 5), "ast.Name.id differ x y"))
        self._test_same("a not in x", "a not in x")
        self._test_differ("a not in x", "b not in x",
                          ((1, 0), (1, 0), "ast.Name.id differ a b"))
        self._test_differ("a not in x", "a not in y",
                          ((1, 9), (1, 9), "ast.Name.id differ x y"))

    def test_not(self):
        self._test_same("not a", "not a")
        self._test_same("~a", "~a")
        self._test_differ("not a", "~a",
                          ((1, 0), (1, 0), "ast.UnaryOp.op differ Not Invert"))

    def test_lambda(self):
        self._test_same("lambda a: x", "lambda a: x")
        if ast_diff.py3:
            self._test_differ("lambda a: x", "lambda b: x",
                              ((1, 7), (1, 7), "ast.arg.arg differ a b"))
        else:
            self._test_differ("lambda a: x", "lambda b: x",
                              ((1, 7), (1, 7), "ast.Name.id differ a b"))
        self._test_differ("lambda a: x", "lambda a,b: x",
                          ((1, 0), (1, 0), "length of ast.Lambda.args.args differ"))
        self._test_differ("lambda a,b: x", "lambda a,b=0: x",
                          ((1, 0), (1, 0), "length of ast.Lambda.args.defaults differ"))
        self._test_differ("lambda a: x", "lambda a: y",
                          ((1, 10), (1, 10), "ast.Name.id differ x y"))
        self._test_same("lambda *a: x", "lambda *a: x")
        self._test_differ("lambda a,*b: x", "lambda a: x",
                          ((1, 0), (1, 0), "ast.Lambda.args.vararg differ"))
        self._test_same("lambda **a: x", "lambda **a: x")
        self._test_differ("lambda a,**b: x", "lambda a: x",
                          ((1, 0), (1, 0), "ast.Lambda.args.kwarg differ"))

    def test_def(self):
        if ast_diff.py38:
            line_with_decorator = 2
        else:
            line_with_decorator = 1
        self._test_same("def a():\n    pass", "def a():\n    pass")
        self._test_same("@deco\ndef a():\n    pass", "@deco\ndef a():\n    pass")
        self._test_differ("@deco\ndef a():\n    pass", "def a():\n    pass",
                          ((line_with_decorator, 0), (1, 0),
                           "length of ast.FunctionDef.decorator_list differ"))
        self._test_differ("@deco1\ndef a():\n    pass", "@deco2\ndef a():\n    pass",
                          ((1, 1), (1, 1), "ast.Name.id differ deco1 deco2"))
        self._test_differ("def a():\n    pass", "def b():\n    pass",
                          ((1, 0), (1, 0), "ast.FunctionDef.name differ a b"))
        self._test_differ("def a(x):\n    pass", "def a():\n    pass",
                          ((1, 0), (1, 0), "length of ast.FunctionDef.args.args differ"))
        if ast_diff.py3:
            self._test_differ("def a(x):\n    pass", "def a(y):\n    pass",
                              ((1, 6), (1, 6), "ast.arg.arg differ x y"))
        else:
            self._test_differ("def a(x):\n    pass", "def a(y):\n    pass",
                              ((1, 6), (1, 6), "ast.Name.id differ x y"))
        self._test_differ("def a(x):\n    pass", "def a(x=z):\n    pass",
                          ((1, 0), (1, 0), "length of ast.FunctionDef.args.defaults differ"))
        self._test_differ("def a(*x):\n    pass", "def a():\n    pass",
                          ((1, 0), (1, 0), "ast.FunctionDef.args.vararg differ"))
        self._test_differ("def a(**x):\n    pass", "def a():\n    pass",
                          ((1, 0), (1, 0), "ast.FunctionDef.args.kwarg differ"))
        self._test_differ("def a():\n    pass\n    pass",
                          "def a():\n    pass",
                          ((1, 0), (1, 0), "length of ast.FunctionDef.body differ"))

    @unittest.skipUnless(ast_diff.py3, "kwonlyargs is added in py3")
    def test_def_kwonlyargs(self):
        self._test_same("def a(*, b):\n    pass", "def a(*, b):\n    pass")
        self._test_differ("def a(*, b):\n    pass", "def a(*, b, c):\n    pass",
                          ((1, 0), (1, 0), "length of ast.FunctionDef.args.kwonlyargs differ"))
        self._test_differ("def a(*, b):\n    pass", "def a(*, c):\n    pass",
                          ((1, 0), (1, 0), "ast.FunctionDef.args.kwonlyargs[0].arg differ b c"))
        self._test_differ("def a(*, b=x):\n    pass", "def a(*, b):\n    pass",
                          ((1, 0), (1, 0), "ast.FunctionDef.args.kw_defaults differ"))
        self._test_differ("def a(*, b=x):\n    pass", "def a(*, b=y):\n    pass",
                          ((1, 11), (1, 11), "ast.Name.id differ x y"))

    @unittest.skipUnless(ast_diff.py3, "kwonlyargs is added in py3")
    def test_lambda_kwonlyargs(self):
        self._test_same("lambda *, b: x", "lambda *, b: x")
        self._test_differ("lambda *, b: x", "lambda *, b, c: x",
                          ((1, 0), (1, 0), "length of ast.Lambda.args.kwonlyargs differ"))
        self._test_differ("lambda *, b: x", "lambda *, c: x",
                          ((1, 0), (1, 0), "ast.Lambda.args.kwonlyargs[0].arg differ b c"))
        self._test_differ("lambda *, b=p: x", "lambda *, b: x",
                          ((1, 0), (1, 0), "ast.Lambda.args.kw_defaults differ"))
        self._test_differ("lambda *, b=p: x", "lambda *, b=q: x",
                          ((1, 12), (1, 12), "ast.Name.id differ p q"))

    @unittest.skipUnless(ast_diff.py38, "postonlyargs is added in py38")
    def test_def_posonlyargs(self):
        self._test_same("def f(a, /):\n    pass", "def f(a, /):\n    pass")
        self._test_differ("def f(a, /):\n    pass", "def f(a, b, /):\n    pass",
                          ((1, 0), (1, 0), "length of ast.FunctionDef.args.posonlyargs differ"))
        self._test_differ("def f(a, /):\n    pass", "def f(b, /):\n    pass",
                          ((1, 0), (1, 0), "ast.FunctionDef.args.posonlyargs[0].arg differ a b"))
        self._test_same("def f(a=p, /):\n    pass", "def f(a=p, /):\n    pass")
        self._test_differ("def f(a=p, /):\n    pass", "def f(a, /):\n    pass",
                          ((1, 0), (1, 0), "length of ast.FunctionDef.args.defaults differ"))
        self._test_differ("def f(a=p, /):\n    pass", "def f(a=q, /):\n    pass",
                          ((1, 8), (1, 8), "ast.Name.id differ p q"))

    @unittest.skipUnless(ast_diff.py38, "postonlyargs is added in py38")
    def test_lambda_posonlyargs(self):
        self._test_same("lambda a, /: x", "lambda a, /: x")
        self._test_differ("lambda a, /: x", "lambda a, b, /: x",
                          ((1, 0), (1, 0), "length of ast.Lambda.args.posonlyargs differ"))
        self._test_differ("lambda a, /: x", "lambda b, /: x",
                          ((1, 0), (1, 0), "ast.Lambda.args.posonlyargs[0].arg differ a b"))
        self._test_same("lambda a=p, /: x", "lambda a=p, /: x")
        self._test_differ("lambda a=p, /: x", "lambda a, /: x",
                          ((1, 0), (1, 0), "length of ast.Lambda.args.defaults differ"))
        self._test_differ("lambda a=p, /: x", "lambda a=q, /: x",
                          ((1, 9), (1, 9), "ast.Name.id differ p q"))

    @unittest.skipUnless(ast_diff.py3, "ast.AsyncDef is added in py3")
    def test_asyncdef(self):
        if ast_diff.py38:
            line_with_decorator = 2
        else:
            line_with_decorator = 1
        self._test_same("async def f():\n    pass", "async def f():\n    pass")
        self._test_same("@deco\nasync def a():\n    pass", "@deco\nasync def a():\n    pass")
        self._test_differ("@deco\nasync def a():\n    pass", "async def a():\n    pass",
                          ((line_with_decorator, 0), (1, 0),
                           "length of ast.AsyncFunctionDef.decorator_list differ"))
        self._test_differ("@deco1\nasync def a():\n    pass", "@deco2\nasync def a():\n    pass",
                          ((1, 1), (1, 1), "ast.Name.id differ deco1 deco2"))
        self._test_differ("async def a():\n    pass", "async def b():\n    pass",
                          ((1, 0), (1, 0), "ast.AsyncFunctionDef.name differ a b"))
        self._test_differ("async def a(x):\n    pass", "async def a():\n    pass",
                          ((1, 0), (1, 0), "length of ast.AsyncFunctionDef.args.args differ"))
        self._test_differ("async def a(x):\n    pass", "async def a(y):\n    pass",
                          ((1, 12), (1, 12), "ast.arg.arg differ x y"))
        self._test_differ("async def a(x):\n    pass", "async def a(x=z):\n    pass",
                          ((1, 0), (1, 0), "length of ast.AsyncFunctionDef.args.defaults differ"))
        self._test_differ("async def a(*x):\n    pass", "async def a():\n    pass",
                          ((1, 0), (1, 0), "ast.AsyncFunctionDef.args.vararg differ"))
        self._test_differ("async def a(**x):\n    pass", "async def a():\n    pass",
                          ((1, 0), (1, 0), "ast.AsyncFunctionDef.args.kwarg differ"))
        self._test_differ("async def a():\n    pass\n    pass",
                          "async def a():\n    pass",
                          ((1, 0), (1, 0), "length of ast.AsyncFunctionDef.body differ"))

    @unittest.skipUnless(ast_diff.py3, "typing support is added in py3")
    def test_typing(self):
        self._test_same("def a(b: s):\n    pass", "def a(b: s):\n    pass")
        self._test_differ("def a(b: s):\n    pass", "def a(b: t):\n    pass",
                          ((1, 9), (1, 9), "ast.Name.id differ s t"))
        self._test_differ("def a(b: t):\n    pass", "def a(b):\n    pass",
                          ((1, 6), (1, 6), "ast.arg.annotation differ"))
        self._test_same("def a(b) -> s:\n    pass", "def a(b) -> s:\n    pass")
        self._test_differ("def a(b) -> s:\n    pass", "def a(b) -> t:\n    pass",
                          ((1, 12), (1, 12), "ast.Name.id differ s t"))
        self._test_differ("def a(b) -> s:\n    pass", "def a(b):\n    pass",
                          ((1, 0), (1, 0), "ast.FunctionDef.returns differ"))

    def test_attr(self):
        self._test_same("a.x", "a.x")
        self._test_differ("a.x", "b.x",
                          ((1, 0), (1, 0), "ast.Name.id differ a b"))
        self._test_differ("a.x", "a.y",
                          ((1, 0), (1, 0), "ast.Attribute.attr differ x y"))
        self._test_same("a.p.x", "a.p.x")
        self._test_differ("a.p.x", "a.q.x",
                          ((1, 0), (1, 0), "ast.Attribute.attr differ p q"))
        self._test_differ("a.p.x", "a.p.y",
                          ((1, 0), (1, 0), "ast.Attribute.attr differ x y"))

    def test_listcomp(self):
        if ast_diff.py38:
            col = 0
        else:
            col = 1
        self._test_same("[p for a in x]", "[p for a in x]")
        self._test_differ("[p for a in x]", "[p for a in x for b in y]",
                          ((1, col), (1, col), "length of ast.ListComp.generators differ"))
        self._test_differ("[p for a in x]", "[q for a in x]",
                          ((1, 1), (1, 1), "ast.Name.id differ p q"))
        self._test_differ("[p for a in x]", "[p for b in x]",
                          ((1, 7), (1, 7), "ast.Name.id differ a b"))
        self._test_differ("[p for a in x]", "[p for a in y]",
                          ((1, 12), (1, 12), "ast.Name.id differ x y"))
        self._test_same("[p for a in x if s]", "[p for a in x if s]")
        self._test_differ("[p for a in x if s]", "[p for a in x if s if t]",
                          ((1, col), (1, col), "length of ast.comprehension.ifs differ"))
        self._test_differ("[p for a in x if s]", "[p for a in x if t]",
                          ((1, 17), (1, 17), "ast.Name.id differ s t"))

    def test_genexp(self):
        if ast_diff.py38:
            col = 0
        else:
            col = 1
        self._test_same("(p for a in x)", "(p for a in x)")
        self._test_differ("(p for a in x)", "(p for a in x for b in y)",
                          ((1, col), (1, col), "length of ast.GeneratorExp.generators differ"))
        self._test_differ("(p for a in x)", "(q for a in x)",
                          ((1, 1), (1, 1), "ast.Name.id differ p q"))
        self._test_differ("(p for a in x)", "(p for b in x)",
                          ((1, 7), (1, 7), "ast.Name.id differ a b"))
        self._test_differ("(p for a in x)", "(p for a in y)",
                          ((1, 12), (1, 12), "ast.Name.id differ x y"))
        self._test_same("(p for a in x if s)", "(p for a in x if s)")
        self._test_differ("(p for a in x if s)", "(p for a in x if s if t)",
                          ((1, col), (1, col), "length of ast.comprehension.ifs differ"))
        self._test_differ("(p for a in x if s)", "(p for a in x if t)",
                          ((1, 17), (1, 17), "ast.Name.id differ s t"))

    def test_setcomp(self):
        if ast_diff.py3:
            col = 0
        else:
            col = 1
        self._test_same("{p for a in x}", "{p for a in x}")
        self._test_differ("{p for a in x}", "{p for a in x for b in y}",
                          ((1, col), (1, col), "length of ast.SetComp.generators differ"))
        self._test_differ("{p for a in x}", "{q for a in x}",
                          ((1, 1), (1, 1), "ast.Name.id differ p q"))
        self._test_differ("{p for a in x}", "{p for b in x}",
                          ((1, 7), (1, 7), "ast.Name.id differ a b"))
        self._test_differ("{p for a in x}", "{p for a in y}",
                          ((1, 12), (1, 12), "ast.Name.id differ x y"))
        self._test_same("{p for a in x if s}", "{p for a in x if s}")
        self._test_differ("{p for a in x if s}", "{p for a in x if s if t}",
                          ((1, col), (1, col), "length of ast.comprehension.ifs differ"))
        self._test_differ("{p for a in x if s}", "{p for a in x if t}",
                          ((1, 17), (1, 17), "ast.Name.id differ s t"))

    def test_dictcomp(self):
        if ast_diff.py3:
            col = 0
        else:
            col = 1
        self._test_same("{k:v for a in x}", "{k:v for a in x}")
        self._test_differ("{k:v for a in x}", "{k:v for a in x for b in y}",
                          ((1, col), (1, col), "length of ast.DictComp.generators differ"))
        self._test_differ("{k1:v for a in x}", "{k2:v for a in x}",
                          ((1, 1), (1, 1), "ast.Name.id differ k1 k2"))
        self._test_differ("{k:v1 for a in x}", "{k:v2 for a in x}",
                          ((1, 3), (1, 3), "ast.Name.id differ v1 v2"))
        self._test_differ("{k:v for a in x}", "{k:v for b in x}",
                          ((1, 9), (1, 9), "ast.Name.id differ a b"))
        self._test_differ("{k:v for a in x}", "{k:v for a in y}",
                          ((1, 14), (1, 14), "ast.Name.id differ x y"))
        self._test_same("{k:v for a in x if s}", "{k:v for a in x if s}")
        self._test_differ("{k:v for a in x if s}", "{k:v for a in x if s if t}",
                          ((1, col), (1, col), "length of ast.comprehension.ifs differ"))
        self._test_differ("{k:v for a in x if s}", "{k:v for a in x if t}",
                          ((1, 19), (1, 19), "ast.Name.id differ s t"))

    def test_class(self):
        if ast_diff.py38:
            line_with_decorator = 2
        else:
            line_with_decorator = 1
        self._test_same("class c:\n    pass", "class c:\n    pass")
        self._test_same("@deco\nclass c:\n    pass", "@deco\nclass c:\n    pass")
        self._test_differ("@deco\nclass c:\n    pass", "class c:\n    pass",
                          ((line_with_decorator, 0), (1, 0),
                           "length of ast.ClassDef.decorator_list differ"))
        self._test_differ("@deco1\nclass c:\n    pass", "@deco2\nclass c:\n    pass",
                          ((1, 1), (1, 1), "ast.Name.id differ deco1 deco2"))
        self._test_differ("class c:\n    pass", "class d:\n    pass",
                          ((1, 0), (1, 0), "ast.ClassDef.name differ c d"))
        self._test_differ("class c(a):\n    pass", "class c:\n    pass",
                          ((1, 0), (1, 0), "length of ast.ClassDef.bases differ"))
        self._test_differ("class c(a):\n    pass", "class c(b):\n    pass",
                          ((1, 8), (1, 8), "ast.Name.id differ a b"))
        self._test_differ("class c:\n    pass\n    pass",
                          "class c:\n    pass",
                          ((1, 0), (1, 0), "length of ast.ClassDef.body differ"))

    @unittest.skipUnless(ast_diff.py3, "ast.Try is added in py3")
    def test_try(self):
        self._test_same("try:\n    pass\nexcept:\n    pass",
                        "try:\n    pass\nexcept:\n    pass")
        self._test_differ("try:\n    pass\n    pass\nexcept:\n    pass",
                          "try:\n    pass\nexcept:\n    pass",
                          ((1, 0), (1, 0), "length of ast.Try.body differ"))
        self._test_same("try:\n    pass\nexcept a:\n    pass",
                        "try:\n    pass\nexcept a:\n    pass")
        self._test_differ("try:\n    pass\nexcept a:\n    pass\nexcept b:\n    pass",
                          "try:\n    pass\nexcept a:\n    pass",
                          ((1, 0), (1, 0), "length of ast.Try.handlers differ"))
        self._test_differ("try:\n    pass\nexcept a:\n    pass",
                          "try:\n    pass\nexcept b:\n    pass",
                          ((3, 7), (3, 7), "ast.Name.id differ a b"))
        self._test_differ("try:\n    pass\nexcept a:\n    pass",
                          "try:\n    pass\nexcept:\n    pass",
                          ((3, 0), (3, 0), "ast.ExceptHandler.type differ"))
        self._test_same("try:\n    pass\nexcept a as x:\n    pass",
                        "try:\n    pass\nexcept a as x:\n    pass")
        self._test_differ("try:\n    pass\nexcept a as x:\n    pass",
                          "try:\n    pass\nexcept a:\n    pass",
                          ((3, 0), (3, 0), "ast.ExceptHandler.name differ"))
        self._test_differ("try:\n    pass\nexcept a as x:\n    pass",
                          "try:\n    pass\nexcept a as y:\n    pass",
                          ((3, 0), (3, 0), "ast.ExceptHandler.name differ"))
        self._test_differ("try:\n    pass\nexcept:\n    pass\n    pass",
                          "try:\n    pass\nexcept:\n    pass",
                          ((3, 0), (3, 0), "length of ast.ExceptHandler.body differ"))
        self._test_same("try:\n    pass\nexcept:\n    pass\nelse:\n    pass",
                        "try:\n    pass\nexcept:\n    pass\nelse:\n    pass")
        self._test_differ("try:\n    pass\nexcept:\n    pass\nelse:\n    pass\n    pass",
                          "try:\n    pass\nexcept:\n    pass\nelse:\n    pass",
                          ((1, 0), (1, 0), "length of ast.Try.orelse differ"))
        self._test_same("try:\n    pass\nfinally:\n    pass",
                        "try:\n    pass\nfinally:\n    pass")
        self._test_differ("try:\n    pass\nfinally:\n    pass\n    pass",
                          "try:\n    pass\nfinally:\n    pass",
                          ((1, 0), (1, 0), "length of ast.Try.finalbody differ"))

    @unittest.skipIf(ast_diff.py3, "ast.TryExcept is removed (and ast.Try is added) in py3")
    def test_tryexcept(self):
        self._test_same("try:\n    pass\nexcept:\n    pass",
                        "try:\n    pass\nexcept:\n    pass")
        self._test_differ("try:\n    pass\n    pass\nexcept:\n    pass",
                          "try:\n    pass\nexcept:\n    pass",
                          ((1, 0), (1, 0), "length of ast.TryExcept.body differ"))
        self._test_same("try:\n    pass\nexcept a:\n    pass",
                        "try:\n    pass\nexcept a:\n    pass")
        self._test_differ("try:\n    pass\nexcept a:\n    pass\nexcept b:\n    pass",
                          "try:\n    pass\nexcept a:\n    pass",
                          ((1, 0), (1, 0), "length of ast.TryExcept.handlers differ"))
        self._test_differ("try:\n    pass\nexcept a:\n    pass",
                          "try:\n    pass\nexcept b:\n    pass",
                          ((3, 7), (3, 7), "ast.Name.id differ a b"))
        self._test_differ("try:\n    pass\nexcept a:\n    pass",
                          "try:\n    pass\nexcept:\n    pass",
                          ((3, 0), (3, 0), "ast.ExceptHandler.type differ"))
        self._test_same("try:\n    pass\nexcept a as x:\n    pass",
                        "try:\n    pass\nexcept a as x:\n    pass")
        self._test_same("try:\n    pass\nexcept a as x:\n    pass",
                        "try:\n    pass\nexcept a, x:\n    pass")
        self._test_differ("try:\n    pass\nexcept a as x:\n    pass",
                          "try:\n    pass\nexcept a:\n    pass",
                          ((3, 0), (3, 0), "ast.ExceptHandler.name differ"))
        self._test_differ("try:\n    pass\nexcept a as x:\n    pass",
                          "try:\n    pass\nexcept a as y:\n    pass",
                          ((3, 12), (3, 12), "ast.Name.id differ x y"))
        self._test_differ("try:\n    pass\nexcept:\n    pass\n    pass",
                          "try:\n    pass\nexcept:\n    pass",
                          ((3, 0), (3, 0), "length of ast.ExceptHandler.body differ"))
        self._test_same("try:\n    pass\nexcept:\n    pass\nelse:\n    pass",
                        "try:\n    pass\nexcept:\n    pass\nelse:\n    pass")
        self._test_differ("try:\n    pass\nexcept:\n    pass\nelse:\n    pass\n    pass",
                          "try:\n    pass\nexcept:\n    pass\nelse:\n    pass",
                          ((1, 0), (1, 0), "length of ast.TryExcept.orelse differ"))

    @unittest.skipIf(ast_diff.py3, "ast.TryFinally is removed (and ast.Try is added) in py3")
    def test_tryfinally(self):
        self._test_same("try:\n    pass\nfinally:\n    pass",
                        "try:\n    pass\nfinally:\n    pass")
        self._test_differ("try:\n    pass\n    pass\nfinally:\n    pass",
                          "try:\n    pass\nfinally:\n    pass",
                          ((1, 0), (1, 0), "length of ast.TryFinally.body differ"))
        self._test_differ("try:\n    pass\nfinally:\n    pass\n    pass",
                          "try:\n    pass\nfinally:\n    pass",
                          ((1, 0), (1, 0), "length of ast.TryFinally.finalbody differ"))
        self._test_differ(
            "try:\n    pass\nexcept a:\n    pass\nexcept b:\n    pass\nfinally:\n    pass",
            "try:\n    pass\nexcept a:\n    pass\nfinally:\n    pass",
            ((1, 0), (1, 0), "length of ast.TryExcept.handlers differ"))

    def test_yield(self):
        self._test_same("def f():\n    yield", "def f():\n    yield")
        self._test_differ("def f():\n    yield a", "def f():\n    yield",
                          ((2, 4), (2, 4), "ast.Yield.value differ"))

    @unittest.skipUnless(ast_diff.py3, "ast.YieldFrom is added in py3")
    def test_yieldfrom(self):
        self._test_same("def f():\n    yield from x",
                        "def f():\n    yield from x")
        self._test_differ("def f():\n    yield from x",
                          "def f():\n    yield from y",
                          ((2, 15), (2, 15), "ast.Name.id differ x y"))

    @unittest.skipUnless(ast_diff.py3, "ast.Ellipsis is added in py3")
    def test_ellipsis(self):
        self._test_same("...", "...")

    @unittest.skipUnless(ast_diff.py3, "ast.Await is added in py3")
    def test_await(self):
        self._test_same("await a", "await a")
        self._test_differ("await a", "await b",
                          ((1, 6), (1, 6), "ast.Name.id differ a b"))

    @unittest.skipUnless(ast_diff.py38, "ast.NamedExpr is added in py38")
    def test_namedexpr(self):
        self._test_same("(a := x)", "(a := x)")
        self._test_differ("(a := x)", "(b := x)",
                          ((1, 1), (1, 1), "ast.Name.id differ a b"))
        self._test_differ("(a := x)", "(a := y)",
                          ((1, 6), (1, 6), "ast.Name.id differ x y"))

    @unittest.skipUnless(ast_diff.py310, "structural pattern matching is added in Python 3.10")
    def test_match(self):
        self._test_same("match a:\n    case _:\n        pass",
                        "match a:\n    case _:\n        pass")
        self._test_differ("match a:\n    case _:\n        pass\n    case _:\n        pass",
                          "match a:\n    case _:\n        pass",
                          ((1, 0), (1, 0), "length of ast.Match.cases differ"))
        self._test_differ("match a:\n    case _:\n        pass",
                          "match b:\n    case _:\n        pass",
                          ((1, 6), (1, 6), "ast.Name.id differ a b"))
        self._test_differ("match a:\n    case b:\n        pass",
                          "match a:\n    case c:\n        pass",
                          ((2, 9), (2, 9), "ast.MatchAs.name differ"))
        self._test_same("match a:\n    case 0:\n        pass",
                        "match a:\n    case 0:\n        pass")
        self._test_differ("match a:\n    case 0:\n        pass",
                          "match a:\n    case 1:\n        pass",
                          ((2, 9), (2, 9), "ast.Constant.value differ 0 1"))
        self._test_same("match a:\n    case (b, c):\n        pass",
                        "match a:\n    case (b, c):\n        pass")
        self._test_differ("match a:\n    case (b, c):\n        pass",
                          "match a:\n    case (_, c):\n        pass",
                          ((2, 10), (2, 10), "ast.MatchAs.name differ"))
        self._test_same("match a:\n    case A():\n        pass",
                        "match a:\n    case A():\n        pass")
        self._test_differ("match a:\n    case A():\n        pass",
                          "match a:\n    case B():\n        pass",
                          ((2, 9), (2, 9), "ast.Name.id differ A B"))
        self._test_differ("match a:\n    case A(a):\n        pass",
                          "match a:\n    case A(b):\n        pass",
                          ((2, 11), (2, 11), "ast.MatchAs.name differ"))


if __name__ == '__main__':
    unittest.main()
