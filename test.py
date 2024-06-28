import regex


def parse_rec_fun_expression(rec_fun_expr):
    env_pattern = r'\((?:[^\(\)]|(?R))*\)'
    fun_patter = r'\[(?:[^\[\]]|(?R))*\]'

    env_match = regex.search(env_pattern, rec_fun_expr)
    env = env_match.group(0)
    if len(env) >= 2:
        env = env[1:-1]

    fun_match = regex.search(fun_patter, rec_fun_expr[env_match.end(0)::])
    fun = fun_match.group(0)
    if len(fun) >= 2:
        fun = fun[1:-1]

    ident_1, ident_2, expr = parse_rec_func(fun)

    return env, ident_1, ident_2, expr


def parse_rec_func(s):
    pattern = r'rec\s+(\w+)\s+=\s+fun\s+(\w+)\s+->\s+(.*)'
    match = regex.match(pattern, s)
    if match:
        ident_1 = match.group(1)
        ident_2 = match.group(2)
        expression = match.group(3)

        return ident_1, ident_2, expression
    return None, None, None


s = "((x = 1), y =()[fun z -> z * z])[rec y = fun x -> x * x]"

env, ident_1, ident_2, expr = parse_rec_fun_expression(s)
print(env, ident_1, ident_2, expr)
