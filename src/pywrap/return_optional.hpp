#pragma once

# include <boost/optional.hpp>
#include <boost/type_traits/remove_cv.hpp>
#include <boost/type_traits/remove_reference.hpp>
#include <boost/python/object.hpp>
#include <boost/python/refcount.hpp>

namespace detail {

template <typename R>
struct optional_to_python_value;

template <typename T>
struct optional_to_python_value<boost::optional<T> >
{
	/**
	 * @brief Return object of type \c T contained in \c boost::optional or \c None.
	 */
	PyObject* operator()(boost::optional<T> const& optional) const
	{
		boost::python::object result =
			optional ? boost::python::object(*optional) : boost::python::object();
		return boost::python::incref(result.ptr());
	}

	PyTypeObject const* get_pytype() const
	{
		return nullptr;
	}
}; // optional_to_python_value

} // namespace detail

struct return_optional_by_value {
	template <typename R>
	struct apply {
		typedef detail::optional_to_python_value<
		    typename boost::remove_cv<typename boost::remove_reference<R>::type>::type>
			type;
	}; // apply
}; // return_optional_by_value
