from EvalML.compiler import Compiler
from env import *
from EvalML.parser import Parser
from stree import *


def s_compile(node, compiler: Compiler, envs: EnvCollection, depth=1) -> (any, str):
    #print(f'{envs} |- {node}')
    envs = envs.copy()
    if node is None:
        pass

    #print(f'{envs} |- {node}')
    if isinstance(node, BinOp):
        left_val, left_expr = s_compile(node.left, compiler, envs, depth + 1)
        right_val, right_expr = s_compile(node.right, compiler, envs, depth + 1)
        if node.op == TokenType.MINUS:
            return compiler.eval_minus(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                       left_val, right_val, depth)
        elif node.op == TokenType.PLUS:
            return compiler.eval_plus(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                      left_val, right_val, depth)
        elif node.op == TokenType.ASTERISK:
            return compiler.eval_times(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                       left_val, right_val, depth)
        elif node.op == TokenType.LT:
            return compiler.eval_lt(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                    left_val, right_val, depth)
    elif isinstance(node, ListNode):
        val_head, expr_head = s_compile(node.head_expr, compiler, envs, depth + 1)
        val_tail, expr_tail = s_compile(node.tail_expr, compiler, envs, depth + 1)
        parser = Parser()
        val_head_node = parser.parse_env(f'DUMMYVAR = {val_head}').get_current()
        val_tail_node = parser.parse_env(f'DUMMYVAR = {val_tail}').get_current()
        if not (val_head_node.kind == TokenType.NUMBER or val_head_node.kind == TokenType.DOUBLE_BRACKET):
            val_head = f'({val_head})'
        if not (val_tail_node.kind == TokenType.NUMBER or val_tail_node.kind == TokenType.DOUBLE_BRACKET):
            val_tail = f'({val_tail})'
        return compiler.eval_cons(str(envs), str(node), str(expr_head), str(expr_tail), val_head,
                                  val_tail, depth)
    elif isinstance(node, Match):
        match_val, match_expr = s_compile(node.match_expr, compiler, envs, depth + 1)
        parser = Parser()
        match_token = parser.parse_env(f'DUMMYVAR = {match_val}').get_current()

        # Nil type
        if isinstance(match_token.val, EnvNil):
            val_nil, expr_nil = s_compile(node.nil_expr.evalto_expr, compiler, envs, depth + 1)
            return compiler.eval_match_nil(str(envs), str(node), match_expr, expr_nil, val_nil, depth)
        elif isinstance(match_token.val, EnvList):
            assert(isinstance(node.cons_expr.var_expr, ListNode))
            new_envs = parser.parse_env(f'{node.cons_expr.var_expr.head_expr} = {match_token.val.get_head()}, '
                                        f'{node.cons_expr.var_expr.tail_expr} = {match_token.val.get_tail()}')

            val_cons, expr_cons = s_compile(node.cons_expr.evalto_expr, compiler, envs + new_envs, depth + 1)
            return compiler.eval_match_cons(str(envs), str(node), match_expr, expr_cons, val_cons, depth)
    elif isinstance(node, IfThenElse):
        if_val, if_expr = s_compile(node.ifExpr, compiler, envs, depth + 1)
        if bool(if_val):
            then_val, then_expr = s_compile(node.thenExpr, compiler, envs, depth + 1)
            return compiler.eval_if_true(str(envs), str(node.ifExpr), str(node.thenExpr), str(node.elseExpr),
                                         if_expr, then_expr, then_val, depth)
        else:
            else_val, else_expr = s_compile(node.elseExpr, compiler, envs, depth + 1)
            return compiler.eval_if_false(str(envs), str(node.ifExpr), str(node.thenExpr), str(node.elseExpr),
                                          if_expr, else_expr, else_val, depth)
    elif isinstance(node, Let):
        val_fun, expr_fun = s_compile(node.fun, compiler, envs, depth + 1)

        parser = Parser()
        sub_envs = parser.parse_env(f'{str(node.var)} = {val_fun}')

        val, sub_expr = s_compile(node.in_expr, compiler, envs + sub_envs, depth + 1)
        return compiler.eval_let(str(envs), str(node.var), str(node.fun), str(node.in_expr), expr_fun,
                                 sub_expr, val, depth)
    elif isinstance(node, VarApp):
        val_1, sub_expr_1 = s_compile(node.var, compiler, envs, depth + 1)
        val_2, sub_expr_2 = s_compile(node.expr, compiler, envs, depth + 1)
        parser = Parser()
        sub_envs, sub_rec, sub_var, sub_expr = parser.parse_func(val_1)
        if sub_rec is not None:
            new_env = parser.parse_env(f'{sub_rec.name} = {val_1}, {sub_var} = {val_2}')
            val, expr = s_compile(sub_expr, compiler, sub_envs + new_env, depth + 1)
            return compiler.eval_app_rec(str(envs), str(node.var), str(node.expr), sub_expr_1, sub_expr_2, expr, val,
                                         depth)
        else:
            assert (isinstance(sub_var, Var))
            new_env = parser.parse_env(f'{sub_var.name} = {val_2}')
            val, expr = s_compile(sub_expr, compiler, sub_envs + new_env, depth + 1)
            return compiler.eval_app(str(envs), str(node.var), str(node.expr), sub_expr_1, sub_expr_2, expr, val, depth)
    elif isinstance(node, Fun):
        env_and_fun, expr = compiler.eval_fun(str(envs), node.var, node.expr)
        return env_and_fun, expr
    elif isinstance(node, RecFun):
        parser = Parser()
        val = compiler.eval_rec(str(envs), node.var, node.fun.var, node.fun.expr)
        new_envs = parser.parse_env(val)
        sub_val, sub_expr = s_compile(node.in_expr, compiler, envs + new_envs, depth + 1)
        env_and_fun, fun_expr = compiler.eval_let_rec(str(envs), node.var, node.fun.var, node.fun.expr, node.in_expr,
                                                      sub_expr, sub_val, depth)
        return env_and_fun, fun_expr
    elif isinstance(node, Num):
        return compiler.eval_int(str(envs), str(node))
    elif isinstance(node, Nil):
        return compiler.eval_nil(str(envs), str(node))
    elif isinstance(node, Var):
        if node.name == envs.get_current().var.text:
            return compiler.eval_var1(str(envs), str(node), envs.get_current_val())
        else:
            val, sub_expr = s_compile(node, compiler, envs.copy().pop(), depth + 1)
            return compiler.eval_var2(str(envs), str(node), sub_expr, val, depth)
    elif isinstance(node, Bool):
        return compiler.eval_bool(str(envs), str(node))
    return None


def program(prog_input):
    # Pre-processing
    program_expr = prog_input.split("|-")
    env_expr = program_expr[0]
    prg = program_expr[1].split('evalto')[0]
    val = program_expr[1].split('evalto')[1]

    parser = Parser()

    env_list = parser.parse_env(env_expr)

    program_tree = parser.parse_program(prg)

    s = s_compile(program_tree, Compiler(), env_list)
    return s[1]
    # dot = program_tree.visualize_tree()
    # dot.render('tree', format='png', view=True)
