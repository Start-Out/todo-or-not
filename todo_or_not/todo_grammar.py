import re
import sys

import ply.lex as lex
import ply.yacc as yacc

from todo_or_not.todo_hit import Hit

C_LIKE = {"line_comment": "//", "block_comment": {"start": r"/\*", "end": r"\*/"}}

comment_symbols = {
    "python": {"line_comment": "#", "block_comment": {"start": "'''", "end": "'''"}},
    "java": C_LIKE,
    "javascript": C_LIKE,
    "c": C_LIKE,
    "c++": C_LIKE,
    "php": C_LIKE,
    "swift": C_LIKE,
    "ruby": {
        "line_comment": "[#]",
        "block_comment": {"start": "=begin", "end": "=end"},
    },
    "go": C_LIKE,
    "rust": C_LIKE,
    "kotlin": C_LIKE,
    "csharp": C_LIKE,
    "typescript": C_LIKE,
    "scala": C_LIKE,
    "shell": {"line_comment": "[#]", "block_comment": {"start": ": '", "end": "'"}},
    "pascal": {"line_comment": "//", "block_comment": {"start": "{", "end": "}"}},
    "sql": {"line_comment": "--", "block_comment": {"start": "/*", "end": "*/"}},
    "x_default": C_LIKE,
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


def find_language(file_extension: str):
    try:
        return file_extensions[file_extension]
    except KeyError:
        return "x_default"


class TodoGrammar:
    def __init__(self, file_extension: str):
        self.language = find_language(file_extension)

        # List of token names. This is always required
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
            structured_title = structured_title.strip(
                comment_symbols[self.language]["line_comment"]
            ).strip()
            structured_body = structured_body.strip()

        _body = body if structured_title is None else structured_body
        labels = re.findall(
            r"(?<=#)(?![tT][oO][dD][oO]|[fF][iI][xX][mM][eE]\b)[^\s]+", _body
        )
        if len(labels) == 0:
            unique_labels = None
        else:
            unique_labels = list(set(labels))

        unique_keywords = list(set(keywords))

        p[0] = {
            "keywords": unique_keywords,
            "body": body,
            "labels": unique_labels,
            "structured_title": structured_title,
            "structured_body": structured_body,
        }

    # Error rule for syntax errors
    def p_error(self, p):
        raise SyntaxError(
            f"\n== Invalid syntax: \n-- [parser state] {self.parser.state} \n-- [stack state] {self.parser.symstack}"
        )

    # Build the parser
    def build(self, **kwargs):
        self._build_lexer(**kwargs)
        self.parser = yacc.yacc(module=self, **kwargs)

    def safe_parse(self, _input: str):
        try:
            _input = _input.strip()
            tmp = self.parser.parse(_input)
            return tmp
        except SyntaxError:
            return None
