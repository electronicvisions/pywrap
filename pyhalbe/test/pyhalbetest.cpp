#include <array>
#include <bitset>
#include <boost/array.hpp>

#include "pyhalbe/expose_array_operator.hpp"
#include "pyhalbe/return_numpy_policy.hpp"

class Y {
public:
	int & operator[](size_t ii) { return data[ii]; }

private:
	int data[3200]; // To large value causes segfault, why?
};

class Z {
public:
	Y & operator[](size_t ii) { return data[ii]; }
	const Y & operator[](size_t ii) const { return data[ii]; }

private:
	Y data[30];
};

std::vector<double> makeDoubleVector()
{
	return std::vector<double>({0,1,2,3,4,5,6,7,8,9});
}

std::vector<unsigned short> makeUShortVector()
{
	return std::vector<unsigned short>({0,1,2,3,4,5,6,7,8,9});
}

BOOST_PYTHON_MODULE(pyhalbe_test)
{
    using namespace boost::python;
	using namespace ::HMF::pyplusplus;

	import("pyublas");

    class_<Y>("Y")
        .def(expose_array_operator(&Y::operator[]))
    ;

	typedef const Y & (Z::* Z_index_operator)(size_t) const;
    class_<Z>("Z")
        .def(expose_array_operator( Z_index_operator(&Z::operator[]) ) )
    ;

	{
		typedef std::bitset<12> bitset_type;
		typedef bitset_type::reference (bitset_type::* operator_type)(std::size_t);
		class_<bitset_type>("MiniBitset12")
			.def(expose_array_operator(operator_type(&bitset_type::operator[]), default_call_policies(), bool() ))
		;
	}
	
	def("makeDoubleVector", &makeDoubleVector, ::HMF::pyplusplus::ReturnNumpyPolicy());
	def("makeUShortVector", &makeUShortVector, ::HMF::pyplusplus::ReturnNumpyPolicy());
}


