from PolyTypingML.compiler import Compiler
from env import *
from parser import Parser, parse_type_token
from stree import *
import re


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


def unify(inferred_1: TypeEnvBase, inferred_2: TypeEnvBase, env_var: EnvVariableDict, env_free_var: FreeEnvVariableDict):
    def check_has_var(env: TypeEnvBase):
        if isinstance(env, TypeEnvVariable):
            return True
        elif isinstance(env, TypeEnvFun):
            return check_has_var(env.left) or check_has_var(env.right)
        elif isinstance(env, TypeEnvList):
            return check_has_var(env.list_type)
        else:
            return False
    if isinstance(inferred_1, TypeEnvFun) and isinstance(inferred_2, TypeEnvFun):
        unify(inferred_1.left, inferred_2.left, env_var, env_free_var)
        unify(inferred_1.right, inferred_2.right, env_var, env_free_var)
    elif isinstance(inferred_1, TypeEnvList) and isinstance(inferred_2, TypeEnvList):
        unify(inferred_1.list_type, inferred_2.list_type, env_var, env_free_var)
    elif isinstance(inferred_1, TypeEnvVariable):
        if isinstance(inferred_2, TypeEnvFun) or isinstance(inferred_2, TypeEnvList):
            inferred_2.is_paren = True
        if inferred_1 in env_free_var and (not check_has_var(inferred_2)):
            env_free_var[inferred_1] = inferred_2
        elif inferred_1 in env_var:
            if isinstance(env_var[inferred_1], TypeEnvVariable):
                env_var[inferred_1] = inferred_2
    elif isinstance(inferred_2, TypeEnvVariable):
        if isinstance(inferred_1, TypeEnvFun) or isinstance(inferred_1, TypeEnvList):
            inferred_1.is_paren = True
        if inferred_2 in env_free_var and (not check_has_var(inferred_1)):
            env_free_var[inferred_2] = inferred_1
        elif inferred_2 in env_var:
            if isinstance(env_var[inferred_2], TypeEnvVariable):
                env_var[inferred_2] = inferred_1
    else:
        pass


def master_unify(inferred: TypeEnvBase, env: TypeEnvBase, env_var: EnvVariableDict, env_free_var: FreeEnvVariableDict):
    old = str(inferred)
    while True:
        unify(inferred, env, env_var, env_free_var)
        _, inferred = parse_type_token(Lexer(replace_env_var(replace_env_var(str(inferred), env_free_var), env_var)).get_tokens())
        _, env = parse_type_token(Lexer(replace_env_var(replace_env_var(str(env), env_free_var), env_var)).get_tokens())
        if str(inferred) == old:
            break
        old = str(inferred)
    return inferred


def flatten(env_var: EnvVariableDict, env_free_var: FreeEnvVariableDict):
    def resolve_type_env(node, dictionary):
        if isinstance(node, TypeEnvVariable):
            while str(node) in dictionary and str(node) != str(dictionary[node]):
                node = resolve_type_env(dictionary[node], dictionary)
            return node
        elif isinstance(node, TypeEnvFun):
            left = resolve_type_env(node.left, dictionary)
            right = resolve_type_env(node.right, dictionary)
            ret = left >> right
            ret.is_paren = node.is_paren
            return ret
        elif isinstance(node, TypeEnvList):
            list_type = resolve_type_env(node.list_type, dictionary)
            if isinstance(list_type, TypeEnvFun) or isinstance(list_type, TypeEnvList):
                list_type.is_paren = True
            node.list_type = list_type
            return node
        return node

    flat_dict = {}

    for key in env_var:
        flat_dict[key] = resolve_type_env(env_var[key], env_free_var)

    env_var.clear()
    env_var.update(flat_dict)


def flatten_2(envs: EnvCollection, env_free_var: FreeEnvVariableDict):
    def resolve_type_env(node, dictionary):
        if isinstance(node, TypeEnvVariable):
            while str(node) in dictionary and str(node) != str(dictionary[node]):
                node = resolve_type_env(dictionary[node], dictionary)
            return node
        elif isinstance(node, TypeEnvFun):
            left = resolve_type_env(node.left, dictionary)
            right = resolve_type_env(node.right, dictionary)
            ret = left >> right
            ret.is_paren = node.is_paren
            return ret
        elif isinstance(node, TypeEnvList):
            list_type = resolve_type_env(node.list_type, dictionary)
            if isinstance(list_type, TypeEnvFun) or isinstance(list_type, TypeEnvList):
                list_type.is_paren = True
            node.list_type = list_type
            return node
        return node

    flat_dict = {}

    for key in envs:
        env = envs[key]
        if isinstance(env, TypeEnvFree):
            flat_dict[key] = envs[key]
        else:
            flat_dict[key] = resolve_type_env(envs[key], env_free_var)

    envs.clear()
    envs.update(flat_dict)


