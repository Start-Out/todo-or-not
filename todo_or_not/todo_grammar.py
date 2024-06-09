import re
import sys

import ply.lex as lex
import ply.yacc as yacc

from todo_or_not.todo_check import Hit


comment_symbols = {
    "python": {
        "line_comment": r"[#].+",
        "block_comment": r"'''.+'''",
    },
    "java": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "javascript": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "c": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "c++": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "php": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "swift": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "ruby": {
        "line_comment": r"[#].+",
        "block_comment": r"=begin.+=end",
    },
    "go": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "rust": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "kotlin": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "csharp": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "typescript": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "scala": {
        "line_comment": r"//.+",
        "block_comment": r"/\*.+\*/",
    },
    "shell": {
        "line_comment": r"[#].+",
        "block_comment": r": '.+'",
    },
    "pascal": {
        "line_comment": r"//.+",
        "block_comment": r"{.+}",
    },
    "sql": {
        "line_comment": r"--.+",
        "block_comment": r"/\*.+\*/",
    },
}

file_extensions = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".c": "c",
    ".cpp": "c++",
    ".hpp": "c++",
    ".cc": "c++",
    ".cxx": "c++",
    ".php": "php",
    ".swift": "swift",
    ".rb": "ruby",
    ".go": "go",
    ".rs": "rust",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".cs": "csharp",
    ".ts": "typescript",
    ".scala": "scala",
    ".sc": "scala",
    ".sh": "shell",
    ".bash": "shell",
    ".pas": "pascal",
    ".pp": "pascal",
    ".sql": "sql",
}

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


def p_todo_line_with_code(p):
    """todo_line : CODE_BEFORE_COMMENT todo_line_comment_body"""
    reconstructed_line = f"{p[1]} {p[2]["body"]}"
    p[0] = Hit("file", 1, p[2]["keywords"], [reconstructed_line], 0)


def p_todo_line_comment_body(p):
    """todo_line_comment_body   : COMMENT_UP_TO_KEY REST_OF_COMMENT
    | COMMENT_UP_TO_KEY"""

    keywords = re.findall(r"(todo|fixme)", p[1].lower())
    body = f"{p[1]} {p[2]}" if len(p) > 2 else p[1]

    p[0] = {"keywords": keywords, "body": body}


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")


# Build the parser
parser = yacc.yacc()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python your_script.py <file extension> <input>")
        exit(1)

    extension = sys.argv[1]
    user_input = " ".join(sys.argv[2:])

    language = file_extensions[f".{extension}"]
    symbol_set = comment_symbols[language]

    tokens = "LINE_COMMENT"

    while True:
        try:
            s = input("code > ")
        except EOFError:
            break
        if not s:
            continue
        result = parser.parse(s)
        print(result)
