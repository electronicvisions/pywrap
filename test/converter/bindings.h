#pragma once

#include <iostream>
#include <vector>

#include <pywrap/compat/numpy.hpp>

struct ConverterTest {
	typedef std::vector<double> data_type;

	size_t sink(data_type data) {
		return data.size();
	}

	size_t sink(pyublas::numpy_vector<double> data)
#ifdef PYPLUSPLUS
		;
#else
	{
		return data.size();
	}
#endif
};
