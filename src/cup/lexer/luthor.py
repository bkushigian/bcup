''' Generate a lexer from a luthor file input '''
import re
from sys import exit
from cup.lexer.lexer import Lexer
from cup.lexer.metatoken import ( MetaToken, StringToken, IntToken, CodeToken,
                                 ClassToken, NameToken, SectionToken,
                                 EqToken)
from cup.utils.helper import accumulator, error, failure, success, info

DEBUG = True                # For debug. Duh

# For parsing lex file
s_ws            = r'(\s)+'
s_comment       = r'#.*'
s_str           = r'"(\\\"|[^"])*"'
s_class         = r'[A-Z]\w*'
s_name          = r'[a-z]\w*'
s_code          = r'(\{-)([^-]|-[^\}])*(-\})'
s_code2         = r'(\{-)([^:]|:[^\}]|[\n])*(-\})'
# s_sect          = r'(\{%)(.|[\n])*(%\})'
s_sect          = r'(\{%)([^%]|%[^\}])*(%\})'
s_equals        = r'='

r_ws       = re.compile(s_ws)
r_comment  = re.compile(s_comment)
r_str      = re.compile(s_str)
r_class    = re.compile(s_class)
r_name     = re.compile(s_name)
r_code     = re.compile(s_code)
r_code2    = re.compile(s_code2)
r_sect     = re.compile(s_sect)
r_equals   = re.compile(s_equals)



# To generate group names
str_names   = { s_ws            : 's_ws'
              , s_comment       : 's_comment'
              , s_str           : 's_str'
              , s_class         : 's_class'
              , s_name          : 's_name'
              , s_code          : 's_code'
              , s_sect          : 's_sect'
              , s_equals        : 's_equals'
              }

token_map = { s_ws            : None
            , s_comment       : None
            , s_str           : StringToken
            , s_class         : ClassToken
            , s_name          : NameToken
            , s_code          : CodeToken
            , s_sect          : SectionToken
            , s_equals        : EqToken
            }

pattern_token_map = { 
              r_ws            : None
            , r_comment       : None
            , r_str           : StringToken
            , r_class         : ClassToken
            , r_name          : NameToken
            , r_code          : CodeToken
            , r_sect          : SectionToken
            , r_equals        : EqToken
            }

class LexLuthor(Lexer):
    ''' 
    Lexically analyze a luthor file. Yes, this class name is precisely why I
    named my lexing module luthor.

    program: a plain text representation of a program to lex into tokens
    '''

    def __init__(self, program):
        if DEBUG:
            info("Initializing LexLuthor...")
        self._program = program
        self._queue = []

        if DEBUG:
            success("Completed LexLuthor Initialization")

    def __iter__(self):
        program = str(self._program)

        info("Creating LexLuthor iter")
        while program:
            if DEBUG:
                info("LexLuthor.__iter__(): looking for next symbol",1)
            if self._queue:
                result = self._queue.pop(0)
                if DEBUG:
                    success("LexLuthor.__iter__(): _queue non-empty, yielding {}".format(result), ind = 2)
                yield result

            # Check for pattern match
            pattern, match = None, None   # Default Values
            if r_comment.match(program):
                pattern = s_comment
                match = r_comment.match(program)
                if DEBUG:
                    success("Found COMMENT")
            elif r_str.match(program):
                pattern = s_str
                match = r_str.match(program)
                if DEBUG:
                    success("Found STRING")
            elif r_class.match(program):
                pattern = s_class
                match = r_class.match(program)
                if DEBUG:
                    success("Found CLASS")
            elif r_name.match(program):
                pattern = s_name
                match = r_name.match(program)
                if DEBUG:
                    success("Found NAME")
            elif r_code.match(program):
                pattern = s_code
                match = r_code.match(program)
                if DEBUG:
                    success("Found CODE")
            elif r_code2.match(program):
                pattern = s_code2
                match = r_code2.match(program)
                if DEBUG:
                    success("Found CODE2")
            elif r_sect.match(program):
                pattern = s_sect
                match = r_sect.match(program)
                if DEBUG:
                    success("Found SECTION")
            elif r_equals.match(program):
                pattern = s_equals
                match = r_equals.match(program)
                if DEBUG:
                    success("Found EQUALS")
            elif r_ws.match(program):
                pattern = s_ws
                match = r_ws.match(program)
                if DEBUG:
                    success("Found WHITESPACE")
            else:
                error("Couldn't find a match!")

            # s = ''
            # while s.strip() != 'q':
            #     s = input('>>> ').rstrip()
            #     if s == 'q':
            #         break
            #     exec(s)

            token_constructor = token_map[pattern]   # Grab token constructor to output
            start, end = match.span()

            if DEBUG:
                info("match start = {}, match end = {}".format(start, end))
                info("match string = {}".format(program[start: end]))

            program = program[end:]

            if token_constructor != None:
                # TODO: Error check?
                value = match.group(0)
                token = token_constructor(value)
                if DEBUG:
                    if '\n' in value:
                        info("value:\n\"{}\"".format(value))
                    info("value: {}".format(value))
                    success("LexLuthor __iter__: lexed and yielding {}".format(token),ind =2)
                yield token
            else:
                if DEBUG:
                    info("Program:\n{}\n{}\n{}\n".format('v'*78, program, '^'*78))

    def putback(self, val):
        '''
        Not the best solution but it works, this solves the problem of when
        we've looked ahead in our lexing (of the luthor file) and cannot use the
        token immediately. We then put that token back and deal with the input
        that we have.
        '''
        self._queue.append(val)

    def lex(self):
        # TODO: Conform to Lexer class
        pass
        
