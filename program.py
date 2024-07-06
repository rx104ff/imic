from compiler import Compiler
from env_list import EnvList
from parser import Parser
from syntax_tree import *


def s_compile(node, compiler: Compiler, envs: EnvList) -> (any, str):
    if node is None:
        pass

    if isinstance(node, BinOp):
        left_val, left_expr = s_compile(node.left, compiler, envs)
        right_val, right_expr = s_compile(node.right, compiler, envs)
        if node.op == TokenType.MINUS:
            return compiler.eval_minus(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                       left_val, right_val)
        elif node.op == TokenType.PLUS:
            return compiler.eval_plus(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                      left_val, right_val)
        elif node.op == TokenType.ASTERISK:
            return compiler.eval_times(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                       left_val, right_val)
        elif node.op == TokenType.LT:
            return compiler.eval_lt(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                    left_val, right_val)
    elif isinstance(node, IfThenElse):
        if_val, if_expr = s_compile(node.ifExpr, compiler, envs)
        then_val, then_expr = s_compile(node.thenExpr, compiler, envs)
        else_val, else_expr = s_compile(node.elseExpr, compiler, envs)
        return compiler.eval_if(str(envs), str(node.ifExpr), str(node.thenExpr), str(node.elseExpr), if_expr,
                                then_expr, else_expr, if_val, then_val, else_val)
    elif isinstance(node, Let):
        env_and_fun, fun_expr = compiler.eval_fun(str(envs), str(node.var), str(node.fun))
        parser = Parser()
        sub_envs = parser.parse_env(f'{str(node.var)} = {env_and_fun}')

        val, sub_expr = s_compile(node.in_expr, compiler, envs + sub_envs)
        return compiler.eval_let(str(envs), str(node.var), str(node.fun), str(node.in_expr), fun_expr,
                                 sub_expr, val)
    elif isinstance(node, VarApp):
        val_1, sub_expr_1 = s_compile(node.var, compiler, envs)
        val_2, sub_expr_2 = s_compile(node.expr, compiler, envs)
        parser = Parser()
        sub_envs, sub_rec, sub_var, sub_expr = parser.parse_func(val_1)
        if sub_rec is not None:
            new_env = parser.parse_env(f'{sub_rec.name} = {val_1}, {sub_var} = {val_2}')
            val, expr = s_compile(sub_expr, compiler, sub_envs + new_env)
            return compiler.eval_app_rec(str(envs), str(node.var), str(node.expr), sub_expr_1, sub_expr_2, expr, val)
        else:
            assert(isinstance(sub_var, Var))
            new_env = parser.parse_env(f'{sub_var.name} = {val_2}')
            val, expr = s_compile(sub_expr, compiler, sub_envs + new_env)
            return compiler.eval_app(str(envs), str(node.var), str(node.expr), sub_expr_1, sub_expr_2, expr, val)
    elif isinstance(node, Fun):
        env_and_fun, expr = compiler.eval_fun(str(envs), node.var, node.expr)
        return env_and_fun, expr
    elif isinstance(node, RecFun):
        env_and_fun, fun_expr = compiler.eval_fun(str(envs), node.fun.var, node.fun.expr)
        sub_val, sub_expr = s_compile(node, compiler, envs)
        parser = Parser()
        sub_envs = parser.parse_env(env_and_fun[0])
        sub_envs.append(parser.parse_env_token(Lexer(f'{node.fun.var} = {sub_val}')))
        fun = parser.parse_program(env_and_fun[1])
        val, expr = s_compile(fun, compiler, sub_envs)
        return compiler.eval_app_rec(str(envs), str(node.fun), str(node.in_expr), fun_expr, sub_expr, expr, val)
    elif isinstance(node, Num):
        return compiler.eval_int(str(envs), str(node))
    elif isinstance(node, Var):
        if node.name == envs.get_current().var.text:
            return compiler.eval_var1(str(envs), str(node), envs.get_current_val())
        else:
            val, sub_expr = s_compile(node, compiler, envs.pop())
            return compiler.eval_var2(str(envs), str(node), sub_expr, val)
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
    print(s[1])
    #dot = program_tree.visualize_tree()
    #dot.render('tree', format='png', view=True)