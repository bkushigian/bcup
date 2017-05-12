from cup.lexer.lexer import Lexer, Token, TokenId, TokenNum, TokenEOF, TokenBinOpAdd
from cup.parser.metaparser import MetaParser
from cup.parser.symbols import Terminal, NonTerminal, Production
from cup.parser.statemachine import Item, State, LLStateMachine
from cup.utils.helper import stop, print_banner


with open("test/p4grammar.bcup") as f:
    grammar = f.read()

lexer = Lexer(grammar)
mp    = MetaParser(grammar, lexer, False)

print_banner("   TERMINALS   ", width = 50)
print mp.terminals

print_banner("   NONTERMINALS   ", width = 50)
print mp.nonterminals

print_banner("   TOKEN MAP   ", width = 50)
print mp.token_map

print_banner("   PRODUCTIONS   ", width = 50)
print mp.productions

mp.compute_firsts()
mp.compute_follows()

firsts = mp.productions.firsts
follows = mp.productions.follows

# Some Debug Info...
print_banner("   FIRSTS   ", width = 50)
for key in firsts:
    s = "FIRST({}) = {{".format(key)
    for val in firsts[key]:
        s += "{}, ".format(val)
    print s + "}"

print_banner("   FOLLOWS   ", width = 50)
for key in follows:
    if isinstance(key, Terminal):
        continue
    s = "FOLLOWS({}) = {{".format(key)
    for val in follows[key]:
        s += "{}, ".format(val)
    print s + "}"

print_banner("   PRODUCTIONS   ", width = 50)
productions = mp.productions
for p in productions:
    print p


print_banner("   TESTING STATE MACHINE   ", width=72, filler='=')

sm = LLStateMachine(mp)
sm.print_table()

