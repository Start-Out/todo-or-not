import os
import unittest

import todo_or_not.todo_check as td


class TestTodoon(unittest.TestCase):

    def setUp(self):
        os.environ["DEBUG"] = "True"

        self.other_files_list = [
            os.path.join("tests", "resources", "a.txt"),
            os.path.join("tests", "resources", "b.txt"),
            os.path.join("tests", "resources", "c.txt"),
        ]

        self.specific_files_list = [
            os.path.join("tests", "resources", "a.txt"),
            os.path.join("tests", "resources", "b.txt"),
            os.path.join("tests", "resources", "c.txt"),
            os.path.join("tests", "resources", "specific_files"),
        ]

    def _environment_up(
        self,
        resource_dir: str,
        env_variables: list[tuple[str, str]] or None = None,
        disable_debug: bool = False,
    ):
        # Preserve state
        with open(".todo-ignore", "r") as _before:
            self.todoignore_before = _before.read()

        safe_dir = (
            os.path.join("tests", "resources", resource_dir)
            if resource_dir != "."
            else None
        )
        self.old_dir = os.getcwd()

        if safe_dir is not None:
            os.chdir(safe_dir)

        # Set environment variables
        self.active_env_variables = env_variables

        if self.active_env_variables is not None:
            for env_variable in self.active_env_variables:
                key, value = env_variable

                os.environ[key] = value

        if disable_debug:
            os.environ["DEBUG"] = "False"

    def _environment_down(self):
        # Reset environment variables
        if self.active_env_variables is not None:
            for env_variable in self.active_env_variables:
                key, _ = env_variable

                del os.environ[key]

        # Restore state
        os.environ["DEBUG"] = "True"
        os.chdir(self.old_dir)

        with open(".todo-ignore", "w+") as _after:
            _after.write(self.todoignore_before)

    #######################################################################

    def test_todoon_standard_succeeds_with_no_todos(self):
        self._environment_up("no_todos")

        td.todoon(verbose=True, print_mode=True)

        self._environment_down()

    def test_todoon_standard_fails_when_finds_todos(self):
        with self.assertRaises(SystemExit) as context:
            td.todoon(verbose=True)

        self.assertEqual(context.exception.code, 1)

    def test_todoon_silent_pushes_environment_variables(self):
        # Set up
        self._environment_up("specific_files")

        td.todoon(verbose=True, silent=True)

        TODOON_STATUS = os.environ.get("TODOON_STATUS")
        TODOON_PROGRESS = os.environ.get("TODOON_PROGRESS")
        TODOON_FILES_SCANNED = os.environ.get("TODOON_FILES_SCANNED")
        TODOON_TODOS_FOUND = os.environ.get("TODOON_TODOS_FOUND")
        TODOON_FIXMES_FOUND = os.environ.get("TODOON_FIXMES_FOUND")
        TODOON_ENCODING_ERRORS = os.environ.get("TODOON_ENCODING_ERRORS")
        TODOON_ISSUES_GENERATED = os.environ.get("TODOON_ISSUES_GENERATED")
        TODOON_DUPLICATE_ISSUES_AVOIDED = os.environ.get(
            "TODOON_DUPLICATE_ISSUES_AVOIDED"
        )
        TODOON_DUPLICATE_CLOSED_ISSUES = os.environ.get(
            "TODOON_DUPLICATE_CLOSED_ISSUES"
        )

        assert TODOON_STATUS == "finished"
        assert TODOON_PROGRESS == "100.0"
        assert int(TODOON_FILES_SCANNED) == 2
        assert int(TODOON_TODOS_FOUND) == 2
        assert int(TODOON_FIXMES_FOUND) == 0
        assert int(TODOON_ENCODING_ERRORS) == 0
        assert TODOON_ISSUES_GENERATED == "0"
        assert TODOON_DUPLICATE_ISSUES_AVOIDED == "0"
        assert TODOON_DUPLICATE_CLOSED_ISSUES == "0"

        self._environment_down()

    def test_todoon_standard_fails_without_todo_ignore(self):
        with open(".todo-ignore", "r") as _before:
            before = _before.read()
        os.remove(".todo-ignore")

        with self.assertRaises(SystemExit) as context:
            td.todoon()

        self.assertEqual(context.exception.code, 1)

        with open(".todo-ignore", "x") as _after:
            _after.write(before)

    def test_todoon_silent_passes(self):
        td.todoon(verbose=True, silent=True)

    def test_todoon_with_print_and_fail_on_closed_duplicate(self):
        td.todoon(verbose=True, silent=True, fail_closed_duplicates=True)

    def test_todoon_runs_when_forced(self):
        self._environment_up(".")

        os.remove(".todo-ignore")

        td.todoon(verbose=True, silent=True, force=True)

        self._environment_down()

    def test_todoon_takes_individual_targets(self):
        td.todoon(verbose=True, silent=True, files=self.specific_files_list)

        self.assertEqual(os.environ.get("TODOON_FILES_SCANNED"), "6")

    def test_todoignore_uses_wildcards(self):
        # Set up
        self._environment_up("wildcard_test")

        # Run util
        td.todoon()

        # Check results
        files_scanned = os.environ["TODOON_FILES_SCANNED"]

        self.assertEqual(files_scanned, "8")

        # Tear down
        self._environment_down()

    def test_issue_mode(self):
        # Set up
        env = [
            ("GITHUB_REPOSITORY", "Start-Out/todo-or-not"),
            ("GITHUB_REF_NAME", "branch"),
            ("GITHUB_TRIGGERING_ACTOR", "pytest"),
            ("MAXIMUM_ISSUES_GENERATED", "1"),
        ]
        self._environment_up("no_todos", env_variables=env)

        td.todoon(print_mode=False, silent=True)

        self._environment_down()

    def test_issue_mode_cannot_create_issues(self):
        # Set up
        env = [
            ("GITHUB_REPOSITORY", "github/gitignore"),
            ("GITHUB_REF_NAME", "branch"),
            ("GITHUB_TRIGGERING_ACTOR", "pytest"),
        ]
        self._environment_up("specific_files", env_variables=env, disable_debug=True)

        td.todoon(print_mode=False, silent=True)

        assert os.environ["TODOON_ISSUES_GENERATED"] == "0"

        self._environment_down()

    def test_issue_mode_exceed_maximum_issues(self):
        # Set up
        env = [
            ("GITHUB_REPOSITORY", "Start-Out/todo-or-not"),
            ("GITHUB_REF_NAME", "branch"),
            ("GITHUB_TRIGGERING_ACTOR", "pytest"),
            ("MAXIMUM_ISSUES_GENERATED", "1"),
        ]
        self._environment_up("specific_files", env_variables=env)

        with self.assertRaises(SystemExit) as context:
            td.todoon(print_mode=False, silent=True)

        self._environment_down()

    def test_issue_mode_with_fail_on_closed(self):
        env = [
            ("GITHUB_REPOSITORY", "Start-Out/todo-or-not"),
            ("GITHUB_REF_NAME", "branch"),
            ("GITHUB_TRIGGERING_ACTOR", "pytest"),
        ]
        self._environment_up("closed_issue", env_variables=env, disable_debug=True)

        with self.assertRaises(SystemExit) as context:
            td.todoon(print_mode=False, fail_closed_duplicates=True, silent=True)

        self._environment_down()

    def test_issue_collection_live(self):
        env = [
            ("GITHUB_REPOSITORY", "Start-Out/todo-or-not"),
            ("GITHUB_REF_NAME", "branch"),
            ("GITHUB_TRIGGERING_ACTOR", "pytest"),
        ]
        self._environment_up("no_todos", env_variables=env, disable_debug=True)

        td.todoon(print_mode=False, silent=True)

        self._environment_down()

    def test_closed_duplicate_issue_fails(self):
        env = [
            ("GITHUB_REPOSITORY", "Start-Out/todo-or-not"),
            ("GITHUB_REF_NAME", "branch"),
            ("GITHUB_TRIGGERING_ACTOR", "pytest"),
        ]
        self._environment_up("closed_issue", env_variables=env, disable_debug=True)

        with self.assertRaises(SystemExit) as context:
            td.todoon(print_mode=False, fail_closed_duplicates=True)

        self._environment_down()

    def test_environment_variables(self):
        env = [
            ("MAXIMUM_ISSUES_GENERATED", "invalid"),
            ("PERTINENT_LINE_LIMIT", "invalid"),
        ]
        self._environment_up("no_todos", env_variables=env, disable_debug=True)

        td.todoon(print_mode=False, silent=True)

        assert td.get_max_issues() == 8
        assert td.get_pertinent_line_limit() == 8

        self._environment_down()

    def test_singular_passages_in_summary(self):
        env = [
            ("GITHUB_REPOSITORY", "Start-Out/todo-or-not"),
            ("GITHUB_REF_NAME", "branch"),
            ("GITHUB_TRIGGERING_ACTOR", "pytest"),
        ]
        self._environment_up("singular", env_variables=env, disable_debug=True)

        td.todoon(print_mode=False, silent=True)

        # number of issues
        assert os.environ["TODOON_ISSUES_GENERATED"] == "0"
        # number of duplicate issues
        assert os.environ["TODOON_DUPLICATE_ISSUES_AVOIDED"] == "1"
        # number of closed issues
        assert os.environ["TODOON_DUPLICATE_CLOSED_ISSUES"] == "1"

        self._environment_down()

    def test_plural_passages_in_summary(self):
        env = [
            ("GITHUB_REPOSITORY", "Start-Out/todo-or-not"),
            ("GITHUB_REF_NAME", "branch"),
            ("GITHUB_TRIGGERING_ACTOR", "pytest"),
        ]
        self._environment_up("plural", env_variables=env, disable_debug=True)

        td.todoon(print_mode=False, silent=True)

        # number of issues
        assert os.environ["TODOON_ISSUES_GENERATED"] == "0"
        # number of duplicate issues
        assert os.environ["TODOON_DUPLICATE_ISSUES_AVOIDED"] == "2"
        # number of closed issues
        assert os.environ["TODOON_DUPLICATE_CLOSED_ISSUES"] == "2"

        self._environment_down()

    def test_todoon_version_print(self):
        with self.assertRaises(SystemExit) as context:
            td.todoon(silent=True, version=True)

    def test_todoon_progress_bar(self):
        self._environment_up("no_todos")

        td.todoon(verbose=True, print_mode=True, show_progress_bar=True)

        self._environment_down()

    def test_todoon_print_level_summary_only(self):
        self._environment_up("no_todos")

        td.todoon(verbose=True, print_mode=True, print_summary_only=True)

        self._environment_down()

    def test_todoon_print_level_none(self):
        self._environment_up("no_todos")

        td.todoon(verbose=True, print_mode=True, print_nothing=True)

        self._environment_down()


if __name__ == "__main__":
    unittest.main()
