import unittest
from scripts.githelper import http_url, ssh_url, from_url

class TestGitHelper(unittest.TestCase):
    def test_http_url(self):
        """Test http_url returns correct HTTP URL."""
        self.assertEqual(http_url("user/repo"), "https://github.com/user/repo.git")

    def test_ssh_url(self):
        """Test ssh_url returns correct SSH URL."""
        self.assertEqual(ssh_url("user/repo"), "git@github.com:user/repo.git")

    def test_from_url_http(self):
        """Test from_url correctly parses HTTP URL."""
        url = "https://github.com/user/repo.git"
        self.assertEqual(from_url(url), "user/repo")

    def test_from_url_ssh(self):
        """Test from_url correctly parses SSH URL."""
        url = "git@github.com:user/repo.git"
        self.assertEqual(from_url(url), "user/repo")

    def test_round_trip_http(self):
        """Test http_url -> from_url round trip."""
        repo = "user/repo"
        self.assertEqual(from_url(http_url(repo)), repo)

    def test_round_trip_ssh(self):
        """Test ssh_url -> from_url round trip."""
        repo = "user/repo"
        self.assertEqual(from_url(ssh_url(repo)), repo)

    def test_from_url_invalid(self):
        """Test from_url handles invalid URLs gracefully."""
        self.assertIsNone(from_url("invalid"))
        self.assertIsNone(from_url("https://gitlab.com/user/repo.git"))
        # URLs without .git extension
        self.assertIsNone(from_url("https://github.com/user/repo"))

if __name__ == "__main__":
    unittest.main()
