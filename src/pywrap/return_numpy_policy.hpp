#pragma once

#include <boost/python.hpp>
#include <boost/make_shared.hpp>

#include "pyublas/numpy.hpp"

namespace pywrap {

template<typename T>
struct is_std_vector : boost::false_type {};

template<typename T>
struct is_std_vector<std::vector<T> > : boost::true_type {};

template<typename T>
struct convert_to_numpy;

template<typename T>
struct convert_to_numpy< std::vector<T> >
{
	typedef pyublas::numpy_vector<T> numpy_type;

	inline PyObject * operator()(std::vector<T> && v) const
	{
		auto v_ptr = boost::make_shared< std::vector<T> >(std::move(v));
		boost::python::object obj(boost::static_pointer_cast<void>(v_ptr));

		npy_intp dims[] = { static_cast<npy_intp>(v_ptr->size()) };
		PyObject * numpy = PyArray_SimpleNewFromData(
				1, // dimensions
				dims, // shape
				pyublas::get_typenum(T()),
				reinterpret_cast<void*>(v_ptr->data())
		);
		PyArray_SetBaseObject((PyArrayObject*)numpy, boost::python::incref(obj.ptr()));
        return numpy;
	}

	PyTypeObject const *get_pytype() const {
		return boost::python::converter::expected_pytype_for_arg<numpy_type>::get_pytype();
	}
};

struct ReturnNumpy
{
	// The boost::python framework calls return_value_policy::apply<T>::type
	template <class T>
	struct apply
	{
		// Typedef that removes any const from the type
		typedef typename boost::remove_const<T>::type non_const_type;

		typedef convert_to_numpy<non_const_type> type;
	};
};

typedef boost::python::return_value_policy<ReturnNumpy> ReturnNumpyPolicy;

} // end namespace pywrap
