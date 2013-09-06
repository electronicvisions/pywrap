#pragma once

#ifdef PYPLUSPLUS
#include <boost/numeric/ublas/matrix_proxy.hpp>
namespace pyublas
{
template <class T> class numpy_vector;
template<class T, class L> class numpy_matrix;
}
#else
#include <pyublas/numpy.hpp>
#endif
