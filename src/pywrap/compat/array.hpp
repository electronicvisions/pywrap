#pragma once
#ifdef PYPLUSPLUS
// <array> -*- C++ -*-

// Copyright (C) 2007, 2008, 2009, 2010 Free Software Foundation, Inc.
//
// This file is part of the GNU ISO C++ Library.  This library is free
// software; you can redistribute it and/or modify it under the
// terms of the GNU General Public License as published by the
// Free Software Foundation; either version 3, or (at your option)
// any later version.

// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// Under Section 7 of GPL version 3, you are granted additional
// permissions described in the GCC Runtime Library Exception, version
// 3.1, as published by the Free Software Foundation.

// You should have received a copy of the GNU General Public License and
// a copy of the GCC Runtime Library Exception along with this program;
// see the files COPYING3 and COPYING.RUNTIME respectively.  If not, see
// <http://www.gnu.org/licenses/>.

/** @file include/array
 *  This is a Standard C++ Library header.
 */

#ifndef _GLIBCXX_ARRAY
#define _GLIBCXX_ARRAY 1

#pragma GCC system_header

#include <bits/stl_algobase.h>
#include <bits/range_access.h>

namespace std _GLIBCXX_VISIBILITY(default)
{
_GLIBCXX_BEGIN_NAMESPACE_VERSION

  /**
   *  @brief A standard container for storing a fixed size sequence of elements.
   *
   *  @ingroup sequences
   *
   *  Meets the requirements of a <a href="tables.html#65">container</a>, a
   *  <a href="tables.html#66">reversible container</a>, and a
   *  <a href="tables.html#67">sequence</a>.
   *
   *  Sets support random access iterators.
   *
   *  @param  Tp  Type of element. Required to be a complete type.
   *  @param  N  Number of elements.
  */
  template<typename _Tp, std::size_t _Nm>
    struct array
    {
      typedef _Tp                                     value_type;
      typedef _Tp*                                    pointer;
      typedef const _Tp*                              const_pointer;
      typedef value_type&                             reference;
      typedef const value_type&                       const_reference;
      typedef value_type*                             iterator;
      typedef const value_type*			              const_iterator;
      typedef std::size_t                             size_type;
      typedef std::ptrdiff_t                          difference_type;
      typedef std::reverse_iterator<iterator>	      reverse_iterator;
      typedef std::reverse_iterator<const_iterator>   const_reverse_iterator;

      // Support for zero-sized arrays mandatory.
      value_type _M_instance[_Nm ? _Nm : 1];

      // No explicit construct/copy/destroy for aggregate type.

      // DR 776.
      void
      fill(const value_type& __u)
      { std::fill_n(begin(), size(), __u); }

      void
      swap(array& __other)
      { std::swap_ranges(begin(), end(), __other.begin()); }

      // Iterators.
      iterator
      begin()
      { return iterator(std::__addressof(_M_instance[0])); }

      const_iterator
      begin() const
      { return const_iterator(std::__addressof(_M_instance[0])); }

      iterator
      end()
      { return iterator(std::__addressof(_M_instance[_Nm])); }

      const_iterator
      end() const
      { return const_iterator(std::__addressof(_M_instance[_Nm])); }

      reverse_iterator
      rbegin()
      { return reverse_iterator(end()); }

      const_reverse_iterator
      rbegin() const
      { return const_reverse_iterator(end()); }

      reverse_iterator
      rend()
      { return reverse_iterator(begin()); }

      const_reverse_iterator
      rend() const
      { return const_reverse_iterator(begin()); }

      const_iterator
      cbegin() const
      { return const_iterator(std::__addressof(_M_instance[0])); }

      const_iterator
      cend() const
      { return const_iterator(std::__addressof(_M_instance[_Nm])); }

      const_reverse_iterator
      crbegin() const
      { return const_reverse_iterator(end()); }

      const_reverse_iterator
      crend() const
      { return const_reverse_iterator(begin()); }

      // Capacity.
      size_type
      size() const { return _Nm; }

