from PolyTypingML.compiler import Compiler
from env import *
from parser import Parser, parse_type_token
from stree import *
import re


def find_free(expr: str):
    # Use regex to find all occurrences of ' followed by a lowercase letter
    matches = re.findall(r"'[a-z]", expr)

    # Convert the list of matches to a set to remove duplicates
    return set(matches)


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


def flat_replace_env_var(expr: str, env_var: EnvVariableDict, env_free_var: FreeEnvVariableDict):
    def flat(_env: TypeEnvBase, _env_var, _env_free_var):
        if isinstance(_env, TypeEnvFun):
            return f'{flat(_env.left, _env_var, _env_free_var)} -> {flat(_env.right, _env_var, _env_free_var)}'
        elif isinstance(_env, TypeEnvList):
            return f'{flat(_env.list_type, _env_var, _env_free_var)} list'
        elif isinstance(_env, TypeEnvVariable):
            if _env in _env_free_var:
                return str(env_free_var[_env])
        else:
            return str(_env)

    for key in env_var:
        s = flat(env_var[key], env_var, env_free_var)
        expr = expr.replace(str(key), s)
    return expr


def flat_free(inferred: TypeEnvBase, env_free_var: FreeEnvVariableDict):
    if isinstance(inferred, TypeEnvFun):
        return f'{flat_free(inferred.left, env_free_var)} -> {flat_free(inferred.right, env_free_var)}'
    elif isinstance(inferred, TypeEnvList):
        return f'{flat_free(inferred.list_type, env_free_var)} list'
    elif isinstance(inferred, TypeEnvVariable):
        if inferred in env_free_var and str(inferred) != str(env_free_var[inferred]):
            return flat_free(env_free_var[inferred], env_free_var)
        else:
            return str(inferred)
    return str(inferred)


def unify(inferred_1: TypeEnvBase, inferred_2: TypeEnvBase, env_var: EnvVariableDict, env_free_var: FreeEnvVariableDict):
    def check_has_var(env: TypeEnvBase):
        if isinstance(env, TypeEnvVariable):
            if env in env_var:
                if str(env_var[env]) == str(env):
                    key = env_free_var.add_entry()
                    _, type_type = parse_type_token(Lexer(key).get_tokens())
                    env_var[env] = type_type
                    return type_type
                else:
                    return env_var[env]
            else:
                return env
        elif isinstance(env, TypeEnvFun):
            return check_has_var(env.left) >> check_has_var(env.right)
        elif isinstance(env, TypeEnvList):
            return TypeEnvList(check_has_var(env.list_type), False)
        else:
            return env
    if isinstance(inferred_1, TypeEnvFun) and isinstance(inferred_2, TypeEnvFun):
        unify(inferred_1.left, inferred_2.left, env_var, env_free_var)
        unify(inferred_1.right, inferred_2.right, env_var, env_free_var)
    if isinstance(inferred_1, TypeEnvList) and isinstance(inferred_2, TypeEnvList):
        unify(inferred_1.list_type, inferred_2.list_type, env_var, env_free_var)
    if isinstance(inferred_1, TypeEnvVariable):
        if isinstance(inferred_2, TypeEnvFun) or isinstance(inferred_2, TypeEnvList):
            inferred_2.is_paren = True
        if inferred_1 in env_free_var:
            inferred_2 = check_has_var(inferred_2)
            if inferred_2 in env_free_var:
                if str(inferred_1) > str(inferred_2):
                    val = env_free_var[inferred_2]
                    if isinstance(val, TypeEnvFun):
                        val.is_paren = True
                    env_free_var[inferred_1] = val
                else:
                    val = env_free_var[inferred_1]
                    if isinstance(val, TypeEnvFun):
                        val.is_paren = True
                    env_free_var[inferred_2] = val
            else:
                if str(inferred_1) in find_free(flat_free(inferred_2, env_free_var)):
                    pass
                else:
                    env_free_var[inferred_1] = inferred_2
        elif inferred_1 in env_var:
            if isinstance(env_var[inferred_1], TypeEnvVariable) and str(inferred_1) == str(env_var[inferred_1]):
                if isinstance(inferred_2, TypeEnvVariable):
                    if inferred_2 in env_var:
                        # flatten
                        val = env_var[inferred_2]
                        if isinstance(val, TypeEnvFun):
                            val.is_paren = True
                        env_var[inferred_1] = val
                    else:
                        env_var[inferred_1] = inferred_2
                else:
                    env_var[inferred_1] = inferred_2
            else:
                unify(env_var[inferred_1], inferred_2, env_var, env_free_var)
    if isinstance(inferred_2, TypeEnvVariable):
        if isinstance(inferred_1, TypeEnvFun) or isinstance(inferred_1, TypeEnvList):
            inferred_1.is_paren = True
        if inferred_2 in env_free_var:
            inferred_1 = check_has_var(inferred_1)
            if inferred_1 in env_free_var:
                if str(inferred_1) > str(inferred_2):
                    val = env_free_var[inferred_2]
                    if isinstance(val, TypeEnvFun):
                        val.is_paren = True
                    env_free_var[inferred_1] = val
                else:
                    val = env_free_var[inferred_1]
                    if isinstance(val, TypeEnvFun):
                        val.is_paren = True
                    env_free_var[inferred_2] = val
            else:
                if str(inferred_2) in find_free(flat_free(inferred_1, env_free_var)):
                    pass
                else:
                    env_free_var[inferred_2] = inferred_1
        elif inferred_2 in env_var:
            if isinstance(env_var[inferred_2], TypeEnvVariable) and str(inferred_2) == str(env_var[inferred_2]):
                if isinstance(inferred_1, TypeEnvVariable):
                    if inferred_1 in env_var:
                        # flatten
                        val = env_var[inferred_1]
                        if isinstance(val, TypeEnvFun):
                            val.is_paren = True
                        env_var[inferred_2] = val
                    else:
                        env_var[inferred_2] = inferred_1
                else:
                    env_var[inferred_2] = inferred_1
            else:
                unify(env_var[inferred_2], inferred_1, env_var, env_free_var)
    else:
        pass


