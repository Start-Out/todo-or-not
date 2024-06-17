import unittest
from todo_or_not.todo_grammar import TodoGrammar
from todo_or_not.todo_check import Hit


class TestTodoGrammarPython(unittest.TestCase):
    def setUp(self):
        self.grammar = TodoGrammar("py")
        self.grammar.build()

    def test_simple_line_comment(self):
        code = "########################################################\n"
        result = self.grammar.safe_parse(code)
        assert result is None

        code = "#todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "#fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "#fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_line_comment_with_leading_comment(self):
        code = "# a todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "# a fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "# a fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_line_comment_with_trailing_comment(self):
        code = "# todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "# fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "# fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_line_comment_with_leading_and_trailing_comment(self):
        code = "# a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "# a fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "# a fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_simple_line_comment(self):
        code = "123 #todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 #fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 #fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_line_comment_with_leading_comment(self):
        code = "123 # a todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 # a fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 # a fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "    return c / 0  # FIXME I just don't know why this doesn't work!"
        expected_hit = Hit("file", 1, ["fixme"], [code.strip()], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_line_comment_with_trailing_comment(self):
        code = "123 # todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 # fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 # fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_line_comment_with_leading_and_trailing_comment(self):
        code = "123 # a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 # a fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 # a fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_complex_comment_with_labels(self):  # TODO that
        code = "123 # a todo z #bug"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_labels = ["bug"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 # #$@1aF_98 a fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        expected_hit.structured_labels = ["$@1aF_98"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 # a fixme z todo #alpha bravo #charlie_delta # echo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        expected_hit.structured_labels = ["alpha", "charlie_delta"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_structured_comments(self):
        code = "123 # Title | a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_title = "Title"
        expected_hit.structured_body = "a todo z"
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 #Title | a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_title = "Title"
        expected_hit.structured_body = "a todo z"
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 #Title | a todo z #label"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_title = "Title"
        expected_hit.structured_body = "a todo z #label"
        expected_hit.structured_labels = ["label"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_structured_comment_with_no_code(self):
        code = "    # TODO Closed Issues are helpful! | This issue is closed, but the TODO string is still in the codebase!"
        expected_hit = Hit("file", 1, ["todo"], [code.strip()], 0)
        expected_hit.structured_title = "TODO Closed Issues are helpful!"
        expected_hit.structured_body = "This issue is closed, but the TODO string is still in the codebase!"
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

class TestTodoGrammarC(unittest.TestCase):
    def setUp(self):
        self.grammar = TodoGrammar("cpp")
        self.grammar.build()

    def test_simple_line_comment(self):
        code = "//todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "//fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "//fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_line_comment_with_leading_comment(self):
        code = "// a todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// a fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// a fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_line_comment_with_trailing_comment(self):
        code = "// todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_line_comment_with_leading_and_trailing_comment(self):
        code = "// a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// a fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// a fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_simple_line_comment(self):
        code = "123 //todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 //fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 //fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_line_comment_with_leading_comment(self):
        code = "123 // a todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // a fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // a fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_line_comment_with_trailing_comment(self):
        code = "123 // todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_line_comment_with_leading_and_trailing_comment(self):
        code = "123 // a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // a fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // a fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_complex_comment_with_labels(self):
        code = "123 // a todo z #bug"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_labels = ["bug"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // #$@1aF_98 a fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        expected_hit.structured_labels = ["$@1aF_98"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // a fixme z todo #alpha bravo #charlie_delta # echo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        expected_hit.structured_labels = ["alpha", "charlie_delta"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_structured_comments(self):
        code = "123 // Title | a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_title = "Title"
        expected_hit.structured_body = "a todo z"
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 //Title | a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_title = "Title"
        expected_hit.structured_body = "a todo z"
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 //Title | a todo z #label"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_title = "Title"
        expected_hit.structured_body = "a todo z #label"
        expected_hit.structured_labels = ["label"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result


class TestTodoGrammarUndefinedLanguage(unittest.TestCase):
    def setUp(self):
        self.grammar = TodoGrammar("invalid_file_extension")
        self.grammar.build()

    def test_simple_line_comment(self):
        code = "//todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "//fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "//fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_line_comment_with_leading_comment(self):
        code = "// a todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// a fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// a fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_line_comment_with_trailing_comment(self):
        code = "// todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_line_comment_with_leading_and_trailing_comment(self):
        code = "// a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// a fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "// a fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_simple_line_comment(self):
        code = "123 //todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 //fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 //fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_line_comment_with_leading_comment(self):
        code = "123 // a todo"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // a fixme"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // a fixme todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_line_comment_with_trailing_comment(self):
        code = "123 // todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_leading_code_line_comment_with_leading_and_trailing_comment(self):
        code = "123 // a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // a fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // a fixme z todo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_complex_comment_with_labels(self):
        code = "123 // a todo z #bug"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_labels = ["bug"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // #$@1aF_98 a fixme z"
        expected_hit = Hit("file", 1, ["fixme"], [code], 0)
        expected_hit.structured_labels = ["$@1aF_98"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 // a fixme z todo #alpha bravo #charlie_delta # echo"
        expected_hit = Hit("file", 1, ["fixme", "todo"], [code], 0)
        expected_hit.structured_labels = ["alpha", "charlie_delta"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

    def test_structured_comments(self):
        code = "123 // Title | a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_title = "Title"
        expected_hit.structured_body = "a todo z"
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 //Title | a todo z"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_title = "Title"
        expected_hit.structured_body = "a todo z"
        result = self.grammar.safe_parse(code)
        assert expected_hit == result

        code = "123 //Title | a todo z #label"
        expected_hit = Hit("file", 1, ["todo"], [code], 0)
        expected_hit.structured_title = "Title"
        expected_hit.structured_body = "a todo z #label"
        expected_hit.structured_labels = ["label"]
        result = self.grammar.safe_parse(code)
        assert expected_hit == result
