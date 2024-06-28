from lexer import *


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

    # program
    def program(self):

        # Parse all the statements in the program.
        while not self.check_token(TokenType.EOF):
            return self.statement()

    def statement(self):
        # Check the first token to see what kind of statement this is.

        # "IF" expression "THEN" expression "ELSE" expression
        if self.check_token(TokenType.IF):
            self.next_token()

            expr_1 = ''
            while not self.check_token(TokenType.THEN) and not self.check_token(TokenType.EOF):
                expr_1 += f' {self.cur_token.text}'
                self.next_token()

            self.match(TokenType.THEN)
            self.next_token()
            expr_2 = ''
            while not self.check_token(TokenType.ELSE) and not self.check_token(TokenType.EOF):
                expr_2 += f' {self.cur_token.text}'
                self.next_token()

            self.match(TokenType.ELSE)
            self.next_token()
            expr_3 = ''
            while not self.check_token(TokenType.EOF):
                expr_3 += f' {self.cur_token.text}'
                self.next_token()

            return self.compiler.eval_if(self.compiler.env, expr_1, expr_2, expr_3)

        # "LET" ident = expression "IN" expression
        elif self.check_token(TokenType.LET):
            self.next_token()

            if self.check_token(TokenType.REC):
                self.next_token()

                self.match(TokenType.IDENT)
                ident_1 = self.cur_token.text
                self.next_token()

                self.match(TokenType.EQ)
                self.next_token()

                self.match(TokenType.IDENT)
                ident_2 = self.cur_token.text
                self.next_token()

                self.match(TokenType.FUN)
                self.next_token()

                expr_1 = ''
                while not self.check_token(TokenType.IN) and not self.check_token(TokenType.EOF):
                    expr_1 += f' {self.cur_token.text}'
                    self.next_token()

                self.match(TokenType.IN)
                self.next_token()

                expr_2 = ''
                while not self.check_token(TokenType.EOF):
                    expr_2 += f' {self.cur_token.text}'
                    self.next_token()

                return self.compiler.eval_let_rec(self.compiler.env, ident_1, ident_2, expr_1, expr_2)
            else:
                self.match(TokenType.IDENT)
                ident = self.cur_token.text
                self.next_token()

                self.match(TokenType.EQ)
                self.next_token()

                expr_1 = ''
                while not self.check_token(TokenType.IN) and not self.check_token(TokenType.EOF):
                    expr_1 += f' {self.cur_token.text}'
                    self.next_token()

                self.match(TokenType.IN)
                self.next_token()

                expr_2 = ''
                while not self.check_token(TokenType.EOF):
                    expr_2 += f' {self.cur_token.text}'
                    self.next_token()

                return self.compiler.eval_let(self.compiler.env, ident, expr_1, expr_2)

        # "FUN" fun ident -> expression
        elif self.check_token(TokenType.FUN):
            self.next_token()

            self.match(TokenType.IDENT)
            ident = self.cur_token.text
            self.next_token()

            self.match(TokenType.ARROW)
            self.next_token()

            expr = ''
            while not self.check_token(TokenType.EOF):
                expr += f' {self.cur_token.text}'
                self.next_token()

            return self.compiler.eval_fun(self.compiler.env, ident, expr)

        # expression
        elif self.check_token(TokenType.IDENT):
            expr_1 = self.cur_token.text
            expr_2 = ''
            cur_op = None
            self.next_token()

            while not self.check_token(TokenType.EOF):
                if self.check_token(TokenType.PLUS):
                    if cur_op is None:
                        cur_op = OpType.PLUS
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        expr_1 = f'{expr_1} + {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        cur_op = OpType.PLUS
                        expr_1 = f'{expr_1} - {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        cur_op = OpType.PLUS
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.PLUS
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.LT:
                        expr_2 = f'{expr_2} +'
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.MINUS):
                    if cur_op is None:
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} + {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} - {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.LT:
                        expr_2 = f'{expr_2} -'
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.ASTERISK):
                    if cur_op is None:
                        cur_op = OpType.ASTERISK
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        expr_2 = f'{expr_2} *'
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        expr_2 = f'{expr_2} *'
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.ASTERISK
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.LT:
                        expr_2 = f'{expr_2} *'
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.LT):
                    if cur_op is None:
                        cur_op = OpType.LT
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} + {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} - {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.IDENT) or self.check_token(TokenType.NUMBER):
                    if cur_op is None:
                        cur_op = OpType.APP
                        expr_2 = self.cur_token.text
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        if expr_2 == '':
                            expr_2 = self.cur_token.text
                        else:
                            expr_2 = f'{expr_2} {self.cur_token.text}'
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        if expr_2 == '':
                            expr_2 = self.cur_token.text
                        else:
                            expr_2 = f'{expr_2} {self.cur_token.text}'
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        if expr_2 == '':
                            expr_2 = self.cur_token.text
                        else:
                            expr_2 = f'{expr_2} {self.cur_token.text}'
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = self.cur_token.text
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.OPEN_PAREN):
                    if cur_op is None:
                        cur_op = OpType.APP
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.PLUS:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.MINUS:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.ASTERISK:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.APP:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    else:
                        self.abort("Invalid op")

            if cur_op is None:
                return self.compiler.eval_var(self.compiler.env, expr_1)
            elif cur_op == OpType.PLUS:
                return self.compiler.eval_plus(self.compiler.env, expr_1, expr_2)
            elif cur_op == OpType.MINUS:
                return self.compiler.eval_minus(self.compiler.env, expr_1, expr_2)
            elif cur_op == OpType.ASTERISK:
                return self.compiler.eval_times(self.compiler.env, expr_1, expr_2)
            elif cur_op == OpType.APP:
                return self.compiler.eval_app_base(self.compiler.env, expr_1, expr_2)

        elif self.check_token(TokenType.NUMBER):
            expr_1 = self.cur_token.text
            expr_2 = ''
            cur_op = None
            self.next_token()

            while not self.check_token(TokenType.EOF):
                if self.check_token(TokenType.PLUS):
                    if cur_op is None:
                        cur_op = OpType.PLUS
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        expr_1 = f'{expr_1} + {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        cur_op = OpType.PLUS
                        expr_1 = f'{expr_1} - {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        cur_op = OpType.PLUS
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.LT:
                        expr_2 = f'{expr_2} +'
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.MINUS):
                    if cur_op is None:
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} + {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} - {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.LT:
                        expr_2 = f'{expr_2} -'
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.ASTERISK):
                    if cur_op is None:
                        cur_op = OpType.ASTERISK
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        expr_2 = f'{expr_2} *'
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        expr_2 = f'{expr_2} *'
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.LT:
                        expr_2 = f'{expr_2} *'
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.LT):
                    if cur_op is None:
                        cur_op = OpType.LT
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} + {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} - {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.IDENT) or self.check_token(TokenType.NUMBER):
                    if cur_op == OpType.PLUS:
                        if expr_2 == '':
                            expr_2 = self.cur_token.text
                        else:
                            expr_2 = f'{expr_2} {self.cur_token.text}'
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        if expr_2 == '':
                            expr_2 = self.cur_token.text
                        else:
                            expr_2 = f'{expr_2} {self.cur_token.text}'
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        if expr_2 == '':
                            expr_2 = self.cur_token.text
                        else:
                            expr_2 = f'{expr_2} {self.cur_token.text}'
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.OPEN_PAREN):
                    if cur_op == OpType.PLUS:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.MINUS:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.ASTERISK:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.APP:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    else:
                        self.abort("Invalid op")

            if cur_op is None:
                return self.compiler.eval_int(self.compiler.env, expr_1)
            elif cur_op == OpType.PLUS:
                return self.compiler.eval_plus(self.compiler.env, expr_1, expr_2)
            elif cur_op == OpType.MINUS:
                return self.compiler.eval_minus(self.compiler.env, expr_1, expr_2)
            elif cur_op == OpType.ASTERISK:
                return self.compiler.eval_times(self.compiler.env, expr_1, expr_2)

        elif self.check_token(TokenType.BOOL):
            expr_1 = self.cur_token.text
            return self.compiler.eval_bool(self.compiler.env, expr_1)

        elif self.check_token(TokenType.OPEN_PAREN):
            expr_1 = self.handle_paren('')
            expr_2 = ''
            cur_op = None

            while not self.check_token(TokenType.EOF):
                if self.check_token(TokenType.PLUS):
                    if cur_op is None:
                        cur_op = OpType.PLUS
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        expr_1 = f'{expr_1} + {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        cur_op = OpType.PLUS
                        expr_1 = f'{expr_1} - {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        cur_op = OpType.PLUS
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.PLUS
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.LT:
                        expr_2 = f'{expr_2} +'
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.MINUS):
                    if cur_op is None:
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} + {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} - {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.MINUS
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.LT:
                        expr_2 = f'{expr_2} -'
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.ASTERISK):
                    if cur_op is None:
                        cur_op = OpType.ASTERISK
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        expr_2 = f'{expr_2} *'
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        expr_2 = f'{expr_2} *'
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.ASTERISK
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.LT:
                        expr_2 = f'{expr_2} *'
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.LT):
                    if cur_op is None:
                        cur_op = OpType.LT
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} + {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} - {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} * {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = ''
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.IDENT) or self.check_token(TokenType.NUMBER):
                    if cur_op is None:
                        cur_op = OpType.APP
                        expr_2 = self.cur_token.text
                        self.next_token()
                        continue
                    elif cur_op == OpType.PLUS:
                        if expr_2 == '':
                            expr_2 = self.cur_token.text
                        else:
                            expr_2 = f'{expr_2} {self.cur_token.text}'
                        self.next_token()
                        continue
                    elif cur_op == OpType.MINUS:
                        if expr_2 == '':
                            expr_2 = self.cur_token.text
                        else:
                            expr_2 = f'{expr_2} {self.cur_token.text}'
                        self.next_token()
                        continue
                    elif cur_op == OpType.ASTERISK:
                        if expr_2 == '':
                            expr_2 = self.cur_token.text
                        else:
                            expr_2 = f'{expr_2} {self.cur_token.text}'
                        self.next_token()
                        continue
                    elif cur_op == OpType.APP:
                        cur_op = OpType.LT
                        expr_1 = f'{expr_1} {expr_2}'
                        expr_2 = self.cur_token.text
                        self.next_token()
                        continue
                    else:
                        self.abort("Invalid op")

                elif self.check_token(TokenType.OPEN_PAREN):
                    if cur_op is None:
                        cur_op = OpType.APP
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.PLUS:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.MINUS:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.ASTERISK:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    elif cur_op == OpType.APP:
                        expr_2 = self.handle_paren(expr_2)
                        continue
                    else:
                        self.abort("Invalid op")

            if cur_op is None:
                return self.compiler.eval_expr(self.compiler.env, expr_1)
            elif cur_op == OpType.PLUS:
                return self.compiler.eval_plus(self.compiler.env, expr_1, expr_2)
            elif cur_op == OpType.MINUS:
                return self.compiler.eval_minus(self.compiler.env, expr_1, expr_2)
            elif cur_op == OpType.ASTERISK:
                return self.compiler.eval_times(self.compiler.env, expr_1, expr_2)
            elif cur_op == OpType.APP:
                return self.compiler.eval_app_base(self.compiler.env, expr_1, expr_2)

        # This is not a valid statement. Error!
        else:
            self.abort("Invalid statement at " + self.cur_token.text + " (" + self.cur_token.kind.name + ")")

    def handle_paren(self, expr):
        stack = 1
        if expr == '':
            expr = self.cur_token.text
        else:
            expr = f'{expr} {self.cur_token.text}'
        self.next_token()
        while stack != 0:
            if self.check_token(TokenType.OPEN_PAREN):
                stack += 1
                if expr == '':
                    expr = self.cur_token.text
                else:
                    expr = f'{expr} {self.cur_token.text}'
            elif self.check_token(TokenType.CLOSE_PAREN):
                stack -= 1
                expr = f'{expr} {self.cur_token.text}'
            else:
                if expr == '':
                    expr = self.cur_token.text
                else:
                    expr = f'{expr} {self.cur_token.text}'
            self.next_token()
        self.next_token()

        return expr


class OpType(enum.Enum):
    PLUS = 1
    MINUS = 2
    ASTERISK = 3
    LT = 4
    APP = 5
