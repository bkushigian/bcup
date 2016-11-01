from src.metaparser import MetaParser
from src.lexer import Lexer, Token, TokenId, TokenNum, TokenEOF, TokenBinOpAdd
from src.symbols import Terminal, NonTerminal, Production
from src.statemachine import Item, State, LLStateMachine
from src.helper import stop


class TokenBinOpAst(Token):
    name = "AST"
    symbol = "*"

class TokenLParen(Token):
    name = "LPAREN"
    symbol = "("

class TokenRParen(Token):
    name = "RPAREN"
    symbol = ")"

class MyLexer(Lexer):
    def __init__(self, program = None):
        self.program = program
        self.token_map = {
            "ID" : TokenId, "ADD" : TokenBinOpAdd, 
            "EOF" : TokenEOF, "AST" : TokenBinOpAst,
            "LPAREN" : TokenLParen, "RPAREN": TokenRParen}
    

with open("test/aho_grammar_4_28.notcup") as f:
    grammar = f.read()

lexer = MyLexer(grammar)
mp    = MetaParser(grammar, lexer, False)

print " === TERMS === "
print mp.terminals
print " === NONTERMS === "
print mp.nonterminals
print " === TOKEN MAP ==="
print mp.token_map

print " === PRODUCTIONS ==="
print mp.productions

mp.compute_firsts()
mp.compute_follows()
firsts = mp.productions.firsts
follows = mp.productions.follows

# Some Debug Info...
print " === FIRSTS === "
for key in firsts:
    s = "FIRST({}) = {{".format(key)
    for val in firsts[key]:
        s += "{}, ".format(val)
    print s + "}"

print " === FOLLOWS === "
for key in follows:
    if isinstance(key, Terminal):
        continue
    s = "FOLLOWS({}) = {{".format(key)
    for val in follows[key]:
        s += "{}, ".format(val)
    print s + "}"

print 
print " === PRODUCTION NUMBERS === "
productions = mp.productions
for i in range(len(productions.productions)):
    print i, productions.productions[i]

stop()

print 
print " === TESTING STATE MACHINE ==="

sm = LLStateMachine(mp)
sm.print_table()


