"""Tests for parsing Alpine APKINDEX records."""

import unittest

from src.apk import dependency_name, find_package, parse_index


class ApkTests(unittest.TestCase):
    """Check metadata parsing, version selection, and dependency tokens."""

    def setUp(self):
        self.index = "P:demo\nV:1.2-r0\nD:libc>=1 so:ssl\n\n"

    def test_parse_record(self):
        packages = parse_index(self.index)
        self.assertEqual(packages["demo"]["version"], "1.2-r0")
        self.assertEqual(len(packages["demo"]["dependencies"]), 2)

    def test_exact_version(self):
        packages = parse_index(self.index)
        self.assertEqual(find_package(packages, "demo", "1.2-r0")["version"],
                         "1.2-r0")

    def test_wrong_version(self):
        packages = parse_index(self.index)
        with self.assertRaises(LookupError):
            find_package(packages, "demo", "2.0")

    def test_missing_package(self):
        with self.assertRaises(LookupError):
            find_package({}, "missing", "1")

    def test_dependency_expression(self):
        self.assertEqual(dependency_name("libc>=1.2"), "libc")
        self.assertEqual(dependency_name("so:ssl"), "so:ssl")


if __name__ == "__main__":
    unittest.main()
