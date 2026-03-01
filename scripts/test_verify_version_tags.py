import pytest
import sys
import os
from pathlib import Path
import importlib.util

# Load the script as a module
script_path = Path(__file__).parent / "verify_version_tags.py"
spec = importlib.util.spec_from_file_location("verify_version_tags", script_path)
verify_version_tags = importlib.util.module_from_spec(spec)
sys.modules["verify_version_tags"] = verify_version_tags
spec.loader.exec_module(verify_version_tags)

VersionTag = verify_version_tags.VersionTag

def test_version_tag_lt_major_minor_patch():
    v1 = VersionTag("v4.23.0", 4, 23, 0, None, None)
    v2 = VersionTag("v4.24.0", 4, 24, 0, None, None)
    assert v1 < v2
    assert not v2 < v1

def test_version_tag_lt_rc_before_final():
    v_rc = VersionTag("v4.24.0-rc1", 4, 24, 0, 1, None)
    v_final = VersionTag("v4.24.0", 4, 24, 0, None, None)
    assert v_rc < v_final
    assert not v_final < v_rc

def test_version_tag_lt_rc_order():
    v_rc1 = VersionTag("v4.24.0-rc1", 4, 24, 0, 1, None)
    v_rc2 = VersionTag("v4.24.0-rc2", 4, 24, 0, 2, None)
    assert v_rc1 < v_rc2
    assert not v_rc2 < v_rc1

def test_version_tag_lt_patch_after_final():
    v_final = VersionTag("v4.24.0", 4, 24, 0, None, None)
    v_patch = VersionTag("v4.24.0-patch1", 4, 24, 0, None, 1)
    assert v_final < v_patch
    assert not v_patch < v_final

def test_version_tag_lt_patch_order():
    v_patch1 = VersionTag("v4.24.0-patch1", 4, 24, 0, None, 1)
    v_patch2 = VersionTag("v4.24.0-patch2", 4, 24, 0, None, 2)
    assert v_patch1 < v_patch2
    assert not v_patch2 < v_patch1

def test_version_tag_lt_rc_with_patch():
    v_rc = VersionTag("v4.24.0-rc1", 4, 24, 0, 1, None)
    v_rc_patch = VersionTag("v4.24.0-rc1-patch1", 4, 24, 0, 1, 1)
    assert v_rc < v_rc_patch
    assert not v_rc_patch < v_rc

def test_version_tag_lt_complex_sorting():
    tags = [
        VersionTag("v4.23.0", 4, 23, 0, None, None),
        VersionTag("v4.23.0-patch1", 4, 23, 0, None, 1),
        VersionTag("v4.24.0-rc1", 4, 24, 0, 1, None),
        VersionTag("v4.24.0-rc1-patch1", 4, 24, 0, 1, 1),
        VersionTag("v4.24.0-rc2", 4, 24, 0, 2, None),
        VersionTag("v4.24.0", 4, 24, 0, None, None),
        VersionTag("v4.24.0-patch1", 4, 24, 0, None, 1),
        VersionTag("v4.24.1-rc1", 4, 24, 1, 1, None),
        VersionTag("v4.24.1", 4, 24, 1, None, None),
    ]

    # Verify that each tag is strictly less than all subsequent tags
    for i in range(len(tags)):
        for j in range(i + 1, len(tags)):
            assert tags[i] < tags[j], f"Expected {tags[i].raw} < {tags[j].raw}"
            assert not tags[j] < tags[i], f"Expected not {tags[j].raw} < {tags[i].raw}"
