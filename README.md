# bcup
An LR(1) Parser Generator written in Python

*bcup:* Supporting your grammars since a couple weeks ago

## Running Tests
There is some cool stuff in here. To run, go to root dir of project and enter
`python test/ahoparser.py` or `python test/ahoparser2.py`. Both of these have
hand-built parsers using the auto-generated state machines. There are other
`.py` files in there that may or may not work (depending on any refactoring I do
and whether or not I had a chance to fix errors)

## TODO
1. Create a lexer generator
    * It would be nice to use built-in `re` module for Python BUT would want
      to build something like a DFA, rather than a:

            if num_regex.match(term):
                return NumToken()
            elif str_regex.match(term)
                return StrToken()
                ...
      scheme, since this would have poor performance.

2. Create the actual parser generator. This will involve:
    * Figuring out a system for storing the state machine (maybe to a file,
      maybe write it as a string literal to the parser file)

3. Develop a unit testing suite to automate tests.

4. LR Parser

5. Work on building parse trees
