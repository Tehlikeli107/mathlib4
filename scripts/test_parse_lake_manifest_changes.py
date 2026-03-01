import unittest
import importlib.util
import sys
import os

# dynamic import since the script has a hyphen (if it did) or is just a script
script_path = os.path.join(os.path.dirname(__file__), "parse_lake_manifest_changes.py")
spec = importlib.util.spec_from_file_location("parse_lake_manifest_changes", script_path)
parse_script = importlib.util.module_from_spec(spec)
sys.modules["parse_lake_manifest_changes"] = parse_script
spec.loader.exec_module(parse_script)

format_changes = parse_script.format_changes

class TestFormatChanges(unittest.TestCase):
    def test_empty_changes(self):
        """Test formatting when there are no changes"""
        self.assertEqual(format_changes([]), "No dependency versions were changed")

    def test_update_only(self):
        """Test formatting a single update change"""
        changes = [{
            'type': 'update',
            'dependency': 'mathlib',
            'old_version': '1234567890abcdef',
            'new_version': 'abcdef1234567890',
            'url': 'https://github.com/leanprover-community/mathlib4'
        }]
        expected = (
            "The following dependencies were updated:\n"
            "* mathlib: 1234567 → abcdef1 [[GitHub link]](https://github.com/leanprover-community/mathlib4/compare/1234567890abcdef...abcdef1234567890)"
        )
        self.assertEqual(format_changes(changes), expected)

    def test_addition_only(self):
        """Test formatting a single add change"""
        changes = [{
            'type': 'add',
            'dependency': 'std',
            'version': '1111111111111111',
            'url': 'https://github.com/leanprover/std4'
        }]
        expected = (
            "The following dependencies were added:\n"
            "* std: 1111111 [[GitHub link]](https://github.com/leanprover/std4/commit/1111111111111111)"
        )
        self.assertEqual(format_changes(changes), expected)

    def test_removal_only(self):
        """Test formatting a single remove change"""
        changes = [{
            'type': 'remove',
            'dependency': 'quote4',
            'version': '2222222222222222',
            'url': 'https://github.com/leodemoura/quote4'
        }]
        expected = (
            "The following dependencies were removed:\n"
            "* quote4: 2222222 [[GitHub link]](https://github.com/leodemoura/quote4/commit/2222222222222222)"
        )
        self.assertEqual(format_changes(changes), expected)

    def test_multiple_changes(self):
        """Test formatting multiple different types of changes"""
        changes = [
            {
                'type': 'update',
                'dependency': 'mathlib',
                'old_version': '12345678',
                'new_version': 'abcdef12',
                'url': 'https://github.com/leanprover-community/mathlib4'
            },
            {
                'type': 'add',
                'dependency': 'std',
                'version': '11111111',
                'url': 'https://github.com/leanprover/std4'
            },
            {
                'type': 'remove',
                'dependency': 'quote4',
                'version': '22222222',
                'url': 'https://github.com/leodemoura/quote4'
            }
        ]
        expected = (
            "The following dependencies were updated:\n"
            "* mathlib: 1234567 → abcdef1 [[GitHub link]](https://github.com/leanprover-community/mathlib4/compare/12345678...abcdef12)\n"
            "\n"
            "The following dependencies were added:\n"
            "* std: 1111111 [[GitHub link]](https://github.com/leanprover/std4/commit/11111111)\n"
            "\n"
            "The following dependencies were removed:\n"
            "* quote4: 2222222 [[GitHub link]](https://github.com/leodemoura/quote4/commit/22222222)"
        )
        self.assertEqual(format_changes(changes), expected)

    def test_short_hashes(self):
        """Test formatting with short hashes"""
        changes = [{
            'type': 'update',
            'dependency': 'mathlib',
            'old_version': '12345',
            'new_version': 'abcd',
            'url': 'https://github.com/leanprover-community/mathlib4'
        }]
        expected = (
            "The following dependencies were updated:\n"
            "* mathlib: 12345 → abcd [[GitHub link]](https://github.com/leanprover-community/mathlib4/compare/12345...abcd)"
        )
        self.assertEqual(format_changes(changes), expected)

if __name__ == '__main__':
    unittest.main()
