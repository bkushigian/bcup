from src.metaparser import MetaParser
from src.lexer.lexer import Lexer
from src.tokens import ( Token, TokenId, TokenNum, TokenEOF, 
                         TokenBinOpAdd, TokenLParen, TokenRParen,
                         TokenBinOpAst)
from src.symbols import Terminal, NonTerminal, Production, terminalEOF
from src.statemachine import Item, State, LLStateMachine
from src.helper import stop
from sys import exit


class MyLexer(Lexer):
    def __init__(self, program = None):
        self.program = program
        self.token_map = {
            "ID" : TokenId, "ADD" : TokenBinOpAdd, 
            "EOF" : TokenEOF, "AST" : TokenBinOpAst,
            "LPAREN" : TokenLParen, "RPAREN": TokenRParen,
            "NUM" : TokenNum
            }

    def load_program(self, program):
        self.program = program

    def lex(self):
        tokens = []
        toks = self.program.split()
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

        tokens.append(TokenEOF())
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
            print "Parse Error! {} Not in Terminals".format(t.name)
            print type(t)

        def capture_state():
            return (list(stack), str(a), str(action))

        def str_stack(s):
            return ', '.join([str(i) for i in reversed(s)])

        def print_states():
            print
            print
            print "=" * 80
            print "{0:=^80}".format("   PRODUCTIONS   ")
            print "=" * 80
            print
            print
            print mp.productions
            print "CONSUMED: ", consumed
            print "STACK                         , TERMINAL, ACTION"
            for s in stacks:
                print "{0: >29} | {1: <8} | {2: <8}".format(str_stack(s[0]), s[1], s[2])


        a = next_terminal()
        stacks.append(capture_state())
        X = stack[-1]
        while X != terminalEOF:
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
                print "Parse Error: No transition for ({},{})".format(X,a)
                print_states()
                exit()
            else:
                p = table[(X,a)][0]
                if len(table[(X,a)]) > 1:
                    print "ERROR: TABLE NON UNIT LENGTH"
                    raw_input()
                rhs = list(p.rhs)
                stack.pop()
                while rhs:
                    stack.append(rhs.pop())
                action = "production {}".format(p.num + 1)
                stacks.append(capture_state())
            X = stack[-1]



        print_states()
            
def main():
    prog1 = "id + id + id"
    with open("test/p4grammar.bcup") as f:
        grammar = f.read()
    parser = Parser(grammar)
    parser.sm.print_table()
    parser.parse(prog1)

if __name__ == "__main__":
    main()
