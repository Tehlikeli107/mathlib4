import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Add scripts directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import fix_deprecations
from fix_deprecations import parse_warnings, fix_file_content, main

class TestFixDeprecations(unittest.TestCase):

    def test_parse_warnings(self):
        output = """
Some random output
warning: MyFile.lean:10:5: `Old.Name` has been deprecated. Use `New.Name` instead
warning: OtherFile.lean:2:0: `Foo` has been deprecated. Use `Bar` instead
"""
        warnings = parse_warnings(output)
        self.assertEqual(len(warnings), 2)
        self.assertIn("MyFile.lean", warnings)
        self.assertIn("OtherFile.lean", warnings)

        self.assertEqual(warnings["MyFile.lean"][0], {
            "line": 10,
            "col": 5,
            "old": "Old.Name",
            "new": "New.Name"
        })
        self.assertEqual(warnings["OtherFile.lean"][0], {
            "line": 2,
            "col": 0,
            "old": "Foo",
            "new": "Bar"
        })

    def test_fix_file_content_exact_match(self):
        lines = ["import Mathlib\n", "def foo := Old.Name\n"]
        warnings = [{
            "line": 2,
            "col": 11,
            "old": "Old.Name",
            "new": "New.Name"
        }]

        new_lines, changes, skipped, logs = fix_file_content(lines, warnings)

        self.assertEqual(changes, 1)
        self.assertEqual(new_lines[1], "def foo := New.Name\n")
        self.assertEqual(skipped, [])
        self.assertEqual(len(logs), 1)

    def test_fix_file_content_suffix_match(self):
        # Case: `Fin.lt_iff_val_lt_val` -> `Fin.val_lt_val`
        # user wrote `lt_iff_val_lt_val` (suffix)
        lines = ["def foo := lt_iff_val_lt_val\n"]
        warnings = [{
            "line": 1,
            "col": 11,
            "old": "Fin.lt_iff_val_lt_val",
            "new": "Fin.val_lt_val"
        }]

        new_lines, changes, skipped, logs = fix_file_content(lines, warnings)
        self.assertEqual(new_lines[0], "def foo := val_lt_val\n")
        self.assertEqual(changes, 1)

    def test_fix_file_content_multiple_warnings(self):
        lines = ["foo bar baz\n"]
        # warnings must be processed in reverse order of position
        warnings = [
            {"line": 1, "col": 0, "old": "foo", "new": "FOO"},
            {"line": 1, "col": 8, "old": "baz", "new": "BAZ"}
        ]

        new_lines, changes, skipped, logs = fix_file_content(lines, warnings)
        self.assertEqual(new_lines[0], "FOO bar BAZ\n")
        self.assertEqual(changes, 2)

    def test_fix_file_content_overlap(self):
        # Sort key: (line, col). (1, 2) > (1, 0).
        # So we process (1, 2) ("cd") first. Replace with "XY". "abXYe".
        # Then we process (1, 0) ("abcde"). It expects "abcde" but finds "abXYe". Match fails.

        lines = ["abcde\n"]
        warnings = [
            {"line": 1, "col": 0, "old": "abcde", "new": "12345"},
            {"line": 1, "col": 2, "old": "cd", "new": "XY"}
        ]

        new_lines, changes, skipped, logs = fix_file_content(lines, warnings)

        self.assertEqual(changes, 1)
        self.assertEqual(new_lines[0], "abXYe\n")
        self.assertEqual(len(skipped), 1)
        # Verify the skipped item contains the actual content found
        self.assertTrue(skipped[0][3].startswith("abXYe"))

    def test_fix_file_content_out_of_range(self):
        lines = ["foo\n"]
        warnings = [{"line": 2, "col": 0, "old": "bar", "new": "baz"}]
        new_lines, changes, skipped, logs = fix_file_content(lines, warnings)
        self.assertEqual(changes, 0)
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0][3], "out of range")

    @patch('fix_deprecations.subprocess.run')
    @patch('fix_deprecations.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="def foo := Old.Name\n")
    def test_main(self, mock_file, mock_exists, mock_run):
        # Setup mock subprocess
        mock_result = MagicMock()
        mock_result.stdout = "warning: MyFile.lean:1:11: `Old.Name` has been deprecated. Use `New.Name` instead\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Setup mock exists
        mock_exists.return_value = True

        # Run main
        main()

        # Verify subprocess called
        mock_run.assert_called_with(['lake', 'build', '--no-build'], capture_output=True, text=True)

        # Verify file opened for read and write
        # Note: 'open' is used for both read and write.
        # mock_file() returns the file handle.

        # Assert file was opened for reading
        mock_file.assert_any_call("MyFile.lean", 'r')
        # Assert file was opened for writing
        mock_file.assert_any_call("MyFile.lean", 'w')

        # Verify content written
        handle = mock_file()
        handle.writelines.assert_called_with(["def foo := New.Name\n"])

if __name__ == '__main__':
    unittest.main()
