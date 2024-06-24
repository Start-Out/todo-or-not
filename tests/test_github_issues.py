import os
import unittest

import pytest

import todo_or_not.todo_check
import todo_or_not.todo_hit
import todo_or_not.utility


@pytest.fixture
def example_hit_todo():
    return todo_or_not.todo_hit.Hit(
        "tests\\resources\\example.txt",
        6,
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


@pytest.fixture
def example_hit_fixme():
    return todo_or_not.todo_check.Hit(
        "tests\\resources\\example.txt",
        24,
        ["fixme"],
        [
            "    #  from the line that triggered the issue.\n",
            "    # The search for pertinent lines will stop when it hits a line break or the\n",
            "    #  maximum number of lines, set by PERTINENT_LINE_LIMIT\n",
            "    a = [\n",
            "        1, 1, 2, 3\n",
            "    ]\n",
            "    b = sum(a)\n",
            "    c = b * len(a)\n",
            "    return c / 0  # FIXME I just don't know why this doesn't work!\n",
            "    # Notice that this line will be collected\n",
        ],
        8,
    )


@pytest.fixture
def example_hit_formatted_todo():
    return todo_or_not.todo_check.Hit(
        "tests\\resources\\example.txt",
        36,
        ["todo"],
        [
            "def a_very_pretty_example():\n",
            "    # TODO Titled Issue! | In this format, you can define a title and a body! Also labels like #example or #enhancement\n",
            '    print("Check this out!")\n',
        ],
        1,
    )


@pytest.fixture
def example_hit_formatted_todo_no_labels():
    return todo_or_not.todo_check.Hit(
        "tests\\resources\\example.txt",
        36,
        ["todo"],
        [
            "def a_very_pretty_example():\n",
            "    # TODO No Labels! | Test coverage said that we have to make an issue without any labels :( # but if there is just an octothorpe then there should be no labels\n",
            '    print("Check this out!")\n',
        ],
        1,
    )


def test_unformatted_hits_not_formatted(
    example_hit_todo, example_hit_fixme, example_hit_formatted_todo
):
    assert example_hit_todo.structured_title is None
    assert example_hit_todo.structured_body is None
    assert example_hit_todo.structured_labels is None

    assert example_hit_fixme.structured_body is None
    assert example_hit_fixme.structured_labels is None
    assert example_hit_fixme.structured_title is None


class TestIssueHelperFunctions(unittest.TestCase):
    def test_hash(self):
        output = todo_or_not.utility.sha1_hash("test")
        self.assertEqual(
            output, "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )  # add assertion here


class TestDebugIssueFeatures(unittest.TestCase):
    def setUp(self):
        if os.environ.get("GITHUB_REPOSITORY", None) is not None:
            del os.environ["GITHUB_REPOSITORY"]

        if os.environ.get("GITHUB_REF_NAME", None) is not None:
            del os.environ["GITHUB_REF_NAME"]

        if os.environ.get("GITHUB_TRIGGERING_ACTOR", None) is not None:
            del os.environ["GITHUB_TRIGGERING_ACTOR"]

        self.bot_submitted_issues = todo_or_not.todo_check.get_bot_submitted_issues(
            _test=True
        )

    def test_unable_to_collect_issues(self):
        result = todo_or_not.todo_check.get_bot_submitted_issues()
        assert result is False

    def test_bot_submitted_issues_collected(self):
        assert self.bot_submitted_issues is False


class TestLiveIssueFeatures(unittest.TestCase):
    def setUp(self):
        self.default_env = [
            ("GITHUB_REPOSITORY", "github/gitignore"),
            ("GITHUB_REF_NAME", "branch"),
            ("GITHUB_TRIGGERING_ACTOR", "pytest"),
        ]

        self.bot_submitted_issues = todo_or_not.todo_check.get_bot_submitted_issues()

        self.example_hit_todo = todo_or_not.todo_check.Hit(
            "tests\\resources\\example.txt",
            6,
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

    def test_bot_submitted_issues_collected(self):
        self._environment_up(".", env_variables=self.default_env)

        assert self.bot_submitted_issues is False

        self._environment_down()

    def test_live_submit_test_issue(self):
        self._environment_up(".", env_variables=self.default_env)

        response = self.example_hit_todo.generate_issue()

        # If the function in test mode makes it all the way to where it would call
        # the subprocesses, it returns true instead.
        assert response is True

        self._environment_down()


def test_debug_submit_test_issue(example_hit_todo):
    response = example_hit_todo.generate_issue(_test=True)

    assert response is True


def test_live_submit_formatted_test_issue(example_hit_formatted_todo):
    response = example_hit_formatted_todo.generate_issue(_test=True)

    assert response is True


if __name__ == "__main__":
    unittest.main()
