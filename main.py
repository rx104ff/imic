# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from lexer import *
from Parser.parser import *
#from Parser.syntax_tree import *


def print_hi(name):
    lex = Lexer("let fact = fun self -> fun n -> if n < 2 then 1 else n * self self (n - 1) in fact fact 3")
    tokens = []
    while True:
        token = lex.get_token()
        if token.kind == TokenType.EOF:
            break
        tokens.append(token)

    parser = Parser()
    tree = parser.parse(tokens)
    print(tree)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
