#from parser import *
from program import *


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    program('|- let max = fun x -> fun y -> if x < y then y else x in max 3 5 evalto 5')

    a = f'     asd'
    b = (f'first line \n'
         f'      {a}')
    c = (f'first line \n'
         f'      {b}')
