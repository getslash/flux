from .timeline import Timeline

class TimelineWrapper(object):

    def __init__(self, timeline):
        super(TimelineWrapper, self).__init__()
        self._timeline = timeline

    @property
    def __class__(self):
        return Timeline

    def set(self, timeline):
        self._timeline = timeline

    def get(self):
        return self._timeline

def _get_wrapper(method_name):
    def _wrapper(self, *args, **kwargs):
        return getattr(self._timeline, method_name)(*args, **kwargs)
    _wrapper.__name__ = method_name
    return _wrapper

for _method_name in dir(Timeline):
    if not _method_name.startswith("_"):
        setattr(TimelineWrapper, _method_name, _get_wrapper(_method_name))
