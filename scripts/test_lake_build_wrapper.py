import importlib.util
import sys
import os
import unittest
from io import StringIO
from contextlib import redirect_stdout
import re

# Helper to import the module with hyphens
def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Import the module under test
lake_build_wrapper = import_module_from_path('lake_build_wrapper', 'scripts/lake-build-wrapper.py')
BuildOutputProcessor = lake_build_wrapper.BuildOutputProcessor

class TestLakeBuildWrapper(unittest.TestCase):
    def setUp(self):
        self.processor = BuildOutputProcessor()
        # Enums are defined in __init__ and assigned to instance
        self.State = self.processor.State
        self.BlockKind = self.processor.BlockKind

    def process_lines(self, lines):
        # Ensure we start fresh for each call if needed, but setUp handles it for test methods
        # This helper assumes self.processor is ready
        f = StringIO()
        with redirect_stdout(f):
            for line in lines:
                self.processor.process_line(line)
            self.processor.finalize()
        return f.getvalue()

    def test_init(self):
        self.assertEqual(self.processor.warnings, [])
        self.assertEqual(self.processor.errors, [])
        self.assertEqual(self.processor.infos, [])
        self.assertEqual(self.processor.current_block, [])
        self.assertFalse(self.processor.group_open)
        self.assertEqual(self.processor.state, self.State.OUTSIDE)
        self.assertIsNone(self.processor.current_kind)

    def test_is_normal_line(self):
        self.assertTrue(self.processor.is_normal_line("✔ [4000/9999] Built Mathlib"))
        self.assertTrue(self.processor.is_normal_line("✔ [5/10] Built something"))
        self.assertFalse(self.processor.is_normal_line("✖ [5/10] Failed"))
        self.assertFalse(self.processor.is_normal_line("warning: foo"))
        self.assertFalse(self.processor.is_normal_line(""))

    def test_detect_block_kind(self):
        self.assertEqual(self.processor.detect_block_kind("⚠ [1/2] Warn"), self.BlockKind.WARNING)
        self.assertEqual(self.processor.detect_block_kind("✖ [1/2] Error"), self.BlockKind.ERROR)
        self.assertEqual(self.processor.detect_block_kind("ℹ [1/2] Info"), self.BlockKind.INFO)
        self.assertIsNone(self.processor.detect_block_kind("✔ [1/2] Ok"))
        self.assertIsNone(self.processor.detect_block_kind("Just some text"))

    def test_is_build_summary(self):
        self.assertTrue(self.processor.is_build_summary("error: build failed"))
        self.assertTrue(self.processor.is_build_summary("Build completed successfully (7401 jobs)."))
        self.assertTrue(self.processor.is_build_summary("Some required targets logged failures:"))
        self.assertTrue(self.processor.is_build_summary("Error: Process completed with exit code 1"))
        self.assertFalse(self.processor.is_build_summary("✔ [1/2] Ok"))
        self.assertFalse(self.processor.is_build_summary("warning: check this"))

    def test_extract_file_info(self):
        # Normal file target
        line = "[4000/9999] Built Mathlib.NumberTheory.LSeries.PrimesInAP"
        info = self.processor.extract_file_info(line)
        self.assertEqual(info['current'], 4000)
        self.assertEqual(info['total'], 9999)
        self.assertEqual(info['target'], "Mathlib.NumberTheory.LSeries.PrimesInAP")
        self.assertEqual(info['file'], "Mathlib/NumberTheory/LSeries/PrimesInAP.lean")

        # Non-file target
        line = "[100/200] Building batteries:extraDep"
        info = self.processor.extract_file_info(line)
        self.assertEqual(info['current'], 100)
        self.assertEqual(info['total'], 200)
        self.assertEqual(info['target'], "batteries:extraDep")
        self.assertIsNone(info['file'])

        # Invalid line
        info = self.processor.extract_file_info("Random output line")
        self.assertEqual(info, {})

    def test_open_group_helpers(self):
        f = StringIO()
        with redirect_stdout(f):
            self.processor.open_group_for_normal_line("✔ [1/2] Test")
            self.assertTrue(self.processor.group_open)
            self.processor.close_group()
            self.assertFalse(self.processor.group_open)

        output = f.getvalue()
        self.assertIn("::group::Build progress [starting at 1/2]", output)
        self.assertIn("::endgroup::", output)

    def test_normal_sequence(self):
        lines = [
            "✔ [1/3] Built A\n",
            "✔ [2/3] Built B\n",
            "✔ [3/3] Built C\n"
        ]
        output = self.process_lines(lines)

        # Should open group once, print lines, and close group at end
        self.assertIn("::group::Build progress [starting at 1/3]", output)
        self.assertEqual(output.count("::group::"), 1)
        self.assertEqual(output.count("::endgroup::"), 1)
        for line in lines:
            self.assertIn(line, output)

        self.assertEqual(self.processor.warnings, [])
        self.assertEqual(self.processor.errors, [])

    def test_warning_block(self):
        # Use newlines to simulate file reading
        lines = [
            "⚠ [1/2] Built A\n",
            "warning: something is wrong\n",
            "more info\n",
            "✔ [2/2] Built B\n"
        ]
        output = self.process_lines(lines)

        # 1. Warning block starts -> opens group with colored title
        # 2. Warning block ends when normal line appears -> closes warning group
        # 3. Normal line -> opens progress group
        # 4. Finalize -> closes progress group

        # Check that group title is colorized
        self.assertIn("::group::\x1b[33m⚠ [1/2] Built A\x1b[0m", output)
        self.assertIn("::group::Build progress [starting at 2/2]", output)

        # Start line should NOT be echoed inside the group
        self.assertNotIn("⚠ [1/2] Built A\n", output)

        # Content should be echoed
        self.assertIn("warning: something is wrong\n", output)
        self.assertIn("more info\n", output)
        self.assertIn("✔ [2/2] Built B\n", output)

        # Verify state
        self.assertEqual(len(self.processor.warnings), 1)
        self.assertEqual(self.processor.warnings[0]['file_info']['target'], "A")
        self.assertEqual(self.processor.warnings[0]['messages'], ["warning: something is wrong"])
        self.assertEqual(self.processor.warnings[0]['full_output'], "⚠ [1/2] Built A\nwarning: something is wrong\nmore info\n")

    def test_error_block(self):
        lines = [
            "✖ [1/1] Failed X\n",
            "error: bad things happened\n",
            "Build completed successfully\n"
        ]
        output = self.process_lines(lines)

        self.assertIn("::group::\x1b[31m✖ [1/1] Failed X\x1b[0m", output)
        self.assertIn("error: bad things happened\n", output)
        self.assertIn("Build completed successfully\n", output)

        self.assertEqual(len(self.processor.errors), 1)
        self.assertEqual(self.processor.errors[0]['messages'], ["error: bad things happened"])
        self.assertEqual(self.processor.errors[0]['full_output'], "✖ [1/1] Failed X\nerror: bad things happened\n")

        # "Build completed successfully" triggers flush, prints it, and goes to OUTSIDE.
        # It should NOT be part of the error block full_output.
        self.assertNotIn("Build completed successfully", self.processor.errors[0]['full_output'])

    def test_mixed_sequence(self):
        lines = [
            "✔ [1/4] A\n",
            "ℹ [2/4] B\n",
            "info: check this\n",
            "✔ [3/4] C\n",
            "✖ [4/4] D\n",
            "error: fail\n"
        ]
        output = self.process_lines(lines)

        self.assertEqual(len(self.processor.infos), 1)
        self.assertEqual(len(self.processor.errors), 1)
        self.assertEqual(len(self.processor.warnings), 0)

        # Verify groups
        # 1. Progress group for A
        # 2. Info group for B (closes progress)
        # 3. Progress group for C (closes info)
        # 4. Error group for D (closes progress)
        # 5. Finalize closes error group

        self.assertEqual(output.count("::group::"), 4)
        self.assertEqual(output.count("::endgroup::"), 4)

    def test_finalize_in_block(self):
        lines = [
            "✖ [1/1] Error start\n",
            "error: content\n"
        ]
        # No normal line or summary line to close it, so finalize must close it
        output = self.process_lines(lines)

        self.assertIn("::group::\x1b[31m✖ [1/1] Error start\x1b[0m", output)
        self.assertIn("::endgroup::", output)
        self.assertEqual(len(self.processor.errors), 1)
        self.assertEqual(self.processor.errors[0]['full_output'], "✖ [1/1] Error start\nerror: content\n")

    def test_get_summary(self):
        lines = [
            "⚠ [1/2] A\n",
            "warning: 1\n",
            "✖ [2/2] B\n",
            "error: 1\n"
        ]
        self.process_lines(lines)
        summary = self.processor.get_summary()

        self.assertEqual(summary['warning_count'], 1)
        self.assertEqual(summary['error_count'], 1)
        self.assertEqual(summary['info_count'], 0)
        self.assertEqual(len(summary['warnings']), 1)
        self.assertEqual(len(summary['errors']), 1)

if __name__ == '__main__':
    unittest.main()
