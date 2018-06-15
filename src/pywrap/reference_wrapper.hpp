#pragma once

#include <algorithm>
#include <boost/ref.hpp>
#include <iterator>
#include <vector>

template <typename T,
          typename V,
          std::vector<boost::reference_wrapper<V const> > (T::*mem_fun)() const>
struct convert_vector_of_references_return_type
{
	typedef std::vector<boost::reference_wrapper<V const> > references_type;
	static std::vector<V> apply(T const& self)
	{
		references_type refs = (self.*mem_fun)();
		std::vector<V> ret;
		ret.reserve(refs.size());
		std::copy(refs.begin(), refs.end(), std::back_inserter(ret));
		return ret;
	}
}; // convert_vector_of_references_return_type
