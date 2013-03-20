from pygccxml.declarations import matcher, matchers

# re-exported for convenience
DeclarationNotFound = matcher.declaration_not_found_t
MultipleDeclarationsFound = matcher.multiple_declarations_found_t


class namespace_contains_matcher_t(matchers.declaration_matcher_t):
    def __init__(self, namespace, recurse=False):
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
