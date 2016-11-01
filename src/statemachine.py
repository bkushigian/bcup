''' statemachine.py: Represents the LR(1) state machine. Generated from output
of MetaParser. '''
from src.metaparser import MetaParser
from src.helper import accumulator, stop, DEBUG
from src.symbols import ( Symbol, Terminal, NonTerminal, Production,
                          Productions, startSymbol, terminalEOF, emptyString)
from sys import exit

class Action(object):
    pass

class ActionShift(Action):
    def __init__(self, state):
        self.state = state
    def __eq__(self, other):
        return self.state == other.state
    def __hash__(self):
        return hash(state)

class ActionReduce(Action):
    def __init__(self, production):
        self.production = production

    def __eq__(self, other):
        return self.production == other.production

    def __hash__(self):
        return hash(production)

class ActionAccept(Action):
    def __init__(self):
        print "ACCEPT"
        # TODO: What should this do?


class ActionError(Action):
    def __init__(self, message=''):
        print "ERROR!", message
        # TODO: Make better, get rid of hard exit
        exit() 

class State(object):
    accum = accumulator()
    def __init__(self, items, state_num = None):
        assert len(items), "items must have positive length"
        self.kernel = set(items)  # Should be a set of items
        self.productions = items[0].productions
        self.closure()
        if state_num == None:
            state_num = self.accum.next()
        self.state_num = state_num

        
    def set_num(self):
        if self.state_num and self.state_num < 0:
            self.state_num = self.accum.next()

    def closure(self):
        closure = set()
        closure.update(self.kernel)
        if DEBUG:
            print "="*80
            print "CLOSURE()"
            print "KERNEL: ", self.kernel
            print "="*80
        while True:
            if DEBUG:
                print "="*80
            updated = False
            new_closure = set(closure)

            for item in closure:
                p, n, f = item.production, item.position, item.follows
                if DEBUG:
                    print (' ' * 5) +  ('-'*70 ) + (' ' * 5)
                    print 
                    print "p = {}, n = {}, f = {}".format(p,n,f)
                if n >= len(p.rhs):
                    continue
                next_symbol = p.rhs[n]
                if DEBUG:
                    print 
                    print "NEXT SYMBOL:", next_symbol, type(next_symbol)
                    print "PRODUCTIONS:\n", self.productions
                    print 

                if not isinstance(next_symbol, NonTerminal):
                    if DEBUG:
                        print "    CONINUING..."
                    continue
                for prod in self.productions.get_productions_for(next_symbol):
                    if DEBUG:
                        print "    PROD   :", prod
                    for a in f:
                        if DEBUG:
                            print "        a       :", a
                            print "        FIRST(a):", a.firsts
                        new_item = Item(prod, 0, self.productions)
                        inp = list(p.rhs[n+1:]) + [a]
                        fos = self.productions.firsts_of_string(list(p.rhs[n+1:]) + [a])
                        if DEBUG:
                            print "        FRST STR:", fos
                        for b in self.productions.firsts_of_string(list(p.rhs[n+1:]) + [a]):
                            if DEBUG:
                                print "            b       :", b
                            new_item.add_follow(b)
                        if DEBUG:
                            print "        NEW ITEM:", new_item
                        if new_item not in new_closure:
                            if DEBUG:
                                print "        ADD ITEM:", new_item
                            updated = True
                            new_closure.add(new_item)
                if DEBUG:
                    print "UPDATED    :", updated
                    print "CLOSURE    :", closure
                    print "NEW CLOSURE:", new_closure
                    print "NEW CLOSURE == CLOSURE: ", new_closure == closure
                    print 
                    stop()
            closure = new_closure
            if not updated:
                break
        self.items = frozenset(list(closure))

    def print_details(self):
        s = "State {}\n    ".format(self.state_num)
        s += '\n    '.join([str(i) for i in self.items])
        print s


    def __eq__(self, other):
        return self.items == other.items

    def __ne__(self, other):
        return not self == other
    
    def __hash__(self):
        return hash(self.items)

    def __repr__(self):
        s = "State({})".format(self.state_num)
        return s

