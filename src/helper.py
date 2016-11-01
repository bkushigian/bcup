''' Some helper functions for the parser generator '''

from sys import exit

CONTINUE = False     # Used in stop()
CONTINUE_WHEN = 0
breaknum = 1

DEBUG = False

def stop(message = None):
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

def accumulator(start_value = 0):
  i = start_value - 1
  while True:
    i += 1
    yield i
