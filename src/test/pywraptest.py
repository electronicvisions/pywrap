#!/usr/bin/env python
import unittest

class Test_Exposer_Utils(unittest.TestCase):
    def test_array_operator(self):
        import pywraptestmodule as test

        bitset = test.MiniBitset12()
        for ii in range(12):
            bitset[ii] = bool(ii % 3)
        for ii in range(12):
            self.assertEqual(bitset[ii], bool(ii % 3))

        y = test.Y()
        for ii in range(12):
            y[ii] = bool(ii % 3)
        for ii in range(12):
            self.assertEqual(y[ii], bool(ii % 3))

        z = test.Z()
        y = z[0]
        self.assertIsInstance(y, test.Y)
        with self.assertRaises(TypeError):
            z[0] = y


    def test_bitset_constructor(self):
        import pywraptestmodule as test
        import numpy as np

        data_sets = [
                [True, False] * 6,
                [True, False, True] * 4,
                [False, True, False, False] * 3,
                [True] * 12,
                [False] * 12,
        ]
        for data in data_sets:
            bitset = test.MiniBitset12(data)
            self.assertEqual( data, [ bitset[ii] for ii in range(12) ] )

            bitset = test.MiniBitset12(np.array(data))
            self.assertEqual( data, [ bitset[ii] for ii in range(12) ] )

    def test_numpy_return_policy(self):
        import pywraptestmodule as test
        import numpy as np

        v = test.makeDoubleVector()
        self.assertIsInstance(v, np.ndarray)
        self.assertEqual(v.dtype, np.float)
        for a, b in zip(v, np.arange(10)):
            self.assertEqual(a, b)

        v = test.makeUShortVector()
        self.assertIsInstance(v, np.ndarray)
        self.assertEqual(v.dtype, np.ushort)
        for a, b in zip(v, np.arange(10, dtype=np.ushort)):
            self.assertEqual(a, b)

if __name__ == '__main__':
    unittest.main()
