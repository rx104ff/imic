# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from lexer import *
from Parser.parser import *
#from Parser.syntax_tree import *
from graphviz import Digraph

def print_hi(name):
    environment_lex = Lexer("x = 2")
    program_lex = Lexer("let fact = fun self -> fun n -> if n < 2 then 1 else n * self self (n - 1) in fact fact 3")
    environment_tokens = []
    program_tokens = []
    while True:
        token = program_lex.get_token()
        if token.kind == TokenType.EOF:
            break
        program_tokens.append(token)

    parser = Parser()
    root = parser.parse(program_tokens)
    tree = SyntaxTree(root)
    dot = tree.visualize_tree()
    dot.render('tree', format='png', view=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
