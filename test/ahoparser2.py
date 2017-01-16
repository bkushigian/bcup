from src.metaparser import MetaParser
from src.lexer.lexer import Lexer
from src.tokens import ( Token, TokenId, TokenNum, TokenEOF, 
                         TokenBinOpAdd, TokenBinOpAst)
from src.symbols import Terminal, NonTerminal, Production, terminalEOF
from src.statemachine import Item, State, LLStateMachine
from src.helper import stop, DEBUG
from sys import exit
import traceback

class TokenBinOpAst(Token):
    def __init__(self):
        self.name = "AST"
        self.symbol = "*"

class TokenLParen(Token):
    def __init__(self):
        self.name = "LPAREN"
        self.symbol = "("

class TokenRParen(Token):
    def __init__(self):
        self.name = "RPAREN"
        self.symbol = ")"

class MyLexer(Lexer):
    def __init__(self, program = None):
        self.program = program
        self.token_map = {
            "ID" : TokenId, "ADD" : TokenBinOpAdd, 
            "EOF" : TokenEOF, "AST" : TokenBinOpAst,
            "LPAREN" : TokenLParen, "RPAREN": TokenRParen,
            "NUM"    : TokenNum 
            }

    def load_program(self, program):
        self.program = program

    def lex(self):
        tokens = []
        if DEBUG: 
            print "LEX: PROGRAM =", self.program
            raw_input()
        toks = self.program.split()
        if DEBUG: 
            print "TOKS"
            print toks
            raw_input()
        for tok in toks:
            if tok.isdigit():
                tokens.append(TokenNum(tok))
            elif tok.isalnum():
                tokens.append(TokenId(tok))
            elif tok == '+':
                tokens.append(TokenBinOpAdd())
            elif tok == '*':
                tokens.append(TokenBinOpAst())
            elif tok == '(':
                tokens.append(TokenLParen())
            elif tok == ')':
                tokens.append(TokenRParen())
            if DEBUG: 
                print "TOK:", tok, " TOKEN[-1]", tokens[-1]

        tokens.append(TokenEOF())
        if DEBUG: 
            print "LEXER: TOKENS",
            print tokens
            raw_input()
        self.tokens = iter(tokens)

    def next(self):
        return self.tokens.next()


class Parser(object):
    def __init__(self, grammar):
        self.grammar  = grammar   # GRAMMAR FOR LANGUAGE
        grammar_lexer = MyLexer(grammar)
        grammar_lexer.lex()
        self.mp       = MetaParser(grammar, grammar_lexer, False)
        self.sm       = LLStateMachine(self.mp)
        self.table    = self.sm.table
        self.start    = self.mp.productions.start

        # Define terminals to be used

    def parse(self, program):
        self.lexer = MyLexer(program)
        self.lexer.lex()
        mp           = self.mp
        stack        = [terminalEOF, mp.start]  # $, S
        table        = self.table
        next_token   = self.lexer.next
        terminals    = mp.terminals
        terminals['EOF'] = terminalEOF
        consumed     = []    # Keep track of consumed characters
        # For printing out
        stacks = []
        action  = None

        def next_terminal():
            t = next_token()
            token = t
            consumed.append(t)
            if t.name in terminals:
                return terminals[t.name]
            print "TERMINALS:", terminals
            print "Parse Error! {} Not in Terminals".format(t.name)
            print type(t)

        def capture_state():
            return (list(stack), str(a), str(action))

        def str_stack(s):
            return ', '.join([str(i) for i in reversed(s)])

        def print_states():
            print
            print '=' * 80
            print "{0:=^80}".format("   PRODUCTIONS   ")
            print '=' * 80
            print
            print mp.productions
            print "CONSUMED: ", consumed
            stacks_widths = [0,0,0]
            for s in stacks:
                l = len(str_stack(s[0]))
                if l > stacks_widths[0]:
                    stacks_widths[0] = l
                if len(str(s[1])) > stacks_widths[1]:
                    stacks_widths[1] = len(str(s[1]))
                if len(str(s[2])) > stacks_widths[2]:
                    stacks_widths[2] = len(str(s[2]))

                    
            banner = "{0: ^{3}} | {1: ^{4}} | {2: ^{5}}".format(
                            'STACK', 'TERMINAL', 'ACTION', 
                            stacks_widths[0], stacks_widths[1], stacks_widths[2])
            print
            print 
            print '=' * len(banner)
            print banner
            print '=' * len(banner)
            for s in stacks:
                print "{0: >{3}} | {1: ^{4}} | {2: <{5}}".format(
                            str_stack(s[0]), s[1], s[2], 
                            stacks_widths[0], stacks_widths[1], stacks_widths[2])


        a = next_terminal()
        stacks.append(capture_state())
        X = stack[-1]
        while X != terminalEOF:
            if DEBUG:
                print " --- PARSER.PARSE(): TOP OF WHILE --- "
                print "    X = {}, a = {}".format(X,a)
                print "STACK:", stack
            if X == a:
                stack.pop()
                action = "match {}".format(str(a))
                a = next_terminal()
                stacks.append(capture_state())
            elif X.is_terminal():
                # error
                print "Parse Error: Unexpected terminal {}".format(X)
                print_states()
                exit()
            elif (X,a) not in table:
                print_states()
                print "Parse Error: No transition for ({},{})".format(X,a)
                traceback.print_stack()
                exit()
            else:
                p = table[(X,a)][0]
                # XXX: Next block is for debuggin
                if len(table[(X,a)]) > 1:
                    print "ERROR: TABLE NON UNIT LENGTH"
                    raw_input()
                rhs = list(p.rhs)
                if DEBUG:
                    print p  # Output production
                stack.pop()
                while rhs:
                    stack.append(rhs.pop())
                action = "production {}".format(p.num + 1)
                stacks.append(capture_state())
            X = stack[-1]



        print_states()
            
def main():
    # List of sentences in the language defined by grammar test/ahogrammar2.bcup
    prog1 = "id + id"
    prog2 = "id * id"
    prog3 = "a + b * c"
    prog4 = "1 + x"
    prog5 = "2 * 4"
    prog6 = "4 + myvarname * 7"
    prog7 = "3 + id * ( id + 2 + ( 1 * 2 ) ) * 5"
    prog8 = "1 + 2 * 3 + 4 * 5 + ( id + 2 + ( ( ( ( 1 ) ) ) + 1 * 2 ) ) * 5"

    programs = [prog1, prog2, prog3, prog4, prog5, prog6, prog7, prog8]

    with open("test/ahogrammar2.bcup") as f:
        grammar = f.read()
    if DEBUG: 
        print "CREATING PARSER"
    if DEBUG: 
        print
        print
        print "=" * 80
        print "{0:=^80}".format("   BEGINNING PARSE   ")
        print "=" * 80
        print
        print
    for p in programs:
        print "INPUT:", p
        parser = Parser(grammar)
        parser.sm.print_table()
        print 
        print
        print "=" * 80
        print "Parsing input:", p
        print "=" * 80
        print 
        print
        parser.parse(p)

if __name__ == "__main__":
    main()
