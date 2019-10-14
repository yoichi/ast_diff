import ast
import sys

if sys.version_info.major < 3:
    from itertools import izip_longest as zip_longest
    py3 = False
else:
    from itertools import zip_longest
    py3 = True


class DiffFound(Exception):
    pass


def _gen_diff(node_name, node1, node2):
    if len(node1.generators) != len(node2.generators):
        raise DiffFound("length of ast.%s.generators differ" % node_name)
    for gen1, gen2 in zip(node1.generators, node2.generators):
        if len(gen1.ifs) != len(gen2.ifs):
            raise DiffFound("length of ast.comprehension.ifs differ")


def ast_diff(tree1, tree2):
    for node1, node2 in zip_longest(ast.walk(tree1), ast.walk(tree2)):
        try:
            if type(node1) != type(node2):
                raise DiffFound("different type %s %s" % (type(node1), type(node2)))
            elif isinstance(node1, ast.Module):
                # diff of len(ast.Module.body) will be handle later
                # since 'Module' object has no attribute 'lineno'
                pass
            elif isinstance(node1, ast.Expr):
                pass
            elif isinstance(node1, ast.Assign):
                pass
            elif isinstance(node1, ast.AugAssign):
                if node1.op != node2.op:
                    raise DiffFound("ast.AugAssign.op differ %s %s" % (type(node1.op), type(node2.op)))
            elif isinstance(node1, ast.Pass):
                pass
            elif isinstance(node1, ast.Call):
                if len(node1.args) != len(node2.args):
                    raise DiffFound("length of ast.Call.args differ")
                elif len(node1.keywords) != len(node2.keywords):
                    raise DiffFound("length of ast.Call.keywords differ")
                elif any(k1.arg != k2.arg for k1, k2 in zip(node1.keywords, node2.keywords)):
                    raise DiffFound("ast.Call.keywords differ")
                elif not py3 and (node1.starargs is None) != (node2.starargs is None):
                    raise DiffFound("ast.Call.starargs differ")
            elif py3 and isinstance(node1, ast.Starred):
                pass
            elif isinstance(node1, ast.If):
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.If.body differ")
                elif len(node1.orelse) != len(node2.orelse):
                    raise DiffFound("length of ast.If.orelse differ")
            elif isinstance(node1, ast.IfExp):
                pass
            elif isinstance(node1, ast.Continue):
                pass
            elif isinstance(node1, ast.Break):
                pass
            elif isinstance(node1, ast.Raise):
                if py3:
                    if (node1.exc is None) != (node2.exc is None):
                        raise DiffFound("ast.Raise.exc differ")
                    if (node1.cause is None) != (node2.cause is None):
                        raise DiffFound("ast.Raise.cause differ")
                else:
                    if (node1.type is None) != (node2.type is None):
                        raise DiffFound("ast.Raise.type differ")
            elif isinstance(node1, ast.Return):
                if (node1.value is None) != (node2.value is None):
                    raise DiffFound("ast.Return.value differ")
            elif isinstance(node1, ast.Yield):
                if (node1.value is None) != (node2.value is None):
                    raise DiffFound("ast.Yield.value differ")
            elif py3 and isinstance(node1, ast.YieldFrom):
                pass
            elif isinstance(node1, ast.BoolOp):
                if node1.op != node2.op:
                    raise DiffFound("ast.BoolOp.op differ %s %s" % (type(node1.op), type(node2.op)))
            elif isinstance(node1, ast.Compare):
                if len(node1.comparators) != len(node2.comparators):
                    raise DiffFound("length of ast.Compare.comparators differ")
                elif node1.ops != node2.ops:
                    raise DiffFound("ast.Compare.ops differ")
            elif isinstance(node1, ast.Name):
                if node1.id != node2.id:
                    raise DiffFound("ast.Name.id differ %s %s" % (node1.id, node2.id))
            elif isinstance(node1, ast.Num):
                if node1.n != node2.n:
                    raise DiffFound("ast.Num.n differ %s %s" % (node1.n, node2.n))
            elif isinstance(node1, ast.Str):
                if node1.s != node2.s:
                    raise DiffFound("ast.Str.s differ %s %s" % (node1.s, node2.s))
            elif isinstance(node1, ast.keyword):
                pass
            elif isinstance(node1, ast.List):
                if len(node1.elts) != len(node2.elts):
                    raise DiffFound("length of ast.List.elts differ")
            elif isinstance(node1, ast.Set):
                if len(node1.elts) != len(node2.elts):
                    raise DiffFound("length of ast.Set.elts differ")
            elif isinstance(node1, ast.Tuple):
                if len(node1.elts) != len(node2.elts):
                    raise DiffFound("length of ast.Tuple.elts differ")
            elif isinstance(node1, ast.While):
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.While.body differ")
                elif len(node1.orelse) != len(node2.orelse):
                    raise DiffFound("length of ast.While.orelse differ")
            elif isinstance(node1, ast.For):
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.For.body differ")
                elif len(node1.orelse) != len(node2.orelse):
                    raise DiffFound("length of ast.For.orelse differ")
            elif isinstance(node1, ast.With):
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.With.body differ")
            elif isinstance(node1, ast.Lambda):
                args1 = node1.args
                args2 = node2.args
                if len(args1.args) != len(args2.args):
                    raise DiffFound("length of ast.Lambda.args.args differ")
                if len(args1.defaults) != len(args2.defaults):
                    raise DiffFound("length of ast.Lambda.args.defaults differ")
                if py3:
                    if len(args1.kwonlyargs) != len(args2.kwonlyargs):
                        raise DiffFound("length of ast.Lambda.args.kwonlyargs differ")
                    for i, (koa1, koa2) in enumerate(zip(args1.kwonlyargs, args2.kwonlyargs)):
                        if koa1.arg != koa2.arg:
                            raise DiffFound("ast.Lambda.args.kwonlyargs[%d].arg differ %s %s" % (i, koa1.arg, koa2.arg))
                    for kd1, kd2 in zip(args1.kw_defaults, args2.kw_defaults):
                        if (kd1 is None) != (kd2 is None):
                            raise DiffFound("ast.Lambda.args.kw_defaults differ")
                if (args1.vararg is None) != (args2.vararg is None):
                    raise DiffFound("ast.Lambda.args.vararg differ")
                if (args1.kwarg is None) != (args2.kwarg is None):
                    raise DiffFound("ast.Lambda.args.kwarg differ")
            elif isinstance(node1, ast.FunctionDef):
                if len(node1.decorator_list) != len(node2.decorator_list):
                    raise DiffFound("length of ast.FunctionDef.decorator_list differ")
                if node1.name != node2.name:
                    raise DiffFound("ast.FunctionDef.name differ %s %s" % (node1.name, node2.name))
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.FunctionDef.body differ")
                if py3 and (node1.returns is None) != (node2.returns is None):
                    raise DiffFound("ast.FunctionDef.returns differ")
                args1 = node1.args
                args2 = node2.args
                if len(args1.args) != len(args2.args):
                    raise DiffFound("length of ast.FunctionDef.args.args differ")
                if len(args1.defaults) != len(args2.defaults):
                    raise DiffFound("length of ast.FunctionDef.args.defaults differ")
                if py3:
                    if len(args1.kwonlyargs) != len(args2.kwonlyargs):
                        raise DiffFound("length of ast.FunctionDef.args.kwonlyargs differ")
                    for i, (koa1, koa2) in enumerate(zip(args1.kwonlyargs, args2.kwonlyargs)):
                        if koa1.arg != koa2.arg:
                            raise DiffFound("ast.FunctionDef.args.kwonlyargs[%d].arg differ %s %s" % (i, koa1.arg, koa2.arg))
                    for kd1, kd2 in zip(args1.kw_defaults, args2.kw_defaults):
                        if (kd1 is None) != (kd2 is None):
                            raise DiffFound("ast.FunctionDef.args.kw_defaults differ")
                if (args1.vararg is None) != (args2.vararg is None):
                    raise DiffFound("ast.FunctionDef.args.vararg differ")
                if (args1.kwarg is None) != (args2.kwarg is None):
                    raise DiffFound("ast.FunctionDef.args.kwarg differ")
            elif isinstance(node1, ast.arguments):
                pass
            elif py3 and isinstance(node1, ast.arg):
                if node1.arg != node2.arg:
                    raise DiffFound("ast.arg.arg differ %s %s" % (node1.arg, node2.arg))
                if (node1.annotation is None) != (node2.annotation is None):
                    raise DiffFound("ast.arg.annotation differ")
            elif isinstance(node1, ast.UnaryOp):
                if node1.op != node2.op:
                    raise DiffFound("ast.UnaryOp.op differ %s %s" % (type(node1.op), type(node2.op)))
            elif isinstance(node1, ast.BinOp):
                if node1.op != node2.op:
                    raise DiffFound("ast.BinOp.op differ %s %s" % (type(node1.op), type(node2.op)))
            elif isinstance(node1, ast.Delete):
                pass
            elif isinstance(node1, ast.Subscript):
                slice1 = node1.slice
                slice2 = node2.slice
                if type(slice1) != type(slice2):
                    raise DiffFound("type of ast.Subscript.slice differ %s %s" % (type(slice1), type(slice2)))
                if isinstance(slice1, ast.Slice):
                    if (slice1.lower is None) != (slice2.lower is None):
                        raise DiffFound("ast.Subscript.slice.lower differ")
                    if (slice1.upper is None) != (slice2.upper is None):
                        raise DiffFound("ast.Subscript.slice.upper differ")
                    if (slice1.step is None) != (slice2.step is None):
                        raise DiffFound("ast.Subscript.slice.step differ")
            elif isinstance(node1, ast.Index):
                pass
            elif isinstance(node1, ast.Slice):
                pass
            elif isinstance(node1, ast.Import):
                if len(node1.names) != len(node2.names):
                    raise DiffFound("length of ast.Import.names differ")
                for name1, name2 in zip(node1.names, node2.names):
                    if name1.name != name2.name:
                        raise DiffFound("ast.alias.name differ %s %s" % (name1.name, name2.name))
                    if name1.asname != name2.asname:
                        raise DiffFound("ast.alias.asname differ %s %s" % (name1.asname, name2.asname))
            elif isinstance(node1, ast.ImportFrom):
                if node1.module != node2.module:
                    raise DiffFound("ast.ImportFrom.module differ %s %s" % (node1.module, node2.module))
                if len(node1.names) != len(node2.names):
                    raise DiffFound("length of ast.ImportFrom.names differ")
                for name1, name2 in zip(node1.names, node2.names):
                    if name1.name != name2.name:
                        raise DiffFound("ast.alias.name differ %s %s" % (name1.name, name2.name))
                    if name1.asname != name2.asname:
                        raise DiffFound("ast.alias.asname differ %s %s" % (name1.asname, name2.asname))
            elif isinstance(node1, ast.alias):
                pass
            elif isinstance(node1, ast.Attribute):
                if node1.attr != node2.attr:
                    raise DiffFound("ast.Attribute.attr differ %s %s" % (node1.attr, node2.attr))
            elif isinstance(node1, ast.Dict):
                if len(node1.keys) != len(node2.keys):
                    raise DiffFound("length of ast.Dict.keys differ")
            elif isinstance(node1, ast.ListComp):
                _gen_diff("ListComp", node1, node2)
            elif isinstance(node1, ast.GeneratorExp):
                _gen_diff("GeneratorExp", node1, node2)
            elif isinstance(node1, ast.SetComp):
                _gen_diff("SetComp", node1, node2)
            elif isinstance(node1, ast.DictComp):
                _gen_diff("DictComp", node1, node2)
            elif isinstance(node1, ast.comprehension):
                pass
            elif isinstance(node1, ast.ClassDef):
                if len(node1.decorator_list) != len(node2.decorator_list):
                    raise DiffFound("length of ast.ClassDef.decorator_list differ")
                if node1.name != node2.name:
                    raise DiffFound("ast.ClassDef.name differ %s %s" % (node1.name, node2.name))
                if len(node1.bases) != len(node2.bases):
                    raise DiffFound("length of ast.ClassDef.bases differ")
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.ClassDef.body differ")
            elif py3 and isinstance(node1, ast.Try):
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.Try.body differ")
                if len(node1.handlers) != len(node2.handlers):
                    raise DiffFound("length of ast.Try.handlers differ")
                if len(node1.orelse) != len(node2.orelse):
                    raise DiffFound("length of ast.Try.orelse differ")
                if len(node1.finalbody) != len(node2.finalbody):
                    raise DiffFound("length of ast.Try.finalbody differ")
            elif not py3 and isinstance(node1, ast.TryExcept):
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.TryExcept.body differ")
                if len(node1.handlers) != len(node2.handlers):
                    raise DiffFound("length of ast.TryExcept.handlers differ")
                if len(node1.orelse) != len(node2.orelse):
                    raise DiffFound("length of ast.TryExcept.orelse differ")
            elif not py3 and isinstance(node1, ast.TryFinally):
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.TryFinally.body differ")
                if len(node1.finalbody) != len(node2.finalbody):
                    raise DiffFound("length of ast.TryFinally.finalbody differ")
            elif isinstance(node1, ast.ExceptHandler):
                if (node1.type is None) != (node2.type is None):
                    raise DiffFound("ast.ExceptHandler.type differ")
                if (node1.name is None) != (node2.name is None):
                    raise DiffFound("ast.ExceptHandler.name differ")
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.ExceptHandler.body differ")
            elif not py3 and isinstance(node1, ast.Print):
                if len(node1.values) != len(node2.values):
                    raise DiffFound("length of ast.Print.values differ")
            elif py3 and isinstance(node1, ast.NameConstant):
                if node1.value != node2.value:
                    raise DiffFound("ast.NameConstant.value differ %s %s" % (node1.value, node2.value))
            elif py3 and isinstance(node1, ast.withitem):
                pass
            else:
                if node1 != node2:
                    raise DiffFound("DEBUG: %s %s" % (node1, dir(node1)))
        except DiffFound as e:
            if node1 is None:
                return None, (node2.lineno, node2.col_offset), e.args[0]
            if node2 is None:
                return (node1.lineno, node1.col_offset), None, e.args[0]
            return (node1.lineno, node1.col_offset), (node2.lineno, node2.col_offset), e.args[0]
        except Exception as e:
            return (node1.lineno, node1.col_offset), (node2.lineno, node2.col_offset), str(e)
    return None


if __name__ == '__main__':
    def load(fname):
        with open(fname) as f:
            return ast.parse(f.read())

    if len(sys.argv) != 3:
        print("usage: %s file1 file2" % sys.argv[0])
        sys.exit(-1)
    fname1 = sys.argv[1]
    fname2 = sys.argv[2]
    result = ast_diff(load(fname1), load(fname2))
    print(result)
    sys.exit(result is not None)
