import ply.lex as lex

# Lexer definition
tokens = (
    "PRINTLN",
    "CONST",
    "FN",
    "COLON",
    "STRING",
    "SYMBOL",
    "EQUALS",
    "LPAREN",
    "RPAREN",
    "NUMBER",
    "LBRACE",
    "RBRACE",
    "COMMENT"
)

t_ignore = " \t"


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)
    exit(1)

def t_COMMENT(t):
    r'//[^\n]*'
    pass  # Ignore comments

# Track line numbers in tokens
def t_PRINTLN(t):
    r"print"
    t.lineno = t.lexer.lineno
    return t


def t_CONST(t):
    r"const"
    t.lineno = t.lexer.lineno
    return t

def t_FN(t):
    r"fn"
    t.lineno = t.lexer.lineno
    return t


def t_COLON(t):
    r":"
    t.lineno = t.lexer.lineno
    return t


def t_LPAREN(t):
    r"\("
    t.lineno = t.lexer.lineno
    return t


def t_RPAREN(t):
    r"\)"
    t.lineno = t.lexer.lineno
    return t

def t_LBRACE(t):
    r"\{"
    t.lineno = t.lexer.lineno
    return t


def t_RBRACE(t):
    r"\}"
    t.lineno = t.lexer.lineno
    return t


def t_EQUALS(t):
    r"="
    t.lineno = t.lexer.lineno
    return t


def t_STRING(t):
    r"\".*?\" "
    t.lineno = t.lexer.lineno
    return t


def t_SYMBOL(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.lineno = t.lexer.lineno
    return t


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    t.lineno = t.lexer.lineno
    return t
