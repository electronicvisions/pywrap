#include "test/pypp/return_optional.hpp"

boost::optional<size_t> ReturnOptional::test() const
{
	return boost::none;
}

boost::optional<size_t> ReturnOptional::test(size_t value) const
{
	return boost::make_optional(value);
}
