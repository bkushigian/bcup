from src.helper import accumulator, stop
from src.lexer import Token



class Production(object):
    def __init__(self, lhs, rhs):
        assert isinstance(lhs, NonTerminal), "lhs {} not an instance of NonTerminal".format(lhs)
        self.lhs = lhs
        self.rhs = tuple(rhs)   # rhs is a tuple of Symbols
        self.code = ""
        self.num = -1

    def add_code(self, code):
        self.code = code

    def __repr__(self):
        return "{} --> {}".format(str(self.lhs), " ".join(map(str,self.rhs)))

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __hash__(self):
        return hash((self.lhs,self.rhs))

class Productions(object):
    def __init__(self, augment_grammar):
        # XXX: There is a lot of duplication of info here.
        self.production_map  = {}   # A map from nonterms to a list of prods
        self.nonterminals    = []   # Keep the keys ordered, these are NTs
        self.productions     = []   # A list of productions
        self.accum = accumulator(0) # Keep track of production numbers
        self.terminals       = set()
        self.augment_grammar = augment_grammar
        self.start           = None
    
    def add_start(self, start):
        self.start = start
        self.nonterminals.append(self.start)
        

    def add_production(self, prod):

        if prod.lhs not in self.production_map:
            self.nonterminals.append(prod.lhs)
            self.production_map[prod.lhs] = []
        self.production_map[prod.lhs].append(prod.rhs)
        prod.num = self.accum.next()
        self.productions.append(prod)
        for sym in prod.rhs:
            if isinstance(sym, Terminal):
                self.terminals.add(sym)

    def get_productions_for(self, nt):
        assert isinstance(nt, NonTerminal), "Can't get productions for terminals"
        result = set()
        for p in self.productions:
            if nt == p.lhs:
                result.add(p)
        return result

    def compute_firsts(self):
        ''' Go through all productions, compute first and follows '''
        firsts = {}
        for key in self.nonterminals:     # Initialize these to empty
            firsts[key] = set()
        for term in self.terminals:
            firsts[term] = set()
            firsts[term].add(term)

        while True:
            updated = False     # Have we updated firsts?
            # Loop thru nonterminals, add first sets
            for prod in self.productions:
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
        for symbol in self.nonterminals + list(self.terminals):
            symbol.firsts = firsts[symbol]
                        
    def firsts_of_string(self, symstr, remove_empty_string = False):
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

    def follows_of_string(self, symstr, remove_empty_string = False):
        follows = set()
        for sym in symstr:
            follows.update(sym.follows)
            if emptyString not in sym.follows:
                break
        if remove_empty_string and emptyString in follows:
            follows.remove(emptyString)
        return follows

    def can_be_empty(self, lhs):
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
        
        productions = self.productions
        while True:   # Fixed Point Algorithm
            updated = False
            # Loop through productions, using the following rules
            # from Aho:
            # 2) If A -> alpha B beta is a right sentential form:
            #         follows(B) += first(beta) - emptyString
            # 3) If A -> alpha B:
            #         follows(B) += follows(A)  

            print 
            print "TOP OF WHILE"
            for prod in productions:
                A, rhs = prod.lhs, prod.rhs

                # Loop through rhs
                for i in range(len(rhs)):
                    B = rhs[i]
                    if isinstance(B, Terminal):
                        continue

                    right_productions = rhs[i+1:]

                    print 
                    print "    PRODUCTION     :", prod
                    print "        TERM       :", B
                    print "        RIGHT PRODS:", right_productions

                    if right_productions:   # There are terms following term
                                            # Use Rule (1)
                        firsts_of_right_productions = self.firsts_of_string(right_productions, True)
                        if emptyString in firsts_of_right_productions:
                            print "        FIRSTS OF RIGHT :", firsts_of_right_productions
                            stop(" [!] EMPTY STRING!!! ")
                            firsts_of_right_productions.remove(emptyString)
                        print "        FIRST OF RP:", firsts_of_right_productions
                        if not firsts_of_right_productions.issubset(follows[B]):
                            updated = True
                            follows[B].update(firsts_of_right_productions)
                        if self.can_be_empty(rhs[i+1:]):
                            print "            CAN BE EMPTY"
                            if not follows[A].issubset(follows[B]):
                                updated = True
                                follows[B].update(follows[A])

                    else:           # There are no terms following term
                                    # Use Rule (2)
                        print "        FOLLOWS(A) :", follows[A]
                        print "        FOLLOWS(B) :", follows[B]
                        if not follows[A].issubset(follows[B]):
                            print "            UPDATING BY RULE 2"
                            updated = True
                            follows[B].update(follows[A])
                            if emptyString in follows[B]:
                                print " [!] EMPTY STRING!!!"
                                follows[B].remove(emptyString)
                    print "        FOLLOWS    :", follows[B]
                    stop(' [!] Is there an empty string? > ')

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

    def is_terminal(self):
        return False

    def is_nonterminal(self):
        return False

class Terminal(Symbol):
    def __init__(self, name):
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
        self.productions.add_production(self.my_prods[-1])
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


startSymbol = NonTerminal("START", "PROG")
terminalEOF = Terminal("$")
emptyString = Terminal("EMPTY")