def replace_env_free_var(expr: str, env_free_var: FreeEnvVariableDict):
    def replace_symbols(match):
        content = match.group(1)  # Get all content inside the closure
        for symbol, replacement in env_free_var.items():
            if symbol in content:
                # Replace the symbol with its corresponding value
                content = content.replace(str(symbol), str(replacement))
        return f"|- {content}\n"

    # Regular expression to match everything between |- and \n
    pattern = re.compile(r"\|-\s*(.*?)\s*\n", re.DOTALL)

    # Apply the replacement using the function
    expr = pattern.sub(replace_symbols, expr)

    return expr


def p_infer(node: SyntaxNode, inferred: TypeEnvBase, compiler: Compiler, envs: EnvCollection, env_var: EnvVariableDict, env_free_var: FreeEnvVariableDict, depth=1) -> (any, str):
    #print(f'{envs} |- {node} : {str(inferred)}')
    env_var.flatten_self()
    if node is None:
        pass

    if isinstance(node, BinOp):
        # Infer base types, int for +|-|*, bool for if else then
        _, left_expr = p_infer(node.left, TypeEnvBase([Token('int', TokenType.INT)], False), compiler, envs, env_var, env_free_var, depth + 1)
        _, right_expr = p_infer(node.right, TypeEnvBase([Token('int', TokenType.INT)], False), compiler, envs, env_var, env_free_var, depth + 1)
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
    elif isinstance(node, IfThenElse):
        if_type, if_expr = p_infer(node.ifExpr, TypeEnvBase([Token('bool', TokenType.BOOL)], False), compiler, envs, env_var, env_free_var, depth + 1)
        then_type, then_expr = p_infer(node.thenExpr, inferred, compiler, envs, env_var, env_free_var, depth + 1)
        else_type, else_expr = p_infer(node.elseExpr, inferred, compiler, envs, env_var, env_free_var, depth + 1)
        return compiler.type_if(str(envs), str(node.ifExpr), str(node.thenExpr), str(node.elseExpr),
                                if_expr, then_expr, else_expr, str(then_type), depth)
    elif isinstance(node, ListNode):
        envs_str = str(envs)
        envs_copy_1 = envs.full_copy()
        head_type, expr_head = p_infer(node.head_expr, TypeEnvEmpty(), compiler, envs, env_var, env_free_var, depth + 1)
        _, new_inferred = parse_type_token(Lexer(f'({head_type}) list').get_tokens())
        _, expr_tail = p_infer(node.tail_expr, new_inferred, compiler, envs_copy_1, env_var, env_free_var, depth + 1)
        return compiler.type_cons(envs_str, str(node), str(expr_head), str(expr_tail), str(new_inferred), depth)
    elif isinstance(node, Match):
        parser = Parser()

        match_type, match_expr = p_infer(node.match_expr, TypeEnvEmpty(), compiler, envs, env_var, env_free_var, depth + 1)
        nil_type, nil_expr = p_infer(node.nil_expr.evalto_expr, inferred, compiler, envs, env_var, env_free_var, depth + 1)

        alpha = env_var.add_entry()

        assert (isinstance(node.cons_expr.var_expr, ListNode))
        sub_envs = parser.parse_type_env(f'{node.cons_expr.var_expr.head_expr} : {alpha},'
                                         f'{node.cons_expr.var_expr.tail_expr} : {alpha} list')

        cons_type, cons_expr = p_infer(node.cons_expr.evalto_expr, inferred, compiler, envs + sub_envs, env_var, env_free_var, depth + 1)

        _, unifiee_1 = parse_type_token(Lexer(match_type).get_tokens())
        _, unifiee_2 = parse_type_token(Lexer(f'{alpha} list').get_tokens())
        _, unifiee_3 = parse_type_token(Lexer(nil_type).get_tokens())
        _, unifiee_4 = parse_type_token(Lexer(cons_type).get_tokens())

        unify(unifiee_1, unifiee_2, env_var, env_free_var)
        unify(unifiee_3, unifiee_4, env_var, env_free_var)
        ret_type, ret_expr = compiler.type_match(str(envs), str(node), match_expr, nil_expr, cons_expr, str(nil_type), depth)
        return ret_type, ret_expr
    elif isinstance(node, Let):
        parser = Parser()
        envs_str = str(envs)
        envs_copy = envs.full_copy()
        envs_free_copy = env_free_var.full_copy()
        fun_type, fun_expr = p_infer(node.fun, TypeEnvEmpty(), compiler, envs, env_var, env_free_var, depth + 1)
        fun_type = replace_env_var(fun_type, env_var)

        free = env_free_var.keys() - envs_free_copy.keys()
        sub_envs = parser.parse_type_env(f'{node.var.name} : {" ".join(free)}. {fun_type}')
        envs_copy.append(sub_envs)
        in_type, in_expr = p_infer(node.in_expr, inferred, compiler, envs_copy, env_var, env_free_var, depth + 1)
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

        # Create environments for sub expression inference
        sub_envs_1 = parser.parse_type_env(f'{node.var.name} : {alpha_1}')
        sub_envs_2 = parser.parse_type_env(f'{node.fun.var.name} : {alpha_2}')
        envs_copy_1.append(sub_envs_1).append(sub_envs_2)

        type_expr_1, expr_1 = p_infer(node.fun.expr, TypeEnvEmpty(), compiler, envs_copy_1, env_var, env_free_var, depth + 1)
        expr_1 = replace_env_var(expr_1, env_var)
        type_expr_1 = replace_env_var(type_expr_1, env_var)
        new_sub_envs_1 = str(envs_copy_1[node.var.name])
        new_sub_envs_1 = replace_env_var(new_sub_envs_1, env_var)
        new_sub_envs_1 = parser.parse_type_env(f'{node.var.name} : {new_sub_envs_1}')
        envs_copy_2.append(new_sub_envs_1)

        type_expr_2, expr_2 = p_infer(node.in_expr, inferred, compiler, envs_copy_2, env_var, env_free_var, depth + 1)
        expr_2 = replace_env_var(expr_2, env_var)
        type_expr_2 = replace_env_var(type_expr_2, env_var)

        # Parse into type env class
        _, inf_1 = parse_type_token(Lexer(type_expr_1).get_tokens())
        _, inf_2 = parse_type_token(Lexer(type_expr_2).get_tokens())

        if isinstance(inf_1, TypeEnvFun):
            inf_1.is_paren = True

        # Unify inferences
        unify(env_var[alpha_1], env_var[alpha_2] >> inf_1, env_var, env_free_var)
        unify(inf_2, inferred, env_var, env_free_var)

        ret_type, ret_expr = compiler.type_let_rec(envs_str, str(node.var), str(node.fun.var), str(node.fun.expr), str(node.in_expr),
                                                   expr_1, expr_2, str(inferred), depth)
        ret_expr = replace_env_var(ret_expr, env_var)
        ret_type = replace_env_var(ret_type, env_var)
        return ret_type, ret_expr
    elif isinstance(node, VarApp):
        env_str = str(envs)
        if isinstance(inferred, TypeEnvEmpty):
            env_free_var_copy = env_free_var.full_copy()
            # Infer the left
            type_1, expr_1 = p_infer(node.var, inferred, compiler, envs, env_var, env_free_var, depth + 1)
            # Infer the right
            type_2, expr_2 = p_infer(node.expr, inferred, compiler, envs, env_var, env_free_var_copy, depth + 1)

            # if type_2 in env_var.keys():
            alpha = env_var.add_entry()

            # Unify inferred types
            _, unifiee_1 = parse_type_token(Lexer(type_1).get_tokens())
            _, unifiee_2 = parse_type_token(Lexer(f'{type_2} -> {alpha}').get_tokens())
            ret = master_unify(unifiee_1, unifiee_2, env_var, env_free_var)
            #unify(unifiee_1, unifiee_2, env_var, env_free_var)

            expr_1 = replace_env_var(expr_1, env_var)
            expr_2 = replace_env_var(expr_2, env_var)

            expr_1 = replace_env_free_var(expr_1, env_free_var)
            expr_2 = replace_env_free_var(expr_2, env_free_var_copy)

            ret_type, ret_expr = compiler.type_app(str(envs), str(node.var), str(node.expr), expr_1, expr_2,
                                                   alpha, depth)
            flatten(env_var, env_free_var)
            flatten_2(envs, env_free_var)
            return ret_type, ret_expr
        else:
            type_2_var = env_var.add_entry()
            if isinstance(inferred, TypeEnvFun):
                inferred.is_paren = True

            type_1_var = f'{type_2_var} -> {str(inferred)}'

            _, type_1_var = parse_type_token(Lexer(type_1_var).get_tokens())
            _, type_2_var = parse_type_token(Lexer(type_2_var).get_tokens())
            envs_copy = envs.full_copy()
            env_free_var_copy = env_free_var.full_copy()
            type_1, expr_1 = p_infer(node.var, type_1_var, compiler, envs, env_var, env_free_var, depth + 1)
            type_2, expr_2 = p_infer(node.expr, type_2_var, compiler, envs_copy, env_var, env_free_var_copy, depth + 1)

            expr_1 = replace_env_var(expr_1, env_var)
            expr_2 = replace_env_var(expr_2, env_var)
            type_1 = replace_env_var(type_1, env_var)
            type_2 = replace_env_var(type_2, env_var)

            expr_1 = replace_env_free_var(expr_1, env_free_var)
            type_1 = replace_env_var(type_1, env_free_var)
            expr_2 = replace_env_free_var(expr_2, env_free_var_copy)
            type_2 = replace_env_var(type_2, env_free_var_copy)

            _, inf_1 = parse_type_token(Lexer(type_1).get_tokens())
            _, inf_2 = parse_type_token(Lexer(type_2).get_tokens())
            env_var[type_2_var] = inf_2
            if isinstance(inf_2, TypeEnvFun):
                inf_2.is_paren = True
            inf_2 = inf_2 >> inferred

            unify(inf_1, inf_2, env_var, env_free_var)
            ret_type, ret_expr = compiler.type_app(env_str, str(node.var), str(node.expr), expr_1, expr_2,
                                                   str(inferred), depth)
            flatten(env_var, env_free_var)
            flatten_2(envs, env_free_var)
            ret_expr = replace_env_var(ret_expr, env_var)
            ret_type = replace_env_var(ret_type, env_var)
            return ret_type, ret_expr
    elif isinstance(node, Fun):
        env_str = str(envs)
        alpha = env_var.add_entry()
        _, alpha_type = parse_type_token(Lexer(alpha).get_tokens())
        envs[node.var] = alpha_type

        if isinstance(inferred, TypeEnvFun):
            right_type = inferred.right
            expr_type, expr_expr = p_infer(node.expr, right_type, compiler, envs, env_var, env_free_var, depth + 1)
        else:
            expr_type, expr_expr = p_infer(node.expr, inferred, compiler, envs, env_var, env_free_var, depth + 1)

        _, inf_1 = parse_type_token(Lexer(str(envs[node.var])).get_tokens())
        _, inf_2 = parse_type_token(Lexer(expr_type).get_tokens())
        if isinstance(inf_2, TypeEnvFun):
            inf_2.is_paren = True

        if not isinstance(inferred, TypeEnvEmpty):
            ret = inf_1 >> inf_2
            unify(ret, inferred, env_var, env_free_var)
        inferred_type, expr = compiler.type_fun(env_str, node.var, node.expr, str(inf_1),
                                                str(inf_2), expr_expr, depth)

        for var in env_var:
            if isinstance(env_var[var], TypeEnvVariable) and str(env_var[var]) == str(var):
                free_var = env_free_var.add_entry()
                _, free_type = parse_type_token(Lexer(free_var).get_tokens())
                env_var[var] = free_type

        for alpha in env_var:
            expr = expr.replace(str(alpha), f'{env_var[alpha]}')
        flatten(env_var, env_free_var)
        flatten_2(envs, env_free_var)
        return inferred_type, expr
    elif isinstance(node, Num):
        return compiler.type_int(str(envs), str(node))
    elif isinstance(node, Bool):
        return compiler.type_bool(str(envs), str(node))
    elif isinstance(node, Nil):
        if isinstance(inferred, TypeEnvEmpty):
            alpha = env_var.add_entry()
            return compiler.type_nil(str(envs), str(node), str(alpha))
        return compiler.type_nil(str(envs), str(node), str(inferred))
    elif isinstance(node, Var):
        if isinstance(inferred, TypeEnvEmpty):
            env = envs[node.name]
            flatten(env_var, env_free_var)
            flatten_2(envs, env_free_var)
            return compiler.type_var(str(envs), str(node), str(env))
        else:
            env = envs[node.name]
            # parse the str env to Env object
            if isinstance(env, str):
                _, env = parse_type_token(Lexer(env).get_tokens(), False)
            elif isinstance(env, TypeEnvFree):
                env = env.expr

            inferred = master_unify(inferred, env, env_var, env_free_var)

            return compiler.type_var(str(envs), str(node), str(inferred))
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
    env_free_var = FreeEnvVariableDict()
    for env in env_list.values():
        if isinstance(env, TypeEnvFree):
            free_vars = env.free_vars
            for free_var in free_vars:
                env_free_var.add_entry_with_key(free_var)

    _, s = p_infer(program_tree, inferred, Compiler(), env_list, env_var, env_free_var)
    return s

