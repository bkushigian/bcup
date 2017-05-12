from cup.lexer.luthor import LexLuthor, LexerGenerator, newluthor, newlex
from cup.parser.helper import error, success, failure, info, banner, GREEN

def test_LexLuthorInit():
    luthor = newluthor()

def test_LexLuthorIter():
    luthor = newluthor()
    luthor_iter = iter(luthor)
    tokens = []
    try:
        for item in luthor_iter:
            tokens.append(item)
    except Exception as e:
        error("Error: {}".format(e))

    banner("FOUND TOKENS", attrs=GREEN)
    for item in tokens:
        info(str(item), 2, '')

def test_LexerGenerator():
    lexer = newlex()
    lexer.build_lexer()
    


def main():
    gs = globals()
    for name in gs.keys():
        if name.startswith('test_'):
            f = gs[name]
            f()

if __name__ == '__main__':
    main()
        
