import logging
from collections import defaultdict

from pyplusplus import decl_wrappers

from . import algorithms


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
        def already_exposed(self):
            if self.parent is None:
                return False
            else:
                return self.parent.already_exposed

        @property
        def ignore(self):
            if self.parent is None:
                return False
            else:
                return self.parent.ignore

    def __init__(self):
        self.names = defaultdict(list)
        self.log = logging.getLogger('pywrap.namespace_util')

    def add_decl(self, decl, drop_ns_levels=0):
        if isinstance(decl.parent, decl_wrappers.namespace_t) and not decl.already_exposed:
            old_name = decl.alias
            ns, name = self.gen_alias(decl, drop_ns_levels=drop_ns_levels)
            decl.wrapper_alias = name + "_wrapper"
            decl.rename(name)
            self.names[ns].append((old_name, decl))
            self.log.info('adding %s to %s as %s' % (decl.decl_string, ".".join(ns), old_name))
        else:
            self.log.info('skipping %s' % decl.decl_string)

    def add_enum(self, decl, drop_ns_levels=0):
        if not isinstance(decl.parent, decl_wrappers.namespace_t):
            return
        self.add_decl(decl, drop_ns_levels=drop_ns_levels)
        for vname, value in decl.values:
            ns, name = self.gen_alias(decl, vname, drop_ns_levels=drop_ns_levels)
            #decl.value_aliases[vname] = name
            self.names[ns].append((vname, self.PseudoDecl(vname, decl)))

    def add_namespace(self, ns, drop_ns_levels=0):
        for cls in ns.classes(allow_empty=True):
            self.add_decl(cls, drop_ns_levels=drop_ns_levels)

        for f in ns.free_functions(allow_empty=True):
            self.add_decl(f, drop_ns_levels=drop_ns_levels)

        for var in ns.variables(allow_empty=True):
            self.add_decl(var, drop_ns_levels=drop_ns_levels)

        for td in ns.typedefs(allow_empty=True):
            self.add_decl(td, drop_ns_levels=drop_ns_levels)

        for enum in ns.enumerations(allow_empty=True):
            self.add_enum(enum, drop_ns_levels=drop_ns_levels)

    def add_custom(self, ns, name, alias=None):
        self.names[ns].append(((alias or name), self.PseudoDecl(name)))

    def gen_alias(self, decl, name=None, drop_ns_levels=0):
        ns = tuple(algorithms.get_namespace_names(decl))[drop_ns_levels:]
        ns = tuple(n for n in ns if n)
        return ns, "_" + "_".join(ns) + "_" + (name or decl.alias)

    def _skip_decl(self, decl):
        return decl.ignore or decl.already_exposed or not decl.exportable

    def write_symbols(self, mb):
        """
        Create table of symbols containing the modules
        Note: deprecated
        """
        code = []
        code.append('bp::dict symbols(bp::object scope) {')
        code.append('bp::dict names;')
        for ns, decls in list(self.names.items()):
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

    def finish(self, wrap):
        """
        Finish the namespace creation and generate boost python code to
        create the submodules.

        A list of submodules will be embedded in the module as '_submodules'
        attribute.
        """

        # Add parent namespaces, which were not included
        for ns in sorted(self.names.keys()):
            while ns:
                self.names[ns]
                ns = ns[:-1]

        code = []
        add = code.append

        def addi(txt):
            "Add code with indention"
            add('\t\t' + txt)

        add('// Create nested modules for all namespaces')
        add('{')
        add('\tbp::object ModuleType = bp::import("types").attr("ModuleType");')
        add('\tbp::object sys = bp::import("sys");')
        add('\tbp::list submodules = bp::list();')
        add('\tbp::scope().attr("_submodules") = submodules;')

        # Sorting the keys, ensure that we start with the outer namespaces
        for ns in sorted(self.names.keys()):
            decls = self.names[ns]
            name = '.'.join((wrap.module_name(), ) + ns)
            add('{')
            # Create new module
            if len(ns) == 0:  # Base namespace
                addi('bp::object module = bp::scope();')
            else:
                addi('bp::object module = ModuleType("%s");' % name)
                addi('sys.attr("modules").attr("setdefault")("%s", module);' % name)
            addi('submodules.append(bp::make_tuple("%s", module));' % name)

            # addi module to parent
            if ns:
                addi('bp::object parent = bp::scope()%s;' % (
                    ''.join('.attr("%s")' % n for n in ns[:-1])))
                addi('parent.attr("%s") = module;' % ns[-1])
                addi('parent.attr("__all__").attr("append")("%s");' % ns[-1])

            addi('bp::list all = bp::list();')
            for old_name, decl in decls:
                if not self._skip_decl(decl):
                    addi('module.attr("%s") = bp::scope().attr("%s");' % (
                        old_name, decl.alias))
                    addi('all.append("%s");' % old_name)
            if not decls:
                addi('// nothing in this namespace')
            addi('module.attr("__all__") = all;')
            add('}')
        add('}')

        wrap.mb.add_registration_code('\n'.join(code))