class Item(object):
    ''' An item is defined to be a production with a position '''
    def __init__(self, production, position, productions):
        assert isinstance(production, Production), "{} not Production".format(production)
        assert isinstance(position, int)
        self.production  = production
        self.position    = position
        self.productions = productions
        self.follows     = []

    def to_transfer(self):
        if self.position >= len(self.production.rhs):   
            return None
        return self.production.rhs[self.position]
    
    def add_follow(self, follow):
        self.follows.append(follow)

    def add_follows(self, follows):
        for f in follows:
            self.follows.append(f)

    def shift(self):
        ''' Returns a copy of Item, shifted by 1 if valid, None otherwise.'''
        if self.position < len(self.production.rhs):
            i = Item(self.production, self.position + 1, self.productions)
            i.follows = self.follows
            return i
        return None

    def __eq__(self, other):
        return self.production == other.production and self.position == other.position and self.follows == other.follows

    def __hash__(self):
        return hash((self.production, self.position, tuple(self.follows) ))

    def __repr__(self):
        rhs = list(self.production.rhs)
        left_strs = [str(t) for t in rhs[:self.position]]
        right_strs = [str(t) for t in rhs[self.position:]]
        s = ' '.join(left_strs + ['(*)'] + right_strs)
        return "Item({}: {} ==> {}, {})".format(self.production.num,
                            self.production.lhs,s, self.follows)


class StateMachine(object):
    pass

class LRStateMachine(StateMachine):
    def __init__(self, terminals, nonterminals, productions):
        self.terminals    = terminals     # Set of terminals
        self.nonterminals = nonterminals  # Set of nonterminals
        self.symbols      = terminals + nonterminals
        self.productions  = productions   # Productions() instance
        # The Start Production
        self.start        = productions.productions[0]
        self.states       = []
        self.state_set    = set()
        
        self.goto         = {}   # keys of form (State, Symbol)
        self.action       = {}   # keys of form (State, Terminal)
        self.number_of_states = 0

    def generate_states(self):
        if DEBUG:
            print "GENERATING STATES"
        I0 = Item(self.start, 0, self.productions)
        I0.add_follow(terminalEOF)

        S0 = State([I0])
        if DEBUG:
            print "S0 State Num:", S0.state_num
        self.states.append(S0)
        self.number_of_states += 1
        self.gen_state(S0)

        if DEBUG:
            print "STATE MACHINE:"
        for s in self.states:
            s.print_details()
        if DEBUG:
            print
            print "GOTO TABLE"
            for key in self.goto.keys():
                print (key[0], key[1]) ,"-->", self.goto[key]

    def gen_state(self, state):
        if DEBUG:
            print "    GEN STATE:", self.number_of_states
            stop()
        transfer_state_map = {} # Set of symbols to transfer on

        # Get symbols to transfer on, and corresponding production numbers
        for i in state.items:
            if DEBUG:
                print "CONSIDERING ITEM {}".format(i)
            if i.to_transfer() not in transfer_state_map:
                transfer_state_map[i.to_transfer()] = []
            transfer_state_map[i.to_transfer()].append(i.shift())

        # transfer_state_map associates symbols w/ items that have already been
        # 'shifted'. We use this to construct the goto table

        if DEBUG:
            print "TRANSFER_STATE_MAP: ",transfer_state_map
            print "KEYS: ", transfer_state_map.keys()
        for symbol in transfer_state_map.keys():
            if DEBUG:
                print "SYMBOL:", symbol
            if symbol is None:
                continue
            if DEBUG:
                stop('CREATING NEW STATE > ')
            s = State(transfer_state_map[symbol], -1) # Create a new state
            if s not in self.state_set:
                self.number_of_states += 1
                s.set_num()             # This is a keeper, so set state_num
                self.state_set.add(s)   # Keep track of s
                self.states.append(s)   # ...
                if (state, symbol) in self.goto:
                    print "    ERROR! ({}, {}) already in goto table".format(
                                        state,symbol)
                self.goto[(state, symbol)] = s
                self.gen_state(s)


    def __repr__(self):
        s = "StateMachine\n"
        for state in self.states:
            s += str(state) + '\n'
        return s
        
