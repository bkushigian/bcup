from src.metaparser import MetaParser
from src.lexer import Lexer
from src.tokens import *
from src.symbols import Terminal, NonTerminal, Production
from src.statemachine import Item, State, LRStateMachine
from src.helper import print_banner

with open("test/grammar.notcup") as f:
    grammar = f.read()

lexer = Lexer(grammar)
mp    = MetaParser(grammar, lexer)

print_banner("TERMINALS")
print mp.terminals
print_banner("NONTERMINALS")
print mp.nonterminals
print mp.token_map

print_banner("PRODUCTIONS")
print mp.productions

mp.compute_firsts()
mp.compute_follows()

follows = mp.productions.follows
firsts = mp.productions.firsts

print_banner("FIRSTS")
for key in firsts:
    s = "FIRST({}) = {{".format(key)
    for val in firsts[key]:
        s += "{}, ".format(val)
    print s + "}"


print_banner("FOLLOWS")
for key in follows:
    if isinstance(key, Terminal):
        continue
    s = "FOLLOWS({}) = {{".format(key)
    for val in follows[key]:
        s += "{}, ".format(val)
    print s + "}"

print_banner("TESTING STATE MACHINE")
sm = LRStateMachine(mp)
print sm

sm.generate_states()
