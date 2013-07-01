#pragma once

#include <boost/functional/hash/hash.hpp>

#if defined(PYPLUSPLUS)
#include <string>

namespace std {

template<typename _Result, typename _Arg>
struct __hash_base
{
  typedef _Result     result_type;
  typedef _Arg      argument_type;
};

/// Primary class template hash.
template<typename _Tp>
struct hash;


/// Partial specializations for pointer types.
template<typename _Tp>
struct hash<_Tp*> : public __hash_base<size_t, _Tp*>
{
	size_t operator()(_Tp* __p) const
	{
		return reinterpret_cast<size_t>(__p);
	}
};

// Explicit specializations for integer types.
#define _Cxx_hashtable_define_trivial_hash(_Tp)         \
	template<>						                    \
	struct hash<_Tp> : public __hash_base<size_t, _Tp>  \
	{                                                   \
		size_t operator()(_Tp __val) const              \
		{                                               \
			return static_cast<size_t>(__val);          \
		}                                               \
	};

/// Explicit specialization for bool.
_Cxx_hashtable_define_trivial_hash(bool)

/// Explicit specialization for char.
_Cxx_hashtable_define_trivial_hash(char)

/// Explicit specialization for signed char.
_Cxx_hashtable_define_trivial_hash(signed char)

/// Explicit specialization for unsigned char.
_Cxx_hashtable_define_trivial_hash(unsigned char)

/// Explicit specialization for wchar_t.
_Cxx_hashtable_define_trivial_hash(wchar_t)

/// Explicit specialization for char16_t.
//_Cxx_hashtable_define_trivial_hash(char16_t)

/// Explicit specialization for char32_t.
//_Cxx_hashtable_define_trivial_hash(char32_t)

/// Explicit specialization for short.
_Cxx_hashtable_define_trivial_hash(short)

/// Explicit specialization for int.
_Cxx_hashtable_define_trivial_hash(int)

/// Explicit specialization for long.
_Cxx_hashtable_define_trivial_hash(long)

/// Explicit specialization for long long.
_Cxx_hashtable_define_trivial_hash(long long)

/// Explicit specialization for unsigned short.
_Cxx_hashtable_define_trivial_hash(unsigned short)

/// Explicit specialization for unsigned int.
_Cxx_hashtable_define_trivial_hash(unsigned int)

/// Explicit specialization for unsigned long.
_Cxx_hashtable_define_trivial_hash(unsigned long)

/// Explicit specialization for unsigned long long.
_Cxx_hashtable_define_trivial_hash(unsigned long long)

#undef _Cxx_hashtable_define_trivial_hash

/// Specialization for float.
template<>
struct hash<float> : public __hash_base<size_t, float>
{
	size_t operator()(float __val) const
	{
		return boost::hash_value(__val);
	}
};

/// Specialization for double.
template<>
struct hash<double> : public __hash_base<size_t, double>
{
	size_t operator()(double __val) const
	{
		return boost::hash_value(__val);
	}
};

template<>
struct hash<std::string> : public __hash_base<size_t, double>
{
	size_t operator()(std::string const& __val) const
	{
		return boost::hash_value(__val);
	}
};

} // std

#else
#include <functional>
#endif // PYPLUSPLUS
