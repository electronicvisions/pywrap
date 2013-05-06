#pragma once

#include <bitset>
#include <functional>
#include <boost/python.hpp>

namespace pywrap {
	namespace bp = boost::python;

	template <std::size_t N>
	std::ostream & operator<<(std::ostream & out, const std::bitset<N>& obj)
	{
		return out << '"' << obj.to_string() << '"';
	}

	template <typename T>
	std::string printClassNice(const T & obj, bp::object cls)
	{
		std::string name = bp::extract<std::string>(cls.attr("__name__"));
		std::stringstream out;
		out << name << "("
			<< obj
			<< ")";
		return out.str();
	}

	class PrintNice :
		public boost::python::def_visitor<PrintNice>
	{
	public:
		template <class classT>
		void visit(classT& c) const
		{
			typedef typename classT::wrapped_type wrapped_type;
			auto f = std::bind(::pywrap::printClassNice< wrapped_type >, std::placeholders::_1, c);
			typedef boost::mpl::vector<std::string, wrapped_type> f_signature;
			c.def("__str__", bp::make_function(f, boost::python::default_call_policies(), f_signature()));
		}
	};


} // end namespace pywrap

