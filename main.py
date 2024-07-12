from program import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    a = program('|- 3 < 4 evalto true')
    print(a.replace('|-','').replace('True', 'true').replace('False', 'false'))
    #print(a.replace('True', 'true').replace('False', 'false'))