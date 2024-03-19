import os
import unittest

import todo_or_not.todo_check
import todo_or_not.localize


class TestFileEncoding(unittest.TestCase):
    def test_todoignore_encoding_pass(self):
        use = "utf-8"
        use_path = os.path.join("tests", "resources", f"{use}.txt")

        encoding = todo_or_not.todo_check.get_encoding(use_path, todo_or_not.localize.SUPPORTED_ENCODINGS_TODOIGNORE)
        encoding = encoding.lower()

        self.assertEqual(use, encoding)

    def test_todoignore_encoding_fail(self):
        use_path = os.path.join("tests", "resources", "logo.png")

        encoding = todo_or_not.todo_check.get_encoding(use_path,
                                                       todo_or_not.localize.SUPPORTED_ENCODINGS_TODOIGNORE)

        self.assertIsNone(encoding)

    def test_todo_check_encoding_pass(self):
        use = "utf-8"
        use_path = os.path.join("tests", "resources", f"{use}.txt")

        encoding = todo_or_not.todo_check.get_encoding(use_path, todo_or_not.localize.SUPPORTED_ENCODINGS_TODO_CHECK)
        encoding = encoding.lower()

        self.assertEqual(use, encoding)

    def test_todo_check_encoding_fail(self):
        use_path = os.path.join("tests", "resources", "logo.png")

        encoding = todo_or_not.todo_check.get_encoding(use_path,
                                                       todo_or_not.localize.SUPPORTED_ENCODINGS_TODO_CHECK)

        self.assertIsNone(encoding)


class TestTodoIgnoreHelpers(unittest.TestCase):

    def setUp(self):
        # Set up other files
        a = os.path.join("tests", "resources", "a.txt")
        b = os.path.join("tests", "resources", "b.txt")
        c = os.path.join("tests", "resources", "c.txt")

        self.other_files = [a, b, c]

    def test_copy_contents_to_new_file(self):
        dest = os.path.join("tests", "resources", "y.txt")

        with open(dest, "x") as _dest:
            todo_or_not.todo_check.paste_contents_into_file(self.other_files, _dest)

        with open(dest, "r") as result:
            _result = result.read()

            self.assertEqual("\na\nb\nc\n\n", _result)

        os.remove(dest)

    def test_copy_contents_to_existing_file(self):
        dest = os.path.join("tests", "resources", "z.txt")

        with open(dest, "x") as _dest:
            pass

        with open(dest, "a+") as _dest:
            todo_or_not.todo_check.paste_contents_into_file(self.other_files, _dest)

        with open(dest, "r") as result:
            _result = result.read()

            self.assertEqual("\na\nb\nc\n\n", _result)

        os.remove(dest)

    def test_try_contents_to_new_file_that_exists(self):

        with self.assertRaises(FileExistsError) as context:

            dest = os.path.join("tests", "resources", "x.txt")

            with open(dest, "x") as _dest:
                todo_or_not.todo_check.paste_contents_into_file([], _dest)

        self.assertIsNotNone(context.exception)


if __name__ == '__main__':
    unittest.main()
