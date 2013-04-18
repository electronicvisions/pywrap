#pragma once

#ifdef PYPLUSPLUS
#define PYPP_CONSTEXPR const
#define constexpr
#define explicit
#define static_assert(X, Y)
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
