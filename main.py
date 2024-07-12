#from parser import *
from program import *
import re




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    program('|- let rec fact = fun n -> if n < 2 then 1 else n * fact (n - 1) in fact 3 evalto 6')
    a = "(f = ( twice = ( ) [ fun f -> fun x -> f ( f x ) ] ) [ fun x -> x * x ])[fun x -> f (f x)]"
