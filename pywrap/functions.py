from pygccxml.declarations import templates
from pyplusplus.module_builder import call_policies


def convert_vector_of_references_return_type(fun):
    """
    Adds a wrapper that returns a vector of copies instead of a vector
    of reference_wrappers.

    Note that you need explicitly register the return type at the moment:
        PYPP_INSTANTIATE(std::vector<T>);
    """
    try:
        container, args = templates.split(fun.return_type.decl_string)
        if not container.endswith('std::vector'):
            return False
        maybe_reference, args = templates.split(args[0])
        if not maybe_reference.endswith('boost::reference_wrapper'):
            return False
    except AssertionError:
        return False
    fun.parent.include_files.append('pywrap/reference_wrapper.hpp')
    fun.parent.include_files.append('boost/type_traits.hpp')
    fun.parent.add_registration_code(
        ('def("{name}", &convert_vector_of_references_return_type< '
         '{klass}, boost::remove_cv<{value}>::type, &{klass}::{name}'
         '>().apply)').format(
             name=fun.name, klass=fun.parent.decl_string, value=args[0]))
    fun.exclude()
    # FIXME: Automatically register an appropriate indexing_suite?
    return True


def return_optional_by_value(fun):
    """
    Sets a call policy that will unpack `boost::optional` return values
    to the contained type, which will be returned by-value.
    If the return value is `boost::none`, `None` will be returned.
    """
    try:
        klass, args = templates.split(fun.return_type.decl_string)
        if not (klass.endswith('boost::optional') or klass.endswith('boost::tuples::tuple')):
            return False
    except AssertionError:
        return False
    fun.parent.include_files.append('pywrap/return_optional.hpp')
    fun.call_policies = call_policies.return_value_policy(
        'return_optional_by_value')
    return True
