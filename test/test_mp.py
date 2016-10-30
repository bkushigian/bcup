from src.generator import MetaParser
from src.lexer import Lexer, Token, TokenId, TokenNum, TokenEOF, TokenBinOpAdd
from src.symbols import Terminal, NonTerminal, Production

with open("test/grammar.notcup") as f:
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
