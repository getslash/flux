from unittest import TestCase
import os
import doctest

class _FakeTimeModule():
    def time(self):
        return 0
    def sleep(self, seconds):
        pass

class ReadMeDocTest(TestCase):
    def test__readme_doctests(self):
        readme_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "README.md"))
        self.assertTrue(os.path.exists(readme_path))
        result = doctest.testfile(readme_path, module_relative=False, globs=dict(time=_FakeTimeModule()))
        self.assertEqual(result.failed, 0, "%s tests failed!" % result.failed)
