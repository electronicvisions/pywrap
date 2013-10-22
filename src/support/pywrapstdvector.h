#pragma once

#include <vector>
#include "pywrap/compat/cstdint.hpp"
#include "pywrap/compat/macros.hpp"

PYPP_INSTANTIATE(std::vector<float>);
PYPP_INSTANTIATE(std::vector<double>);
PYPP_INSTANTIATE(std::vector<bool>);
PYPP_INSTANTIATE(std::vector<int8_t>);
PYPP_INSTANTIATE(std::vector<int16_t>);
PYPP_INSTANTIATE(std::vector<int32_t>);
PYPP_INSTANTIATE(std::vector<int64_t>);
PYPP_INSTANTIATE(std::vector<uint8_t>);
PYPP_INSTANTIATE(std::vector<uint16_t>);
PYPP_INSTANTIATE(std::vector<uint32_t>);
PYPP_INSTANTIATE(std::vector<uint64_t>);
