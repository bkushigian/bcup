class Token(object):
    name = None
    def __init__(self, value=None):
        self.value = value
    def __repr__(self):
        return "<{},{}>".format(self.name, self.value)

class TokenId(Token):
    name  = "ID"

class TokenNum(Token):
    name = "NUM"
    def __init__(self, value):
        value = int(value)
        super(TokenNum, self).__init__(value)

class TokenBinOp(Token):
    name = "BINOP"
    def __init__(self):
        self.value = None
    def __repr__(self):
        return "<{}>".format(self.name)

class TokenBinOpAdd(Token):
    name = "ADD"

class TokenEOF(Token):
    name = "EOF"

class Lexer(object):
    ''' Trivial lexer, can be overridden, this adds id's and nums'''
    def __init__(self, program = None):
        self.program = program
        self.token_map = {"NUM" : TokenNum, "ID" : TokenId, "ADD" : TokenBinOpAdd, "EOF" : TokenEOF }

    def load_program(self, program):
        self.program = program

    def lex(self):
        tokens = []
        toks = program.split()
        for tok in toks:
            if tok.isdigit():
                tokens.append(TokenNum(tok))
            elif tok.isalnum():
                tokens.append(TokenId(tok))
            elif tok == '+':
                tokens.append(TokenBinOpAdd('+'))
        self.tokens = iter(tokens)

    def next(self):
        return self.tokens.next()
                




