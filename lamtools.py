from string import ascii_lowercase

class LamTerm:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def collapse_lams(self):
        if self.op == 'lam' or self.op == 'mlam':
            if self.op == 'lam':
                self.op = 'mlam'
                self.left = [self.left]
            if self.right.op == 'lam':
                self.left.append(self.right.left)
                self.right = self.right.right
                self.collapse_lams()
            else:
                self.right.collapse_lams()
        elif self.op == '@':
            self.left.collapse_lams()
            self.right.collapse_lams()

    def encode_vars(self, env={}):
        if self.op == 'lam':
            env = env.copy()
            env = {i: (env[i][0]+1, env[i][1]) for i in env}
            newenv = {self.left: (0, 1)}
            self.left = (0,1)
            env.update(newenv)
            self.right.encode_vars(env)
        elif self.op == 'mlam':
            env = env.copy()
            env = {i: (env[i][0]+1, env[i][1]) for i in env}
            newenv = {lt: (0, i+1) for i, lt in enumerate(self.left)}
            self.left = [newenv[lt] for lt in self.left]
            env.update(newenv)
            self.right.encode_vars(env)
        elif self.op == '@':
            self.left.encode_vars(env)
            self.right.encode_vars(env)
        else:
            try:
                self.op = env[self.op]
            except:
                raise Exception("Must be a closed term")

    def decode_vars(self, env={}, letterstack=list(ascii_lowercase)[::-1]):
        if self.op == 'lam':
            raise Exception("Must have collapsed lams")
        elif self.op == 'mlam':
            env = env.copy()
            newenv = {k: letterstack.pop() for (_, k) in self.left}
            self.left = [newenv[k] for (_, k) in self.left]
            env.update(newenv)
            self.right.decode_vars(env)
        elif self.op == '@':
            self.left.decode_vars(env)
            self.right.decode_vars(env)
        else:
            self.op = env[self.op[1]]

    def __repr__(self):
        if self.op == '@' or self.op == 'lam' or self.op == 'mlam':
            return "({}, {}, {})".format(self.op, self.left, self.right)
        else:
            return "{}".format(self.op)

def interpret_term(text):
    text = text.strip()
    if len(text) == 0:
        return None
    elif text[0] == '(':
        termtext, remterm = takeparen(text)
        term = interpret_term(termtext)
        appterm = interpret_term(remterm)
        if appterm is None:
            return term
        else:
            return LamTerm('@', term, appterm)
    elif text[0] == '%':
        #input(text[1:].strip()[1:])
        return LamTerm('lam', text[1:].strip()[0], interpret_term(text[1:].strip()[1:]))
    elif len(text) == 1:
        return LamTerm(text[0], None, None)
    else:
        raise Exception("Parsing Error")

def takeparen(text):
    i = 1
    pc = 1
    while pc != 0:
        if text[i] == '(':
            pc += 1
        elif text[i] == ')':
            pc -= 1
        i += 1
    return text[1:i-1], text[i:]

