#!/usr/bin/env python
import unittest

class Test_TestA(unittest.TestCase):
    def test_array_operator(self):
        from pywrap_example import A

        obj = A()
        self.assertEqual(obj.a(), 23)
        self.assertEqual(obj.b(), 42.0)

if __name__ == '__main__':
    unittest.main()
