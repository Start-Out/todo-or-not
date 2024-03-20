import os
import unittest

import todo_or_not.todo_check as td


class TestTodoon(unittest.TestCase):

    def setUp(self):
        os.environ["DEBUG"] = 'True'

        self.other_files_list = [
            os.path.join("tests", "resources", "a.txt"),
            os.path.join("tests", "resources", "b.txt"),
            os.path.join("tests", "resources", "c.txt")
        ]

        self.specific_files_list = [
            os.path.join("tests", "resources", "a.txt"),
            os.path.join("tests", "resources", "b.txt"),
            os.path.join("tests", "resources", "c.txt"),
            os.path.join("tests", "resources", "specific_files")
        ]

    def test_todoon_standard_succeeds_with_no_todos(self):
        safe_dir = os.path.join("tests", "resources", "no_todos")
        os.chdir(safe_dir)

        td.main(verbose=True)


    def test_todoon_standard_fails_when_finds_todos(self):
        with self.assertRaises(SystemExit) as context:
            td.main(verbose=True)

        self.assertEqual(context.exception.code, 1)


    def test_todoon_silent_pushes_environment_variables(self):
        td.main(verbose=True, silent=True)

        TODOON_STATUS = os.environ.get("TODOON_STATUS")
        TODOON_PROGRESS = os.environ.get("TODOON_PROGRESS")
        TODOON_FILES_SCANNED = os.environ.get("TODOON_FILES_SCANNED")
        TODOON_TODOS_FOUND = os.environ.get("TODOON_TODOS_FOUND")
        TODOON_FIXMES_FOUND = os.environ.get("TODOON_FIXMES_FOUND")
        TODOON_ENCODING_ERRORS = os.environ.get("TODOON_ENCODING_ERRORS")
        TODOON_ISSUES_GENERATED = os.environ.get("TODOON_ISSUES_GENERATED")
        TODOON_DUPLICATE_ISSUES_AVOIDED = os.environ.get("TODOON_DUPLICATE_ISSUES_AVOIDED")

        assert TODOON_STATUS == "finished"
        assert TODOON_PROGRESS == "100.0"
        assert int(TODOON_FILES_SCANNED) > 0
        assert int(TODOON_TODOS_FOUND) > 0
        assert int(TODOON_FIXMES_FOUND) > 0
        assert int(TODOON_ENCODING_ERRORS) > 0
        assert TODOON_ISSUES_GENERATED == "0"
        assert TODOON_DUPLICATE_ISSUES_AVOIDED == "0"

    def test_todoon_standard_fails_without_todo_ignore(self):
        with open(".todo-ignore", "r") as _before:
            before = _before.read()
        os.remove(".todo-ignore")

        with self.assertRaises(SystemExit) as context:
            td.main()

        self.assertEqual(context.exception.code, 1)

        with open(".todo-ignore", "x") as _after:
            _after.write(before)

    def test_todoon_silent_passes(self):
        td.main(verbose=True, silent=True)


    def test_todoon_modifies_existing_todo_ignore(self):
        with open(".todo-ignore", "r") as _before:
            before = _before.read()

        td.main(verbose=True, silent=True, xi=self.other_files_list)

        with open(".todo-ignore", "r") as _after:
            after = _after.read()

        self.assertNotEqual(before, after)

    def test_todoon_creates_new_todo_ignore(self):
        os.remove(".todo-ignore")

        example = "example.todo-ignore"
        example_todo_ignore = [example]

        td.main(verbose=True, silent=True, ni=example_todo_ignore)

        with open(".todo-ignore", "r") as new_todo_ignore:
            new_result = []
            for line in new_todo_ignore.readlines():
                line = line.strip(" \n\t")

                if len(line) > 0:
                    new_result.append(line)

        with open(example, "r") as new_todo_ignore:
            example_result = []
            for line in new_todo_ignore.readlines():
                line = line.strip(" \n\t")

                if len(line) > 0:
                    example_result.append(line)

        self.assertEqual(new_result, example_result)

    def test_todoon_runs_when_forced(self):
        with open(".todo-ignore", "r") as _before:
            before = _before.read()

        os.remove(".todo-ignore")

        td.main(verbose=True, silent=True, force=True)

        with open(".todo-ignore", "x") as _after:
            _after.write(before)

    def test_todoon_takes_individual_targets(self):
        td.main(verbose=True, silent=True, files=self.specific_files_list)

        self.assertEqual(os.environ.get("TODOON_FILES_SCANNED"), '5')


if __name__ == '__main__':
    unittest.main()
