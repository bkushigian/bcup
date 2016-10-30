''' Some helper functions for the parser generator '''


def accumulator(start_value = 0):
  i = start_value - 1
  while True:
    i += 1
    yield i
