#pragma once

#include <string>
#include <sstream>
#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>

namespace HMF {
namespace pyplusplus {

template <typename T, typename iarchive, typename oarchive>
struct pickle_suite : boost::python::pickle_suite {

	static boost::python::object getstate(boost::python::object pyobj) {
		namespace bp = boost::python;
		T const & obj = bp::extract<T const &>(pyobj)();
		std::ostringstream os;

		{
			oarchive oa(os);
			oa << obj;
		}
		bp::object tmp(bp::handle<>(PyBytes_FromStringAndSize(
		    os.str().c_str(),
		    static_cast<Py_ssize_t>(os.str().size())
		)));

		if (pyobj.attr("__dict__")) {
			return boost::python::make_tuple(
				tmp,
				pyobj.attr("__dict__")
			);
		}
		return tmp;
	}

	static void setstate(boost::python::object obj, boost::python::object state) {
		namespace bp = boost::python;
		if (!bp::extract<bp::tuple>(state).check()) {
			// deserializing into C++ object (w/o Python __dict__)
			std::string st = bp::extract<std::string>(state);
			std::istringstream is(st);
			iarchive ia(is);
			auto& obj_cpp = bp::extract<T&>(obj)(); // FIXME: add check?
			ia >> obj_cpp;
			return;
		}

		auto tuple = bp::extract<bp::tuple>(state)();
		if ((bp::len(tuple) != 2)) {
			std::stringstream err;
			err << "Expected scalar or 2-item tuple in scall to __setstate__; got: "
				<< bp::len(tuple) << "\n";
			PyErr_SetString(PyExc_ValueError, err.str().c_str());
			bp::throw_error_already_set();
		}

		// restore the C++ state
		std::string st = bp::extract<std::string>(tuple[0])();
		std::istringstream is(st);
		iarchive ia(is);
		auto& obj_cpp = bp::extract<T&>(obj)(); // FIXME: add check?
		ia >> obj_cpp;
		// restore python's __dict__
		bp::dict d = bp::extract<bp::dict>(obj.attr("__dict__"))();
		d.update(tuple[1]);
	}

	static bool getstate_manages_dict() { return true; }
};

} // namespace pyplusplus
} // namespace HMF
