#!/usr/bin/env python
from pywrap.wrapper import Wrapper
from pywrap.namespace_util import NamespaceUtil

wrap = Wrapper()
wrap.set_number_of_files(0)
mb = wrap.mb

ns_util = NamespaceUtil()

# Add namespace A1 complete
ns_util.add_namespace(mb.namespace("A1"))

# Add namespace B0 complete, and flatten the lowest level into the module
# namespace
ns_util.add_namespace(mb.namespace("B0"), drop_ns_levels=1)

# Add global variable
ns_util.add_decl(mb.decl("in_global_b"))

ns_util.finish(wrap)
wrap.finish()
