import re
import logging

import classes
from matchers import (
        access_type_matcher_t, custom_matcher_t,
        namespace_contains_matcher_t, declaration_not_found_t,
        match_std_container_t
)
from pyplusplus.decl_wrappers import namespace_t, class_t

def find(namespace, groups, filters, allow_empty=False):
    """Yields all objects in groups ('classes', 'namespaces', ...)
    that match one of the given filters.  By default raises an error
    if a filter did not match in any group."""

    if isinstance(groups, basestring):
        groups = re.split(r'\W+', groups)

    groups = set(groups)

    for f in filters:
        matched = False

        for name in groups:
            group = getattr(namespace, name)
            for obj in group(f, allow_empty=True):
                matched = True
                yield obj

        if not (allow_empty or matched):
            raise RuntimeError(
                'No match found for {} in [{}]'.format(
                    f, ', '.join(groups)
                ))


def exclude(ns, groups, filters, allow_missing=False):
    """Prevents declarations that match one of the filters from being exported.
    By default raises an error if a filter did not match in any group."""

    for obj in find(ns, groups, filters, allow_missing):
        obj.exclude()


def include(ns, groups, filters, allow_missing=False):
    """Includes declarations that match one of the filters.
    By default raises an error if a filter did not match in any group."""

    for obj in find(ns, groups, filters, allow_missing):
        obj.include()


def exclude_by_access_type(ns, groups, t):
    """Prevents certain declarations from being exported based on their access type:
    >>> exclude_by_access_type(mb, ['variables', 'calldefs', 'classes'], 'protected')
    """

    exclude(ns, groups, [access_type_matcher_t(t)], True)


def exclude_by_regex(ns, groups, pattern):
    """Prevents certain declarations from being exported based on their name:
    >>> exclude_by_regex(mb, ['calldefs'], r'(^_[^_])|(.*Cpp$)|(^impl$)')
    """

    regex = pattern if hasattr(pattern, 'match') else re.compile(pattern)
    member_filter = custom_matcher_t(lambda decl: regex.match(decl.name))

    exclude(ns, groups, [member_filter], True)

def extend_array_operators(ns, recurse=True):
    """Expose the operator[] of all matching classes with __setitem__ support, 
    when possible
    """
    for c in ns.classes(namespace_contains_matcher_t(ns.name, recurse), allow_empty=True):
        classes.add_array_operators(c)

def include_default_copy_constructors(ns):
    """Expose the default copy constructor of all matching classes
    """
    for c in ns.classes(allow_empty = True):
        classes.add_default_copy_construtor(c)

def get_deps(ns, matcher = lambda : True, recurse=True):
    decls = set()
    if not hasattr(ns, "declarations"):
		return decls
    for decl in ns.declarations:
        if not decl.ignore and recurse or not isinstance(decl, namespace_t):
            for deps in  decl.i_depend_on_them():
                d = [ decl for decl in deps.find_out_depend_on_it_declarations() if matcher(decl) ]
                decls.update(d)
    return decls

# We need to wrap the generated code to print but ignore errors
# as creating aliases for typedefs may trigger attribute errors
# if the target type was not found or has been renamed.
_exception_wrapper = '''try {
    %s
} catch(bp::error_already_set) {
    // Print exception but allow loading to continue.
    if (PyErr_Occurred()) PyErr_Print();
}'''

_ns_typedef = 'bp::scope().attr("%s") = bp::scope().attr("%s");'
_cls_typedef = 'bp::scope().attr("%s").attr("%s") = bp::scope().attr("%s");'

def expose_typedefs(mb, ns, recurse=True, cross_namespace_aliases=True):
    log = logging.getLogger('pywrap.typedefs.aliases')
    log.info('Searching namespace %s for typedefs.', ns.name)

    ns_matcher = namespace_contains_matcher_t(ns.name, recurse)

    for td in ns.typedefs(ns_matcher, allow_empty=True):
        td.exclude()
        to_log = ' %s::%s ' % (td.parent.name, td.name)
        try:
            target = mb.class_(td.type.decl_string)
            to_log += ' -> ' + str(target.name) + ': '
        except declaration_not_found_t:
            to_log += ' target "%s" not found' % td.type.decl_string
            log.info(to_log)
            continue

        # TODO: By enforcing target to be contained in the same ns
        # aliases like BaseType<bool>.value_type will be skipped
        # as bool is not contained in the same namespace.
        # Targets in other namespaces would however require
        # different code in _ns_typedef and _cls_typedef.
        if (not (cross_namespace_aliases
                or ns_matcher(target)
                or namespace_contains_matcher_t("::std")(target)
                or not target.indexing_suite is None)):
            to_log += ' target "%s" in diffrent namespace' % td.type.decl_string
            log.info(to_log)
            continue

        target.include()

        # Typedefs in this namespace
        if isinstance(td.parent, namespace_t):
            to_log += 'New alias: %s -> %s' % (td.name, target.alias)
            mb.add_registration_code(_exception_wrapper % (
                _ns_typedef % (td.name, target.alias)))

        # Public typdefs in classes of this namespace
        elif (access_type_matcher_t('public')(td) and
                isinstance(td.parent, class_t)):

            to_log += 'New alias: %s::%s -> %s' % (
                    td.parent.alias, td.name, target.alias)
            mb.add_registration_code(_exception_wrapper % (
                _cls_typedef % (td.parent.alias, td.name, target.alias)))

        else:
            to_log += 'ignored'
        log.info(to_log)

_rant_filter_re = re.compile(r"integral_range<[^>]*>")
def getRants(ns):
    try:
        f = custom_matcher_t(lambda decl: _rant_filter_re.match(decl.name))
        return [c for c in ns.classes(f)]
    except RuntimeError:
        return []
