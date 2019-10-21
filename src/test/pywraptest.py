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

    def test_typdefs(self):
        """
        Check cross module typedefs
        """
        from pywrapstdvector import Vector_String
        import pywraptestpypp as t
        self.assertIs(t.String1, Vector_String)
        self.assertIs(t.String1, t.String2)
        self.assertIs(t.String1, t.String3)
        self.assertIs(t.String1, t.String4)

        self.assertIs(t.int_type, int)

    def test_vector(self):
        import pywraptestpypp as t
        import pywrapstdvector
        v_f = pywrapstdvector.Vector_Float()
        v_d = pywrapstdvector.Vector_Double()
        t.test_vector(v_f)
        t.test_vector(v_d)

        self.assertAlmostEqual(v_f[0], 0.7)
        self.assertAlmostEqual(v_d[0], 1.4)

    def test_vector_typedefs(self):
        import pywraptestpypp as t
        import pywrapstdvector

        tds = t.TestVectorTypedefs;

        self.assertIs(tds.Vector_Bool, pywrapstdvector.Vector_Bool)
        self.assertIs(tds.Vector_Float, pywrapstdvector.Vector_Float)
        self.assertIs(tds.Vector_Double, pywrapstdvector.Vector_Double)

    def test_pickle(self):
        import pywraptestpypp as t
        import pickle

        inst = t.WithPickle()
        inst.value = 42
        inst2 = pickle.loads(pickle.dumps(inst))
        self.assertEqual(inst.value, inst2.value)

        inst = t.WithPickle()
        inst.value = 42
        inst.other_value = 13
        inst2 = pickle.loads(pickle.dumps(inst))
        self.assertEqual(inst.value, inst2.value)
        self.assertEqual(inst.other_value, inst2.other_value)

    def test_pickle_cereal(self):
        import pywraptestpypp as t
        import pickle

        inst = t.WithPickleCereal()
        inst.value = 42
        inst2 = pickle.loads(pickle.dumps(inst))
        self.assertEqual(inst.value, inst2.value)

        inst = t.WithPickleCereal()
        inst.value = 42
        inst.other_value = 13
        inst2 = pickle.loads(pickle.dumps(inst))
        self.assertEqual(inst.value, inst2.value)
        self.assertEqual(inst.other_value, inst2.other_value)

    def test_reference_wrapper(self):
        import pywraptestpypp as t
        r = t.RefWrap()
        ints = r.ints()
        self.assertSequenceEqual([42, 42], ints)

    def test_return_optional(self):
        import pywraptestpypp as t
        r = t.ReturnOptional()
        self.assertIsNone(r.test())
        self.assertEqual(42, r.test(42))
        r2 = t.ReturnOptionalB()
        self.assertEqual((42, None), r2.test(21, 21))
        r3 = t.ReturnOptionalC()
        self.assertEqual((45, 3), r3.test(42, 3))


if __name__ == '__main__':
    unittest.main()
