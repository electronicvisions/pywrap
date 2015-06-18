#include <iostream>
#include <list>
#include <vector>
#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>

#include "create_constructor.hpp"

namespace pywrap {

// partly copy and pasted from http://stackoverflow.com/questions/15842126/

/// @brief Type that allows for registration of conversions from
///        python iterable types.
struct iterable_converter
{
	/// @note Registers converter from a python interable type to the
	///       provided type.
	template <typename Container>
	iterable_converter& from_python()
	{
		boost::python::converter::registry::push_back(&iterable_converter::convertible<Container>,
		                                              &iterable_converter::construct<Container>,
		                                              boost::python::type_id<Container>());
		// Support chaining.
		return *this;
	}

	/// Exlude boost python types, because this can lead to messy situation
	/// when handling function overloads.
	/// Also I think it would be stupid to convert C++ typs in python
	template <typename Container>
	static void* convertible(PyObject* object)
	{
		// std::cerr << "Test convert to " << ztl::typestring<Container>() << std::endl;
		using boost::python::objects::class_type;
		if (!PyType_IsSubtype(object->ob_type, class_type().get())
			&& PySequence_Check(object))
			return PyObject_GetIter(object);
		return NULL;
	}

	/// @brief Convert iterable PyObject to C++ container type.
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

		// Allocate the C++ type into the converter's memory block, and assign
		// its handle to the converter's convertible variable. The C++
		// container is populated by passing the begin and end iterators of
		// the python object to the container's constructor.
		new (container) Container(bp::len(obj));
		data->convertible = storage;

		/// Try numpy, but don't do implicit conversions of the datatype
		if (PyArray_Check(raw) &&
			!from_numpy<value_type>::extract_vector(
						obj, container->begin(), container->end()))
		{
			// If there are overloads, this causes boost python to try the
			// nex possible one
			PyErr_SetString(PyExc_TypeError, "Invalid numpy data type");
			bp::throw_error_already_set();
		}
		else
		{
			// STL iterator uses __iter__ internally which doesn't work
			// always
			// Or catch AttributeError and set type error?
			for (size_t ii = 0; ii < container->size(); ++ii)
			{
				container->operator[](ii) = bp::extract<value_type>(obj[ii]);
			}
		}
	}
};

} // end namespace pywrap
