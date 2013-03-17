#pragma once

#include <functional>
#include <type_traits>
#include <boost/python.hpp>

namespace HMF 
{
namespace pyplusplus
{

namespace detail
{
	struct array_operator_auto_value_type {};
	struct array_operator_auto_policy_type {};

	template<bool is_integral, bool is_ref, bool is_const>
	struct auto_policy_type {
		typedef boost::python::default_call_policies type;
	};
	
	template<>
	struct auto_policy_type<true, true, true> {
		typedef boost::python::return_value_policy<boost::python::copy_const_reference> type;
	};

	template<>
	struct auto_policy_type<true, false, true> {
		typedef boost::python::return_value_policy<boost::python::copy_non_const_reference> type;
	};

	template<bool is_const>
	struct auto_policy_type<false, true, is_const>  {
		typedef boost::python::return_internal_reference<> type;
	};

	template <typename ValueType, typename Policy>
	struct array_operator_get_policy
	{
		static const bool is_intergral = std::is_integral< typename std::decay<ValueType>::type >::value;
		static const bool is_ref =  std::is_reference< ValueType >::value;
		static const bool is_const = std::is_const<typename std::remove_reference<ValueType>::type>::value;

		typedef typename std::conditional< 
			std::is_same<Policy, array_operator_auto_policy_type>::value,
			typename auto_policy_type<is_intergral, is_ref, is_const>::type,
			Policy
			>::type type;
	};

	template <typename ReturnType, typename ForcedValueType>
	struct array_operator_get_value_type
	{
		static const bool has_setter_value_type = 
			!std::is_same<ForcedValueType, array_operator_auto_value_type>::value;
	
		typedef typename std::conditional<
			std::is_integral< typename std::decay<ReturnType>::type >::value,
			typename std::decay<ReturnType>::type,	
			ReturnType	
				>::type deduced_value_type;

		typedef typename std::conditional< has_setter_value_type, 
			ForcedValueType,
			deduced_value_type
			>::type type;
	};

	template <typename Operator,
			 typename Policy = array_operator_auto_policy_type,
			 typename ForcedValueType = array_operator_auto_value_type>
	struct array_operator_traits
	{
		static_assert(sizeof(Operator) == 0, "First template argument must be a member function pointer");
	};

	template <typename T, typename Ret, typename KeyValue, 
			 typename Policy, typename ForcedValueType>
	struct array_operator_traits<Ret (T::*)(KeyValue), Policy, ForcedValueType>
	{
	public:
		static_assert(!std::is_pointer<Ret>::value, "This is not intended to handle pointers, sry");
		typedef Ret (T::* operator_type)(KeyValue);
		typedef T        class_type;
		typedef KeyValue key_type;
		typedef typename array_operator_get_value_type<Ret, ForcedValueType>::type value_type;
		typedef typename array_operator_get_policy<value_type, Policy>::type  policy_type;

		static const bool make_setitem = std::is_same<value_type, ForcedValueType>::value ||
			(std::is_reference<Ret>::value && !std::is_const<typename std::remove_reference<Ret>::type>::value);
	};

	template <typename T, typename Ret, typename KeyValue, 
			 typename Policy, typename ForcedValueType>
	struct array_operator_traits<Ret (T::*)(KeyValue) const, Policy, ForcedValueType>
	{
	public:
		static_assert(!std::is_pointer<Ret>::value, "This is not intended to handle pointers, sry");
		typedef Ret (T::* operator_type)(KeyValue) const;
		typedef T        class_type;
		typedef KeyValue key_type;
		typedef typename array_operator_get_value_type<Ret, ForcedValueType>::type value_type;
		typedef typename array_operator_get_policy<value_type, Policy>::type  policy_type;

		static const bool make_setitem = false;
//			(std::is_reference<value_type>::value && !std::is_const<value_type>::value);
	};

	template <class classT, class Traits, bool>
	struct make_setitem 
	{
		typedef typename Traits::operator_type operator_type;
		static void def(classT&, operator_type) {}
	};
	
	template <class classT, class Traits>
	struct make_setitem<classT, Traits, true>
	{
		typedef typename Traits::class_type    class_type;
		typedef typename Traits::key_type      key_type;
		typedef typename Traits::value_type    value_type;
		typedef typename Traits::operator_type operator_type;

		static void def(classT& c, operator_type op) {
			auto setitem_f = std::bind(&setitem, std::placeholders::_1, std::placeholders::_2, std::placeholders::_3, op);
			auto f = boost::python::make_function(setitem_f,
					boost::python::default_call_policies(),
					boost::mpl::vector<void, class_type, key_type, value_type>());
			c.def("__setitem__", f);
		}

		static void setitem(class_type & t, key_type k, value_type v, operator_type op) {
			(t.*op)(k) = v;
		}
	};

}

template <typename Traits>
class array_operator_visitor : 
 	public boost::python::def_visitor< array_operator_visitor<Traits> >
{
public:
	typedef Traits                         traits_type;
	typedef typename Traits::operator_type operator_type;
	typedef typename Traits::class_type    class_type;
	typedef typename Traits::value_type    value_type;
	typedef typename Traits::key_type      key_type;
	typedef typename Traits::policy_type   policy_type;

	array_operator_visitor(operator_type op, policy_type po = policy_type()) : 
		operator_fun(op),
		policy(po)
	{}

    template <class classT>
    void visit(classT& c) const
    {
		static_assert(std::is_same< typename classT::wrapped_type, class_type>::value,
				"operator member function, does not match class type");
		auto getitem_f = std::bind(&getitem, std::placeholders::_1, std::placeholders::_2, operator_fun);
		auto boost_f = boost::python::make_function(getitem_f,
				policy,
				boost::mpl::vector<value_type, class_type, key_type>());
        c.def("__getitem__", boost_f); 
		detail::make_setitem<classT, Traits, Traits::make_setitem>::def(c, operator_fun);
    }
	
	static value_type getitem(class_type & t, key_type key, operator_type op)
	{
		return (t.*op)(key);
	}

private:
	operator_type operator_fun;
	policy_type policy;
};

template<typename Operator>
array_operator_visitor< detail::array_operator_traits<Operator> >
expose_array_operator( Operator op )
{
	typedef detail::array_operator_traits<Operator> Traits;
	return array_operator_visitor<Traits>(op);
}

template<typename Operator, typename Policy,
	typename ForcedValueType = detail::array_operator_auto_value_type> 
array_operator_visitor<
		detail::array_operator_traits<Operator, Policy, ForcedValueType> >
expose_array_operator( Operator op, Policy policy = Policy(), ForcedValueType = ForcedValueType() )
{
	return array_operator_visitor<
		detail::array_operator_traits<Operator, Policy, ForcedValueType>
		>(op, policy);
}

} // end pyplusplus
} // end HMF

