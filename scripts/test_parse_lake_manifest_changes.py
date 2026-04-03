import unittest
import sys
import os

# Add scripts directory to sys.path to import parse_lake_manifest_changes
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import parse_lake_manifest_changes

class TestParseLakeManifestChanges(unittest.TestCase):
    def test_find_package_changes_no_changes(self):
        old_manifest = {
            "packages": [
                {"name": "pkg1", "rev": "rev1", "url": "url1"}
            ]
        }
        new_manifest = {
            "packages": [
                {"name": "pkg1", "rev": "rev1", "url": "url1"}
            ]
        }
        changes = parse_lake_manifest_changes.find_package_changes(old_manifest, new_manifest)
        self.assertEqual(changes, [])

    def test_find_package_changes_update(self):
        old_manifest = {
            "packages": [
                {"name": "pkg1", "rev": "rev1", "url": "url1"}
            ]
        }
        new_manifest = {
            "packages": [
                {"name": "pkg1", "rev": "rev2", "url": "url1"}
            ]
        }
        changes = parse_lake_manifest_changes.find_package_changes(old_manifest, new_manifest)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0], {
            'type': 'update',
            'dependency': 'pkg1',
            'old_version': 'rev1',
            'new_version': 'rev2',
            'url': 'url1'
        })

    def test_find_package_changes_add(self):
        old_manifest = {
            "packages": [
                {"name": "pkg1", "rev": "rev1", "url": "url1"}
            ]
        }
        new_manifest = {
            "packages": [
                {"name": "pkg1", "rev": "rev1", "url": "url1"},
                {"name": "pkg2", "rev": "rev2", "url": "url2"}
            ]
        }
        changes = parse_lake_manifest_changes.find_package_changes(old_manifest, new_manifest)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0], {
            'type': 'add',
            'dependency': 'pkg2',
            'version': 'rev2',
            'url': 'url2'
        })

    def test_find_package_changes_remove(self):
        old_manifest = {
            "packages": [
                {"name": "pkg1", "rev": "rev1", "url": "url1"},
                {"name": "pkg2", "rev": "rev2", "url": "url2"}
            ]
        }
        new_manifest = {
            "packages": [
                {"name": "pkg1", "rev": "rev1", "url": "url1"}
            ]
        }
        changes = parse_lake_manifest_changes.find_package_changes(old_manifest, new_manifest)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0], {
            'type': 'remove',
            'dependency': 'pkg2',
            'version': 'rev2',
            'url': 'url2'
        })

    def test_find_package_changes_combination(self):
        old_manifest = {
            "packages": [
                {"name": "pkg_keep", "rev": "rev1", "url": "url1"},
                {"name": "pkg_update", "rev": "rev2", "url": "url2"},
                {"name": "pkg_remove", "rev": "rev3", "url": "url3"}
            ]
        }
        new_manifest = {
            "packages": [
                {"name": "pkg_keep", "rev": "rev1", "url": "url1"},
                {"name": "pkg_update", "rev": "rev4", "url": "url2"},
                {"name": "pkg_add", "rev": "rev5", "url": "url5"}
            ]
        }
        changes = parse_lake_manifest_changes.find_package_changes(old_manifest, new_manifest)

        # We expect 3 changes: update, add, remove
        self.assertEqual(len(changes), 3)

        types = [c['type'] for c in changes]
        self.assertCountEqual(types, ['update', 'add', 'remove'])

        update_change = next(c for c in changes if c['type'] == 'update')
        add_change = next(c for c in changes if c['type'] == 'add')
        remove_change = next(c for c in changes if c['type'] == 'remove')

        self.assertEqual(update_change, {
            'type': 'update',
            'dependency': 'pkg_update',
            'old_version': 'rev2',
            'new_version': 'rev4',
            'url': 'url2'
        })
        self.assertEqual(add_change, {
            'type': 'add',
            'dependency': 'pkg_add',
            'version': 'rev5',
            'url': 'url5'
        })
        self.assertEqual(remove_change, {
            'type': 'remove',
            'dependency': 'pkg_remove',
            'version': 'rev3',
            'url': 'url3'
        })

if __name__ == "__main__":
    unittest.main()
