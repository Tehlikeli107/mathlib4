
import unittest
import tempfile
import os
import sys

# Add the current directory to sys.path to import the script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import fix_unused

class TestFixUnused(unittest.TestCase):
    def test_process_file_multiple_edits_same_line(self):
        # "unused1" is at index 8 (col 9, 1-based)
        # "unused2" is at index 17 (col 18, 1-based)
        # content = "def foo(unused1, unused2): pass\n"
        #            0123456789012345678901234567890
        #            def foo(u       , u       ): pass

        content = "def foo(unused1, unused2): pass\n"

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Edits in increasing column order (as typically emitted by tools)
            # Current implementation processes them in this order (if stable sort)
            edits = [
                {'line_num': 1, 'col_num': 9, 'var_name': 'unused1'},
                {'line_num': 1, 'col_num': 18, 'var_name': 'unused2'}
            ]

            fix_unused.process_file(tmp_path, edits)

            with open(tmp_path, 'r', encoding='utf-8') as f:
                new_content = f.read()

            # We expect both to be replaced
            expected = "def foo(_, _): pass\n"
            self.assertEqual(new_content, expected)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == '__main__':
    unittest.main()
