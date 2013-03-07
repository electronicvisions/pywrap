#pragma once

#include <boost/python.hpp>

#include "pyublas/numpy.hpp"
#include <boost/numeric/ublas/matrix_proxy.hpp>

namespace HMF {
namespace pyplusplus {

template <typename T>
struct from_numpy {
	struct arithmetic_tag {};
	struct not_arithmetic_tag {};

	typedef pyublas::numpy_vector<T> vector_type;
	typedef pyublas::numpy_matrix<T> matrix_type;
	typedef const boost::python::object & obj_type;
	typedef typename std::conditional<std::is_arithmetic<T>::value,
			arithmetic_tag, not_arithmetic_tag>::type tag_type;

	template <typename iterator>
	static bool extract_vector(obj_type obj, iterator begin, iterator end)
	{
		return do_extract_vector(obj, begin, end, tag_type());
	}

	template <typename iterator>
	static bool extract_matrix(obj_type obj, iterator begin, iterator end)
	{
		return do_extract_matrix(obj, begin, end, tag_type());
	}

private:
	template <typename iterator>
	static bool do_extract_vector(obj_type, iterator, iterator, not_arithmetic_tag)
	{
		return false;
	}

	template <typename iterator>
	static bool do_extract_vector(obj_type obj, iterator begin, iterator end, arithmetic_tag)
	{
		typedef typename std::iterator_traits<iterator>::difference_type difference_type;

		namespace bp = boost::python;
		bp::extract<vector_type> type_checker(obj);
		if (type_checker.check())
		{
			const vector_type & a = type_checker();
			if (std::distance(begin, end) != static_cast<difference_type>(a.size()))
			{
				std::stringstream err;
				err << "Size missmatch, expected shape (" << std::distance(begin, end)
					<< ",) got (" << a.size() << ",)";
				throw std::out_of_range(err.str());
			}
			std::copy(a.begin(), a.end(), begin);
			return true;
		}
		return false;
	}

	template <typename iterator>
	static bool do_extract_matrix(obj_type, iterator, iterator, not_arithmetic_tag)
	{
		return false;
	}

	template <typename iterator>
	static bool do_extract_matrix(obj_type obj, iterator begin, iterator end, arithmetic_tag)
	{
		using namespace boost::numeric::ublas;
		typedef typename std::iterator_traits<iterator>::difference_type difference_type;

		const difference_type rows   = std::distance(begin, end);
		const difference_type colums = std::distance(begin->begin(), begin->end());

		namespace bp = boost::python;
		bp::extract<matrix_type> type_checker(obj);
		if (type_checker.check())
		{
			const matrix_type & m = type_checker();

			const difference_type m_colums = m.size2();
			const difference_type m_rows   = m.size1();

			if (rows != m_rows or colums != m_colums)
			{
				std::stringstream err;
				err << "Size missmatch, expected shape ("
					<< rows << ", " << colums
					<< ",) got (" << m.size1() << ", " << m.size2() <<")";
				throw std::out_of_range(err.str());
			}

			difference_type current_row = 0;
			iterator it = begin;
			for (; it != end && current_row < rows; ++it, ++current_row)
			{
				matrix_row<const matrix_type> mr(m, current_row);
				if (std::distance(it->begin(), it->end()) != colums)
				{
					throw std::runtime_error("Internal Error: Invalid input to function");
				}
				std::copy(mr.begin(), mr.end(), it->begin());

			}
			return true;
		}
		return false;
	}
};

template <typename T>
struct from_numpy_matrix{
	struct arithmetic_tag {};
	struct not_arithmetic_tag {};

	typedef pyublas::numpy_vector<T> numpy_type;
	typedef const boost::python::object & obj_type;
	typedef typename std::conditional<std::is_arithmetic<T>::value,
			arithmetic_tag, not_arithmetic_tag>::type tag_type;

	template <typename iterator>
	static bool extract(obj_type obj, iterator begin, iterator end)
	{
		return do_extract(obj, begin, end, tag_type());
	}

private:
	template <typename iterator>
	static bool do_extract(obj_type, iterator, iterator, not_arithmetic_tag)
	{
		return false;
	}

	template <typename iterator>
	static bool do_extract(obj_type obj, iterator begin, iterator end, arithmetic_tag)
	{
		typedef typename std::iterator_traits<iterator>::difference_type difference_type;

		namespace bp = boost::python;
		bp::extract<numpy_type> type_checker(obj);
		if (type_checker.check())
		{
			const numpy_type & a = type_checker();
			if (std::distance(begin, end) != static_cast<difference_type>(a.size()))
			{
				std::stringstream err;
				err << "Size missmatch, expected shape (" << std::distance(begin, end)
					<< ",) got (" << a.size() << ",)";
				throw std::out_of_range(err.str());
			}
			std::copy(a.begin(), a.end(), begin);
			return true;
		}
		return false;
	}
};

} // end namespace pyplusplus
} // end namespace HMF
