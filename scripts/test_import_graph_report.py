import unittest
import importlib.util
import os
import sys

# Import the script
script_path = os.path.join(os.path.dirname(__file__), 'import-graph-report.py')
spec = importlib.util.spec_from_file_location("import_graph_report", script_path)
mgr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mgr)

class TestImportGraphReport(unittest.TestCase):

    def test_no_changes(self):
        base_counts = {"Mathlib.File1": 10}
        head_counts = {"Mathlib.File1": 10}
        changed_files = ["Mathlib/File1.lean"]
        message, high_pct = mgr.compare_counts_from_data(base_counts, head_counts, changed_files)
        self.assertIn("No significant changes", message)
        self.assertEqual(high_pct, "")

    def test_dependency_decrease(self):
        base_counts = {"Mathlib.File1": 10}
        head_counts = {"Mathlib.File1": 8}
        changed_files = ["Mathlib/File1.lean"]
        message, high_pct = mgr.compare_counts_from_data(base_counts, head_counts, changed_files)
        self.assertIn("Dependency changes", message)
        self.assertIn("| Mathlib.File1 | 10 | 8 | -2 (-20.00%) |", message)
        self.assertEqual(high_pct, "")

    def test_dependency_increase_significant(self):
        # new_files = 0
        base_counts = {"Mathlib.File1": 10}
        head_counts = {"Mathlib.File1": 11}
        changed_files = ["Mathlib/File1.lean"]
        message, high_pct = mgr.compare_counts_from_data(base_counts, head_counts, changed_files)
        self.assertIn("Dependency changes", message)
        self.assertIn("| Mathlib.File1 | 10 | 11 | +1 (+10.00%) |", message)
        self.assertIn("| +10.00% | `Mathlib.File1` |", high_pct)

    def test_dependency_increase_insignificant(self):
        # new_files = 1
        base_counts = {"Mathlib.File1": 10}
        head_counts = {"Mathlib.File1": 11, "Mathlib.File2": 5}
        changed_files = ["Mathlib/File1.lean"]
        message, high_pct = mgr.compare_counts_from_data(base_counts, head_counts, changed_files)
        # diff = 1, new_files = 1. diff > new_files is false.
        self.assertIn("No significant changes", message)
        # but 10% > 2%, so it should be in high_pct
        self.assertIn("| +10.00% | `Mathlib.File1` |", high_pct)

    def test_high_percentage_increase(self):
        base_counts = {"Mathlib.File1": 100}
        head_counts = {"Mathlib.File1": 103}
        changed_files = ["Mathlib/File1.lean"]
        message, high_pct = mgr.compare_counts_from_data(base_counts, head_counts, changed_files)
        # diff = 3, new_files = 0. Significant.
        # percent = 3% > 2%. In high_pct.
        self.assertIn("| +3.00% | `Mathlib.File1` |", high_pct)

    def test_new_file_ignored(self):
        base_counts = {}
        head_counts = {"Mathlib.File1": 10}
        changed_files = ["Mathlib/File1.lean"]
        message, high_pct = mgr.compare_counts_from_data(base_counts, head_counts, changed_files)
        self.assertIn("No significant changes", message)
        self.assertEqual(high_pct, "")

    def test_non_lean_files_ignored(self):
        base_counts = {"Mathlib.File1": 10}
        head_counts = {"Mathlib.File1": 15}
        changed_files = ["README.md"]
        message, high_pct = mgr.compare_counts_from_data(base_counts, head_counts, changed_files)
        self.assertIn("No significant changes", message)
        self.assertEqual(high_pct, "")

if __name__ == '__main__':
    unittest.main()
