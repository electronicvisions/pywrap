#pragma once

#include <vector>
#include <pywrap/compat/boost_python.hpp>
#include <pywrap/compat/numpy.hpp>

using boost::python::list;
using boost::python::tuple;

static const int int_tag = 0;
static const int double_tag = 1;

struct ConverterTest {
	ConverterTest() {}

	typedef std::vector<int32_t> int_data_type;
	typedef std::vector<double> double_data_type;

	tuple sink(int_data_type data);
	tuple sink(double_data_type data);

	tuple sink(pyublas::numpy_vector<int32_t> data);
	tuple sink(pyublas::numpy_vector<double> data);

	list test_int_sink(int_data_type data);
	list test_int_sink(pyublas::numpy_vector<int32_t> data);

	list test_double_sink(double_data_type data);
	list test_double_sink(pyublas::numpy_vector<double> data);

	void instantiate()
	{
		int_data_type();
		double_data_type();
	}
};

#ifndef PYPLUSPLUS
#include <boost/python/tuple.hpp>

using boost::python::make_tuple;

tuple ConverterTest::sink(int_data_type data)
{
	return make_tuple(int_tag, data.size());
}

tuple ConverterTest::sink(double_data_type data) {
	return make_tuple(double_tag, data.size());
}

tuple ConverterTest::sink(pyublas::numpy_vector<int32_t> data)
{
	return make_tuple(int_tag, data.size());
}

tuple ConverterTest::sink(pyublas::numpy_vector<double> data)
{
	return make_tuple(double_tag, data.size());
}

list ConverterTest::test_int_sink(int_data_type data) {
	list ret;
	typedef int_data_type::iterator iterator;
	for (iterator it = data.begin(); it != data.end(); ++it) {
		ret.append(*it);
	}
	return ret;
}

list ConverterTest::test_int_sink(pyublas::numpy_vector<int32_t> data) {
	typedef pyublas::numpy_vector<int32_t>::iterator iterator;
	list ret;
	for (iterator it = data.begin(); it != data.end(); ++it) {
		ret.append(*it);
	}
	return ret;
}

list ConverterTest::test_double_sink(double_data_type data) {
	list ret;
	typedef double_data_type::iterator iterator;
	for (iterator it = data.begin(); it != data.end(); ++it) {
		ret.append(*it);
	}
	return ret;
}

list ConverterTest::test_double_sink(pyublas::numpy_vector<double> data) {
	typedef pyublas::numpy_vector<double>::iterator iterator;
	list ret;
	for (iterator it = data.begin(); it != data.end(); ++it) {
		ret.append(*it);
	}
	return ret;
}
#endif
