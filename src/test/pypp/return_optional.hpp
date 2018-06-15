#include <boost/optional.hpp>

struct ReturnOptional
{
	boost::optional<size_t> test() const;
	boost::optional<size_t> test(size_t value) const;
}; // ReturnOptional
