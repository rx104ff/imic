#from parser import *
from program import *
import re




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    program('|- let twice = fun f -> fun x -> f (f x) in twice (fun x -> x * x) 2 evalto 16')
    a = "(f = ( twice = ( ) [ fun f -> fun x -> f ( f x ) ] ) [ fun x -> x * x ])[fun x -> f (f x)]"

