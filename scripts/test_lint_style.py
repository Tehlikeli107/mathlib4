import unittest
import importlib.util
import sys
from pathlib import Path

# Import lint-style.py
# We use importlib because the filename contains a hyphen
spec = importlib.util.spec_from_file_location("lint_style", "scripts/lint-style.py")
lint_style = importlib.util.module_from_spec(spec)
sys.modules["lint_style"] = lint_style
spec.loader.exec_module(lint_style)

class TestLintStyle(unittest.TestCase):
    def test_import(self):
        """Test that the module imports correctly."""
        self.assertIsNotNone(lint_style)

    def test_annotate_comments(self):
        """Test comment annotation logic."""
        lines = [
            (1, "def foo := 1\n"),
            (2, "-- comment\n"),
            (3, "  -- comment indented\n"),
            (4, "/- block comment -/\n"),
            (5, "def bar := 2 -- inline comment\n"),
        ]
        annotated = list(lint_style.annotate_comments(lines))
        self.assertEqual(len(annotated), 5)
        # format: (line_nr, line, is_comment)
        self.assertFalse(annotated[0][2]) # Not comment
        self.assertTrue(annotated[1][2])  # Comment
        self.assertTrue(annotated[2][2])  # Comment
        self.assertTrue(annotated[3][2])  # Comment
        self.assertFalse(annotated[4][2]) # Not comment (line starts not as comment)

    def test_annotate_strings(self):
        """Test string annotation logic."""
        # input format: (line_nr, line, is_comment)
        input_lines = [
            (1, 'def s := "string"\n', False),
            (2, 'def s2 := "string with \\"quote\\""\n', False),
            # This line is a comment, so annotate_strings should theoretically ignore it or handle it?
            # actually annotate_strings implementation ignores the passed is_comment flag
            # and does its own detection for block comments.
            (3, '-- "comment with quote"\n', True),
        ]

        annotated = list(lint_style.annotate_strings(input_lines))
        self.assertEqual(len(annotated), 3)
        # format: (line_nr, line, is_comment, is_string_or_has_quote)
        self.assertTrue(annotated[0][3])
        self.assertTrue(annotated[1][3])
        # annotate_strings returns True if line has quotes, regardless of context (mostly)
        self.assertTrue(annotated[2][3])

    def test_four_spaces_in_second_line(self):
        """Test 4-space indentation check."""
        path = Path("test.lean")

        # Case 1: Correct indentation (4 spaces)
        lines = [
            (1, "theorem foo :\n"),
            (2, "    Nat := 0\n")
        ]
        # We need to simulate the input to the check function.
        # In lint(), it passes list(enumerate(lines, 1)).
        # But four_spaces_in_second_line expects just that list.

        errors, newlines = lint_style.four_spaces_in_second_line(lines, path)
        self.assertEqual(errors, [])
        self.assertEqual(newlines[1][1], "    Nat := 0\n")

        # Case 2: Incorrect indentation (2 spaces)
        lines = [
            (1, "theorem foo :\n"),
            (2, "  Nat := 0\n")
        ]
        errors, newlines = lint_style.four_spaces_in_second_line(lines, path)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], lint_style.ERR_IND)
        # It should fix it in newlines
        self.assertEqual(newlines[1][1], "    Nat := 0\n")

        # Case 3: Correct indentation for | (2 spaces)
        lines = [
            (1, "theorem foo :\n"),
            (2, "  | 0 => 0\n")
        ]
        errors, newlines = lint_style.four_spaces_in_second_line(lines, path)
        self.assertEqual(errors, [])

    def test_isolated_by_dot_semicolon_check(self):
        """Test isolated 'by' check."""
        path = Path("test.lean")

        lines = [
            (1, "lemma foo := by\n"),
            (2, "  simp\n"),
            (3, "by\n"), # Error: isolated by
        ]

        errors, newlines = lint_style.isolated_by_dot_semicolon_check(lines, path)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], lint_style.ERR_IBY)
        self.assertEqual(errors[0][1], 3) # Line 3

    def test_left_arrow_check(self):
        """Test left arrow spacing check."""
        path = Path("test.lean")

        lines = [
            (1, "def f := ←x\n"),
        ]

        # left_arrow_check calls annotate_comments inside, so we pass raw lines (enumerated)
        errors, newlines = lint_style.left_arrow_check(lines, path)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], lint_style.ERR_ARR)
        self.assertEqual(newlines[0][1], "def f := ← x\n")

if __name__ == '__main__':
    unittest.main()
