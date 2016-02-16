import random
import time

from hutils.promise import Promise


class TestPromise(unittest.TestCase):

    def test_basic(self):
        threads = 1000
        count = 5000
        delay = 1

        def product(a, b):
            time.sleep(delay)
            return a * b

        promise = Promise()
        elapsed_time = time.time()

        for _ in range(count):
            promise.add(product, 1, 2)

        result = promise.result
        total = reduce(lambda el, acc: el + acc, result)
        self.assertEqual(total, 2 * count)

        elapsed_time = round(time.time() - elapsed_time)
        self.assertEqual(elapsed_time, count / threads * delay)

    def test_order(self):
        promise = Promise()
        expected_result = []
        for i in range(10):
            def number():
                n = random.randint(1, 10)
                expected_result.append(n)
                return n
            promise.add(number)
        self.assertEqual(promise.result, expected_result)
