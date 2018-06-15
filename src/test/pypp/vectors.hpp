#pragma once

#include <vector>

inline void test_vector(std::vector<float> & f)
{
	f.clear();
	f.push_back(0.7);
}

inline void test_vector(std::vector<double> & f)
{
	f.clear();
	f.push_back(1.4);
}

struct TestVectorTypedefs
{
	typedef std::vector<bool>   Vector_Bool;
	typedef std::vector<float>  Vector_Float;
	typedef std::vector<double> Vector_Double;
};
