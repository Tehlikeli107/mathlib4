import sys
from pathlib import Path
import pytest

# Add the scripts directory to the path so we can import the script
sys.path.append(str(Path(__file__).parent.resolve()))

from verify_version_tags import parse_version_tag, VersionTag

def test_parse_version_tag_valid():
    """Test parsing valid version tags."""
    # Basic tag
    tag = parse_version_tag("v4.24.1")
    assert tag == VersionTag(raw="v4.24.1", major=4, minor=24, patch=1, rc=None, patch_suffix=None)

    # RC tag
    tag = parse_version_tag("v4.24.0-rc1")
    assert tag == VersionTag(raw="v4.24.0-rc1", major=4, minor=24, patch=0, rc=1, patch_suffix=None)

    # Patch tag
    tag = parse_version_tag("v4.24.1-patch1")
    assert tag == VersionTag(raw="v4.24.1-patch1", major=4, minor=24, patch=1, rc=None, patch_suffix=1)

    # RC and patch tag
    tag = parse_version_tag("v4.24.0-rc1-patch2")
    assert tag == VersionTag(raw="v4.24.0-rc1-patch2", major=4, minor=24, patch=0, rc=1, patch_suffix=2)

def test_parse_version_tag_invalid():
    """Test parsing invalid version tags."""
    assert parse_version_tag("4.24.1") is None  # Missing 'v'
    assert parse_version_tag("v4") is None      # Missing minor and patch
    assert parse_version_tag("v4.24") is None   # Missing patch
    assert parse_version_tag("v4.24.1-rc") is None # Missing rc number
    assert parse_version_tag("v4.24.1-patch") is None # Missing patch number
    assert parse_version_tag("v4.24.a") is None # Non-numeric patch
    assert parse_version_tag("latest") is None  # Completely invalid string

def test_parse_version_tag_edge_cases():
    """Test edge cases for parse_version_tag."""
    assert parse_version_tag(None) is None      # None input
    assert parse_version_tag("") is None        # Empty string
    assert parse_version_tag("   ") is None     # Whitespace only
