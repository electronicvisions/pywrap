import unittest, time, numpy
import pywrapstdvector
import pywraptestconverter

class ConverterTest(unittest.TestCase):

    def setUp(self):
        self.myList = range(5,20)
        self.sizeLongList = int(1e6)
        self.aLongList = range(self.sizeLongList)
        self.aLongVector = pywrapstdvector.Vector_Double(self.aLongList)
        self.aLongNumpyArray = numpy.array([float(x) for x in self.aLongList])

    def callit(self, data):
        cls = pywraptestconverter.ConverterTest()
        return cls.sink(data)

    def test_list(self):
        self.callit(self.myList)

    def test_Vector_Double(self):
        self.callit(pywrapstdvector.Vector_Double(self.myList))

    def test_speedIterVsPlain(self):
        start = time.time()
        for i in xrange(10):
            self.assertEqual(self.callit(self.aLongList), self.sizeLongList)
        runtime_PyIter = time.time()  - start

        start = time.time()
        for i in xrange(10):
            self.assertEqual(self.callit(self.aLongVector), self.sizeLongList)
        runtime_Vector = time.time()  - start

        # I guess that passing down C++ data shold be at least 10 times faster
        self.assertLess(runtime_Vector * 10, runtime_PyIter)

        # now test if numpy converter is still ok
        start = time.time()
        for i in xrange(10):
            self.assertEqual(self.callit(self.aLongNumpyArray), self.sizeLongList)
        runtime_NumpyArray = time.time()  - start

        # Numpy should be also at least as fast as C++
        self.assertLess(runtime_NumpyArray, runtime_Vector)

        print "PyIter took %.3fs" % runtime_PyIter
        print "Vector took %.3fs" % runtime_Vector
        print "NumpyArray took %.3fs" % runtime_NumpyArray

    def test_nonIterable(self):
        for T in pywrapstdvector.__dict__.keys():
            if T == "Vector_Double":
                continue
            elif T == 'Vector_String':
                with self.assertRaises(TypeError):
                    self.callit(getattr(pywrapstdvector, T)(self.myList))
            elif T.startswith('Vector_'):
                with self.assertRaises(AttributeError):
                    self.callit(getattr(pywrapstdvector, T)(self.myList))

if __name__ == '__main__':
        unittest.main()
