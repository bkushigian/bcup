''' lexer.py has the base Lexer class, as well as Token and Token* subclasses.
These are filler classes for tests and can (should) be overridden.
This lexer class is the default for parsing a grammar and can be extended to
parse different forms of grammars.'''

from src.helper import DEBUG

class Token(object):
    def __init__(self, value=None):
        self.name = None
        self.value = value
        self.symbol = None
    def __repr__(self):
        if self.symbol:
            return " {} ".format(self.symbol)
        return "Token({},{})".format(self.name, self.value)

class TokenId(Token):
    def __init__(self, value):
        self.symbol = str(value)
        self.value = value
        self.name = "ID"

    def __repr__(self):
        return "Token({},{})".format(self.name, self.value)

class TokenNum(Token):
    def __init__(self, value):
        super(TokenNum, self).__init__(value)
        self.value = int(value)
        self.symbol = "{}".format(value)
        self.name = "NUM"

    def __repr__(self):
        return "Token({},{})".format(self.name, self.value)

class TokenBinOp(Token):
    name = "BINOP"
    def __init__(self):
        self.value = None
    def __repr__(self):
        return "<{}>".format(self.name)

    def __repr__(self):
        return "Token({},{})".format(self.name, self.value)

class TokenBinOpAdd(Token):
    def __init__(self, value= None):
        self.name = "ADD"
        self.symbol = "+"

    def __repr__(self):
        return "Token({})".format(self.name)

class TokenEOF(Token):
    def __init__(self):
        self.name = "EOF"
        self.symbol = "$"

    def __repr__(self):
        return "Token({})".format(self.symbol)

class Lexer(object):
    ''' Trivial lexer, can be overridden, this adds id's and nums'''
    def __init__(self, program = None):
        self.program = program
        self.token_map = {"NUM" : TokenNum, "ID" : TokenId, 
                "ADD" : TokenBinOpAdd, "EOF" : TokenEOF }
        if self.program:
            self.lex()

    def load_program(self, program):
        self.program = program

    def lex(self):
        ''' This splits the input file into strings. This should be overridden
        for any grammars as it presupposes that the grammar is white-space
        seperated.
        '''
        tokens = []
        if DEBUG:
            print "LEX: PROGRAM =", self.program
            raw_input()

        toks = self.program.split()
        for tok in toks:
            if tok.isdigit():
                tokens.append(TokenNum(tok))
            elif tok.isalnum():
                tokens.append(TokenId(tok))
            elif tok == '+':
                tokens.append(TokenBinOpAdd('+'))

        tokens.append(tokenEOF)
        if DEBUG:
            print tokens
            raw_input()
        self.tokens = iter(tokens)

    def next(self):
        ''' If lex is overridden, this needs to be rewritten to. This is the
        main function defined for the Lexer class and is how the outside world
        talks to it.
        '''
        return self.tokens.next()

tokenEOF = TokenEOF()    # A Cannonical EOF token
