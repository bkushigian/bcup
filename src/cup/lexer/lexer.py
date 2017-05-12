''' lexer.py has the base Lexer class, as well as Token and Token* subclasses.
These are filler classes for tests and can (should) be overridden.
This lexer class is the default for parsing a grammar and can be extended to
parse different forms of grammars.'''

from cup.utils.helper import DEBUG
from cup.parser.tokens import *

class Lexer(object):
    ''' Trivial lexer, can be overridden, this adds id's and nums'''
    def __init__(self, program = None):
        self.program = program
        self.token_map = {"NUM" : TokenNum, "ID" : TokenId, "ADD" : TokenBinOpAdd, "EOF" : TokenEOF }
        if self.program:
            self.lex()

    def load_program(self, program):
        self.program = program

    def lex(self):
        ''' This splits the input file into strings. This should be overridden
        for any grammars as it presupposes that the grammar is white-space
        seperated (ie, this is a terrible lexer).
        '''
        #TODO: Remove lex and use __iter__(). Thus, no need for precomputation.
        tokens = []
        if DEBUG:
            print "LEX: PROGRAM =", self.program
            raw_input()

        toks = self.program.split()

        for tok in toks:
            if tok.isdigit():
                tokens.append(TokenNum(tok))
            elif tok.isalnum():
                tokens.append(TokenId(tok))
            elif tok == '+':
                tokens.append(TokenBinOpAdd('+'))

        tokens.append(tokenEOF)
        if DEBUG:
            print tokens
            raw_input()
        self.tokens = iter(tokens)

    def next(self):
        ''' If lex is overridden, this needs to be rewritten to. This is the
        main function defined for the Lexer class and is how the outside world
        talks to it.
        '''
        return self.tokens.next()

    def __iter__(self):
        pass