class MatchEntry(object):
    counter = accumulator(0)
    _entries = []             # Hold all MatchEntries
    def __init__(self, token, code = None):
        '''
        patern: regex pattern to match on
        code: code to execute on match
        '''
        self.code       = code
        self.num        = next(self.counter)
        self.name = 'e{}'.format(self.num)
        if token.type == 'STRING':
            self.pattern = '(?<{}>{})'.format(self.name, token.value)
        elif token.type == 'NAME':
            # This should output '(?<name>' + varname + ')'
            self.pattern = "'(?<{}>' + str({}) + ')'".format(self.name,
            token.value)

        self._entries.append(self)    # For iterating over later

    @staticmethod
    def iterator():
        return iter(MatchEntry._entries)

    def __hash__(self):
        return self.num

    def __eq__(self, other):
        ''' Checks that these are logically equivalent (not same instance) '''
        return self.pattern == other.pattern and self.code == other.code

    def __ne__(self, other):
        return self.code != other.code or self.pattern != other.pattern

    def __str__(self):
        return self.pattern


class LexerGenerator(object):
    ''' 
    Generate a lexer given an input file.
    '''
    def __init__(self, lexfile, tokenfilepath):
        '''
        lexfile: file with lex specs
        tokenfile: file with token code, created by user
        '''
        self.lexfile       = lexfile
        self.tokenfile     = tokenfilepath
        with open(lexfile) as f:
            lexstr = f.read()
        self.lexer = LexLuthor(lexstr)

        self.sections = []  
        self.patterns = []


    def build_lexer(self):
        ''' Build the actual lexer '''

        # ordering is a list of items to write to lex.py. It consists of string
        # literals and MatchEntry items. Each MatchEntry item should have a name
        # associated with it, arbitrarily generated. 
        ordering = self.parse()
        entryDict = {}
        nameCounter = accumulator(0)
        def newName():
            ''' Give unique names for each entry '''
            return 'e{}'.format(next(nameCounter))

        def processEntry(me):
            ''' Process a match entry, forming a regex string '''
            name = newName()
            pattern = '(?<{}>{})'.format(name, me.pattern)

        result = ''   # Store the string that will be written to lex.py


        for e in ordering:   
            if isinstance(e, MatchEntry):
                print('Match Entry:', e, e.code)
                



    def parse(self):
        ''' 
        We need to translate the luthor file into a lexer. To do this we
        need to construct an ordering on the input and wrap the appropriate
        parts of the luthor file (such as creating functions for setup,
        teardown, etc)

        returns a list of items to write to lex.py
        '''

        lexer = self.lexer      # This will be used for the putback method
        lexiter = iter(lexer)   # Iterate through the lexer
        ordering = []           # Hold constructed objects to be transformed
        current  = []
        # Construct ordering
        for token in lexiter:
            if token.type == 'SECTION':
                ordering.append(token.value)    # Hold the string literal

            elif token.type == 'NAME' or token.type == 'STRING':
                try:
                    next_token = next(lexiter)
                except Exception as e:
                    ordering.append(MatchEntry(token))
                    break    # Exit the loop, no more tokens

                input( "NEXT_TOKEN:" + str( next_token))
                if next_token.type == 'CODE':
                    ordering.append(MatchEntry(token, next_token))

                else:
                    ordering.append(MatchEntry(token))
                    lexer.putback(next_token)

        return ordering

# FOR DEBUG
def newluthor():
    print("New luthor being generated...")
    with open("test/luthor/test.luth") as f:
        program = f.read()
    luthor = LexLuthor(program)
    return luthor

def newlex():
    lex = LexerGenerator("test/luthor/test.luth", None)
    return lex

