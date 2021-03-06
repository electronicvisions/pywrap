#include <iostream>
#include <array>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>

#include "create_constructor.hpp"

namespace pywrap {

// copied and modified (see below) from http://stackoverflow.com/questions/15842126/
// * support added for conversion to std::array
// * support added for fast from-numpy conversion
// * check (and disables) conversion from boost::python types
//   (i.e. only raw Python-interface types allowed)

/// @brief Class to support Python rvalue conversions from python iterables (i.e.
///        PySequence types) to C++ Container types.
/// @note currently only tested for std's array, list, vector
struct iterable_converter
{
	/// @note Registers converter to "Container" type
	template <typename Container>
	iterable_converter& from_python()
	{
		boost::python::converter::registry::push_back(&iterable_converter::convertible<Container>,
		                                              &iterable_converter::construct<Container>,
		                                              boost::python::type_id<Container>());
		// Support chaining.
		return *this;
	}

	/// @note Check for PySequence and exclude boost::python's own types to
	///       avoid problems when handling function overloads.
	template <typename Container>
	static void* convertible(PyObject* object)
	{
		// std::cerr << "Test convert to " << ztl::typestring<Container>() << std::endl;
		using boost::python::objects::class_type;
		if ((PySequence_Check(object) == 1) &&
		    !PyType_IsSubtype(object->ob_type, class_type().get()))
			return PyObject_GetIter(object);
		return NULL;
	}

	/// Allocate the C++ type into the converter's memory block, and assign
	/// its handle to the converter's convertible variable. The C++
	/// container is populated by passing the begin and end iterators of
	/// the python object to the container's constructor.
	template <typename Container>
	static void inplace_construct(Container * storage,
			                      boost::python::object obj)
	{
		new (storage) Container(boost::python::len(obj));
	}

	/// Version for std::array (i.e. fixed-length) conversion.
	template <typename value_type, size_t size>
	static void inplace_construct(std::array<value_type, size> * storage,
								  boost::python::object obj)
	{
		if (boost::python::len(obj) != size)
		{
			PyErr_SetString(PyExc_TypeError, "Invalid sequence size");
			boost::python::throw_error_already_set();
		}
		new (storage) std::array<value_type, size>();
	}

	/// @brief Convert iterable PyObject (i.e. supporting PySequence) to C++ "Container" type.
	///
	/// Container Concept requirements:
	///
	///   * Container::value_type is CopyConstructable.
	///   * Container can be constructed and populated with two iterators.
	///     I.e. Container(begin, end)
	template <typename Container>
	static void construct(PyObject* raw,
	                      boost::python::converter::rvalue_from_python_stage1_data* data)
	{
		namespace bp = boost::python;
		typedef typename Container::value_type value_type;


		// Object is a borrowed reference, so create a handle indicting it is
		// borrowed for proper reference counting.
		bp::handle<> handle(bp::borrowed(raw));
		bp::object obj(handle);


		// Debug output, could be handy for the next poor soul ;)
		//bp::handle<> obj_type_h(PyObject_Type(raw));
		//bp::object obj_type(obj_type_h);
		//std::string obj_str = bp::extract<std::string>(bp::str(obj));
		//std::string obj_type_str = bp::extract<std::string>(bp::str(obj_type));
		//std::cerr << "construct: " << obj_str << std::endl;
		//std::cerr << "Construct "
		//	      << ztl::typestring<Container>() << " from "
		//	      << obj_type_str << std::endl;


		// Obtain a handle to the memory block that the converter has allocated
		// for the C++ type.
		typedef bp::converter::rvalue_from_python_storage<Container> storage_type;
		void* storage = reinterpret_cast<storage_type*>(data)->storage.bytes;
		Container * container = reinterpret_cast<Container*>(storage);

		inplace_construct(container, obj);
		data->convertible = storage;

		// Try numpy, but don't do implicit conversions of the datatype
		if (PyArray_Check(raw) &&
			!from_numpy<value_type>::extract_vector(
						obj, container->begin(), container->end()))
		{
			// If there are overloads, this causes boost python to try the
			// next possible one
			PyErr_SetString(PyExc_TypeError, "Invalid numpy data type");
			bp::throw_error_already_set();
		}
		else
		{
			// STL iterator uses __iter__ internally which doesn't work
			// always. Catch AttributeError and set type error?
			typedef bp::stl_input_iterator<value_type> iterator;
			std::copy(iterator(obj), iterator(), container->begin());
		}
	}
};

} // end namespace pywrap
