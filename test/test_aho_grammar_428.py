from src.metaparser import MetaParser
from src.lexer import Lexer, Token, TokenId, TokenNum, TokenEOF, TokenBinOpAdd
from src.tokens import *
from src.symbols import Terminal, NonTerminal, Production
from src.statemachine import Item, State, LLStateMachine
from src.helper import stop, print_banner

class MyLexer(Lexer):
    def __init__(self, program = None):
        self.program = program
        self.token_map = {
            "ID" : TokenId, "ADD" : TokenBinOpAdd, 
            "EOF" : TokenEOF, "AST" : TokenBinOpAst,
            "LPAREN" : TokenLParen, "RPAREN": TokenRParen}
    

with open("test/aho_grammar_4_28.bcup") as f:
    grammar = f.read()

lexer = MyLexer(grammar)
mp    = MetaParser(grammar, lexer, False)

print_banner( "   TERMINALS   ")
print mp.terminals
print_banner( "   NONTERMINALS   ")
print mp.nonterminals
print_banner( "   TOKEN MAP   ")
print mp.token_map

print_banner( "   PRODUCTIONS   ")
print mp.productions

mp.compute_firsts()
mp.compute_follows()
firsts = mp.productions.firsts
follows = mp.productions.follows

# Some Debug Info...
print_banner("   FIRSTS   ")
for key in firsts:
    s = "FIRST({}) = {{".format(key)
    for val in firsts[key]:
        s += "{}, ".format(val)
    print s + "}"

print_banner("   FOLLOWS   ")
for key in follows:
    if isinstance(key, Terminal):
        continue
    s = "FOLLOWS({}) = {{".format(key)
    for val in follows[key]:
        s += "{}, ".format(val)
    print s + "}"


print 
print " === TESTING STATE MACHINE ==="

sm = LLStateMachine(mp)
sm.print_table()


