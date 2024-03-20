import os
import unittest

import todo_or_not.todo_check


class TestLocalization(unittest.TestCase):
    def setUp(self):
        os.environ["REGION"] = '"not a supported region"'
        os.environ["OS"] = '"not a supported operating system"'

    def test_unsupported_and_supported_regions(self):
        # Check unsupported
        region = todo_or_not.todo_check.get_region()

        self.assertEqual(region, "en_us")

        # Check supported
        os.environ["REGION"] = "ko_kr"
        region = todo_or_not.todo_check.get_region()

        self.assertEqual(region, "ko_kr")

    def test_unsupported_and_supported_operating_systems(self):
        # Check unsupported
        region = todo_or_not.todo_check.get_os()

        self.assertEqual(region, "default")

        # Check supported
        os.environ["OS"] = "windows_nt"
        region = todo_or_not.todo_check.get_os()

        self.assertEqual(region, "windows_nt")


def test_get_encoding_file_not_exists():
    assert todo_or_not.todo_check.get_encoding("!*&^#(#)@@", []) is None




if __name__ == '__main__':
    unittest.main()
