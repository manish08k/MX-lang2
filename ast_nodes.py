"""
MX Language AST (Abstract Syntax Tree) Node Definitions
"""

from dataclasses import dataclass, field
from typing import Optional, Any


# ─── Base ────────────────────────────────────────────────────────────────────

class Node:
    pass

class Stmt(Node):
    pass

class Expr(Node):
    pass


# ─── Expressions ─────────────────────────────────────────────────────────────

@dataclass
class IntLit(Expr):
    value: int

@dataclass
class FloatLit(Expr):
    value: float

@dataclass
class StringLit(Expr):
    value: str

@dataclass
class BoolLit(Expr):
    value: bool

@dataclass
class NullLit(Expr):
    pass

@dataclass
class Ident(Expr):
    name: str

@dataclass
class BinOp(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass
class UnaryOp(Expr):
    op: str
    operand: Expr

@dataclass
class Assign(Expr):
    name: str
    op: str        # '=', '+=', '-=', '*=', '/='
    value: Expr

@dataclass
class Call(Expr):
    callee: Expr
    args: list

@dataclass
class Index(Expr):
    obj: Expr
    idx: Expr

@dataclass
class Member(Expr):
    obj: Expr
    attr: str

@dataclass
class ArrayLit(Expr):
    elements: list

@dataclass
class RangeExpr(Expr):
    start: Expr
    end: Expr

@dataclass
class StructCreate(Expr):
    name: str
    fields: dict   # {field_name: Expr}

@dataclass
class Lambda(Expr):
    params: list   # [(name, type_hint)]
    body: Expr


# ─── Statements ──────────────────────────────────────────────────────────────

@dataclass
class Program(Node):
    body: list     # list of Stmt

@dataclass
class VarDecl(Stmt):
    name: str
    type_hint: Optional[str]
    value: Optional[Expr]
    is_const: bool = False

@dataclass
class ExprStmt(Stmt):
    expr: Expr

@dataclass
class Block(Stmt):
    stmts: list

@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_block: Block
    else_block: Optional[Node]  # Block or IfStmt

@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Block

@dataclass
class ForStmt(Stmt):
    var: str
    iterable: Expr
    body: Block

@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr]

@dataclass
class BreakStmt(Stmt):
    pass

@dataclass
class ContinueStmt(Stmt):
    pass

@dataclass
class FnParam:
    name: str
    type_hint: Optional[str]
    default: Optional[Expr] = None

@dataclass
class FnDecl(Stmt):
    name: str
    params: list       # list of FnParam
    return_type: Optional[str]
    body: Block

@dataclass
class StructDecl(Stmt):
    name: str
    fields: list       # [(name, type_hint)]

@dataclass
class ImportStmt(Stmt):
    module: str
