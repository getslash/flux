import contextlib
import datetime
import time
import functools
import heapq

class Timeline(object):
    def __init__(self, start_time=None):
        super(Timeline, self).__init__()
        current_time = self._real_time()
        if start_time is None:
            start_time = current_time
        self._forced_time = None
        self._scheduled = []
        self._time_factor = 1
        self._time_correction = TimeCorrection(start_time, current_time)

    def _real_sleep(self, seconds):
        time.sleep(seconds)

    def _real_time(self):
        return time.time()

    def set_time_factor(self, factor):
        """
        Sets the time factor -- the factor by which the virtual time advances compared to the real
        time. If set to 0, this means the virtual time does not progress at all until
        sleeps are performed
        """
        if factor < 0:
            raise ValueError("Cannot set negative time factor")
        self._correct_time()
        self._time_factor = factor

    def get_time_factor(self):
        """
        Retrieves the current time factor
        """
        return self._time_factor

    def freeze(self):
        """
        Shortcut for :func:`.set_time_factor`(0)
        """
        self.set_time_factor(0)

    def _correct_time(self):
        self._time_correction.virtual_time = self.time()
        self._time_correction.real_time = self._real_time()
        self._time_correction.shift = 0 # shift stems from the previous correction...

    def sleep(self, seconds):
        """
        Sleeps a given number of seconds in the virtual timeline
        """
        if seconds < 0:
            raise ValueError("Cannot sleep negative number of seconds")
        if self._time_factor == 0:
            self.set_time(self.time() + seconds)
        else:
            self._real_sleep(seconds / self._time_factor)
        self.trigger_past_callbacks()

    def sleep_wait_all_scheduled(self):
        """
        Sleeps enough time for all scheduled callbacks to occur
        """
        while self._scheduled:
            self.sleep(max(0, self._scheduled[0][0]-self.time()))

    def trigger_past_callbacks(self):
        current_time = self.time()
        while self._scheduled and self._scheduled[0][0] <= current_time:
            call_at_time, callback = heapq.heappop(self._scheduled)
            with self._get_forced_time_context(call_at_time):
                callback()
    def set_time(self, time):
        delta = time - self.time()
        if delta < 0:
            raise ValueError("Cannot set time to the past")
        self._time_correction.shift += delta
    def time(self):
        """
        Gets the virtual time
        """
        if self._forced_time is not None:
            return self._forced_time
        current_time = self._real_time()
        return self._time_correction.virtual_time + self._time_correction.shift + (current_time - self._time_correction.real_time) * self._time_factor
    @contextlib.contextmanager
    def _get_forced_time_context(self, time):
        prev_forced_time = self._forced_time
        self._forced_time = time
        try:
            yield
        finally:
            self._forced_time = prev_forced_time
    def schedule_callback(self, delay, callback, *args, **kwargs):
        if delay < 0:
            raise ValueError("Cannot schedule negative delays")
        item = (self.time() + delay, functools.partial(callback, *args, **kwargs))
        heapq.heappush(self._scheduled, item)
    def __repr__(self):
        return "<Timeline (@{})>".format(datetime.datetime.fromtimestamp(self.time()).ctime())

class TimeCorrection(object):
    """
    Utility class used for keeping records of time shifts or corrections
    """
    def __init__(self, virtual_time, real_time):
        super(TimeCorrection, self).__init__()
        self.virtual_time = virtual_time
        self.real_time = real_time
        self.shift = 0
