#include "pywrap/create_constructor.hpp"
#include "pywrap/expose_array_operator.hpp"
#include "pywrap/return_numpy_policy.hpp"

namespace {
	template <typename T>
	void addVector(const char * const name)
	{
		boost::python::class_< std::vector<T> >(name)
			.def( boost::python::indexing::vector_suite< std::vector< T> >() );
			.def( "__init__", boost::python::make_constructor(&::pywrap::create_constructor< ::std::vector<T> >::construct))
		;
	}
}

BOOST_PYTHON_MODULE(pywrapstdvector)
{
    using namespace boost::python;
	using namespace ::pywrap;

	import("pyublas");

	addVector< float >         ("Vector_Float");
	addVector< double >        ("Vector_Double");
	addVector< char >          ("Vector_Char");
	addVector< unsigned char > ("Vector_UChar");
	addVector< short >         ("Vector_Short");
	addVector< unsigned short >("Vector_UShort");
	addVector< int >           ("Vector_Int");
	addVector< unsigned int >  ("Vector_UInt");
}