class LLStateMachine(StateMachine):
    def __init__(self, metaparser):
        self.mp           = metaparser
        self.terminals    = self.mp.terminals.values()     # Set of terminals
        self.nonterminals = self.mp.nonterminals.values()  # Set of nonterminals
        self.productions  = self.mp.productions   # Productions() instance
        self.symbols      = self.terminals + self.nonterminals

        # The Start Production
        self.start        = self.productions.productions[0]
        self.states       = []
        self.state_set    = set()
        
        self.table        = {}
        self.number_of_states = 0

        self._generate_table()

    def _add_to_table(self, A, a, prod):
        assert isinstance(A, NonTerminal), "A = {} must be a nonterminal".format(A)
        assert isinstance(a, Terminal), "a = {} must be a terminal".format(a)
        assert isinstance(prod, Production), "prod = {} must be a production".format(prod)

        if (A, a) not in self.table:
            self.table[(A,a)] = []

        if prod not in self.table[(A,a)]:
            self.table[(A,a)].append(prod)

    def _generate_table(self):
        ''' 
        Algorithm from Aho:
        For each production A -> alpha of grammar:
            1 For each terminal a in First(alpha): 
                1a add A -> alpha to M[A,a]
            2 If emptyString in First(alpha), then 
                2a For each terminal b in Follow(A), 
                    2ai add A -> alpha to M[A,b]. 
                
                2b If empty string in First(alpha) and '$' is in Follow(A):
                    2bi add A -> alpha to M[A,$]
        ''' 

        prods = self.productions.productions
        table = self.table

        for p in prods:
            if DEBUG:
                print
                print "    CURRENT_PRODUCTON: {}".format(p)
            alpha = list(p.rhs)
            A     = p.lhs

            alpha_firsts = self.productions.firsts_of_string(alpha)

            for a in alpha_firsts:         # 1
                if a.is_terminal() and a != emptyString:        # 1a
                    self._add_to_table(A, a, p) # Add (A,a) -> p to table
                    if DEBUG:
                        print "    ADDED1 {}, {}: {}".format(A,a,p)

            if emptyString in alpha_firsts:
                if DEBUG:
                    print "    FOLLOWS{}:".format(A), A.follows
                for b in A.follows:
                    if DEBUG:
                        print "    b:", b
                    if b.is_terminal() and b != emptyString:
                        self._add_to_table(A, b, p)
                        if DEBUG:
                            print "    ADDED2 {}, {}: {}".format(A,b,p)
                if terminalEOF in A.follows:
                    self._add_to_table(A, terminalEOF, p)
                    if DEBUG:
                        print "    ADDED3 {}, {}: {}".format(A,terminalEOF,p)
        if DEBUG:
            print 
            print " === LL GENERATE TABLE ==="
        entry_num = 0
        for k in self.table.keys():
            entry_num += 1
            if DEBUG:
                print "TABLE ENTRY: {}".format(entry_num), 
                print "    M[{},{}]:".format(k[0], k[1])
                for entry in self.table[k]:
                    print "        {}".format(entry)
        if DEBUG:
            stop("GEN TABLES")

    def print_table(self):
        ''' Print the transition table '''
        # TODO: This could use some refinement
        terms, nonterms = list(self.terminals), list(self.nonterminals)
        table = self.table

        def f(a, width=12):
            s = '{0: ^{1}}|'
            if isinstance(a, int):
                a += 1
            return s.format(str(a),width)

        def seperate(width = 12):
            s = ((('-' * (width+1)) + '+') * len(terms)) + ('-' * (width) + '+')
            print s

        def get(a,b):
            if (a,b) in table:
                p = table[(a,b)][0]
                if p.num == None:
                    print
                    print "p.num = None, p =", p
                    print
                return f(p.num)
            return f('')
        print
        print '=' * 80
        print '{0:=^80}'.format("   LLStateMachine Table   ")
        print '=' * 80
        print 
        # Print Terminals
        seperate()
        print f(' '),
        for t in terms:
            print f(t),
        print
        seperate()

        for n in nonterms:
            print f(n),
            for t in terms:
                print get(n,t),
            print
            seperate()

        
