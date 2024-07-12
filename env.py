from lexer import TokenType, Token


class Env:
    def __init__(self, kind: TokenType, var: Token, val: [Token]):
        self.kind = kind
        self.var = var
        self.val = val

    def __str__(self):
        return f'{str(self.var)} = {" ".join([str(token) for token in self.val])}'


class EnvList:
    def __init__(self):
        self.envs: [Env] = []

    def append(self, env: Env):
        self.envs.append(env)
        return self.envs

    def __add__(self, other):
        if isinstance(other, EnvList):
            if self.envs is not None and len(self.envs) > 0 and self.envs[0] is not None:
                new_env = EnvList()
                new_env.envs = self.envs + other.envs
                return new_env
            else:
                return other

    def copy(self):
        new_env = EnvList()
        for env in self.envs:
            new_env.append(env)
        return new_env

    def pop(self):
        self.envs.pop()
        return self

    def get_current(self):
        return self.envs[-1]

    def get_current_val(self) -> str:
        return ' '.join([str(token) for token in self.envs[-1].val])

    def __str__(self):
        return ", ".join([str(env) for env in self.envs])
