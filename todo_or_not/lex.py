import ply.lex as lex

# List of token names.   This is always required
tokens = ("CODE_BEFORE_COMMENT", "COMMENT_UP_TO_KEY", "REST_OF_COMMENT")

# Regular expression rules for simple tokens
t_CODE_BEFORE_COMMENT = r"^[^#]*(?=[#])"
t_COMMENT_UP_TO_KEY = r"[#].*([tT][oO][dD][oO]|[fF][iI][xX][mM][eE])"
t_REST_OF_COMMENT = r".+"


# Define a rule so we can track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


t_ignore = " \t"


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()
