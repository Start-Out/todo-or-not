import io
import os
import unittest
import unittest.mock

import todo_or_not.todo_check
import todo_or_not.localize


class TestFindLines(unittest.TestCase):

    def setUp(self):
        self.hit_tests = os.path.join("tests", "resources", "example.txt")
        self.unsupported_encoding_test = os.path.join("tests", "resources", "logo.png")
        self.broken_encoding_test = os.path.join("tests", "resources", "broken.donotopen")
        self.really_broken_encoding_test = os.path.join("tests", "resources", "reallybroken.donotopen")

    def test_find_lines(self):
        hits, encoding = todo_or_not.todo_check.find_lines(self.hit_tests, False, "# todoon", "todo", "fixme")

        hits_repr_list = []
        for hit in hits:
            hits_repr_list.append((hit.__repr__(), hit))
        hits_repr_list.sort()

        assert len(hits) == 3

        # Test Hit contents
        hit_0 = hits_repr_list[0][1]
        hit_1 = hits_repr_list[1][1]
        hit_2 = hits_repr_list[2][1]

        assert hit_0.found_keys == ['todo']
        assert len(hit_0.pertinent_lines) == 3
        assert hit_0.source_line == 36
        assert hit_0.structured_title == '# TODO Titled Issue!'
        assert hit_0.structured_body == 'In this format, you can define a title and a body! Also labels like #example or #enhancement'
        assert hit_0.structured_labels == ['example', 'enhancement']

        assert hit_1.found_keys == ['fixme']
        assert len(hit_1.pertinent_lines) == 10
        assert hit_1.source_line == 24
        assert hit_1.structured_title is None
        assert hit_1.structured_body is None
        assert hit_1.structured_labels is None

        assert hit_2.found_keys == ['todo']
        assert len(hit_2.pertinent_lines) == 7
        assert hit_2.source_line == 6
        assert hit_2.structured_title is None
        assert hit_2.structured_body is None
        assert hit_2.structured_labels is None

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_non_verbose_print(self, stderr):
        _, _ = todo_or_not.todo_check.find_lines(self.unsupported_encoding_test, False, "# todoon", "todo", "fixme")

        self.assertEqual(stderr.getvalue(), "")

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_verbose_print(self, stderr):
        _, _ = todo_or_not.todo_check.find_lines(self.unsupported_encoding_test, True, "# todoon", "todo", "fixme")

        expected_value = "WARNING: File uses unsupported encoding, we will skip it but consider adding to .todo-ignore (Supported encodings: ['utf-8', 'utf-16']) \n *  tests\\resources\\logo.png"
        expected_value = expected_value.strip()

        printed_value = stderr.getvalue()
        printed_value = expected_value.strip()

        self.assertEqual(printed_value, expected_value)

    def test_unsupported_encoding(self):
        _, _ = todo_or_not.todo_check.find_lines(self.unsupported_encoding_test, False, "# todoon", "todo", "fixme")

    def test_broken_file_appears_utf(self):
        hits, encoding = todo_or_not.todo_check.find_lines(self.broken_encoding_test, False, "# todoon", "todo", "fixme")

        assert len(hits) == 0
        assert encoding == 'utf-8'

        hits, encoding = todo_or_not.todo_check.find_lines(self.really_broken_encoding_test, False, "# todoon", "todo",
                                                           "fixme")

        assert len(hits) == 0
        assert encoding == 'utf-8'


if __name__ == '__main__':
    unittest.main()
