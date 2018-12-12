import time
from forge import Forge
import pytest


@pytest.fixture
def forge(request):

    returned = Forge()

    @request.addfinalizer
    def cleanup():  # pylint: disable=unused-variable
        returned.verify()
        returned.restore_all_replacements()

    return returned


@pytest.fixture
def mocked_time_module():

    class _Mocked(object):

        def __init__(self):
            self._time = time.time()

        def time(self):
            return self._time

        def __set_time__(self, value):
            self._time = value

        def __advance__(self, increment=30):
            self._time += increment

    return _Mocked()
