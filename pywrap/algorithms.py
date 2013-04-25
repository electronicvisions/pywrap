from pygccxml.declarations.namespace import namespace_t

def get_namespace(decl):
    p = decl
    ret = []
    while p:
        if isinstance(p, namespace_t):
            ret.append(p)
        p = p.parent
    return reversed(ret[:-1])

def get_namespace_names(decl):
    return [n.name for n in get_namespace(decl)]
