import forge
import functools
from unittest import TestCase
import flux
from flux import timeline as timeline_module
from flux.sequence import Sequence

class TimelineTestBase(TestCase):
    def setUp(self):
        super(TimelineTestBase, self).setUp()
        self.timeline = timeline_module.Timeline()
        self.timeline.set_time_factor(0)

class TimelineAPITest(TimelineTestBase):
    def test__time_does_not_progress(self):
        self.assertEquals(self.timeline.time(), self.timeline.time())
    def test__sleep(self):
        start_time = self.timeline.time()
        sleep_time = 6.5
        self.timeline.sleep(sleep_time)
        self.assertEquals(self.timeline.time(), start_time + sleep_time)
    def test__sleep_wait_all_scheduled(self):
        start_time = self.timeline.time()
        self.timeline.schedule_callback(100, setattr, self, "called1", True)
        self.timeline.schedule_callback(200, setattr, self, "called2", True)
        self.timeline.sleep_wait_all_scheduled()
        self.assertEquals(self.timeline.time(), start_time + 200)
        self.assertTrue(self.called1)
        self.assertTrue(self.called2)
    def test__cannot_sleep_negative_seconds(self):
        with self.assertRaises(ValueError):
            self.timeline.sleep(-0.1)
    def test__cannot_sleep_negative_time_factor(self):
        with self.assertRaises(ValueError):
            self.timeline.set_time_factor(-0.1)
    def test__cannot_schedule_negative_delay(self):
        with self.assertRaises(ValueError):
            self.timeline.schedule_callback(-0.1, lambda : None)
    def test__cannot_set_past_time(self):
        self.timeline.set_time(self.timeline.time() + 10)
        with self.assertRaises(ValueError):
            self.timeline.set_time(self.timeline.time() - 1)

class TimeFactorTest(TestCase):
    def setUp(self):
        super(TimeFactorTest, self).setUp()
        self._time = 1337.0
        self._callback_calls = []
        self.forge = forge.Forge()
        self.forge.replace_with(timeline_module, "_real_time", self.time)
        self.forge.replace_with(timeline_module, "_real_sleep", self.sleep)
        self.timeline = timeline_module.Timeline()
    def tearDown(self):
        self.forge.restore_all_replacements()
        self.forge.verify()
        self.forge.reset()
        super(TimeFactorTest, self).tearDown()
    def callback(self):
        self._callback_calls.append(self.timeline.time())
    def time(self):
        return self._time
    def sleep(self, seconds):
        assert seconds >= 0
        self._time += seconds
    def test__default_factor(self):
        start_time = self.timeline.time()
        self.sleep(10)
        self.assertEquals(self.timeline.time(), start_time + 10)
    def test__scheduled_callbacks(self):
        start_time = self.timeline.time()
        schedule_delay = 5
        schedule_time = start_time + schedule_delay
        self.timeline.schedule_callback(schedule_delay, self.callback)
        self.sleep(10)
        # need to trigger the callbacks
        self.timeline.sleep(0)
        self.assertEquals(self.timeline.time(), start_time + 10)
        self.assertEquals(self._callback_calls, [schedule_time])
    def test__factor_change(self):
        expected_time = self.timeline.time()
        for index, (factor, sleep) in enumerate([
            (1, 20),
            (2.5, 3),
            (0.5, 70),
            ]):
            vtime_before_factor_change = self.timeline.time()
            self.timeline.set_time_factor(factor)
            vtime_after_factor_change = self.timeline.time()
            self.assertEquals(vtime_before_factor_change, vtime_after_factor_change, "set_time_factor() unexpectedly changed virtual time!")
            self.sleep(sleep)
            expected_time += (sleep * factor)
            self.assertEquals(expected_time, self.timeline.time(), "Sleep #{} did not sleep as expected".format(index))

class ScheduleTest(TimelineTestBase):
    def setUp(self):
        super(ScheduleTest, self).setUp()
        self.start_time = self.timeline.time()
        self.sleep_time = 10
        self.called_count = 0
        self.called_time = None
        self.timeline.schedule_callback(self.sleep_time, self.callback)
    def callback(self):
        self.called_count += 1
        self.called_time = self.timeline.time()
    def tearDown(self):
        self.assertEquals(self.called_count, 1)
        self.assertEquals(self.called_time, self.start_time + self.sleep_time)
        super(ScheduleTest, self).tearDown()
    def test__one_sleep(self):
        self.timeline.sleep(self.sleep_time)
    def test__several_sleeps(self):
        for i in range(3):
            self.timeline.sleep(self.sleep_time / 4)
            self.assertEquals(self.called_count, 0)
        self.timeline.sleep(self.sleep_time)
    def test__advance_time(self):
        dest_time = self.start_time + self.sleep_time * 10
        self.timeline.set_time(dest_time)
        self.assertEquals(self.timeline.time(), dest_time)
        self.assertEquals(self.called_count, 0)
        self.timeline.sleep(0)

class ScheduleSequenceTest(TimelineTestBase):
    class MySequence(Sequence):
        def __init__(self, test, num_steps):
            super(ScheduleSequenceTest.MySequence, self).__init__()
            self.test = test
            self.num_steps = num_steps
        def _run(self):
            for i in range(1, self.num_steps + 1):
                yield self.sleep(i)
                self.test.value = i
    def setUp(self):
        super(ScheduleSequenceTest, self).setUp()
        self.num_steps = 10
        self.value = 0
        self.seq = self.MySequence(self, self.num_steps)
        self.assertFalse(self.seq.is_running())
        self.seq.run(self.timeline)
        self.assertTrue(self.seq.is_running())
    def tearDown(self):
        self.assertFalse(self.seq.is_running())
        super(ScheduleSequenceTest, self).tearDown()
    def test__schedule_sequence(self):
        for i in range(1, self.num_steps + 1):
            self.assertEquals(self.value, i - 1)
            self.timeline.sleep(i - 1)
            self.assertEquals(self.value, i - 1)
            self.timeline.sleep(1)
            self.assertEquals(self.value, i)
    def test__schedule_sequence_and_interrupt(self):
        for i in range(1, self.num_steps - 1):
            self.timeline.sleep(i)
        self.assertEquals(self.value, i)
        self.assertTrue(self.seq.is_running())
        self.seq.stop()
        self.timeline.sleep(i + 1)
        self.assertEquals(self.value, i)

class CurrentTimeLineTest(TestCase):

    def test__current_timeline_available(self):
        self.assertIsInstance(flux.current_timeline, timeline_module.Timeline)
        self.assertIsNot(type(flux.current_timeline), timeline_module.Timeline)

    def test__current_timeline_replacing(self):
        self.addCleanup(flux.current_timeline.set, flux.current_timeline.get)
        new_timeline = timeline_module.Timeline()
        new_factor = 12345
        flux.current_timeline.set(new_timeline)
        flux.current_timeline.set_time_factor(new_factor)
        self.assertEquals(flux.current_timeline.get_time_factor(), new_factor)
        self.assertEquals(new_timeline.get_time_factor(), new_factor)
