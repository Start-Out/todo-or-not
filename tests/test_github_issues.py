import unittest

import todo_or_not.todo_check


class TestIssueHelperFunctions(unittest.TestCase):
    def test_hash(self):
        output = todo_or_not.todo_check._hash("test")
        self.assertEqual(output, "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3")  # add assertion here


class TestClassHits(unittest.TestCase):

    def setUp(self):
        self.example_hit_todo = todo_or_not.todo_check.Hit('tests\\resources\\example.txt', 6, ['todo'],
                                                           ['def an_unfinished_function():\n',
                                                            '    # TODO Finish documenting todo-or-not\n',
                                                            '    print("Hello, I\'m not quite done, there\'s more to do!")\n',
                                                            '    print("Look at all these things I have to do!")\n',
                                                            '    a = 1 + 1\n', '    b = a * 2\n',
                                                            '    print("Okay I\'m done!")\n'], 1)

        self.example_hit_fixme = todo_or_not.todo_check.Hit('tests\\resources\\example.txt', 24, ['fixme'],
                                                            ['    #  from the line that triggered the issue.\n',
                                                             '    # The search for pertinent lines will stop when it hits a line break or the\n',
                                                             '    #  maximum number of lines, set by PERTINENT_LINE_LIMIT\n',
                                                             '    a = [\n', '        1, 1, 2, 3\n', '    ]\n',
                                                             '    b = sum(a)\n', '    c = b * len(a)\n',
                                                             "    return c / 0  # FIXME I just don't know why this doesn't work!\n",
                                                             '    # Notice that this line will be collected\n'], 8)

        self.example_hit_formatted_todo = todo_or_not.todo_check.Hit('tests\\resources\\example.txt', 36, ['todo'],
                                                                     ['def a_very_pretty_example():\n',
                                                                      '    # TODO Titled Issue! | In this format, you can define a title and a body! Also labels like #example or #enhancement\n',
                                                                      '    print("Check this out!")\n'],
                                                                     1)

    def test_unformatted_hits_not_formatted(self):
        self.assertIsNone(self.example_hit_todo.structured_title)
        self.assertIsNone(self.example_hit_todo.structured_body)
        self.assertIsNone(self.example_hit_todo.structured_labels)

        self.assertIsNone(self.example_hit_fixme.structured_title)
        self.assertIsNone(self.example_hit_fixme.structured_body)
        self.assertIsNone(self.example_hit_fixme.structured_labels)

    def test_formatted_hits_are_formatted(self):
        self.assertIsNone(self.example_hit_todo.structured_title, '# TODO Titled Issue!')
        self.assertIsNone(self.example_hit_todo.structured_body,
                          'In this format, you can define a title and a body! Also labels like #example or #enhancement')
        self.assertIsNone(self.example_hit_todo.structured_labels, ['example', 'enhancement'])


class TestLiveIssueFeatures(unittest.TestCase):
    def setUp(self):
        self.bot_submitted_issues = todo_or_not.todo_check.get_bot_submitted_issues()

    def test_bot_submitted_issues_collected(self):
        assert len(self.bot_submitted_issues) > 0


if __name__ == '__main__':
    unittest.main()
