import gevent
from .timeline import Timeline

class GeventTimeline(Timeline):
    _real_sleep = gevent.sleep
    def __init__(self, start_time=None):
        super(GeventTimeline, self).__init__(start_time=start_time)
