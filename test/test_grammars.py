from src.metaparser import MetaParser
from src.lexer import Lexer, Token, TokenId, TokenNum, TokenEOF, TokenBinOpAdd
from src.symbols import Terminal, NonTerminal, Production
from src.statemachine import Item, State, LRStateMachine
from src.helper import stop


with open("test/p4grammar.notcup") as f:
    grammar = f.read()

lexer = Lexer(grammar)
mp    = MetaParser(grammar, lexer)

print " === TERMS === "
print mp.terminals
print " === NONTERMS === "
print mp.nonterminals
print " === TOKEN MAP ==="
print mp.token_map

print " === PRODUCTIONS ==="
print mp.productions

stop()
mp.compute_firsts()
firsts = mp.productions.firsts
for key in firsts:
    s = "FIRST({}) = {{".format(key)
    for val in firsts[key]:
        s += "{}, ".format(val)
    print s + "}"

print
print " === first_of_string() === "
s = mp.nonterminals.values() + mp.terminals.values()
while s:
    print s," --> ", mp.firsts_of_string(s)
    s = s[1:]

s = mp.terminals.values() + mp.nonterminals.values()  
print
while s:
    print s," --> ", mp.firsts_of_string(s)
    s = s[1:]

stop()
mp.compute_follows()
follows = mp.productions.follows
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

sm = LRStateMachine(mp.terminals.values(), mp.nonterminals.values(), productions)
print sm

sm.generate_states()
