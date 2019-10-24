import calendar
import datetime
import functools
import time
import types

import flux
import forge
from flux.sequence import Sequence
from flux.timeline import Timeline

try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase


class TimelineTestBase(TestCase):

    def setUp(self):
        super().setUp()
        self.timeline = self._get_timeline()
        self.timeline.set_time_factor(0)

    def _get_timeline(self):
        return Timeline()


class TimelineAPITest(TimelineTestBase):

    def test__time_does_not_progress(self):
        self.assertEqual(self.timeline.time(), self.timeline.time())

    def test__sleep(self):
        start_time = self.timeline.time()
        sleep_time = 6.5
        self.timeline.sleep(sleep_time)
        self.assertEqual(self.timeline.time(), start_time + sleep_time)

    def test__sleep_wait_all_scheduled(self):
        start_time = self.timeline.time()
        self.timeline.schedule_callback(100, setattr, self, "called1", True)
        self.timeline.schedule_callback(200, setattr, self, "called2", True)
        self.timeline.sleep_wait_all_scheduled()
        self.assertEqual(self.timeline.time(), start_time + 200)
        self.assertTrue(self.called1)
        self.assertTrue(self.called2)

    def test__sleep_stop_first_scheduled_with_scheduled(self):
        start_time = self.timeline.time()
        self.timeline.schedule_callback(100, setattr, self, "called", True)
        self.timeline.sleep_stop_first_scheduled(200)
        assert self.called
        assert self.timeline.time() == start_time + 100

    def test__schedule_functools_partial(self):
        for i in range(5):
            self.timeline.schedule_callback(100 + i, functools.partial(setattr, self, 'counter', i))
        self.timeline.sleep_wait_all_scheduled()
        assert self.counter == i

    def test__sleep_stop_first_scheduled_without_scheduled(self):
        start_time = self.timeline.time()
        self.timeline.sleep_stop_first_scheduled(200)
        assert self.timeline.time() == start_time + 200

    def test__cannot_sleep_negative_seconds(self):
        with self.assertRaises(ValueError):
            self.timeline.sleep(-0.1)

    def test__cannot_sleep_negative_time_factor(self):
        with self.assertRaises(ValueError):
            self.timeline.set_time_factor(-0.1)

    def test__cannot_schedule_negative_delay(self):
        with self.assertRaises(ValueError):
            self.timeline.schedule_callback(-0.1, lambda: None)

    def test__cannot_set_past_time(self):
        self.timeline.set_time(self.timeline.time() + 10)
        current_time = self.timeline.time()
        self.timeline.set_time(self.timeline.time() - 1)
        self.assertEqual(self.timeline.time(), current_time)

    def test__force_set_past_time(self):
        current_time = self.timeline.time()
        self.timeline.set_time(current_time - 10, allow_backwards=True)
        self.assertEqual(self.timeline.time(), current_time - 10)


class TimeFactorTest(TestCase):

    def setUp(self):
        super().setUp()
        self._real_time = self._start_real_time = 1337.0
        self._callback_calls = []
        self._forge_timeline()

    def _forge_timeline(self):
        self.forge = forge.Forge()
        self.forge.replace_with(Timeline, "_real_time", self.time)
        self.forge.replace_with(Timeline, "_real_sleep", self.sleep)
        self.timeline = Timeline()

    def tearDown(self):
        self.forge.restore_all_replacements()
        self.forge.verify()
        self.forge.reset()
        super().tearDown()

    def callback(self):
        self._callback_calls.append(self.timeline.time())

    def time(self):
        return self._real_time

    def sleep(self, seconds):
        assert seconds >= 0
        self._real_time += seconds

    def test__default_factor(self):
        start_time = self.timeline.time()
        self.sleep(10)
        self.assertEqual(self.timeline.time(), start_time + 10)
        self.assertEqual(self._real_time, self._start_real_time + 10)

    def test__scheduled_callbacks(self):
        start_time = self.timeline.time()
        schedule_delay = 5
        schedule_time = start_time + schedule_delay
        self.timeline.schedule_callback(schedule_delay, self.callback)
        self.sleep(10)
        # need to trigger the callbacks
        self.timeline.sleep(0)
        self.assertEqual(self.timeline.time(), start_time + 10)
        self.assertEqual(self._callback_calls, [schedule_time])

    def test__factor_changes_real_sleeps(self):
        self._test__factor_changes(real_sleep=True)

    def test__factor_changes_fake_sleeps(self):
        self._test__factor_changes(real_sleep=False)

    def test__freeze(self):
        self.timeline.freeze()
        self.assertEqual(self.timeline.get_time_factor(), 0)

    def _test__factor_changes(self, real_sleep):
        expected_virtual_time = self.timeline.time()
        expected_real_time = self._real_time
        for index, (factor, sleep) in enumerate([
            (1, 20),
            (2.5, 3),
            (0.5, 70),
            (0, 30),
        ]):
            vtime_before_factor_change = self.timeline.time()
            self.timeline.set_time_factor(factor)
            vtime_after_factor_change = self.timeline.time()
            self.assertEqual(
                vtime_before_factor_change, vtime_after_factor_change,
                "set_time_factor() unexpectedly changed virtual time!")
            if real_sleep:
                self.sleep(sleep)
                expected_virtual_time += (sleep * factor)
                expected_real_time += sleep
            else:
                self.timeline.sleep(sleep)
                expected_virtual_time += sleep
                if factor != 0:
                    expected_real_time += sleep / factor
            self._assert_equals(expected_virtual_time, self.timeline.time(),
                                "Sleep {0}X{1} did not sleep virtual time as expected".format(sleep, factor))
            self._assert_equals(expected_real_time, self._real_time,
                                "Sleep {0}X{1} did not sleep real time as expected".format(sleep, factor))

    def _assert_equals(self, a, b, msg):
        assert a == b, "{0} ({1} != {2})".format(msg, a, b)


