import unittest

from todo_or_not.todo_hit import Hit


class TestTodoHit(unittest.TestCase):
    def setUp(self):
        self.hit_a = Hit("file", 1, ["todo"], ["code"], 0)
        self.hit_a.structured_labels = ["test"]

    def test_eq_with_wrong_type(self):
        assert 1 != self.hit_a

    def test_labels_with_issue_generation(self):
        self.hit_a.generate_issue(True)


if __name__ == "__main__":
    unittest.main()
