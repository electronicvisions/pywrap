#pragma once

#include <array>
#include <vector>

#include "boost/shared_ptr.hpp"
#ifdef HAVE_NUMPY
#include "from_numpy.hpp"
#endif

namespace HMF {
namespace pyplusplus {

template <typename T>
struct extract_obj
{
	static void extract(boost::python::object const & arg, T & out) {
		out = boost::python::extract<T>(arg);
	}
};

template <typename T>
struct extract_obj< std::vector<T> >
{
	static void extract(boost::python::object const & arg, std::vector<T> & out) {
		namespace bp = boost::python;
		out.resize( bp::len(arg) );
#ifdef HAVE_NUMPY
		if( !from_numpy<T>::extract_vector(arg, out.begin(), out.end()) )
#endif
		{
			for (size_t ii = 0; ii < out.size(); ii++) {
				extract_obj<T>::extract(arg[ii], out[ii]);
			}
		}
	}
};

template <typename T, size_t N>
struct extract_obj< std::array<T, N> >
{
	static void extract(boost::python::object const & arg, std::array<T, N> & out) {
		namespace bp = boost::python;
#ifdef HAVE_NUMPY
		if( !from_numpy<T>::extract_vector(arg, out.begin(), out.end()) )
#endif
		{
			for (size_t ii = 0; ii < out.size(); ii++) {
				extract_obj<T>::extract(arg[ii], out[ii]);
			}
		}
	}
};

template <typename T, size_t N, size_t M>
struct extract_obj< std::array< std::array<T, N>, M > >
{
	static void extract(boost::python::object const & arg, std::array< std::array<T, N>, M> & out) {
		namespace bp = boost::python;
#ifdef HAVE_NUMPY
		if( !from_numpy<T>::extract_matrix(arg, out.begin(), out.end()) )
#endif
		{
			for (size_t ii = 0; ii < M; ii++) {
				for (size_t jj = 0; jj < N; jj++) {
					extract_obj<T>::extract(arg[ii][jj], out[ii][jj]);
				}
			}
		}
	}
};

template <typename T>
struct create_constructor
{
	typedef boost::shared_ptr<T> return_type;

	static return_type construct(boost::python::object const & obj)
	{
		return_type r(new T());
		extract_obj<T>::extract(obj, *r);
		return r;
	}
};

} // end namespace pyplusplus
} // end namespace HMF

