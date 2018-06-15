#pragma once

#include <boost/serialization/serialization.hpp>
#include <boost/serialization/nvp.hpp>

struct WithPickle
{
	int value;

	friend class boost::serialization::access;
	template<typename Archiver>
	void serialize(Archiver& ar, unsigned int const)
	{
		using namespace boost::serialization;
		ar & make_nvp("value", value);
	}
};
