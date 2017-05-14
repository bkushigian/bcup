import unittest
from cup.lexer.luthor import LexLuthor
from cup.lexer.metatoken import (StringToken, IntToken, CodeToken, ClassToken,
                                 NameToken, SectionToken, EqToken)

p1 = '''
{%
    tokens_matched = 0
%}

int_pattern "\d+"
{-
    RESULT = IntToken(MATCHED)
    tokens_matched += 1
-}
'''

p2 = r'''
{% 
    # GLOBAL CONFIGURATION 
    tokens_matched  = 0    # A normal python variable
%}

int_pattern "\d+"
{- 
    RESULT = IntToken(MATCHED) 
    tokens_matched += 1
-}

str_pattern "([\"]|[^\"])+"
{-
    RESULT = StrToken(MATCHED)
    tokens_matched += 1
-}

ws_pattern "\s"

{%  # Program Suffix
    print "Total tokens matched: {}".format(tokens_matched)
%}
'''

class TestLuthor(unittest.TestCase):
    def test_constructor(self):
        luthor = LexLuthor(p1)
        self.assertEqual(luthor._program, p)

    def test_tokenLength1(self):
        luthor = LexLuthor(p1)
        expect = [SectionToken, NameToken, StringToken, CodeToken]
        actual = list(iter(luthor))
        self.assertEqual(len(expect), len(actual))

    def test_tokenLength2(self):
        luthor = LexLuthor(p2)
        expect = [SectionToken, NameToken, StringToken, CodeToken, 
                                NameToken, StringToken, CodeToken,
                                NameToken, StringToken, CodeToken]
        actual = list(iter(luthor))
        self.assertEqual(len(expect), len(actual))

    def test_tokenTypes1(self):
        luthor = LexLuthor(p1)
        expect = [SectionToken, NameToken, StringToken, CodeToken]
        actual = list(iter(luthor))
        for e, a in zip(expect, actual):
            self.assertTrue(isinstance(a,e))

    def test_tokenTypes2(self):
        luthor = LexLuthor(p2)
        expect = [SectionToken, NameToken, StringToken, CodeToken, 
                                NameToken, StringToken, CodeToken,
                                NameToken, StringToken, CodeToken]
        actual = list(iter(luthor))
        for i,a in enumerate(actual):
            print(i,a)


