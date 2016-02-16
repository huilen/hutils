import threading
import sys
import time

from datetime import timedelta
from string import Template


class ProgressBar(threading.Thread):

    def __init__(self,
                 total,
                 output=sys.stdout,
                 update_interval=1,
                 chunk_size=None):
        super(ProgressBar, self).__init__()
        self.completed = 0
        self.total = total
        self._update_interval = update_interval
        self._last_chunk_time = time.time()
        self._last_chunk_completed = 0
        self.setDaemon(True)
        self.start()

    def update(self, completed=1):
        completed = self.completed + completed
        self._last_chunk_completed += completed - self.completed
        self.completed = completed

    def run(self):
        while True:
            self.print_progress()
            if self.completed == self.total:
                break
            time.sleep(self._update_interval)

    def print_progress(self):
        message = "\r{completed}/{total} ({percentage}%) completed " \
                  "(remain {remain_time})"
        remain_time = self.remain_time
        if remain_time:
            if remain_time != None:
                remain_time = timedelta(seconds=remain_time)
            remain_time = strfdelta(remain_time, '%D days %H:%M:%S')
        sys.stdout.write(message.format(completed=self.completed,
                                        total=self.total,
                                        percentage=self.percentage,
                                        remain_time=remain_time))
        if self.completed == self.total:
            sys.stdout.write("\r")
        sys.stdout.flush()

    @property
    def remain_time(self):
        now = time.time()
        chunk_interval = now - self._last_chunk_time
        remain_time = self._last_chunk_completed / chunk_interval
        remain_time = (self.total / remain_time) if remain_time else None
        if now - self._last_chunk_time > 30:
            self._last_chunk_time = now
            self._last_chunk_completed = 0
        return remain_time

    @property
    def percentage(self):
        return int(self.completed / self.total * 100)


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

