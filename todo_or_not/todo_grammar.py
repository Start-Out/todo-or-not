from todo_or_not.todo_check import Hit

import ply.lex as lex

import re
import sys

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

code = '''
if __name__ == "__main__":
if len(sys.argv) < 3:
    print("Usage: python your_script.py <file extension> <input>")
    exit(1)  # this is a comment with a #label
'''

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python your_script.py <file extension> <input>")
        exit(1)

    extension = sys.argv[1]
    user_input = " ".join(sys.argv[2:])

    language = file_extensions[f".{extension}"]
    symbol_set = comment_symbols[language]

    tokens = (
        "LINE_COMMENT"
    )

    r_COMMENT_TITLE = r"\<.*\>"
    # t_LINE_COMMENT_BODY = symbol_set["line_comment"]
    # t_BLOCK_COMMENT_BODY = symbol_set["block_comment"]
    # t_LABEL = r"[#]\w+"
    # t_CODE = r".+"

    def t_COMMENT_BODY(t):
        symbol_set["line_comment"]
        t.lexer.todoon_hits.append(t)

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()
    lexer.todoon_hits = []
    lexer.input(code)

    parsed_tokens = []
    for token in lexer:
        parsed_tokens.append(token)

    pass
