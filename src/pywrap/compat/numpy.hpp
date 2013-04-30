#pragma once

#ifdef PYPLUSPLUS
#include "boost/serialization/ublas_fwd.h"
namespace pyublas
{
template <class T> class numpy_vector;
template<class T, class L> class numpy_matrix;
}
#else
#include "pyublas/numpy.hpp"
#endif
