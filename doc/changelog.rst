Changelog
=========

* :feature:`-` Use GitHub actions (instead of Travis CI)
* :feature:`-` Use ``pyproject.toml`` for project's metadata
* :feature:`-` Support asyncio sleep for Timeline
* :feature:`-` Update supported python versions (>= 3.6)
* :feature:`12` Drop support for python version < 3.5

* :release:`1.3.5 <17-12-2018>`
* :bug:`-` Timeline now()/utcnow() - defer to default behavior if timeline is not modified
* :bug:`11` Handle time drifts when time factor hasn't been changed
* :bug:`-` Move to pbr
* :bug:`-` Update Travis deployment

* :release:`1.3.4 <21-01-2016>`
* :bug:`-` Patch utcnow in timeline

* :release:`1.3.3 <19-11-2015>`
* :bug:`-` Add Python 3.5
* :bug:`-` Ensure gevent switch on sleep

* :release:`1.3.2 <16-09-2015>`
* :bug:`-` Add python 2.6 support again

* :release:`1.3.1 <16-09-2015>`
* :bug:`-` Fix sleep behavior for short time factors

* :release:`1.3.0 <29-12-2014>`
* :feature:`-` Add ``allow_backwards`` argument to ``set_time``, to allow setting the time to the past
* :feature:`6` Document ``sleep_wait_all_scheduled``

* :release:`1.2.4 <22-07-2014>`
* :bug:`5` Fix Python 3 compatibility
* :bug:`-` Add Python 3.4 to tox and travis

* :release:`1.2.3 <17-04-2014>`
* :bug:`-` Set time backwards might happen in threaded environments

* :release:`1.2.2 <16-04-2014>`
* :bug:`-` fail properly for non-number seconds
* :bug:`-` Add ``timeline.sleep_stop_first_scheduled``

* :release:`1.2.1 <16-02-2014>`
* :bug:`-` Sequences: immediately trigger the beginning of the sequence generator upon registration

* :release:`1.2.0 <13-02-2014>`
* :feature:`-` Factor 0 requires an implicit gevent switch
* :feature:`-` Add gevent supported timeline
* :feature:`1` datetime mocking
* :feature:`-` Make ``current_timeline`` a module

* :release:`1.1.0 <01-08-2013>`
* :feature:`-` Perform sleeps according to the currently configured factor
* :feature:`-` Documentation

* :release:`1.0.0 <31-07-2013>`
* :feature:`-` Restore python 2.6 support
* :feature:`-` Add ``current_timeline`` wrapper
* :bug:`- major` Fix sleep behavior
