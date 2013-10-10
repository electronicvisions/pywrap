#if !defined(PYPLUSPLUS)
#include <ztl/debug.h>
#else
#include <typeinfo>
#include <string>
namespace ZTL {

template <typename T>
std::string typestring(T t);

template <typename T>
std::string typestring();

} // ZTL
#endif
