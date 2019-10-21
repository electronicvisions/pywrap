#include <boost/optional.hpp>
#include <boost/tuple/tuple.hpp>

struct ReturnOptional
{
	boost::optional<size_t> test() const;
	boost::optional<size_t> test(size_t value) const;
}; // ReturnOptional

struct ReturnOptionalB
{
	boost::tuple<boost::optional<size_t>, boost::optional<size_t> > test(size_t value, size_t value2) const;
}; // ReturnOptionalB

struct ReturnOptionalC
{
	boost::tuple<size_t, boost::optional<size_t> > test(size_t value, size_t value2) const;
}; // ReturnOptionalC
