import os
import unittest

import todo_or_not.todo_check as td


class TestTodoignoreUtil(unittest.TestCase):

    def setUp(self):
        self.source_files_list = [
            os.path.join("res", "a.txt"),
            os.path.join("res", "b.txt"),
            os.path.join("res", "c.txt"),
        ]

        self.source_text_list = [
            "hello_world.txt",
            "goodbye_world.txt",
            "directory/file.txt",
            "directory/",
        ]

    def test_todoignore_util_copies_files_to_existing(self):
        # Set up
        safe_dir = os.path.join("tests", "resources", "todoignore_util_dir")
        old_dir = os.getcwd()
        os.chdir(safe_dir)

        with open(".todo-ignore", "r") as _old:
            old_todoignore = _old.read()

        # Run util
        td.todo_ignore_util(
            self.source_files_list, create_mode=False, source_is_text=False
        )

        # Check results
        results = []
        expected = ["existing.content", "a", "b", "c"]

        with open(".todo-ignore", "r") as _results:
            for raw_line in _results.readlines():
                raw_line = raw_line.strip()

                if len(raw_line) > 0:
                    results.append(raw_line)

        self.assertEqual(results, expected)

        # Tear down
        with open(".todo-ignore", "w") as _new:
            _new.write(old_todoignore)

        os.chdir(old_dir)

    def test_todoignore_util_copies_files_to_new(self):
        # Set up
        safe_dir = os.path.join("tests", "resources", "todoignore_util_dir")
        old_dir = os.getcwd()
        os.chdir(safe_dir)

        with open(".todo-ignore", "r") as _old:
            old_todoignore = _old.read()

        os.remove(".todo-ignore")

        # Run util
        td.todo_ignore_util(
            self.source_files_list, create_mode=True, source_is_text=False
        )

        # Check results
        results = []
        expected = ["a", "b", "c"]

        with open(".todo-ignore", "r") as _results:
            for raw_line in _results.readlines():
                raw_line = raw_line.strip()

                if len(raw_line) > 0:
                    results.append(raw_line)

        self.assertEqual(results, expected)

        # Tear down
        with open(".todo-ignore", "w") as _new:
            _new.write(old_todoignore)

        os.chdir(old_dir)

    def test_todoignore_util_writes_lines_to_existing(self):
        # Set up
        safe_dir = os.path.join("tests", "resources", "todoignore_util_dir")
        old_dir = os.getcwd()
        os.chdir(safe_dir)

        with open(".todo-ignore", "r") as _old:
            old_todoignore = _old.read()

        # Run util
        td.todo_ignore_util(
            self.source_text_list, create_mode=False, source_is_text=True
        )

        # Check results
        results = []
        expected = [
            "existing.content",
            "hello_world.txt",
            "goodbye_world.txt",
            "directory/file.txt",
            "directory/",
        ]

        with open(".todo-ignore", "r") as _results:
            for raw_line in _results.readlines():
                raw_line = raw_line.strip()

                if len(raw_line) > 0:
                    results.append(raw_line)

        self.assertEqual(results, expected)

        # Tear down
        with open(".todo-ignore", "w") as _new:
            _new.write(old_todoignore)

        os.chdir(old_dir)

    def test_todoignore_util_writes_lines_to_new(self):
        # Set up
        safe_dir = os.path.join("tests", "resources", "todoignore_util_dir")
        old_dir = os.getcwd()
        os.chdir(safe_dir)

        with open(".todo-ignore", "r") as _old:
            old_todoignore = _old.read()

        os.remove(".todo-ignore")

        # Run util
        td.todo_ignore_util(
            self.source_text_list, create_mode=True, source_is_text=True
        )

        # Check results
        results = []
        expected = [
            "hello_world.txt",
            "goodbye_world.txt",
            "directory/file.txt",
            "directory/",
        ]

        with open(".todo-ignore", "r") as _results:
            for raw_line in _results.readlines():
                raw_line = raw_line.strip()

                if len(raw_line) > 0:
                    results.append(raw_line)

        self.assertEqual(results, expected)

        # Tear down
        with open(".todo-ignore", "w") as _new:
            _new.write(old_todoignore)

        os.chdir(old_dir)

    def test_todoignore_util_handles_missing_files(self):
        # Set up
        safe_dir = os.path.join("tests", "resources", "todoignore_util_dir")
        old_dir = os.getcwd()
        os.chdir(safe_dir)

        with open(".todo-ignore", "r") as _old:
            old_todoignore = _old.read()

        os.remove(".todo-ignore")

        missing_files_list = [
            os.path.join("res", "none1.txt"),
            os.path.join("res", "none2.txt"),
            os.path.join("res", "none3.txt"),
        ]

        # Run util
        td.todo_ignore_util(missing_files_list, create_mode=True, source_is_text=False)

        # Tear down
        with open(".todo-ignore", "w") as _new:
            _new.write(old_todoignore)

        os.chdir(old_dir)

    def test_todoignore_util_does_not_override_in_create_mode(self):
        # Set up
        safe_dir = os.path.join("tests", "resources", "todoignore_util_dir")
        old_dir = os.getcwd()
        os.chdir(safe_dir)

        # Run util
        with self.assertRaises(SystemExit) as context:
            td.todo_ignore_util(["do not write"], create_mode=True, source_is_text=True)

        os.chdir(old_dir)

    def test_todoignore_util_with_directory_target(self):
        # Set up
        safe_dir = os.path.join("tests", "resources", "todoignore_util_dir")
        old_dir = os.getcwd()
        os.chdir(safe_dir)

        with open(".todo-ignore", "r") as _old:
            old_todoignore = _old.read()

        os.remove(".todo-ignore")

        # Run util
        # TODO there is a PermissionError here
        td.todo_ignore_util(["res"], source_is_text=False)

        # Tear down
        with open(".todo-ignore", "w") as _new:
            _new.write(old_todoignore)

        os.chdir(old_dir)
