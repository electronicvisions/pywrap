#pragma once

#include <cstddef>
#include "pywrap/compat/array.hpp"

struct Data1
{
	int a;
};

struct Data2
{
	int b;
};

struct KProxy
{
	Data1 & value1;
	Data2 & value2;
	KProxy(Data1 & a, Data2 &b) :
		value1(a),
		value2(b)
	{}
};

struct K
{
#ifndef PYPLUSPLUS
	K() :
		data1{{{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}}},
		data2{{{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}}}
	{}
	KProxy operator[](size_t ii) { return KProxy{data1[ii], data2[ii]}; }
#else
	K();
	KProxy operator[](size_t ii);
	//KConstProxy operator[](size_t ii) const;
#endif
	std::array<Data1, 123> data1;
	std::array<Data2, 123> data2;
};
