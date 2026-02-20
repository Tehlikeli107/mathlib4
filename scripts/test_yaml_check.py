import unittest
import sys
import os

# Ensure we can import yaml_check from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yaml_check import tiered_extract

class TestTieredExtract(unittest.TestCase):
    def test_simple_extract(self):
        """Test simple flat dictionary."""
        data = {"a": "b"}
        expected = [(["a"], "b")]
        self.assertEqual(tiered_extract(data), expected)

    def test_nested_extract(self):
        """Test nested dictionary."""
        data = {"a": {"b": "c"}}
        expected = [(["a", "b"], "c")]
        self.assertEqual(tiered_extract(data), expected)

    def test_deep_nesting(self):
        """Test deeper nesting."""
        data = {"a": {"b": {"c": "d"}}}
        expected = [(["a", "b", "c"], "d")]
        self.assertEqual(tiered_extract(data), expected)

    def test_mixed_structure(self):
        """Test mixed flat and nested dictionary."""
        data = {"a": "b", "c": {"d": "e"}}
        expected = [(["a"], "b"), (["c", "d"], "e")]
        # Sort to handle dictionary order variations
        self.assertEqual(sorted(tiered_extract(data)), sorted(expected))

    def test_filtering_empty(self):
        """Test filtering of empty values."""
        data = {"a": "", "b": None}
        expected = []
        self.assertEqual(tiered_extract(data), expected)

    def test_filtering_slash(self):
        """Test filtering of values containing slash."""
        data = {"a": "foo/bar"}
        expected = []
        self.assertEqual(tiered_extract(data), expected)

    def test_empty_dict(self):
        """Test empty dictionary."""
        data = {}
        expected = []
        self.assertEqual(tiered_extract(data), expected)

if __name__ == "__main__":
    unittest.main()
