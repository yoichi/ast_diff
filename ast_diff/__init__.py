import ast
import difflib
import sys
from itertools import zip_longest

py39 = sys.version_info.minor >= 9
py310 = sys.version_info.minor >= 10
py311 = sys.version_info.minor >= 11
py312 = sys.version_info.minor >= 12


class DiffFound(Exception):
    pass


def _gen_diff(node_name, node1, node2):
    if len(node1.generators) != len(node2.generators):
        raise DiffFound("length of ast.%s.generators differ" % node_name)
    for gen1, gen2 in zip(node1.generators, node2.generators):
        if len(gen1.ifs) != len(gen2.ifs):
            raise DiffFound("length of ast.comprehension.ifs differ")


def _for_diff(node_name, node1, node2):
    if len(node1.body) != len(node2.body):
        raise DiffFound("length of ast.%s.body differ" % node_name)
    elif len(node1.orelse) != len(node2.orelse):
        raise DiffFound("length of ast.%s.orelse differ" % node_name)


def _funcdef_diff(node_name, node1, node2):
    if len(node1.decorator_list) != len(node2.decorator_list):
        raise DiffFound("length of ast.%s.decorator_list differ" % node_name)
    if node1.name != node2.name:
        raise DiffFound(
            "ast.%s.name differ %s %s" % (node_name, node1.name, node2.name)
        )
    if len(node1.body) != len(node2.body):
        raise DiffFound("length of ast.%s.body differ" % node_name)
    if (node1.returns is None) != (node2.returns is None):
        raise DiffFound("ast.%s.returns differ" % node_name)
    args1 = node1.args
    args2 = node2.args
    if len(args1.args) != len(args2.args):
        raise DiffFound("length of ast.%s.args.args differ" % node_name)
    if len(args1.defaults) != len(args2.defaults):
        raise DiffFound("length of ast.%s.args.defaults differ" % node_name)
    if len(args1.posonlyargs) != len(args2.posonlyargs):
        raise DiffFound("length of ast.%s.args.posonlyargs differ" % node_name)
    for i, (poa1, poa2) in enumerate(zip(args1.posonlyargs, args2.posonlyargs)):
        if poa1.arg != poa2.arg:
            raise DiffFound(
                "ast.%s.args.posonlyargs[%d].arg differ %s %s"
                % (node_name, i, poa1.arg, poa2.arg)
            )
    if len(args1.kwonlyargs) != len(args2.kwonlyargs):
        raise DiffFound("length of ast.%s.args.kwonlyargs differ" % node_name)
    for i, (koa1, koa2) in enumerate(zip(args1.kwonlyargs, args2.kwonlyargs)):
        if koa1.arg != koa2.arg:
            raise DiffFound(
                "ast.%s.args.kwonlyargs[%d].arg differ %s %s"
                % (node_name, i, koa1.arg, koa2.arg)
            )
    for kd1, kd2 in zip(args1.kw_defaults, args2.kw_defaults):
        if (kd1 is None) != (kd2 is None):
            raise DiffFound("ast.%s.args.kw_defaults differ" % node_name)
    if (args1.vararg is None) != (args2.vararg is None):
        raise DiffFound("ast.%s.args.vararg differ" % node_name)
    if (args1.kwarg is None) != (args2.kwarg is None):
        raise DiffFound("ast.%s.args.kwarg differ" % node_name)


def _with_diff(node_name, node1, node2):
    if len(node1.items) != len(node2.items):
        raise DiffFound("length of ast.%s.items differ" % node_name)
    for i, (item1, item2) in enumerate(zip(node1.items, node2.items)):
        if (item1.optional_vars is None) != (item2.optional_vars is None):
            raise DiffFound("ast.%s.items[%d].optional_vars differ" % (node_name, i))
    if len(node1.body) != len(node2.body):
        raise DiffFound("length of ast.%s.body differ" % node_name)


def _try_diff(node_name, node1, node2):
    if len(node1.body) != len(node2.body):
        raise DiffFound("length of ast.%s.body differ" % node_name)
    if len(node1.handlers) != len(node2.handlers):
        raise DiffFound("length of ast.%s.handlers differ" % node_name)
    if len(node1.orelse) != len(node2.orelse):
        raise DiffFound("length of ast.%s.orelse differ" % node_name)
    if len(node1.finalbody) != len(node2.finalbody):
        raise DiffFound("length of ast.%s.finalbody differ" % node_name)


