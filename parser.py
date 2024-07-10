import ply.yacc as yacc

# Define the tokens (this should match the tokens defined in the lexer)
tokens = (
    'PRINTLN',
    'LET',
    'EQUALS',
    'COLON',
    'LPAREN',
    'RPAREN',
    'STRING',
    'SYMBOL',
    'NUMBER',
)

# Grammar rules and handler functions
def p_statements(p):
    '''statements : statement
                  | statements statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_expression_string(p):
    'expression : STRING'
    p[0] = p[1]

def p_expression_symbol(p):
    'expression : SYMBOL'
    p[0] = p[1]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_statement_println(p):
    'statement : PRINTLN LPAREN expression RPAREN'
    print(f'println statement found at line {p.lineno(1)}: {p[3]}')
    p[0] = ('PRINTLN', p[3])

def p_statement_let(p):
    'statement : LET SYMBOL COLON SYMBOL EQUALS expression'
    print(f'let statement found at line {p.lineno(1)}: {p[2]}: {p[4]} = {p[6]}')
    if not p[4] in {'str', 'u8'}:
        print(f"Type error: {p[4]} is not a valid type at line {p.lineno}")
        exit(3)
    print(f'[parser ]let statement found at line {p.lineno(1)}: {p[2]}: {p[4]} = {p[6]}')
    p[0] = ('LET', p[2], p[4], p[6])

def p_error(p):
    if p:
        print(f"Syntax error at line {p.lineno}: {p.value}")
        exit(2)
    else:
        print("Syntax error at EOF")
        exit(2)

# Build the parser
parser = yacc.yacc()

