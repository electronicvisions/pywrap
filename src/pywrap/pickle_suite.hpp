#pragma once

#include <string>
#include <sstream>
#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/binary_iarchive.hpp>

namespace HMF {
namespace pyplusplus {

// FIXME@CK Fix pickling when pyhton class dict is not empty: #1641
template <typename T>
struct pickle_suite : boost::python::pickle_suite
{
	static boost::python::object
	getstate(boost::python::object pyobj)
	{
		using namespace boost::python;

		if (pyobj.attr("__dict__"))
		{
			std::stringstream err;
			err << "Pickling of wrapped instance of class '"
				<< pyobj.ptr()->ob_type->tp_name
				<< "' with additional python attributes is not supported.\n"
				<< "Added attributes are:\n";

			dict d = extract<dict>(pyobj.attr("__dict__"));
			typedef stl_input_iterator<std::string> iterator;
			for(iterator it(d.keys()), iend; it != iend; ++it) {
				err << "\n - " << *it;
			}
			PyErr_SetString(PyExc_ValueError, err.str().c_str());
			throw_error_already_set();
		}

		T const & obj = extract<T const &>(pyobj)();
		std::ostringstream os;
		{
			boost::archive::binary_oarchive oa(os);
			oa << obj;
		}
		return boost::python::str(os.str());
	}

	static void
	setstate(T & obj, boost::python::object state)
	{
		namespace bp = boost::python;
		std::string st = bp::extract<std::string>(state)();
		std::istringstream is(st);
		boost::archive::binary_iarchive ia(is);
		ia >> obj;
	}

	static bool getstate_manages_dict() { return true; }
};

} // end namespace pyplusplus
} // end namespace HMF
