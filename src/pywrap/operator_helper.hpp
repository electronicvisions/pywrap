#pragma once

#include <Python.h>
#include <boost/python.hpp>

namespace pywrap {

	boost::python::object comparator_not_implemented(boost::python::object, boost::python::object);

	boost::python::object comparator_ne(boost::python::object self, boost::python::object other);

	boost::python::object comparator_ge(boost::python::object self, boost::python::object other);

	boost::python::object comparator_gt(boost::python::object self, boost::python::object other);

	boost::python::object comparator_le(boost::python::object self, boost::python::object other);

} // end namespace pywrap

