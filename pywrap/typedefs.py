import logging

from pygccxml.declarations.matchers import (
    namespace_matcher_t, access_type_matcher_t
)
from pywrap.matchers import namespace_contains_matcher_t, DeclarationNotFound

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


def make_aliases(mb, ns):
    log = logging.getLogger('pywrap.typedefs.aliases')
    log.debug('Searching namespace %s for typedefs.', ns.name)
    for td in ns.typedefs(allow_empty=True):
        log.debug('Found typedef %s in %s.', td.name, td.parent.name)
        try:
            target = mb.class_(td.type.decl_string)
            # TODO: By enforcing target to be contained in the same ns
            # aliases like BaseType<bool>.value_type will be skipped
            # as bool is not contained in the same namespace.
            # Targets in other namespaces would however require
            # different code in _ns_typedef and _cls_typedef.
            if (namespace_contains_matcher_t(ns.name)(target)
                    or target.indexing_suite is not None):
                target.include()
        except DeclarationNotFound:
            log.debug('Target not found: %s', td.type.decl_string)
            continue

        # Typedefs in this namespace
        if namespace_matcher_t(ns.name)(td.parent):
            log.info('New alias: %s -> %s', td.name, target.alias)
            mb.add_registration_code(_exception_wrapper % (
                _ns_typedef % (td.name, target.alias)))

        # Public typdefs in classes of this namespace
        elif (access_type_matcher_t('public')(td) and
                namespace_contains_matcher_t(ns.name)(td.parent)):

            log.info(
                'New alias: %s::%s -> %s',
                td.parent.alias, td.name, target.alias)
            mb.add_registration_code(_exception_wrapper % (
                _cls_typedef % (td.parent.alias, td.name, target.alias)))

        else:
            log.info('Skipping %s.', td.name)
