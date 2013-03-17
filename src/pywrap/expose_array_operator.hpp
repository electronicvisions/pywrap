#pragma once

#include <type_traits>
#include <boost/python.hpp>


namespace HMF 
{
namespace pyplusplus
{

namespace detail
{

	template <class classT, class Traits, bool ret_is_ref>
	struct make_setitem 
	{
		static void def(classT&) {}
	};
	
	template <class classT, class Traits>
	struct make_setitem<classT, Traits, true>
	{
		typedef typename Traits::class_type    class_type;
		typedef typename Traits::return_type   op_return_type;
		typedef typename Traits::key_type      key_type;
		typedef typename std::conditional<
			std::is_integral< typename std::decay<op_return_type>::type >::value,
			typename std::decay<op_return_type>::type,	
			op_return_type	
				>::type value_type;

		static void def(classT& c)
		{
			c.def("__setitem__", &setitem, boost::python::default_call_policies());
		}

		static void setitem(class_type & t, key_type k, value_type v)
		{
			t[k] = v;
		}
	};

	template <typename ReturnValue>
	struct array_operator_default_policy
	{
		typedef typename std::conditional<
			std::is_reference< ReturnValue >::value,
			boost::python::return_value_policy<boost::python::copy_non_const_reference>,
			boost::python::default_call_policies
				>::type integral_policy;

		typedef typename std::conditional<
			std::is_integral< typename std::decay<ReturnValue>::type >::value,
			integral_policy,	
			boost::python::return_internal_reference<>
				>::type type;
	};
}


template <typename T, typename Operator, typename Ret, typename Key>
struct array_operator_visitor_traits
{
	typedef T class_type;
	typedef Operator operator_type;
	typedef Ret return_type;
	typedef Key key_type;

	static const bool ret_is_ref = std::is_reference<return_type>::value 
		&& !std::is_const<return_type>::value;
};

template <typename Traits, typename Policy>
class array_operator_visitor : 
 	public boost::python::def_visitor< array_operator_visitor<Traits, Policy> >
{
public:
	typedef typename Traits::operator_type operator_type;
	typedef typename Traits::class_type class_type;

	array_operator_visitor(operator_type op, Policy p) : 
		operator_fun(op),
		policy(p)
	{}

    template <class classT>
    void visit(classT& c) const
    {
		static_assert(std::is_same< typename classT::wrapped_type, class_type>::value,
				"operator member function, does not match class type");
        c.def("__getitem__", operator_fun, Policy());
		detail::make_setitem<classT, Traits, Traits::ret_is_ref>::def(c);
    }


private:
	operator_type operator_fun;
	Policy policy;
};

template<typename T, typename Ret, typename Arg, class Policy = typename detail::array_operator_default_policy<Ret>::type> 
array_operator_visitor<
		array_operator_visitor_traits<T, Ret (T::*)(Arg), Ret, Arg>,
		Policy>
expose_array_operator( Ret (T::*op)(Arg), Policy p = Policy())
{
	typedef Ret (T::* Operator )(Arg);
	return array_operator_visitor<
		array_operator_visitor_traits<T, Operator, Ret, Arg>,
		Policy>(op, p);
}

template<typename T, typename Ret, typename Arg, class Policy = typename detail::array_operator_default_policy<Ret>::type> 
array_operator_visitor<
		array_operator_visitor_traits<T, Ret (T::*)(Arg) const, Ret, Arg>,
		Policy>
expose_array_operator( Ret (T::*op)(Arg) const, Policy p = Policy())
{
	typedef Ret (T::* Operator )(Arg) const;
	return array_operator_visitor<
		array_operator_visitor_traits<T, Operator, Ret, Arg>,
		Policy>(op, p);
}

} // end pyplusplus
} // end HMF

