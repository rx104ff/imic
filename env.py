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
    def __init__(self, token: Token):
        super().__init__([token])

    def get_val(self):
        return self.tokens[0]

    def __str__(self):
        return f'{self.get_val().text}'


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


class Env:
    def __init__(self, kind: TokenType, var: Token, val: EnvNode):
        self.kind = kind
        self.var = var
        self.val = val

    def __str__(self):
        return f'{str(self.var)} = {str(self.val)}'


class EnvCollection:
    def __init__(self):
        self.envs: [Env] = []

    def append(self, env: Env):
        self.envs.append(env)
        return self.envs

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

    def __str__(self):
        return ", ".join([str(env) for env in self.envs])
