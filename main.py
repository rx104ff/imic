from program import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    a = program('|- let rec f = fun x -> if x < 1 then [] else x :: f (x - 1) in f 3 evalto 3 :: 2 :: 1 :: []')
    #print(a.replace('|-','').replace('True', 'true').replace('False', 'false'))
    print(a.replace('True', 'true').replace('False', 'false'))