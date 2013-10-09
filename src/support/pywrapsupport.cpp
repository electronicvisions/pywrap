#include <boost/python.hpp>

BOOST_PYTHON_MODULE(pywrapsupport)
{
    using namespace boost::python;

	import("pyublas");

	class_< boost::shared_ptr<void> >("__void_ptr");
}

