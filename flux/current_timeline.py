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

