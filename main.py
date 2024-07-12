from program import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    program('|- let fact = fun self -> fun n -> if n < 2 then 1 else n * self self (n - 1) in fact fact 3 evalto 6')
