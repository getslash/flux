from .timeline import Timeline

class GeventTimeline(Timeline):
    try:
        import gevent
        _real_sleep = gevent.sleep
    except ImportError:
        pass # gracefully ignore gevent
