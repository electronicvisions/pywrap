from collections import defaultdict
from pyplusplus import decl_wrappers

import algorithms

class EnumValue(object):
    def __init__(self, name):
        self.alias = name
        self.ignore = False

class NamespaceUtil(object):
    def __init__(self):
        self.names = defaultdict(list)

    def add_decl(self, decl):
        if not isinstance(decl.parent, decl_wrappers.namespace_t):
            return
        old_name = decl.alias
        ns, name = self.gen_alias(decl)
        decl.wrapper_alias = name + "_wrapper"
        decl.rename(name)
        self.names[ns].append((old_name, decl))

    def add_enum(self, decl):
        if not isinstance(decl.parent, decl_wrappers.namespace_t):
            return
        self.add_decl(decl)
        for vname, value in decl.values:
            ns, name = self.gen_alias(decl, vname)
            decl.value_aliases[vname] = name
            self.names[ns].append((vname, EnumValue(name)))

    def get_ns(self, decl):
        return tuple(algorithms.get_namespace_names(decl))

    def gen_alias(self, decl, name=None):
        ns = self.get_ns(decl)
        return ns, "_".join(ns) + "_" + (name or decl.alias)

    def write_symbols(self, mb):
        code = []
        code.append('bp::dict symbols(bp::object scope) {')
        code.append('bp::dict names;')
        for ns, decls in self.names.iteritems():
            ns_key = ' ,'.join(['"%s"' % s for s in ns])
            code.append('{')
            code.append('auto key = bp::make_tuple(%s);' % ns_key)
            code.append('auto stuff = bp::dict();')
            for old_name, decl in decls:
                if decl.ignore:
                    continue
                code.append(
                        'stuff["%s"] = scope.attr("%s");'
                            % (old_name, decl.alias) )
            code.append('names[key] = stuff;')
            code.append('}')
        code.append( 'return names; }' )
        mb.add_declaration_code( '\n'.join(code) )
        mb.add_registration_code('bp::def("symbols",'
                'bp::make_function(std::bind(&symbols, bp::scope()),'
                'bp::default_call_policies(),'
                'boost::mpl::vector<bp::dict>()));')
