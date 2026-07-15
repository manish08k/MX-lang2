"""
MX Language Parser
Converts token stream → AST using recursive descent parsing.
"""

from lexer import Token, TokenType
from ast_nodes import *


class ParseError(Exception):
    def __init__(self, msg, token):
        line = token.line if token else '?'
        col  = token.col  if token else '?'
        super().__init__(f"[Parse Error] Line {line}, Col {col}: {msg}")


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # ── Helpers ──────────────────────────────────────────────────────────────

    def peek(self, offset=0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def current(self) -> Token:
        return self.peek(0)

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def check(self, *types: TokenType) -> bool:
        return self.current().type in types

    def match(self, *types: TokenType) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def expect(self, ttype: TokenType, msg: str = None) -> Token:
        if self.current().type != ttype:
            raise ParseError(
                msg or f"Expected {ttype.name}, got {self.current().type.name} ({self.current().value!r})",
                self.current()
            )
        return self.advance()

    def skip_semis(self):
        while self.check(TokenType.SEMICOLON):
            self.advance()

    def error(self, msg):
        raise ParseError(msg, self.current())

    # ── Entry Point ──────────────────────────────────────────────────────────

    def parse(self) -> Program:
        stmts = []
        self.skip_semis()
        while not self.check(TokenType.EOF):
            stmts.append(self.parse_stmt())
            self.skip_semis()
        return Program(body=stmts)

    # ── Statements ───────────────────────────────────────────────────────────

    def parse_stmt(self) -> Stmt:
        tok = self.current()

        if tok.type == TokenType.FN:
            return self.parse_fn_decl()
        if tok.type == TokenType.STRUCT:
            return self.parse_struct_decl()
        if tok.type in (TokenType.LET, TokenType.CONST):
            return self.parse_var_decl()
        if tok.type == TokenType.IF:
            return self.parse_if()
        if tok.type == TokenType.WHILE:
            return self.parse_while()
        if tok.type == TokenType.FOR:
            return self.parse_for()
        if tok.type == TokenType.RETURN:
            return self.parse_return()
        if tok.type == TokenType.BREAK:
            self.advance()
            return BreakStmt()
        if tok.type == TokenType.CONTINUE:
            self.advance()
            return ContinueStmt()
        if tok.type == TokenType.IMPORT:
            return self.parse_import()
        if tok.type == TokenType.LBRACE:
            return self.parse_block()

        # Expression statement
        expr = self.parse_expr()
        self.skip_semis()
        return ExprStmt(expr=expr)

    def parse_block(self) -> Block:
        self.expect(TokenType.LBRACE, "Expected '{'")
        stmts = []
        self.skip_semis()
        while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            stmts.append(self.parse_stmt())
            self.skip_semis()
        self.expect(TokenType.RBRACE, "Expected '}'")
        return Block(stmts=stmts)

    def parse_var_decl(self) -> VarDecl:
        is_const = self.current().type == TokenType.CONST
        self.advance()
        name = self.expect(TokenType.IDENT, "Expected variable name").value
        type_hint = None
        if self.match(TokenType.COLON):
            type_hint = self.parse_type_hint()
        value = None
        if self.match(TokenType.ASSIGN):
            value = self.parse_expr()
        self.skip_semis()
        return VarDecl(name=name, type_hint=type_hint, value=value, is_const=is_const)

    def parse_type_hint(self) -> str:
        type_tokens = {
            TokenType.TYPE_INT, TokenType.TYPE_FLOAT,
            TokenType.TYPE_STR, TokenType.TYPE_BOOL,
            TokenType.TYPE_VOID, TokenType.IDENT,
        }
        if self.current().type in type_tokens:
            name = self.advance().value
            if self.check(TokenType.LBRACKET):
                self.advance()
                self.expect(TokenType.RBRACKET)
                return f"{name}[]"
            return name
        self.error(f"Expected type, got {self.current().value!r}")

    def parse_fn_decl(self) -> FnDecl:
        self.expect(TokenType.FN)
        name = self.expect(TokenType.IDENT, "Expected function name").value
        self.expect(TokenType.LPAREN)
        params = []
        while not self.check(TokenType.RPAREN) and not self.check(TokenType.EOF):
            pname = self.expect(TokenType.IDENT, "Expected parameter name").value
            ptype = None
            if self.match(TokenType.COLON):
                ptype = self.parse_type_hint()
            default = None
            if self.match(TokenType.ASSIGN):
                default = self.parse_expr()
            params.append(FnParam(name=pname, type_hint=ptype, default=default))
            if not self.match(TokenType.COMMA):
                break
        self.expect(TokenType.RPAREN)
        ret_type = None
        if self.match(TokenType.ARROW):
            ret_type = self.parse_type_hint()
        body = self.parse_block()
        return FnDecl(name=name, params=params, return_type=ret_type, body=body)

    def parse_struct_decl(self) -> StructDecl:
        self.expect(TokenType.STRUCT)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.LBRACE)
        fields = []
        self.skip_semis()
        while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            fname = self.expect(TokenType.IDENT).value
            self.expect(TokenType.COLON)
            ftype = self.parse_type_hint()
            fields.append((fname, ftype))
            self.skip_semis()
            if not self.match(TokenType.COMMA):
                self.skip_semis()
        self.expect(TokenType.RBRACE)
        return StructDecl(name=name, fields=fields)

    def parse_if(self) -> IfStmt:
        self.expect(TokenType.IF)
        cond = self.parse_expr()
        then_blk = self.parse_block()
        else_blk = None
        if self.match(TokenType.ELSE):
            if self.check(TokenType.IF):
                else_blk = self.parse_if()
            else:
                else_blk = self.parse_block()
        return IfStmt(condition=cond, then_block=then_blk, else_block=else_blk)

    def parse_while(self) -> WhileStmt:
        self.expect(TokenType.WHILE)
        cond = self.parse_expr()
        body = self.parse_block()
        return WhileStmt(condition=cond, body=body)

    def parse_for(self) -> ForStmt:
        self.expect(TokenType.FOR)
        var = self.expect(TokenType.IDENT).value
        self.expect(TokenType.IN, "Expected 'in'")
        iterable = self.parse_expr()
        body = self.parse_block()
        return ForStmt(var=var, iterable=iterable, body=body)

    def parse_return(self) -> ReturnStmt:
        self.expect(TokenType.RETURN)
        value = None
        if not self.check(TokenType.SEMICOLON) and not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            value = self.parse_expr()
        self.skip_semis()
        return ReturnStmt(value=value)

    def parse_import(self) -> ImportStmt:
        self.expect(TokenType.IMPORT)
        module = self.expect(TokenType.IDENT).value
        self.skip_semis()
        return ImportStmt(module=module)

    # ── Expressions (Pratt-style precedence) ─────────────────────────────────

    def parse_expr(self) -> Expr:
        return self.parse_assign()

    def parse_assign(self) -> Expr:
        left = self.parse_or()
        assign_ops = {
            TokenType.ASSIGN:    '=',
            TokenType.PLUS_EQ:   '+=',
            TokenType.MINUS_EQ:  '-=',
            TokenType.STAR_EQ:   '*=',
            TokenType.SLASH_EQ:  '/=',
        }
        if self.current().type in assign_ops:
            op = assign_ops[self.advance().type]
            value = self.parse_assign()
            if isinstance(left, Ident):
                return Assign(name=left.name, op=op, value=value)
            elif isinstance(left, Member):
                # struct field assignment — handled in interpreter
                return Assign(name=left, op=op, value=value)
            elif isinstance(left, Index):
                return Assign(name=left, op=op, value=value)
            self.error("Invalid assignment target")
        return left

    def parse_or(self) -> Expr:
        left = self.parse_and()
        while self.check(TokenType.OR):
            self.advance()
            right = self.parse_and()
            left = BinOp(op='or', left=left, right=right)
        return left

    def parse_and(self) -> Expr:
        left = self.parse_not()
        while self.check(TokenType.AND):
            self.advance()
            right = self.parse_not()
            left = BinOp(op='and', left=left, right=right)
        return left

    def parse_not(self) -> Expr:
        if self.check(TokenType.NOT):
            self.advance()
            return UnaryOp(op='not', operand=self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self) -> Expr:
        left = self.parse_additive()
        cmp_ops = {
            TokenType.EQ: '==', TokenType.NEQ: '!=',
            TokenType.LT: '<',  TokenType.GT:  '>',
            TokenType.LTE: '<=',TokenType.GTE: '>=',
        }
        while self.current().type in cmp_ops:
            op = cmp_ops[self.advance().type]
            right = self.parse_additive()
            left = BinOp(op=op, left=left, right=right)
        return left

    def parse_additive(self) -> Expr:
        left = self.parse_multiplicative()
        while self.check(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinOp(op=op, left=left, right=right)
        return left

    def parse_multiplicative(self) -> Expr:
        left = self.parse_power()
        while self.check(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.advance().value
            right = self.parse_power()
            left = BinOp(op=op, left=left, right=right)
        return left

    def parse_power(self) -> Expr:
        base = self.parse_unary()
        if self.check(TokenType.POWER):
            self.advance()
            exp = self.parse_power()  # right-associative
            return BinOp(op='**', left=base, right=exp)
        return base

    def parse_unary(self) -> Expr:
        if self.check(TokenType.MINUS):
            self.advance()
            return UnaryOp(op='-', operand=self.parse_unary())
        if self.check(TokenType.NOT):
            self.advance()
            return UnaryOp(op='not', operand=self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self) -> Expr:
        expr = self.parse_primary()
        while True:
            if self.check(TokenType.LPAREN):
                # Function call
                self.advance()
                args = []
                while not self.check(TokenType.RPAREN) and not self.check(TokenType.EOF):
                    args.append(self.parse_expr())
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RPAREN)
                expr = Call(callee=expr, args=args)
            elif self.check(TokenType.LBRACKET):
                # Index access
                self.advance()
                idx = self.parse_expr()
                self.expect(TokenType.RBRACKET)
                expr = Index(obj=expr, idx=idx)
            elif self.check(TokenType.DOT):
                # Member access
                self.advance()
                attr = self.expect(TokenType.IDENT).value
                expr = Member(obj=expr, attr=attr)
            else:
                break
        return expr

    def parse_primary(self) -> Expr:
        tok = self.current()

        if tok.type == TokenType.INT_LIT:
            self.advance(); return IntLit(value=tok.value)
        if tok.type == TokenType.FLOAT_LIT:
            self.advance(); return FloatLit(value=tok.value)
        if tok.type == TokenType.STRING_LIT:
            self.advance(); return StringLit(value=tok.value)
        if tok.type == TokenType.BOOL_LIT:
            self.advance(); return BoolLit(value=tok.value)
        if tok.type == TokenType.NULL:
            self.advance(); return NullLit()

        if tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TokenType.RPAREN)
            return expr

        if tok.type == TokenType.LBRACKET:
            return self.parse_array_lit()

        if tok.type == TokenType.NEW:
            return self.parse_struct_create()

        if tok.type == TokenType.IDENT:
            self.advance()
            return Ident(name=tok.value)

        # Allow type keywords as identifiers in expression context (int(), str(), float(), bool() builtins)
        type_as_ident = {
            TokenType.TYPE_INT, TokenType.TYPE_FLOAT,
            TokenType.TYPE_STR, TokenType.TYPE_BOOL,
            TokenType.TYPE_VOID,
        }
        if tok.type in type_as_ident:
            self.advance()
            return Ident(name=tok.value)

        self.error(f"Unexpected token: {tok.type.name} ({tok.value!r})")

    def parse_array_lit(self) -> ArrayLit:
        self.expect(TokenType.LBRACKET)
        elements = []
        while not self.check(TokenType.RBRACKET) and not self.check(TokenType.EOF):
            # Check for range  e.g. 1..10
            elem = self.parse_expr()
            if self.check(TokenType.DOTDOT):
                self.advance()
                end = self.parse_expr()
                elements.append(RangeExpr(start=elem, end=end))
            else:
                elements.append(elem)
            if not self.match(TokenType.COMMA):
                break
        self.expect(TokenType.RBRACKET)
        return ArrayLit(elements=elements)

    def parse_struct_create(self) -> StructCreate:
        self.expect(TokenType.NEW)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.LBRACE)
        fields = {}
        while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            fname = self.expect(TokenType.IDENT).value
            self.expect(TokenType.COLON)
            fval = self.parse_expr()
            fields[fname] = fval
            if not self.match(TokenType.COMMA):
                break
        self.expect(TokenType.RBRACE)
        return StructCreate(name=name, fields=fields)
