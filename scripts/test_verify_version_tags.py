import sys
from pathlib import Path

# Add scripts directory to path to allow importing verify_version_tags
sys.path.insert(0, str(Path(__file__).parent))

from verify_version_tags import VersionTag, parse_version_tag

def test_parse_version_tag_final_release():
    tag = parse_version_tag("v4.24.1")
    assert tag is not None
    assert tag.raw == "v4.24.1"
    assert tag.major == 4
    assert tag.minor == 24
    assert tag.patch == 1
    assert tag.rc is None
    assert tag.patch_suffix is None

def test_parse_version_tag_rc():
    tag = parse_version_tag("v4.24.0-rc1")
    assert tag is not None
    assert tag.raw == "v4.24.0-rc1"
    assert tag.major == 4
    assert tag.minor == 24
    assert tag.patch == 0
    assert tag.rc == 1
    assert tag.patch_suffix is None

def test_parse_version_tag_patch():
    tag = parse_version_tag("v4.24.1-patch1")
    assert tag is not None
    assert tag.raw == "v4.24.1-patch1"
    assert tag.major == 4
    assert tag.minor == 24
    assert tag.patch == 1
    assert tag.rc is None
    assert tag.patch_suffix == 1

def test_parse_version_tag_rc_patch():
    tag = parse_version_tag("v4.24.0-rc1-patch2")
    assert tag is not None
    assert tag.raw == "v4.24.0-rc1-patch2"
    assert tag.major == 4
    assert tag.minor == 24
    assert tag.patch == 0
    assert tag.rc == 1
    assert tag.patch_suffix == 2

def test_parse_version_tag_invalid():
    assert parse_version_tag("4.24.1") is None  # Missing 'v'
    assert parse_version_tag("v4.24") is None  # Missing patch version
    assert parse_version_tag("v4.a.1") is None  # Invalid minor version
    assert parse_version_tag("v4.24.1-rc") is None  # Missing rc number

def test_version_tag_base_version():
    assert parse_version_tag("v4.24.1").base_version == "v4.24.1"
    assert parse_version_tag("v4.24.0-rc1").base_version == "v4.24.0-rc1"
    assert parse_version_tag("v4.24.1-patch1").base_version == "v4.24.1"
    assert parse_version_tag("v4.24.0-rc1-patch2").base_version == "v4.24.0-rc1"

def test_version_tag_equality():
    tag1 = parse_version_tag("v4.24.1")
    tag2 = parse_version_tag("v4.24.1")
    tag3 = parse_version_tag("v4.24.1-patch1")

    assert tag1 == tag2
    assert tag1 != tag3
    assert tag1 != "v4.24.1"  # Different type

def test_version_tag_comparison_major_minor_patch():
    assert parse_version_tag("v4.23.1") < parse_version_tag("v4.24.1")
    assert parse_version_tag("v4.24.0") < parse_version_tag("v4.24.1")
    assert parse_version_tag("v3.99.99") < parse_version_tag("v4.0.0")

def test_version_tag_comparison_rc():
    # RCs sort before final releases
    assert parse_version_tag("v4.24.0-rc1") < parse_version_tag("v4.24.0")
    assert parse_version_tag("v4.24.0-rc1") < parse_version_tag("v4.24.0-rc2")

    # But a higher patch version with an RC is still greater than a lower patch version final
    assert parse_version_tag("v4.24.0") < parse_version_tag("v4.24.1-rc1")

def test_version_tag_comparison_patch_suffix():
    # Base version < patched version
    assert parse_version_tag("v4.24.1") < parse_version_tag("v4.24.1-patch1")
    assert parse_version_tag("v4.24.1-patch1") < parse_version_tag("v4.24.1-patch2")

    # Same with RC
    assert parse_version_tag("v4.24.0-rc1") < parse_version_tag("v4.24.0-rc1-patch1")

def test_version_tag_supports_no_build():
    # MIN_NO_BUILD_VERSION = (4, 2, 0, 2)  # (major, minor, patch, rc) - rc2 or later

    # Before
    assert not parse_version_tag("v4.1.0").supports_no_build()
    assert not parse_version_tag("v4.2.0-rc1").supports_no_build()

    # At
    assert parse_version_tag("v4.2.0-rc2").supports_no_build()

    # After
    assert parse_version_tag("v4.2.0-rc3").supports_no_build()
    assert parse_version_tag("v4.2.0").supports_no_build()  # Final release sorts after all RCs
    assert parse_version_tag("v4.2.1").supports_no_build()
    assert parse_version_tag("v4.3.0").supports_no_build()
    assert parse_version_tag("v5.0.0").supports_no_build()
