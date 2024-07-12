from graphviz import Digraph

from lexer import *


class SyntaxTree:
    def __init__(self, root):
        self.root = root

    def visualize_tree(self):
        def add_nodes_edges(node, _dot=None):
            if _dot is None:
                _dot = Digraph()
                _dot.node(name=str(id(node)), label=str(node))

            if isinstance(node, BinOp):
                _dot.node(name=str(id(node.left)), label=str(node.left))
                _dot.node(name=str(id(node.right)), label=str(node.right))
                _dot.edge(str(id(node)), str(id(node.left)))
                _dot.edge(str(id(node)), str(id(node.right)))
                add_nodes_edges(node.left, _dot=_dot)
                add_nodes_edges(node.right, _dot=_dot)
            elif isinstance(node, IfThenElse):
                _dot.node(name=str(id(node.ifExpr)), label=str(node.ifExpr))
                _dot.node(name=str(id(node.elseExpr)), label=str(node.elseExpr))
                _dot.node(name=str(id(node.thenExpr)), label=str(node.thenExpr))
                _dot.edge(str(id(node)), str(id(node.ifExpr)))
                _dot.edge(str(id(node)), str(id(node.elseExpr)))
                _dot.edge(str(id(node)), str(id(node.thenExpr)))
                add_nodes_edges(node.ifExpr, _dot=_dot)
                add_nodes_edges(node.elseExpr, _dot=_dot)
                add_nodes_edges(node.thenExpr, _dot=_dot)
            elif isinstance(node, Let):
                _dot.node(name=str(id(node.var)), label=str(node.var))
                _dot.node(name=str(id(node.fun)), label=str(node.fun))
                _dot.node(name=str(id(node.in_expr)), label=str(node.in_expr))
                _dot.edge(str(id(node)), str(id(node.var)))
                _dot.edge(str(id(node)), str(id(node.fun)))
                _dot.edge(str(id(node)), str(id(node.in_expr)))
                add_nodes_edges(node.var, _dot=_dot)
                add_nodes_edges(node.fun, _dot=_dot)
                add_nodes_edges(node.in_expr, _dot=_dot)
            elif isinstance(node, RecFun):
                _dot.node(name=str(id(node.var)), label=str(node.var))
                _dot.node(name=str(id(node.fun)), label=str(node.fun))
                _dot.node(name=str(id(node.in_expr)), label=str(node.in_expr))
                _dot.edge(str(id(node)), str(id(node.var)))
                _dot.edge(str(id(node)), str(id(node.fun)))
                _dot.edge(str(id(node)), str(id(node.in_expr)))
                add_nodes_edges(node.var, _dot=_dot)
                add_nodes_edges(node.fun, _dot=_dot)
                add_nodes_edges(node.in_expr, _dot=_dot)
            elif isinstance(node, VarApp):
                _dot.node(name=str(id(node.var)), label=str(node.var))
                _dot.node(name=str(id(node.expr)), label=str(node.expr))
                _dot.edge(str(id(node)), str(id(node.var)))
                _dot.edge(str(id(node)), str(id(node.expr)))
                add_nodes_edges(node.var, _dot=_dot)
                add_nodes_edges(node.expr, _dot=_dot)
            elif isinstance(node, Fun):
                _dot.node(name=str(id(node.var)), label=str(node.var))
                _dot.node(name=str(id(node.expr)), label=str(node.expr))
                _dot.edge(str(id(node)), str(id(node.var)))
                _dot.edge(str(id(node)), str(id(node.expr)))
                add_nodes_edges(node.var, _dot=_dot)
                add_nodes_edges(node.expr, _dot=_dot)
            elif isinstance(node, Num):
                _dot.node(name=str(id(node)), label=str(node.value))
            elif isinstance(node, Var):
                _dot.node(name=str(id(node)), label=str(node.name))
            elif isinstance(node, Bool):
                _dot.node(name=str(id(node)), label=str(node.value))
            return _dot

        dot = add_nodes_edges(self.root)
        return dot


class SyntaxNode:
    def __init__(self, is_paren: bool):
        self.is_paren = is_paren


class NatZ(SyntaxNode):
    pass


