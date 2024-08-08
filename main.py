from EvalML.program import program
from TypingML.type_infer import infer
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
    a = infer('|- let rec fact = fun n -> if n < 2 then 1 else n * fact (n - 1) in fact 3 : int')
    #b = program('x = true, y = 4 |- if y then x + 1 else x - 1 evalto 5 by')
    #print(a.replace('|-','').replace('True', 'true').replace('False', 'false'))
    #print(b.replace('True', 'true').replace('False', 'false'))
    print(replace_evar(a.replace('True', 'true').replace('False', 'false')))
    #test= "' l = ( ( ) ( apply = ( ) [ rec apply = fun l -> fun x -> match l with [] -> x | f :: l -> f ( apply l x ) ] ) [ fun y -> y + 3 ] ) :: [] )'"
    #stack = 0

