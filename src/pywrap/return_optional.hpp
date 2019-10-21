#pragma once

#include <boost/optional.hpp>
#include <boost/tuple/tuple.hpp>
#include <boost/type_traits/remove_cv.hpp>
#include <boost/type_traits/remove_reference.hpp>
#include <boost/python/object.hpp>
#include <boost/python/refcount.hpp>
#include <boost/python/tuple.hpp>

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

template <typename T>
struct optional_to_python_value<boost::tuple<boost::optional<T>, boost::optional<T> > >
{
	/**
	 * @brief Return object of type \c T contained in \c boost::optional or \c None.
	 */
	PyObject* operator()(boost::tuple<boost::optional<T>, boost::optional<T> > const& to) const
	{
		boost::python::object r1 =
			boost::get<0>(to) ? boost::python::object(*(boost::get<0>(to))) : boost::python::object();
		boost::python::object r2 =
			boost::get<1>(to) ? boost::python::object(*(boost::get<1>(to))) : boost::python::object();

		return boost::python::incref(boost::python::make_tuple(r1, r2).ptr());
	}

	PyTypeObject const* get_pytype() const
	{
		return nullptr;
	}
}; // optional_to_python_value (tuple of optionals)

template <typename T>
struct optional_to_python_value<boost::tuple<T, boost::optional<T> > >
{
	/**
	 * @brief Return object of type \c T contained in \c boost::optional or \c None.
	 */
	PyObject* operator()(boost::tuple<T, boost::optional<T> > const& to) const
	{
		boost::python::object r1 = boost::python::object(boost::get<0>(to));
		boost::python::object r2 =
			boost::get<1>(to) ? boost::python::object(*(boost::get<1>(to))) : boost::python::object();

		return boost::python::incref(boost::python::make_tuple(r1, r2).ptr());
	}

	PyTypeObject const* get_pytype() const
	{
		return nullptr;
	}
}; // optional_to_python_value (tuple of type and optional)

} // namespace detail

struct return_optional_by_value {
	template <typename R>
	struct apply {
		typedef detail::optional_to_python_value<
		    typename boost::remove_cv<typename boost::remove_reference<R>::type>::type>
			type;
	}; // apply
}; // return_optional_by_value
