''' Some helper functions for the parser generator '''

from sys import exit

CONTINUE = False     # Used in stop()
CONTINUE_WHEN = 0
breaknum = 1

DEBUG = False

def stop(message = None):
    ''' A make-shift poor mans debugger. Don't use, k?'''
    global breaknum, CONTINUE, CONTINUE_WHEN
    if not DEBUG:
        return
    if message == None:
        message = '\n ({}) BREAK > '.format(breaknum)
    else:
        message = "\n({}) {} >".format(breaknum, message)
    if CONTINUE_WHEN == breaknum:
        CONTINUE = False
    if not CONTINUE:
        c = raw_input(message)
        if c.lower()  in ('c', 'continue'):
            CONTINUE = True
        elif c.lower() in ('q', 'quit', 'e'):
            print "EXITING"
            exit()
        elif c.lower().startswith("bp"):
            try:
                CONTINUE_WHEN = int(c[2:].strip())
                CONTINUE = True
            except:
                print "Invalid Break Point: {}".format(c)

    breaknum += 1

def print_banner(message, filler = '=', padding = 1, width = 60, word_padding = '   '):
    message = word_padding + message + word_padding
    for i in range(padding):
        print
    print '{0: ^80}'.format(filler * width)
    print '{0: ^80}'.format( ('{0:' + filler + '^{1}}').format(message, width))
    print '{0: ^80}'.format(filler * width)
    for i in range(padding):
        print

def accumulator(start_value = 0):
    ''' accumulator returns a generator that generates numbers, starting with
    it's input value. '''
    i = start_value - 1
    while True:
        i += 1
        yield i
