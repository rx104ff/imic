from Parser.parser import *


def program(prog_input):
    # Pre-processing
    program_expr = prog_input.split("|-")
    env_expr = program_expr[0]
    prg = program_expr[1].split('evalto')[0]
    val = program_expr[1].split('evalto')[1]

    envs = env_expr.split(",")
    parser = Parser()
    env_list = EnvList()
    for env in envs:
        env_lex = Lexer(env)
        parsed_env = parser.parse_env(env_lex.get_tokens())
        if parsed_env is not None:
            env_list.append(parsed_env)

    program_lex = Lexer(prg)
    program_tokens = program_lex.get_tokens()

    program_root = parser.parse_program(program_tokens)
    program_tree = SyntaxTree(program_root)

    dot = program_tree.visualize_tree()
    dot.render('tree', format='png', view=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    program('|- let fact = fun self -> fun n -> if n < 2 then 1 else n * self self (n - 1) in fact fact 3 evalto 6')
