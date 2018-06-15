#pragma once

#include <cereal/archives/binary.hpp>

#include "pickle_suite.tpp"

namespace HMF {
namespace pyplusplus {

template <typename T>
using pickle_suite_cereal = pickle_suite<T, cereal::BinaryInputArchive, cereal::BinaryOutputArchive>;

} // namespace pyplusplus
} // namespace HMF
