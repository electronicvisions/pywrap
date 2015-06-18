#pragma once
// Provides Py++ compatible definitions

#ifndef PYPLUSPLUS
#include <boost/python/object_fwd.hpp>
#include <boost/python.hpp>
#else
namespace boost {
    namespace python {
		class object;
        class dict;
        class list;
        class slice;
        class tuple;
        class str;

        object import(str);

        namespace numeric
        {
            class array;
        }
    }
}

#endif
