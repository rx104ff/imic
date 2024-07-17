from lexer import TokenType, Token


class EnvNode:
    def __init__(self, tokens: [Token]):
        self.tokens = tokens

    def __str__(self):
        return f'{" ".join([str(token) for token in self.tokens])}'


class EnvBool(EnvNode):
    def __init__(self, token: Token):
        super().__init__([token])

    def get_val(self):
        return self.tokens[0]

    def __str__(self):
        return f'{self.get_val().text}'


class EnvNum(EnvNode):
    def __init__(self, token: Token, minus: bool):
        super().__init__([token])
        self.minus = minus

    def __str__(self):
        if self.minus:
            return f'-{self.tokens[0].text}'
        else:
            return f'{self.tokens[0].text}'


class EnvNil(EnvNode):
    def __init__(self):
        super().__init__([Token('[]', TokenType.DOUBLE_BRACKET)])

    def get_val(self):
        return self.tokens[0]

    def __str__(self):
        return f'{self.get_val().text}'


class EnvRec(EnvNode):
    def __init__(self, tokens: [Token]):
        super().__init__(tokens)

    def __str__(self):
        return f'{" ".join([str(token) for token in self.tokens])}'


class EnvFun(EnvNode):
    def __init__(self, tokens: [Token]):
        super().__init__(tokens)

    def __str__(self):
        return f'{" ".join([str(token) for token in self.tokens])}'


class EnvList(EnvNode):
    def __init__(self, head: [Token], tail: [Token]):
        super().__init__(head + tail)
        self.head = head
        self.tail = tail

    def get_head(self):
        ret = f'{" ".join([str(token) for token in self.head])}'
        return f'{" ".join([str(token) for token in self.head])}'

    def get_tail(self):
        return f'{" ".join([str(token) for token in self.tail])}'

    def __str__(self):
        return f'{" ".join([str(token) for token in self.head])}::{" ".join([str(token) for token in self.tail])}'


class EnvType(EnvNode):
    def __init__(self, tokens: [Token]):
        super().__init__(tokens)

    def __str__(self):
        return f'{" ".join([str(token) for token in self.tokens])}'


class EnvTypeFun(EnvType):
    def __init__(self, tokens: [Token], index: int):
        super().__init__(tokens)
        self.index = index

    def get_left(self):
        return EnvType(self.tokens[0:self.index])

    def get_right(self):
        return EnvType(self.tokens[self.index+1::])


class EnvTypeList(EnvType):
    def __init__(self, tokens: [Token], list_type: [Token]):
        super().__init__(tokens)
        self.list_type = list_type

    def get_list_type(self):
        return EnvType(self.list_type)


class EnvTypeEmpty(EnvType):
    def __init__(self):
        super().__init__([])


class Env:
    def __init__(self, kind: TokenType, var: Token, val: EnvNode):
        self.kind = kind
        self.var = var
        self.val = val

    def __str__(self):
        pass

    def check_var(self, var):
        if self.var.text == var:
            return True


class ProgramEnv(Env):
    def __init__(self, env: Env):
        super().__init__(env.kind, env.var, env.val)

    def __str__(self):
        return f'{str(self.var)} = {str(self.val)}'


class TypeEnv(Env):
    def __init__(self, env: Env):
        super().__init__(env.kind, env.var, env.val)

    def __str__(self):
        return f'{str(self.var)} : {str(self.val)}'


class TypeEnvPromise(TypeEnv):
    def __init__(self, var: Token):
        env = Env(var.kind, var, EnvTypeEmpty())
        super().__init__(env)

    def __str__(self):
        return f'{str(self.var)} : PROMISED'


class EnvCollection:
    def __init__(self):
        self.envs: [Env] = []

    def append(self, env: Env):
        self.envs.append(env)
        return self

    def __add__(self, other):
        if isinstance(other, EnvCollection):
            if self.envs is not None and len(self.envs) > 0 and self.envs[0] is not None:
                new_env = EnvCollection()
                new_env.envs = self.envs + other.envs
                return new_env
            else:
                return other

    def copy(self):
        new_env = EnvCollection()
        for env in self.envs:
            new_env.append(env)
        return new_env

    def pop(self):
        self.envs.pop()
        return self

    def get_current(self) -> Env:
        return self.envs[-1]

    def get_current_val(self) -> str:
        return str(self.envs[-1].val)

    def get_val_by_var(self, var: str) -> str:
        return str(self.get_env_by_var(var).val)

    def get_env_by_var(self, var: str) -> Env:
        for env in self.envs:
            if env.check_var(var):
                return env

    def check_var(self, var: str):
        for env in self.envs:
            if env.check_var(var):
                return True
        return False

    def set_var(self, var: str, new_env: Env):
        for index, env in enumerate(self.envs):
            if env.check_var(var):
                self.envs[index] = new_env

    def is_not_empty(self):
        if len(self.envs) > 0:
            return True
        return False

    def __str__(self):
        return ", ".join([str(env) for env in self.envs])
