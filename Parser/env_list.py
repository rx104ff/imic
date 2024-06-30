class Env:
    def __init__(self, kind, var, val):
        self.kind = kind
        self.var = var
        self.val = val


class EnvList:
    def __init__(self):
        self.envs: [Env] = []

    def append(self, env: Env):
        self.envs.append(env)
