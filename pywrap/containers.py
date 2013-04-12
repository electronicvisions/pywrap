import collections, re

import classes
from matchers import match_std_container_t
from pygccxml.declarations import templates
from pyplusplus.module_builder import call_policies


def beautify_stl_container_names(ns):
    _STL_Containers.rename(ns)

def extend_std_containers(ns):
    _STL_Containers.expose(ns)

def get_stl_ontainers(ns, *names):
    ret = []
    for name, containers in _STL_Containers.find(ns, *names):
        ret.extend(containers)
    return ret

class _STL_Exposer(object):
    @classmethod
    def rename(cls, c):
        n = c.name
        n = n.replace('unsigned', 'u')
        # uppercase each word
        n = re.sub(r'\b(\w)', lambda m: m.group(1).upper(), n)
        # remove namespaces
        n = re.sub(r'\w+::', '', n)
        # isolate numbers
        n = re.sub(r'\b(\d+)\w*', r'\1', n)
        # remove spaces
        n = re.sub(r'\s+', '', n)
        # remove allocator<...> if same type
        n = re.sub(r'(?i)([^_]+)<([^_]+),allocator<\2>', r'\1<\2', n)
        # replace template chars
        n = re.sub(r'[<>,]+', '_', n)
        # remove duplicates
        n = re.sub(r'([^_]+_)\1', r'\1', n)
        c.rename(re.sub(r'^_+|_+$', '', n))

    @classmethod
    def expose(cls, c):
        cls.rename(c)

class _STL_Construct_from_numpy(_STL_Exposer):
    decl_code = '#include "create_constructor.hpp"'
    reg_code = (
            'def( "__init__", boost::python::make_constructor(&HMF::pyplusplus::create_constructor< {} >::construct))',
    )

    @classmethod
    def expose(cls, c):
        super(_STL_Construct_from_numpy, cls).expose(c)
        classes.add_numpy_construtor(c)

class _Bitset_STL_Exposer(_STL_Construct_from_numpy):
    bitset_re = re.compile(r"bitset<(\d*)\w*>")

    @classmethod
    def expose(cls, c):
        c.include()
        super(_Bitset_STL_Exposer, cls).expose(c)
        c.mem_opers().include()
        c.allow_implicit_conversion = True
        for f in c.member_functions(name = lambda x: x.name in ("set", "reset", "flip") ):
            f.call_policies = call_policies.return_self()
        classes.add_array_operators(c, "bp::default_call_policies()", "bool()")

    @classmethod
    def rename(cls, c):
        match = cls.bitset_re.search(c.name)
        c.rename("Bitset" + match.group(1))


class _STL_Containers(object):
    containers = {
        'array' : _STL_Exposer,
        'bitset' : _Bitset_STL_Exposer,
        'vector' : _STL_Exposer,
    }

    @classmethod
    def find(cls, ns, *names):
        containers = collections.defaultdict(list)
        for name in names:
            f = match_std_container_t(name)
            containers[name].extend(ns.classes(f, allow_empty=True))
        return containers

    @classmethod
    def findall(cls, ns):
        return cls.find(ns, *cls.containers.keys())

    @classmethod
    def expose(cls, ns):
        for name, containers in cls.findall(ns).items():
            exposer = cls.containers[name]
            for c in containers:
                exposer.expose(c)
                exposer.rename(c)

    def rename(cls, ns):
        for name, containers in cls.findall(ns).items():
            exposer = cls.containers[name]
            for c in containers:
                exposer.rename(c)
