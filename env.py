from lexer import TokenType, Token


class EnvVal:
    def __init__(self, tokens: [Token], is_paren: bool):
        self.tokens = tokens
        self.is_paren = is_paren

    def __str__(self):
        if self.is_paren:
            return f'({" ".join([str(token) for token in self.tokens])})'
        else:
            return f'{" ".join([str(token) for token in self.tokens])}'


class EvalEnvBool(EnvVal):
    def __init__(self, token: Token, is_paren: bool):
        super().__init__([token], is_paren)

    def get_val(self):
        return self.tokens[0]

    def __str__(self):
        return f'{self.get_val().text}'


class EvalEnvNum(EnvVal):
    def __init__(self, token: Token, minus: bool, is_paren: bool):
        super().__init__([token], is_paren)
        self.minus = minus

    def __str__(self):
        if self.minus:
            return f'-{self.tokens[0].text}'
        else:
            return f'{self.tokens[0].text}'


class EvalEnvNil(EnvVal):
    def __init__(self):
        super().__init__([Token('[]', TokenType.DOUBLE_BRACKET)], False)

    def get_val(self):
        return self.tokens[0]

    def __str__(self):
        return f'{self.get_val().text}'


class EvalEnvRec(EnvVal):
    def __init__(self, tokens: [Token], is_paren: bool):
        super().__init__(tokens, is_paren)

    def __str__(self):
        return f'{" ".join([str(token) for token in self.tokens])}'


class EvalEnvFun(EnvVal):
    def __init__(self, tokens: [Token], is_paren: bool):
        super().__init__(tokens, is_paren)

    def __str__(self):
        return f'{" ".join([str(token) for token in self.tokens])}'


class EvalEnvList(EnvVal):
    def __init__(self, head: [Token], tail: [Token], is_paren: bool):
        super().__init__(head + tail, is_paren)
        self.head = head
        self.tail = tail

    def get_head(self):
        return f'{" ".join([str(token) for token in self.head])}'

    def get_tail(self):
        return f'{" ".join([str(token) for token in self.tail])}'

    def __str__(self):
        if self.is_paren:
            return f'({" ".join([str(token) for token in self.head])}::{" ".join([str(token) for token in self.tail])})'
        else:
            return f'{" ".join([str(token) for token in self.head])}::{" ".join([str(token) for token in self.tail])}'


class TypeEnvBase(EnvVal):
    def __init__(self, tokens: [Token], is_paren: bool):
        super().__init__(tokens, is_paren)

    def __rshift__(self, other):
        tokens = self.tokens + [Token('->', TokenType.ARROW)] + other.tokens
        return TypeEnvFun(tokens, self, other, False)

    def __str__(self):
        if self.is_paren:
            return f'({" ".join([str(token) for token in self.tokens])})'
        else:
            return f'{" ".join([str(token) for token in self.tokens])}'


class TypeEnvVariable(TypeEnvBase):
    def __init__(self, tokens: [Token]):
        super().__init__(tokens, False)


class TypeEnvFun(TypeEnvBase):
    def __init__(self, tokens: [Token], left: TypeEnvBase, right: TypeEnvBase, is_paren: bool):
        super().__init__(tokens, is_paren)
        self.left = left
        self.right = right

    def __str__(self):
        if self.is_paren:
            return f'({self.left} -> {self.right})'
        else:
            return f'{self.left} -> {self.right}'


class TypeEnvList(TypeEnvBase):
    def __init__(self, tokens: [Token], list_type: TypeEnvBase, is_paren: bool):
        super().__init__(tokens, is_paren)
        self.list_type = list_type


class TypeEnvFree(TypeEnvBase):
    def __init__(self, tokens: [Token], free_vars: [TypeEnvVariable], expr: TypeEnvBase):
        super().__init__(tokens, False)
        self.free_vars = free_vars
        self.expr = expr

    def __str__(self):
        if len(self.free_vars) == 0:
            return str(self.expr)
        else:
            free = ' '.join([str (env) for env in self.free_vars])
            return f"{free}. {self.expr}"


