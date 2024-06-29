from lexer import *
from syntax_tree import *

open_closures = {TokenType.OPEN_PAREN: TokenType.CLOSE_PAREN,
                 TokenType.LET: TokenType.IN,
                 TokenType.IF: TokenType.THEN,
                 TokenType.THEN: TokenType.ELSE}

close_closures = {TokenType.CLOSE_PAREN: TokenType.OPEN_PAREN,
                  TokenType.LET: TokenType.IN,
                  TokenType.ELSE: TokenType.THEN,
                  TokenType.THEN: TokenType.IF}


# Parser object keeps track of current token, checks if the code matches the grammar, and emits code along the way.
class Parser:
    def __init__(self, lexer, compiler):
        self.lexer = lexer
        self.compiler = compiler

        self.symbols = set()  # All variables we have declared so far.
        self.labelsDeclared = set()  # Keep track of all labels declared

        self.cur_token = None
        self.peekToken = None
        self.next_token()
        self.next_token()  # Call this twice to initialize current and peek.

    def parse(self, tokens):
        stack = []

        if len(tokens) == 1:
            token = tokens.first()
            if token.kind == TokenType.NUMBER:
                return Num(token.text)
            elif token.kind == TokenType.IDENT:
                return Var(token.text)
            elif token.kind == TokenType.BOOL:
                return Bool(token.text)

        for index, token in tokens:
            if token.kind == TokenType.OPEN_PAREN:
                stack.append(token)
            elif token.kind == TokenType.CLOSE_PAREN:
                if not stack or stack[-1] != TokenType.OPEN_PAREN:
                    self.abort("Unmatched parenthesis")
                stack.pop()
            elif token.kind == TokenType.PLUS or token.kind == TokenType.MINUS:
                if not stack:
                    left = self.parse(tokens[::index])
                    right = self.parse(tokens[index+1::])
                    return BinOp(left, token.kind, right)
            elif token.kind == TokenType.ASTERISK:
                if not stack and self.is_root(tokens[index+1::]):
                    left = self.parse(tokens[::index])
                    right = self.parse(tokens[index+1::])
                    return BinOp(left, token.kind, right)
            elif token.kind == TokenType.IF:
                if not stack:
                    index_then = self.matcher(tokens[1::], open_closures[token.kind])
                    index_else = self.matcher(tokens[index_then::], open_closures[TokenType.THEN])
                    if_expr = self.parse(tokens[::index_then])
                    then_expr = self.parse(tokens[index_then+1:index_else])
                    else_expr = self.parse(tokens[index_then+1::])
                    return IfThenElse(if_expr, then_expr, else_expr)
            elif token.kind == TokenType.LET:
                if not stack:
                    index_in = self.matcher(tokens[1::], open_closures[token.kind])
                    if index_in == -1:
                        self.abort("Unmatched syntax Let")
                    var = self.parse([tokens[1]])
                    fun = self.parse(tokens[3:index_in])
                    expr = self.parse(tokens[index_in+1::])
                    return Let(var, fun, expr)
            elif token.kind == TokenType.REC:
                if not stack:
                    index_in = self.matcher(tokens[1::], open_closures[token.kind])
                    if index_in == -1:
                        self.abort("Unmatched syntax Rec")
                    var = self.parse([tokens[1]])
                    fun = self.parse(tokens[3:index_in])
                    expr = self.parse(tokens[index_in + 1::])
                    return RecFun(var, fun, expr)

    @staticmethod
    def matcher(tokens, close_type):
        stack = []
        for i, token in tokens:
            if token.kind in open_closures:
                stack.append(token)
            elif token.kind in close_closures:
                if not stack or stack[-1].kind != close_closures[token.kind]:
                    if token.kind == close_type:
                        return i
                    else:
                        return -1
        return -1

    @staticmethod
    def is_root(tokens):
        stack = []
        for i, token in tokens:
            if token.kind in open_closures:
                stack.append(token)
            elif token.kind in close_closures:
                if not stack or stack[-1].kind != close_closures[token.kind]:
                    return -1
            elif token.kind == TokenType.PLUS or token == TokenType.MINUS:
                if not stack:
                    return 0
        return 1

    # Return true if the current token matches.
    def check_token(self, kind):
        return kind == self.cur_token.kind

    # Return true if the next token matches.
    def check_peek(self, kind):
        return kind == self.peekToken.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind):
        if not self.check_token(kind):
            self.abort("Expected " + kind.name + ", got " + self.cur_token.kind.name)

    # Advances the current token.
    def next_token(self):
        self.cur_token = self.peekToken
        self.peekToken = self.lexer.get_token()
        # No need to worry about passing the EOF, lexer handles that.

    # Return true if the current token is a comparison operator.
    def is_comparison_operator(self):
        return self.check_token(TokenType.LT)

    @staticmethod
    def abort(message):
        sys.exit("Error! " + message)


class OpType(enum.Enum):
    PLUS = 1
    MINUS = 2
    ASTERISK = 3
    LT = 4
    APP = 5
