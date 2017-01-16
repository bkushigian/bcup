''' Generate a lexer from a luthor file input '''
import re
from sys import exit
from src.lexer.lexer import Lexer
from src.lexer.metatoken import ( MetaToken, StringToken, IntToken, CodeToken,
                                    ClassToken, NameToken, SectionToken,
                                    EqToken)
from src.helper import accumulator, error, failure, success, info

DEBUG = True                # For debug. Duh

# For parsing lex file
s_ws            = r'(\s)+'
s_comment       = r'#.*'
s_str           = r'"([\"]|[^"])*"'
s_class         = r'[A-Z]\w*'
s_name          = r'[a-z]\w*'
s_code          = r'(\{:)(.|[\n])*(:\})'
s_code          = r'(\{:)([^:]|:[^\}]|[\n])*(:\})'
s_sect          = r'(\{%)(.|[\n])*(%\})'
s_equals        = r'='

# To iterate over
pattern_strs = [s_ws, s_comment, s_str, s_class, s_name, s_code, s_sect,
     s_equals]

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

token_map = { 's_ws'            : None
            , 's_comment'       : None
            , 's_str'           : StringToken
            , 's_class'         : ClassToken
            , 's_name'          : NameToken
            , 's_code'          : CodeToken
            , 's_sect'          : SectionToken
            , 's_equals'        : EqToken
            }


class LexLuthor(Lexer):
    ''' 
    Lexically analyze a luthor file. Yes, this class name is precisely why I
    named my lexing module luthor.
    '''

    def __init__(self, program):
        if DEBUG:
            info("Initializing LexLuthor...")
        self._program = program
        blank_pattern = r'(?P<{0}>^{1})'
        self._meta_pattern  = re.compile('|'.join( 
            [blank_pattern.format( str_names[s], s) for s in pattern_strs]))
        self._groupindex = self._meta_pattern.groupindex
        self._queue = []
        if DEBUG:
            success("Completed LexLuthor Initialization")

    def __iter__(self):
        program    = str(self._program)
        groupindex = self._groupindex
        info("Creating LexLuthor iter")
        while program:
            if DEBUG:
                info("LexLuthor.__iter__(): looking for next symbol",1)
            if self._queue:
                result = self._queue[0]
                self._queue = self._queue[1:]
                if DEBUG:
                    success("LexLuthor.__iter__(): _queue non-empty, yielding {}".format(result), ind = 2)
                yield result

            match = self._meta_pattern.match(program)
            if match == None:
                raise SyntaxError(
                    error("LexLuthor.__iter__: No Match in '{}'.".format(
                        program[:min(40,len(program))])), 1)
            if DEBUG:
                info("LexLuthor.__iter__(): matched '{}'".format(match.group(0)), 1)
            start, end = match.span()
            program = program[end:]
            for i in groupindex:
                if match.group(i) != None:
                    val = match.group(i)
                    token_type = token_map[i]
                    if token_type != None:
                        token = token_map[i](val)
                        if DEBUG:
                            success("LexLuthor __iter__: lexed and yielding {}".format(token),ind =2)
                        yield token
            if DEBUG:
                info("LexLuthor __iter__: Bottom of while", 1)

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
        self.num        = self.counter.next()
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
            return 'e{}'.format(nameCounter.next())

        def processEntry(me):
            ''' Process a match entry, forming a regex string '''
            name = newName()
            pattern = '(?<{}>{})'.format(name, me.pattern)

        result = ''   # Store the string that will be written to lex.py


        for e in ordering:   
            if isinstance(e, MatchEntry):
                print 'Match Entry:', e, e.code
                



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
                    next_token = lexiter.next()
                except Exception as e:
                    ordering.append(MatchEntry(token))
                    break    # Exit the loop, no more tokens

                raw_input( "NEXT_TOKEN:" + str( next_token))
                if next_token.type == 'CODE':
                    ordering.append(MatchEntry(token, next_token))

                else:
                    ordering.append(MatchEntry(token))
                    lexer.putback(next_token)

        return ordering

# FOR DEBUG
def newluthor():
    print "New luthor being generated..."
    with open("test/luthor/test.luth") as f:
        program = f.read()
    luthor = LexLuthor(program)
    return luthor

def newlex():
    lex = LexerGenerator("test/luthor/test.luth", None)
    return lex

