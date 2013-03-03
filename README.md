# What is Flux?
Flux is a Python library enabling you to create virtual timelines and use them to test long processes.

The need for Flux is realized if you think about testing a code like the following:

	def long_running_func():
	    start_time = time.time()
	    while not some_predicate():
	        if time.time() - start_time > (60 * 60 * 24):
			    LOG("This has been over a day now!!!")
				notify_long_wait()
			time.sleep(30)

Let's say you have a test case in place that makes sure the notification function gets triggered after one day of waiting. How do you test it?

The obvious reason is mocking the time module. However, even with mocking tools you still have to fiddle your way around the time logic to test this elegantly. You don't want to record/replay the amount of sleeps that take place, so that your test doesn't break for every change in the sleep policy. You need something that would let you express the case you're trying to achieve. Flux does just that.

Flux contains the `Timeline` class. This class lets you mock time progression, and optionally lets you register callbacks when a virtual time is reached:

	>>> from flux import Timeline
	>>> t = Timeline()

`Timeline.time()` behaves just like `time.time()`, only returning the virtual time. It also lets you set the

	>>> virtual_start_time = t.time()

`Timeline.set_time_factor` sets the *time factor*, or in other words, the ratio between the real world time and the virtual time. A factor of 1 would mean that the virtual timeline progresses just like the real world time. A factor of 1000 means it progresses 1000 times faster, etc.

A factor of zero is especially interesting for testing, since it freezes time altogether:

	>>> t.set_time_factor(0)

`Timeline.sleep()` behaves just like time.sleep(), advancing the virtual time. For a time factor of zero, this is the only way to advance the time. This is important for testing since it exposes race conditions and code that does not properly wait on conditions and works "by chance":

	>>> virtual_start_time = t.time()
	>>> t.sleep(10)
	>>> t.time() == virtual_start_time + 10
	True

`Timeline.schedule_callback` schedules a function to be called later in the virtual timeline. It is called for you whenever someone sleeps on the virtual timeline.

	>>> def callback():
	...     print("Hello!")
	>>> t.schedule_callback(100, callback)
	>>> t.sleep(99) # nothing happens here
	>>> t.sleep(10)
	Hello!

So coming back to the original code, that's how we'd test it with timeline:


	# the tested code
	def long_running_func(_sleep=time.sleep, _time=time.time):
	    start_time = _time()
	    while not some_predicate():
	        if _time() - start_time > (60 * 60 * 24):
			    LOG("This has been over a day now!!!")
				notify_long_wait()
			_sleep(30)
     
	 # testing code
	 def test():
	     timeline = Timeline()
		 timeline.set_time_factor(0)
		 timeline.schedule_callback((60 * 60 * 24) + 1, _satisfy_predicate)
		 long_running_func(_sleep=timeline.sleep, _time=timeline.time)
		 assert_notified_for_long_wait()
