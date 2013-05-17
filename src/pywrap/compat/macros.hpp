#pragma once

#ifdef PYPLUSPLUS
#define PYPP_CONSTEXPR const
#define constexpr
#define explicit
#define static_assert(X, Y)
#define nullptr NULL
#define PYPP_TYPED_ENUM(name, type) enum name
#define PYPP_TYPENAME
#define PYPP_EXPLICIT_CAST
#define PYPP_INSTANTIATE(TYPE) inline void _instantiate(TYPE& a) { static_cast<void>(a); }
#define PYPP_DEFAULT(x)
#else
#define PYPP_CONSTEXPR constexpr
#define PYPP_TYPED_ENUM(name, type) enum name : type
#define PYPP_TYPENAME typename
#define PYPP_EXPLICIT_CAST explicit
#define PYPP_INSTANTIATE(TYPE)
#define PYPP_DEFAULT(x) x = default
#endif

#if __cplusplus >= 201103L
#define PYPP_FINAL final
#else
#define PYPP_FINAL
#endif
