import unittest
from smfr import parse, validate, compare, IncomparableVersions


class TestSMFR(unittest.TestCase):
    def test_valid(self):
        for version in ("P1", "B2", "S3", "S2G", "S2.9", "S2.12", "S2.12A", "S2G.12Z", "S100.1000"):
            with self.subTest(version=version):
                self.assertTrue(validate(version))
                self.assertEqual(str(parse(version)), version)

    def test_invalid(self):
        for version in ("P0", "S01", "S1.0", "S1.01", "S1.1AA", "S1AB.2", "s1", "S1.2a", "S1.1.2", "S1.2 ", "vS1"):
            with self.subTest(version=version):
                self.assertFalse(validate(version))

    def test_comparisons(self):
        for old, new in (("S2.9", "S2.12"), ("S2.12", "S2.12A"), ("S2.12A", "S2.12B"), ("S2.12B", "S2.13"), ("P2.5", "B2.5"), ("B2.5", "S2.5"), ("S2.4", "P2.5")):
            with self.subTest(old=old, new=new):
                self.assertEqual(compare(old, new), -1)
                self.assertEqual(compare(new, old), 1)
        self.assertEqual(compare("S1.1", "S1.1"), 0)

    def test_track_isolation(self):
        with self.assertRaises(IncomparableVersions):
            compare("S2G.1", "S2N.1")

    def test_warnings_not_invalid(self):
        self.assertTrue(validate("S100.1000"))
        self.assertEqual(len(parse("S100.1000").warnings), 2)


if __name__ == "__main__":
    unittest.main()
