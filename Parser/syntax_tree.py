from graphviz import Digraph


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


class VarApp(SyntaxNode):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr


class Fun(SyntaxNode):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr


class Let(SyntaxNode):
    def __init__(self, var, fun, in_expr):
        self.var = var
        self.fun = fun
        self.in_expr = in_expr


class RecFun(SyntaxNode):
    def __init__(self, var, fun, in_expr):
        self.var = var
        self.fun = fun
        self.in_expr = in_expr
