import re
import sys

import ply.lex as lex
import ply.yacc as yacc

from todo_or_not.todo_check import Hit


comment_symbols = {
    "python": {
        "line_comment": "#",
        "block_comment": r"'''.+'''",
    },
    "java": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "javascript": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "c": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "c++": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "php": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "swift": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "ruby": {
        "line_comment": "[#]",
        "block_comment": r"=begin.+=end",
    },
    "go": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "rust": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "kotlin": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "csharp": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "typescript": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "scala": {
        "line_comment": "//",
        "block_comment": r"/\*.+\*/",
    },
    "shell": {
        "line_comment": "[#]",
        "block_comment": r": '.+'",
    },
    "pascal": {
        "line_comment": "//",
        "block_comment": r"{.+}",
    },
    "sql": {
        "line_comment": "--",
        "block_comment": r"/\*.+\*/",
    },
}

file_extensions = {
    "py": "python",
    "java": "java",
    "js": "javascript",
    "c": "c",
    "cpp": "c++",
    "hpp": "c++",
    "cc": "c++",
    "cxx": "c++",
    "php": "php",
    "swift": "swift",
    "rb": "ruby",
    "go": "go",
    "rs": "rust",
    "kt": "kotlin",
    "kts": "kotlin",
    "cs": "csharp",
    "ts": "typescript",
    "scala": "scala",
    "sc": "scala",
    "sh": "shell",
    "bash": "shell",
    "pas": "pascal",
    "pp": "pascal",
    "sql": "sql",
}


class TodoGrammar:
    def __init__(self, file_extension: str):
        self.language = file_extensions[file_extension]

        # List of token names.   This is always required
        self.tokens = ("CODE_BEFORE_COMMENT", "COMMENT_UP_TO_KEY", "REST_OF_COMMENT")

        # Regular expression rules for simple tokens
        self.t_CODE_BEFORE_COMMENT = f'^[^{comment_symbols[self.language]["line_comment"]}]*(?=[{comment_symbols[self.language]["line_comment"]}])'
        self.t_COMMENT_UP_TO_KEY = f'[{comment_symbols[self.language]["line_comment"]}].*([tT][oO][dD][oO]|[fF][iI][xX][mM][eE])'
        self.t_REST_OF_COMMENT = f".+"

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    t_ignore = " \t"

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def _build_lexer(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def p_todo_line_with_code(self, p):
        """todo_line : pre_todo_comment todo_line_comment_body"""
        reconstructed_line = f"{p[1]}{p[2]['body']}"
        p[0] = Hit("file", 1, p[2]["keywords"], [reconstructed_line], 0)

        if p[2]["labels"] is not None:
            p[0].structured_labels = p[2]["labels"]
        if p[2]["structured_title"] is not None:
            p[0].structured_title = p[2]["structured_title"]
        if p[2]["structured_body"] is not None:
            p[0].structured_body = p[2]["structured_body"]

    def p_pre_todo_comment(self, p):
        """pre_todo_comment : CODE_BEFORE_COMMENT"""
        p[0] = p[1]

    def p_empty_pre_todo_comment(self, p):
        """pre_todo_comment :"""
        p[0] = ""

    def p_todo_line_comment_body(self, p):
        """todo_line_comment_body   : COMMENT_UP_TO_KEY REST_OF_COMMENT
        | COMMENT_UP_TO_KEY"""

        keywords = re.findall(r"(todo|fixme)", p[1].lower())
        body = f"{p[1]} {p[2]}" if len(p) > 2 else p[1]

        _structured = body.split("|", 1)

        structured_title, structured_body = None, None
        if len(_structured) > 1:
            structured_title, structured_body = _structured
            structured_title = structured_title.strip(comment_symbols[self.language]["line_comment"]).strip()
            structured_body = structured_body.strip()

        _body = body if structured_title is None else structured_body
        labels = re.findall(r"(?<=#)(?![tT][oO][dD][oO]|[fF][iI][xX][mM][eE]\b)[^\s]+", _body)
        if len(labels) == 0:
            labels = None

        p[0] = {"keywords": keywords, "body": body, "labels": labels, "structured_title": structured_title, "structured_body": structured_body}

    # Error rule for syntax errors
    def p_error(self, p):
        print("Syntax error in input!")

    # Build the parser
    def build(self, **kwargs):
        self._build_lexer(**kwargs)
        self.parser = yacc.yacc(module=self, **kwargs)


if __name__ == "__main__":
    g = TodoGrammar("py")
    g.build()

    while True:
        try:
            s = input("code > ")
        except EOFError:
            break
        if not s:
            continue
        result = g.parser.parse(s)
        print(result)
