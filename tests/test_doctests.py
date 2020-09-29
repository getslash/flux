import doctest
import os

import pytest

_HERE = os.path.abspath(os.path.dirname(__file__))
_DOCS_ROOT = os.path.abspath(os.path.join(_HERE, "..", "doc"))


def test_doctests(doctest_path):
    assert os.path.exists(doctest_path)
    globs = {'pytest': pytest}
    result = doctest.testfile(doctest_path, module_relative=False, globs=globs)
    assert result.failed == 0


assert os.path.exists(_DOCS_ROOT)
_DOCTEST_PATHS = list(os.path.join(path, filename)
                      for path, _, filenames in os.walk(_DOCS_ROOT)
                      for filename in filenames
                      if filename.endswith(".rst"))
_README_PATH = os.path.join(_HERE, '..', 'README.md')


@pytest.fixture(name="doctest_path", params=_DOCTEST_PATHS + [_README_PATH])
def doctest_path_fixture(request):
    return request.param
