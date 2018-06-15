#include "test/pypp/reference_wrapper.hpp"

std::vector<boost::reference_wrapper<int const> > RefWrap::ints() const {
	boost::reference_wrapper<int const> ref(internal);
	return {ref, ref};
}
