import io
import os
import unittest
import unittest.mock

import todo_or_not.todo_check
import todo_or_not.localize
from todo_or_not.todo_hit import Hit


class TestFindLines(unittest.TestCase):

    def setUp(self):
        self.hit_tests = os.path.join("tests", "resources", "example.py")
        self.unsupported_encoding_test = os.path.join("tests", "resources", "logo.png")
        self.broken_encoding_test = os.path.join(
            "tests", "resources", "broken.donotopen"
        )
        self.really_broken_encoding_test = os.path.join(
            "tests", "resources", "reallybroken.donotopen"
        )

    def test_find_lines(
        self,
    ):
        parsers = {}

        hits, _ = todo_or_not.todo_check.find_hits(
            self.hit_tests, False, "# todoon", parsers
        )

        hits_by_name = {}
        for hit in hits:
            hits_by_name[hit.__repr__()] = hit

        expected_hits_by_name = {}

        todo_in_unfinished_function = Hit(
            self.hit_tests,
            7,
            ["todo"],
            [
                "def an_unfinished_function():\n",
                "    # TODO Finish documenting todo-or-not\n",
                "    print(\"Hello, I'm not quite done, there's more to do!\")\n",
                '    print("Look at all these things I have to do!")\n',
                "    a = 1 + 1\n",
                "    b = a * 2\n",
                '    print("Okay I\'m done!")\n',
            ],
            1,
        )
        expected_hits_by_name[todo_in_unfinished_function.__repr__()] = (
            todo_in_unfinished_function
        )

        fixme_in_broken_function = Hit(
            self.hit_tests,
            23,
            ["fixme"],
            [
                "def a_broken_function():\n",
                "    # This line might not show up in the generated issue because it's too far away\n",
                "    #  from the line that triggered the issue.\n",
                "    # The search for pertinent lines will stop when it hits a line break or the\n",
                "    #  maximum number of lines, set by PERTINENT_LINE_LIMIT\n",
                "    a = [1, 1, 2, 3]\n",
                "    b = sum(a)\n",
                "    c = b * len(a)\n",
                "    return c / 0  # FIXME I just don't know why this doesn't work!\n",
                "    # Notice that this line will be collected\n",
            ],
            8,
        )
        expected_hits_by_name[fixme_in_broken_function.__repr__()] = (
            fixme_in_broken_function
        )

        formatted_todo_in_pretty_function = Hit(
            self.hit_tests,
            36,
            ["todo"],
            [
                "def a_very_pretty_example():\n",
                "    # TODO Titled Issue! | In this format, you can define a title and a body! Also labels like #example or #enhancement\n",
                '    print("Check this out!")\n',
            ],
            1,
        )
        formatted_todo_in_pretty_function.structured_title = "TODO Titled Issue!"
        formatted_todo_in_pretty_function.structured_body = "In this format, you can define a title and a body! Also labels like #example or #enhancement"
        formatted_todo_in_pretty_function.structured_labels = ["example", "enhancement"]
        expected_hits_by_name[formatted_todo_in_pretty_function.__repr__()] = (
            formatted_todo_in_pretty_function
        )

        todo_in_closed_function = Hit(
            self.hit_tests,
            42,
            ["todo"],
            [
                "def a_closed_example():\n",
                "    # TODO Closed Issues are helpful! | This issue is closed, but the TODO string is still in the codebase!\n",
                "    print(\n",
                '        "This should be a red flag, because if the issue is still in the code then something isn\'t done yet"\n',
                "    )\n",
                '    print("(Though it may simply be that the comment hasn\'t been removed)")\n',
            ],
            1,
        )
        todo_in_closed_function.structured_title = "TODO Closed Issues are helpful!"
        todo_in_closed_function.structured_body = (
            "This issue is closed, but the TODO string is still in the codebase!"
        )
        expected_hits_by_name[todo_in_closed_function.__repr__()] = (
            todo_in_closed_function
        )

        for hit in hits_by_name:
            assert hits_by_name[hit] == expected_hits_by_name[hit]

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_non_verbose_print(self, stderr):
        parsers = {}

        _, _ = todo_or_not.todo_check.find_hits(
            self.unsupported_encoding_test, False, "# todoon", parsers
        )

        self.assertEqual(stderr.getvalue(), "")

    @unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_verbose_print(self, stderr):
        parsers = {}

        _, _ = todo_or_not.todo_check.find_hits(
            self.unsupported_encoding_test, True, "# todoon", parsers
        )

        expected_value = "WARNING: File uses unsupported encoding, we will skip it but consider adding to .todo-ignore (Supported encodings: ['utf-8', 'utf-16']) \n *  tests\\resources\\logo.png"
        expected_value = expected_value.strip()

        printed_value = stderr.getvalue()
        printed_value = expected_value.strip()

        self.assertEqual(printed_value, expected_value)

    def test_unsupported_encoding(self):
        parsers = {}

        _, _ = todo_or_not.todo_check.find_hits(
            self.unsupported_encoding_test, False, "# todoon", parsers
        )

    def test_broken_file_appears_utf(self):
        parsers = {}

        hits, encoding = todo_or_not.todo_check.find_hits(
            self.broken_encoding_test, False, "# todoon", parsers
        )

        assert len(hits) == 0
        assert encoding == "utf-8"
        parsers = {}

        hits, encoding = todo_or_not.todo_check.find_hits(
            self.really_broken_encoding_test, False, "# todoon", parsers
        )

        assert len(hits) == 0
        assert encoding == "utf-8"


if __name__ == "__main__":
    unittest.main()
