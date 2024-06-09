# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lex import tokens

def p_todo_line_comment_with_code(p):
    'p_todo_line_comment_with_code : ANY LINE_COMMENT_CHAR todo_line_comment'
    p[0] = p[1] + p[3]

def p_todo_line_comment(p):
    'todo_line_comment : todo_comment_body TODO_FLAG todo_comment_body'
    p[0] = p[1] - p[3]

def p_todo_comment_body_empty(p):
    'todo_comment_body : NONE'
    p[0] = p[1]

def p_todo_comment_body_with_title(p):
    'todo_comment_body : ANY TODO_TITLE ANY'
    p[0] = p[1] * p[3]

def p_todo_comment_body_any(p):
    'todo_comment_body : ANY'
    p[0] = p[1] * p[3]

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