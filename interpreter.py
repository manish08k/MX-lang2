"""
MX Language Interpreter
Tree-walking interpreter that executes the AST directly.
"""

import math
import time
import sys
from ast_nodes import *


# ─── Runtime Values ───────────────────────────────────────────────────────────

class MXNull:
    def __repr__(self): return "null"

class MXArray:
    def __init__(self, elements=None):
        self.elements = elements or []
    def __repr__(self):
        return "[" + ", ".join(repr(e) for e in self.elements) + "]"

class MXStruct:
    def __init__(self, type_name, fields):
        self.type_name = type_name
        self.fields = fields  # dict
    def __repr__(self):
        fstr = ", ".join(f"{k}: {repr(v)}" for k, v in self.fields.items())
        return f"{self.type_name} {{ {fstr} }}"

class MXFunction:
    def __init__(self, decl: FnDecl, closure):
        self.decl = decl
        self.closure = closure
    def __repr__(self):
        return f"<fn {self.decl.name}>"

class MXBuiltin:
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn
    def __repr__(self):
        return f"<builtin {self.name}>"


NULL = MXNull()


# ─── Control Flow Signals ────────────────────────────────────────────────────

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass


# ─── Environment (Scoped Variable Store) ─────────────────────────────────────

class Env:
    def __init__(self, parent=None):
        self.vars = {}
        self.consts = set()
        self.parent = parent

    def get(self, name: str):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: '{name}'")

    def set(self, name: str, value, const=False):
        self.vars[name] = value
        if const:
            self.consts.add(name)

    def assign(self, name: str, value):
        if name in self.vars:
            if name in self.consts:
                raise RuntimeError(f"Cannot reassign const '{name}'")
            self.vars[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
        else:
            raise RuntimeError(f"Undefined variable: '{name}'")

    def child(self):
        return Env(parent=self)


# ─── Interpreter ─────────────────────────────────────────────────────────────

class RuntimeError_(Exception):
    def __init__(self, msg):
        super().__init__(f"[Runtime Error] {msg}")


class Interpreter:
    def __init__(self):
        self.globals = Env()
        self.struct_defs = {}   # name -> [(field, type)]
        self._setup_builtins()

    # ── Builtins ─────────────────────────────────────────────────────────────

    def _setup_builtins(self):
        def mx_print(*args):
            print(*[self._to_str(a) for a in args])
            return NULL

        def mx_input(prompt=None):
            if prompt and prompt is not NULL:
                val = input(self._to_str(prompt))
            else:
                val = input()
            return val

        def mx_len(obj):
            if isinstance(obj, MXArray): return len(obj.elements)
            if isinstance(obj, str): return len(obj)
            raise RuntimeError_(f"len() not supported on {type(obj).__name__}")

        def mx_type(obj):
            type_map = {
                int: 'int', float: 'float', str: 'str',
                bool: 'bool', MXNull: 'null',
                MXArray: 'array', MXFunction: 'fn',
                MXBuiltin: 'builtin', MXStruct: 'struct',
            }
            return type_map.get(type(obj), 'unknown')

        def mx_int(v):
            try: return int(v)
            except: raise RuntimeError_(f"Cannot convert {v!r} to int")

        def mx_float(v):
            try: return float(v)
            except: raise RuntimeError_(f"Cannot convert {v!r} to float")

        def mx_str(v):
            return self._to_str(v)

        def mx_bool(v):
            return self._truthy(v)

        def mx_range(start, stop=None, step=1):
            if stop is None: start, stop = 0, start
            arr = MXArray(list(range(int(start), int(stop), int(step))))
            return arr

        def mx_push(arr, val):
            if not isinstance(arr, MXArray):
                raise RuntimeError_("push() requires an array")
            arr.elements.append(val)
            return NULL

        def mx_pop(arr):
            if not isinstance(arr, MXArray):
                raise RuntimeError_("pop() requires an array")
            if not arr.elements:
                raise RuntimeError_("pop() on empty array")
            return arr.elements.pop()

        def mx_append(arr, val):
            mx_push(arr, val)
            return arr

        def mx_contains(arr, val):
            if isinstance(arr, MXArray):
                return val in arr.elements
            if isinstance(arr, str):
                return str(val) in arr
            return False

        def mx_keys(struct):
            if isinstance(struct, MXStruct):
                return MXArray(list(struct.fields.keys()))
            raise RuntimeError_("keys() requires a struct")

        def mx_sqrt(v):   return math.sqrt(float(v))
        def mx_abs(v):    return abs(v)
        def mx_max(*args):
            if len(args) == 1 and isinstance(args[0], MXArray):
                return max(args[0].elements)
            return max(args)
        def mx_min(*args):
            if len(args) == 1 and isinstance(args[0], MXArray):
                return min(args[0].elements)
            return min(args)
        def mx_floor(v):  return math.floor(float(v))
        def mx_ceil(v):   return math.ceil(float(v))
        def mx_round(v, n=0): return round(float(v), int(n))

        def mx_exit(code=0): sys.exit(int(code))

        builtins = {
            'print':    mx_print,
            'input':    mx_input,
            'len':      mx_len,
            'type':     mx_type,
            'int':      mx_int,
            'float':    mx_float,
            'str':      mx_str,
            'bool':     mx_bool,
            'range':    mx_range,
            'push':     mx_push,
            'pop':      mx_pop,
            'append':   mx_append,
            'contains': mx_contains,
            'keys':     mx_keys,
            'sqrt':     mx_sqrt,
            'abs':      mx_abs,
            'max':      mx_max,
            'min':      mx_min,
            'floor':    mx_floor,
            'ceil':     mx_ceil,
            'round':    mx_round,
            'exit':     mx_exit,
            'PI':       math.pi,
            'E':        math.e,
        }

        for name, fn in builtins.items():
            if callable(fn):
                self.globals.set(name, MXBuiltin(name, fn))
            else:
                self.globals.set(name, fn)

    # ── Execution Entry ───────────────────────────────────────────────────────

    def run(self, program: Program):
        self.exec_block_stmts(program.body, self.globals)

    def exec_stmt(self, stmt: Stmt, env: Env):
        if isinstance(stmt, VarDecl):
            val = self.eval_expr(stmt.value, env) if stmt.value else NULL
            env.set(stmt.name, val, const=stmt.is_const)

        elif isinstance(stmt, ExprStmt):
            self.eval_expr(stmt.expr, env)

        elif isinstance(stmt, Block):
            self.exec_block_stmts(stmt.stmts, env.child())

        elif isinstance(stmt, IfStmt):
            cond = self.eval_expr(stmt.condition, env)
            if self._truthy(cond):
                self.exec_block_stmts(stmt.then_block.stmts, env.child())
            elif stmt.else_block:
                if isinstance(stmt.else_block, Block):
                    self.exec_block_stmts(stmt.else_block.stmts, env.child())
                else:
                    self.exec_stmt(stmt.else_block, env)

        elif isinstance(stmt, WhileStmt):
            while self._truthy(self.eval_expr(stmt.condition, env)):
                try:
                    self.exec_block_stmts(stmt.body.stmts, env.child())
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue

        elif isinstance(stmt, ForStmt):
            iterable = self.eval_expr(stmt.iterable, env)
            items = self._to_iter(iterable)
            for item in items:
                loop_env = env.child()
                loop_env.set(stmt.var, item)
                try:
                    self.exec_block_stmts(stmt.body.stmts, loop_env)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue

        elif isinstance(stmt, FnDecl):
            fn = MXFunction(decl=stmt, closure=env)
            env.set(stmt.name, fn)

        elif isinstance(stmt, StructDecl):
            self.struct_defs[stmt.name] = stmt.fields
            env.set(stmt.name, stmt.name)  # register name

        elif isinstance(stmt, ReturnStmt):
            val = self.eval_expr(stmt.value, env) if stmt.value else NULL
            raise ReturnSignal(val)

        elif isinstance(stmt, BreakStmt):
            raise BreakSignal()

        elif isinstance(stmt, ContinueStmt):
            raise ContinueSignal()

        elif isinstance(stmt, ImportStmt):
            self._import_module(stmt.module, env)

        else:
            raise RuntimeError_(f"Unknown statement type: {type(stmt).__name__}")

    def exec_block_stmts(self, stmts, env: Env):
        for stmt in stmts:
            self.exec_stmt(stmt, env)

    # ── Expression Evaluator ──────────────────────────────────────────────────

    def eval_expr(self, expr: Expr, env: Env):
        if isinstance(expr, IntLit):    return expr.value
        if isinstance(expr, FloatLit):  return expr.value
        if isinstance(expr, StringLit): return expr.value
        if isinstance(expr, BoolLit):   return expr.value
        if isinstance(expr, NullLit):   return NULL

        if isinstance(expr, Ident):
            return env.get(expr.name)

        if isinstance(expr, ArrayLit):
            result = []
            for elem in expr.elements:
                if isinstance(elem, RangeExpr):
                    s = int(self.eval_expr(elem.start, env))
                    e = int(self.eval_expr(elem.end, env))
                    result.extend(range(s, e))
                else:
                    result.append(self.eval_expr(elem, env))
            return MXArray(result)

        if isinstance(expr, RangeExpr):
            s = int(self.eval_expr(expr.start, env))
            e = int(self.eval_expr(expr.end, env))
            return MXArray(list(range(s, e)))

        if isinstance(expr, StructCreate):
            if expr.name not in self.struct_defs:
                raise RuntimeError_(f"Unknown struct type: '{expr.name}'")
            fields = {}
            for fname, fval_expr in expr.fields.items():
                fields[fname] = self.eval_expr(fval_expr, env)
            return MXStruct(type_name=expr.name, fields=fields)

        if isinstance(expr, BinOp):
            return self.eval_binop(expr, env)

        if isinstance(expr, UnaryOp):
            val = self.eval_expr(expr.operand, env)
            if expr.op == '-':   return -val
            if expr.op == 'not': return not self._truthy(val)
            raise RuntimeError_(f"Unknown unary op: {expr.op}")

        if isinstance(expr, Assign):
            return self.eval_assign(expr, env)

        if isinstance(expr, Call):
            return self.eval_call(expr, env)

        if isinstance(expr, Index):
            obj = self.eval_expr(expr.obj, env)
            idx = self.eval_expr(expr.idx, env)
            if isinstance(obj, MXArray):
                if not isinstance(idx, int):
                    raise RuntimeError_("Array index must be an integer")
                if idx < 0 or idx >= len(obj.elements):
                    raise RuntimeError_(f"Index {idx} out of bounds (size {len(obj.elements)})")
                return obj.elements[idx]
            if isinstance(obj, str):
                return obj[int(idx)]
            raise RuntimeError_(f"Cannot index into {type(obj).__name__}")

        if isinstance(expr, Member):
            obj = self.eval_expr(expr.obj, env)
            if isinstance(obj, MXStruct):
                if expr.attr not in obj.fields:
                    raise RuntimeError_(f"Struct '{obj.type_name}' has no field '{expr.attr}'")
                return obj.fields[expr.attr]
            # Array methods
            if isinstance(obj, MXArray):
                return self._array_method(obj, expr.attr, env)
            if isinstance(obj, str):
                return self._str_method(obj, expr.attr)
            raise RuntimeError_(f"Cannot access member '{expr.attr}' on {type(obj).__name__}")

        raise RuntimeError_(f"Unknown expression type: {type(expr).__name__}")

    def eval_binop(self, expr: BinOp, env: Env):
        # Short-circuit for logical ops
        if expr.op == 'and':
            left = self.eval_expr(expr.left, env)
            return left if not self._truthy(left) else self.eval_expr(expr.right, env)
        if expr.op == 'or':
            left = self.eval_expr(expr.left, env)
            return left if self._truthy(left) else self.eval_expr(expr.right, env)

        left  = self.eval_expr(expr.left,  env)
        right = self.eval_expr(expr.right, env)
        op = expr.op

        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return self._to_str(left) + self._to_str(right)
            if isinstance(left, MXArray) and isinstance(right, MXArray):
                return MXArray(left.elements + right.elements)
            return left + right
        if op == '-':   return left - right
        if op == '*':
            if isinstance(left, str) and isinstance(right, int):
                return left * right
            return left * right
        if op == '/':
            if right == 0: raise RuntimeError_("Division by zero")
            if isinstance(left, int) and isinstance(right, int):
                return left // right
            return left / right
        if op == '%':   return left % right
        if op == '**':  return left ** right
        if op == '==':  return self._equals(left, right)
        if op == '!=':  return not self._equals(left, right)
        if op == '<':   return left < right
        if op == '>':   return left > right
        if op == '<=':  return left <= right
        if op == '>=':  return left >= right

        raise RuntimeError_(f"Unknown binary operator: {op}")

    def eval_assign(self, expr: Assign, env: Env):
        # Member or index assignment
        if isinstance(expr.name, Member):
            obj = self.eval_expr(expr.name.obj, env)
            val = self.eval_expr(expr.value, env)
            if isinstance(obj, MXStruct):
                if expr.name.attr not in obj.fields:
                    raise RuntimeError_(f"Struct '{obj.type_name}' has no field '{expr.name.attr}'")
                obj.fields[expr.name.attr] = val
                return val
            raise RuntimeError_("Cannot assign to member of non-struct")

        if isinstance(expr.name, Index):
            obj = self.eval_expr(expr.name.obj, env)
            idx = int(self.eval_expr(expr.name.idx, env))
            val = self.eval_expr(expr.value, env)
            if isinstance(obj, MXArray):
                obj.elements[idx] = val
                return val
            raise RuntimeError_("Cannot index-assign on non-array")

        # Simple variable assignment
        name = expr.name
        if expr.op == '=':
            val = self.eval_expr(expr.value, env)
            env.assign(name, val)
            return val
        # Compound assignment
        old = env.get(name)
        new_val = self.eval_expr(expr.value, env)
        op_map = {'+=': '+', '-=': '-', '*=': '*', '/=': '/'}
        result = self.eval_binop(BinOp(op=op_map[expr.op], left=IntLit(0), right=IntLit(0)), env)
        # Compute directly
        if expr.op == '+=': result = old + new_val if not isinstance(old, str) else old + self._to_str(new_val)
        elif expr.op == '-=': result = old - new_val
        elif expr.op == '*=': result = old * new_val
        elif expr.op == '/=':
            if new_val == 0: raise RuntimeError_("Division by zero")
            result = old / new_val
        env.assign(name, result)
        return result

    def eval_call(self, expr: Call, env: Env):
        callee = self.eval_expr(expr.callee, env)
        args = [self.eval_expr(a, env) for a in expr.args]

        if isinstance(callee, MXBuiltin):
            try:
                return callee.fn(*args)
            except TypeError as e:
                raise RuntimeError_(f"Wrong arguments for builtin '{callee.name}': {e}")

        if isinstance(callee, MXFunction):
            fn_env = callee.closure.child()
            decl = callee.decl

            # Bind parameters
            for i, param in enumerate(decl.params):
                if i < len(args):
                    fn_env.set(param.name, args[i])
                elif param.default is not None:
                    fn_env.set(param.name, self.eval_expr(param.default, callee.closure))
                else:
                    raise RuntimeError_(f"Missing argument '{param.name}' in call to '{decl.name}'")

            try:
                self.exec_block_stmts(decl.body.stmts, fn_env)
                return NULL
            except ReturnSignal as ret:
                return ret.value

        if callable(callee):
            return callee(*args)

        raise RuntimeError_(f"'{self._to_str(callee)}' is not callable")

    # ── Array & String Methods ────────────────────────────────────────────────

    def _array_method(self, arr: MXArray, method: str, env: Env):
        if method == 'length':
            return len(arr.elements)
        if method == 'push':
            return MXBuiltin('push', lambda v: (arr.elements.append(v), NULL)[1])
        if method == 'pop':
            return MXBuiltin('pop', lambda: arr.elements.pop() if arr.elements else NULL)
        if method == 'reverse':
            return MXBuiltin('reverse', lambda: (arr.elements.reverse(), arr)[1])
        if method == 'join':
            return MXBuiltin('join', lambda sep='': sep.join(self._to_str(e) for e in arr.elements))
        if method == 'slice':
            return MXBuiltin('slice', lambda s, e=None: MXArray(arr.elements[int(s):int(e) if e is not None else None]))
        if method == 'contains':
            return MXBuiltin('contains', lambda v: v in arr.elements)
        if method == 'first':
            return arr.elements[0] if arr.elements else NULL
        if method == 'last':
            return arr.elements[-1] if arr.elements else NULL
        raise RuntimeError_(f"Array has no method '{method}'")

    def _str_method(self, s: str, method: str):
        if method == 'length':
            return len(s)
        if method == 'upper':
            return MXBuiltin('upper', lambda: s.upper())
        if method == 'lower':
            return MXBuiltin('lower', lambda: s.lower())
        if method == 'split':
            return MXBuiltin('split', lambda sep=' ': MXArray(s.split(sep)))
        if method == 'trim':
            return MXBuiltin('trim', lambda: s.strip())
        if method == 'starts_with':
            return MXBuiltin('starts_with', lambda p: s.startswith(p))
        if method == 'ends_with':
            return MXBuiltin('ends_with', lambda p: s.endswith(p))
        if method == 'contains':
            return MXBuiltin('contains', lambda p: p in s)
        if method == 'replace':
            return MXBuiltin('replace', lambda old, new: s.replace(old, new))
        if method == 'to_int':
            return MXBuiltin('to_int', lambda: int(s))
        if method == 'to_float':
            return MXBuiltin('to_float', lambda: float(s))
        raise RuntimeError_(f"String has no method '{method}'")

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _truthy(self, val) -> bool:
        if isinstance(val, MXNull): return False
        if isinstance(val, bool):   return val
        if isinstance(val, int):    return val != 0
        if isinstance(val, float):  return val != 0.0
        if isinstance(val, str):    return len(val) > 0
        if isinstance(val, MXArray):return len(val.elements) > 0
        return True

    def _equals(self, a, b) -> bool:
        if isinstance(a, MXNull) and isinstance(b, MXNull): return True
        if isinstance(a, MXNull) or isinstance(b, MXNull):  return False
        if isinstance(a, MXArray) and isinstance(b, MXArray):
            return a.elements == b.elements
        return a == b

    def _to_str(self, val) -> str:
        if isinstance(val, bool):    return 'true' if val else 'false'
        if isinstance(val, MXNull):  return 'null'
        if isinstance(val, MXArray): return repr(val)
        if isinstance(val, MXStruct):return repr(val)
        if isinstance(val, float):
            if val == int(val): return f"{val:.1f}"
            return str(val)
        return str(val)

    def _to_iter(self, val):
        if isinstance(val, MXArray): return val.elements
        if isinstance(val, str):     return list(val)
        if isinstance(val, range):   return list(val)
        raise RuntimeError_(f"Cannot iterate over {type(val).__name__}")

    def _import_module(self, name: str, env: Env):
        modules = {
            'math': {
                'PI': math.pi, 'E': math.e,
                'sqrt':  MXBuiltin('sqrt',  lambda v: math.sqrt(float(v))),
                'sin':   MXBuiltin('sin',   lambda v: math.sin(float(v))),
                'cos':   MXBuiltin('cos',   lambda v: math.cos(float(v))),
                'tan':   MXBuiltin('tan',   lambda v: math.tan(float(v))),
                'log':   MXBuiltin('log',   lambda v, b=math.e: math.log(float(v), float(b))),
                'pow':   MXBuiltin('pow',   lambda b, e: float(b) ** float(e)),
                'floor': MXBuiltin('floor', lambda v: math.floor(float(v))),
                'ceil':  MXBuiltin('ceil',  lambda v: math.ceil(float(v))),
            },
        }
        if name not in modules:
            raise RuntimeError_(f"Unknown module: '{name}'")
        for k, v in modules[name].items():
            env.set(k, v)
