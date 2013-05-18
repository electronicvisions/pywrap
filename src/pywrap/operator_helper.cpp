#include "pywrap/operator_helper.hpp"

namespace pywrap {
	namespace bp = boost::python;

	bp::object comparator_not_implemented(bp::object, bp::object)
	{
		PyErr_SetString(PyExc_NotImplementedError,
			"This comparator has not been implemented in the C++ interface.");
		bp::throw_error_already_set();
		return bp::object();
	}

	bp::object comparator_ne(bp::object self, bp::object other)
	{
		return bp::object(!(self == other));
	}

	bp::object comparator_ge(bp::object self, bp::object other)
	{
		return bp::object(!(self < other));
	}

	bp::object comparator_gt(bp::object self, bp::object other)
	{
		return bp::object(!(self == other || self < other));
	}

	bp::object comparator_le(bp::object self, bp::object other)
	{
		return bp::object((self == other || self < other));
	}

} // end namespace pywrap

