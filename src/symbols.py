from src.helper import accumulator, stop
from src.lexer.lexer import Token

class Production(object):
    ''' The production class holds a single grammar production, along with some
    meta information (such as the production number) and the associated code
    string that will build the parse tree.'''
    _name = 'Production'
    def __init__(self, lhs, rhs, code = ''):
        assert isinstance(lhs, NonTerminal), "lhs {} not an instance of NonTerminal".format(lhs)
        self.lhs = lhs
# TODO: rhs is currently a list of (type,binding) tuples, but this expects a
# list of types
        self.rhs, self.bindings = (), ()
        if len(rhs):
            self.rhs, self.bindings = zip(*rhs)   # rhs is a tuple of Symbols

        self.code = code
        self.num = -1

    def add_code(self, code):
        if not code:
            return

        print "Production code:"
        print code
        lines = code.split('\n')
        indent = '  ' # Indent String
        stack = [0]    # Stack for indent depths
        newcode = ''     # Will rewrite code

        # XXX: THIS DOES NOT CHECK FOR GOOD WHITE SPACE FORMATTING
        # TODO: Check for white space formatting
        for line in lines:
            cind = len(line) - len(line.lstrip())
            print stack
            print cind
            if cind > stack[-1]:
                stack.append(cind)
            else:
                while stack and cind < stack[-1]:
                    stack.pop()
            newcode += '{}\n'.format((indent * (len(stack)-1) ) + line.strip())
        self.code = newcode
        print "NEWCODE"
        print newcode

    def __repr__(self):
        return "{} --> {}".format(str(self.lhs), " ".join(map(str,self.rhs)))

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __hash__(self):
        return hash((self.lhs,self.rhs))

