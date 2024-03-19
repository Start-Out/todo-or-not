import os
import unittest

import pytest

import todo_or_not.todo_check


@pytest.fixture
def example_hit_todo():
    return todo_or_not.todo_check.Hit('tests\\resources\\example.txt', 6, ['todo'],
                                      ['def an_unfinished_function():\n',
                                       '    # TODO Finish documenting todo-or-not\n',
                                       '    print("Hello, I\'m not quite done, there\'s more to do!")\n',
                                       '    print("Look at all these things I have to do!")\n',
                                       '    a = 1 + 1\n', '    b = a * 2\n',
                                       '    print("Okay I\'m done!")\n'], 1)


@pytest.fixture
def example_hit_fixme():
    return todo_or_not.todo_check.Hit('tests\\resources\\example.txt', 24, ['fixme'],
                                      ['    #  from the line that triggered the issue.\n',
                                       '    # The search for pertinent lines will stop when it hits a line break or the\n',
                                       '    #  maximum number of lines, set by PERTINENT_LINE_LIMIT\n',
                                       '    a = [\n', '        1, 1, 2, 3\n', '    ]\n',
                                       '    b = sum(a)\n', '    c = b * len(a)\n',
                                       "    return c / 0  # FIXME I just don't know why this doesn't work!\n",
                                       '    # Notice that this line will be collected\n'], 8)


@pytest.fixture
def example_hit_formatted_todo():
    return todo_or_not.todo_check.Hit('tests\\resources\\example.txt', 36, ['todo'],
                                      ['def a_very_pretty_example():\n',
                                       '    # TODO Titled Issue! | In this format, you can define a title and a body! Also labels like #example or #enhancement\n',
                                       '    print("Check this out!")\n'],
                                      1)


def test_unformatted_hits_not_formatted(example_hit_todo, example_hit_fixme, example_hit_formatted_todo):
    assert example_hit_todo.structured_title is None
    assert example_hit_todo.structured_body is None
    assert example_hit_todo.structured_labels is None

    assert example_hit_fixme.structured_body is None
    assert example_hit_fixme.structured_labels is None
    assert example_hit_fixme.structured_title is None


def test_formatted_hits_are_formatted(example_hit_todo, example_hit_fixme, example_hit_formatted_todo):
    assert example_hit_formatted_todo.structured_title == '# TODO Titled Issue!'
    assert example_hit_formatted_todo.structured_body == 'In this format, you can define a title and a body! Also labels like #example or #enhancement'
    assert example_hit_formatted_todo.structured_labels == ['example', 'enhancement']


class TestIssueHelperFunctions(unittest.TestCase):
    def test_hash(self):
        output = todo_or_not.todo_check._hash("test")
        self.assertEqual(output, "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3")  # add assertion here


class TestLiveIssueFeatures(unittest.TestCase):
    def setUp(self):
        self.bot_submitted_issues = todo_or_not.todo_check.get_bot_submitted_issues(_test=True)

    def test_bot_submitted_issues_collected(self):
        assert len(self.bot_submitted_issues) > 0


def test_live_submit_test_issue(example_hit_todo):
    api_call = example_hit_todo.generate_issue(_test=True)
    assert api_call == ['gh', 'api', '--method', 'POST', '-H', 'Accept: application/vnd.github+json', '-H',
                        'X-GitHub-Api-Version: 2022-11-28', '/repos/owner/repository/issues', '-f',
                        'title=TODO -     # TODO Finish documenting todo-or-not\n', '-f',
                        'body=## [TODO]           - tests\\resources\\example.txt:6 - # TODO Finish documenting todo-or-not\n\n```txt\n   5:\tdef an_unfinished_function():\n * 6:\t    # TODO Finish documenting todo-or-not\n   7:\t    print("Hello, I\'m not quite done, there\'s more to do!")\n   8:\t    print("Look at all these things I have to do!")\n   9:\t    a = 1 + 1\n  10:\t    b = a * 2\n  11:\t    print("Okay I\'m done!")\n```\n\nReference: <a href="https://github.com/Start-Out/todo-or-not/blob/reference/tests\\resources\\example.txt">tests\\resources\\example.txt</a>',
                        '-f', 'assignees[]=octocat']


if __name__ == '__main__':
    unittest.main()
