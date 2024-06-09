# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

# List of token names.   This is always required
tokens = (
    'LINE_COMMENT_CHAR',
    'TODO_FLAG',
    'TODO_TITLE',
    'LABEL',
    'ANY',
    'NONE'
)

# Regular expression rules for simple tokens
t_LINE_COMMENT_CHAR = r'[#].+'
t_TODO_FLAG = r'[tT][oO][dD][oO]|[fF][iI][xX][mM][eE]'
t_TODO_TITLE = r'\<.*\>'
t_LABEL = r'[#]\w+'
t_ANY = r'.*'
t_NONE = r''

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()