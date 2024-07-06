from syntax_tree import *
from env_list import *
from typing import Optional
import re

open_closures = {TokenType.OPEN_PAREN: TokenType.CLOSE_PAREN,
                 TokenType.LET: TokenType.IN,
                 TokenType.IF: TokenType.THEN,
                 TokenType.THEN: TokenType.ELSE}

close_closures = {TokenType.CLOSE_PAREN: TokenType.OPEN_PAREN,
                  TokenType.IN: TokenType.LET,
                  TokenType.THEN: TokenType.IF,
                  TokenType.ELSE: TokenType.THEN}

bop = [TokenType.LT, TokenType.MINUS, TokenType.PLUS, TokenType.ASTERISK, TokenType.ARROW, TokenType.EQ]


# Parser object keeps track of current token, checks if the code matches the grammar, and emits code along the way.
class Parser:
    @staticmethod
    def match_parts(s):
        # Regex to match the first balanced parentheses part
        paren_pattern = re.compile(r'\(([^()]*(\([^()]*\))*[^()]*)\)')
        # Find the first balanced parentheses part
        paren_match = paren_pattern.search(s)
        if paren_match:
            envs = paren_match.group(1)
            remaining_string = s[paren_match.end():]  # Get the remaining string after the matched parentheses
        else:
            envs = None
            remaining_string = s

        # Regex to match the "rec x = fun y -> e0" or "fun x -> e0" part
        rec_fun_pattern = re.compile(r'\[rec\s+(\w+)\s*=\s*fun\s+(\w+)\s*->\s*(.*?)\]')
        fun_pattern = re.compile(r'\[fun\s+(\w+)\s*->\s*(.*?)\]')

        # Check for the "rec x = fun y -> e0" pattern
        rec_fun_match = rec_fun_pattern.search(remaining_string)
        if rec_fun_match:
            rec_var = rec_fun_match.group(1)
            fun_var = rec_fun_match.group(2)
            expr = rec_fun_match.group(3)
            return envs, rec_var, fun_var, expr
        else:
            # Check for the "fun x -> e0" pattern
            fun_match = fun_pattern.search(remaining_string)
            if fun_match:
                fun_var = fun_match.group(1)
                expr = fun_match.group(2)
                return envs, None, fun_var, expr

        return envs, None, None, None

    def parse_func(self, func_expr) -> (EnvList, Optional[Var], Var, SyntaxNode):
        envs_str, rec_var_str, fun_var_str, expr_str = self.match_parts(func_expr)
        envs = self.parse_env(envs_str)
        var = self.parse_program(fun_var_str)
        expr = self.parse_program(expr_str)

        if rec_var_str:
            rec = self.parse_program(rec_var_str)
            return envs, rec, var, expr
        else:
            return envs, var, expr

    def parse_env(self, env_expr: str) -> EnvList:
        stack = 0
        env_start = 0
        env_list = EnvList()

        for i, s in enumerate(env_expr):
            if s == '(':
                stack += 1
            elif s == ')':
                if stack == 0:
                    self.abort("Invalid parenthesis")
            elif s == ',':
                env = env_expr[env_start:i]
                env_start = i+1
                env_lex = Lexer(env)
                parsed_env = self.parse_env_token(env_lex.get_tokens())
                if parsed_env is not None:
                    env_list.append(parsed_env)

        return env_list

    def parse_program(self, program: str) -> SyntaxNode:
        program_lex = Lexer(program)
        program_tokens = program_lex.get_tokens()
        program_root = self.parse_program_token(program_tokens)
        return program_root

    def parse_env_token(self, tokens: [Token]) -> Optional[Env]:
        if not tokens:
            return None
        var = tokens[0]
        val = tokens[2::]
        kinds = [token.kind for token in tokens]
        if TokenType.REC in kinds:
            return Env(TokenType.REC, var, val)
        elif TokenType.FUN in kinds:
            return Env(TokenType.FUN, var, val)
        elif tokens[2].kind == TokenType.BOOL:
            return Env(TokenType.BOOL, var, val)
        elif tokens[2].kind == TokenType.NUMBER:
            return Env(TokenType.NUMBER, var, val)
        else:
            self.abort("Invalid environment")

    def parse_program_token(self, tokens, is_paren=False) -> SyntaxNode:
        stack = []
        if len(tokens) == 1:
            token = tokens[0]
            if token.kind == TokenType.NUMBER:
                return Num(token.text, is_paren)
            elif token.kind == TokenType.IDENT:
                return Var(token.text, is_paren)
            elif token.kind == TokenType.BOOL:
                return Bool(token.text, is_paren)
        for index, token in enumerate(tokens):
            if token.kind == TokenType.OPEN_PAREN:
                stack.append(token)
            elif token.kind == TokenType.CLOSE_PAREN:
                if not stack or stack[-1].kind != TokenType.OPEN_PAREN:
                    self.abort("Unmatched parenthesis")
                stack.pop()
            elif token.kind == TokenType.PLUS or token.kind == TokenType.MINUS or token.kind == TokenType.LT:
                if not stack:
                    left = self.parse_program_token(tokens[0:index])
                    right = self.parse_program_token(tokens[index + 1::])
                    return BinOp(left, token.kind, right, is_paren)
            elif token.kind == TokenType.ASTERISK:
                if not stack:
                    checker = self.is_root(tokens[index + 1::])
                    if checker == -1:
                        self.abort("Unmatched closures")
                    elif checker == 1:
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
            elif token.kind == TokenType.FUN:
                if not stack:
                    var = self.parse_program_token([tokens[index + 1]])
                    expr = self.parse_program_token(tokens[index + 3::])
                    return Fun(var, expr, is_paren)
            elif token.kind == TokenType.IDENT:
                if not stack:
                    if tokens[index+1].kind not in bop:
                        if self.is_root(tokens[index + 1::]) == 1:
                            var = self.parse_program_token([token])
                            expr = self.parse_program_token(tokens[index + 1::])
                            assert (isinstance(var, Var))
                            return VarApp(var, expr, is_paren)

        return self.parse_program_token(tokens[1:-1], True)

    @staticmethod
    def matcher(tokens, close_type, start_index):
        stack = []
        for i, token in enumerate(tokens):
            if token.kind in close_closures:
                if not stack or stack[-1].kind != close_closures[token.kind]:
                    if token.kind == close_type:
                        return i + start_index
                    else:
                        return -1
                else:
                    stack.pop()
            if token.kind in open_closures:
                stack.append(token)

        return -1

    @staticmethod
    def is_root(tokens):
        stack = []
        for i, token in enumerate(tokens):
            if token.kind in close_closures:
                if not stack or stack[-1].kind != close_closures[token.kind]:
                    return -1
                else:
                    stack.pop()
            if token.kind in open_closures:
                stack.append(token)
            if token.kind == TokenType.PLUS or token == TokenType.MINUS:
                if not stack:
                    return 0
        return 1

    @staticmethod
    def abort(message):
        sys.exit("Error! " + message)


class OpType(enum.Enum):
    PLUS = 1
    MINUS = 2
    ASTERISK = 3
    LT = 4
    APP = 5
