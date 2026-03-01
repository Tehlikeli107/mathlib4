import re
import sys
import importlib.util
from unittest.mock import patch

def import_script(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

try:
    dashboard = import_script("downstream_dashboard", "scripts/downstream_dashboard.py")
    tags = import_script("downstream_tags", "scripts/downstream-tags.py")

    assert hasattr(dashboard, "VERSION_PATTERN"), "VERSION_PATTERN missing in downstream_dashboard"
    assert hasattr(tags, "VERSION_PATTERN"), "VERSION_PATTERN missing in downstream-tags"

    # Test compilation
    assert dashboard.VERSION_PATTERN.match('v4.1.0') is not None
    assert dashboard.VERSION_PATTERN.match('v4.1.0-rc1') is not None
    assert dashboard.VERSION_PATTERN.match('v5.1.0') is None

    print("Tests passed!")
except Exception as e:
    print(f"Test failed: {e}")
    sys.exit(1)
