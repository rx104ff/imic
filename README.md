This project dedicated to automate https://www.fos.kuis.kyoto-u.ac.jp/~igarashi/CoPL/index.cgi.
To run the app, clone the repo to a local folder. Ensure that python and other libs are installed properly on the environment.
The compiler support EvalML, TypingML and PolyTypingML.

A sample usage would be **python main.py "PolyTypingML" "|- if 4 < 5 then 2 + 3 else 8 * 8 : int"**, whose output is 

```
|- if 4 < 5 then 2 + 3 else 8 * 8 : int by T-If {
    |- 4 < 5 : bool by T-Lt {
        |- 4 : int by T-Int{};
        |- 5 : int by T-Int{};
    };
    |- 2 + 3 : int by T-Plus {
        |- 2 : int by T-Int{};
        |- 3 : int by T-Int{};
    };
    |- 8 * 8 : int by T-Times {
        |- 8 : int by T-Int{};
        |- 8 : int by T-Int{};
    };
};
```
**python main.py "TypingML" "|- let rec append = fun l1 -> fun l2 -> match l1 with [] -> l2 | x :: y -> x :: append y l2 in append (true :: []) (false :: []) : bool list"**


```
|- let rec append = fun l1 -> fun l2 -> match l1 with [] -> l2 | x::y -> x::append y l2 in append (true::[]) (false::[]) : bool list by T-LetRec {
    append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list)|- fun l2 -> match l1 with [] -> l2 | x::y -> x::append y l2 : (( bool ) list) -> (( bool ) list) by T-Fun{
        append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list), l2 : (( bool ) list)|- match l1 with [] -> l2 | x::y -> x::append y l2 : (( bool ) list) by T-Match {
            append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list), l2 : (( bool ) list)|- l1 : (bool list) by T-Var{};
            append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list), l2 : (( bool ) list)|- l2 : (( bool ) list) by T-Var{};
            append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list), l2 : (( bool ) list), x : bool, y : bool list|- x::append y l2 : ( bool ) list by T-Cons {
                append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list), l2 : (( bool ) list), x : bool, y : bool list|- x : bool by T-Var{};
                append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list), l2 : (( bool ) list), x : bool, y : bool list|- append y l2 : ( bool ) list by T-App {
                    append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list), l2 : (( bool ) list), x : bool, y : bool list|- append y : ((( bool ) list) -> ( bool ) list) by T-App {
                        append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list), l2 : (( bool ) list), x : bool, y : bool list|- append : ((bool list) -> ((( bool ) list) -> ( bool ) list)) by T-Var{};
                        append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list), l2 : (( bool ) list), x : bool, y : (bool list)|- y : (bool list) by T-Var{};
                    };
                    append : ((bool list) -> ((( bool ) list) -> ( bool ) list)), l1 : (bool list), l2 : (( bool ) list), x : bool, y : (bool list)|- l2 : (( bool ) list) by T-Var{};
                };
            };
        };
    }; 
    append : ((bool list) -> ((( bool ) list) -> ( bool ) list))|- append (true::[]) (false::[]) : bool list by T-App {
        append : ((bool list) -> ((( bool ) list) -> ( bool ) list))|- append (true::[]) : ((( bool ) list) -> bool list) by T-App {
            append : ((bool list) -> ((( bool ) list) -> ( bool ) list))|- append : ((bool list) -> ((( bool ) list) -> ( bool ) list)) by T-Var{};
            append : ((bool list) -> ((( bool ) list) -> ( bool ) list))|- (true::[]) : ( bool ) list by T-Cons {
                append : ((bool list) -> ((( bool ) list) -> ( bool ) list))|- true : bool by T-Bool{};
                append : ((bool list) -> ((( bool ) list) -> ( bool ) list))|- [] : ( bool ) list by T-Nil{};
            };
        };
        append : ((bool list) -> ((( bool ) list) -> ( bool ) list))|- (false::[]) : ( bool ) list by T-Cons {
            append : ((bool list) -> ((( bool ) list) -> ( bool ) list))|- false : bool by T-Bool{};
            append : ((bool list) -> ((( bool ) list) -> ( bool ) list))|- [] : ( bool ) list by T-Nil{};
        };
    };
};
```

printed in the console

#### List of first input argv
1. EvalML1
2. EvalML2
3. EvalML3
4. EvalML4
5. TypingML
6. PolyTypingML

*Remark.* EvalML1 ~ EvalML4 are effectively programmed by the same compiler but handled differently for the final output.
