from src.metaparser import MetaParser
from src.lexer.lexer import Lexer
from src.tokens import ( Token, TokenId, TokenNum, TokenEOF, 
                         TokenBinOpAdd, TokenBinOpAst)
from src.symbols import Terminal, NonTerminal, Production, terminalEOF
from src.statemachine import Item, State, LLStateMachine
from src.helper import stop, DEBUG
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


        
