import ply.lex as lex

import re
import sys

from pygments import lexer

comment_symbols = {
    "python": {
        "line_comment": re.compile(r"#.+"),
        # "block_comment": {"start": re.compile(r"'''"), "end": re.compile(r"'''")},
        "block_comment": re.compile(r"'''.+'''"),
    },
    "java": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "javascript": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "c": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "c++": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "php": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "swift": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "ruby": {
        "line_comment": re.compile(r"#.+"),
        "block_comment": {"start": re.compile(r"=begin"), "end": re.compile(r"=end")},
    },
    "go": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "rust": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "kotlin": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "csharp": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "typescript": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "scala": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
    },
    "shell": {
        "line_comment": re.compile(r"#.+"),
        "block_comment": {"start": re.compile(r": '"), "end": re.compile(r"'")},
    },
    "pascal": {
        "line_comment": re.compile(r"//.+"),
        "block_comment": {"start": re.compile(r"{"), "end": re.compile(r"}")},
    },
    "sql": {
        "line_comment": re.compile(r"--.+"),
        "block_comment": {"start": re.compile(r"/\*"), "end": re.compile(r"\*/")},
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

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python your_script.py <file extension> <input>")
        exit(1)

    extension = sys.argv[1]
    user_input = " ".join(sys.argv[2:])

    language = file_extensions[f".{extension}"]
    symbol_set = comment_symbols[language]

    tokens = (
        "COMMENT_TITLE",
        "LINE_COMMENT_BODY",
        "BLOCK_COMMENT_CHAR_START",
        "BLOCK_COMMENT_CHAR_END",
        "BLOCK_COMMENT_BODY",
        "BLOCK_COMMENT_TITLE",
        "LABEL",
        "CODE",
    )

    t_COMMENT_TITLE = r"\<.*\>"
    t_LINE_COMMENT_BODY = symbol_set["line_comment"]
    t_BLOCK_COMMENT_CHAR_START = symbol_set["block_comment"]["start"]
    t_BLOCK_COMMENT_CHAR_END = symbol_set["block_comment"]["end"]
    t_BLOCK_COMMENT_BODY = r"BLOCK_COMMENT_BODY"
    t_BLOCK_COMMENT_TITLE = r"BLOCK_COMMENT_TITLE"
    t_LABEL = r"#\w+"
    t_CODE = r"CODE"

    lexer = lex.lex()
    lexer.input(user_input)

    code = '''
if __name__ == "__main__":
if len(sys.argv) < 3:
    print("Usage: python your_script.py <file extension> <input>")
    exit(1)  # this is a comment with a #label
    '''
