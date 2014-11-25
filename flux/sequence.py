class Sequence(object):

    class sleep(object):

        def __init__(self, seconds):
            super(Sequence.sleep, self).__init__()
            self.seconds = seconds
    _running = False

    def run(self, timeline):
        self._running = True
        generator = self._run()
        self._tick(generator, timeline)

    def is_running(self):
        return self._running

    def stop(self):
        self._running = False

    def _run(self):
        raise NotImplementedError()  # pragma: no cover

    def _tick(self, generator, timeline):
        if not self.is_running() or generator is None:
            return
        try:
            action = next(generator)
        except StopIteration:
            self._running = False
            return
        if isinstance(action, self.sleep):
            timeline.schedule_callback(
                action.seconds, self._tick, generator, timeline)
        else:
            raise NotImplementedError()  # pragma: no cover
