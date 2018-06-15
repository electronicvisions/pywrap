#pragma once

#ifdef PYPLUSPLUS
#define PYPP_CONSTEXPR
#define static_assert(...)
#define nullptr NULL
#define PYPP_TYPED_ENUM(name, type) enum name
#define PYPP_CLASS_ENUM(name) enum name
#define PYPP_TYPED_CLASS_ENUM(name, type) enum name
#define PYPP_TYPENAME /* this is only due to gcc4.4 ignoring the c++ std */
#define PYPP_EXPLICIT_CAST
#define PYPP_INSTANTIATE(TYPE) static inline void pywrap_instantiate(TYPE& a) { static_cast<void>(a); }
#define PYPP_DELETE(x)
#define PYPP_EXCLUDE(...)
#define PYPP_INIT(TYPE, VALUE) TYPE
#define PYPP_NOEXCEPT(VALUE)
#else
#define PYPP_CONSTEXPR constexpr
#define PYPP_TYPED_ENUM(name, type) enum name : type
#define PYPP_CLASS_ENUM(name) enum class name
#define PYPP_TYPED_CLASS_ENUM(name, type) enum class name : type
#define PYPP_TYPENAME typename
#define PYPP_EXPLICIT_CAST explicit
#define PYPP_INSTANTIATE(TYPE) static inline void pywrap_instantiate(TYPE& a) { static_cast<void>(a); }
#define PYPP_DELETE(x) x = delete
#define PYPP_EXCLUDE(...) __VA_ARGS__
#define PYPP_INIT(TYPE, VALUE) TYPE = VALUE
#define PYPP_NOEXCEPT(VALUE) noexcept(VALUE)
#endif

#if defined(PYPLUSPLUS) && !defined(PYBINDINGS)
#define PYPP_DEFAULT(x) x
#else
#define PYPP_DEFAULT(x) x = default
#endif

#if __cplusplus >= 201103L
#define PYPP_FINAL final
#define PYPP_OVERRIDE override
#else
#define PYPP_FINAL
#define PYPP_OVERRIDE
#endif
