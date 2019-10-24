import flux
import forge
from flux.gevent_timeline import GeventTimeline
from .test__timeline import TimeFactorTest, CurrentTimeLineTest, DatetimeTest, ScheduleSequenceTest, ScheduleTest, TimelineAPITest

class GeventTimeFactorTest(TimeFactorTest):
    def _forge_timeline(self):
        self.forge = forge.Forge()
        self.forge.replace_with(GeventTimeline, "_real_time", self.time)
        self.forge.replace_with(GeventTimeline, "_real_sleep", self.sleep)
        self.timeline = GeventTimeline()

class GeventCurrentTimeLineTest(CurrentTimeLineTest):
    def setUp(self):
        super().setUp()
        timeline = GeventTimeline()
        self.addCleanup(flux.current_timeline.set, flux.current_timeline.get())
        flux.current_timeline.set(timeline)

class GeventScheduleSequenceTest(ScheduleSequenceTest):
    def _get_timeline(self):
        return GeventTimeline()

class GeventDatetimeTest(DatetimeTest):
    def _get_timeline(self):
        timeline = GeventTimeline()
        self.addCleanup(flux.current_timeline.set, flux.current_timeline.get())
        flux.current_timeline.set(timeline)
        return timeline

class GeventScheduleTest(ScheduleTest):
    def _get_timeline(self):
        return GeventTimeline()

class GeventTimelineAPITest(TimelineAPITest):
    def _get_timeline(self):
        return GeventTimeline()
