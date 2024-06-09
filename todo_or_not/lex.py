import ply.lex as lex

# List of token names.   This is always required
tokens = ("PRE_LINE_COMMENT", "TODO_FLAG", "NOT_FLAG", "ELSE")

# Regular expression rules for simple tokens
t_PRE_LINE_COMMENT = r"^[^#]*(?=[#])"
t_TODO_FLAG = r"[#].*([tT][oO][dD][oO]|[fF][iI][xX][mM][eE])"
t_ELSE = r".+"

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