class Productions(object):
    ''' The Productions class holds the collection of productions associated
    with a grammar. This could also maybe be named the Grammar class.'''
    _name = 'Productions'
    def __init__(self, augment_grammar):
        # XXX: There is a lot of duplication of info here.
        self._production_map  = {}   # A map from nonterms to a list of prods
        self._productions     = []   # A list of productions
        # TODO: Use Terminals/NonTerminals classes
        self.terminals       = Terminals()
        self.nonterminals    = NonTerminals()
        # TODO: This may be obsolete
        self.accum = accumulator(0) # Keep track of production numbers
        self.augment_grammar = augment_grammar
        # The start symbol of the grammar
        self.start           = None
    
    def __getitem__(self, n):
        if isinstance(n, int):
            if n <= -len(self._productions) or n > len(self._productions):
                raise IndexError("Index {} out of bounds".format(n))
            return self._productions[n]
        elif isinstance(n, NonTerminal):
            if n not in self._productions_map:
                raise KeyError("{}".format(n))
            return self._productions_map[n]
        raise ValueError("Expected type int or type NonTerminal")

    def __iadd__(self, prod):
        ''' Adds a single production to instance '''
        if not isinstance(prod, Production):
            raise ValueError(prod)
        if prod.lhs not in self.nonterminals:
            self.nonterminals += prod.lhs
            self._production_map[prod.lhs] = []
        self._production_map[prod.lhs].append(prod.rhs)
        prod.num = self.accum.next()
        self._productions.append(prod)
        for sym in prod.rhs:
            if isinstance(sym, Terminal):
                self.terminals += sym
        return self

    def add_start(self, start):
        ''' Update with a start symbol. At the time of reading a grammar we
        don't know if we want to augment it or not. This should probably be
        fixed at some point.'''
        self.start = start
        self.nonterminals += start
        

    def get_productions_for(self, nt):
        ''' Return a set of all productions for nonterminal `nt`. '''
        assert isinstance(nt, NonTerminal), "Can't get productions for terminals"
        result = set()
        for p in self._productions:
            if nt == p.lhs:
                result.add(p)
        return result

    def compute_firsts(self):
        ''' Go through all productions, compute first and follows. '''
        firsts = {}
        for key in self.nonterminals:     # Initialize these to empty
            firsts[key] = set()
        for term in self.terminals:
            firsts[term] = set()
            firsts[term].add(term)

        while True:
            updated = False     # Have we updated firsts?
            # Loop thru nonterminals, add first sets
            for prod in self._productions:
                rhs = prod.rhs  # Get the RHS of the production
                lhs = prod.lhs  # Get the NonTerminal to work on
                assert isinstance(lhs, NonTerminal)
                if not rhs:  # TODO: Update with emptyString
                    if emptyString not in firsts[lhs]:
                        firsts[lhs].add(emptyString)
                        updated = True
                    continue
                for X in rhs:
                    for f in firsts[X]: 
                        if f not in firsts[lhs]:
                            updated = True
                            firsts[lhs].add(f)
                    if emptyString not in firsts[X]:
                        # There is no empty string in firsts[X], so we break.
                        # Otherwise, continue adding to firsts
                        break
            if not updated:
                break
        self.firsts = firsts

        # Now, update symbols local firsts set
        for symbol in list(self.nonterminals) + list(self.terminals):
            symbol.firsts = firsts[symbol]
                        
    def firsts_of_string(self, symstr, remove_empty_string = False):
        ''' Compute the FIRST set of a string X_1 X_2 X_3 ... X_n'''
        firsts = set()
        if len(symstr) == 0 and not remove_empty_string:
            firsts.add(emptyString)
            return firsts

        for sym in symstr:
            firsts.update(sym.firsts)
            if emptyString not in sym.firsts:
                break
        if remove_empty_string and emptyString in firsts:
            firsts.remove(emptyString)
        return firsts

    # TODO: What does this do?
    def follows_of_string(self, symstr, remove_empty_string = False):
        ''' Compute the FOLLOW set of a string - might not be used (or correctly
        defined). If I'm being honest, I have no idea how it got here...'''
        follows = set()
        for sym in symstr:
            follows.update(sym.follows)
            if emptyString not in sym.follows:
                break
        if remove_empty_string and emptyString in follows:
            follows.remove(emptyString)
        return follows

    def can_be_empty(self, lhs):
        ''' Determine if a non-terminal can derive the empty string. '''
        # TODO: Memoize?
        for term in lhs:
            if emptyString not in term.firsts:
                return False
        return True

    def compute_follows(self, start_sym = None):
        ''' 
        Compute the follow sets for nonterminal A. From Aho, for nonterminal
        A we define FOLLOW(A) := { t : t is TERMINAL, there is a sentential form
        alpha A t beta}. That is, it is the set of terminals that can directly
        follow A in some sentential form.
        '''
        if start_sym == None:
            start_sym = self.start
        follows = {}
        for key in self.nonterminals:     # Initialize these to empty
            follows[key] = set()
        for term in self.terminals:
            follows[term] = set()
        follows[start_sym].add(terminalEOF)
        
        productions = self._productions
        while True:   # Fixed Point Algorithm
            updated = False
            for prod in productions:
                A, rhs = prod.lhs, prod.rhs

                # Loop through rhs
                for i in range(len(rhs)):
                    B = rhs[i]
                    if isinstance(B, Terminal):
                        continue
                    right_productions = rhs[i+1:]
                    if right_productions:   # There are terms following term
                                            # Use Rule (1)
                        firsts_of_right_productions = self.firsts_of_string(right_productions, True)
                        if emptyString in firsts_of_right_productions:
                            firsts_of_right_productions.remove(emptyString)
                        if not firsts_of_right_productions.issubset(follows[B]):
                            updated = True
                            follows[B].update(firsts_of_right_productions)
                        if self.can_be_empty(rhs[i+1:]):
                            if not follows[A].issubset(follows[B]):
                                updated = True
                                follows[B].update(follows[A])

                    else:           # There are no terms following term
                                    # Use Rule (2)
                        if not follows[A].issubset(follows[B]):
                            updated = True
                            follows[B].update(follows[A])
                            if emptyString in follows[B]:
                                follows[B].remove(emptyString)

            if not updated:
                self.follows = follows
                break
        for nt in self.nonterminals:
            nt.follows = self.follows[nt]


    def __repr__(self):
        # XXX: This is kind of hacky...
        s = ""
        accum = accumulator(1)
        for key in self.nonterminals:
            if s:
                s += '\n'
            s += "({}) {} ::= {}".format(accum.next(), key,
                        self._production_map[key][0])
            l = len(str(key))
            for p in self._production_map[key][1:]:
                s += "\n({}) {}  |  {}".format(accum.next(), l * ' ', p)
            
        return s 

    def __iter__(self):
        return iter(self._productions)


class Symbol(object):
    symbolSet = set()
    productions = None
    def __init__(self):
        self._name = 'Symbol'

    @staticmethod
    def set_productions(prod):
        ''' This allows all classes derived from Symbol to see the full set of
        productions. This will be necessary during the parse. '''
        Symbol.productions = prod

    def is_terminal(self):
        return False

    def is_nonterminal(self):
        return False

    @staticmethod
    def reset():
        Symbol.symbolSet = set()
        Symbol.productions = None
        