class TypeEnvEmpty(TypeEnvBase):
    def __init__(self):
        super().__init__([], False)


class Env:
    def __init__(self, kind: TokenType, var: Token, val: EnvVal):
        self.kind = kind
        self.var = var
        self.val = val

    def __str__(self):
        pass

    def check_var(self, var):
        if self.var.text == var:
            return True


class EvalEnv(Env):
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
        env = Env(var.kind, var, TypeEnvEmpty())
        super().__init__(env)

    def __str__(self):
        return f'{str(self.var)} : PROMISED'
"""

class EnvCollection:
    def __init__(self):
        self.envs: [Env] = []

    def append(self, env):
        if isinstance(env, Env):
            self.envs.append(env)
            return self
        elif isinstance(env, EnvCollection):
            for e in env.envs:
                self.envs.append(e)
            return self

    def __add__(self, other):
        if isinstance(other, EnvCollection):
            if self.envs is not None and len(self.envs) > 0 and self.envs[0] is not None:
                new_env = EnvCollection()
                new_env.envs = self.envs + other.envs
                return new_env
            else:
                return other
        elif isinstance(other, Env):
            new_env = EnvCollection()
            new_env.envs = self.envs + [other]
            return new_env

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

"""


class EnvCollection(dict):
    def __init__(self, *args, **kwargs):
        super(EnvCollection, self).__init__(*args, **kwargs)
        self.next_index = 0

    def _get_str_key(self, key):
        """Helper method to get the string representation of the key."""
        for k in self.keys():
            if str(k) == str(key):
                return k
        return key

    def append(self, env):
        if isinstance(env, Env):
            key = env.var
            self[key] = env.val
        elif isinstance(env, EnvCollection):
            for key, value in env.items():
                self[self._get_str_key(key)] = value
        return self

    def __add__(self, other):
        if isinstance(other, EnvCollection):
            new_env = EnvCollection(self)
            for key, value in other.items():
                new_env[new_env._get_str_key(key)] = value
            return new_env
        elif isinstance(other, Env):
            new_env = EnvCollection(self)
            new_env[new_env._get_str_key(other.val)] = other
            return new_env

    def full_copy(self):
        new_env = EnvCollection()
        for key, value in self.items():
            new_env[new_env._get_str_key(key)] = value
        return new_env

    def pop(self, key):
        key = self._get_str_key(key)
        super().pop(key, None)
        return self

    def get_current(self):
        return list(self.keys())[-1] if self else None

    def get_current_val(self):
        current = self.get_current()
        return self[current] if current else None

    def get_val_by_var(self, var):
        env = self.get_env_by_var(var)
        return str(env.val) if env else None

    def get_env_by_var(self, var):
        return self.__getitem__(var)

    def check_var(self, var):
        return any(env.check_var(var) for env in self.values())

    def set_var(self, var, new_env):
        for key, env in self.items():
            if env.check_var(var):
                self[self._get_str_key(key)] = new_env

    def is_not_empty(self):
        return bool(self)

    def values(self):
        #value_list = super(EnvCollection, self).values()
        #return [str(v) for v in value_list]
        value_list = super(EnvCollection, self).values()
        return value_list

    def __str__(self):
        envs = []
        for key in self:
            env = self[key]
            if isinstance(env, TypeEnvBase) or isinstance(env, str):
                envs.append(f'{key} : {self[key]}')
            else:
                envs.append(f'{key} = {self[key]}')
        return ", ".join(envs)

    def __getitem__(self, key):
        key = self._get_str_key(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        key = self._get_str_key(key)
        return super().__setitem__(key, value)

    def find_key_by_value(self, value):
        return next((key for key, v in self.items() if str(v) == value), None)


class EnvVariableDict(dict):
    def __init__(self, *args, **kwargs):
        super(EnvVariableDict, self).__init__(*args, **kwargs)
        self.alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.next_index = 0

    def flatten(self):
        def sub_flatten(s_dict, t: TypeEnvBase):
            if isinstance(t, TypeEnvFun):
                t.left = sub_flatten(s_dict, t.left)
                t.right = sub_flatten(s_dict, t.right)
                return t
            elif isinstance(t, TypeEnvVariable):
                if str(t) in s_dict.keys():
                    if not isinstance(s_dict[t], TypeEnvVariable):
                        return s_dict[t]
            else:
                return t

        for key in self:
            sub_flatten(self, self[key])

    def _get_next_key_value(self):
        if self.next_index >= len(self.alphabet):
            raise ValueError("No more alphabetical keys available")
        key_value = "'" + self.alphabet[self.next_index]
        self.next_index += 1
        return key_value

    def _get_str_key(self, key):
        """Helper method to get the string representation of the key."""
        for k in self.keys():
            if str(k) == str(key):
                return k
        return key

    def add_entry(self) -> str:
        key = self._get_next_key_value()
        value = TypeEnvVariable([Token(key, TokenType.QUOT)])
        self[key] = value
        self.flatten_self()
        return key

    def __setitem__(self, key, value):
        key = self._get_str_key(key)
        ret = super().__setitem__(key, value)
        self.flatten_self()
        return ret

    def __getitem__(self, key):
        key = self._get_str_key(key)
        return super().__getitem__(key)

    def __contains__(self, item):
        for k in self.keys():
            if str(k) == str(item):
                return True
        return False

    # We might need to prove that there would be no circular dependencies
    def flatten_env_fun(self, env):
        if env is None:
            return None
        value = self[env]
        if isinstance(value, TypeEnvVariable):
            if str(value) in self and str(value) != str(env):
                self[env] = self[value]
        elif isinstance(env, TypeEnvFun):
            self.flatten_env_fun(value.left)
            self.flatten_env_fun(value.right)

    def flatten_self(self):
        def resolve_type_env(node, dictionary):
            if isinstance(node, TypeEnvVariable):
                while str(node) in dictionary and str(node) != str(dictionary[node]):
                    node = resolve_type_env(dictionary[node], dictionary)
                return node
            elif isinstance(node, TypeEnvFun):
                left = resolve_type_env(node.left, dictionary)
                right = resolve_type_env(node.right, dictionary)
                ret = left >> right
                ret.is_paren = node.is_paren
                return ret
            elif isinstance(node, TypeEnvList):
                list_type = resolve_type_env(node.list_type, dictionary)
                if isinstance(list_type, TypeEnvFun) or isinstance(list_type, TypeEnvList):
                    list_type.is_paren = True
                node.list_type = list_type
                return node
            return node

        flat_dict = {}

        for key in self:
            flat_dict[key] = resolve_type_env(self[key], self)

        self.clear()
        super().update(flat_dict)


class FreeEnvVariableDict(EnvVariableDict):
    @staticmethod
    def remove_alphabets(a: str, b: str) -> str:
        a_set = set(a)
        result = ''.join([char for char in b if char not in a_set])

        return result

    def __init__(self, *args, **kwargs):
        super(EnvVariableDict, self).__init__(*args, **kwargs)
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz'
        self.next_index = 0

    def __setitem__(self, key, value):
        key = self._get_str_key(key)
        ret = super().__setitem__(key, value)
        self.alphabet = self.remove_alphabets(str(key), self.alphabet)
        self.flatten_self()
        self.next_index = 0
        return ret

    def add_entry_with_key(self, key) -> str:
        key = self._get_str_key(key)
        self.__setitem__(key, key)
        self.flatten_self()
        return key

    def full_copy(self):
        new_env = FreeEnvVariableDict()
        for key, value in self.items():
            new_env[new_env._get_str_key(key)] = value
            new_env.next_index = self.next_index
            new_env.alphabet = self.alphabet
        return new_env
