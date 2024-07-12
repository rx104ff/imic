from program import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    a = program('|- let compose = fun f -> fun g -> fun x -> f (g x) in let p = fun x -> x * x in let q = fun x -> x + 4 in compose p q 4 evalto 64')
    print(a.replace('True', 'true').replace('False', 'false'))
