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
        if value and value[0] == value[-1] and value[0] == '"':
            value = value[1:-1]
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
            # XXX: Removed an lstrip - this looked to be a bug but it may come
            # back to haunt us! Just a warning!
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
            # XXX: Removed an lstrip - this looked to be a bug but it may come
            # back to haunt us! Just a warning!
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

