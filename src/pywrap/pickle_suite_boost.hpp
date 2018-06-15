#pragma once

#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/binary_iarchive.hpp>

#include "pickle_suite.tpp"

namespace HMF {
namespace pyplusplus {

template <typename T>
using pickle_suite_boost = pickle_suite<T, boost::archive::binary_iarchive, boost::archive::binary_oarchive>;

} // namespace pyplusplus
} // namespace HMF