class ScheduleTest(TimelineTestBase):

    def setUp(self):
        super().setUp()
        self.start_time = self.timeline.time()
        self.sleep_time = 10
        self.called_count = 0
        self.called_time = None
        self.timeline.schedule_callback(self.sleep_time, self.callback)

    def callback(self):
        self.called_count += 1
        self.called_time = self.timeline.time()

    def tearDown(self):
        self.assertEqual(self.called_count, 1)
        self.assertEqual(self.called_time, self.start_time + self.sleep_time)
        super().tearDown()

    def test__one_sleep(self):
        self.timeline.sleep(self.sleep_time)

    def test__several_sleeps(self):
        for i in range(3):
            self.timeline.sleep(self.sleep_time / 4)
            self.assertEqual(self.called_count, 0)
        self.timeline.sleep(self.sleep_time)

    def test__advance_time(self):
        dest_time = self.start_time + self.sleep_time * 10
        self.timeline.set_time(dest_time)
        self.assertEqual(self.timeline.time(), dest_time)
        self.assertEqual(self.called_count, 0)
        self.timeline.sleep(0)


class ScheduleSequenceTest(TimelineTestBase):

    class MySequence(Sequence):

        def __init__(self, test, num_steps):
            super().__init__()
            self.test = test
            self.num_steps = num_steps

        def _run(self):
            self.test.value = 0
            for i in range(1, self.num_steps + 1):
                yield self.sleep(i)
                self.test.value = i

    def setUp(self):
        super().setUp()
        self.num_steps = 10
        self.value = None
        self.seq = self.MySequence(self, self.num_steps)
        self.assertFalse(self.seq.is_running())
        self.seq.run(self.timeline)
        self.assertTrue(self.seq.is_running())

    def tearDown(self):
        self.assertFalse(self.seq.is_running())
        super().tearDown()

    def test__schedule_sequence(self):
        for i in range(1, self.num_steps + 1):
            self.assertEqual(self.value, i - 1)
            self.timeline.sleep(i - 1)
            self.assertEqual(self.value, i - 1)
            self.timeline.sleep(1)
            self.assertEqual(self.value, i)

    def test__schedule_sequence_and_interrupt(self):
        for i in range(1, self.num_steps - 1):
            self.timeline.sleep(i)
        self.assertEqual(self.value, i)
        self.assertTrue(self.seq.is_running())
        self.seq.stop()
        self.timeline.sleep(i + 1)
        self.assertEqual(self.value, i)


class CurrentTimeLineTest(TestCase):

    def test__current_timeline_available(self):
        self.assertIs(type(flux.current_timeline), types.ModuleType)

    def test__current_timeline_replacing(self):
        self.addCleanup(flux.current_timeline.set, flux.current_timeline.get())
        new_timeline = Timeline()
        new_factor = 12345
        flux.current_timeline.set(new_timeline)
        flux.current_timeline.set_time_factor(new_factor)
        self.assertEqual(flux.current_timeline.get_time_factor(), new_factor)
        self.assertEqual(new_timeline.get_time_factor(), new_factor)


class DatetimeTest(TimelineTestBase):

    def setUp(self):
        super().setUp()
        self.addCleanup(flux.current_timeline.set, flux.current_timeline.get())
        flux.current_timeline.set(self.timeline)

    def test__datetime_now(self):
        now = flux.current_timeline.datetime.now()
        self.assertIsInstance(now, datetime.datetime)
        self.assertEqual(now.timetuple(), datetime.datetime.fromtimestamp(
            flux.current_timeline.time()).timetuple())

    def test__datetime_utcnow(self):
        now = flux.current_timeline.datetime.utcnow()
        timestamp = calendar.timegm(now.utctimetuple())
        self.assertEqual(now.utctimetuple(),
                          time.gmtime(flux.current_timeline.time()))

    def test__datetime_date_today(self):
        now = flux.current_timeline.datetime.now()
        today = flux.current_timeline.date.today()
        self.assertIsInstance(now, datetime.date)
        self.assertEqual(now.date(), today)
