#pragma once

#include <bitset>
#include <functional>
#include <boost/python.hpp>


namespace HMF {
namespace pyplusplus {

	template <std::size_t N>
	std::ostream & operator<<(std::ostream & out, const std::bitset<N>& obj)
	{
		return out << obj.to_ulong();
	}

	template <typename T>
	std::string printClassNice(const T & obj, std::string name)
	{
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
			std::string name = boost::python::extract<std::string>(c.attr("__name__"));
			auto f = std::bind(HMF::pyplusplus::printClassNice< wrapped_type >, std::placeholders::_1, name);
			typedef boost::mpl::vector<std::string, wrapped_type> f_signature;
			c.def("__str__", bp::make_function(f, boost::python::default_call_policies(), f_signature()));
		}
	};


} // end namespace pyplusplus
} // end namespace HMF