      size_type
      max_size() const { return _Nm; }

      bool
      empty() const { return size() == 0; }

      // Element access.
      reference
      operator[](size_type __n)
      { return _M_instance[__n]; }

      const_reference
      operator[](size_type __n) const
      { return _M_instance[__n]; }

      reference
      at(size_type __n)
      {
	if (__n >= _Nm)
	  std::__throw_out_of_range(__N("array::at"));
	return _M_instance[__n];
      }

      const_reference
      at(size_type __n) const
      {
	if (__n >= _Nm)
	  std::__throw_out_of_range(__N("array::at"));
	return _M_instance[__n];
      }

      reference
      front()
      { return *begin(); }

      const_reference
      front() const
      { return *begin(); }

      reference
      back()
      { return _Nm ? *(end() - 1) : *end(); }

      const_reference
      back() const
      { return _Nm ? *(end() - 1) : *end(); }

      _Tp*
      data()
      { return std::__addressof(_M_instance[0]); }

      const _Tp*
      data() const
      { return std::__addressof(_M_instance[0]); }
    };

  // Array comparisons.
  template<typename _Tp, std::size_t _Nm>
    inline bool
    operator==(const array<_Tp, _Nm>& __one, const array<_Tp, _Nm>& __two)
    { return std::equal(__one.begin(), __one.end(), __two.begin()); }

  template<typename _Tp, std::size_t _Nm>
    inline bool
    operator!=(const array<_Tp, _Nm>& __one, const array<_Tp, _Nm>& __two)
    { return !(__one == __two); }

  template<typename _Tp, std::size_t _Nm>
    inline bool
    operator<(const array<_Tp, _Nm>& __a, const array<_Tp, _Nm>& __b)
    {
      return std::lexicographical_compare(__a.begin(), __a.end(),
					  __b.begin(), __b.end());
    }

  template<typename _Tp, std::size_t _Nm>
    inline bool
    operator>(const array<_Tp, _Nm>& __one, const array<_Tp, _Nm>& __two)
    { return __two < __one; }

  template<typename _Tp, std::size_t _Nm>
    inline bool
    operator<=(const array<_Tp, _Nm>& __one, const array<_Tp, _Nm>& __two)
    { return !(__one > __two); }

  template<typename _Tp, std::size_t _Nm>
    inline bool
    operator>=(const array<_Tp, _Nm>& __one, const array<_Tp, _Nm>& __two)
    { return !(__one < __two); }

  // Specialized algorithms [6.2.2.2].
  template<typename _Tp, std::size_t _Nm>
    inline void
    swap(array<_Tp, _Nm>& __one, array<_Tp, _Nm>& __two)
    { __one.swap(__two); }

  // Tuple interface to class template array [6.2.2.5].

  /// tuple_size
  template<typename _Tp>
    class tuple_size;

  /// tuple_element
  template<std::size_t _Int, typename _Tp>
    class tuple_element;

  template<typename _Tp, std::size_t _Nm>
    struct tuple_size<array<_Tp, _Nm> >
    { static const std::size_t value = _Nm; };

  template<typename _Tp, std::size_t _Nm>
    const std::size_t
    tuple_size<array<_Tp, _Nm> >::value;

  template<std::size_t _Int, typename _Tp, std::size_t _Nm>
    struct tuple_element<_Int, array<_Tp, _Nm> >
    { typedef _Tp type; };

  template<std::size_t _Int, typename _Tp, std::size_t _Nm>
    inline _Tp&
    get(array<_Tp, _Nm>& __arr)
    { return __arr[_Int]; }

  template<std::size_t _Int, typename _Tp, std::size_t _Nm>
    inline const _Tp&
    get(const array<_Tp, _Nm>& __arr)
    { return __arr[_Int]; }

_GLIBCXX_END_NAMESPACE_VERSION
} // namespace

#endif // _GLIBCXX_ARRAY
#else
#include <array>
#endif // PYPLUSPLUS
