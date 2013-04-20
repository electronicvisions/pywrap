from pygccxml.declarations import cpptypes, matcher, matchers, templates, type_traits

from pygccxml.declarations.matchers import *
from pygccxml.declarations.matcher import matcher
declaration_not_found_t       = matcher.declaration_not_found_t
multiple_declarations_found_t = matcher.multiple_declarations_found_t

from pyplusplus.decl_wrappers.calldef_wrapper import casting_operator_t


class namespace_contains_matcher_t(matchers.declaration_matcher_t):
    """
    Instance of this class will match declaration by the namespace containing
    the declaration. If recurse is true also declaration in a subnamespace
    are matched.
    """
    def __init__(self, namespace, recurse=False):
        """
        :param access_type: namespace name
        :type access_type: :class: `str`
        :param access_type: recurse recurse into subnamespaces
        """
        super(namespace_contains_matcher_t, self).__init__(name=namespace)
        self.recurse = recurse

    def __call__(self, decl):
        p = decl.parent
        # Find containing namespace
        while not isinstance(p, matchers.namespace.namespace_t):
            p = p.parent
            if p is None:
                return False
        # Check if the the right one (and recurse if required)
        while p is not None:
            if self.check_name(p):
                return True
            if self.recurse:
                p = p.parent
            else:
                return False
        return False

    def __str__(self):
        return '(in namespace %s)' % self.ns


class match_std_container_t(matchers.declaration_matcher_t):
    def __init__(self, container):
        super(match_std_container_t, self).__init__(name=container)
        self.ns_matcher = namespace_contains_matcher_t("std")

    def __call__(self, decl):
        return self.ns_matcher(decl) and templates.name(decl.name) == self.name

class match_casting_operator_t(matchers.matcher_base_t):
    def __init__(self, return_types):
        self.return_types = return_types

    def __call__(self, decl):
        if not isinstance(decl, casting_operator_t):
            return False
        if self.return_types:
            base = type(type_traits.base_type(decl.return_type))
            return base in self.return_types
        else:
            return True

class match_casting_int_operator_t(match_casting_operator_t):
    def __init__(self):
        super(match_casting_int_operator_t, self).__init__(return_types=[
                cpptypes.char_t,
                cpptypes.signed_char_t,
                cpptypes.unsigned_char_t,
                cpptypes.wchar_t,
                cpptypes.short_int_t,
                cpptypes.short_unsigned_int_t,
                cpptypes.bool_t,
                cpptypes.int_t,
                cpptypes.unsigned_int_t,
                cpptypes.long_int_t,
                cpptypes.long_unsigned_int_t,
                cpptypes.long_long_int_t,
                cpptypes.long_long_unsigned_int_t,
        ])


class match_casting_float_operator_t(match_casting_operator_t):
    def __init__(self):
        super(match_casting_float_operator_t, self).__init__(return_types=[
                cpptypes.float_t,
                cpptypes.double_t,
                cpptypes.long_double_t,
        ])