class BinOp(SyntaxNode):
    def __init__(self, left, op, right, is_paren: bool):
        super().__init__(is_paren)
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        if self.is_paren:
            if self.op == TokenType.MINUS:
                return f'({str(self.left)} - {str(self.right)})'
            elif self.op == TokenType.PLUS:
                return f'({str(self.left)} + {str(self.right)})'
            elif self.op == TokenType.ASTERISK:
                return f'({str(self.left)} * {str(self.right)})'
            elif self.op == TokenType.LT:
                return f'({str(self.left)} < {str(self.right)})'
            elif self.op == TokenType.EQ:
                return f'({str(self.left)} = {str(self.right)})'
        else:
            if self.op == TokenType.MINUS:
                return f'{str(self.left)} - {str(self.right)}'
            elif self.op == TokenType.PLUS:
                return f'{str(self.left)} + {str(self.right)}'
            elif self.op == TokenType.ASTERISK:
                return f'{str(self.left)} * {str(self.right)}'
            elif self.op == TokenType.LT:
                return f'{str(self.left)} < {str(self.right)}'
            elif self.op == TokenType.EQ:
                return f'{str(self.left)} = {str(self.right)}'


class Num(SyntaxNode):
    def __init__(self, value, is_paren: bool):
        super().__init__(is_paren)
        self.value = value

    def __str__(self):
        if self.is_paren:
            return f'({self.value})'
        else:
            return f'{self.value}'


class Var(SyntaxNode):
    def __init__(self, name: str, is_paren):
        super().__init__(is_paren)
        self.name = name

    def __str__(self):
        if self.is_paren:
            return f'({self.name})'
        else:
            return f'{self.name}'


class Bool(SyntaxNode):
    def __init__(self, value: str, is_paren):
        super().__init__(is_paren)
        self.value = value

    def __str__(self):
        if self.is_paren:
            return f'({self.value})'
        else:
            return f'{self.value}'


class Nil(SyntaxNode):
    def __init__(self, is_paren):
        super().__init__(is_paren)

    def __str__(self):
        if self.is_paren:
            return f'([])'
        else:
            return f'[]'


class IfThenElse(SyntaxNode):
    def __init__(self, if_expr: SyntaxNode, then_expr: SyntaxNode, else_expr: SyntaxNode, is_paren: bool):
        super().__init__(is_paren)
        self.ifExpr = if_expr
        self.thenExpr = then_expr
        self.elseExpr = else_expr

    def __str__(self):
        if self.is_paren:
            return f'(if {str(self.ifExpr)} then {str(self.thenExpr)} else {str(self.elseExpr)})'
        else:
            return f'if {str(self.ifExpr)} then {str(self.thenExpr)} else {str(self.elseExpr)}'


class Fun(SyntaxNode):
    def __init__(self, var, expr, is_paren: bool):
        super().__init__(is_paren)
        self.var = var
        self.expr = expr

    def __str__(self):
        if self.is_paren:
            return f'(fun {str(self.var)} -> {str(self.expr)})'
        else:
            return f'fun {str(self.var)} -> {str(self.expr)}'


class VarApp(SyntaxNode):
    def __init__(self, var: SyntaxNode, expr: SyntaxNode, is_paren: bool):
        super().__init__(is_paren)
        self.var = var
        self.expr = expr

    def __str__(self):
        if self.is_paren:
            return f'({str(self.var)} {str(self.expr)})'
        else:
            return f'{str(self.var)} {str(self.expr)}'


class Let(SyntaxNode):
    def __init__(self, var: Var, fun: SyntaxNode, in_expr: SyntaxNode, is_paren: bool):
        super().__init__(is_paren)
        self.var = var
        self.fun = fun
        self.in_expr = in_expr

    def __str__(self):
        if self.is_paren:
            return f'(let {str(self.var)} = {str(self.fun)} in {str(self.in_expr)})'
        else:
            return f'let {str(self.var)} = {str(self.fun)} in {str(self.in_expr)}'


class RecFun(SyntaxNode):
    def __init__(self, var, fun, in_expr, is_paren: bool):
        super().__init__(is_paren)
        self.var = var
        self.fun = fun
        self.in_expr = in_expr

    def __str__(self):
        if self.is_paren:
            return f'(let rec {str(self.var)} = {str(self.fun)} in {str(self.in_expr)})'
        else:
            return f'let rec {str(self.var)} = {str(self.fun)} in {str(self.in_expr)}'
