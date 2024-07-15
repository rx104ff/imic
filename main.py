from program import *
import regex


def replace_evar(text):
    # Pattern to match "E-Var2" followed by a balanced set of braces
    pattern_var2 = r'E-Var2(\{(?:[^{}]*|(?1))*\})'
    # Replace the matched pattern for "E-Var2"
    text = regex.sub(pattern_var2, "E-Var{}", text)

    # Pattern to match "E-Var1" followed by braces containing only white spaces
    pattern_var1 = r'E-Var1\{\s*\}'
    # Replace the matched pattern for "E-Var1"
    text = regex.sub(pattern_var1, "E-Var{}", text)

    return text


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    a = program('x = 5 |- 1 < x evalto true')
    #print(a.replace('|-','').replace('True', 'true').replace('False', 'false'))
    #print(a.replace('True', 'true').replace('False', 'false'))
    print(replace_evar(a.replace('True', 'true').replace('False', 'false')))
    #test= "' l = ( ( ) ( apply = ( ) [ rec apply = fun l -> fun x -> match l with [] -> x | f :: l -> f ( apply l x ) ] ) [ fun y -> y + 3 ] ) :: [] )'"
    #stack = 0
