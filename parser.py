from stree import *
from env import *
from typing import Optional
import re

open_closures = {TokenType.OPEN_PAREN: TokenType.CLOSE_PAREN,
                 TokenType.LET: TokenType.IN,
                 TokenType.IF: TokenType.THEN,
                 TokenType.THEN: TokenType.ELSE,
                 TokenType.MATCH: TokenType.WITH}

close_closures = {TokenType.CLOSE_PAREN: TokenType.OPEN_PAREN,
                  TokenType.IN: TokenType.LET,
                  TokenType.THEN: TokenType.IF,
                  TokenType.ELSE: TokenType.THEN,
                  TokenType.WITH: TokenType.MATCH}

bop = [TokenType.LT, TokenType.MINUS, TokenType.PLUS, TokenType.ASTERISK, TokenType.ARROW, TokenType.EQ]


# Parser object keeps track of current token, checks if the code matches the grammar, and emits code along the way.
def parse_env_token(tokens: [Token]) -> Optional[Env]:
    if not tokens:
        return None
    var = tokens[0]
    val = tokens[2::]

    if len(val) == 1:
        if val[0].kind == TokenType.BOOL:
            val = EnvBool(val[0])
            return Env(TokenType.BOOL, var, val)
        elif val[0].kind == TokenType.NUMBER:
            val = EnvNum(val[0])
            return Env(TokenType.NUMBER, var, val)
        elif val[0].kind == TokenType.DOUBLE_BRACKET:
            val = EnvNil()
            return Env(TokenType.DOUBLE_BRACKET, var, val)

    stack = []
    for i, token in enumerate(val):
        # Bracket not considered as a closure in this case
        if token.kind in close_closures:
            if not stack or stack[-1].kind != close_closures[token.kind]:
                sys.exit("Error! Closure not match")
            else:
                stack.pop()
        if token.kind in open_closures:
            stack.append(token)

        if token.kind == TokenType.REC:
            if not stack:
                rec = EnvRec(val)
                return Env(TokenType.REC, var, rec)
        elif token.kind == TokenType.FUN:
            if not stack:
                fun = EnvFun(val)
                return Env(TokenType.FUN, var, fun)
        elif token.kind == TokenType.DOUBLE_COLON:
            if not stack:
                li = EnvList(val[0:i], val[i+1::])
                return Env(TokenType.DOUBLE_COLON, var, li)

    # Remove outer parenthesis
    return parse_env_token(tokens[0:2] + val[1:-1])