class Terminal(Symbol):
    def __init__(self, name):
        self._name = 'Terminal'
        self.name = name
        if self in self.symbolSet:
            print "*** ERROR - {} already created".format(self)
        self.symbolSet.add(self)
        self.firsts   = [self]
        self.follows  = []

    def add_to_follow(self, f):
        self.follow.append(f)

    def add_to_first(self, f):
        self.first.append(f)

    def is_terminal(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Terminal) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<{}>".format(self.name)

    def __hash__(self):
        return hash(self.name)
        

class NonTerminal(Symbol):
    def __init__(self, name, tp, symbol = None):
        self._name = 'NonTerminal' # Type Name
        self.my_prods = []      # Local Productions: self -> alpha
        self.name     = name    # Name of nonterminal, specified by grammar
        self.type     = tp      # Type of nonterminal, specified by grammar
        self.full_print = False

        if self in self.symbolSet:
            print "*** ERROR - {} already created".format(self)

        self.symbolSet.add(self)
        self.firsts   = []     # FIRST(self)
        self.follows  = []     # FOLLOW(self)

    def add_to_follow(self, f):
        self.follow.append(f)

    def add_to_first(self, f):
        self.first.append(f)

    def add_production(self, rhs):
        self.my_prods.append(Production(self, rhs))
        self.productions += self.my_prods[-1]
        return self.my_prods[-1]

    def is_nonterminal(self):
        return True

    def __eq__(self, other):
        return isinstance(other,NonTerminal) and self.name == other.name and self.type == other.type


    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash( (self.name, self.type) )

    def __repr__(self):
        if self.full_print:
            return "<{} {}>".format(self.type, self.name)
        return "<{}>".format(self.name)


class Symbols(object):
    ''' A collection of symbols to be used during the parse phase '''
    def __init__(self):
        self._name = 'Symbols'
        self._symbols   = []
        self._symbolset = set()
        self._namemap   = {}
        self._elem_type = Symbol

    def __iadd__(self, sym):
        assert isinstance(sym, self._elem_type), "{} is not instance of {}".format(sym, self._elem_type)
        if sym not in self._symbolset:
            self._symbolset.add(sym)
            self._symbols.append(sym)
            self._namemap[sym.name] = sym
        return self

    def __add__(self, other):
        if not isinstance(other, Symbols):
            raise ValueError(str(other))

        if isinstance(self,Terminals):
            if isinstance(other, Terminals):
                res = Terminals()
            else:
                res = Symbols()
        elif isinstance(self, NonTerminals):
            if isinstance(other, NonTerminals):
                res = NonTerminals()
            else:
                res = Symbols()
        else:
            res = Symbols()
        for i in self:
            res += i
        for j in other:
            res += j
        return res
            
            
        
    def __call__(self, sym):
        pass

    def __getitem__(self, key):
        if isinstance(key, int):
            if key <= -len(self._symbols) or key > len(self._symbols):
                raise IndexError("Index {} out of bounds".format(key))
            return self._symbols[key]
        if isinstance(key, str):
            if key not in self._namemap:
                raise KeyError(key)
            return self._namemap[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if key in self._namemap:
                raise KeyError("{} already stored".format(key))
            if not isinstance(value, self._elem_type):
                raise TypeError("{}".format(value))
            self._namemap[key] = value
            if value not in self._symbolset:
                self._symbols.append(value)
                self._symbolset.add(value)
        else:
            raise KeyError(str(key))

    def __iter__(self):
        return iter(self._symbols)

    def __repr__(self):
        s = '\n'.join(["({}) {}".format(i+1,s) for (i,s) in enumerate(self)])
        return s

    def __contains__(self, obj):
        if isinstance(obj, str):
            return obj in self._namemap
        return obj in self._symbolset
            

class Terminals(Symbols):
    def __init__(self):
        super(Terminals, self).__init__()
        self._name      = 'Terminals'
        self._terminals = self._symbols
        self._elem_type = Terminal


class NonTerminals(Symbols):
    def __init__(self):
        super(NonTerminals, self).__init__()
        self._name = 'NonTerminals'
        self._nonterminals = self._symbols
        self._elem_type  = NonTerminal

startSymbol = NonTerminal("START", "PROG")
terminalEOF = Terminal("$")
emptyString = Terminal("EMPTY")
