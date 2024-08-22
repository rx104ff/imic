from EvalML.program import program
from TypingML.type_infer import infer as s_infer
from PolyTypingML.poly_type_infer import infer as p_infer
import regex
import sys


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


if __name__ == '__main__':
    #ml_type = "PolyTypingML"
    #input_value = "f: 'a 'b.'a->'b->'a |- f 3 true + f 2 4 : int "
    ml_type = sys.argv[1]
    input_value = sys.argv[2]

    if ml_type == "EvalML1":
        val = program(f'|- {input_value}')
        print(val.replace('|-','').replace('True', 'true').replace('False', 'false'))
    elif ml_type == "EvalML2" or ml_type == "EvalML3":
        val = program(f'{input_value}')
        print(val.replace('True', 'true').replace('False', 'false'))
    elif ml_type == "EvalML4":
        val = program(f'{input_value}')
        print(replace_evar(val.replace('True', 'true').replace('False', 'false')))
    elif ml_type == "TypingML":
        val = s_infer(f'{input_value}')
        print(replace_evar(val.replace('True', 'true').replace('False', 'false')))
    elif ml_type == "PolyTypingML":
        val = p_infer(f'{input_value}')
        print(replace_evar(val.replace('True', 'true').replace('False', 'false')))