def ast_diff(tree1, tree2):
    for node1, node2 in zip_longest(ast.walk(tree1), ast.walk(tree2)):
        try:
            if type(node1) is not type(node2):
                raise DiffFound(
                    "different type %s %s"
                    % (type(node1).__name__, type(node2).__name__)
                )
            elif isinstance(node1, ast.Module):
                # diff of len(ast.Module.body) will be handle later
                # since 'Module' object has no attribute 'lineno'
                pass
            elif isinstance(node1, ast.Expr):
                pass
            elif isinstance(node1, ast.NamedExpr):
                pass
            elif isinstance(node1, ast.Assign):
                pass
            elif isinstance(node1, ast.AugAssign):
                if node1.op != node2.op:
                    raise DiffFound(
                        "ast.AugAssign.op differ %s %s"
                        % (type(node1.op).__name__, type(node2.op).__name__)
                    )
            elif isinstance(node1, ast.AnnAssign):
                pass
            elif isinstance(node1, ast.Pass):
                pass
            elif isinstance(node1, ast.Call):
                if len(node1.args) != len(node2.args):
                    raise DiffFound("length of ast.Call.args differ")
                elif len(node1.keywords) != len(node2.keywords):
                    raise DiffFound("length of ast.Call.keywords differ")
                elif any(
                    k1.arg != k2.arg for k1, k2 in zip(node1.keywords, node2.keywords)
                ):
                    raise DiffFound("ast.Call.keywords differ")
            elif isinstance(node1, ast.Starred):
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
                if (node1.exc is None) != (node2.exc is None):
                    raise DiffFound("ast.Raise.exc differ")
                if (node1.cause is None) != (node2.cause is None):
                    raise DiffFound("ast.Raise.cause differ")
            elif isinstance(node1, ast.Return):
                if (node1.value is None) != (node2.value is None):
                    raise DiffFound("ast.Return.value differ")
            elif isinstance(node1, ast.Yield):
                if (node1.value is None) != (node2.value is None):
                    raise DiffFound("ast.Yield.value differ")
            elif isinstance(node1, ast.YieldFrom):
                pass
            elif isinstance(node1, ast.BoolOp):
                if node1.op != node2.op:
                    raise DiffFound(
                        "ast.BoolOp.op differ %s %s"
                        % (type(node1.op).__name__, type(node2.op).__name__)
                    )
            elif isinstance(node1, ast.Compare):
                if len(node1.comparators) != len(node2.comparators):
                    raise DiffFound("length of ast.Compare.comparators differ")
                elif node1.ops != node2.ops:
                    raise DiffFound("ast.Compare.ops differ")
            elif isinstance(node1, ast.Name):
                if node1.id != node2.id:
                    raise DiffFound("ast.Name.id differ %s %s" % (node1.id, node2.id))
            elif isinstance(node1, ast.Global):
                if node1.names != node2.names:
                    raise DiffFound("ast.Global.names differ")
            elif isinstance(node1, ast.Nonlocal):
                if node1.names != node2.names:
                    raise DiffFound("ast.Nonlocal.names differ")
            elif isinstance(node1, ast.Constant):
                if node1.value != node2.value:
                    raise DiffFound(
                        "ast.Constant.value differ %s %s" % (node1.value, node2.value)
                    )
            elif isinstance(node1, ast.JoinedStr):
                if len(node1.values) != len(node2.values):
                    raise DiffFound("length of ast.JoinedStr.values differ")
            elif isinstance(node1, ast.FormattedValue):
                if node1.conversion != node2.conversion:
                    raise DiffFound("ast.FormattedValue.conversion differ")
                if (node1.format_spec is None) != (node2.format_spec is None):
                    raise DiffFound("ast.FormattedValue.format_spec differ")
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
                _for_diff("For", node1, node2)
            elif isinstance(node1, ast.AsyncFor):
                _for_diff("AsyncFor", node1, node2)
            elif isinstance(node1, ast.With):
                _with_diff("With", node1, node2)
            elif isinstance(node1, ast.AsyncWith):
                _with_diff("AsyncWith", node1, node2)
            elif isinstance(node1, ast.Lambda):
                args1 = node1.args
                args2 = node2.args
                if len(args1.args) != len(args2.args):
                    raise DiffFound("length of ast.Lambda.args.args differ")
                if len(args1.defaults) != len(args2.defaults):
                    raise DiffFound("length of ast.Lambda.args.defaults differ")
                if len(args1.posonlyargs) != len(args2.posonlyargs):
                    raise DiffFound("length of ast.Lambda.args.posonlyargs differ")
                for i, (poa1, poa2) in enumerate(
                    zip(args1.posonlyargs, args2.posonlyargs)
                ):
                    if poa1.arg != poa2.arg:
                        raise DiffFound(
                            "ast.Lambda.args.posonlyargs[%d].arg differ %s %s"
                            % (i, poa1.arg, poa2.arg)
                        )
                if len(args1.kwonlyargs) != len(args2.kwonlyargs):
                    raise DiffFound("length of ast.Lambda.args.kwonlyargs differ")
                for i, (koa1, koa2) in enumerate(
                    zip(args1.kwonlyargs, args2.kwonlyargs)
                ):
                    if koa1.arg != koa2.arg:
                        raise DiffFound(
                            "ast.Lambda.args.kwonlyargs[%d].arg differ %s %s"
                            % (i, koa1.arg, koa2.arg)
                        )
                for kd1, kd2 in zip(args1.kw_defaults, args2.kw_defaults):
                    if (kd1 is None) != (kd2 is None):
                        raise DiffFound("ast.Lambda.args.kw_defaults differ")
                if (args1.vararg is None) != (args2.vararg is None):
                    raise DiffFound("ast.Lambda.args.vararg differ")
                if (args1.kwarg is None) != (args2.kwarg is None):
                    raise DiffFound("ast.Lambda.args.kwarg differ")
            elif isinstance(node1, ast.FunctionDef):
                _funcdef_diff("FunctionDef", node1, node2)
            elif isinstance(node1, ast.AsyncFunctionDef):
                _funcdef_diff("AsyncFunctionDef", node1, node2)
            elif isinstance(node1, ast.arguments):
                pass
            elif isinstance(node1, ast.arg):
                if node1.arg != node2.arg:
                    raise DiffFound("ast.arg.arg differ %s %s" % (node1.arg, node2.arg))
                if (node1.annotation is None) != (node2.annotation is None):
                    raise DiffFound("ast.arg.annotation differ")
            elif isinstance(node1, ast.UnaryOp):
                if node1.op != node2.op:
                    raise DiffFound(
                        "ast.UnaryOp.op differ %s %s"
                        % (type(node1.op).__name__, type(node2.op).__name__)
                    )
            elif isinstance(node1, ast.BinOp):
                if node1.op != node2.op:
                    raise DiffFound(
                        "ast.BinOp.op differ %s %s"
                        % (type(node1.op).__name__, type(node2.op).__name__)
                    )
            elif isinstance(node1, ast.Delete):
                pass
            elif isinstance(node1, ast.Subscript):
                slice1 = node1.slice
                slice2 = node2.slice
                if type(slice1) is not type(slice2):
                    raise DiffFound(
                        "type of ast.Subscript.slice differ %s %s"
                        % (type(slice1).__name__, type(slice2).__name__)
                    )
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
                        raise DiffFound(
                            "ast.alias.name differ %s %s" % (name1.name, name2.name)
                        )
                    if name1.asname != name2.asname:
                        raise DiffFound(
                            "ast.alias.asname differ %s %s"
                            % (name1.asname, name2.asname)
                        )
            elif isinstance(node1, ast.ImportFrom):
                if node1.module != node2.module:
                    raise DiffFound(
                        "ast.ImportFrom.module differ %s %s"
                        % (node1.module, node2.module)
                    )
                if len(node1.names) != len(node2.names):
                    raise DiffFound("length of ast.ImportFrom.names differ")
                for name1, name2 in zip(node1.names, node2.names):
                    if name1.name != name2.name:
                        raise DiffFound(
                            "ast.alias.name differ %s %s" % (name1.name, name2.name)
                        )
                    if name1.asname != name2.asname:
                        raise DiffFound(
                            "ast.alias.asname differ %s %s"
                            % (name1.asname, name2.asname)
                        )
            elif isinstance(node1, ast.alias):
                pass
            elif isinstance(node1, ast.Attribute):
                if node1.attr != node2.attr:
                    raise DiffFound(
                        "ast.Attribute.attr differ %s %s" % (node1.attr, node2.attr)
                    )
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
                    raise DiffFound(
                        "ast.ClassDef.name differ %s %s" % (node1.name, node2.name)
                    )
                if len(node1.bases) != len(node2.bases):
                    raise DiffFound("length of ast.ClassDef.bases differ")
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.ClassDef.body differ")
            elif isinstance(node1, ast.Try):
                _try_diff("Try", node1, node2)
            elif py311 and isinstance(node1, ast.TryStar):
                _try_diff("TryStar", node1, node2)
            elif isinstance(node1, ast.ExceptHandler):
                if (node1.type is None) != (node2.type is None):
                    raise DiffFound("ast.ExceptHandler.type differ")
                if node1.name != node2.name:
                    raise DiffFound("ast.ExceptHandler.name differ")
                if len(node1.body) != len(node2.body):
                    raise DiffFound("length of ast.ExceptHandler.body differ")
            elif isinstance(node1, ast.Assert):
                pass
            elif isinstance(node1, ast.withitem):
                pass
            elif isinstance(node1, ast.Await):
                pass
            elif py310 and isinstance(node1, ast.Match):
                if len(node1.cases) != len(node2.cases):
                    raise DiffFound("length of ast.Match.cases differ")
            elif py310 and isinstance(node1, ast.match_case):
                pass
            elif py310 and isinstance(node1, ast.MatchAs):
                if node1.name != node2.name:
                    raise DiffFound("ast.MatchAs.name differ")
            elif py310 and isinstance(node1, ast.MatchValue):
                pass
            elif py310 and isinstance(node1, ast.MatchOr):
                pass
            elif py310 and isinstance(node1, ast.MatchSingleton):
                if node1.value != node2.value:
                    raise DiffFound("ast.MatchSingleton.value differ")
            elif py310 and isinstance(node1, ast.MatchSequence):
                pass
            elif py310 and isinstance(node1, ast.MatchStar):
                if node1.name != node2.name:
                    raise DiffFound("ast.MatchStar.name differ")
            elif py310 and isinstance(node1, ast.MatchMapping):
                pass
            elif py310 and isinstance(node1, ast.MatchClass):
                pass
            else:
                if node1 != node2:
                    raise DiffFound("DEBUG: %s %s" % (node1, dir(node1)))
        except DiffFound as e:
            if node1 is None:
                return None, (node2.lineno, node2.col_offset), e.args[0]
            if node2 is None:
                return (node1.lineno, node1.col_offset), None, e.args[0]
            return (
                (node1.lineno, node1.col_offset),
                (node2.lineno, node2.col_offset),
                e.args[0],
            )
        except Exception as e:
            return (
                (node1.lineno, node1.col_offset),
                (node2.lineno, node2.col_offset),
                str(e),
            )
    return None


def ast_parse_file(fname):
    with open(fname) as f:
        return ast.parse(f.read())


def main(fname1, fname2):
    ast1 = ast_parse_file(fname1)
    ast2 = ast_parse_file(fname2)
    result = ast_diff(ast1, ast2)
    if result is not None:
        print(result)
        if py39:
            print(
                "\n".join(
                    difflib.unified_diff(
                        ast.dump(ast1, indent=1).splitlines(),
                        ast.dump(ast2, indent=1).splitlines(),
                        fromfile=fname1,
                        tofile=fname2,
                        lineterm="",
                    )
                )
            )
        return 1
    assert ast.dump(ast1) == ast.dump(ast2)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s file1 file2" % sys.argv[0])
        sys.exit(-1)
    fname1 = sys.argv[1]
    fname2 = sys.argv[2]
    sys.exit(main(fname1, fname2))
