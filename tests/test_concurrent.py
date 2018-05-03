# pylint: disable=duplicate-code,protected-access

import unittest

import concurrent

class TestHandler(unittest.TestCase):
    def test_concurrent_has_python_exit(self):
        self.assertIsNotNone(concurrent.futures.thread._python_exit)
        concurrent.futures.thread._python_exit()

if __name__ == '__main__':
    unittest.main()
