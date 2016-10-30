from src.helper import accumulator
from src.symbols import Symbol, Terminal, NonTerminal, Productions

class MetaParser(object):
    def __init__(self, grammar_string, lexer):
        ''' Assumes that everything is white space seperated,
            Comments on their own line (starting with '#').
            Productions are on their own line.
            
            grammar_string: The string literal to parse
            tokens: map of token names to their corresponding class constructors.
            '''
        lines             = iter(grammar_string.split('\n'))
        self.terminals    = {}
        self.nonterminals = {}
        self.lexer        = lexer
        self.token_map    = lexer.token_map
        self.productions  = Productions()
        Symbol.set_productions(self.productions)

        startSymbol = NonTerminal("START", "PROG")
        terminalEOF = Terminal("$")
        self.nonterminals["START"] = startSymbol
        self.terminals['$'] = terminalEOF
        foundStart = False

        for line in lines:
            # print "line = {}".format(line)
            if line.strip().startswith('#'):
                continue        # COMMENT
            elif "nonterminal" in line:
                terms = line.split()
                assert len(terms) == 3
                assert terms[0] == 'nonterminal'
                tp   = terms[1]
                name = terms[2]
                # print "NONTERMINAL: {} {}".format(tp, name)
                assert name not in self.nonterminals, "nonterminal {} already declared".format(name)
                assert name not in self.terminals,    "terminal {} is already declared".format(name)
                self.nonterminals[name] = NonTerminal(name, tp)

            elif "terminal" in line:
                terms = line.split()
                assert len(terms) == 2
                assert terms[0] == 'terminal'
                name = terms[1]
                # print "TERMINAL: {}".format( name)
                assert name in self.token_map,        "no lexer token by this name"
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
                        if not foundStart:
                            print "FOUND START!"
                            foundStart = True
                            startSymbol.add_production([current_nt, terminalEOF])
                        rhs = map(self.str_to_symbol, list(terms[2:]))

                        current_production = current_nt.add_production( rhs )

                    elif terms[0] == '|':
                        rhs = map(self.str_to_symbol, list(terms[1:]))
                        current_production = current_nt.add_production( rhs )

                    elif terms[0] == '{:':
                        # Rules for code gen, add to current_production
                        code = ""
                        while True:         # Get code for production
                            try:
                                line = lines.next()
                                if ':}' in line:
                                    current_production.add_code(code)
                                    break
                                code += line

                            except:
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

    def str_to_symbol(self, sym):
        if sym in self.terminals:
            return self.terminals[sym]
        if sym in self.nonterminals:
            return self.nonterminals[sym]
        assert False, "sym: {} - not in any table".format(sym)

    def compute_firsts(self):
        self.productions.compute_firsts()

    def firsts_of_string(self, symstr):
        return self.productions.firsts_of_string(symstr)
                        



class Generator(object):
    def __init__(self, terminals, nonterminals, grammar_location):
        self.productions  = productions
        self.terminals    = terminals
        self.nonterminals = nonterminals


