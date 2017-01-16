""" 
Defines some useful color printing, plus allows for more tweaking if
desired
"""

indent = 0
indent_str = '    '

COLORS = ['WHITE', 'BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'PURPLE', 'AQUA', 'GREY']
FONT_S = ["BOLD", "LIGHT", "ULINE", "INVERT", "INVISIBLE", "STRIKE"]
SUFFIX = '_DARK'
STARTSTR = "\033["
ENDSTR = "\033[0m"
STATE_OPEN = False

FONTS =         [NONE, 
                BOLD, 
                LIGHT, 
                Q1, 
                ULINE, 
                Q2, 
                Q3, 
                INVERT,
                INVISIBLE, 
                STRIKE] = [str(i) for i in range(10)]

FOREGROUNDS = [FG_WHITE_DARK, 
              FG_BLACK_DARK, 
              FG_RED_DARK, 
              FG_GREEN_DARK, 
              FG_YELLOW_DARK, 
              FG_BLUE_DARK, 
              FG_PURPLE_DARK, 
              FG_AQUA_DARK,
              FG_GREY_DARK,
              FG_WHITE_LIGHT, 
              FG_BLACK_LIGHT, 
              FG_RED_LIGHT, 
              FG_GREEN_LIGHT, 
              FG_YELLOW_LIGHT, 
              FG_BLUE_LIGHT, 
              FG_PURPLE_LIGHT, 
              FG_AQUA_LIGHT,
              FG_GREY_LIGHT] = [str(i) for i in (range(29,38) + range(89,98))]

### Shortcuts 
[WHITE, BLACK, RED, GREEN, YELLOW, BLUE, PURPLE, AQUA, GREY] = ['WHITE', 
                    'BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'PURPLE',
                    'AQUA', 'GREY']

BACKGROUNDS = [BG_WHITE_DARK, 
              BG_BLACK_DARK, 
              BG_RED_DARK, 
              BG_GREEN_DARK, 
              BG_YELLOW_DARK, 
              BG_BLUE_DARK, 
              BG_PURPLE_DARK, 
              BG_AQUA_DARK,
              BG_GREY_DARK,
              BG_WHITE_LIGHT, 
              BG_BLACK_LIGHT, 
              BG_RED_LIGHT, 
              BG_GREEN_LIGHT, 
              BG_YELLOW_LIGHT, 
              BG_BLUE_LIGHT, 
              BG_PURPLE_LIGHT, 
              BG_AQUA_LIGHT,
              BG_GREY_LIGHT] = [str(i) for i in (range(39,48) + range(99,108))]

STR_MAP = {}
for color in COLORS:
    STR_MAP[color] = globals()["FG_{}{}".format(color, SUFFIX)]
    for pre in ("FG_", "BG_"):
        for suf in ("_LIGHT", "_DARK"):
            s = pre + color + suf
            STR_MAP[s] = globals()[s]
for font in FONT_S:
    STR_MAP[font] = globals()[font]

# STATE
FG = FG_WHITE_DARK
BG = BG_WHITE_DARK
FONT = []

# INDENT
def get_indent():
    global indent
    return (indent * indent_str)

def inc_indent(n = 1):
    global indent
    indent += n

def dec_indent(n = 1):
    global indent
    indent -= n
    if indent < 0:
        indent = 0

def set_indent(n):
    global indent
    if n >= 0:
        indent = n

def parse_attrs(attrs):
    res = []
    if not hasattr(attrs, '__iter__'):
        attrs = [attrs]
    for a in attrs:
        a = a.upper()
        if a in STR_MAP:
            res.append(STR_MAP[a])
        else:
            res.append(a)
    return res
            

def prefix(attrs):
    attrs = parse_attrs(attrs)
    return  STARTSTR + ";".join(attrs) + "m"

def suffix(attrs):
    return ENDSTR

def state_str():
    l = list(FONT)
    for attr in [FG, BG]:
        if attr:
            l.append(attr)
    l = list(set(l))
    return "\033[" + ';'.join(l) + "m"

def open_state():
    global STATE_OPEN
    if not STATE_OPEN:
        print state_str(),
        STATE_OPEN = True

def close_state():
    global STATE_OPEN
    if STATE_OPEN:
        print ENDSTR,
        STATE_OPEN = False

def echo(s, attrs=[]):
    print prefix(attrs) + s + ENDSTR

def echo_lines(s, attrs = []):
    lines = s.split('\n')
    i = get_indent()
    output = (i + '\n').join(lines)
    echo(output, attrs)


def echos(s):
    res = state_str() + s + ENDSTR
    print res

def colorstr(s, cs = []):
    return prefix(cs) + s + suffix()
    

### Getters and Setters
def set_fg(fg, dark=True):
    global FG
    fg = fg.upper()
    shade_str = "LIGHT"
    if dark:
        shade_str = "DARK"
    if fg in COLORS:
        FG = globals()["FG_{}_{}".format(fg, shade_str)]
    elif fg in FOREGROUNDS:
        FG = globals()[fg]
    

def get_fg():
    return FG

def unset_fg():
    global FG
    FG = ""

def set_bg(bg, dark=True):
    global BG
    bg = bg.upper()
    shade_str = "LIGHT"
    if dark:
        shade_str = "DARK"
    if bg in COLORS:
        BG = globals()["BG_{}_{}".format(bg, shade_str)]
    elif bg in BACKGROUNDS:
        BG = globals()[bg]

def get_bg():
    return BG

def unset_bg():
    global BG
    BG = ""

def set_font(f):
    try:
        f = globals()[f]
        if f not in FONT:
            FONT.append(f)
    except:
        pass
    
def unset_font(f=None):
    global FONT
    if not f:
        FONT = []
        return
        
    try:
        f = globals()[f]
        while f in FONT:
            FONT.remove(f)
    except:
        pass
    

def get_fonts():
    return FONT
    
def reset_state():
    unset_font()
    unset_bg()
    unset_fg()

# Heart of program

def error(s, ind = 0, prefix = "[!] "):
    inc_indent(ind)
    echo_lines( "{}{}{}".format(get_indent(), prefix, s), [FG_RED_LIGHT, BOLD])
    dec_indent(ind)

def warn(s, ind = 0, prefix = "[!] "):
    inc_indent(ind)
    echo_lines( "{}{}{}".format(get_indent(), prefix, s), [FG_YELLOW_DARK, BOLD])
    dec_indent(ind)

def info(s,  ind = 0,prefix = "[*] "):
    inc_indent(ind)
    echo_lines( "{}{}{}".format(get_indent(), prefix, s), [FG_BLUE_LIGHT])
    dec_indent(ind)

def attempt(s,  ind = 0, prefix = "[*] "):
    inc_indent(ind)
    echo_lines( "{}{}{}".format(get_indent(), prefix, s), [FG_GREEN_DARK])
    dec_indent(ind)
    
def success(s, ind = 0, prefix = "[+] "):
    inc_indent(ind)
    echo_lines( "{}{}{}".format(get_indent(), prefix, s), [FG_GREEN_LIGHT])
    dec_indent(ind)

def failure(s, ind = 0, prefix = "[-] "):
    inc_indent(ind)
    echo_lines( "{}{}{}".format(get_indent(), prefix, s), [FG_YELLOW_LIGHT])
    dec_indent(ind)

def banner(message, filler = '=', padding = 1, width = 60, word_padding = '   ', attrs = []):
    message = word_padding + message + word_padding
    for i in range(padding):
        print
    echo('{0: ^80}'.format(filler * width ), attrs)
    echo('{0: ^80}'.format( ('{0:' + filler + '^{1}}').format(message, width)), attrs)
    echo('{0: ^80}'.format(filler * width ), attrs)
    for i in range(padding):
        print
