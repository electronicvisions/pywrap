import logging
from collections import defaultdict

from pyplusplus import decl_wrappers

import algorithms


class NamespaceUtil(object):
    class PseudoDecl(object):
        """Place holder to map custom values and enum values"""
        def __init__(self, name, parent=None):
            self.alias = name
            self.parent = parent

        @property
        def exportable(self):
            if self.parent is None:
                return True
            else:
                return self.parent.exportable

        @property
        def ignore(self):
            if self.parent is None:
                return False
            else:
                return self.parent.ignore

    def __init__(self):
        self.names = defaultdict(list)
        self.log = logging.getLogger('pywrap.namespace_util')


    def add_decl(self, decl):
        if isinstance(decl.parent, decl_wrappers.namespace_t):
            old_name = decl.alias
            ns, name = self.gen_alias(decl)
            decl.wrapper_alias = name + "_wrapper"
            decl.rename(name)
            self.names[ns].append((old_name, decl))
            self.log.info('adding %s to %s as %s' % (decl.decl_string, ".".join(ns), old_name))
        else:
            self.log.info('skipping %s' % decl.decl_string)

    def add_enum(self, decl):
        if not isinstance(decl.parent, decl_wrappers.namespace_t):
            return
        self.add_decl(decl)
        for vname, value in decl.values:
            ns, name = self.gen_alias(decl, vname)
            #decl.value_aliases[vname] = name
            self.names[ns].append((vname, self.PseudoDecl(vname, decl)))

    def add_namespace(self, ns):
        for cls in ns.classes(allow_empty=True):
            self.add_decl(cls)

        for f in ns.free_functions(allow_empty=True):
            self.add_decl(f)

        for var in ns.variables(allow_empty=True):
            self.add_decl(var)

        for td in ns.typedefs(allow_empty=True):
            self.add_decl(td)

        for enum in ns.enumerations(allow_empty=True):
            self.add_enum(enum)

    def add_custom(self, ns, name, alias=None):
        self.names[ns].append(((alias or name), self.PseudoDecl(name)))

    def get_ns(self, decl):
        return tuple(algorithms.get_namespace_names(decl))

    def gen_alias(self, decl, name=None):
        ns = self.get_ns(decl)
        return ns, "_".join(ns) + "_" + (name or decl.alias)

    def _skip_decl(self, decl):
        return decl.ignore or not decl.exportable

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
                if not self._skip_decl(decl):
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
