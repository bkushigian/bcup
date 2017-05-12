from cup.lexer.lexer import Lexer, Token, TokenId, TokenNum, TokenEOF, TokenBinOpAdd
from cup.parser.metaparser import MetaParser
from cup.parser.symbols import Terminal, NonTerminal, Production, Symbol
from cup.parser.statemachine import Item, State, LRStateMachine
from cup.utils.helper import stop


grammar1 = '''nonterminal Expr E
nonterminal Expr Et
nonterminal Expr T
nonterminal Expr Tt
nonterminal Expr F

terminal    ID
terminal    ADD
terminal    AST
terminal    LPAREN
terminal    RPAREN

E  ::=  T Et
Et ::=  ADD  T Et
    | 
T  ::= F Tt
Tt ::= AST F Tt
    | 
F ::= LPAREN E RPAREN
    | ID
'''


grammar2 = '''nonterminal Expr G
nonterminal Expr E
nonterminal Expr Et
nonterminal Expr T

terminal    ID
terminal    NUM
terminal    ADD

G ::=  E
E ::=  T Et
Et ::= ADD E
    |  E
T ::= ID
   |  NUM
'''

grammar3 = '''
nonterminal Expr S
nonterminal Expr E
nonterminal Expr T

terminal    ID
terminal    NUM
terminal    ADD

S ::=  E
E ::=  T
   |   T ADD E
T ::= ID
   |  NUM
'''

grammar4 = '''
nonterminal Expr S
nonterminal Expr E
nonterminal Expr Et
nonterminal Expr T

terminal    ID
terminal    NUM
terminal    ADD

S ::=  E
E ::=  T Et
Et ::= ADD T Et
    | 
T ::= NUM
   |  ID
'''

errors = 0
def test_grammar(grammar):
    global errors
    Symbol.reset()
    print '=' * 80
    print '{0:=^80}'.format('   Testing Grammar   ')
    print '=' * 80
    print grammar
    try:
        print "Creating Lexer"
        lexer = Lexer(grammar)
        print "Creating MetaParser"
        mp    = MetaParser(grammar, lexer)
    except  Exception as e:
        print "ERROR:"
        print e
        errors += 1

for g in (grammar1, grammar2, grammar3, grammar4):
    test_grammar(g)
print "Errors: ", errors
