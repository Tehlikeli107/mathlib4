import importlib.util
import sys
import unittest
import os

# Load the script dynamically because its name contains hyphens
script_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(script_dir, "lake-build-wrapper.py")

spec = importlib.util.spec_from_file_location("lake_build_wrapper", script_path)
if spec is None or spec.loader is None:
    raise ImportError("Could not load lake-build-wrapper.py")

lake_build_wrapper = importlib.util.module_from_spec(spec)
sys.modules["lake_build_wrapper"] = lake_build_wrapper
spec.loader.exec_module(lake_build_wrapper)

BuildOutputProcessor = lake_build_wrapper.BuildOutputProcessor


class TestExtractFileInfo(unittest.TestCase):
    def setUp(self):
        self.processor = BuildOutputProcessor()

    def test_normal_build_line(self):
        """Test a standard successful build line."""
        line = "✔ [4000/9999] Built Mathlib.NumberTheory.LSeries.PrimesInAP"
        expected = {
            'current': 4000,
            'total': 9999,
            'target': 'Mathlib.NumberTheory.LSeries.PrimesInAP',
            'file': 'Mathlib/NumberTheory/LSeries/PrimesInAP.lean'
        }
        self.assertEqual(self.processor.extract_file_info(line), expected)

    def test_building_line_with_time(self):
        """Test a building line that includes trailing execution time."""
        line = "✖ [5000/9999] Building MathlibTest.toAdditive (4.2s)"
        expected = {
            'current': 5000,
            'total': 9999,
            'target': 'MathlibTest.toAdditive',
            'file': 'MathlibTest/toAdditive.lean'
        }
        self.assertEqual(self.processor.extract_file_info(line), expected)

    def test_colon_target(self):
        """Test a target containing a colon, which should not generate a file path."""
        line = "⚠ [1/2] Building batteries:extraDep"
        expected = {
            'current': 1,
            'total': 2,
            'target': 'batteries:extraDep',
            'file': None
        }
        self.assertEqual(self.processor.extract_file_info(line), expected)

    def test_invalid_line(self):
        """Test a line that does not match the expected [N/M] format."""
        line = "Error: error: MathlibTest/toAdditive.lean:168:105: Fields missing"
        self.assertEqual(self.processor.extract_file_info(line), {})

    def test_different_spacing_and_verb(self):
        """Test a line with arbitrary spacing and a different verb."""
        line = "   [10/20]    Compiling    My.Module.Name   "
        expected = {
            'current': 10,
            'total': 20,
            'target': 'My.Module.Name',
            'file': 'My/Module/Name.lean'
        }
        self.assertEqual(self.processor.extract_file_info(line), expected)

    def test_no_file_info(self):
        """Test with an empty string or generic summary string."""
        self.assertEqual(self.processor.extract_file_info(""), {})
        self.assertEqual(self.processor.extract_file_info("Build completed successfully (7401 jobs)."), {})

if __name__ == '__main__':
    unittest.main()
