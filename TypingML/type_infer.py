from TypingML.compiler import Compiler
from env import *
from parser import Parser, parse_type_token, parse_promised
from stree import *
import re


def unify(inferred_1: TypeEnvBase, inferred_2: TypeEnvBase, env_var: EnvVariableDict):
    if isinstance(inferred_1, TypeEnvFun) and isinstance(inferred_2, TypeEnvFun):
        unify(inferred_1.left, inferred_2.left, env_var)
        unify(inferred_1.right, inferred_2.right, env_var)
        return
    elif isinstance(inferred_1, TypeEnvList) and isinstance(inferred_2, TypeEnvList):
        return
    elif isinstance(inferred_1, TypeEnvVariable):
        if isinstance(inferred_2, TypeEnvFun):
            inferred_2.is_paren = True
        env_var[inferred_1] = inferred_2
    elif isinstance(inferred_2, TypeEnvVariable):
        if isinstance(inferred_1, TypeEnvFun):
            inferred_1.is_paren = True
        env_var[inferred_2] = inferred_1
    else:
        pass


def replace_env_var(expr: str, env_var: EnvVariableDict):
    while True:
        old = expr
        for key in env_var:
            if isinstance(env_var[key], TypeEnvFun):
                s = f'{env_var[key]}'
            else:
                s = str(env_var[key])
            old = old.replace(str(key), s)
        if old == expr:
            return expr
        expr = old


