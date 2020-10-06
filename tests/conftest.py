from flux.timeline import Timeline
import flux
import pytest
import time

from functools import partial
from forge import Forge


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

    class _Mocked():

        def __init__(self):
            self._time = time.time()

        def time(self):
            return self._time

        def __set_time__(self, value):
            self._time = value

        def __advance__(self, increment=30):
            self._time += increment

    return _Mocked()


@pytest.fixture
def timeline(request):
    request.addfinalizer(partial(flux.current_timeline.set, flux.current_timeline.get()))
    timeline = Timeline()
    flux.current_timeline.set(timeline)
    return timeline
