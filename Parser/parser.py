from lexer import *
from .syntax_tree import *
from .env_list import *
from typing import Optional

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
    def parse_env(self, tokens: [Token]) -> Optional[Env]:
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

    def parse_program(self, tokens) -> SyntaxNode:
        stack = []
        if len(tokens) == 1:
            token = tokens[0]
            if token.kind == TokenType.NUMBER:
                return Num(token.text)
            elif token.kind == TokenType.IDENT:
                return Var(token.text)
            elif token.kind == TokenType.BOOL:
                return Bool(token.text)
        for index, token in enumerate(tokens):
            if token.kind == TokenType.OPEN_PAREN:
                stack.append(token)
            elif token.kind == TokenType.CLOSE_PAREN:
                if not stack or stack[-1].kind != TokenType.OPEN_PAREN:
                    self.abort("Unmatched parenthesis")
                stack.pop()
            elif token.kind == TokenType.PLUS or token.kind == TokenType.MINUS or token.kind == TokenType.LT:
                if not stack:
                    left = self.parse_program(tokens[0:index])
                    right = self.parse_program(tokens[index + 1::])
                    return BinOp(left, token.kind, right)
            elif token.kind == TokenType.ASTERISK:
                if not stack:
                    checker = self.is_root(tokens[index + 1::])
                    if checker == -1:
                        self.abort("Unmatched closures")
                    elif checker == 1:
                        left = self.parse_program(tokens[0:index])
                        right = self.parse_program(tokens[index + 1::])
                        return BinOp(left, token.kind, right)
            elif token.kind == TokenType.IF:
                if not stack:
                    index_then = self.matcher(tokens[index+1::], open_closures[TokenType.IF], index+1)
                    index_else = self.matcher(tokens[index_then+1::], open_closures[TokenType.THEN], index_then+1)
                    if_expr = self.parse_program(tokens[index + 1:index_then])
                    then_expr = self.parse_program(tokens[index_then + 1:index_else])
                    else_expr = self.parse_program(tokens[index_else + 1::])
                    return IfThenElse(if_expr, then_expr, else_expr)
            elif token.kind == TokenType.LET:
                if not stack:
                    if tokens[index+1].kind == TokenType.REC:
                        # let rec var = fun in  expr
                        # i_l 1   2   3 4   i_n 1
                        index_in = self.matcher(tokens[index + 2::], open_closures[token.kind], index + 2)
                        if index_in == -1:
                            self.abort("Unmatched syntax Rec")
                        var = self.parse_program([tokens[index + 2]])
                        fun = self.parse_program(tokens[index + 4:index_in])
                        expr = self.parse_program(tokens[index_in + 1::])
                        return RecFun(var, fun, expr)
                    else:
                        # let var = fun in  expr
                        # i_l 1   2 3   i_n 1
                        index_in = self.matcher(tokens[index+1::], open_closures[token.kind], index+1)
                        if index_in == -1:
                            self.abort("Unmatched syntax Let")
                        var = self.parse_program([tokens[index + 1]])
                        fun = self.parse_program(tokens[index + 3:index_in])
                        expr = self.parse_program(tokens[index_in + 1::])
                        return Let(var, fun, expr)
            elif token.kind == TokenType.FUN:
                if not stack:
                    var = self.parse_program([tokens[index + 1]])
                    expr = self.parse_program(tokens[index + 3::])
                    return Fun(var, expr)
            elif token.kind == TokenType.IDENT:
                if not stack:
                    if tokens[index+1].kind not in bop:
                        if self.is_root(tokens[index + 1::]) == 1:
                            var = self.parse_program([token])
                            expr = self.parse_program(tokens[index + 1::])
                            return VarApp(var, expr)

        return self.parse_program(tokens[1:-1])

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
