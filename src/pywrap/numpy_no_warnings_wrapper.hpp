#pragma once

#pragma GCC system_header

#include "pyublas/numpy.hpp"

// PyArray_SetBaseObject triggers a compile warning:
// ISO C++ forbids casting between pointer-to-function and pointer-to
// -object [enabled by default]
// Since I cannot disable this with a diagnostic pragma, this header is
// marked as system header (see line 3), and will not cause warnings anymore :)
// HACKY, HACKY, HACKY, ...

namespace pywrap {
	inline
	void
	Wrapper_PyArray_SetBaseObject(PyArrayObject * array, PyObject *  base)
	{
		PyArray_SetBaseObject(array, base);
	}

	inline
	PyObject *
	Wrapper_PyArray_SimpleNewFromData(int nd, npy_intp * dims, int typenum,
		                              void *data)
	{
		return PyArray_SimpleNewFromData(nd, dims, typenum, data);
	}
}

