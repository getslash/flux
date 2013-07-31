from .__version__ import __version__
from .timeline import Timeline
from .timeline_wrapper import TimelineWrapper

current_timeline = TimelineWrapper(Timeline())