def master_unify(inferred: TypeEnvBase, env: TypeEnvBase, env_var: EnvVariableDict, env_free_var: FreeEnvVariableDict):
    if isinstance(inferred, TypeEnvEmpty):
        return env
    old = str(inferred)
    while True:
        unify(inferred, env, env_var, env_free_var)
        _, inferred = parse_type_token(Lexer(replace_env_var(replace_env_var(str(inferred), env_free_var), env_var)).get_tokens())
        _, env = parse_type_token(Lexer(replace_env_var(replace_env_var(str(env), env_free_var), env_var)).get_tokens())
        if str(inferred) == old:
            break
        old = str(inferred)
    return inferred


def cross_unify(env_free_var_1: FreeEnvVariableDict, env_free_var_2: FreeEnvVariableDict,
                env_var_1: EnvVariableDict, env_var_2: EnvVariableDict):

    def cross(e_1: TypeEnvBase, e_2: TypeEnvBase):
        if isinstance(e_1, TypeEnvFun) and isinstance(e_2, TypeEnvFun):
            cross(e_1.left, e_2.left)
            cross(e_1.right, e_2.right)
        elif isinstance(e_1, TypeEnvList) and isinstance(e_2, TypeEnvList):
            cross(e_1.list_type, e_2.list_type)
        elif isinstance(e_1, TypeEnvVariable) and isinstance(e_2, TypeEnvVariable):
            if str(e_1) == str(env_free_var_1[e_1]) and str(e_2) == str(env_free_var_2[e_2]):
                if str(e_1) > str(e_2):
                    env_free_var_1[e_1] = e_2
                else:
                    env_free_var_2[e_2] = e_1
            else:
                cross(env_free_var_1[e_1], env_free_var_2[e_2])
        if isinstance(e_1, TypeEnvVariable):
            if e_1 in env_free_var_1 and str(e_1) == str(env_free_var_1[e_1]):
                if e_2 in env_free_var_2:
                    env_free_var_1[e_1] = env_free_var_2[e_2]
                else:
                    env_free_var_1[e_1] = e_2
        if isinstance(e_2, TypeEnvVariable):
            if e_2 in env_free_var_2 and str(e_2) == str(env_free_var_2[e_2]):
                if e_1 in env_free_var_1:
                    env_free_var_2[e_2] = env_free_var_1[e_1]
                else:
                    env_free_var_2[e_2] = e_1

    keys = set(env_var_1.keys()).intersection(env_var_2.keys())
    keys = sorted(list(keys))
    for key in keys:
        env_1 = env_var_1[key]
        env_2 = env_var_2[key]
        cross(env_1, env_2)


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
            if str(symbol) in content:
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
        env_free_var_copy = env_free_var.full_copy()
        _, left_expr = p_infer(node.left, TypeEnvBase([Token('int', TokenType.INT)], False), compiler, envs, env_var, env_free_var, depth + 1)
        _, right_expr = p_infer(node.right, TypeEnvBase([Token('int', TokenType.INT)], False), compiler, envs, env_var, env_free_var_copy, depth + 1)
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
        envs_free_var_copy = env_free_var.full_copy()
        if isinstance(inferred, TypeEnvList):
            head_type, expr_head = p_infer(node.head_expr, inferred.list_type, compiler, envs, env_var, env_free_var, depth + 1)
        else:
            head_type, expr_head = p_infer(node.head_expr, TypeEnvEmpty(), compiler, envs, env_var, env_free_var, depth + 1)
        _, head_type = parse_type_token(Lexer(head_type).get_tokens())
        if isinstance(head_type, TypeEnvFun) or isinstance(head_type, TypeEnvList):
            head_type.is_paren = True
        _, new_inferred = parse_type_token(Lexer(f'{head_type} list').get_tokens())
        if not isinstance(inferred, TypeEnvEmpty):
            new_inferred = master_unify(inferred, new_inferred, env_var, env_free_var)
        _, expr_tail = p_infer(node.tail_expr, new_inferred, compiler, envs_copy_1, env_var, envs_free_var_copy, depth + 1)
        return compiler.type_cons(envs_str, str(node), str(expr_head), str(expr_tail), str(new_inferred), depth)
    elif isinstance(node, Match):
        parser = Parser()
        env_free_var_copy = env_free_var.full_copy()
        match_type, match_expr = p_infer(node.match_expr, TypeEnvEmpty(), compiler, envs, env_var, env_free_var, depth + 1)

        alpha = env_var.add_entry()

        assert (isinstance(node.cons_expr.var_expr, ListNode))
        sub_envs = parser.parse_type_env(f'{node.cons_expr.var_expr.head_expr} : {alpha},'
                                         f'{node.cons_expr.var_expr.tail_expr} : {alpha} list')

        envs_str = str(envs + sub_envs)
        nil_type, nil_expr = p_infer(node.nil_expr.evalto_expr, inferred, compiler, envs, env_var, env_free_var, depth + 1)
        _, unifiee_1 = parse_type_token(Lexer(match_type).get_tokens())
        _, unifiee_2 = parse_type_token(Lexer(f'{alpha} list').get_tokens())
        _, unifiee_3 = parse_type_token(Lexer(nil_type).get_tokens())
        unify(unifiee_1, unifiee_2, env_var, env_free_var_copy)
        unify(unifiee_2, unifiee_3, env_var, env_free_var_copy)

        cons_type, cons_expr = p_infer(node.cons_expr.evalto_expr, inferred, compiler, envs + sub_envs, env_var, env_free_var_copy, depth + 1)

        _, unifiee_1 = parse_type_token(Lexer(match_type).get_tokens())
        _, unifiee_2 = parse_type_token(Lexer(f'{alpha} list').get_tokens())


        _, unifiee_4 = parse_type_token(Lexer(cons_type).get_tokens())

        unify(unifiee_1, unifiee_2, env_var, env_free_var_copy)
        unify(unifiee_3, unifiee_4, env_var, env_free_var_copy)

        #unify(unifiee_2, unifiee_4, env_var, env_free_var_copy)
        envs_str = flat_replace_env_var(envs_str, env_var, env_free_var_copy)
        ret_type, ret_expr = compiler.type_match(str(envs), str(node), match_expr, nil_expr, cons_expr, str(nil_type), depth)
        return ret_type, ret_expr
    elif isinstance(node, Let):
        parser = Parser()
        envs_str = str(envs)
        envs_copy = envs.full_copy()
        envs_free_copy = env_free_var.full_copy()
        fun_type, fun_expr = p_infer(node.fun, TypeEnvEmpty(), compiler, envs, env_var, env_free_var, depth + 1)

        for var in env_var:
            if isinstance(env_var[var], TypeEnvVariable) and str(env_var[var]) == str(var):
                free_var = env_free_var.add_entry()
                _, free_type = parse_type_token(Lexer(free_var).get_tokens())
                env_var[var] = free_type

        fun_type = replace_env_var(fun_type, env_var)
        fun_expr = replace_env_var(fun_expr, env_var)

        existing_free = find_free(fun_type)
        env_free_var.keys()
        free = set()
        for env in envs_copy.values():
            if not isinstance(env, TypeEnvFree):
                temp = replace_env_var(str(env), env_var)
                free = free.union(set(find_free(temp)))
        free = existing_free - free
        sub_envs = parser.parse_type_env(f'{node.var.name} : {" ".join(free)}. {fun_type}')
        envs_copy.append(sub_envs)
        in_type, in_expr = p_infer(node.in_expr, inferred, compiler, envs_copy, env_var, env_free_var, depth + 1)

        inferred = master_unify(inferred, in_type, env_var, env_free_var)
        ret_type, ret_expr = compiler.type_let(envs_str, str(node.var), str(node.fun), str(node.in_expr),
                                               fun_expr, in_expr, str(inferred), depth)
        ret_expr = replace_env_var(ret_expr, env_var)
        return ret_type, ret_expr
    elif isinstance(node, RecFun):
        parser = Parser()
        envs_str = str(envs)
        envs_copy_1 = envs.full_copy()
        envs_copy_2 = envs.full_copy()
        envs_free_copy = env_free_var.full_copy()

        # Create type variables
        alpha_1 = env_var.add_entry()
        alpha_2 = env_var.add_entry()

        # Create environments for sub expression inference
        sub_envs_1 = parser.parse_type_env(f'{node.var.name} : {alpha_1}')
        sub_envs_2 = parser.parse_type_env(f'{node.fun.var.name} : {alpha_2}')
        envs_copy_1.append(sub_envs_1).append(sub_envs_2)

        type_expr_1, expr_1 = p_infer(node.fun.expr, TypeEnvEmpty(), compiler, envs_copy_1, env_var, env_free_var, depth + 1)

        for var in env_var:
            if isinstance(env_var[var], TypeEnvVariable) and str(env_var[var]) == str(var):
                free_var = env_free_var.add_entry()
                _, free_type = parse_type_token(Lexer(free_var).get_tokens())
                env_var[var] = free_type

        env_var.flatten_self()

        expr_1 = replace_env_var(expr_1, env_var)
        type_expr_1 = replace_env_var(type_expr_1, env_var)
        new_sub_envs_1 = str(envs_copy_1[node.var.name])
        new_sub_envs_1 = replace_env_var(new_sub_envs_1, env_var)

        free = env_free_var.keys() - envs_free_copy.keys()
        new_sub_envs_1 = parser.parse_type_env(f'{node.var.name} : {" ".join(free)}. {new_sub_envs_1}')

        #new_sub_envs_1 = parser.parse_type_env(f'{node.var.name} : {new_sub_envs_1}')
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
        #ret_expr = replace_env_var(ret_expr, env_var)
        #ret_type = replace_env_var(ret_type, env_var)
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
            _, unifiee_2 = parse_type_token(Lexer(f'({type_2}) -> {alpha}').get_tokens())
            ret = master_unify(unifiee_1, unifiee_2, env_var, env_free_var)
            #unify(unifiee_1, unifiee_2, env_var, env_free_var)

            expr_1 = replace_env_var(expr_1, env_var)
            expr_2 = replace_env_var(expr_2, env_var)

            expr_1 = replace_env_free_var(expr_1, env_free_var)
            expr_2 = replace_env_free_var(expr_2, env_free_var_copy)

            ret_type, ret_expr = compiler.type_app(env_str, str(node.var), str(node.expr), expr_1, expr_2,
                                                   alpha, depth)
            #flatten(env_var, env_free_var)
            #flatten_2(envs, env_free_var)
            ret_type = replace_env_var(ret_type, env_var)
            ret_type = replace_env_var(ret_type, env_free_var)
            ret_type = replace_env_var(ret_type, env_free_var_copy)
            ret_expr = replace_env_var(ret_expr, env_var)
            ret_expr = replace_env_free_var(ret_expr, env_free_var)
            ret_expr = replace_env_free_var(ret_expr, env_free_var_copy)
            #ret_expr = replace_env_var(ret_expr, env_var)
            #ret_expr = replace_env_var(ret_expr, env_free_var_copy)
            return ret_type, ret_expr
        else:
            type_2_var = env_var.add_entry()
            env_var_copy = env_var.full_copy()
            #type_3_var = env_var.add_entry()
            if isinstance(inferred, TypeEnvFun):
                inferred.is_paren = True

            type_1_var = f'{type_2_var} -> {str(inferred)}'

            _, type_1_var = parse_type_token(Lexer(type_1_var).get_tokens())
            _, type_2_var = parse_type_token(Lexer(type_2_var).get_tokens())
            #_, type_3_var = parse_type_token(Lexer(type_3_var).get_tokens())

            envs_copy = envs.full_copy()
            env_free_var_copy = env_free_var.full_copy()
            type_1, expr_1 = p_infer(node.var, type_1_var, compiler, envs, env_var, env_free_var, depth + 1)
            type_2, expr_2 = p_infer(node.expr, type_2_var, compiler, envs_copy, env_var_copy, env_free_var_copy, depth + 1)

            expr_1 = replace_env_var(expr_1, env_var)
            expr_2 = replace_env_var(expr_2, env_var)
            type_1 = replace_env_var(type_1, env_var)
            type_2 = replace_env_var(type_2, env_var)

            #expr_1 = replace_env_free_var(expr_1, env_free_var)
            #type_1 = replace_env_var(type_1, env_free_var)
            #expr_2 = replace_env_free_var(expr_2, env_free_var_copy)
            #type_2 = replace_env_var(type_2, env_free_var_copy)

            _, inf_1 = parse_type_token(Lexer(type_1).get_tokens())
            _, inf_2 = parse_type_token(Lexer(type_2).get_tokens())
            env_var[type_2_var] = inf_2
            if isinstance(inf_2, TypeEnvFun):
                inf_2.is_paren = True
            inf_2 = inf_2 >> inferred

            master_unify(inf_1, inf_2, env_var, env_free_var)
            master_unify(inf_1, inf_2, env_var_copy, env_free_var_copy)
            cross_unify(env_free_var, env_free_var_copy, env_var, env_var_copy)
            #master_unify(type_2_var, type_3_var, env_var, env_free_var)
            #master_unify(type_2_var, type_3_var, env_var, env_free_var_copy)

            expr_1 = replace_env_free_var(expr_1, env_free_var)
            expr_2 = replace_env_free_var(expr_2, env_free_var_copy)

            ret_type, ret_expr = compiler.type_app(env_str, str(node.var), str(node.expr), expr_1, expr_2,
                                                   str(inferred), depth)
            #flatten(env_var, env_free_var)
            #flatten_2(envs, env_free_var)
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
            master_unify(ret, inferred, env_var, env_free_var)

        inf_1_str = str(inf_1)
        inf_2_str = str(inf_2)

        inf_1_str = replace_env_var(inf_1_str, env_var)
        inf_1_str = replace_env_var(inf_1_str, env_free_var)

        inf_2_str = replace_env_var(inf_2_str, env_var)
        inf_2_str = replace_env_var(inf_2_str, env_free_var)

        expr_expr = replace_env_var(expr_expr, env_var)
        #expr_expr = replace_env_var(expr_expr, env_free_var)

        inferred_type, expr = compiler.type_fun(env_str, node.var, node.expr, str(inf_1_str),
                                                str(inf_2_str), expr_expr, depth)

        #flatten(env_var, env_free_var)
        #flatten_2(envs, env_free_var)
        return inferred_type, expr
    elif isinstance(node, Num):
        return compiler.type_int(str(envs), str(node))
    elif isinstance(node, Bool):
        return compiler.type_bool(str(envs), str(node))
    elif isinstance(node, Nil):
        if isinstance(inferred, TypeEnvEmpty):
            alpha = env_var.add_entry()
            return compiler.type_nil(str(envs), str(node), f'{alpha} list')
        return compiler.type_nil(str(envs), str(node), str(inferred))
    elif isinstance(node, Var):
        env = envs[node.name]
        if isinstance(env, str):
            _, env = parse_type_token(Lexer(env).get_tokens(), False)
        elif isinstance(env, TypeEnvFree):
            env = env.expr
        if isinstance(inferred, TypeEnvEmpty):
            return compiler.type_var(str(envs), str(node), str(env))
        else:
            ret = str(inferred)
            _, inferred = parse_type_token(Lexer(replace_env_var(str(inferred), env_var)).get_tokens())

            inferred = master_unify(inferred, env, env_var, env_free_var)

            return compiler.type_var(str(envs), str(node), str(ret))
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

