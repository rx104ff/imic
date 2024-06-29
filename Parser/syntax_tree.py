class SyntaxTree:
    def __init__(self):
        self.root = None


class SyntaxNode:
    pass


class NatZ(SyntaxNode):
    pass


class BinOp(SyntaxNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Num(SyntaxNode):
    def __init__(self, value):
        self.value = value


class Var(SyntaxNode):
    def __init__(self, name):
        self.name = name


class Bool(SyntaxNode):
    def __init__(self, text):
        self.value = text

class IfThenElse(SyntaxNode):
    def __init__(self, if_expr, then_expr, else_expr):
        self.ifExpr = if_expr
        self.thenExpr = then_expr
        self.elseExpr = else_expr


class Fun(SyntaxNode):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr


class Let(SyntaxNode):
    def __init__(self, var, fun, expr):
        self.var = var
        self.fun = fun
        self.expr = expr


class RecFun(SyntaxNode):
    def __init__(self, var, fun, expr):
        self.var = var
        self.fun = fun
        self.expr = expr
