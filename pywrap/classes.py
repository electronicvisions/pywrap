"""utility functions to be applied on classes"""

import collections, re
import matchers
from matchers import access_type_matcher_t, declaration_not_found_t

def get_all_bases(cls, only_public = True ):
    """Returns recursivly all (public) bases of a class"""
    if only_public:
        return [ x.related_class for x in cls.recursive_bases if x.access == 'public']
    else:
        return [ x.related_class for x in cls.recursive_bases ]


def add_int_value_operator(c, allow_empty=False):
    match_int   = matchers.match_casting_int_operator_t()
    reg_code = ('def(int_(bp::self))', 'def(long_(bp::self))')
    _add_value_operator(c, match_int, reg_code, allow_empty)

def add_float_value_operator(c, allow_empty=False):
    match_float = matchers.match_casting_float_operator_t()
    reg_code = ('def(float_(bp::self))')
    _add_value_operator(c, match_int, reg_code, allow_empty)

def _add_value_operator(c, matcher, reg_code, allow_empty):
    cls = [c] + get_all_bases(c)
    ops = []
    for x in cls:
        tmp = x.casting_operators(access_type_matcher_t('public'), recursive=False, allow_empty=True)
        ops.extend(tmp.to_list())
    for op in ops:
        if matcher(op):
            for code in reg_code:
                c.add_registration_code(code)
                return
    if not allow_empty:
        raise RuntimeError("Could not find value operator for " + c.name)


_numpy_construtor_decl_code = '#include "pywrap/create_constructor.hpp"'
_numpy_construtor_reg_code = (
        'def( "__init__", boost::python::make_constructor(&::pywrap::create_constructor< {} >::construct))',
)

def add_numpy_construtor(c):
    c.add_declaration_code(_numpy_construtor_decl_code)
    for code in _numpy_construtor_reg_code:
        c.add_registration_code(code.format(c.decl_string))

_array_operator_include  = '#include "pywrap/expose_array_operator.hpp"'
_array_operator_code = 'def(::pywrap::expose_array_operator( (%(type)s)(%(op)s), %(policy)s ))'

def add_array_operators(c, policy = None, value_type = None):
    ops = c.member_operators("operator[]", allow_empty=True).to_list()
    by_arguments = collections.defaultdict(list)
    for op in ops:
        op.exclude()
        arg = op.argument_types[0]
        by_arguments[arg.decl_string].append(op)

    # If there are 2 operators with the same argument type one
    # of them must be a const versions
    # We try to use the non const version
    for operators in by_arguments.values():
        assert len(operators) < 3
        op = operators[0]
        if op.has_const and len(operators) > 1:
            op = operators[1]

        subs = {
                "type"  : op.decl_string,
                "policy" : policy if policy else op.call_policies.create(None),
                "op"     :  "&" + op.parent.decl_string + "::" + op.name,
                }
        if value_type is not None:
            subs["policy"] += ", " + value_type
        c.add_declaration_code(_array_operator_include)
        c.add_registration_code( _array_operator_code % subs)


def add_default_copy_construtor(c):
    """Redefines the properties of the default copy construtor, to allow
    Py++ to include it"""
    if c.noncopyable:
        return
    copy_ctor = c.find_copy_constructor()
    default_ctor = c.find_trivial_constructor()
    if copy_ctor and copy_ctor.is_artificial and copy_ctor.access_type == 'public':
        copy_ctor.exportable = True
        copy_ctor.is_artificial = False
        copy_ctor.include()
        if default_ctor and default_ctor.is_artificial:
            default_ctor.exportable = True
            default_ctor.is_artificial = False
            default_ctor.include()


_remove_ns = re.compile(r"\w+::")
_clean_numbers = re.compile(r"\b(\d+)\w*")
def beautify_rant_name(c):
    n = c.name
    n = re.sub(r"\(.+?\)", "", n)
    n = re.sub(_remove_ns, "", n)
    n = re.sub(_clean_numbers, "\g<1>", n)
    n = re.sub(r"\s+", "", n) # remove spaces
    n = re.sub(r"[<>,]+", "_", n) # <> => _
    n = re.sub(r"integral_constant_[^_]*_", "", n)
    n = re.sub(r"-", "n", n)
    c.rename(n[:-1])
