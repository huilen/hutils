import unittest
import time

from hutils.progressbar import ProgressBar


class TestProgressbar(unittest.TestCase):

    def test_basic(self):
        progressbar = ProgressBar(1000)
        for _ in range(1000):
            progressbar.update()
            time.sleep(.008)
