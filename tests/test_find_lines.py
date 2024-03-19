import os
import unittest

import todo_or_not.todo_check
import todo_or_not.localize


class TestFindLines(unittest.TestCase):

    def setUp(self):
        self.hit_tests = os.path.join("tests", "resources", "example.txt")
        self.unsupported_encoding_test = os.path.join("tests", "resources", "logo.png")
        self.broken_encoding_test = os.path.join("tests", "resources", "broken.donotopen")
        self.really_broken_encoding_test = os.path.join("tests", "resources", "reallybroken.donotopen")

        self.expected_hit_0 = "[FIXME]          - tests\\resources\example.txt:24 - return c / 0  # FIXME I just don't know why this doesn't work!"
        self.expected_hit_1 = "[TODO]           - tests\\resources\example.txt:36 - # TODO Titled Issue! | In this format, you can define a title and a body! Also labels like #example or #enhancement"
        self.expected_hit_2 = "[TODO]           - tests\\resources\example.txt:6 - # TODO Finish documenting todo-or-not"

    def test_find_lines(self):
        hits, encoding = todo_or_not.todo_check.find_lines(self.hit_tests, "#todoon", "todo", "fixme")

        hits_repr_list = []
        for hit in hits:
            hits_repr_list.append((hit.__repr__(), hit))
        hits_repr_list.sort()

        assert len(hits) == 3

        assert self.expected_hit_0 == hits_repr_list[0][0]
        assert self.expected_hit_1 == hits_repr_list[1][0]
        assert self.expected_hit_2 == hits_repr_list[2][0]

        # Test Hit contents
        hit_0 = hits_repr_list[0][1]
        hit_1 = hits_repr_list[1][1]
        hit_2 = hits_repr_list[2][1]

        assert hit_0.found_keys == ['fixme']
        assert len(hit_0.pertinent_lines) == 10
        assert hit_0.source_line == 24
        assert hit_0.structured_title is None
        assert hit_0.structured_body is None
        assert hit_0.structured_labels is None

        assert hit_1.found_keys == ['todo']
        assert len(hit_1.pertinent_lines) == 3
        assert hit_1.source_line == 36
        assert hit_1.structured_title == '# TODO Titled Issue!'
        assert hit_1.structured_body == 'In this format, you can define a title and a body! Also labels like #example or #enhancement'
        assert hit_1.structured_labels == ['example', 'enhancement']

        assert hit_2.found_keys == ['todo']
        assert len(hit_2.pertinent_lines) == 7
        assert hit_2.source_line == 6
        assert hit_2.structured_title is None
        assert hit_2.structured_body is None
        assert hit_2.structured_labels is None

    def test_unsupported_encoding(self):
        todo_or_not.todo_check.find_lines(self.unsupported_encoding_test, "#todoon", "todo", "fixme")

    def test_broken_file_appears_utf(self):
        hits, encoding = todo_or_not.todo_check.find_lines(self.broken_encoding_test, "#todoon", "todo", "fixme")

        assert len(hits) == 0
        assert encoding == 'utf-8'

        hits, encoding = todo_or_not.todo_check.find_lines(self.really_broken_encoding_test, "#todoon", "todo", "fixme")

        assert len(hits) == 0
        assert encoding == 'utf-8'


if __name__ == '__main__':
    unittest.main()
