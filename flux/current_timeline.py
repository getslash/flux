import datetime as _datetime
from .timeline import Timeline

_current = Timeline()

def set(timeline):
    global _current
    _current = timeline

def get():
    return _current

def _get_wrapper(method_name):
    def _wrapper(*args, **kwargs):
        return getattr(_current, method_name)(*args, **kwargs)
    _wrapper.__name__ = method_name
    return _wrapper

for _method_name in dir(Timeline):
    if not _method_name.startswith("_"):
        globals()[_method_name] = _get_wrapper(_method_name)

class datetime(_datetime.datetime):
    @classmethod
    def now(cls):
        if not _current.is_modified():
            return _datetime.datetime.now()
        return _datetime.datetime.fromtimestamp(time())

    @classmethod
    def utcnow(cls):
        if not _current.is_modified():
            return _datetime.datetime.utcnow()
        return _datetime.datetime.utcfromtimestamp(time())

class date(_datetime.date):
    @classmethod
    def today(cls):
        return datetime.now().date()
