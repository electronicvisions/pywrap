#pragma once

#include <bitset>
#include <functional>


namespace HMF {
namespace pyplusplus {

	template<size_t N>
	std::ostream & operator<<(std::ostream & out, const std::bitset<N> & obj)
	{
		return out << obj.to_ulong();
	}

	template <typename T>
	std::string printGeometryClass(const T & obj, std::string name)
	{
		typedef typename T::value_type value_type;
		std::stringstream out;
		out << name << "("
			<< static_cast<value_type>(obj)
			<< ")";
		return out.str();
	}

} // end namespace pyplusplus
} // end namespace HMF

