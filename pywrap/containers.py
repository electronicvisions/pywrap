import collections, re

import classes
from matchers import match_std_container_t, namespace_contains_matcher_t
from pygccxml.declarations import templates
from pyplusplus.module_builder import call_policies

from pyplusplus.decl_wrappers.enumeration_wrapper import enumeration_t


def beautify_stl_container_names(ns):
    STL_Containers.rename(ns)

def extend_std_containers(ns):
    STL_Containers.expose(ns)

def get_stl_containers(ns, *names):
    return STL_Containers.find(ns, names)

class STLExposer(type):
    registered_exposers = {}

    def __new__(cls, name, bases, dct):
        containers = dct.get("containers", [])
        new_cls = super(STLExposer, cls).__new__(cls, name, bases, dct)

        for c in containers:
            cls.registered_exposers[c] = new_cls
        return new_cls

    @classmethod
    def get(cls, container):
        return cls.registered_exposers.get(container, STLExposerBase)

    @classmethod
    def list(cls):
        return cls.registered_exposers.keys()

class STL_Containers(object):
    @classmethod
    def find(cls, ns, names):
        containers = []
        for name in names:
            f = match_std_container_t(name)
            containers.extend(ns.classes(f, allow_empty=True))
        return containers

    @classmethod
    def findall(cls, ns):
        return cls.find(ns, STLExposer.list())

    @classmethod
    def expose(cls, ns):
        for c in cls.findall(ns):
            container = templates.name(c.name)
            exposer = STLExposer.get(container)
            exposer.expose(c)
            exposer.rename(c)

    def rename(cls, ns):
        for c in cls.findall(ns):
            container = templates.name(c.name)
            exposer = STLExposer.get(container)
            exposer.rename(c)

class STLExposerBase(object):
    __metaclass__ = STLExposer

    containers = ["pair"]

    re_match_number = re.compile(r'(\d+)\w+')

    builtins = {
            "bool"           : "Bool",
            "char"           : "Char",
            "double"         : "Double",
            "float"          : "Float",
            "int"            : "Int",
            "long"           : "Long",
            "short"          : "Short",
            "unsigned char"  : "Char",
            "unsigend int"   : "UInt",
            "unsigned short" : "UShort",
            "unsigned long"  : "ULong",
            }

    @classmethod
    def rename(cls, c):
        cls.create_alias(c)
#        n = c.name
#        n = n.replace('unsigned', 'u')
#        # uppercase each word
#        n = re.sub(r'\b(\w)', lambda m: m.group(1).upper(), n)
#        # remove namespaces
#        n = re.sub(r'\w+::', '', n)
#        # isolate numbers
#        n = re.sub(r'\b(\d+)\w*', r'\1', n)
#        # remove spaces
#        n = re.sub(r'\s+', '', n)
#        # remove allocator<...> if same type
#        n = re.sub(r'(?i)([^_]+)<([^_]+),allocator<\2>', r'\1<\2', n)
#        # replace template chars
#        n = re.sub(r'[<>,]+', '_', n)
#        # remove duplicates
#        n = re.sub(r'([^_]+_)\1', r'\1', n)
#        c.rename(re.sub(r'^_+|_+$', '', n))

    @classmethod
    def create_alias(cls, c):
        def decl_alias(decl):
            return lambda: decl.alias

        name = [ templates.name(c.name).capitalize() ]
        for arg in templates.args(c.name):
            number = cls.re_match_number.match(arg)
            if number:
                name.append( number.group(1) )
            elif arg in cls.builtins:
                name.append( cls.builtins[arg] )
            else:
                # Enumerations are exposed as class_t and enumeration_t, don't use the 2nd
                decls = [d for d in c.top_parent.decls('::' + arg) if not isinstance(d, (enumeration_t))]
                assert len(decls) == 1
                arg_decl = decls[0]
                # Put in a closure to get track if the name of class is changed later
                name.append( decl_alias(arg_decl) )
        c.rename( lambda: "_".join([ n() if callable(n) else n for n in name]) )

    @classmethod
    def expose(cls, c):
        cls.create_alias(c)

class Sequence_Exposer(STLExposerBase):
    containers = ["array", "vector"]

    @classmethod
    def expose(cls, c):
        super(Sequence_Exposer, cls).expose(c)
        classes.add_numpy_construtor(c)

class Bitset_Exposer(Sequence_Exposer):
    containers = ["bitset"]

    bitset_re = re.compile(r"bitset<(\d*)\w*>")

    @classmethod
    def expose(cls, c):
        super(Bitset_Exposer, cls).expose(c)
        c.mem_opers().include()
        c.allow_implicit_conversion = True
        for f in c.member_functions(name = lambda x: x.name in ("set", "reset", "flip") ):
            f.call_policies = call_policies.return_self()
        classes.add_array_operators(c, "bp::default_call_policies()", "bool()")

    @classmethod
    def create_alias(cls, c):
        match = cls.bitset_re.search(c.name)
        c.rename("Bitset" + match.group(1))


