import unittest
import sys
import os
import importlib.util

# Add the scripts directory to the path so we can import lake-build-wrapper.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

spec = importlib.util.spec_from_file_location("lake_build_wrapper", os.path.abspath(os.path.join(os.path.dirname(__file__), 'lake-build-wrapper.py')))
lake_build_wrapper = importlib.util.module_from_spec(spec)
sys.modules["lake_build_wrapper"] = lake_build_wrapper
spec.loader.exec_module(lake_build_wrapper)

class TestBuildOutputProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = lake_build_wrapper.BuildOutputProcessor()

    def test_extract_file_info_normal(self):
        """Test extraction of normal file targets."""
        line = "[1/2] Building Mathlib.Data.Nat.Basic"
        info = self.processor.extract_file_info(line)
        self.assertEqual(info['current'], 1)
        self.assertEqual(info['total'], 2)
        self.assertEqual(info['target'], "Mathlib.Data.Nat.Basic")
        self.assertEqual(info['file'], "Mathlib/Data/Nat/Basic.lean")

    def test_extract_file_info_non_file(self):
        """Test extraction of non-file targets (containing colon)."""
        line = "[1/2] Building batteries:extraDep"
        info = self.processor.extract_file_info(line)
        self.assertEqual(info['current'], 1)
        self.assertEqual(info['total'], 2)
        self.assertEqual(info['target'], "batteries:extraDep")
        self.assertIsNone(info['file'])

    def test_extract_file_info_no_match(self):
        """Test when the line doesn't match the expected format."""
        line = "Some other line entirely"
        info = self.processor.extract_file_info(line)
        self.assertEqual(info, {})

if __name__ == '__main__':
    unittest.main()
