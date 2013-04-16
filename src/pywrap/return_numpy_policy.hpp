#pragma once

#include <boost/python.hpp>
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

	inline PyObject * operator()(const std::vector<T> & v) const
	{
        numpy_type * numpy = new numpy_type(v.size());
		std::copy(v.begin(), v.end(), numpy->begin());
        return boost::python::incref(boost::python::object(numpy).ptr());
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
