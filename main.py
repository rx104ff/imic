from program import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    program('|- let rec sum = fun f -> fun n -> if n < 1 then 0 else f n + sum f (n - 1) in sum (fun x -> x * x) 2 evalto 5')
