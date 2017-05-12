from cup.parser.symbols import (Symbol, Terminal, NonTerminal, Symbols, Terminals,
                        NonTerminals, Production, Productions)

t1 = Terminal("ADD")
t2 = Terminal("AST")

ts = Terminals()
nts = NonTerminals()
print(ts._symbols)
print(ts)
ts += t1
print(ts)
print(ts._symbols)
ts += t2
print(ts._symbols)

try:
    print("ts[1] =", ts[1])
    print("ts[0] =", ts[0])
    print("ts[-1]=", ts[-1])
    print("ts[ts]=", ts[ts])
except:
    print("Failed")

print("ITER")
for t in ts:
    print(t)

print("ENUMERATE")
for t in enumerate(ts):
    print(t)

print("REPR")
print(ts)

print(t1 in ts)
print(2 in ts)


