from cup.lexer.lexer import Lexer
from cup.parser.metaparser import MetaParser
from cup.parser.tokens import ( Token, TokenId, TokenNum, TokenEOF, 
                         TokenBinOpAdd, TokenBinOpAst)
from cup.parser.symbols import Terminal, NonTerminal, Production, terminalEOF
from cup.parser.statemachine import Item, State, LLStateMachine
from cup.utils.helper import stop, DEBUG
from sys import exit

PARSER_DEST = "bin/parser.py"

class Generator(object):
    def __init__(self, terminals, nonterminals, grammar_location):
        raise NotImplementedError()
        self.productions  = productions
        self.terminals    = terminals
        self.nonterminals = nonterminals

class LLGenerator(object):
    ''' Generate an LL Parser '''
    def __init__(self, grammar, lexer):
        self.grammar = grammar
        self.glexer  = glexer
        self.mp      = MetaParser(grammar, glexer, False)
        self.sm      = LLStateMachine(self.mp)
        self.table   = table
        self.start   = self.mp.productions.start


        
