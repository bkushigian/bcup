''' tokens.py includes the base Token class as well as some other convenience
    classes. These are used primarily by the lexer, and can be overridden as the
    user sees fit. The `name` field is used, as is the `value` field where
    applicable. 
'''

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

class TokenBinOpAst(Token):
    def __init__(self, value= None):
        self.name = "AST"
        self.symbol = "*"

    def __repr__(self):
        return "Token({})".format(self.name)

class TokenLParen(Token):
    def __init__(self):
        self.name = "LPAREN"
        self.symbol = "("

class TokenRParen(Token):
    def __init__(self):
        self.name = "RPAREN"
        self.symbol = ")"

class TokenSemi(Token):
    def __init__(self):
        self.name = "SEMI"
        self.symbol = ";"

class TokenEOF(Token):
    def __init__(self):
        self.name = "EOF"
        self.symbol = "$"

    def __repr__(self):
        return "Token({})".format(self.symbol)

tokenEOF = TokenEOF()    # A Cannonical EOF token
