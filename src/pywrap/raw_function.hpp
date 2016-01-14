#include <boost/python/raw_function.hpp>

/* wrapper lambda function that provides a wrapper to call member functions 'raw'ly
 *
 * Usage:
 * # c is a pyplusplus class wrapper thing
 * c.include_files.extend(['pywrap/raw_function.hpp'])
 * c.add_registration_code('def("functionname",
 *     bp::raw_function(RAW_MEMFUN_WRAPPER(classname, functionname), 1))')
 */
#define RAW_MEMFUN_WRAPPER(CLASS, FUNCTIONNAME)                                                    \
	[](boost::python::tuple args, boost::python::dict kwargs) -> boost::python::object {           \
		CLASS& self = boost::python::extract<CLASS&>(args[0]);                                     \
		return self.FUNCTIONNAME(                                                                  \
		    boost::python::extract<boost::python::tuple>(args.slice(1, boost::python::len(args))), \
		    kwargs);                                                                               \
	}
