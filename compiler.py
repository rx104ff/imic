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
    def eval_int(environment, expr):
        value = expr
        evalto = f'{environment} |- {expr} evalto {value} by E-Int{{}};\n'
        return value, evalto

    @staticmethod
    def eval_bool(environment: str, expr: str) -> (any, str):
        value = expr
        evalto = f'{environment} |- {expr} evalto {value} by E-bool{{}};\n'
        return value, evalto

    @staticmethod
    def eval_var1(environment: str, expr: str, val: str) -> (any, str):
        evalto = f'{environment} |- {expr} evalto {val} by E-Var1{{}};\n'
        return val, evalto

    @staticmethod
    def eval_var2(environment: str, expr: str, sub_expr: str, val: str, depth: int) -> (any, str):
        evalto = (f'{environment} |- {expr} evalto {val} by E-Var2{{\n'
                  f'{Compiler.base_indent * depth}{sub_expr}'
                  f'{Compiler.base_indent * (depth-1)}}};\n')
        return val, evalto

    @staticmethod
    def eval_plus(environment: str,
                  expr_1: str, expr_2: str,
                  sub_expr_1: str, sub_expr_2: str,
                  val_1: str, val_2: str,
                  depth: int) -> (any, str):
        value = Compiler.parse_int(val_1) + Compiler.parse_int(val_2)
        evalto = (f'{environment} |- {expr_1} + {expr_2} evalto {value} by E-Plus {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * depth}{val_1} plus {val_2} is {value} by B-Plus {{}};\n'
                  f'{Compiler.base_indent * (depth-1)}}};\n')
        return value, evalto

    @staticmethod
    def eval_minus(environment: str,
                   expr_1: str, expr_2: str,
                   sub_expr_1: str, sub_expr_2: str,
                   val_1: str, val_2: str,
                   depth: int) -> (any, str):
        value = Compiler.parse_int(val_1) - Compiler.parse_int(val_2)
        evalto = (f'{environment} |- {expr_1} - {expr_2} evalto {value} by E-Minus {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * depth}{val_1} minus {val_2} is {value} by B-Minus {{}}; \n'
                  f'{Compiler.base_indent * (depth-1)}}};\n')
        return value, evalto

    @staticmethod
    def eval_times(environment: str,
                   expr_1: str, expr_2: str,
                   sub_expr_1: str, sub_expr_2: str,
                   val_1: str, val_2: str,
                   depth: int) -> (any, str):
        value = Compiler.parse_int(val_1) * Compiler.parse_int(val_2)
        evalto = (f'{environment} |- {expr_1} * {expr_2} evalto {value} by E-Times {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * depth}{val_1} times {val_2} is {value} by B-Times {{}}; \n'
                  f'{Compiler.base_indent * (depth-1)}}};\n')

        return value, evalto

    @staticmethod
    def eval_lt(environment: str,
                expr_1: str, expr_2: str,
                sub_expr_1: str, sub_expr_2: str,
                val_1: str, val_2: str,
                depth: int) -> (any, str):
        value = Compiler.parse_int(val_1) < Compiler.parse_int(val_2)
        evalto = (f'{environment} |- {expr_1} < {expr_2} evalto {value} by E-Lt {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * depth}{val_1} less than {val_2} is {value} by B-Lt {{}};\n'
                  f'{Compiler.base_indent * (depth-1)}}};\n')

        return value, evalto

    @staticmethod
    def eval_let(environment: str, ident: str,
                 expr_1: str, expr_2: str,
                 sub_expr_1: str, sub_expr_2: str,
                 val: str,
                 depth: int) -> (any, str):
        evalto = (f'{environment} |- let {ident} = {expr_1} in {expr_2} evalto {val} by E-Let {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * (depth-1)}}};\n')

        return val, evalto

    @staticmethod
    def eval_if_true(environment: str,
                     if_expr: str, then_expr: str, else_expr: str,
                     sub_expr_1: str, sub_expr_2: str,
                     val: str,
                     depth: int) -> (any, str):

        evalto = (f'{environment} |- if {if_expr} then {then_expr} else {else_expr} evalto {val} by E-IfT {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * (depth-1)}}};\n')

        return val, evalto

    @staticmethod
    def eval_if_false(environment: str,
                      expr_1: str, expr_2: str, expr_3: str,
                      sub_expr_1: str, sub_expr_2: str,
                      val: str,
                      depth: int) -> (any, str):

        evalto = (f'{environment} |- if {expr_1} then {expr_2} else {expr_3} evalto {val} by E-IfF {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * (depth-1)}}};\n')

        return val, evalto

    @staticmethod
    def eval_fun(environment, ident, expr):
        value = f'({environment})[fun {ident} -> {expr}]'
        evalto = f'{environment} |- fun {ident} -> {expr} evalto {value} by E-Fun{{}}; \n'
        return value, evalto

    @staticmethod
    def eval_app(environment,
                 ident: str, expr: str,
                 sub_expr_1: str, sub_expr_2: str, sub_expr_3: str,
                 val: str,
                 depth: int) -> (any, str):
        evalto = (f'{environment} |- {ident} {expr} evalto {val} by E-App {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * depth}{sub_expr_3}'
                  f'{Compiler.base_indent * (depth-1)}}};\n')
        return val, evalto

    @staticmethod
    def eval_let_rec(environment: str,
                     ident_1: str, ident_2: str,
                     expr_1: str, expr_2: str,
                     sub_expr: str,
                     val: str,
                     depth: int):
        evalto = (
            f'{environment} |- let rec {ident_1} = fun {ident_2} -> {expr_1} in {expr_2} evalto {val} by E-LetRec {{\n'
            f'{Compiler.base_indent * depth}{sub_expr}'
            f'{Compiler.base_indent * (depth-1)}}};\n')
        return val, evalto

    @staticmethod
    def eval_rec(environment, ident_1, ident_2, expr):
        value = f"""{ident_1} = ({environment})[rec {ident_1} = fun {ident_2} -> {expr}]"""
        return value

    @staticmethod
    def eval_app_rec(environment,
                     expr_1: str, expr_2: str,
                     sub_expr_1: str, sub_expr_2: str, sub_expr_3: str,
                     val: str,
                     depth: int) -> (any, str):
        evalto = (f'{environment} |- {expr_1} {expr_2} evalto {val} by E-AppRec {{\n'
                  f'{Compiler.base_indent * depth}{sub_expr_1}'
                  f'{Compiler.base_indent * depth}{sub_expr_2}'
                  f'{Compiler.base_indent * depth}{sub_expr_3}'
                  f'{Compiler.base_indent * (depth-1)}}};\n')
        return val, evalto
