import ply.lex as lex

# Lexer definition
tokens = (
    'PRINTLN',
    'LET',
    'COLON',
    'STRING',
    'SYMBOL',
    'EQUALS',
)

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)
    exit(1)

# Track line numbers in tokens
def t_PRINTLN(t):
    r'println'
    t.lineno = t.lexer.lineno
    return t

def t_LET(t):
    r'let'
    t.lineno = t.lexer.lineno
    return t

def t_COLON(t):
    r':'
    t.lineno = t.lexer.lineno
    return t

def t_EQUALS(t):
    r'='
    t.lineno = t.lexer.lineno
    return t

def t_STRING(t):
    r'\".*?\"'
    t.lineno = t.lexer.lineno
    return t

def t_SYMBOL(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.lineno = t.lexer.lineno
    return t

