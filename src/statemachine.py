''' statemachine.py: Represents the LR(1) state machine. Generated from output
of MetaParser. '''
from src.metaparser import MetaParser
from src.helper import accumulator
from src.symbols import ( Symbol, Terminal, NonTerminal, Production,
                          Productions, startSymbol, terminalEOF)
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
        # print "KERNEL: ", self.kernel
        while True:
            updated = False
            # print
            # print
            # print "CLOSURE:", closure
            new_closure = set(closure)

            for item in closure:
                p, n, f = item.production, item.position, item.follows
            
                if n >= len(p.rhs):      # Production of form A -> alpha beta (*)
                    continue
                next_symbol = p.rhs[n]
                # print "NEXT SYMBOL:", next_symbol, type(next_symbol)
                # print "PRODUCTIONS:", self.productions
                if isinstance(next_symbol, NonTerminal):
                    # Get collection of productions starting with next_symbol
                    prods = self.productions.get_productions_for(next_symbol)
                    prods = set([Item(x, 0, self.productions) for x in prods])
                    # print "PRODS : ", prods
                    # print "NEW CL: ", new_closure
                    # print "PRODS C NEW CLOSURE:", prods.issubset(new_closure)
                    if not prods.issubset(new_closure):
                        updated = True
                        new_closure.update(prods)
                # print "UPDATED    :", updated
                # print "CLOSURE    :", closure
                # print "NEW CLOSURE:", new_closure
                # print "NEW CLOSURE == CLOSURE: ", new_closure == closure
                # print 
                        
            closure = new_closure

            if not updated:
                break
        self.items = frozenset(list(closure))

    def __eq__(self, other):
        return self.items == other.items

    def __ne__(self, other):
        return not self == other
    
    def __hash__(self):
        return hash(self.items)

    def __repr__(self):
        s = "State {}\n    ".format(self.state_num)
        s += '\n    '.join([str(i) for i in self.items])
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
        self.follows.append(f)

    def add_follows(self, follows):
        for f in follows:
            self.follows.append(f)

    def shift(self):
        ''' Returns a copy of Item, shifted by 1 if valid, None otherwise.'''
        if self.position < len(self.production.rhs):
            return Item(self.production, self.position + 1, self.productions)
        return None

    def __eq__(self, other):
        return self.production == other.production and self.position == other.position

    def __hash__(self):
        return hash((self.production, self.position))

    def __repr__(self):
        return "Item({},{},{})".format(self.production.num, self.production, self.position)


class StateMachine(object):
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
        print "GENERATING STATES"
        I0 = Item(self.start, 0, self.productions)
        I0.add_follow(terminalEOF)

        S0 = State([I0])
        print "S0 State Num:", S0.state_num
        self.states.append(S0)
        self.number_of_states += 1
        self.gen_state(S0)

        print "STATE MACHINE:"
        for s in self.states:
            print s
        print
        print "GOTO TABLE"
        for key in self.goto.keys():
            print 
            print key[0]
            print key[1]
            print "-->", self.goto[key]
            print 

    def gen_state(self, state):
        print "    GEN STATE:", self.number_of_states
        transfer_state_map = {} # Set of symbols to transfer on

        # Get symbols to transfer on, and corresponding production numbers
        for i in state.items:
            print "CONSIDERING ITEM {}".format(i)
            if i.to_transfer() not in transfer_state_map:
                transfer_state_map[i.to_transfer()] = []
            transfer_state_map[i.to_transfer()].append(i.shift())

        # transfer_state_map associates symbols w/ items that have already been
        # 'shifted'. We use this to construct the goto table

        print "TRANSFER_STATE_MAP: ",transfer_state_map

        print "KEYS: ", transfer_state_map.keys()
        for symbol in transfer_state_map.keys():
            
            print "SYMBOL:", symbol
            if symbol is None:
                continue
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
        



