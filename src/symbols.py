from src.helper import accumulator
from src.lexer import Token

class Production(object):
    def __init__(self, lhs, rhs):
        assert isinstance(lhs, NonTerminal), "lhs {} not an instance of NonTerminal".format(lhs)
        self.lhs = lhs
        self.rhs = tuple(rhs)
        self.code = ""

    def add_code(self, code):
        self.code = code

    def __repr__(self):
        return "{} --> {}".format(str(self.lhs), " ".join(map(str,self.rhs)))

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __hash__(self):
        return hash((self.lhs,self.rhs))

class Productions(object):
    def __init__(self):
        # XXX: There is a lot of duplication of info here.
        self.production_map  = {}   # A map from nonterms to a list of prods
        self.keys            = []   # Keep the keys ordered, these are NTs
        self.production_nums = {}   # A map from productions to their numbers
        self.productions     = []   # A list of productions
        self.accum = accumulator(0) # Keep track of production numbers
        self.terminals       = set()

    def add_production(self, prod):

        if prod.lhs not in self.production_map:
            self.keys.append(prod.lhs)
            self.production_map[prod.lhs] = []
        self.production_map[prod.lhs].append(prod.rhs)
        self.production_nums[prod] = self.accum.next()
        self.productions.append(prod)
        for sym in prod.rhs:
            if isinstance(sym, Terminal):
                self.terminals.add(sym)

    def compute_firsts(self):
        ''' Go through all productions, compute first and follows '''
        firsts = {}
        for key in self.keys:     # Initialize these to empty
            firsts[key] = set()
        for term in self.terminals:
            firsts[term] = set()
            firsts[term].add(term)

        while True:
            update = False    # Have we updated firsts?
            # Loop thru nonterminals, add first sets
            for prod in self.productions:
                rhs = prod.rhs  # Get the RHS of the production
                lhs = prod.lhs  # Get the NonTerminal to work on
                assert isinstance(lhs, NonTerminal)
                if not rhs:  # TODO: Update with emptyString
                    if emptyString not in firsts[lhs]:
                        firsts[lhs].add(emptyString)
                        update = True
                    continue
                for X in rhs:
                    for f in firsts[X]: 
                        if f not in firsts[lhs]:
                            update = True
                            firsts[lhs].add(f)
                    if emptyString not in firsts[X]:
                        # There is no empty string in firsts[X], so we break.
                        # Otherwise, continue adding to firsts
                        break
            if not update:
                break
        self.firsts = firsts

        # Now, update symbols local firsts set
        for symbol in self.keys + list(self.terminals):
            symbol.firsts = firsts[symbol]
                        
    def firsts_of_string(self, symstr):
        firsts = set()
        for sym in symstr:
            firsts.update(sym.firsts)
            if emptyString not in sym.firsts:
                return firsts

    def compute_follows(self):
        follows = {}
        for key in self.keys:     # Initialize these to empty
            follows[key] = set()
        for term in self.terminals:
            follows[term] = set()
        follows[startSymbol].update(self.terminals['EOF'])

        update = False
        pass

    def __repr__(self):
        # XXX: This is kind of hacky...
        s = ""
        accum = accumulator(1)
        for key in self.keys:
            print "type of key = ", type(key)
            if s:
                s += '\n'
            s += "({}) {} ::= {}".format(accum.next(), key,
                        self.production_map[key][0])
            l = len(str(key))
            for p in self.production_map[key][1:]:
                s += "\n({}) {}  |  {}".format(accum.next(), l * ' ', p)
            
        return s 

class Symbol(object):
    symbolSet = set()
    productions = None
    @staticmethod
    def set_productions(prod):
        Symbol.productions = prod

class Terminal(Symbol):
    def __init__(self, name):
        self.name = name
        if self in self.symbolSet:
            print "*** ERROR - {} already created".format(self)
        self.symbolSet.add(self)
        self.firsts   = []
        self.follows  = []

    def add_to_follow(self, f):
        self.follow.append(f)

    def add_to_first(self, f):
        self.first.append(f)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<{}>".format(self.name)

    def __hash__(self):
        return hash(self.name)
        

class NonTerminal(Symbol):
    def __init__(self, name, tp):
        self.my_prods = []
        self.name     = name
        self.type     = tp
        if self in self.symbolSet:
            print "*** ERROR - {} already created".format(self)
        self.symbolSet.add(self)
        self.firsts   = []
        self.follows  = []

    def add_to_follow(self, f):
        self.follow.append(f)

    def add_to_first(self, f):
        self.first.append(f)

    def add_production(self, rhs):
        self.my_prods.append(Production(self, rhs))
        self.productions.add_production(self.my_prods[-1])
        return self.my_prods[-1]

    def __eq__(self, other):
        return self.name == other.name and self.tp == other.tp

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash( (self.name, self.type) )
    def __repr__(self):
        return "<{} {}>".format(self.type, self.name)


emptyString = Terminal("EMPTY")

