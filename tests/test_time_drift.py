from flux import timeline
import pytest

def test_time_drift_default_factor(forge, mocked_time_module):
    forge.replace_with(timeline, "time", mocked_time_module)
    t = timeline.Timeline()
    assert t.time() == mocked_time_module.time()
    mocked_time_module.__advance__()
    assert t.time() == mocked_time_module.time()

def test_time_drift_change_restore_default_factor(forge, mocked_time_module):
    forge.replace_with(timeline, "time", mocked_time_module)
    t = timeline.Timeline()
    assert t.time() == mocked_time_module.time()
    mocked_time_module.__advance__()
    t.set_time_factor(1.5)
    t.set_time_factor(1)
    mocked_time_module.__advance__()
    assert t.time() == mocked_time_module.time()
