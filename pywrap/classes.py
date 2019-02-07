"""utility functions to be applied on classes"""

import collections
import logging
import re
import textwrap
from copy import copy

from . import matchers
from .matchers import access_type_matcher_t, declaration_not_found_t
from pygccxml.declarations import ACCESS_TYPES, templates

log = logging.getLogger('pywrap.classes')

def get_all_bases(cls, only_public = True ):
    """Returns recursivly all (public) bases of a class"""
    if only_public:
        return [ x.related_class for x in cls.recursive_bases if x.access == 'public']
    else:
        return [ x.related_class for x in cls.recursive_bases ]

def has_default_constructor(c):
    def default_callable(args):
        for a in args:
            if getattr(a, 'default_value', None) is None:
                return False
        return True

    return any(default_callable(x.arguments) for x in c.constructors())


def add_comparison_operators(c, disable_all=False):
    c.include_files.append('pywrap/operator_helper.hpp')

    for op in ('<', '<=', '>', '>=', '==', '!='):
        try:
            o = c.member_operator(symbol=op)
            o.exclude()
            log.info("exclude operator {}".format(o))
        except RuntimeError: pass

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

_pyiterable_converter_includes = ('pywrap/from_pyiterable.hpp', )
_pyiterable_converter_reg_code = '::pywrap::iterable_converter().from_python< {} >();'

def add_from_pyiterable_converter_to(cls, base = None):
    """Adds a generic converter to a STL container (@cls) from a Python iterable.
    @base can be specified to specifiy where (i.e. a class) to add the wrapper code.
    """
    if base is None:
        base = cls
    base.include_files.extend(_pyiterable_converter_includes)
    base.add_registration_code(_pyiterable_converter_reg_code.format(cls.decl_string), works_on_instance=False)

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


def add_pickle_suite(c, serialization_framework='boost'):
    c.include_files.append('pywrap/pickle_suite_{}.hpp'.format(serialization_framework))
    c.add_registration_code(
        'def_pickle(HMF::pyplusplus::pickle_suite_{}< {} >())'.format(
            serialization_framework, c.create_decl_string()))

def add_to_and_from_json(c): # only for cereal
    c.include_files.append('cereal/archives/json.hpp')
    c.add_registration_code(
        'def("to_json", \
             bp::make_function( \
                 []({0}& t){{ \
                     std::stringstream ss; \
                     {{ \
                         cereal::JSONOutputArchive archive(ss); \
                         archive(t); \
                     }} \
                     return ss.str();\
                 }}, \
                 bp::default_call_policies(), \
                 boost::mpl::vector< std::string, {0} >()))'.format(c.partial_decl_string))
    c.add_registration_code(
        'def("from_json", \
             bp::make_function( \
                 []({0}& t, std::string const& s){{ \
                     {{ \
                         std::stringstream ss(s); \
                         cereal::JSONInputArchive archive(ss); \
                         archive(t); \
                     }} \
                 }}, \
                 bp::default_call_policies(), \
                 boost::mpl::vector< void, {0}, std::string >()))'.format(c.partial_decl_string))


def add_context_manager(c, exit_callee=None):
    """Adds context manager stuff (__enter__(self) and __exit__(self, exc_type,
    exc_value, traceback)) to wrapped class"""
    # __enter__ just returns *the* referenced object - lifetime bound to t == itself
    c.add_registration_code(
        'def("__enter__", bp::make_function( []({0} & t) -> {0} & {{ return t; }}, \
             bp::return_internal_reference<>(), \
             boost::mpl::vector< {0} &, {0} & >()))'.format(c.partial_decl_string))
    if exit_callee is None:
        exit_call = ""
    else:
        # call the exit_callee function which is expected to be a member
        # function without arguments
        exit_call = "t.{}();".format(exit_callee.partial_name)
    c.add_registration_code(
        'def("__exit__", bp::make_function( []({0} & t, bp::object, bp::object, bp::object) {{ \
                {1} \
                return false; \
             }}, \
             bp::default_call_policies(), \
             boost::mpl::vector< bool, {0} &, bp::object, bp::object, bp::object >()))'.format(
                 c.partial_decl_string, exit_call))


def add_variant_converters_for(mb, cl):
    """
    Register to-python converters for boost::variant objects.
    (will copy contained type, see pywrap/variant_converter.hpp)

    Somehow mb.namespace('::boost').classes(allow_empty=True) does not
    contain the boost::variant class in the project this function was
    developed for, as a workaround we use:

        for td in namespace.typedefs(allow_empty=True):
           if not classes.add_variant_converters_for(mb, td.target_decl):
              continue
           # do other things with boost::variant class
    """
    if not templates.is_instantiation(cl.decl_string):
        return False
    name, args = templates.split(cl.decl_string)
    if not name == '::boost::variant':
        return False

    # Normally one would like to use cl.include_files.append() here, but
    # when "cl=td.target_decl", cl points to a
    # pyplusplus.decl_wrappers.class_wrapper.class_declaration_t
    # instead of a pyplusplus.decl_wrappers.class_wrapper.class_t object.
    mb.add_declaration_code('#include "pywrap/variant_converter.hpp"\n')
    mb.add_registration_code(textwrap.dedent("""
    typedef {variant} {alias};
    bp::to_python_converter<{alias}, variant_to_object<{alias}> >();
    """).format(variant=cl.decl_string, alias=cl.alias))
    for arg in args:
        if arg == 'boost::detail::variant::void_':
            continue
        mb.add_registration_code(textwrap.dedent("""
        bp::implicitly_convertible<{from_type}, {variant}>();
        """).format(variant=cl.alias, from_type=arg))
    return True


def add_optional_vector_wrapper_for(mb, variable):
    if not templates.is_instantiation(variable.type.decl_string):
        return False
    name, args = templates.split(variable.type.decl_string)
    if not name == '::boost::optional':
        return False
    assert(len(args) == 1)
    vec, v_type = templates.split(args[0])

    mb.add_registration_code(textwrap.dedent(
    """
    bp::class_<{optional}>("{optional}", bp::init<>()) // support default non-construct init
        .def("is_initialized", &{optional}::is_initialized)
        .def("value", &{optional}::value, bp::return_internal_reference<>())
        .add_property("access", +[]({optional} const & self){{return *self;}}, +[]({optional}  self , bp::object& value)
            {{
                auto& vect = *self;
                vect.clear();
                for ( auto it = bp::stl_input_iterator< {v_type} > (value); it != bp::stl_input_iterator< {v_type} > (); it++) {{
                    vect.push_back(*it);
                }}
                self = vect;
            }} )
        ;
    ;
    """).format(optional=variable.type.decl_string, alias=args[0], v_type=v_type[0]))
    return True


def add_omp_safe_virtual_functions(cls, *args, **kwargs):
    """
    Adds OMP based locking around callback to python in virtual function overrides
    """

    cls.include_files.append("pywrap/omp_helper.hpp")
    cls.add_wrapper_code('pywrap::OMPLock lock;')
    for fun in cls.mem_funs(*args, **kwargs):
        fun.add_override_precall_code('pywrap::ScopedOMPGuard guard(lock);')
        fun.add_override_native_precall_code('guard.unlock();')

