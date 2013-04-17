#pragma once

#include <array>
#include <bitset>
#include <vector>

#include "boost/shared_ptr.hpp"
#include "from_numpy.hpp"

namespace pywrap {

template <typename T, typename U = void>
struct extract_obj
{
	static void extract(boost::python::object const & arg, T & out) {
		out = boost::python::extract<T>(arg);
	}
};

template <size_t N>
struct extract_obj< std::bitset<N> >
{
	static void extract(boost::python::object const & arg, std::bitset<N> & out) {
		namespace bp = boost::python;
		bp::extract<unsigned long> number(arg);
		bp::extract<std::string> string(arg);
		if (number.check())
		{
			out = std::bitset<N>(number());
		}
		else if(string.check())
		{
			 out = std::bitset<N>(string());
		}
		else if( !from_numpy<bool>::extract_bitset(arg, out) )
		{
			for (size_t ii = 0; ii < out.size(); ii++) {
				out[ii] = boost::python::extract<bool>(arg[ii]);
			}
		}
	}
};

template <typename T>
struct extract_obj< std::vector<T> >
{
	static void extract(boost::python::object const & arg, std::vector<T> & out) {
		namespace bp = boost::python;
		out.resize( bp::len(arg) );
		if( !from_numpy<T>::extract_vector(arg, out.begin(), out.end()) )
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
		if( !from_numpy<T>::extract_vector(arg, out.begin(), out.end()) )
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
		if( !from_numpy<T>::extract_matrix(arg, out.begin(), out.end()) )
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

} // end namespace pywrap

