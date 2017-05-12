from cup.utils.helper import accumulator
from cup.parser.symbols import ( Symbol, Terminal, NonTerminal, 
                          Productions, startSymbol, terminalEOF,
                          Terminals, NonTerminals)

class MetaParser(object):
    ''' Meta Parser is responsible for parsing the grammar.'''
    def __init__(self, grammar_string, lexer, augment_grammar = True):
        ''' Assumes that everything is white space seperated,
            Comments on their own line (starting with '#').
            Productions are on their own line.
            
            grammar_string: The string literal to parse
            tokens: map of token names to their corresponding class constructors.
            augment_grammar: Should we add extra start symbol? Yes for LR, no 
                for LL.
        '''
        self.grammar_string  = grammar_string    # String literal with grammar
        self.augment_grammar = augment_grammar  # Should we create extra start sym?
        self.terminals    = Terminals()
        self.nonterminals = NonTerminals()
        self.lexer        = lexer               # The grammar lexer
        self.token_map    = lexer.token_map     # Map strings to tokens

        self.productions  = Productions(self.augment_grammar)

        Symbol.set_productions(self.productions)    # Allow all Symbol classes
                                                    # (including Token*) to have
                                                    # access to all productions
        
        # XXX: This is working (for now). 
        # TODO: Clean these lines up
        if augment_grammar:
            self.nonterminals += startSymbol
            self.start = startSymbol
        else:
            self.start = None

        self.terminals  += terminalEOF
        self.setup()

    def setup(self):
        ''' Must be called exactly once. Called by __init__ '''
        self._parse_grammar()
        self.compute_firsts()
        self.compute_follows()

    def str_to_symbol(self, raw_sym):
        split_sym = raw_sym.split(':')
        if len(split_sym) == 2:
            sym, binding = split_sym
        elif len(split_sym) == 1:
            sym, binding = raw_sym, None
        else:
            raise SyntaxError(raw_sym)
        if sym in self.terminals:
            return self.terminals[sym], binding
        if sym in self.nonterminals:
            return self.nonterminals[sym], binding
        raise ValueError("{}".format(sym))

    def compute_firsts(self):
        self.productions.compute_firsts()

    def compute_follows(self):
        self.productions.compute_follows(self.start)

    def firsts_of_string(self, symstr):
        return self.productions.firsts_of_string(symstr)

    def _parse_grammar(self):
        ''' 
        This is an unwieldly beast. It's just a big loop that does stuff.
        Peruse at your own risk.
        '''
        global startSymbol
        foundStart = False    # We want to find the start symbol
        lines = iter(self.grammar_string.split('\n'))
        for line in lines:
            if line.strip().startswith('#'):
                continue        # COMMENT
            elif "nonterminal" in line:
                terms = line.split()
                assert len(terms) == 3
                assert terms[0] == 'nonterminal'

                tp   = terms[1]
                name = terms[2]

                assert name not in self.nonterminals, "nonterminal {} already declared".format(name)
                assert name not in self.terminals,    "terminal {} is already declared".format(name)
                self.nonterminals[name] = NonTerminal(name, tp)

            elif "terminal" in line:
                terms = line.split()
                assert len(terms) == 2
                assert terms[0] == 'terminal'
                name = terms[1]
                assert name in self.token_map,        "no lexer token by name {}".format(name)
                assert name not in self.nonterminals, "nonterminal {} already declared".format(name)
                assert name not in self.terminals,    "terminal {} is already declared".format(name)
                self.terminals[name] = Terminal(name)

            elif line.strip():
                terms = line.split()
                current_nt = None           # Current non terminal
                while ';' not in terms:     # Assumes ';' on own line
                    if terms == []:
                        try:
                            line = lines.next()
                            continue
                        except:
                            break
                    if terms[0].isalnum():  # Found a NonTerminal
                        name = terms[0]
                        assert name in self.nonterminals, "no nonterminal {}".format(name)
                        assert len(terms) > 1 and terms[1] == '::='
                        # Update Start Symbol if necessary
                        current_nt = self.nonterminals[name]
                        
                        #  Found the START symbol
                        if not foundStart:
                            foundStart = True
                            if self.augment_grammar:
                                self.start = startSymbol
                                startSymbol.add_production([current_nt])
                            else:
                                self.start = current_nt
                            # self.productions.add_start(self.start)
                        rhs = map(self.str_to_symbol, list(terms[2:]))

                        current_production = current_nt.add_production( rhs )

                    elif terms[0] == '|':
                        rhs = map(self.str_to_symbol, list(terms[1:]))
                        current_production = current_nt.add_production( rhs )

                    elif terms[0] == '{:':
                        # TODO: Check this
                        # Rules for code gen, add to current_production
                        code = ""
                        while True:         # Get code for production
                            try:
                                line = lines.next()
                                if ':}' in line:
                                    current_production.add_code(code)
                                    break
                                else:
                                    code += line + '\n'

                            except:
                                # TODO: Add debug error
                                print "Parse Error!"
                                break
                    else:
                        print "Error on line:"
                        print line

                    # Done with line, get next line or break if done
                    try:
                        line = lines.next()
                        terms = line.split()
                        continue
                    except:
                        break