class Parser:
    @staticmethod
    def validate_expression(expr: [Token]):
        if not expr:
            return False
        stack = []
        for token in expr:
            if token.kind in close_closures:
                if not stack or stack[-1].kind != close_closures[token.kind]:
                    return False
                stack.pop()
            if token.kind in open_closures:
                stack.append(token)

        return not stack

    @staticmethod
    def match_parts(s):
        # Regex to match the first balanced parentheses part
        env_pattern = re.compile(r'^\((.*)\)\s*\[(.*)\]$', re.DOTALL)

        match = env_pattern.match(s)
        # Find the first balanced parentheses part

        envs = match.group(1).strip()
        function_expr = match.group(2).strip()

        # Regex to match the "rec x = fun y -> e0" or "fun x -> e0" part
        rec_fun_pattern = re.compile(r'rec\s+(\S+)\s*=\s*fun\s+(\S+)\s*->\s*(.*)')
        fun_pattern = re.compile(r'fun\s+(\S+)\s*->\s*(.*)')

        # Check for the "rec x = fun y -> e0" pattern
        rec_fun_match = rec_fun_pattern.search(function_expr)
        if rec_fun_match:
            rec_var = rec_fun_match.group(1)
            fun_var = rec_fun_match.group(2)
            expr = rec_fun_match.group(3)
            return envs, rec_var, fun_var, expr
        else:
            # Check for the "fun x -> e0" pattern
            fun_match = fun_pattern.search(function_expr)
            if fun_match:
                fun_var = fun_match.group(1)
                expr = fun_match.group(2)
                return envs, None, fun_var, expr

        return envs, None, None, None

    def parse_func(self, func_expr) -> (EnvCollection, Var, Var, SyntaxNode):
        envs_str, rec_var_str, fun_var_str, expr_str = self.match_parts(func_expr)
        envs = self.parse_env(envs_str)
        var = self.parse_program(fun_var_str)
        expr = self.parse_program(expr_str)

        if rec_var_str:
            rec = self.parse_program(rec_var_str)
            return envs, rec, var, expr
        else:
            return envs, None, var, expr

    def parse_env(self, env_expr: str) -> EnvCollection:
        stack = 0
        env_start = 0
        env_list = EnvCollection()

        if not env_expr:
            return env_list

        for i, s in enumerate(env_expr):
            if s == '(':
                stack += 1
            elif s == ')':
                if stack == 0:
                    self.abort("Env: Invalid parenthesis " + env_expr)
                else:
                    stack -= 1
            elif s == ',':
                if stack == 0:
                    env = env_expr[env_start:i]
                    env_start = i+1
                    env_lex = Lexer(env)
                    parsed_env = parse_env_token(env_lex.get_tokens())
                    if parsed_env is not None:
                        env_list.append(parsed_env)

        env = env_expr[env_start::]
        env_lex = Lexer(env)
        parsed_env = parse_env_token(env_lex.get_tokens())
        env_list.append(parsed_env)
        return env_list

    def parse_program(self, program: str) -> SyntaxNode:
        program_lex = Lexer(program)
        program_tokens = program_lex.get_tokens()
        program_root = self.parse_program_token(program_tokens)
        return program_root

    def parse_program_token(self, tokens, is_paren=False) -> Optional[SyntaxNode]:
        stack = []
        if len(tokens) == 0:
            return SyntaxNode(False)
        if len(tokens) == 1:
            token = tokens[0]
            if token.kind == TokenType.NUMBER:
                return Num(token.text, is_paren)
            elif token.kind == TokenType.IDENT:
                return Var(token.text, is_paren)
            elif token.kind == TokenType.BOOL:
                return Bool(token.text, is_paren)
            elif token.kind == TokenType.DOUBLE_BRACKET:
                return Nil(is_paren)
        if len(tokens) == 2:
            token = tokens[0]
            if token.kind == TokenType.MINUS:
                return Num(f'-{tokens[1].text}', is_paren)
        for index, token in enumerate(tokens):
            if token.kind == TokenType.OPEN_PAREN:
                stack.append(token)
            elif token.kind == TokenType.CLOSE_PAREN:
                if not stack or stack[-1].kind != TokenType.OPEN_PAREN:
                    self.abort("Unmatched parenthesis")
                stack.pop()
            elif token.kind == TokenType.LT:
                if not stack:
                    left = self.parse_program_token(tokens[0:index])
                    right = self.parse_program_token(tokens[index + 1::])
                    return BinOp(left, token.kind, right, is_paren)
            elif token.kind == TokenType.DOUBLE_COLON:
                if not stack:
                    checker = self.precedence_checker(tokens[index + 1::])
                    if checker == -1:
                        self.abort("Unmatched closures")
                    elif checker >= 1:
                        if Parser.validate_expression(tokens[0:index]):
                            head = self.parse_program_token(tokens[0:index])
                            tail = self.parse_program_token(tokens[index + 1::])
                            return ListNode(head, tail, is_paren)
            elif token.kind == TokenType.PLUS or token.kind == TokenType.MINUS:
                if not stack:
                    checker = self.precedence_checker(tokens[index + 1::])
                    if checker == -1:
                        self.abort("Unmatched closures")
                    elif checker > 2:
                        if Parser.validate_expression(tokens[0:index]):
                            left = self.parse_program_token(tokens[0:index])
                            right = self.parse_program_token(tokens[index + 1::])
                            return BinOp(left, token.kind, right, is_paren)
            elif token.kind == TokenType.ASTERISK:
                if not stack:
                    checker = self.precedence_checker(tokens[index + 1::])
                    if checker == -1:
                        self.abort("Unmatched closures")
                    elif checker > 3:
                        left = self.parse_program_token(tokens[0:index])
                        right = self.parse_program_token(tokens[index + 1::])
                        return BinOp(left, token.kind, right, is_paren)
            elif token.kind == TokenType.IF:
                if not stack:
                    index_then = self.matcher(tokens[index+1::], open_closures[TokenType.IF], index+1)
                    index_else = self.matcher(tokens[index_then+1::], open_closures[TokenType.THEN], index_then+1)
                    if_expr = self.parse_program_token(tokens[index + 1:index_then])
                    then_expr = self.parse_program_token(tokens[index_then + 1:index_else])
                    else_expr = self.parse_program_token(tokens[index_else + 1::])
                    return IfThenElse(if_expr, then_expr, else_expr, is_paren)
            elif token.kind == TokenType.LET:
                if not stack:
                    if tokens[index+1].kind == TokenType.REC:
                        # let rec var = fun in  expr
                        # i_l 1   2   3 4   i_n 1
                        index_in = self.matcher(tokens[index + 2::], open_closures[token.kind], index + 2)
                        if index_in == -1:
                            self.abort("Unmatched syntax Rec")
                        var = self.parse_program_token([tokens[index + 2]])
                        fun = self.parse_program_token(tokens[index + 4:index_in])
                        expr = self.parse_program_token(tokens[index_in + 1::])
                        return RecFun(var, fun, expr, is_paren)
                    else:
                        # let var = fun in  expr
                        # i_l 1   2 3   i_n 1
                        index_in = self.matcher(tokens[index+1::], open_closures[token.kind], index+1)
                        if index_in == -1:
                            self.abort("Unmatched syntax Let")
                        var = self.parse_program_token([tokens[index + 1]])
                        fun = self.parse_program_token(tokens[index + 3:index_in])
                        expr = self.parse_program_token(tokens[index_in + 1::])
                        assert (isinstance(var, Var))
                        return Let(var, fun, expr, is_paren)
            elif token.kind == TokenType.MATCH:
                index_with = self.matcher(tokens[index + 1::], open_closures[token.kind], index + 1)
                if index_with == -1:
                    self.abort("Unmatched syntax Match")
                index_or = self.matcher(tokens[index_with + 1::], TokenType.BAR, index_with + 1)
                if index_or == -1:
                    self.abort("Unmatched syntax Match")
                match_expr = self.parse_program_token(tokens[index + 1:index_with])

                index_nil_arr = self.matcher(tokens[index_with + 1:index_or], TokenType.ARROW, index_with + 1)
                nil_var = self.parse_program_token([tokens[index_with + 1]])
                nil_expr = self.parse_program_token(tokens[index_nil_arr + 1:index_or])
                nil = With(nil_var, nil_expr, False)

                index_cons_arr = self.matcher(tokens[index_or + 1::], TokenType.ARROW, index_or + 1)
                cons_var = self.parse_program_token(tokens[index_or + 1:index_cons_arr])
                cons_expr = self.parse_program_token(tokens[index_cons_arr + 1::])
                cons = With(cons_var, cons_expr, False)
                return Match(match_expr, nil, cons, is_paren)
            elif token.kind == TokenType.FUN:
                if not stack:
                    var = self.parse_program_token([tokens[index + 1]])
                    expr = self.parse_program_token(tokens[index + 3::])
                    return Fun(var, expr, is_paren)
            elif token.kind == TokenType.IDENT:
                if not stack:
                    #test = self.precedence_checker(tokens[index + 1::])
                    if self.precedence_checker(tokens[index + 1::]) == 4:
                        sub_stack = []
                        for sub_index, sub_token in enumerate(tokens[index + 1::]):
                            if sub_token.kind == TokenType.LET or sub_token.kind == TokenType.IF:
                                if not sub_stack:
                                    var = self.parse_program_token(token[index:sub_index])
                                    expr = self.parse_program_token(tokens[sub_index::])
                                    return VarApp(var, expr, is_paren)
                            elif sub_token.kind == TokenType.OPEN_PAREN:
                                sub_stack.append(sub_token)
                            elif sub_token.kind == TokenType.CLOSE_PAREN:
                                if not sub_stack or sub_stack[-1].kind != TokenType.OPEN_PAREN:
                                    self.abort("Unmatched parenthesis")
                                sub_stack.pop()

                        i = len(tokens) - 1
                        if tokens[i].kind == TokenType.CLOSE_PAREN:
                            sub_stack.append(tokens[i])
                            i -= 1
                            while sub_stack:
                                if tokens[i].kind == TokenType.CLOSE_PAREN:
                                    sub_stack.append(tokens[i])
                                elif tokens[i].kind == TokenType.OPEN_PAREN:
                                    if not sub_stack or sub_stack[-1].kind != TokenType.CLOSE_PAREN:
                                        self.abort("Unmatched parenthesis")
                                    sub_stack.pop()
                                i -= 1
                            var = self.parse_program_token(tokens[index:i + 1])
                            expr = self.parse_program_token(tokens[i + 1::])
                            return VarApp(var, expr, is_paren)
                        else:
                            var = self.parse_program_token(tokens[index:-1])
                            expr = self.parse_program_token(tokens[-1::])
                            return VarApp(var, expr, is_paren)
                    else:
                        continue

        return self.parse_program_token(tokens[1:-1], True)

    @staticmethod
    def matcher(tokens, token_type, start_index):
        stack = []
        for i, token in enumerate(tokens):
            if token.kind in close_closures:
                if not stack or stack[-1].kind != close_closures[token.kind]:
                    if token.kind == token_type:
                        return i + start_index
                    else:
                        return -1
                else:
                    stack.pop()
            if token.kind in open_closures:
                stack.append(token)
            if token.kind == token_type:
                if not stack:
                    return i + start_index

        return -1

    @staticmethod
    def precedence_checker(tokens):
        stack = []
        flag = False
        for i, token in enumerate(tokens):
            if token.kind in close_closures:
                if not stack or stack[-1].kind != close_closures[token.kind]:
                    return -1
                else:
                    stack.pop()
            if token.kind in open_closures:
                if token.kind == TokenType.LET or token.kind == TokenType.IF or token.kind == TokenType.MATCH:
                    if not stack:
                        flag = True
                stack.append(token)
            if token.kind == TokenType.LT:
                if not stack and not flag:
                    return 0
            elif token.kind == TokenType.DOUBLE_COLON:
                if not stack and not flag:
                    return 1
            elif token.kind == TokenType.PLUS or token.kind == TokenType.MINUS:
                if not stack and not flag:
                    return 2
            elif token.kind == TokenType.ASTERISK:
                if not stack and not flag:
                    return 3
        return 4

    @staticmethod
    def abort(message):
        sys.exit("Error! " + message)


class OpType(enum.Enum):
    PLUS = 1
    MINUS = 2
    ASTERISK = 3
    LT = 4
    APP = 5
