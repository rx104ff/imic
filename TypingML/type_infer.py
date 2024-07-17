from TypingML.compiler import Compiler
from env import *
from parser import Parser, parse_type_token
from stree import *
import re


def s_infer(node: SyntaxNode, inferred: EnvType, compiler: Compiler, envs: EnvCollection, depth=1) -> (any, str):
    #print(f'{envs} |- {node} : {str(inferred)}')
    if node is None:
        pass

    if isinstance(node, BinOp):
        _, left_expr = s_infer(node.left, EnvType([Token('int', TokenType.INT)]), compiler, envs, depth + 1)
        _, right_expr = s_infer(node.right, EnvType([Token('int', TokenType.INT)]), compiler, envs, depth + 1)
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
        assert (isinstance(inferred, EnvTypeList))
        _, expr_head = s_infer(node.head_expr, inferred.get_list_type(), compiler, envs, depth + 1)
        _, expr_tail = s_infer(node.tail_expr, inferred, compiler, envs, depth + 1)
        return compiler.type_cons(str(envs), str(node), str(expr_head), str(expr_tail), str(inferred), depth)
    elif isinstance(node, Match):
        match_type, match_expr = s_infer(node.match_expr, EnvTypeEmpty(), compiler, envs, depth + 1)
        _, nil_expr = s_infer(node.nil_expr, inferred, compiler, envs, depth + 1)

        parser = Parser()
        assert (isinstance(node.cons_expr.var_expr, ListNode))
        sub_envs = parser.parse_type_env(f'{node.cons_expr.var_expr.head_expr} : {match_type},'
                                         f'{node.cons_expr.var_expr.tail_expr} : {match_type} list')

        _, cons_expr = s_infer(node.cons_expr, inferred, compiler, envs + sub_envs, depth + 1)
        return compiler.type_match(str(envs), str(node), match_expr, nil_expr, cons_expr, str(inferred), depth)
    elif isinstance(node, IfThenElse):
        if_type, if_expr = s_infer(node.ifExpr, EnvType([Token('bool', TokenType.BOOL)]), compiler, envs, depth + 1)
        then_type, then_expr = s_infer(node.thenExpr, inferred, compiler, envs, depth + 1)
        else_type, else_expr = s_infer(node.elseExpr, inferred, compiler, envs, depth + 1)
        return compiler.type_if(str(envs), str(node.ifExpr), str(node.thenExpr), str(node.elseExpr),
                                if_expr, then_expr, else_expr, str(inferred), depth)
    elif isinstance(node, Let):
        sub_envs = envs.copy().append(TypeEnvPromise(node.var.name))
        sub_type, sub_expr = s_infer(node.in_expr, inferred, compiler, sub_envs, depth + 1)
        sub_expr = sub_expr.replace(f'{node.var.name} : PROMISED', f'{sub_envs}')
        sub_inferred = sub_envs.get_env_by_var(str(node.var.name))
        fun_type, fun_expr = s_infer(node.fun, sub_inferred.val, compiler, envs, depth + 1)
        return compiler.type_let(str(envs), str(node.var), str(node.fun), str(node.in_expr), fun_expr,
                                 sub_expr, str(inferred), depth)
    elif isinstance(node, VarApp):
        type_2, sub_expr_2 = s_infer(node.expr, EnvTypeEmpty(), compiler, envs, depth + 1)
        _, new_inferred = parse_type_token(Lexer(f'{type_2} -> {str(inferred)}').get_tokens())
        type_1, sub_expr_1 = s_infer(node.var, new_inferred, compiler, envs, depth + 1)

        return compiler.type_app(str(envs), str(node.var), str(node.expr), sub_expr_1, sub_expr_2, str(inferred),
                                 depth)
    elif isinstance(node, Fun):
        if isinstance(inferred, EnvTypeEmpty):
            expr_type, expr_expr = s_infer(node.expr, inferred, compiler, envs, depth + 1)
            x,y = compiler.type_fun(str(envs), node.var, node.expr, expr_type, expr_type, expr_expr, depth)
            return x,y
        parser = Parser()

        if isinstance(inferred, EnvTypeFun):
            left_type = inferred.get_left()
            right_type = inferred.get_right()
            _, right_type = parse_type_token(right_type.tokens)
            new_env = parser.parse_type_env(f'{node.var} : {str(left_type)}')
            expr_type, expr_expr = s_infer(node.expr, right_type, compiler, envs + new_env, depth + 1)
            inferred_type, expr = compiler.type_fun_2(str(envs), node.var, node.expr, str(inferred),
                                                      expr_expr, depth)
            return inferred_type, expr
    elif isinstance(node, Num):
        return compiler.type_int(str(envs), str(node))
    elif isinstance(node, Bool):
        return compiler.type_bool(str(envs), str(node))
    elif isinstance(node, Nil):
        return compiler.type_nil(str(envs), str(node))
    elif isinstance(node, Var):
        if envs.is_not_empty and envs.check_var(node.name.text):
            env = envs.get_env_by_var(node.name.text)
            if isinstance(env, TypeEnvPromise):
                envs.set_var(node.name.text, TypeEnv(Env(node.name.kind, node.name, inferred)))
                return compiler.type_var(str(envs), str(node), str(inferred))
            else:
                return compiler.type_var(str(envs), str(node), str(inferred))
        else:
            parser = Parser()
            sub_envs = parser.parse_type_env(f'{str(node.name)} : {str(inferred)}')
            return compiler.type_var(str(envs + sub_envs), str(node), str(inferred))
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
    prg, inferred = extract_expression_and_type(prog_input)
    inferred_lex = Lexer(inferred)
    inferred_tokens = inferred_lex.get_tokens()

    parser = Parser()

    env_list = parser.parse_type_env(env_expr)
    _, inferred = parse_type_token(inferred_tokens)

    program_tree = parser.parse_program(prg)

    s = s_infer(program_tree, inferred, Compiler(), env_list)
    return s[1]
    # dot = program_tree.visualize_tree()
    # dot.render('tree', format='png', view=True)
