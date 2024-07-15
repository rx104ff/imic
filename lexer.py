import sys
import enum
from typing import Optional


# TokenType is our enum for all the types of tokens.
class TokenType(enum.Enum):
    EOF = -1
    NUMBER = 1
    IDENT = 2
    STRING = 3
    BOOL = 4
    COMMA = 5
    COLON = 6
    BAR = 7
    # Keywords.
    FUN = 101
    LET = 102
    REC = 103
    IN = 104
    IF = 105
    THEN = 106
    ELSE = 107
    ARROW = 108
    DOUBLE_COLON = 109
    DOUBLE_BRACKET = 110
    MATCH = 111
    WITH = 112
    # Operators.
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    LT = 208
    # Parenthesis
    OPEN_PAREN = 301
    CLOSE_PAREN = 302
    OPEN_BRACKET = 303
    CLOSE_BRACKET = 304
    # Nat
    NAT_S = 401
    NAT_Z = 402


# Token contains the original text and the type of token.
class Token:
    def __init__(self, token_txt, token_type):
        self.text = token_txt  # The token's actual text. Used for identifiers, strings, and numbers.
        self.kind = token_type  # The TokenType that this token is classified as.

    def __str__(self):
        return f'{self.text}'

    @staticmethod
    def check_if_keyword(token_txt: str) -> Optional[TokenType]:
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == token_txt.upper() and 100 <= kind.value < 200:
                return kind
        return None


# Lexer object keeps track of current position in the source code and produces each token.
class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.cur_char = ''  # Current character in the string.
        self.cur_pos = -1  # Current position in the string.
        self.next_char()

    # Process the next character.
    def next_char(self):
        self.cur_pos += 1
        if self.source is None or self.cur_pos >= len(self.source):
            self.cur_char = '\0'  # EOF
        else:
            self.cur_char = self.source[self.cur_pos]

    # Return the lookahead character.
    def peek(self):
        if self.cur_pos + 1 >= len(self.source):
            return '\0'
        return self.source[self.cur_pos + 1]

    # Invalid token found, print error message and exit.
    @staticmethod
    def abort(message: str):
        sys.exit("Lexing error. " + message)

    # Return the next token.
    def get_token(self):
        self.skip_whitespace()
        token = None

        if self.cur_char == '+':
            token = Token(self.cur_char, TokenType.PLUS)
        elif self.cur_char == '-':
            if self.peek() == '>':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.ARROW)
            else:
                token = Token(self.cur_char, TokenType.MINUS)
        elif self.cur_char == ',':
            token = Token(self.cur_char, TokenType.COMMA)
        elif self.cur_char == '*':
            token = Token(self.cur_char, TokenType.ASTERISK)
        elif self.cur_char == '=':
            # Check whether this token is =
            token = Token(self.cur_char, TokenType.EQ)
        elif self.cur_char == '<':
            # Check whether this is token is <
            token = Token(self.cur_char, TokenType.LT)
        elif self.cur_char == '|':
            token = Token(self.cur_char, TokenType.BAR)
        elif self.cur_char == '(':
            # Check whether this is token is (
            token = Token(self.cur_char, TokenType.OPEN_PAREN)
        elif self.cur_char == ')':
            # Check whether this is token is )
            token = Token(self.cur_char, TokenType.CLOSE_PAREN)
        elif self.cur_char == '[':
            if self.peek() == ']':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.DOUBLE_BRACKET)
            else:
                # Check whether this is token is [
                token = Token(self.cur_char, TokenType.OPEN_BRACKET)
        elif self.cur_char == ']':
            # Check whether this is token is ]
            token = Token(self.cur_char, TokenType.CLOSE_BRACKET)
        elif self.cur_char == ':':
            if self.peek() == ':':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.DOUBLE_COLON)
            else:
                token = Token(self.cur_char, TokenType.COLON)
        elif self.cur_char.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits.
            start_pos = self.cur_pos
            while self.peek().isdigit():
                self.next_char()

            token_txt = self.source[start_pos: self.cur_pos + 1]  # Get the substring.
            token = Token(token_txt, TokenType.NUMBER)
        elif self.cur_char.isalpha():
            if self.cur_char == 'Z':
                token = Token(self.cur_char, TokenType.NAT_Z)
            elif self.cur_char == 'S':
                token = Token(self.cur_char, TokenType.NAT_S)
            else:
                # Leading character is a letter, so this must be an identifier or a keyword.
                # Get all consecutive alphanumeric characters.
                start_pos = self.cur_pos
                while self.peek().isalnum():
                    self.next_char()

                # Check if the token is in the list of keywords.
                token_txt = self.source[start_pos: self.cur_pos + 1]  # Get the substring.
                keyword = Token.check_if_keyword(token_txt)

                if token_txt == 'true' or token_txt == 'false':
                    token = Token(token_txt, TokenType.BOOL)  # Bool
                elif keyword is None:  # Identifier
                    token = Token(token_txt, TokenType.IDENT)
                else:  # Keyword
                    token = Token(token_txt, keyword)
        elif self.cur_char == '\0':
            # EOF.
            token = Token('', TokenType.EOF)
        else:
            # Unknown token!
            self.abort("Unknown token: " + self.source)
            #pass

        self.next_char()
        return token

    # Skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skip_whitespace(self):
        while self.cur_char == ' ' or self.cur_char == '\t' or self.cur_char == '\r':
            self.next_char()

    def get_tokens(self) -> [Token]:
        tokens = []
        while True:
            token = self.get_token()
            if token.kind == TokenType.EOF:
                break
            tokens.append(token)
        return tokens
