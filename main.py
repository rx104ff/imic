from Parser.parser import *


def program(prg_input):
    # Pre-processing
    prg_input.split('|-')
    env_expr = prg_input[0]
    prg = prg_input[0].split('evalto')[0]
    val = prg_input[0].split('evalto')[1]

    envs = env_expr.split(",")
    parser = Parser()
    env_list = EnvList()
    for env in envs:
        env_lex = Lexer(env)
        env_list.append(parser.parse_env(env_lex.get_tokens()))

    program_lex = Lexer(prg)
    program_tokens = program_lex.get_tokens()

    program_root = parser.parse_program(program_tokens)
    program_tree = SyntaxTree(program_root)

    dot = program_tree.visualize_tree()
    dot.render('tree', format='png', view=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    program('PyCharm')
