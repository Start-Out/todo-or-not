# Yacc example

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from lex import tokens
from todo_or_not.todo_check import Hit


def p_todo_line_with_code(p):
    "todo_line : PRE_LINE_COMMENT todo_line_comment_body"
    reconstructed_line = f"{p[1]} {p[2]["body"]}"
    p[0] = Hit("file", 1, [p[2]["keyword"]], [reconstructed_line], 0)


def p_todo_line_comment_body(p):
    "todo_line_comment_body : TODO_FLAG ELSE"
    p[0] = {"keyword": p[1].lower(), "body": f"{p[1]}{p[2]}"}


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")


# Build the parser
parser = yacc.yacc()

while True:
    try:
        s = input("calc > ")
    except EOFError:
        break
    if not s:
        continue
    result = parser.parse(s)
    print(result)
