''' Generate a lexer from a luthor file input '''
import re
from sys import exit
from cup.lexer.lexer import Lexer
from cup.lexer.metatoken import ( MetaToken, StringToken, IntToken, CodeToken,
                                 ClassToken, NameToken, SectionToken,
                                 EqToken)
from cup.utils.helper import accumulator, error, failure, success, info
from math import gcd

DEBUG = False

# For parsing lex file
s_ws            = r'(\s)+'
s_comment       = r'#.*'
s_str           = r'"(\\\"|[^"])*"'
s_class         = r'[A-Z]\w*'
s_name          = r'[a-z]\w*'
s_code          = r'(\{-)([^-]|-[^\}])*(-\})'
s_code2         = r'(\{-)([^:]|:[^\}]|[\n])*(-\})'
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

        if DEBUG:
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
        # XXX: Queue should be a stack
        self._queue.append(val)

    def lex(self):
        # TODO: Conform to Lexer class
        pass

class LuthorREPattern(object):
    ''' Represents a Luthor Regular Expression and the associated code to be
    executed.'''
    def __init__(self, name, pattern, code):
        '''
        name : string literal of the pattern name
        pattern : regex to be matched
        code : CodeSegment instance
        '''
        self.name    = name
        self.pattern = pattern
        self.code    = code
    def __repr__(self):
        return '<LuthorREPattern {} {}>'.format(self.name, self.pattern)
    def __eq__(self, other):
        return self.name == other.name and self.pattern == other.pattern and self.code == other.code
    def __neq__(self, other):
        return not self.__eq__(other)

class CodeSegment(object):
    '''This class represents a piece of code that is tied to some action of the
    lexer. This can be used for a SectionToken or for a CodeToken. A raw string
    of Python code is passed and parsed/reformatted so that it can be easily
    modified as needed.'''

    def __init__(self, code, indent_str = ' '):
        self._raw = code
        self.indent_str = indent_str
        # The following get initialized in normalize_indents()
        self._indents = None
        self._lines   = None
        self._zipped  = None
        self.normalize_indents()

    def normalize_indents(self):
        # lines stores the list of of nonempty lines
        # TODO: strip comments
        code = self._raw
        lines = list(filter(lambda x: x.strip() != '', code.split('\n')))
        # stack stores information on the indent levels we have seen
        stack = []
        # indents is a list of normalized indentation levels. These are stored
        # as ints, where each indentation is stored as an incrementation by 1
        indents = []
        raw_indents = [len(line) - len(line.lstrip()) for line in lines]
        # Set up line[0]
        if code.strip():
            stack.append(raw_indents[0])
            indents.append(0)
            for i in raw_indents[1:]:
                if len(stack) < 1:
                    raise RuntimeError("Indentation error: " + line)
                if i == stack[-1]:
                    indents.append(len(stack) - 1)
                elif i > stack[-1]:
                    stack.append(i)
                    indents.append(len(stack) - 1)
                else:
                    while stack and stack[-1] > i:
                        stack.pop()
                    if stack == []:
                        raise RuntimeError("Illegal Indentation") # TODO: More info
                    if stack[-1] != i:
                        raise RuntimeError("Illegal Indentation") # TODO: More info
                    indents.append(len(stack) - 1)
                if DEBUG:
                    info(str(indents) +  str(stack))
        self._indents = indents
        self._lines   = lines
        self._zipped  = list(zip(indents, map(lambda s : s.lstrip(), lines)))

    def indent(self, depth = 1):
        return '\n'.join( [((i + depth) * self.indent_str) + l for i,l in self._zipped] )
    def __str__(self):
        return '\n'.join( [(i * self.indent_str) + l for i,l in self._zipped] )
    def __repr__(self):
        return "<{} @{}>".format("CodeSegment object", hex(id(self)))
    def __eq__(self, other):

        if len(self._zipped) != len(other._zipped): return False
        for (i, lself), (j, lother) in zip(self._zipped, other._zipped):
            if i != j or lself.strip() != lother.strip(): return False
        return True

    def __neq__(self, other):
        return not self.__eq__(other)


class LuthorFile(object):
    '''Represent a luthor file. Calls into a LexLuthor class and parses the
    output.'''
    def __init__(self, program):
        self.program = program
        self.patterns = []
        self.setup    = CodeSegment('')
        self.teardown = CodeSegment('')

    def parse(self):
        ''' Parse a stream of tokens  '''
        self.lexluthor = LexLuthor(self.program)
        tokens = list(self.lexluthor)
        name, pattern, code = None, None, None
        state = 'start'

        # XXX: This is a MacGyvered State Machine
        while tokens:
            token = tokens.pop(0)
            if state == 'start':
                if isinstance(token, SectionToken):
                    self.setup = CodeSegment(token.value)
                    state = 'seen-code'
                elif isinstance(token, NameToken):
                    name  = token.value
                    state = 'seen-name'
                else:
                    state = 'error'

            elif state == 'seen-code':
                if name is not None: # If we just saw a section name will be None
                    self.patterns.append( LuthorREPattern(name, pattern, code) )
                    name, pattern, code = None, None, None
                if isinstance(token, SectionToken):
                    self.teardown = CodeSegment(token.value)
                elif isinstance(token, NameToken):
                    name = token.value
                    state = 'seen-name'
                else:
                    state = 'error'

            elif state == 'seen-name':
                if isinstance(token, StringToken):
                    pattern = token.value
                    state = 'seen-pattern'
                else:
                    state = 'error'

            elif state == 'seen-pattern':
                if isinstance(token, CodeToken):
                    code = CodeSegment(token.value)
                    state = 'seen-code'
                elif isinstance(token, SectionToken):
                    state = 'seen-section'
                    if name is not None or pattern is not None or code is not None:
                        self.patterns.append(LuthorREPattern(name, pattern, CodeSegment('')))
                        name, pattern, code = None, None, None
                    self.teardown = CodeSegment(token.value)
                else:
                    state = 'error'

            elif state == 'error':
                raise RuntimeError("Unexpected token: {}".format(token))
                
        if name is not None or pattern is not None or code is not None:
            pattern = LuthorREPattern(name, pattern, code)
            self.patterns.append(pattern)
    def _print(self):
        print("="*80)
        print("Luthor File Stdout Dump")
        print("="*80)
        print("Setup:")
        print(self.setup.indent(2))
        print("Patterns:")
        for pattern in self.patterns:
            print(pattern)
        print("Teardown:")
        print(self.teardown.indent(2))

class LexerGenerator(object):
    ''' 
    Generate a lexer given an input file.
    '''
    def __init__(self, luthor, tokenfile):
        '''
        luthor: luthor file (on disk, not LuthorFile instance) to create a lexer
        from.
        tokenfile: file to import in the generated lexer
        '''
        self.luth = luthor
    def generate(self, output, py_version = '3'):
        '''output: where to store the output python file'''
        if py_version != '3':
            error("Aw crap, we can only generate Python3 Code! Proceding anyways")
            py_version = '3'
        # First, creat prefix
        luthorfile = LuthorFile


# FOR DEBUG
def newluthor():
    info("New luthor being generated...")
    with open("test/luthor/test.luth") as f:
        program = f.read()
    luthor = LexLuthor(program)
    return luthor

def newlex():
    lex = LexerGenerator("test/luthor/test.luth", None)
    return lex

