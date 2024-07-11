#from parser import *
from program import *


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    program('|- let a = 3 in let f = fun y -> y * a in let a = 5 in f 4 evalto 12')

    a = f'     asd'
    b = (f'first line \n'
         f'      {a}')
    c = (f'first line \n'
         f'      {b}')
