import regex
from collections import OrderedDict


class Compiler:
    base_indent = "    "

    @staticmethod
    def parse_int(a: any):
        if isinstance(a, int):
            return a
        elif isinstance(a, str):
            return int(a.strip().replace(' ', ''))
        else:
            return int(a)

    @staticmethod
    def parse_fun(fun):
        pattern = r'fun\s+(\w+)\s+->\s+(.*)'
        match = regex.match(pattern, fun)
        if match:
            ident = match.group(1)
            expr = match.group(2)
            return ident, expr
        return None, None

    @staticmethod
    def parse_rec_func(s):
        pattern = r'rec\s+(\w+)\s+=\s+fun\s+(\w+)\s+->\s+(.*)'
        match = regex.match(pattern, s)
        if match:
            ident_1 = match.group(1)
            ident_2 = match.group(2)
            expression = match.group(3)

            return ident_1, ident_2, expression
        return None, None, None

    @staticmethod
    def parse_environment(environment):
        environments = [s.strip() for s in environment.split(',')]
        od = OrderedDict()

        for env in environments:
            if env != '':
                ident = env.split('=', 1)[0].strip()
                expr = env.split('=', 1)[1].strip()
                od[ident] = expr

        return od

    @staticmethod
    def type_int(environment, expr):
        evalto = f'{environment}|- {expr} : int by T-Int{{}};\n'
        return 'int', evalto

    @staticmethod
    def type_nil(environment, expr, inferred_type):
        value = expr
        evalto = f'{environment}|- {expr} : {inferred_type} by T-Nil{{}};\n'
        return inferred_type, evalto

    @staticmethod
    def type_bool(environment: str, expr: str) -> (any, str):
        evalto = f'{environment}|- {expr} : bool by T-Bool{{}};\n'
        return 'bool', evalto

    @staticmethod
    def type_var(environment: str, expr: str, inferred_type: str) -> (any, str):
        evalto = f'{environment}|- {expr} : {inferred_type} by T-Var{{}};\n'
        return inferred_type, evalto

    @staticmethod
    def type_plus(environment: str,
                  expr_1: str, expr_2: str,
                  sub_expr_1: str, sub_expr_2: str,
                  depth: int) -> (any, str):
        evalto = (f'{environment}|- {expr_1} + {expr_2} : int by T-Plus {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * (depth - 1)}}};\n')
        return 'int', evalto

    @staticmethod
    def type_minus(environment: str,
                   expr_1: str, expr_2: str,
                   sub_expr_1: str, sub_expr_2: str,
                   depth: int) -> (any, str):
        evalto = (f'{environment}|- {expr_1} - {expr_2} : int by T-Minus {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * (depth - 1)}}};\n')
        return 'int', evalto

    @staticmethod
    def type_times(environment: str,
                   expr_1: str, expr_2: str,
                   sub_expr_1: str, sub_expr_2: str,
                   depth: int) -> (any, str):
        evalto = (f'{environment}|- {expr_1} * {expr_2} : int by T-Mult {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * (depth - 1)}}};\n')

        return 'int', evalto

    @staticmethod
    def type_lt(environment: str,
                expr_1: str, expr_2: str,
                sub_expr_1: str, sub_expr_2: str,
                depth: int) -> (any, str):
        evalto = (f'{environment}|- {expr_1} < {expr_2} : bool by T-Lt {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * (depth - 1)}}};\n')

        return 'bool', evalto

    @staticmethod
    def type_let(environment: str, ident: str,
                 expr_1: str, expr_2: str,
                 sub_expr_1: str, sub_expr_2: str,
                 inferred_type: str,
                 depth: int) -> (any, str):
        evalto = (f'{environment}|- let {ident} = {expr_1} in {expr_2} : {inferred_type} by T-Let {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * (depth - 1)}}};\n')

        return inferred_type, evalto

    @staticmethod
    def type_cons(environment: str, list_expr: str,
                  head_expr: str, tail_expr: str,
                  inferred_type: str,
                  depth: int) -> (any, str):
        evalto = (f'{environment}|- {list_expr} : {inferred_type} by T-Cons {{\n'
                  f'{Compiler.base_indent * depth}{head_expr}'
                  f'{Compiler.base_indent * depth}{tail_expr}'
                  f'{Compiler.base_indent * (depth - 1)}}};\n')

        return inferred_type, evalto

    @staticmethod
    def type_match(environment: str, match_with_expr: str,
                   match_expr: str, nil_expr: str, cons_expr: str,
                   inferred_type: str,
                   depth: int) -> (any, str):
        evalto = (f'{environment}|- {match_with_expr} : {inferred_type} by T-Match {{\n'
                  f'{Compiler.base_indent * depth}{match_expr}'
                  f'{Compiler.base_indent * depth}{nil_expr}'
                  f'{Compiler.base_indent * depth}{cons_expr}'
                  f'{Compiler.base_indent * (depth - 1)}}};\n')

        return inferred_type, evalto

    @staticmethod
    def type_if(environment: str,
                if_expr: str, then_expr: str, else_expr: str,
                sub_expr_1: str, sub_expr_2: str, sub_expr_3: str,
                inferred_type: str,
                depth: int) -> (any, str):

        evalto = (f'{environment}|- if {if_expr} then {then_expr} else {else_expr} : {inferred_type} by T-If {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * depth}{sub_expr_3}'
                  f'{Compiler.base_indent * (depth - 1)}}};\n')

        return inferred_type, evalto

    @staticmethod
    def type_fun(environment, ident, expr, var_type, expr_type, expr_expr, depth: int):
        inferred_type = f'{var_type} -> {expr_type}'
        return Compiler.type_fun_2(environment, ident, expr, inferred_type, expr_expr, depth)

    @staticmethod
    def type_fun_2(environment, ident, expr, inferred_type, expr_expr, depth: int):
        evalto = (f'{environment}|- fun {ident} -> {expr} : {inferred_type} by T-Abs{{\n'
                  f'{Compiler.base_indent * depth}{expr_expr}'
                  f'{Compiler.base_indent * (depth - 1)}}}; \n')
        return inferred_type, evalto

    @staticmethod
    def type_app(environment,
                 ident: str, expr: str,
                 sub_expr_1: str, sub_expr_2: str,
                 inferred_type: str,
                 depth: int) -> (any, str):
        evalto = (f'{environment}|- {ident} {expr} : {inferred_type} by T-App {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * (depth - 1)}}};\n')
        return inferred_type, evalto

    @staticmethod
    def type_let_rec(environment: str,
                     ident_1: str, ident_2: str,
                     expr_1: str, expr_2: str,
                     sub_expr_1: str, sub_expr_2: str,
                     inferred_type: str,
                     depth: int):
        evalto = (
            f'{environment}|- let rec {ident_1} = fun {ident_2} -> {expr_1} in {expr_2} : {inferred_type} by T-LetRec {{\n'
            f'{Compiler.base_indent * depth}{sub_expr_1}'
            f'{Compiler.base_indent * depth}{sub_expr_2}'
            f'{Compiler.base_indent * (depth - 1)}}};\n')
        return inferred_type, evalto
