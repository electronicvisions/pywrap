#pragma once
#ifndef PYPLUSPLUS
#include <tuple>
#else
// class template tuple -*- C++ -*-

// Copyright (C) 2004, 2005 Free Software Foundation, Inc.
//
// This file is part of the GNU ISO C++ Library.  This library is free
// software; you can redistribute it and/or modify it under the
// terms of the GNU General Public License as published by the
// Free Software Foundation; either version 2, or (at your option)
// any later version.

// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License along
// with this library; see the file COPYING.  If not, write to the Free
// Software Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
// USA.

// As a special exception, you may use this file as part of a free software
// library without restriction.  Specifically, if other files instantiate
// templates or use macros or inline functions from this file, or you compile
// this file and link it with other files to produce an executable, this
// file does not by itself cause the resulting executable to be covered by
// the GNU General Public License.  This exception does not however
// invalidate any other reasons why the executable file might be covered by
// the GNU General Public License.

/** @file tr1/tuple
*  This is a TR1 C++ Library header.
*/

// Chris Jefferson <chris@bubblescope.net>

#ifndef _TR1_TUPLE
#define _TR1_TUPLE 1

//#include <tr1/utility>
#include "ref_fwd.h"

namespace std
{

 // An implementation specific class which is used in the tuple class
 // when the tuple is not maximum possible size.
 struct _NullClass { };

 /// Gives the type of the ith element of a given tuple type.
 template<std::size_t __i, typename _Tp>
   struct tuple_element;

 /// Finds the size of a given tuple type.
 template<typename _Tp>
   struct tuple_size;

 // Adds a const reference to a non-reference type.
 template<typename _Tp>
   struct __add_c_ref
   { typedef const _Tp& type; };

 template<typename _Tp>
   struct __add_c_ref<_Tp&>
   { typedef _Tp& type; };

 // Adds a reference to a non-reference type.
 template<typename _Tp>
   struct __add_ref
   { typedef _Tp& type; };

 template<typename _Tp>
   struct __add_ref<_Tp&>
   { typedef _Tp& type; };

 // Class used in the implementation of get
 template<int __i, typename _Tp>
   struct __get_helper;

 // Returns a const reference to the ith element of a tuple.
 // Any const or non-const ref elements are returned with their original type.

 // This class helps construct the various comparison operations on tuples
 template<int __check_equal_size, int __i, int __j, typename _Tp, typename _Up>
   struct __tuple_compare;

 // Helper which adds a reference to a type when given a reference_wrapper
 template<typename _Tp>
   struct __strip_reference_wrapper
   {
       typedef _Tp __type;
   };

 template<typename _Tp>
   struct __strip_reference_wrapper<reference_wrapper<_Tp> >
   {
     typedef _Tp& __type;
   };

 template<typename _Tp>
   struct __strip_reference_wrapper<const reference_wrapper<_Tp> >
   {
       typedef _Tp& __type;
   };

  #include "tuple_defs.h"

 template<int __i, int __j, typename _Tp, typename _Up>
   struct __tuple_compare<0, __i, __j, _Tp, _Up>
   {
     static bool __eq(const _Tp& __t, const _Up& __u)
     {
       return get<__i>(__t) == get<__i>(__u) &&
          __tuple_compare<0, __i+1, __j, _Tp, _Up>::__eq(__t, __u);
     }
     static bool __less(const _Tp& __t, const _Up& __u)
     {
       return (get<__i>(__t) < get<__i>(__u)) || !(get<__i>(__u) < get<__i>(__t)) &&
          __tuple_compare<0, __i+1, __j, _Tp, _Up>::__less(__t, __u);
     }
   };

 template<int __i, typename _Tp, typename _Up>
   struct __tuple_compare<0, __i, __i, _Tp, _Up>
   {
     static bool __eq(const _Tp&, const _Up&)
     { return true; }
     static bool __less(const _Tp&, const _Up&)
     { return false; }
   };

 // A class (and instance) which can be used in 'tie' when an element
 // of a tuple is not required
 struct swallow_assign
 {
   template<class T>
   swallow_assign&
     operator=(const T&)
     { return *this; }
 };

 // TODO: Put this in some kind of shared file.
 namespace
 {
   swallow_assign ignore;
 }; // anonymous namespace

}

#define _GLIBCXX_CAT(x,y) _GLIBCXX_CAT2(x,y)
#define _GLIBCXX_CAT2(x,y) x##y
#define _SHORT_REPEAT
#define _GLIBCXX_REPEAT_HEADER "tuple_iterate.h"
#include "repeat.h"
#undef _GLIBCXX_REPEAT_HEADER
#undef _SHORT_REPEAT

//#include <tr1/functional>

#endif

#endif // PYPLUSPLUS
