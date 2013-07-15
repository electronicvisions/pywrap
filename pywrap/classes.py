"""utility functions to be applied on classes"""

import collections, re
import matchers
from matchers import access_type_matcher_t, declaration_not_found_t
from pygccxml.declarations import ACCESS_TYPES
import logging
from copy import copy
log = logging.getLogger('pywrap.classes')

def get_all_bases(cls, only_public = True ):
    """Returns recursivly all (public) bases of a class"""
    if only_public:
        return [ x.related_class for x in cls.recursive_bases if x.access == 'public']
    else:
        return [ x.related_class for x in cls.recursive_bases ]

def add_comparison_operators(c, disable_all=False):
    c.include_files.append('pywrap/operator_helper.hpp')

    if c.equality_comparable and not disable_all:
        log.info("{} has ==, adding != operator".format(c))
        c.add_registration_code('def(bp::self == bp::self)')
        c.add_registration_code('def("__ne__", &pywrap::comparator_ne)')

        if c.less_than_comparable:
            log.info("{} has <, adding <=, >, >= operators".format(c))
            c.add_registration_code('def(bp::self < bp::self)')
            c.add_registration_code('def("__ge__", &pywrap::comparator_ge)')
            c.add_registration_code('def("__gt__", &pywrap::comparator_gt)')
            c.add_registration_code('def("__le__", &pywrap::comparator_le)')
            return

    else:
        if c.less_than_comparable:
            raise RuntimeError(
                "Class has operator< but not operator==: {}".format(c))

        log.info("{} does not have == and != operators".format(c))
        c.add_registration_code('def("__eq__", &pywrap::comparator_not_implemented)')
        c.add_registration_code('def("__ne__", &pywrap::comparator_not_implemented)')

    log.info("{} does not have <, <=, >, >= operators".format(c))
    c.add_registration_code('def("__lt__", &pywrap::comparator_not_implemented)')
    c.add_registration_code('def("__le__", &pywrap::comparator_not_implemented)')
    c.add_registration_code('def("__ge__", &pywrap::comparator_not_implemented)')
    c.add_registration_code('def("__gt__", &pywrap::comparator_not_implemented)')


_numpy_construtor_includes = ('pywrap/create_constructor.hpp', )
_numpy_construtor_reg_code = (
        'def( "__init__", boost::python::make_constructor(&::pywrap::create_constructor< {} >::construct))',
)

def add_numpy_construtor(c):
    c.include_files.extend(_numpy_construtor_includes)
    for code in _numpy_construtor_reg_code:
        c.add_registration_code(code.format(c.decl_string))

_array_operator_includes  = ("pywrap/expose_array_operator.hpp", )
_array_operator_code = 'def(::pywrap::expose_array_operator( (%(type)s)(%(op)s)%(policy)s ))'

def add_array_operators(c, policy = None, value_type = None):
    by_arguments = collections.defaultdict(list)
    for op in c.member_operators("operator[]", allow_empty=True):
        if op.parent != c:
            continue

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
                "policy" : (", " + policy) if policy else "",
                "op"     :  "&" + op.parent.decl_string + "::" + op.name,
                }
        if value_type is not None:
            subs["policy"] += ", " + value_type
        c.include_files.extend(_array_operator_includes)
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


def expose_std_hash(c):
    """Links Python hashing operator to std::hash::operator()"""
    stdhash = 'std::hash'
    s = 'hash< %s >' % c.partial_decl_string
    # TODO: add allow_empty option and search for std::hash < CLASS >::operator()
    c.add_registration_code(
        'def("__hash__", \
             bp::make_function( \
                 []({0} t){{ \
                     return {1}< {0} >()(t); \
                 }}, \
                 bp::default_call_policies(), \
                 boost::mpl::vector<size_t, {0} >()))'.format(c.partial_decl_string, stdhash))


def add_context_manager(c):
    """Adds context manager stuff (__enter__(self) and __exit__(self, exc_type,
    exc_value, traceback)) to wrapped class"""
    # __enter__ just returns *the* referenced object - lifetime bound to t == itself
    c.add_registration_code(
        'def("__enter__", bp::make_function( []({0} & t) -> {0} & {{ return t; }}, \
             bp::return_internal_reference<>(), \
             boost::mpl::vector< {0} &, {0} & >()))'.format(c.partial_decl_string))
    # check if python exception occured in context and just pass it on
    c.add_registration_code(
        'def("__exit__", bp::make_function( []({0} const &, bp::object a, bp::object, bp::object) {{ \
                return false; \
             }}, \
             bp::default_call_policies(), \
             boost::mpl::vector< bool, {0} const &, bp::object, bp::object, bp::object >()))'.format(c.partial_decl_string))
