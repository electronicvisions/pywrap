import re

from pygccxml.declarations.matchers import (
    access_type_matcher_t, custom_matcher_t
)


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
