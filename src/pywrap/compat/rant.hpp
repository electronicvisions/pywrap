#pragma once

#include <ostream>

#if defined(PYPLUSPLUS)
#include <boost/integer_traits.hpp>
namespace std {

template<typename T, T Val>
struct integral_constant
{
	static T const value = Val;
	typedef T value_type;
	typedef integral_constant<T, Val> type;
	operator value_type () const { return value; }
};

} // std

namespace rant {

template<typename T, typename Max, typename Min>
struct throw_on_error
{
	template<typename U>
	T operator() (U const val) { return T(); }
};

template<typename T, typename Max, typename Min>
struct clip_on_error
{
	template<typename U>
	T operator() (U const val) { return T(); }
};

template<typename T,
	T Max = boost::integer_traits<T>::const_max,
	T Min = boost::integer_traits<T>::const_min,
	typename Check = throw_on_error<T,
		std::integral_constant<T, Max>,
		std::integral_constant<T, Min> > >
class integral_range
{
public:
	template<typename U>
	integral_range(U const v) : value(v) {}
	integral_range() : value(T()) {}

	operator T () const
	{
		return value;
	}
private:
	T value;
};

} // rant

#define ADD_RANT_SERIALIZER(NAME)

#else

#define RANT_CONEXPR

#include <rant/rant.h>
#include <boost/serialization/rant.hpp>

#include <type_traits>

template<typename U, U Max, U Min, typename Check>
rant::integral_range<U, Max, Min, Check>
get_base_type(rant::integral_range<U, Max, Min, Check> const*)
{
	return {};
}

#define ADD_RANT_SERIALIZER(NAME) \
	friend class boost::serialization::access; \
	template<typename Archive> \
	void serialize(Archive& ar, unsigned int const version) \
	{ \
		typedef decltype(get_base_type((NAME const*)NULL)) base_type; \
		boost::serialization::serialize(ar, static_cast<base_type&>(*this), version); \
	}

#endif // PYPLUSPLUS

template<typename T, typename U, U Max, U Min, typename Check,
	typename boost::enable_if_c<boost::is_base_of<
	rant::integral_range<U, Max, Min, Check>, T>::value>::type>
std::ostream & operator<<(std::ostream & out, T const & t)
{
	return out << static_cast<U>(t);
}
