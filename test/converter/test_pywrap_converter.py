import unittest, time, numpy
import pywrapstdvector
import convertertestmodule

class ConverterTest(unittest.TestCase):

    def setUp(self):
        self.myList = range(5,20)
        self.sizeLongList = int(1e6)
        self.aLongList = range(self.sizeLongList)
        self.aLongVector = pywrapstdvector.Vector_Double(self.aLongList)
        self.aLongNumpyArray = numpy.array([float(x) for x in self.aLongList])

    @staticmethod
    def get_dtype(dtype):
        if dtype == convertertestmodule.int_tag:
            return int
        elif dtype == convertertestmodule.double_tag:
            return float
        else:
            raise RuntimeError("Unexpected data type")

    def callit(self, data):
        cls = convertertestmodule.ConverterTest()
        dtype, size = cls.sink(data)
        return self.get_dtype(dtype), size

    def test_list(self):
        self.callit(self.myList)

    def test_overloads(self):
        dtype, size = self.callit(pywrapstdvector.Vector_Double(self.myList))
        self.assertEqual(size, len(self.myList))
        self.assertEqual(dtype, float)
        dtype, size = self.callit(numpy.array(self.myList, dtype=numpy.double))
        self.assertEqual(size, len(self.myList))
        self.assertEqual(dtype, float)
        dtype, size = self.callit(pywrapstdvector.Vector_Int32(self.myList))
        self.assertEqual(size, len(self.myList))
        self.assertEqual(dtype, int)
        dtype, size = self.callit(numpy.array(self.myList, dtype=numpy.int32))
        self.assertEqual(size, len(self.myList))
        self.assertEqual(dtype, int)

        # Here we except float, because the wrapper is registered first
        dtype, size = self.callit([0.1, 0.2, 0.3, 0.4])
        self.assertEqual(dtype, float)
        dtype, size = self.callit([1, 2, 3, 4])
        self.assertEqual(dtype, float)
        dtype, size = self.callit((1, 2, 3, 4))
        self.assertEqual(dtype, float)

    def verify_double_conversion(self):
        x = numpy.linspace(-5 * numpy.pi, 5 * numpy.pi, 1e5)
        data = numpy.array(numpy.sin(x) * 10, dtype=numpy.double)

        cls = convertertestmodule.ConverterTest()
        self.assertEqual(cls.test_double_sink(data), list(data))
        self.assertEqual(cls.test_double_sink(list(data)), list(data))
        self.assertEqual(cls.test_double_sink(tuple(data)), list(data))

    def verify_int_conversion(self):
        x = numpy.linspace(-5 * numpy.pi, 5 * numpy.pi, 1e5)
        data = numpy.array(numpy.sin(x) * 10, dtype=numpy.int32)

        cls = convertertestmodule.ConverterTest()
        self.assertEqual(cls.test_int_sink(data), list(data))
        self.assertEqual(cls.test_int_sink(list(data)), list(data))
        self.assertEqual(cls.test_int_sink(tuple(data)), list(data))

    def test_speedIterVsPlain(self):
        start = time.time()
        for i in xrange(10):
            dtype, n = self.callit(self.aLongList)
            self.assertEqual(n, self.sizeLongList)
        runtime_PyIter = time.time()  - start

        start = time.time()
        for i in xrange(10):
            dtype, n = self.callit(self.aLongVector)
            self.assertEqual(n, self.sizeLongList)
        runtime_Vector = time.time()  - start

        # I guess that passing down C++ data shold be at least 10 times faster
        self.assertLess(runtime_Vector * 10, runtime_PyIter)

        # now test if numpy converter is still ok
        start = time.time()
        for i in xrange(10):
            dtype, n = self.callit(self.aLongNumpyArray)
            self.assertEqual(n, self.sizeLongList)
        runtime_NumpyArray = time.time()  - start

        # Numpy should be also at least as fast as C++
        self.assertLess(runtime_NumpyArray, runtime_Vector)

        print "PyIter took %.3fs" % runtime_PyIter
        print "Vector took %.3fs" % runtime_Vector
        print "NumpyArray took %.3fs" % runtime_NumpyArray

    def test_nonIterable(self):
        for T in pywrapstdvector.__dict__.keys():
            if T == "Vector_Int32":
                t, _ = self.callit(getattr(pywrapstdvector, T)(self.myList))
                self.assertIs(t, int)
            elif T == "Vector_Double":
                t, _ = self.callit(getattr(pywrapstdvector, T)(self.myList))
                self.assertIs(t, float)
            elif T == 'Vector_String':
                with self.assertRaises(TypeError):
                    self.callit(getattr(pywrapstdvector, T)(self.myList))
            elif T.startswith('Vector_'):
                with self.assertRaises(Exception) as ctx:
                    self.callit(getattr(pywrapstdvector, T)(self.myList))
                self.assertEqual(type(ctx.exception).__name__,
                                 'ArgumentError')

if __name__ == '__main__':
        unittest.main()