def s_infer(node: SyntaxNode, inferred: TypeEnvBase, compiler: Compiler, envs: EnvCollection, env_var: EnvVariableDict, depth=1) -> (any, str):
    #print(f'{envs} |- {node} : {str(inferred)}')
    env_var.flatten_self()
    if node is None:
        pass

    if isinstance(node, BinOp):
        _, left_expr = s_infer(node.left, TypeEnvBase([Token('int', TokenType.INT)], False), compiler, envs, env_var, depth + 1)
        _, right_expr = s_infer(node.right, TypeEnvBase([Token('int', TokenType.INT)], False), compiler, envs, env_var, depth + 1)
        if node.op == TokenType.MINUS:
            return compiler.type_minus(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                       depth)
        elif node.op == TokenType.PLUS:
            return compiler.type_plus(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                      depth)
        elif node.op == TokenType.ASTERISK:
            return compiler.type_times(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                       depth)
        elif node.op == TokenType.LT:
            return compiler.type_lt(str(envs), str(node.left), str(node.right), left_expr, right_expr,
                                    depth)
    elif isinstance(node, ListNode):
        head_type, expr_head = s_infer(node.head_expr, TypeEnvEmpty(), compiler, envs, env_var, depth + 1)
        _, new_inferred = parse_type_token(Lexer(f'{head_type} list').get_tokens())
        _, expr_tail = s_infer(node.tail_expr, new_inferred, compiler, envs, env_var, depth + 1)
        return compiler.type_cons(str(envs), str(node), str(expr_head), str(expr_tail), str(new_inferred), depth)
    elif isinstance(node, Match):
        match_type, match_expr = s_infer(node.match_expr, TypeEnvEmpty(), compiler, envs, env_var, depth + 1)
        _, nil_expr = s_infer(node.nil_expr, inferred, compiler, envs, env_var, depth + 1)

        parser = Parser()
        assert (isinstance(node.cons_expr.var_expr, ListNode))
        sub_envs = parser.parse_type_env(f'{node.cons_expr.var_expr.head_expr} : {match_type},'
                                         f'{node.cons_expr.var_expr.tail_expr} : {match_type} list')

        _, cons_expr = s_infer(node.cons_expr, inferred, compiler, envs + sub_envs, env_var, depth + 1)
        return compiler.type_match(str(envs), str(node), match_expr, nil_expr, cons_expr, str(inferred), depth)
    elif isinstance(node, IfThenElse):
        if_type, if_expr = s_infer(node.ifExpr, TypeEnvBase([Token('bool', TokenType.BOOL)], False), compiler, envs, env_var, depth + 1)
        then_type, then_expr = s_infer(node.thenExpr, inferred, compiler, envs, env_var, depth + 1)
        else_type, else_expr = s_infer(node.elseExpr, inferred, compiler, envs, env_var, depth + 1)
        return compiler.type_if(str(envs), str(node.ifExpr), str(node.thenExpr), str(node.elseExpr),
                                if_expr, then_expr, else_expr, str(then_type), depth)
    elif isinstance(node, Let):
        parser = Parser()
        envs_str = str(envs)
        envs_copy = envs.full_copy()
        fun_type, fun_expr = s_infer(node.fun, TypeEnvEmpty(), compiler, envs, env_var, depth + 1)
        fun_type = replace_env_var(fun_type, env_var)
        sub_envs = parser.parse_type_env(f'{node.var.name} : {fun_type}')
        envs_copy.append(sub_envs)
        in_type, in_expr = s_infer(node.in_expr, inferred, compiler, envs_copy, env_var, depth + 1)
        ret_type, ret_expr = compiler.type_let(envs_str, str(node.var), str(node.fun), str(node.in_expr),
                                               fun_expr, in_expr, str(inferred), depth)
        ret_expr = replace_env_var(ret_expr, env_var)
        return ret_type, ret_expr
    elif isinstance(node, RecFun):
        parser = Parser()
        envs_str = str(envs)
        envs_copy_1 = envs.full_copy()
        envs_copy_2 = envs.full_copy()

        # Create type variables
        alpha_1 = env_var.add_entry()
        alpha_2 = env_var.add_entry()

        # Create environments for sub expression inferrence
        sub_envs_1 = parser.parse_type_env(f'{node.var.name} : {alpha_1}')
        sub_envs_2 = parser.parse_type_env(f'{node.fun.var.name} : {alpha_2}')
        envs_copy_1.append(sub_envs_1).append(sub_envs_2)
        envs_copy_2.append(sub_envs_1)

        type_expr_1, expr_1 = s_infer(node.fun.expr, TypeEnvEmpty(), compiler, envs_copy_1 , env_var, depth + 1)
        expr_1 = replace_env_var(expr_1, env_var)
        type_expr_1 = replace_env_var(type_expr_1, env_var)

        type_expr_2, expr_2 = s_infer(node.in_expr, inferred, compiler, envs_copy_2, env_var, depth + 1)
        expr_2 = replace_env_var(expr_2, env_var)
        type_expr_2 = replace_env_var(type_expr_2, env_var)

        # Parse into type env class
        _, inf_1 = parse_type_token(Lexer(type_expr_1).get_tokens())
        _, inf_2 = parse_type_token(Lexer(type_expr_2).get_tokens())

        if isinstance(inf_1, TypeEnvFun):
            inf_1.is_paren = True

        # Unify inferences
        unify(env_var[alpha_1], env_var[alpha_2] >> inf_1, env_var)
        unify(inf_2, inferred, env_var)

        ret_type, ret_expr = compiler.type_let_rec(envs_str, str(node.var), str(node.fun.var), str(node.fun.expr), str(node.in_expr),
                                                   expr_1, expr_2, str(inferred), depth)
        ret_expr = replace_env_var(ret_expr, env_var)
        ret_type = replace_env_var(ret_type, env_var)
        return ret_type, ret_expr
    elif isinstance(node, VarApp):
        env_str = str(envs)
        if isinstance(inferred, TypeEnvEmpty):
            type_1, sub_expr_1 = s_infer(node.var, inferred, compiler, envs, env_var, depth + 1)
            type_2, sub_expr_2 = s_infer(node.expr, inferred, compiler, envs, env_var, depth + 1)
            if type_2 in env_var.keys():
                key = env_var.add_entry()
                _, unifiee_1 = parse_type_token(Lexer(type_1).get_tokens())
                _, unifiee_2 = parse_type_token(Lexer(f'{type_2} -> {key}').get_tokens())
                unify(unifiee_1, unifiee_2, env_var)
                ret_type, ret_expr = compiler.type_app(str(envs), str(node.var), str(node.expr), sub_expr_1, sub_expr_2,
                                                       key, depth)
                return ret_type, ret_expr
        else:
            type_2_var = env_var.add_entry()
            if isinstance(inferred, TypeEnvFun):
                inferred.is_paren = True

            type_1_var = f'{type_2_var} -> {str(inferred)}'

            _, type_1_var = parse_type_token(Lexer(type_1_var).get_tokens())
            _, type_2_var = parse_type_token(Lexer(type_2_var).get_tokens())
            type_1, sub_expr_1 = s_infer(node.var, type_1_var, compiler, envs, env_var, depth + 1)
            type_2, sub_expr_2 = s_infer(node.expr, type_2_var, compiler, envs, env_var, depth + 1)

            for key in env_var:
                sub_expr_1 = sub_expr_1.replace(str(key), f'{env_var[key]}')
                sub_expr_2 = sub_expr_2.replace(str(key), f'{env_var[key]}')
                type_1 = type_1.replace(str(key), f'{env_var[key]}')
                type_2 = type_2.replace(str(key), f'{env_var[key]}')

            _, inf_1 = parse_type_token(Lexer(type_1).get_tokens())
            _, inf_2 = parse_type_token(Lexer(type_2).get_tokens())
            env_var[type_2_var] = inf_2
            if isinstance(inf_2, TypeEnvFun):
                inf_2.is_paren = True
            inf_2 = inf_2 >> inferred

            unify(inf_1, inf_2, env_var)
            ret_type, ret_expr = compiler.type_app(env_str, str(node.var), str(node.expr), sub_expr_1, sub_expr_2,
                                                   str(inferred), depth)
            ret_expr = replace_env_var(ret_expr, env_var)
            ret_type = replace_env_var(ret_type, env_var)
            return ret_type, ret_expr
    elif isinstance(node, Fun):
        env_str = str(envs)
        key = env_var.add_entry()
        envs[node.var] = key

        if isinstance(inferred, TypeEnvFun):
            right_type = inferred.right
            expr_type, expr_expr = s_infer(node.expr, right_type, compiler, envs, env_var, depth + 1)
        else:
            expr_type, expr_expr = s_infer(node.expr, inferred, compiler, envs, env_var, depth + 1)

        _, inf_1 = parse_type_token(Lexer(str(envs[node.var])).get_tokens())
        _, inf_2 = parse_type_token(Lexer(expr_type).get_tokens())
        if isinstance(inf_2, TypeEnvFun):
            inf_2.is_paren = True

        if not isinstance(inferred, TypeEnvEmpty):
            ret = inf_1 >> inf_2
            unify(ret, inferred, env_var)
        inferred_type, expr = compiler.type_fun(env_str, node.var, node.expr, str(inf_1),
                                                str(inf_2), expr_expr, depth)
        for key in env_var:
            expr = expr.replace(str(key), f'{env_var[key]}')
        return inferred_type, expr
    elif isinstance(node, Num):
        return compiler.type_int(str(envs), str(node))
    elif isinstance(node, Bool):
        return compiler.type_bool(str(envs), str(node))
    elif isinstance(node, Nil):
        return compiler.type_nil(str(envs), str(node), str(inferred))
    elif isinstance(node, Var):
        if isinstance(inferred, TypeEnvEmpty):
            env = envs[node.name]
            return compiler.type_var(str(envs), str(node), str(env))
        else:
            env = envs[node.name]
            # parse the str env to Env object
            if isinstance(env, str):
                _, env = parse_type_token(Lexer(env).get_tokens(), False)
            unify(env, inferred, env_var)
            return compiler.type_var(str(envs), str(node), str(env))
    elif isinstance(node, Bool):
        return compiler.type_bool(str(envs), str(node))
    return None


def extract_expression_and_type(input_string):
    # This regex matches the part between `|-` and captures the type after the final `:`
    pattern = r'\|-\s*(.*?)\s*:\s*(.*)\s*$'
    match = re.search(pattern, input_string)

    if match:
        expression = match.group(1).strip()
        type_info = match.group(2).strip()
        return expression, type_info
    return None, None


def infer(prog_input):
    # Pre-processing
    program_expr = prog_input.split("|-")
    env_expr = program_expr[0]
    prg, inferred = extract_expression_and_type(prog_input.replace('::', '$$'))
    inferred = inferred.replace('$$', '::')
    prg = prg.replace('$$', '::')
    inferred_lex = Lexer(inferred)
    inferred_tokens = inferred_lex.get_tokens()
    parser = Parser()

    env_list = parser.parse_type_env(env_expr)
    _, inferred = parse_type_token(inferred_tokens)

    program_tree = parser.parse_program(prg)

    env_var = EnvVariableDict()
    _, s = s_infer(program_tree, inferred, Compiler(), env_list, env_var)

    # This is to replace those cannot be inferred to int
    for key in env_var:
        if isinstance(env_var[key], TypeEnvVariable):
            pass
            s = s.replace(str(key), "int")
    return s

