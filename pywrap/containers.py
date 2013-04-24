import collections, re

import classes, namespaces
from matchers import match_std_container_t, namespace_contains_matcher_t
from pygccxml.declarations import algorithm, templates
from pyplusplus.module_builder import call_policies
from pyplusplus.messages import warnings_
from pyplusplus.decl_wrappers.enumeration_wrapper import enumeration_t
from pyplusplus.decl_wrappers.typedef_wrapper import typedef_t

def beautify_stl_container_names(ns):
    STL_Containers.rename(ns)

def extend_std_containers(ns):
    STL_Containers.expose(ns)

    for c in namespaces.getRants(ns):
        classes.beautify_rant_name(c)

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

    @classmethod
    def rename(cls, ns):
        for c in cls.findall(ns):
            container = templates.name(c.name)
            exposer = STLExposer.get(container)
            exposer.rename(c)

class STLExposerBase(object):
    __metaclass__ = STLExposer

    containers = ["pair"]

    re_match_number = re.compile(r'(\(.*?\))?(\d+)\w*')
    ignore_in_alias_tag = "STLExposer_IGNORE_IN_ALIAS"


    # TODO we could use pygccxml.declarations.cpptypes.FUNDAMENTAL_TYPES here?
    # but be careful with 'short unsigned int'
    builtins = {
            "bool"           : "Bool",
            "char"           : "Char",
            "double"         : "Double",
            "float"          : "Float",
            "int"            : "Int",
            "long"           : "Long",
            "short"          : "Short",
            "unsigned char"  : "UChar",
            "unsigned int"   : "UInt",
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
            def alias():
                if hasattr(decl, cls.ignore_in_alias_tag):
                    return ""
                else:
                    return decl.alias
            return alias

        def make_alias(name):
            def alias():
                tmp = [n() if callable(n) else n for n in name]
                return "_".join([n for n in tmp if n])
            return alias

        name = [ templates.name(c.name).capitalize() ]
        for arg in templates.args(c.name):
            number = cls.re_match_number.match(arg)
            if number:
                name.append( number.group(2) )
            elif arg in cls.builtins:
                name.append( cls.builtins[arg] )
            else:
                # Enumerations are exposed as class_t and enumeration_t, don't use the 2nd
                decls_f = lambda d: not (isinstance(d, (enumeration_t)) or isinstance(d, (typedef_t)))
                decls = [d for d in c.top_parent.decls('::' + arg) if decls_f(d)]
                if len(decls) == 0:
                    name.append(algorithm.create_valid_name(c.partial_name))
                elif len(decls) == 1:
                    # Put in a closure to get track if the name of class is changed later
                    name.append( decl_alias(decls[0]) )
                else:
                    print decls
                    raise RuntimeError("Something weired happend when renaming: " + c.decl_string)

        c.rename(make_alias(name))

    @classmethod
    def expose(cls, c):
        cls.create_alias(c)

class StdStringExposer(STLExposerBase):
    containers = ["basic_string"] #std::string

    @classmethod
    def create_alias(cls, c):
        if c.alias == "string":
            c.rename("String")
        elif c.alias == "wstring":
            c.rename("WString")

class Sequence_Exposer(STLExposerBase):
    containers = ["array", "vector"]

    @classmethod
    def expose(cls, c):
        super(Sequence_Exposer, cls).expose(c)
        classes.add_numpy_construtor(c)
        c.disable_warnings(warnings_.W1008)
        for f in c.mem_funs():
            f.disable_warnings(warnings_.W1008, warnings_.W1050)

class Not_Exposer(STLExposerBase):
    containers = ["allocator"]

    @classmethod
    def create_alias(cls, c):
        setattr(c, cls.ignore_in_alias_tag, True)

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
        c.operator(">>").disable_warnings(warnings_.W1014)
        c.operator("<<").disable_warnings(warnings_.W1014)

    @classmethod
    def create_alias(cls, c):
        match = cls.bitset_re.search(c.name)
        c.rename("Bitset" + match.group(1))


