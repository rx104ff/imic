#from parser import *

def program(prog_input):
    pass
    # Pre-processing
    #program_expr = prog_input.split("|-")
    #env_expr = program_expr[0]
    #prg = program_expr[1].split('evalto')[0]
    #val = program_expr[1].split('evalto')[1]

    #parser = Parser()

    #env_list = parser.parse_env(env_expr)

    #program_tree = parser.parse_program(prg)

    #print(env_list)
    #dot = program_tree.visualize_tree()
    #dot.render('tree', format='png', view=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    program('|- let fact = fun self -> fun n -> if n < 2 then 1 else n * self self (n - 1) in fact fact 3 evalto 6')
