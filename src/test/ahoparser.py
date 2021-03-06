from cup.lexer.lexer import Lexer
from cup.parser.metaparser import MetaParser
from cup.lexer.tokens import ( Token, TokenId, TokenNum, TokenEOF, 
                         TokenBinOpAdd, TokenBinOpAst)
from cup.parser.symbols import Terminal, NonTerminal, Production, terminalEOF
from cup.parser.statemachine import Item, State, LLStateMachine
from cup.utils.helper import stop, DEBUG
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
            "LPAREN" : TokenLParen, "RPAREN": TokenRParen
            }

    def load_program(self, program):
        self.program = program

    def lex(self):
        tokens = []
        if DEBUG: 
            print("LEX: PROGRAM =", self.program)
            input()
        toks = self.program.split()
        if DEBUG: 
            print("TOKS")
            print(toks)
            input()
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
                print("TOK:", tok, " TOKEN[-1]", tokens[-1])

        tokens.append(TokenEOF())
        if DEBUG: 
            print("LEXER: TOKENS", end=' ')
            print(tokens)
            input()
        self.tokens = iter(tokens)

    def __next__(self):
        return next(self.tokens)


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
        next_token   = self.lexer.__next__
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
            print("TERMINALS:", terminals)
            print("Parse Error! {} Not in Terminals".format(t.name))
            print(type(t))

        def capture_state():
            return (list(stack), str(a), str(action))

        def str_stack(s):
            return ', '.join([str(i) for i in reversed(s)])

        def print_states():
            print()
            print('=' * 80)
            print("{0:=^80}".format("   PRODUCTIONS   "))
            print('=' * 80)
            print()
            print(mp.productions)
            print("CONSUMED: ", consumed)
            print("STACK                         , TERMINAL, ACTION")
            for s in stacks:
                print("{0: >29} | {1: <8} | {2: <8}".format(str_stack(s[0]), s[1], s[2]))


        a = next_terminal()
        stacks.append(capture_state())
        X = stack[-1]
        while X != terminalEOF:
            if DEBUG:
                print(" --- PARSER.PARSE(): TOP OF WHILE --- ")
                print("    X = {}, a = {}".format(X,a))
                print("STACK:", stack)
            if X == a:
                stack.pop()
                action = "match {}".format(str(a))
                a = next_terminal()
                stacks.append(capture_state())
            elif X.is_terminal():
                # error
                print("Parse Error: Unexpected terminal {}".format(X))
                print_states()
                exit()
            elif (X,a) not in table:
                print_states()
                print("Parse Error: No transition for ({},{})".format(X,a))
                traceback.print_stack()
                exit()
            else:
                p = table[(X,a)][0]
                # XXX: Next block is for debuggin
                if len(table[(X,a)]) > 1:
                    print("ERROR: TABLE NON UNIT LENGTH")
                    input()
                rhs = list(p.rhs)
                if DEBUG:
                    print(p)  # Output production
                stack.pop()
                while rhs:
                    stack.append(rhs.pop())
                action = "production {}".format(p.num + 1)
                stacks.append(capture_state())
            X = stack[-1]



        print_states()
            
def main():
    prog1 = "id + id * id"
    with open("test/ahogrammar.bcup") as f:
        grammar = f.read()
    if DEBUG: 
        print("CREATING PARSER")
    parser = Parser(grammar)
    if DEBUG: 
        print()
        print()
        print("=" * 80)
        print("{0:=^80}".format("   BEGINNING PARSE   "))
        print("=" * 80)
        print()
        print()
    parser.sm.print_table()
    parser.parse(prog1)

if __name__ == "__main__":
    main()
