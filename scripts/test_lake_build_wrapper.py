import unittest
import importlib.util
from enum import Enum

# Load the module dynamically since it has dashes in the name
spec = importlib.util.spec_from_file_location("lake_build_wrapper", "scripts/lake-build-wrapper.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

BuildOutputProcessor = module.BuildOutputProcessor

class TestBuildOutputProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = BuildOutputProcessor()

    def test_detect_block_kind_warning(self):
        self.assertEqual(
            self.processor.detect_block_kind("⚠ [8000/9999] Built Mathlib.Algebra.Quandle (7.0s)"),
            self.processor.BlockKind.WARNING
        )
        self.assertEqual(
            self.processor.detect_block_kind("  ⚠ indented warning"),
            self.processor.BlockKind.WARNING
        )

    def test_detect_block_kind_error(self):
        self.assertEqual(
            self.processor.detect_block_kind("✖ [5000/9999] Building MathlibTest.toAdditive (4.2s)"),
            self.processor.BlockKind.ERROR
        )

    def test_detect_block_kind_info(self):
        self.assertEqual(
            self.processor.detect_block_kind("ℹ info message"),
            self.processor.BlockKind.INFO
        )

    def test_detect_block_kind_none(self):
        self.assertIsNone(self.processor.detect_block_kind("✔ [4000/9999] Built Mathlib.NumberTheory.LSeries.PrimesInAP"))
        self.assertIsNone(self.processor.detect_block_kind("Build completed successfully (7401 jobs)."))
        self.assertIsNone(self.processor.detect_block_kind("warning: Mathlib/Algebra/Quandle.lean:122:0: This line exceeds the 100 character limit"))

if __name__ == '__main__':
    unittest.main()
