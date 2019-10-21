#include "test/pypp/return_optional.hpp"

boost::optional<size_t> ReturnOptional::test() const
{
	return boost::none;
}

boost::optional<size_t> ReturnOptional::test(size_t value) const
{
	return boost::make_optional(value);
}

boost::tuple<boost::optional<size_t>, boost::optional<size_t> > ReturnOptionalB::test(size_t value, size_t value2) const
{
	return boost::make_tuple(boost::optional<size_t>(value + value2), boost::optional<size_t>());
}

boost::tuple<size_t, boost::optional<size_t> > ReturnOptionalC::test(size_t value, size_t value2) const
{
	return boost::make_tuple(value + value2, boost::optional<size_t>(value2));
}
