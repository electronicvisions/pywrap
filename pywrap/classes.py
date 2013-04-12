"""utility functions to be applied on classes"""

import collections

def get_all_bases(cls, only_public = True ):
    """Returns recursivly all (public) bases of a class"""
    if only_public:
        return [ x.related_class for x in cls.recursive_bases if x.access == 'public']
    else:
        return [ x.related_class for x in cls.recursive_bases ]

def get_casting_operators(cls, *types):
    cls = get_all_bases(cls) + [cls]
    ops = []
    for c in cls:
        tmp = c.casting_operators(access_type_matcher_t('public'), allow_empty = True)
        ops.extend(tmp.to_list())


_numpy_construtor_decl_code = '#include "create_constructor.hpp"'
_numpy_construtor_reg_code = (
        'def( "__init__", boost::python::make_constructor(&HMF::pyplusplus::create_constructor< {} >::construct))',
)

def add_numpy_construtor(c):
    c.add_declaration_code(_numpy_construtor_decl_code)
    for code in _numpy_construtor_reg_code:
        c.add_registration_code(code.format(c.decl_string))

_array_operator_include  = '#include "expose_array_operator.hpp"'
_array_operator_code = 'def(::HMF::pyplusplus::expose_array_operator( (%(type)s)(%(op)s), %(policy)s ))'

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
    ctor = c.find_copy_constructor()
    if ctor and ctor.is_artificial and ctor.access_type == 'public':
        ctor.exportable = True
        ctor.is_artificial = False
        ctor.include()
