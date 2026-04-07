import os
import sys
import unittest

# Add the scripts directory to sys.path so we can import the script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from verify_version_tags import VersionTag, parse_version_tag

class TestVerifyVersionTags(unittest.TestCase):
    def test_valid_tags(self):
        """Test parsing of valid version tags."""
        # Simple vX.Y.Z
        self.assertEqual(
            parse_version_tag("v4.24.1"),
            VersionTag(raw="v4.24.1", major=4, minor=24, patch=1, rc=None, patch_suffix=None)
        )

        # With RC vX.Y.Z-rcK
        self.assertEqual(
            parse_version_tag("v4.24.0-rc1"),
            VersionTag(raw="v4.24.0-rc1", major=4, minor=24, patch=0, rc=1, patch_suffix=None)
        )
        self.assertEqual(
            parse_version_tag("v5.0.0-rc10"),
            VersionTag(raw="v5.0.0-rc10", major=5, minor=0, patch=0, rc=10, patch_suffix=None)
        )

        # With patch suffix vX.Y.Z-patchM
        self.assertEqual(
            parse_version_tag("v4.24.1-patch1"),
            VersionTag(raw="v4.24.1-patch1", major=4, minor=24, patch=1, rc=None, patch_suffix=1)
        )
        self.assertEqual(
            parse_version_tag("v4.24.1-patch12"),
            VersionTag(raw="v4.24.1-patch12", major=4, minor=24, patch=1, rc=None, patch_suffix=12)
        )

        # With RC and patch suffix vX.Y.Z-rcK-patchM
        self.assertEqual(
            parse_version_tag("v4.24.0-rc1-patch2"),
            VersionTag(raw="v4.24.0-rc1-patch2", major=4, minor=24, patch=0, rc=1, patch_suffix=2)
        )

    def test_invalid_tags(self):
        """Test parsing of invalid version tags."""
        invalid_tags = [
            "4.24.1",           # missing 'v'
            "v4.24",            # missing patch version
            "v4.24.1-rc",       # missing RC number
            "v4.24.1-patch",    # missing patch number
            "v4.24.1-foo",      # invalid suffix
            "v4.24.1-rc1-foo",  # invalid suffix after RC
            "v4.24.1-foo-patch1",# invalid prefix before patch
            "",                 # empty string
            "vA.B.C",           # letters instead of numbers
        ]

        for tag in invalid_tags:
            with self.subTest(tag=tag):
                self.assertIsNone(parse_version_tag(tag))

if __name__ == '__main__':
    unittest.main()
