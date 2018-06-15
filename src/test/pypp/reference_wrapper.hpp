#include <boost/ref.hpp>
#include <vector>

#include "pywrap/compat/macros.hpp"

class RefWrap {
public:
	RefWrap() : internal(42) {}
	std::vector<boost::reference_wrapper<int const> > ints() const;
	PYPP_INSTANTIATE(std::vector<int>);
private:
	int internal;
}; // RefWrap
