#pragma once

#ifndef PYPLUSPLUS
#include <cereal/cereal.hpp>
#include <cereal/archives/binary.hpp>
#else
#define CEREAL_NVP
namespace cereal { class access; }
#endif

struct WithPickleCereal
{
	int value;

	friend class cereal::access;
	template <class Archive>
	void serialize(Archive& ar)
	{
		ar(CEREAL_NVP(value));
	}
};
