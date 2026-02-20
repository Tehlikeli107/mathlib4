#!/usr/bin/env python3
import unittest
import subprocess
import os
import json
import tempfile

class TestLakeBuildWrapper(unittest.TestCase):
    def test_wrapper_output(self):
        input_data = """✔ [4000/9999] Built Mathlib.NumberTheory.LSeries.PrimesInAP
✖ [5000/9999] Building MathlibTest.toAdditive (4.2s)
trace: .> LEAN_PATH=...
Error: error: MathlibTest/toAdditive.lean:168:105: Fields missing: `fileName`, `fileMap`
Error: error: MathlibTest/toAdditive.lean:219:60: invalid {...} notation, structure type expected
  Name
error: Lean exited with code 1
✔ [6000/9999] Built MathlibTest.MathlibTestExecutable (3.2s)
✔ [7000/9999] Built Mathlib.Analysis.CStarAlgebra.Module.Defs
⚠ [8000/9999] Built Mathlib.Algebra.Quandle (7.0s)
warning: Mathlib/Algebra/Quandle.lean:122:0: This line exceeds the 100 character limit, please shorten it!

Note: This linter can be disabled with `set_option linter.style.longLine false`
✔ [9999/9999] Built Mathlib (111s)
Build completed successfully (7401 jobs).
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_input:
            tmp_input.write(input_data)
            tmp_input_path = tmp_input.name

        # Create a temp file for output JSON
        # We need to manually remove it later
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_output:
            tmp_output_path = tmp_output.name

        # The command to test
        cmd = ["python3", "scripts/lake-build-wrapper.py", tmp_output_path, "cat", tmp_input_path]

        # We need to capture stdout to check for ::group:: commands
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Check stdout contains expected group markers
        # The wrapper prints to stdout whatever it receives, plus group commands
        self.assertIn("::group::Build progress [starting at 4000/9999]", result.stdout)
        self.assertIn("::endgroup::", result.stdout)

        # Check JSON output
        with open(tmp_output_path, 'r') as f:
            summary = json.load(f)

        # Verify summary structure
        # We expect 1 error block (from [5000/9999])
        self.assertEqual(summary['error_count'], 1, "Expected 1 error block")

        # We expect 1 warning block (from [8000/9999])
        self.assertEqual(summary['warning_count'], 1, "Expected 1 warning block")

        # Verify error details
        error_block = summary['errors'][0]
        self.assertEqual(error_block['file_info']['target'], 'MathlibTest.toAdditive')

        # Check that the specific error message is present in the messages list
        found_error = False
        for msg in error_block['messages']:
            if "Fields missing: `fileName`, `fileMap`" in msg:
                found_error = True
                break
        self.assertTrue(found_error, "Specific error message not found in error block messages")

        # Cleanup
        if os.path.exists(tmp_input_path):
            os.remove(tmp_input_path)
        if os.path.exists(tmp_output_path):
            os.remove(tmp_output_path)

if __name__ == '__main__':
    unittest.main()
