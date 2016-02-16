import threading


class Promise(object):

    _queue = Queue()

    def __init__(self):
        self._cond = threading.Condition()
        self._results = {}
        self._index = 0

    def add(self, part, *args, **kwargs):
        index = self._index

        def wrap_part():
            result = part(*args, **kwargs)
            self._cond.acquire()
            self._results[index]['value'] = result
            self._results[index]['executed'] = True
            self._cond.notify_all()
            self._cond.release()

        self._results[index] = {'executed': False, 'value': None}
        self._queue.put(wrap_part)
        self._index += 1

    @property
    def result(self):
        self._cond.acquire()
        while not self.fulfilled():
            self._cond.wait()
        results = sorted(self._results.items(), key=lambda r: r[0])
        return [r[1]['value'] for r in results]

    def fulfilled(self):
        for result in self._results.values():
            if not result['executed']:
                return False
        return True

    @classmethod
    def init(cls, max_threads=1000):
        threads = []
        for idx in range(max_threads):
            def loop():
                while True:
                    part = cls._queue.get()
                    part()
            thread = threading.Thread(target=loop)
            threads.append(thread)
            thread.setDaemon(True)
            thread.start()
