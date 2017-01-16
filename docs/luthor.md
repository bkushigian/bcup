# LexerGenerator Documentation

## Lexfile Format
The basic format of a lexfile is as follows:
        
    {% 
    # GLOBAL CONFIGURATION 
    int_pattern     = "\d+"
    str_pattern     = "([\"]|[^\"])+"
    ws_pattern      = "\s"
    tokens_matched  = 0    # A normal python variable
    %}

    # LEX SPECIFICATIONS
    int_pattern 
    {- 
    RESULT = IntToken(MATCHED) 
    tokens_matched += 1
    -}

    str_pattern
    {-
    RESULT = StrToken(MATCHED)
    tokens_matched += 1
    -}

    ws_pattern

    {%  # Program Suffix
    print "Total tokens matched: {}".format(tokens_matched)
    %}

### Global Configuration
This section allows for some global configurations. The user can input global
variables for the lexer, such as sub-patterns for regex matches. An example
would be
    
    {%          # Begin Global Configuration
    int_pattern = "\d+"          # First line of code on NEW LINE
    str_pattern = "[\"]|[^\"]"   # Must start flush left - indentation matters!
    ws_pattern  = "\s"
    %}

Note that since Python is indentation based, any code written must be correctly
formatted. Thus, the code section has to start on a new line, and subsequent
indentation will be passed literally to the generated program.

### Lex Specifications
This is the heart of the lexer generator. The basic syntax is

    REGEX_NAME       {- ASSOCIATED_CODE -}

Both `class_name` and `code` values are optional. For example

    int_pattern      {- RESULT = IntToken(MATCHED) -}
    str_pattern      {- RESULT = StrToken(MATCHED) -}
    ws_pattern       # White space is consumed, not used. No code necessary

Note that all `regex_name` types must start with a lower case letter. If a class
name 
