
#include <array>
#include <tr1/array>
#include <boost/array.hpp>

#include "array_conv.hpp"

using std::tr1::array;

typedef array< int, 7u> array_t;

array_t test_array_out()
{
	return {{1,2,3,7,3,2,1}};
}

array_t test_array_in(array_t x)
{
	return x; 
}

typedef array< std::array<int, 3>, 3> complex_array_t;

complex_array_t test_complex_array_out() {
	    return {{{{1,2,3}},{{2,3,4}},{{7,3,2}}}};
}

complex_array_t test_complex_array_in(complex_array_t x) {
	    return x; 
}

typedef array< bool, 7u> bool_array_t;

bool_array_t test_bool_array_out() {
	    return {{true, false, false, true, true, true, false}};
}

bool_array_t test_bool_array_in(bool_array_t x) {
	    return x; 
}

BOOST_PYTHON_MODULE(pyhalbe_test)
{
    using namespace boost::python;

    def("test_array_in",  test_array_in);
    def("test_array_out", test_array_out);
	XArray_from_PyObject< array_t >::reg();

    def("test_complex_array_in",  test_complex_array_in);
    def("test_complex_array_out", test_complex_array_out);
	XArray_from_PyObject< complex_array_t >::reg();

    def("test_bool_array_in",  test_bool_array_in);
    def("test_bool_array_out", test_bool_array_out);
	XArray_from_PyObject< bool_array_t >::reg();
}


