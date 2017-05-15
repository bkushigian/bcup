''' 
MetaTokens are used by lexing generator and shouldn't be used by client
programs. These help with lexing the luthor file.

Eventually this will be obsolete (we will be building our lexing generator with
normal token classes)
'''

class MetaToken(object):
    ''' Token for LexerGenerator '''
    def __init__(self, value):
        self.type = None
        self.value = value
    def __repr__(self):
        return "{}[{}]".format(self.type, self.value)

class StringToken(MetaToken):
    def __init__(self, value):
        self.value = value
        self.type = 'StringMetaToken'
    def __repr__(self):
        return "{}[\"{}...\"]".format(self.type, self.value[:min(12, len(self.value))])

class IntToken(MetaToken):
    def __init__(self, value):
        self.value = value
        self.type = 'IntMetaToken'

class CodeToken(MetaToken):
    def __init__(self, value):
        try:
            index = value.index('-}')   # Get index of trailing delimiter
            value = value[2:index]      # Strip leading delimiter
            value = value[:index]       # Strip trailing delimiter
            # TODO: Inefficient
            while value and value[0] in (' \t\n\r'): # Strip leading whitespace
                value = value[1:]
        except Exception as e:
            # TODO: Make more expressive
            print("Lex error:", e)
        self.value = value
        self.type = 'CodeMetaToken'
    def __repr__(self):
        output = self.value[ : min(32, len(self.value), self.value.index('\n'))]
        return "{}[\"{}...\"]".format( self.type, output)

class ClassToken(MetaToken):
    def __init__(self, value):
        self.value = value
        self.type = 'ClassMetaToken'

class NameToken(MetaToken):
    def __init__(self, value):
        self.value = value
        self.type = 'NameMetaToken'


class SectionToken(MetaToken):
    ''' A section is a place to put python code '''
    def __init__(self, value):
        try:
            value = value[2:]           # Strip leading delimiter
            index = value.index('%}')   # Get index of trailing delimiter
            value = value[:index]       # Strip trailing delimiter
            value = value.lstrip()      # Get rid of leading white space
        except Exception as e:
            # TODO: Make more expressive
            print("Lex error", e)

        self.value = value
        self.type = "SectMetaToken"
    def __repr__(self):
        output = self.value[ : min(32, len(self.value), self.value.index('\n'))]
        return "{}[\"{}...\"]".format( self.type, output)

class EqToken(MetaToken):
    def __init__(self, value = '='):
        self.value = value
        self.type = "EqualsMetaToken"

