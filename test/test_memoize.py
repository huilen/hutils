import time
import unittest

from unittest.mock import Mock

from hutils.memoize import memoized


class TestMemoized(unittest.TestCase):

    def test_same_parameters(self):
        calculate = Mock(wraps=self._get_calculate())

        result = calculate(1, 1)
        self.assertEqual(result, 2)

        result = calculate(1, 1)
        self.assertEqual(result, 2)

        self.assertEqual(self._called_count, 1)

    def test_different_parameters(self):
        calculate = Mock(wraps=self._get_calculate())

        result = calculate(1, 1)
        self.assertEqual(result, 2)

        result = calculate(1, 2)
        self.assertEqual(result, 3)

        self.assertEqual(self._called_count, 2)

    def _get_calculate(self):
        self._called_count = 0
        now = time.time()
        @memoized('/tmp/calculate_{now}_{hash}'.format(
            now=now, hash='{hash}'))
        def _calculate(a, b):
            self._called_count += 1
            return a + b
        return _calculate
