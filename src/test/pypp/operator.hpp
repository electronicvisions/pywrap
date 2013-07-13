#include <cstddef>
#include "pywrap/compat/array.hpp"

struct Base1
{
	int operator[](size_t ii) { return ii; }
	int operator()(size_t ii) { return ii; }

	operator int() { return 0; }

	Base1 operator+(const Base1 & b) { return Base1(); }
};

struct Base2
{
	int b;
};

struct Derived : public Base1
{
};

