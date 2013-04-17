#include <array>
#include <bitset>
#include <boost/array.hpp>

#include "pywrap/create_constructor.hpp"
#include "pywrap/expose_array_operator.hpp"
#include "pywrap/return_numpy_policy.hpp"

struct X {
	int operator[](size_t ii) { return ii; }
};

class Y {
public:
	int & operator[](size_t ii) { return data[ii]; }

private:
	int data[320]; // To large value causes segfault, why?
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

// Some compile time checks on expose_array_operator
void test_array_trais()
{
	using namespace ::pywrap;
    using namespace boost::python;
	{
		typedef decltype(expose_array_operator( &X::operator[]) ) exposer_type;
		typedef typename exposer_type::traits_type traits;
		static_assert(std::is_same<int, typename traits::value_type>::value, "");
		static_assert(std::is_same<size_t, typename traits::key_type>::value, "");
		static_assert(std::is_same<X, typename traits::class_type>::value, "");
		static_assert(traits::make_setitem == false, "");
	}

	{
		typedef const Y & (Z::* Z_index_operator)(size_t) const;
		typedef decltype(expose_array_operator( Z_index_operator(&Z::operator[]) )) exposer_type;
		typedef typename exposer_type::traits_type traits;
		static_assert(std::is_same<const Y &, typename traits::value_type>::value, "");
		static_assert(std::is_same<size_t, typename traits::key_type>::value, "");
		static_assert(std::is_same<Z, typename traits::class_type>::value, "");
		static_assert(traits::make_setitem == false, "");
	}

	{
		typedef Y & (Z::* Z_index_operator)(size_t);
		typedef decltype(expose_array_operator( Z_index_operator(&Z::operator[]) )) exposer_type;
		typedef typename exposer_type::traits_type traits;
		static_assert(std::is_same<Y &, typename traits::value_type>::value, "");
		static_assert(std::is_same<size_t, typename traits::key_type>::value, "");
		static_assert(std::is_same<Z, typename traits::class_type>::value, "");
		static_assert(traits::make_setitem == true, "");
	}

	{
		typedef decltype(expose_array_operator( &Y::operator[]) ) exposer_type;
		typedef typename exposer_type::traits_type traits;
		static_assert(std::is_same<int, typename traits::value_type>::value, "");
		static_assert(std::is_same<size_t, typename traits::key_type>::value, "");
		static_assert(std::is_same<Y, typename traits::class_type>::value, "");
		static_assert(traits::make_setitem == true, "");
	}

	{
		typedef std::bitset<12> bitset_type;
		typedef bitset_type::reference (bitset_type::* operator_type)(std::size_t);
		typedef decltype(expose_array_operator( operator_type(&bitset_type::operator[]),
					default_call_policies(), bool() )) exposer_type;
		typedef typename exposer_type::traits_type traits;
		static_assert(std::is_same<bool, typename traits::value_type>::value, "");
		static_assert(std::is_same<std::size_t, typename traits::key_type>::value, "");
		static_assert(std::is_same<bitset_type, typename traits::class_type>::value, "");
		static_assert(traits::make_setitem == true, "");
	}
	{
		typedef std::bitset<12> bitset_type;
		typedef bool (bitset_type::* operator_type)(std::size_t) const;
		typedef decltype(expose_array_operator( operator_type(&bitset_type::operator[]))
				) exposer_type;
		typedef typename exposer_type::traits_type traits;
		static_assert(std::is_same<bool, typename traits::value_type>::value, "");
		static_assert(std::is_same<std::size_t, typename traits::key_type>::value, "");
		static_assert(std::is_same<bitset_type, typename traits::class_type>::value, "");
		static_assert(traits::make_setitem == false, "");
	}
}

BOOST_PYTHON_MODULE(pywraptestmodule)
{
    using namespace boost::python;
	using namespace ::pywrap;

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
			.def("__init__", make_constructor(&::pywrap::create_constructor< ::std::bitset<12> >::construct))
		;
	}

	def("makeDoubleVector", &makeDoubleVector, ReturnNumpyPolicy());
	def("makeUShortVector", &makeUShortVector, ReturnNumpyPolicy());
}


