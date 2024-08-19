This project dedicated to automate https://www.fos.kuis.kyoto-u.ac.jp/~igarashi/CoPL/index.cgi.
To run the app, clone the repo to a local folder. Ensure that python and other libs are installed properly on the environment.
The compiler support EvalML, TypingML and PolyTypingML.

A sample usage would be **python main.py "PolyTypingML" "|- if 4 < 5 then 2 + 3 else 8 * 8 : int"**, whose output is 

---
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
---

printed in the console

#### List of first input argv
1. EvalML1
2. EvalML2
3. EvalML3
4. EvalML4
5. TypingML
6. PolyTypingML

*Remark.* EvalML1 ~ EvalML4 are effectively programmed by the same compiler but handled differently for the final output.
