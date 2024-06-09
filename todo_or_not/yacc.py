# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lex import tokens
from todo_or_not.todo_check import Hit

def p_todo_line(p):
    'todo_line : LINE_COMMENT_CHAR TODO_FLAG ELSE'
    p[0] = Hit("file", 1, [p[2].lower()], [p[2]], 0)

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

while True:
   try:
       s = input('calc > ')
   except EOFError:
       break
   if not s: continue
   result = parser.parse(s)
   print(result)